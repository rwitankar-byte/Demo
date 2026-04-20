# Deployment Guide

## Architecture

- Frontend: Render Static Site
- Backend: Render Web Service
- Database: none

This version is stateless. It does not store farmer images, history, or user records.

## 1. Backend on Render

1. Create a new Web Service from this repo.
2. Render can auto-detect `render.yaml`, or you can set it manually:
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
   - Health check path: `/health`
3. Set these environment variables in Render:
   - `HF_TOKEN`
   - `GROQ_API_KEY`
   - `CORS_ORIGINS`

Example `CORS_ORIGINS`:

```env
https://your-frontend-name.onrender.com,http://localhost:3000
```

## 2. Frontend on Render

1. Create a new Static Site from this repo.
2. Use:
   - Root directory: `frontend`
   - Build command: `yarn install --frozen-lockfile && yarn build`
   - Publish directory: `build`
3. Set:
   - `REACT_APP_BACKEND_URL=https://your-backend-name.onrender.com`
   - `WDS_SOCKET_PORT=443`
   - `ENABLE_HEALTH_CHECK=false`

## 3. Local Development

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
yarn install
yarn start
```

## 4. Important Notes

- Use Node `20.18.0` or another Node 20 LTS release for the frontend build.
- Use Python `3.11` on Render for the backend.
- A public frontend-only deployment is not recommended because it would expose your Hugging Face and Groq API keys.
- If Hugging Face or Groq is temporarily unavailable, the backend returns a safe fallback response instead of crashing.
