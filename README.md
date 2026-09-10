# TRINETRA

AI-Based Fake Identity and Document Screening System for Smart India Hackathon 2026, problem statement `SIH26188`.

## Live demo

Open the website from any device:

**[https://dachepally-sheshank.github.io/Fake-identity-and-document-screening/](https://dachepally-sheshank.github.io/Fake-identity-and-document-screening/)**

The live demo uses only synthetic test documents. It provides screening indicators, not legally valid identity verification.

## Architecture

- Frontend: React, TypeScript, Tailwind CSS
- Backend: FastAPI, SQLAlchemy, SQLite for the prototype
- Audit: hash-only local audit ledger
- Deployment: GitHub Pages frontend with a Render-hosted FastAPI backend

## Run locally

Start the API:

```powershell
cd backend
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --port 8000
```

In a second terminal, start the frontend:

```powershell
cd frontend
pnpm install
pnpm run dev
```

Open `http://localhost:5173/`.

## Safety

Do not upload real Aadhaar, PAN, passport, or any other personal identity documents. Use only synthetic, public, or explicitly authorized test data.
