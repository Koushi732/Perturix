# Deployment Guide

## Prerequisites
- Python 3.12+ (Backend)
- Node.js 20+ (Frontend)

## 1. Backend Setup
```bash
cd backend

# Install dependencies using UV (or pip)
uv sync

# Initialize database schema
uv run alembic upgrade head

# Start the server
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000
```
This will start the FastAPI backend locally at `http://localhost:8000`.

## 2. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```
The React frontend will be accessible at `http://localhost:5173`.

## 3. Production Build
To prepare the frontend for production deployment (Nginx/Vercel):
```bash
npm run build
```
Serve the `dist/` directory via a static web server.
