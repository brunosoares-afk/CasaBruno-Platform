# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

CasaBruno Platform (codename "cbos") is a home infrastructure management platform. It integrates Home Assistant, Docker, MikroTik, Nginx Proxy Manager, go2rtc, Ollama and an AI assistant ("Fred/Jarvis") behind a FastAPI backend and a React dashboard.

## Architecture

- **Backend** — FastAPI app in `backend/app/`, run inside a Python **venv** (`backend/venv` or the project-root `.venv`), not system Python. Entry point is `backend/app/main.py`, which wires together routers from `app/routers/` and `app/api/` (system, Home Assistant, MikroTik, Docker, network, scenes, Fred AI, Alexa, kernel, config, storage, database, models, services, plugins, events, Tuya, Android integration). Also runnable via Docker: `backend/Dockerfile` builds from `backend/requirements.txt` and starts `uvicorn main:app` on port 8088 (mapped to host port 8090 in `docker-compose.yml`).
- **Frontend** — React 19 + Vite in `frontend/`, using MUI, TanStack Query, Axios, React Router and Recharts.
- **Home Assistant** — runs as its own service in **Docker**, external to this repo; the backend talks to it over HTTP using `HA_URL`/`HA_TOKEN` (see `.env` and `backend/app/config.json`), via `app/core/homeassistant/*` (client, devices, manager, services, states, weather).
- **cbos CLI** — a Typer-based CLI (`tools/cbos_cli`, packaged via `pyproject.toml` as the `cbos` console script) drives operational tasks (doctor, update, backup, restore, deploy, release, docs, logs) — see `Makefile`, which just wraps `cbos <command>`.
- **Config/secrets** — `backend/app/config.json` holds live credentials (Home Assistant token, MikroTik host/user/password, network settings); `.env` holds `APP_NAME`, `APP_VERSION`, `HA_URL`, `HA_TOKEN`, `DOCKER_SOCKET`, `REFRESH_SECONDS`.

## Commands

Backend (from `backend/`, inside the venv):
```
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8088   # or: uvicorn main:app ... if run from backend/app
pytest                                       # tests live under backend/app/tests/ and root tests/
```

Frontend (from `frontend/`):
```
npm run dev       # Vite dev server
npm run build
npm run lint
npm run preview
```

Docker (Home Assistant + backend API container):
```
docker compose up -d
```

cbos CLI (operational tasks, also exposed via `make <target>`):
```
cbos doctor|update|backup|restore|deploy|release|docs|logs
```

## Conventions

- **Never write files to the terminal using large heredocs** (`cat <<'EOF' > file`). Large heredocs trigger terminal paste bugs in this environment and can silently corrupt content. Instead, use the `Write`/`Edit` tools directly, or pipe content through `base64` when a shell one-liner is unavoidable.

## Sensitive areas — confirm before touching

- **`backend/app/config.json`** contains live credentials (Home Assistant token, MikroTik user/password, network config). Do not modify, rotate, or overwrite values in this file without explicit confirmation from the user first, even when the change looks incidental (e.g. reformatting, adding a key nearby).
