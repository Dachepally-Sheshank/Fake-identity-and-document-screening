# TRINETRA FastAPI backend

This service screens only synthetic or explicitly authorized test documents. It does not provide legal identity verification.

## Run locally

```powershell
cd C:\Users\STUDENT\Downloads\TRINETRA\backend
Copy-Item .env.example .env
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

OpenAPI documentation: `http://127.0.0.1:8000/docs`.

SQLite is the default. To use PostgreSQL, set `DATABASE_URL` in `.env`, for example:

```text
DATABASE_URL=postgresql+psycopg://trinetra:change-me@localhost:5432/trinetra
```

Install a PostgreSQL SQLAlchemy driver such as `psycopg[binary]` when using that URL.

## Tests

```powershell
python -m pytest -q
```

The demo analysis adapters are deterministic and explicitly labelled in each signal as `deterministic_demo`. They infer synthetic scenarios from allowed demo filenames or the `demo_scenario` request field. Replace the interfaces in `app/services/analysis/contracts.py` with OCR, OpenCV, face-match, and liveness implementations in a later phase.
