# syntax=docker/dockerfile:1

# =============================================================================
# Stage 1: Build the React frontend
# =============================================================================
# Uses a full Node image just for the build step - none of this ends up in
# the final image, so image size doesn't matter here.
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy only the dependency manifests first, so Docker can cache the
# install layer and skip re-running it on every build unless
# package.json/package-lock.json actually change.
#
# NOTE: `npm ci` requires package-lock.json to exist (it's the whole point
# - reproducible installs from an exact lockfile). Your frontend/ folder
# should already have one from Step 2's `npm install`. If this build fails
# with "The `npm ci` command can only install with an existing
# package-lock.json", run `npm install` once locally to generate it, then
# rebuild.
COPY frontend/package*.json ./
RUN npm ci

# Now copy the rest of the frontend source and build the production bundle.
COPY frontend/ ./
RUN npm run build
# Output lands in /app/frontend/dist


# =============================================================================
# Stage 2: The actual runtime image (this is what App Runner deploys)
# =============================================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Install Python dependencies first (same caching logic as above - this
# layer is skipped on rebuilds unless requirements.txt changes).
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the actual backend application code.
COPY backend/app ./app

# Copy the built frontend from Stage 1 into ./static - a SIBLING of ./app,
# not inside it. main.py specifically looks for "../static" relative to
# its own location (app/main.py), so this path must match exactly:
#   /app/app/main.py  ->  looks for  ->  /app/static
COPY --from=frontend-builder /app/frontend/dist ./static

# App Runner (and most container platforms) expect the app to listen on
# the port specified by the PORT env var, defaulting to 8000 if unset.
ENV PORT=8000
EXPOSE 8000

# No --reload here (that's a dev-only feature) - production runs the
# plain, stable uvicorn process.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]