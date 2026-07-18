"""
FastAPI application entrypoint.

Responsibilities of this file (and ONLY this file):
  1. Create the FastAPI app instance
  2. Attach middleware (CORS)
  3. Mount routers (health, analyze)
  4. Serve the built React frontend as static files (production only)

Business logic never lives here — it lives in routers/ and services/.
This keeps main.py small and easy to reason about even as the app grows.
"""

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import analyze, health

app = FastAPI(
    title=settings.APP_NAME,
    description="Upload a resume + job description and get an AI-powered ATS analysis.",
    version="0.1.0",
)

# --- CORS ---
# Needed so the Vite dev server (http://localhost:5173) can call the API
# during local development. In production (single-container deployment)
# the frontend and backend share an origin, so CORS is less critical there,
# but we keep it configurable via CORS_ORIGINS for flexibility.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API routers ---
# All API routes are grouped under settings.API_PREFIX (default "/api") so
# they're clearly namespaced away from the static frontend routes below.
app.include_router(health.router, prefix=settings.API_PREFIX)
app.include_router(analyze.router, prefix=settings.API_PREFIX)


# --- Static frontend (production) ---
# In Step 6 (Dockerfile), the React build output (frontend/dist) is copied
# into backend/static at image build time. If that folder exists, we mount
# it so FastAPI serves the SPA directly — this is what makes the
# "single container" deployment approach work on App Runner.
#
# In local dev, this folder won't exist yet (you'll run Vite separately),
# so this block is safely skipped — no errors, no missing-folder crashes.
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.isdir(STATIC_DIR):
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
