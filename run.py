#!/usr/bin/env python3
import os
import sys
import time
import threading
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
from rich.live import Live
from rich.console import Console

from utils import (
    load_config, PipelineConfig, TopicConfig, ArtifactConfig,
    run_nlm, extract_notebook_id, extract_task_id, parse_latest_artifacts, safe_filename,
    StateManager, StatusDashboard
)

# Status Symbols
DONE = "[green]✔[/green]"
PENDING = "[yellow]●[/yellow]"
NOT_DONE = "[red]✘[/red]"
POLLING = "[bold cyan]⧖[/bold cyan]"

CONSOLE = Console()

def topic_worker(topic: TopicConfig, config: PipelineConfig, state: StateManager, dashboard: StatusDashboard, index: int):
    key = topic.key
    nb_id = topic.notebook_id or state.get_notebook_id(key)

    # Resolve effective artifacts: topic-level overrides global
    effective_artifacts = topic.artifacts if topic.artifacts is not None else config.artifacts
    artifact_types = [a.type for a in effective_artifacts]
    
    # Initialize symbols based on state
    if nb_id: dashboard.update_status(key, "notebook", PENDING, "Found ID")
    if state.is_research_done(key): dashboard.update_status(key, "research", DONE)
    for art in artifact_types:
        if state.is_artifact_done(key, art): dashboard.update_status(key, art, DONE)

    # 0. Stagger
    if index > 0:
        dashboard.update_status(key, "msg", f"Staggering ({index*2}s)...")
        time.sleep(index * 2)

    # 1. Notebook
    if nb_id:
        v_out = run_nlm(["get", "notebook", nb_id], timeout=30, log_key=key)
        if not v_out or "Error" in v_out or "not found" in v_out.lower():
            dashboard.update_status(key, "notebook", NOT_DONE, "Invalid/Missing")
            nb_id = None
            state.clear_topic(key)
            # Update dashboard to reflect cleared status
            dashboard.update_status(key, "research", NOT_DONE, "Cleared")
            for art in artifact_types:
                dashboard.update_status(key, art, NOT_DONE, "Cleared")

    # 0.7 Force-Restart Research?
    if config.research_force and state.is_research_done(key):
        # We keep the notebook, but clear everything else to force a full redo
        dashboard.update_status(key, "msg", "Force-clearing state...")
        state.reset_topic_progress(key)
        # Update dashboard
        dashboard.update_status(key, "research", PENDING, "Restarting...")
        for art in artifact_types:
            dashboard.update_status(key, art, NOT_DONE, "Restarting")
        
    if not nb_id:
        dashboard.update_status(key, "notebook", PENDING, "Creating...")
        out = run_nlm(["create", "notebook", topic.title], log_key=key)
        nb_id = extract_notebook_id(out)
        if nb_id:
            state.set_notebook_id(key, nb_id)
            dashboard.update_status(key, "notebook", DONE, "Created.")
        else:
            dashboard.update_status(key, "notebook", NOT_DONE, "Failed creation.")
            return
    else:
        dashboard.update_status(key, "notebook", DONE, "Verified.")

    # 1.5 Sources
    if topic.sources and not state.is_artifact_done(key, "sources_processed"):
        dashboard.update_status(key, "msg", "Adding sources...")
        expected_source_count = len(topic.sources)

        for src in topic.sources:
            cmd = ["source", "add", nb_id]
            if src.type == "url": cmd.extend(["--url", src.value])
            elif src.type == "file": cmd.extend(["--file", src.value])
            elif src.type == "text": cmd.extend(["--text", src.value, "--title", src.title or "Untitled Text"])
            elif src.type == "drive": cmd.extend(["--drive", src.value])
            elif src.type == "youtube": cmd.extend(["--youtube", src.value])
            run_nlm(cmd, timeout=120, log_key=key)

        # Poll to verify sources are processed before continuing
        dashboard.update_status(key, "msg", "Waiting for sources to process...")
        max_source_wait = 60  # 60 attempts = up to 5 minutes
        for attempt in range(max_source_wait):
            nb_info = run_nlm(["get", "notebook", nb_id], timeout=30, log_key=key)

            # Check if sources are mentioned and processed
            # NotebookLM output typically shows "X sources" when ready
            if nb_info and ("source" in nb_info.lower()):
                # Give a bit more time for processing to stabilize
                time.sleep(5)
                state.set_artifact_done(key, "sources_processed")
                dashboard.update_status(key, "msg", "Sources processed ✓")
                break

            time.sleep(5)
        else:
            dashboard.update_status(key, "msg", "[red]Error: Sources failed to process[/red]")
            return  # Don't continue if sources aren't ready
    elif topic.sources:
        dashboard.update_status(key, "msg", "Sources already processed ✓")

    # 1.7 Chat Config
    if topic.chat:
        dashboard.update_status(key, "msg", "Configuring chat...")
        chat_args = ["chat", "configure", nb_id, "--goal", topic.chat.goal, "--response-length", topic.chat.response_length]
        if topic.chat.goal == "custom" and topic.chat.prompt:
            chat_args.extend(["--prompt", topic.chat.prompt])
        run_nlm(chat_args, log_key=key)

    # 2. Research
    if topic.query and (not state.is_research_done(key) or config.research_force):
        dashboard.update_status(key, "research", PENDING, "Reviewing...")
        status_out = run_nlm(["research", "status", nb_id], timeout=60, log_key=key)
        
        needs_start = "no research found" in status_out.lower() or not status_out
        if config.research_force: needs_start = True

        if needs_start:
            dashboard.update_status(key, "research", PENDING, "Starting...")
            start_args = ["research", "start", "--mode", config.research_mode, "--source", config.research_source, "--notebook-id", nb_id]
            if config.research_force: start_args.append("--force")
            start_args.append(topic.query)
            run_nlm(start_args, timeout=360, log_key=key) # Increased for deep research
            
        dashboard.update_status(key, "research", POLLING, "Polling...")
        attempts = 0
        max_attempts = 40 if config.research_mode == "fast" else 80
        while attempts < max_attempts:
            status_out = run_nlm(["research", "status", nb_id, "--max-wait", "0"], timeout=60, log_key=key)
            if "status: completed" in status_out.lower():
                tid = extract_task_id(status_out)
                dashboard.update_status(key, "msg", "Importing research...")
                import_args = ["research", "import", nb_id]
                if tid: import_args.append(tid)
                run_nlm(import_args, timeout=120, log_key=key)

                # Poll until imported sources are reflected in the notebook
                dashboard.update_status(key, "msg", "Waiting for sources to process...")
                for src_attempt in range(60):  # up to 5 minutes
                    nb_info = run_nlm(["get", "notebook", nb_id], timeout=30, log_key=key)
                    if nb_info and "source" in nb_info.lower():
                        time.sleep(5)  # stabilisation pause
                        break
                    time.sleep(5)
                else:
                    dashboard.update_status(key, "research", NOT_DONE, "Source processing timeout.")
                    return

                state.set_research_done(key)
                dashboard.update_status(key, "research", DONE, "Imported.")
                break
            elif "failed" in status_out.lower():
                dashboard.update_status(key, "research", NOT_DONE, "Failed.")
                return  # Don't continue to artifacts if research failed
            attempts += 1
            time.sleep(20)
        else:
            dashboard.update_status(key, "research", NOT_DONE, "Timeout.")
            return
    elif not topic.query:
        # If no query but sources added, mark research done (research implies query-based discovery)
        state.set_research_done(key)
        dashboard.update_status(key, "research", DONE, "Sources only.")

    # 3. Artifacts
    # Only proceed with artifacts if research is complete (or not required)
    if not state.is_research_done(key) and topic.query:
        dashboard.update_status(key, "msg", "[red]Skipping artifacts: Research not complete[/red]")
        return

    if effective_artifacts:
        needed_artifacts = [a for a in effective_artifacts if not state.is_artifact_done(key, a.type)]
        if needed_artifacts:
            dashboard.update_status(key, "msg", "Triggering artifacts...")
            
            # Map type names
            type_map = {
                "audio": "audio", "video": "video", "slide_deck": "slides",
                "report": "report", "flashcards": "flashcards", "quiz": "quiz",
                "mind_map": "mindmap", "infographic": "infographic", "data_table": "data-table"
            }

            for art_cfg in needed_artifacts:
                dashboard.update_status(key, art_cfg.type, PENDING, "Creating...")
                subcmd = type_map.get(art_cfg.type, art_cfg.type.replace("_", "-"))
                cmd = ["create", subcmd, nb_id, "--confirm"]
                
                # Add flags
                for f_key, f_val in art_cfg.flags.items():
                    flag = f"--{f_key.replace('_', '-')}"
                    cmd.extend([flag, str(f_val)])
                
                # Focus/Language/Sources
                focus = art_cfg.focus or config.focus_prompt
                if focus: cmd.extend(["--focus", focus])
                lang = art_cfg.language or config.language
                if lang: cmd.extend(["--language", lang])
                if art_cfg.source_ids: cmd.extend(["--source-ids", ",".join(art_cfg.source_ids)])
                
                run_nlm(cmd, timeout=180, log_key=key)
                time.sleep(2)

            # Poll/Revise/Rename
            dashboard.update_status(key, "msg", "Polling artifacts...")
            for i in range(30):
                out = run_nlm(["studio", "status", nb_id, "--json"], timeout=60, log_key=key)
                latest = parse_latest_artifacts(out)

                all_done = True
                for art_cfg in effective_artifacts:
                    art_data = latest.get(art_cfg.type)
                    if not art_data:
                        all_done = False
                        continue
                        
                    status = art_data.get("status")
                    art_id = art_data.get("artifact_id")

                    if status == "completed":
                        # Revision check (only once)
                        if art_cfg.revision_instructions and art_cfg.type == "slide_deck" and not state.is_artifact_done(key, f"{art_cfg.type}_revised"):
                            dashboard.update_status(key, art_cfg.type, PENDING, "Revising...")
                            rev_cmd = ["slides", "revise", art_id, "--confirm"]
                            for ri in art_cfg.revision_instructions:
                                rev_cmd.extend(["--slide", f"{ri['slide']} {ri['instruction']}"])
                            run_nlm(rev_cmd, timeout=180, log_key=key)
                            state.set_artifact_done(key, f"{art_cfg.type}_revised")
                            all_done = False # Wait for revised deck
                            continue

                        # Rename?
                        if art_cfg.rename and not state.is_artifact_done(key, f"{art_cfg.type}_renamed"):
                            run_nlm(["studio", "rename", nb_id, art_id, art_cfg.rename], log_key=key)
                            state.set_artifact_done(key, f"{art_cfg.type}_renamed")

                        state.set_artifact_done(key, art_cfg.type)
                        dashboard.update_status(key, art_cfg.type, DONE, "Done.")
                    elif status == "failed":
                        dashboard.update_status(key, art_cfg.type, NOT_DONE, "Failed.")
                    else:
                        dashboard.update_status(key, art_cfg.type, POLLING, "Wait...")
                        all_done = False
                
                if all_done: break
                time.sleep(30)

    # 4. Download
    if config.download and effective_artifacts:
        dashboard.update_status(key, "msg", "Downloading...")
        fname = safe_filename(key)
        for art_cfg in effective_artifacts:
            if not state.is_download_done(key, art_cfg.type):
                ext_map = {
                    "audio": ".m4a", "video": ".mp4", "slide_deck": ".pdf",
                    "report": ".md", "flashcards": ".json", "quiz": ".json",
                    "mind_map": ".json", "infographic": ".png", "data_table": ".csv"
                }
                ext = ext_map.get(art_cfg.type, ".bin")
                
                # Robust subdir naming
                sub_map = {"quiz": "quizzes", "flashcards": "flashcards", "data_table": "data_tables", "slide_deck": "slide_decks"}
                sub_dir = sub_map.get(art_cfg.type, art_cfg.type + "s")
                
                out_path = os.path.join(config.output_dir, sub_dir, f"{fname}{ext}")
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                
                dl_type = art_cfg.type.replace("_", "-")
                dl_args = ["download", dl_type, nb_id, "--output", out_path]
                if art_cfg.type == "slide_deck": dl_args.extend(["--format", "pdf"])
                
                run_nlm(dl_args, timeout=120, log_key=key)
                if os.path.exists(out_path):
                    state.set_download_done(key, art_cfg.type)

    dashboard.update_status(key, "msg", "[bold green]Finished[/bold green]")

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json")
    args = parser.parse_args()

    if not os.path.exists(args.config):
        CONSOLE.print(f"[red]Error: {args.config} not found. Ensure the AI has created it.[/red]")
        sys.exit(1)

    CONSOLE.print("[bold blue]Ensuring Authentication via `uv run nlm login`...[/bold blue]")
    try:
        res = subprocess.run(["uv", "run", "nlm", "login"], check=True)
    except subprocess.CalledProcessError:
        CONSOLE.print("[bold red]Authentication Failed. Pipeline aborted.[/bold red]")
        sys.exit(1)
        
    CONSOLE.print("[bold green]Authentication Complete.[/bold green]\n")

    config = load_config(args.config)
    os.makedirs(config.output_dir, exist_ok=True)

    state = StateManager("state.json")

    # Collect all unique artifact types across all topics (union of global + per-topic)
    all_artifact_types = list(dict.fromkeys(
        [a.type for a in config.artifacts] +
        [a.type for t in config.topics if t.artifacts for a in t.artifacts]
    ))

    # Build per-topic artifact map for the dashboard
    topic_artifact_map = {
        t.key: [a.type for a in (t.artifacts if t.artifacts is not None else config.artifacts)]
        for t in config.topics
    }

    dashboard = StatusDashboard([t.key for t in config.topics], all_artifact_types, topic_artifact_map)

    with Live(dashboard.generate_table(), console=CONSOLE, refresh_per_second=2) as live:
        with ThreadPoolExecutor(max_workers=len(config.topics)) as executor:
            futures = {executor.submit(topic_worker, topic, config, state, dashboard, i): topic.key for i, topic in enumerate(config.topics)}
            
            while any(f.running() for f in futures.keys()):
                live.update(dashboard.generate_table())
                time.sleep(0.5)
            
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    dashboard.update_status(futures[future], "msg", f"[red]Crash: {e}[/red]")
            
            live.update(dashboard.generate_table())

    CONSOLE.print("\n[bold green]Automation Pipeline Finished.[/bold green]")

if __name__ == "__main__":
    main()
