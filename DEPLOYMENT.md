# Deployment Guide

## Architecture

- Frontend: Render Static Site
- Backend: Render Web Service
- Database: Supabase Postgres

The backend also works locally without Supabase. It automatically falls back to a local SQLite database in `backend/data/local.db`.

## 1. Supabase Setup

1. Create a new Supabase project.
2. Open the SQL editor.
3. Run the SQL from `backend/supabase_schema.sql`.
4. In Supabase project settings, copy:
   - `Project URL` as `SUPABASE_URL`
   - `service_role` key as `SUPABASE_SERVICE_ROLE_KEY`

## 2. Backend on Render

1. Create a new Web Service from this repo.
2. Render can auto-detect `render.yaml`, or you can set it manually:
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/health`
3. Set these environment variables in Render:
   - `HF_TOKEN`
   - `GROQ_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `CORS_ORIGINS`

Example `CORS_ORIGINS`:

```env
https://your-frontend-name.onrender.com,http://localhost:3000
```

## 3. Frontend on Render

1. Create a new Static Site from this repo.
2. Use:
   - Root directory: `frontend`
   - Build command: `npm ci && npm run build`
   - Publish directory: `build`
3. Set:
   - `REACT_APP_BACKEND_URL=https://your-backend-name.onrender.com`
   - `WDS_SOCKET_PORT=443`
   - `ENABLE_HEALTH_CHECK=false`

## 4. Local Development

Backend:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn server:app --reload --port 8001
```

Frontend:

```bash
cd frontend
cp .env.example .env
npm install
npm start
```

## 5. Important Notes

- Use Node `20.18.0` or another Node 20 LTS release for the frontend build.
- Use Python `3.11` on Render for the backend.
- If Hugging Face or Groq is temporarily unavailable, the backend now returns a safe fallback response instead of crashing.
