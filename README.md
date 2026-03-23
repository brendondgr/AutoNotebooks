# AutoNotebooks

Create notebooks automatically by simply requesting them in your console.

Ask your local agent to create you Notebooks on specific topics and it will carry out creating however many you request, along with conducting Research, creation of Artifacts and downloading directly to your local repository. 

## How to Use

Follow these steps to generate notebooks automatically:

1. **Clone the repository** (if you haven't):
   ```bash
   git clone https://github.com/brendondgr/AutoNotebooks.git
   cd AutoNotebooks
   ```
2. **Open the project** in your AI assistant (e.g., Claude Code, Cursor, or Antigravity).
3. **Reference the Skill**: Reference `AutoNotebooks` in your prompt and say:

   > **"Following AutoNotebooks Skill, create me a series of Notebooks on the following topics: [Insert Topics List]"**

The agent will follow the orchestration logic in `SKILL.md` to create notebooks, research topics, and generate artifacts automatically.

### Example Commands

**Simple:**

```
Following AutoNotebooks skill, create me notebooks on: Python Basics, Data Structures, and Machine Learning
```

**With preferences:**

```
Following AutoNotebooks skill, create me notebooks on: Cell Biology and Photosynthesis.
I'd like audio explanations and slides for each one, plus a quiz.
Use fast research mode.
```

**More detailed:**

```
Following AutoNotebooks skill, create me the following notebooks:
- Python Fundamentals (with audio dialogue and flashcards)
- Advanced Python (with slides and a quiz)

Use deep research mode and include relevant online sources.
```

## What You Get

The LLM will automatically:

- Create NotebookLM notebooks for each topic  
- Research and populate your notebooks with relevant information  
- Generate the artifacts you request (audio, slides, quizzes, flashcards, etc.)  
- Download everything locally for you  
- Show real-time progress in your terminal

You can then integrate this into a local HTML to see everything live.

## Available Learning Materials

You can ask for any or all of these:

- **Audio** - AI-generated audio explanations (podcast-style)
- **Slides** - Presentation slides
- **Quizzes** - Interactive quizzes to test knowledge
- **Flashcards** - Flashcard sets for studying
- **Video** - Video content
- **Mindmaps** - Visual mind maps
- **Infographics** - Visual infographics
- **Reports** - Written reports
- **Data Tables** - Structured data presentations

## Setup

You only need to set up once:

1. **Install dependencies** (one time):
   ```bash
   uv sync
   ```

## Using as an AI Skill

This repository includes an `AutoNotebooks/` directory with a `SKILL.md` document loaded with YAML front-matter and explicit instructions on the NotebookLM automation workflow. You can easily integrate this into your preferred Agent so it inherently understands how to generate notebooks for you.

### Claude Code

Claude Code discovers skills from `SKILL.md` files organized in a `skills` directory. To integrate this skill:

**Choose your installation location:**

- **Global (all projects)**: `~/.claude/skills/`
- **Per project**: `.claude/skills/`

**Minimal setup:**

```bash
cp -r AutoNotebooks/ .claude/skills/
```

**Folder structure:**

```
.claude/skills/
└── AutoNotebooks/
  ├── SKILL.md              # required
  ├── scripts/              # optional helpers
  │   └── nlm_runner.py
  └── references/           # optional docs
    └── utils/
```

Claude automatically discovers and loads the skill once `SKILL.md` is in place.

### Google Antigravity

Antigravity natively supports the `SKILL.md` standard. The agent will automatically discover and parse the `SKILL.md` file in the repository to extend its capabilities.

- **Recommended**: Copy to the specific agent rules folder:
  ```bash
  mkdir -p .agent/rules
  cp SKILL.md .agent/rules/notebook-automation.md
  ```
- **Portable (Self-Contained)**: You can also move the logic into the rule folder for a cleaner root:
  ```bash
  mkdir -p .agent/rules
  cp -r nlm_runner.py utils/ SKILL.md .agent/rules/
  ```

### Cursor

Cursor uses Markdown Domain Configuration (`.mdc`) and rule files to understand project context. To integrate this skill:

- **Recommended**: Copy it into Cursor's rules directory so it applies automatically:
  ```bash
  mkdir -p .cursor/rules
  cp SKILL.md .cursor/rules/notebook-automation.mdc
  ```
- **Portable (Self-Contained)**: Bundle the automation logic inside Cursor's rule directory:
  ```bash
  mkdir -p .cursor/rules
  cp -r nlm_runner.py utils/ SKILL.md .cursor/rules/
  mv .cursor/rules/SKILL.md .cursor/rules/notebook-automation.mdc
  ```
- **Quick Use**: Simply tag `@SKILL.md` in your Cursor Chat.

## Features

- **Fast & Parallel** - Creates multiple notebooks simultaneously
- **AI-Powered** - Works seamlessly with any LLM
- **Live Progress** - Watch real-time progress in your terminal
- **Auto-Download** - All materials downloaded locally automatically
- **Flexible** - Create 1 notebook or 10, mix and match artifacts
- **Resumable** - Pause and resume pipelines as needed

## License

This project is designed to work with NotebookLM and follows its terms of service.
