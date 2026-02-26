# AutoNotebooks

Create AI-powered **NotebookLM** notebooks and learning materials (audio, slides, quizzes, flashcards, and more) by simply telling an LLM what you want.

## How to Use

Simply provide this command to an LLM (like Claude, ChatGPT, or any AI assistant):

> **"Create me a series of Notebooks on the following topics: [Insert Topics List]"**

That's it! The LLM will handle everything for you—creating notebooks, researching topics, and generating all the learning materials you need.

### Example Commands

**Simple:**
```
Create me notebooks on: Python Basics, Data Structures, and Machine Learning
```

**With preferences:**
```
Create me notebooks on: Cell Biology and Photosynthesis. 
I'd like audio explanations and slides for each one, plus a quiz.
Use fast research mode.
```

**More detailed:**
```
Create me the following notebooks:
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

2. **Add your NotebookLM credentials** to a `.env` file in the project folder:
   ```
   NOTEBOOKLM_USERNAME=your_username
   NOTEBOOKLM_PASSWORD=your_password
   ```

That's it! From now on, just tell an LLM what notebooks you want and it will create them for you.

## Features

- **Fast & Parallel** - Creates multiple notebooks simultaneously
- **AI-Powered** - Works seamlessly with any LLM
- **Live Progress** - Watch real-time progress in your terminal
- **Auto-Download** - All materials downloaded locally automatically
- **Flexible** - Create 1 notebook or 10, mix and match artifacts
- **Resumable** - Pause and resume pipelines as needed

## License

This project is designed to work with NotebookLM and follows its terms of service.
