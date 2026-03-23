from dataclasses import dataclass, field
import json
from typing import List, Optional, Dict, Any

@dataclass
class SourceConfig:
    type: str # url, file, text, drive
    value: str # URL, file path, text content, or document ID
    title: Optional[str] = None # For text sources

@dataclass
class ArtifactConfig:
    type: str # audio, video, slide_deck, report, flashcards, quiz, mind_map, infographic, data_table
    flags: Dict[str, Any] = field(default_factory=dict)
    focus: Optional[str] = None
    language: Optional[str] = None
    source_ids: List[str] = field(default_factory=list)
    rename: Optional[str] = None
    revision_instructions: List[Dict[str, Any]] = field(default_factory=list) # e.g. [{"slide": 1, "instruction": "..."}]

@dataclass
class ChatConfig:
    goal: str = "default" # default, learning_guide, custom
    prompt: Optional[str] = None
    response_length: str = "default" # default, longer, shorter

@dataclass
class TopicConfig:
    key: str
    title: str
    query: Optional[str] = None
    sources: List[SourceConfig] = field(default_factory=list)
    notebook_id: Optional[str] = None
    chat: Optional[ChatConfig] = None
    artifacts: Optional[List['ArtifactConfig']] = None  # Per-topic override; None = use global

@dataclass
class PipelineConfig:
    topics: List[TopicConfig]
    research_mode: str = "fast" # fast or deep
    research_source: str = "web" # web or drive
    research_force: bool = True
    artifacts: List[ArtifactConfig] = field(default_factory=list)
    download: bool = True
    output_dir: str = "./output"
    language: str = "en"
    focus_prompt: Optional[str] = None

def load_config(path: str) -> PipelineConfig:
    with open(path, 'r') as f:
        data = json.load(f)
    
    topics = []
    for t in data.get("topics", []):
        sources = [SourceConfig(**s) for s in t.get("sources", [])]
        chat = None
        if t.get("chat") is not None:
            chat = ChatConfig(**t["chat"])
        topic_artifacts = None
        if "artifacts" in t:
            topic_artifacts = []
            for a in t["artifacts"]:
                topic_artifacts.append(ArtifactConfig(
                    type=a["type"],
                    flags=a.get("flags", {}),
                    focus=a.get("focus"),
                    language=a.get("language"),
                    source_ids=a.get("source_ids", []),
                    rename=a.get("rename"),
                    revision_instructions=a.get("revision_instructions", [])
                ))
        topics.append(TopicConfig(
            key=t["key"],
            title=t["title"],
            query=t.get("query"),
            sources=sources,
            notebook_id=t.get("notebook_id"),
            chat=chat,
            artifacts=topic_artifacts
        ))
        
    artifacts = []
    for a in data.get("artifacts", []):
        artifacts.append(ArtifactConfig(
            type=a["type"],
            flags=a.get("flags", {}),
            focus=a.get("focus"),
            language=a.get("language"),
            source_ids=a.get("source_ids", []),
            rename=a.get("rename"),
            revision_instructions=a.get("revision_instructions", [])
        ))
    
    return PipelineConfig(
        topics=topics,
        research_mode=data.get("research_mode", "fast"),
        research_source=data.get("research_source", "web"),
        research_force=data.get("research_force", True),
        artifacts=artifacts,
        download=data.get("download", True),
        output_dir=data.get("output_dir", "./output"),
        language=data.get("language", "en"),
        focus_prompt=data.get("focus_prompt")
    )

def save_config(config: PipelineConfig, path: str):
    data = {
        "topics": [{
            "key": t.key,
            "title": t.title,
            "query": t.query,
            "sources": [vars(s) for s in t.sources],
            "notebook_id": t.notebook_id,
            "chat": vars(t.chat) if t.chat else None,
            "artifacts": [{
                "type": a.type, "flags": a.flags, "focus": a.focus,
                "language": a.language, "source_ids": a.source_ids,
                "rename": a.rename, "revision_instructions": a.revision_instructions
            } for a in t.artifacts] if t.artifacts is not None else None
        } for t in config.topics],
        "research_mode": config.research_mode,
        "research_source": config.research_source,
        "research_force": config.research_force,
        "artifacts": [{
            "type": a.type,
            "flags": a.flags,
            "focus": a.focus,
            "language": a.language,
            "source_ids": a.source_ids,
            "rename": a.rename,
            "revision_instructions": a.revision_instructions
        } for a in config.artifacts],
        "download": config.download,
        "output_dir": config.output_dir,
        "language": config.language,
        "focus_prompt": config.focus_prompt
    }
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)
