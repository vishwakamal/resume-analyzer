# Resume-Analyzer

## What it does
Analyzes resumes using Ollama's local AI (Mistral model). No cloud API needed.

## Stack
- Python 3
- Ollama (local, must be running)
- Mistral model

## Run
```bash
ollama run mistral
pip3 install -r requirements.txt
python3 analyze.py
```

## Key files
- `analyze.py` — main script, edit sample_resume here

## Conventions
- No external AI APIs, local only
