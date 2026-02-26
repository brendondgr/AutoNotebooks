---
name: NotebookAutomation
description: A semi-skill for parallelized NotebookLM notebook creation and artifact generation through AI-User interaction.
---

## ⚠️ Critical Rule: No Code Modifications

The automation engine (`nlm_runner.py` and `utils/`) is a finalized, robust system that supports **ALL** NotebookLM features through its configuration schema.
**As an AI agent, you MUST NOT modify any Python code in this directory.**

Your sole responsibility is to:

1.  Gather requirements.
2.  Generate the correct JSON configuration.
3.  Execute the pipeline using the `--config` flag.

---

## Workflow: Back-and-Forth Planning

Before generating any files or running the automation, you must gather all necessary details from the user.

### Phase 1: Requirement Gathering

Ask for the following details (grouping is allowed for efficiency):

1.  **Topics**: Names and research queries. **NEW**: You can now also provide an existing `notebook_id` to skip creation, specific `sources` (URLs, local files, Drive IDs, or YouTube links), and **per-topic `artifacts`** to generate different artifacts for different notebooks.
2.  **Research**: Mode (`fast`/`deep`), Source (`web`/`drive`), and if it should be `force` started.
3.  **Chat Settings**: Optional `goal` (`learning_guide`, `custom`) and `response_length`.
4.  **Artifacts**: Which ones? (audio, video, slides, report, quiz, flashcards, mindmap, infographic, data-table).
5.  **Artifact Specs**:
    - **Flags**: (e.g., audio format, quiz difficulty).
    - **Focus**: Specific focus prompt for _this_ artifact.
    - **Sources**: Filter which source IDs to use for this artifact.
    - **Revision**: (For slides) specific slide-by-slide revision instructions.
    - **Rename**: Custom title for the generated artifact.
6.  **Downloads**: Whether to download locally (Default: yes).

### Phase 2: Confirmation

Consolidate the plan and ask for user confirmation.

### Phase 3: Execution

1.  **Create Config Directory**: `NotebookAutomation/config/`.
2.  **Write Config**: `config_<timestamp>.json` following the `PipelineConfig` schema in `utils/config.py`.
3.  **Run Pipeline**: Locate `nlm_runner.py` (check root or `.agent/rules/`) and execute **strictly** using the `--config` flag:
    ```bash
    uv run python [path/to/]nlm_runner.py --config config/config_<timestamp>.json
    ```

## Advanced Config Schema Reference

```json
{
  "topics": [
    {
      "key": "unique_id",
      "title": "Notebook Title",
      "query": "Research Query",
      "sources": [{ "type": "url", "value": "https://..." }],
      "chat": { "goal": "learning_guide", "response_length": "longer" },
      "artifacts": [
        {
          "type": "audio",
          "flags": { "format": "debate" },
          "rename": "Deep Dive"
        },
        { "type": "infographic" }
      ]
    },
    {
      "key": "another_topic",
      "title": "Another Notebook",
      "query": "Another query",
      "artifacts": [{ "type": "audio" }]
    }
  ],
  "research_mode": "fast",
  "artifacts": [],
  "download": true
}
```

> **Artifact Resolution**: If a topic defines its own `artifacts` list, it overrides the global `artifacts` for that topic. If a topic omits `artifacts` (or sets it to `null`), the global `artifacts` list is used. The terminal dashboard will show a neutral **`─`** for any artifact column that does not apply to a given topic.
