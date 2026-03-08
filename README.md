# MyDateQ starter repo

This is a clean starter repository for the real **MyDateQ** app.

It includes:

- a **React + Vite** frontend
- a **FastAPI** backend
- your uploaded **DateQ demo integrated as the initial UI prototype**
- a minimal mocked analysis endpoint for further development
- optional Docker setup for local development

## Structure

```text
mydateq-starter/
├── frontend/         # React + Vite app
├── backend/          # FastAPI app
├── docker-compose.yml
└── README.md
```

## 1. Run locally without Docker

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend URLs:

- API root: `http://localhost:8000/`
- Swagger docs: `http://localhost:8000/docs`
- Health: `http://localhost:8000/api/health`

### Frontend

Open a second terminal:

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```

Frontend URL:

- `http://localhost:5173`

The floating badge in the bottom-right corner shows whether the frontend can reach the backend.

## 2. Run with Docker

From the repo root:

```bash
docker compose up --build
```

Then open:

- frontend: `http://localhost:5173`
- backend: `http://localhost:8000/docs`

## 3. What is already integrated

The provided JSX demo is wired into the frontend as the initial product prototype:

- upload screen
- Jake demo profile
- loading flow
- free report
- pro report

For now, the UI still behaves like the original prototype, which is good for continued product work and polishing.

## 4. Backend starter API

### Health check

```http
GET /api/health
```

Example response:

```json
{
  "status": "ok",
  "service": "mydateq-backend",
  "version": "0.1.0"
}
```

### Mock analysis endpoint

```http
POST /api/analyze-profile
```

Example request:

```json
{
  "platform": "hinge",
  "photo_count": 4,
  "bio": "Engineer, runner, brunch enthusiast",
  "prompts": [
    "Best cheap food at 2am",
    "I cook on date three"
  ]
}
```

Example response:

```json
{
  "dq_score": 6.8,
  "verdict": "Promising",
  "platform": "hinge",
  "breakdown": {
    "photo_quality": 6.3,
    "bio_strength": 7.6,
    "profile_energy": 6.2,
    "platform_fit": 6.3
  },
  "notes": [
    "Backend is currently returning mocked development data.",
    "Wire your real CV / LLM / ranking pipeline into this endpoint next."
  ]
}
```

## 5. Recommended next steps

### Frontend

- split the large demo component into smaller reusable components
- move inline styles into a design system or CSS modules
- connect uploaded photos to real backend analysis
- add routing for landing page / app / pricing / auth
- add forms for bio and prompt input

### Backend

- accept real image uploads
- store jobs and results in a database
- add async processing for CV / vision scoring
- add auth and rate limiting
- separate scoring services from API routes
- add tests for analysis logic

## 6. Suggested first real milestone

A strong next milestone would be:

1. upload 1 to 6 photos from the frontend
2. send them to FastAPI
3. run mocked scoring first
4. show returned score dynamically in the report
5. then replace the mock with real analysis modules

## 7. GitHub setup

After unzipping:

```bash
git init
git add .
git commit -m "Initial MyDateQ starter"
```

Then connect your GitHub repo and push.
# mydateqapp
