# AI Resume Analyzer

An AI-powered ATS (Applicant Tracking System) Resume Analyzer. Upload your resume in PDF format, paste a job description, and get instant, streaming AI feedback with an ATS score, match percentage, missing skills, and suggestions.

## Project Structure

```text
ai-resume-analyzer/
│
├── frontend/                          # React + Vite app
│   ├── src/
│   │   ├── components/                # UI components
│   │   │   ├── ResultsPanel/          # Feedback cards
│   │   │   └── ...
│   │   ├── hooks/                     # Custom hooks (e.g. useStreamingAnalysis)
│   │   ├── services/                  # API communication layer
│   │   ├── context/                   # State contexts
│   │   └── App.jsx
│   ├── vite.config.js
│   └── package.json
│
├── backend/                           # FastAPI app
│   ├── app/
│   │   ├── main.py                    # Entrypoint
│   │   ├── config.py                  # Pydantic Settings
│   │   ├── routers/                   # API routes (/analyze, /health)
│   │   ├── services/                  # Core services (Gemini, PDF Parsing)
│   │   └── models/                    # Pydantic schemas
│   ├── requirements.txt
│   └── Dockerfile
│
├── docker-compose.yml                 # Unified local runner
├── .gitignore
└── .dockerignore
```

## Getting Started

### Local Development

#### Backend Setup
1. Navigate to the backend folder:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file and add your Gemini API Key:
   ```env
   GEMINI_API_KEY=your-gemini-key
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```

#### Frontend Setup
1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the Vite development server:
   ```bash
   npm run dev
   ```
4. Open your browser to `http://localhost:5173`.

---

### Running with Docker

You can run the entire system (frontend build + backend) inside a single containerized environment using Docker.

#### 1. Setup environment variables
Make sure you have populated the backend environment file at `backend/.env` with your credentials:
```env
GEMINI_API_KEY=your_gemini_api_key_here
```

#### 2. Start the container
From the root workspace directory, run:
```bash
docker compose up --build
```
This builds the React static files, installs Python dependencies, and mounts the static files on the Uvicorn server.
Access the app at **`http://localhost:8000`**.
