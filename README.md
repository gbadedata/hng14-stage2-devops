# Jobpilot

A containerized job processing system with a full CI/CD pipeline. Built as part of HNG14 Stage 2 DevOps assessment.

## Architecture

- **Frontend** — Node.js / Express. Users submit jobs and track their status.
- **API** — Python / FastAPI. Creates jobs and serves status updates.
- **Worker** — Python. Picks up jobs from the Redis queue and processes them.
- **Redis** — Shared queue and state store between the API and worker.

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed and running
- [Git](https://git-scm.com/)
- No cloud account required — runs entirely on your machine

## Quick start

### 1. Clone the repository

```bash
git clone https://github.com/gbadedata/hng14-stage2-devops
cd hng14-stage2-devops
```

### 2. Create your environment file

```bash
cp .env.example .env
```

The defaults in `.env.example` work out of the box for local development. No edits needed.

### 3. Start the full stack

```bash
docker compose up --build
```

### 4. Verify everything is running

You should see output like this:

```
redis-1     | Ready to accept connections tcp
api-1       | Uvicorn running on http://0.0.0.0:8000
frontend-1  | Frontend running on port 3000
```

All four containers should reach a healthy state:

```bash
docker compose ps
```

Expected output:

```
NAME                            STATUS
hng14-stage2-devops-redis-1     running (healthy)
hng14-stage2-devops-api-1       running (healthy)
hng14-stage2-devops-worker-1    running
hng14-stage2-devops-frontend-1  running (healthy)
```

### 5. Open the app

Go to http://localhost:3000 in your browser.

Click **Submit New Job** — the job will appear as `queued` and transition to `completed` within a few seconds.

## Running tests locally

```bash
cd api
pip install -r requirements.txt
python -m pytest tests/ -v --cov=. --cov-report=term
```

## Stopping the stack

```bash
docker compose down
```

To also remove volumes:

```bash
docker compose down -v
```

## Environment variables

| Variable | Description | Default |
|---|---|---|
| REDIS_HOST | Redis service hostname | redis |
| REDIS_PORT | Redis port | 6379 |
| REDIS_PASSWORD | Redis password (optional) | empty |
| FRONTEND_PORT | Host port for the frontend | 3000 |
| API_URL | API URL seen by the frontend | http://api:8000 |

## CI/CD Pipeline

The pipeline runs automatically on every push via GitHub Actions with these stages in strict order:

1. **Lint** — flake8 (Python), eslint (JavaScript), hadolint (Dockerfiles)
2. **Test** — pytest with coverage report uploaded as artifact
3. **Build** — all three images built and pushed to a local registry tagged with git SHA and latest
4. **Security scan** — Trivy scans all images, SARIF results uploaded as artifact
5. **Integration test** — full stack started inside the runner, job submitted and polled to completion, stack torn down
6. **Deploy** — rolling update to production server, runs on main branch only, skipped gracefully if no server secrets configured

## Project structure

```
.
├── api/                    # FastAPI backend
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── tests/
│       └── test_main.py
├── worker/                 # Job processor
│   ├── worker.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/               # Express frontend
│   ├── app.js
│   ├── package.json
│   ├── package-lock.json
│   ├── Dockerfile
│   └── views/
│       └── index.html
├── docker-compose.yml
├── integration-test.sh
├── .env.example
├── .gitignore
├── FIXES.md
└── README.md
```
