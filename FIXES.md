# FIXES.md

## Fix 1
- **File**: `api/main.py`, line 7
- **Problem**: Redis client hardcoded to `localhost`. Inside Docker, containers communicate via service names, not localhost.
- **Fix**: Changed to `os.getenv("REDIS_HOST", "redis")` and `os.getenv("REDIS_PORT", 6379)`.

## Fix 2
- **File**: `api/main.py`, line 7
- **Problem**: Redis connection did not read `REDIS_PASSWORD` from environment. If Redis requires auth, all connections silently fail.
- **Fix**: Added `password=os.getenv("REDIS_PASSWORD", None)` to Redis client.

## Fix 3
- **File**: `api/main.py`, line 6
- **Problem**: No `/health` endpoint existed. The Dockerfile HEALTHCHECK and integration test both require one.
- **Fix**: Added `GET /health` endpoint returning `{"status": "ok"}`.

## Fix 4
- **File**: `api/main.py`, line 17
- **Problem**: Missing job returned HTTP 200 with `{"error": "not found"}` instead of a proper 404. This breaks integration test assertions and REST conventions.
- **Fix**: Changed to `raise HTTPException(status_code=404, detail="Job not found")`.

## Fix 5
- **File**: `api/main.py`, line 11
- **Problem**: Queue key named `"job"` (singular) was inconsistent and misleading.
- **Fix**: Renamed to `"jobs_queue"` in both API and worker for clarity and consistency.

## Fix 6
- **File**: `api/Dockerfile`
- **Problem**: Uvicorn was not explicitly bound to `0.0.0.0`. Default binding to `127.0.0.1` inside a container makes the service unreachable from other containers.
- **Fix**: Added `--host 0.0.0.0` to the CMD in `api/Dockerfile`.

## Fix 7
- **File**: `api/requirements.txt`
- **Problem**: No version pins on any dependency. Builds are not reproducible — a new release of fastapi, uvicorn, or redis could silently break the app.
- **Fix**: Pinned all dependencies to specific versions.

## Fix 8
- **File**: `worker/worker.py`, line 5
- **Problem**: Redis client hardcoded to `localhost`. Fails inside Docker for the same reason as Fix 1.
- **Fix**: Changed to `os.getenv("REDIS_HOST", "redis")` and `os.getenv("REDIS_PORT", 6379)`.

## Fix 9
- **File**: `worker/worker.py`, line 5
- **Problem**: `import sys` was present but `sys` was never used anywhere in the file.
- **Fix**: Removed the unused import.

## Fix 10
- **File**: `worker/worker.py`
- **Problem**: No error handling around job processing. Any exception in `process_job` would crash the entire worker loop permanently, leaving jobs stuck as `queued` forever.
- **Fix**: Wrapped the loop body in a `try/except` block that logs the error and continues.

## Fix 11
- **File**: `worker/worker.py`
- **Problem**: `signal` was imported but never used. Docker sends `SIGTERM` on container stop — without handling it, the worker is killed mid-job leaving jobs in a broken state.
- **Fix**: Added `signal.signal(SIGTERM)` and `signal.signal(SIGINT)` handlers that set a `running` flag to False for graceful shutdown.

## Fix 12
- **File**: `frontend/app.js`, line 5
- **Problem**: API URL hardcoded to `http://localhost:8000`. Inside Docker, the frontend container cannot reach the API via localhost — it must use the service name `api`.
- **Fix**: Changed to `process.env.API_URL || "http://api:8000"`.

## Fix 13
- **File**: `frontend/app.js`
- **Problem**: No `/health` endpoint on the frontend. The Dockerfile HEALTHCHECK requires one.
- **Fix**: Added `GET /health` endpoint returning `{"status": "ok"}`.

## Fix 14
- **File**: `frontend/package.json`
- **Problem**: No `lint` script defined. The CI pipeline runs `npm run lint` which would fail.
- **Fix**: Added `"lint": "eslint app.js"` to the scripts section.

## Fix 15
- **File**: `frontend/views/index.html`, line 47
- **Problem**: Em dash character was corrupted to `â€"` due to UTF-8 encoding mismatch. Rendered as garbage characters in the browser.
- **Fix**: Replaced with a plain hyphen and ensured file is saved as UTF-8.

## Fix 16
- **File**: `frontend/views/index.html`
- **Problem**: `pollJob` function had no error guard. If the API returned `{"error": "..."}`, `data.status` would be `undefined`, which is not `"completed"`, causing infinite polling.
- **Fix**: Added `if (data.error)` check that stops polling and renders an error state.

## Fix 17
- **File**: `api/.env`
- **Problem**: A real `.env` file containing `REDIS_PASSWORD=supersecretpassword123` was committed to the repository in the original source. Credentials in git history are a critical security violation.
- **Fix**: Removed file from git tracking, purged from full git history using `git filter-repo`, added `.gitignore` to prevent recurrence.
