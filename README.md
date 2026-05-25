## Prerequisites
- Python 3.10+
- Node.js 18+
- Ollama installed (https://ollama.com)

## Setup

### 1. Pull Ollama models
ollama pull llama3
ollama pull nomic-embed-text

### 2. Start Ollama
ollama serve

### 3. Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload

### 4. Frontend
cd frontend
npm install
npm run dev

### 5. Open
http://localhost:3000

## File Structure
backend/
  main.py
  extractor.py
  ollama_client.py
  session_manager.py
  requirements.txt
frontend/
  app/
    page.tsx
README.md
