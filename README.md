# JobSeekingAgent

JobSeekingAgent is being rebuilt as a Docker-first web platform for job seeking automation, AI-assisted application workflows, community communication, and user/account management.

The current architecture uses React for the frontend, FastAPI microservices for the backend, separate databases for identity/communication and AI vector data, Redis/Celery for background work, MinIO for files, and Nginx as the public gateway.

## Stack

- Frontend: React 19, TypeScript, Vite, Bootstrap, React Icons, React Markdown, KaTeX
- Routing: React Router
- Backend: Python FastAPI microservices
- Services:
  - `identity-service`: authentication, users, identity, Stripe customer linkage
  - `communication-service`: forum, notifications, activity feeds
  - `ai-service`: AI chat, indexing, vector retrieval
  - `crawler-service`: private job crawling and job database update backend
- Databases:
  - MySQL 8 for identity and communication data
  - PostgreSQL 17 + pgvector for AI vector data
- Cache and queue: Redis + Celery
- Object storage: MinIO
- AI: Google Gemini API, LangGraph, LangChain, pgvector
- Payments: Stripe
- Gateway: Nginx
- Shared Python package: `platform_common`

## Project Layout

```text
.
├── apps/
│   └── web/                         # React 19 + TypeScript + Vite frontend
├── services/
│   ├── identity-service/            # FastAPI identity/auth service
│   ├── communication-service/       # FastAPI forum/notification service
│   ├── ai-service/                  # FastAPI AI/chat/indexing service
│   └── crawler-service/             # Private job crawling backend
├── packages/
│   └── platform_common/             # Shared Python settings, health, utilities
├── infra/
│   ├── docker-compose.yml
│   ├── docker/
│   │   ├── python-service.Dockerfile
│   │   └── web.Dockerfile
│   ├── nginx/
│   ├── mysql/
│   └── postgres/
├── src/jobseeking_agent/            # Legacy job automation modules during migration
├── tests/
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## Quick Start

Create a local environment file:

```bash
cp .env.example .env
```

Start the full platform:

```bash
docker compose --env-file .env -f infra/docker-compose.yml up -d --build
```

Open:

```text
http://localhost:8080
```

Useful service endpoints:

```text
http://localhost:8080/api/identity/health
http://localhost:8080/api/communication/health
http://localhost:8080/api/ai/health
http://localhost:8090/health
http://localhost:9001
```

If a host port is already in use, change the matching `*_HOST_PORT` value in `.env`.
For example, if local MySQL already uses `3306`:

```env
MYSQL_HOST_PORT=3307
```

Common host port settings:

```env
WEB_HOST_PORT=8080
MYSQL_HOST_PORT=3306
POSTGRES_HOST_PORT=5432
REDIS_HOST_PORT=6379
MINIO_API_HOST_PORT=9000
MINIO_CONSOLE_HOST_PORT=9001
CRAWLER_HOST_PORT=8090
```

## Private Crawler Backend

The user-facing website reads saved jobs. The crawler backend is separate and is used by the project owner to crawl and refresh job listings in the shared job database.

Default crawler URL:

```text
http://localhost:8090
```

Open the private crawler dashboard:

```text
http://localhost:8090
```

Run one crawl:

```bash
curl -X POST http://localhost:8090/crawl/once \
  -H "Content-Type: application/json" \
  -d '{"keywords":"backend engineer","location":"Sydney","platform":"seek"}'
```

Run an official company careers crawl:

```bash
curl -X POST http://localhost:8090/crawl/company \
  -H "Content-Type: application/json" \
  -d '{"company_name":"Amazon Web Services","keywords":"software engineer","location":"Sydney"}'
```

List discovered company sources:

```bash
curl http://localhost:8090/companies
```

Run the configured keyword/location/platform batch:

```bash
curl -X POST http://localhost:8090/crawl/run \
  -H "Content-Type: application/json" \
  -d '{}'
