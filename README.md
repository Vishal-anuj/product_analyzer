# Product Analyzer MVP (Phase 1)

Modular product review aggregator and analyzer.

- Frontend: Next.js + Tailwind + Axios
- Backend: FastAPI
- AI: Ollama local (sentiment + summary)
- DB: MongoDB
- Scraping: Requests/BS4 (Playwright later)

## Project Structure

```
product_analyzer/
  frontend/
  backend/
    models/
    routes/
    services/
    scrapers/
    db/
```

## Prerequisites
- Node.js 18+
- Python 3.10+
- MongoDB running locally or in the cloud
- Ollama installed locally

## Environment Variables

Create `backend/.env` from `backend/.env.example` and `frontend/.env.local` from `frontend/.env.example`.

### Backend
```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=product_analyzer
OLLAMA_HOST=http://localhost:11434
ALLOWED_ORIGINS=http://localhost:3000
``` 

### Frontend
```
NEXT_PUBLIC_API_BASE=http://localhost:8000
```

## Setup & Run

### Backend
```
cd backend
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell: . .venv/Scripts/Activate.ps1
pip install -r requirements.txt
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

### Frontend
```
cd frontend
npm install
npm run dev
```

Open UI: http://localhost:3000

## Test Instructions
- Backend unit tests (pytest):
```
cd backend
pytest -q
```
- Frontend basic start test (manual UI): search any product and observe loading + results.

## API
- `GET /health` → health check
- `GET /analyze?product=iphone%2015` → triggers scrape → analyze → returns JSON

## Next Steps
- Implement Flipkart/Croma/Reliance scrapers
- Replace mock analysis fallback with real Ollama prompts
- Add Playwright for dynamic pages
- Add Docker Compose for full stack
- Add charts and richer UI states

## Contributing
- Use GitHub Issues for tasks
- Feature branches + PRs
- Meaningful commit messages
