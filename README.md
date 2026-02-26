# AutoNotebooks

Create AI-powered **NotebookLM** notebooks and learning materials (audio, slides, quizzes, flashcards, and more) by simply telling an LLM what you want.

## How to Use

Follow these steps to generate notebooks automatically:

1. **Clone the repository** (if you haven't):
   ```bash
   git clone https://github.com/brendondgr/AutoNotebooks.git
   cd AutoNotebooks
   ```
2. **Open the project** in your AI assistant (e.g., Claude Code, Cursor, or Antigravity).
3. **Reference the Skill**: Reference `@SKILL.md` in your prompt and say:

   > **"Following @SKILL.md, create me a series of Notebooks on the following topics: [Insert Topics List]"**

The agent will follow the orchestration logic in `SKILL.md` to create notebooks, research topics, and generate artifacts automatically.

### Example Commands

**Simple:**

```
Following @SKILL.md, create me notebooks on: Python Basics, Data Structures, and Machine Learning
```

**With preferences:**

```
Following @SKILL.md, create me notebooks on: Cell Biology and Photosynthesis.
I'd like audio explanations and slides for each one, plus a quiz.
Use fast research mode.
```

**More detailed:**

```
Following @SKILL.md, create me the following notebooks:
- Python Fundamentals (with audio dialogue and flashcards)
- Advanced Python (with slides and a quiz)

Use deep research mode and include relevant online sources.
```

## What You Get

The LLM will automatically:

✅ Create NotebookLM notebooks for each topic  
✅ Research and populate your notebooks with relevant information  
✅ Generate the artifacts you request (audio, slides, quizzes, flashcards, etc.)  
✅ Download everything locally for you  
✅ Show real-time progress in your terminal

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

This repository includes a `SKILL.md` document loaded with YAML front-matter and explicit instructions on the NotebookLM automation workflow. You can easily integrate this into your preferred AI assistant so it inherently understands how to generate notebooks for you!

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

### Claude Code

Claude Code uses a `CLAUDE.md` file in the project directory for its primary memory and project guidelines. To integrate:

- **Recommended**: Copy the skill to be Claude's default project instructions:
  ```bash
  mkdir -p .claude
  cp SKILL.md .claude/CLAUDE.md
  ```
- **Portable (Self-Contained)**: Bundle the logic directly inside the `.claude/` folder:
  ```bash
  mkdir -p .claude
  cp -r nlm_runner.py utils/ SKILL.md .claude/
  mv .claude/SKILL.md .claude/CLAUDE.md
  ```
- **Alternative**: Reference the file in your prompt directly (e.g., _"Following @SKILL.md, create me a notebook..."_).

## Features

- **Fast & Parallel** - Creates multiple notebooks simultaneously
- **AI-Powered** - Works seamlessly with any LLM
- **Live Progress** - Watch real-time progress in your terminal
- **Auto-Download** - All materials downloaded locally automatically
- **Flexible** - Create 1 notebook or 10, mix and match artifacts
- **Resumable** - Pause and resume pipelines as needed

## License

This project is designed to work with NotebookLM and follows its terms of service.