```

Configure defaults in `.env`:

```env
CRAWLER_DEFAULT_KEYWORDS=software engineer,backend engineer,full stack developer
CRAWLER_DEFAULT_LOCATIONS=Sydney,Melbourne,Remote
CRAWLER_DEFAULT_PLATFORMS=seek,linkedin,indeed
CRAWLER_ADMIN_TOKEN=
CRAWLER_PROVIDER=auto
CRAWLER_OFFICIAL_APPLY_ONLY=true
CRAWLER_ALLOW_SEARCH_DISCOVERY=true
JOBSPY_RESULTS_WANTED=25
JOBSPY_HOURS_OLD=168
JOBSPY_COUNTRY_INDEED=Australia
JOBSPY_LINKEDIN_FETCH_DESCRIPTION=true
JOBSPY_PROXIES=
BROWSER_STORAGE_DIR=./data/browser-states
```

If `CRAWLER_ADMIN_TOKEN` is set, include it in crawler requests:

```bash
curl -H "X-Crawler-Token: your-token" http://localhost:8090/config
```

The crawler flow is official-apply first. With `CRAWLER_PROVIDER=auto`, supported platforms use JobSpy to discover job leads and descriptions, then the ATS resolver tries to enrich each lead with a company careers or ATS URL such as Greenhouse, Lever, Ashby, Workday, SmartRecruiters, Amazon Jobs, or another official careers page. Unsupported platforms fall back to the existing Playwright crawler. Set `CRAWLER_PROVIDER=jobspy` to force JobSpy for supported platforms, or `CRAWLER_PROVIDER=playwright` to force the browser crawler. Jobs without an external apply URL are skipped when `CRAWLER_OFFICIAL_APPLY_ONLY=true`.

Create a logged-in browser session locally before running the Docker crawler:

```bash
python3 -m jobseeking_agent crawler login seek
python3 -m jobseeking_agent crawler login linkedin
python3 -m jobseeking_agent crawler login indeed
```

The login helper uses your installed Google Chrome by default because some job boards reject generic automation Chromium as an insecure browser. You can choose another browser channel:

```bash
python3 -m jobseeking_agent crawler login linkedin --browser chrome
python3 -m jobseeking_agent crawler login linkedin --browser msedge
python3 -m jobseeking_agent crawler login linkedin --browser chromium
```

These commands save Playwright storage state files under `data/browser-states/`. The Docker crawler mounts `data/` and reads those files; it does not store account passwords.

The preferred official-link path is company-first: use job boards to discover titles and companies, then scan company career pages and ATS sources directly. The crawler stores company sources in `companies` and currently supports Greenhouse, Lever, Amazon Jobs search pages, and conservative generic career-page link extraction.

The user-facing job search reads from the shared job database. On the first search of each keyword/location/platform combination per UTC day, `ai-service` asks the private `crawler-service` to refresh that query, then returns the updated saved database results. Repeating the same search later that day uses the database only, which keeps crawler traffic controlled.

Stop everything:

```bash
docker compose --env-file .env -f infra/docker-compose.yml down --remove-orphans
```

Stop and remove database/object-storage volumes:

```bash
docker compose --env-file .env -f infra/docker-compose.yml down --remove-orphans -v
```

## Local Frontend Development

```bash
cd apps/web
npm install
npm run dev
```

Vite runs on:

```text
http://localhost:5173
```

API calls under `/api` proxy to Nginx on `http://localhost:8080`.
If you change `WEB_HOST_PORT`, update `VITE_API_PROXY_TARGET` in `.env` for local Vite development.

## Local Python Checks

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
python -m ruff check .
python -m pytest
```

## Architecture Notes

- New frontend work should go in `apps/web`.
- New API work should go in the matching service under `services/`.
- Shared Python helpers belong in `packages/platform_common`.
- Identity and communication data should use MySQL.
- AI embeddings, indexed documents, and vector retrieval data should use PostgreSQL with pgvector.
- Long-running AI/indexing jobs should run through Celery workers backed by Redis.
- Uploaded resumes, generated files, and indexed source documents should go to MinIO.
- The old Qt desktop UI and Streamlit UI have been removed from the active architecture.

## GitHub Branch Policy

Recommended repository rules:

- Block direct pushes to `main`
- Require pull requests into `main`
- Only allow `develop` to merge into `main`
- Require CI checks before merge
- Keep feature work on short-lived branches and merge into `develop`
