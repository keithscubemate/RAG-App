# RAG App (Fast API + React)

This repository contains the RAG App

# Frontend

To install dependencies:

```bash
cd ./rag_frontend
npm install
npm run build
```

To run:


# Backend

Setup:

```bash
cd ./rag_backend
python3 -m venv .venv
source .venv/bin/activate # Linux/macOS or
.venv\Scripts\activate  # Windows

pip -r requirements.txt
```

Run the app:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```