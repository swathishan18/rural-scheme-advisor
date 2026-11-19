# Rural Scheme Advisor

A professional, multilingual rural government scheme assistance web application built with
Streamlit, SQLite and an existing Agentic RAG pipeline.

The project preserves `agent.py`, `rag.py`, `eligibility.py`, `config.py`, the multilingual
embedding model, the Nexus API configuration and all existing documents in `data/`.

## Features

- Secure registration and login with PBKDF2 password hashing
- Personalised dashboard
- Tamil and English scheme questions
- Agentic RAG with source excerpts
- Scheme explorer
- Preliminary eligibility checker
- Saved, user-owned chat conversations
- Profile and eligibility-profile management
- Secure logout

## Existing configuration

This project continues to read `NEXUS_API_KEY`, `NEXUS_BASE_URL` and `NEXUS_MODEL`
through `config.py` and the existing `.env` file. Do not copy or publish the `.env` file.

## Installation on Windows

Open VS Code in the project directory and run:

```powershell
py -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use:

```powershell
venv\Scripts\activate.bat
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the URL printed by Streamlit, normally `http://localhost:8501`.

## Adding scheme documents

Place official `.txt` or `.pdf` documents in `data/`. The existing retriever indexes them
automatically when the app restarts.

## Database

SQLite data is stored in `rural_scheme_advisor.db` in this project directory. It is created
automatically with parameterised SQL and foreign-key relationships.

## Important limitation

Eligibility output is a preliminary screening, not official approval. Users should verify
current rules, documents and benefits on official government websites or at a CSC/panchayat office.

## Architecture

User -> profile extraction -> multilingual RAG retrieval -> eligibility tool -> Nexus answer synthesis
