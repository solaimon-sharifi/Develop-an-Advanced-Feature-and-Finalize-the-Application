# Calculator BREAD App with Exponent Support

This FastAPI + SQLAlchemy + Playwright application provides a full BREAD (Browse, Read, Edit, Add, Delete) workflow for mathematical calculations tied to authenticated users. The latest enhancement introduces an **Exponent (Power)** operation so you can compute `base^exponent`, store it alongside addition/subtraction/multiplication/division records, and view the result immediately in the dashboard.

## Key Features

- JWT-based authentication with secure password hashing.
- Polymorphic SQLAlchemy calculation models for each operation type.
- Exponent (Power) calculation that accepts two numeric operands (base + exponent) and persists the result with the other history entries.
- Playwright-powered UI tests that log in, perform calculations, and verify validation handling.

## Requirements

- Python 3.12 (3.10+ compatible, the project ships with a `venv`)
- PostgreSQL 13+ (local or via Docker)
- Playwright browsers (`python -m playwright install`)
- Docker / Docker Compose for containerized execution

## Local Setup

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

2. Upgrade pip, install dependencies, and install Playwright browsers:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   python -m playwright install
   ```

3. Configure environment variables or rely on the defaults exposed in `app/core/config.py` (`DATABASE_URL`, `JWT_SECRET_KEY`, `JWT_REFRESH_SECRET_KEY`, `REDIS_URL`, etc.). If you prefer a `.env` file, create one and export it before running the app.

## Running the App Locally

1. Ensure PostgreSQL is running (either locally or via Docker).
2. Initialize the database schema and start the FastAPI server:

   ```bash
   python -m app.database_init
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

3. Open `http://localhost:8000` in your browser, register/log in, select **Exponent (Power)** from the dropdown, supply a base/exponent pair, and submit. The result appears immediately in the calculation history along with the metadata for each operation.

4. Use the API route `POST /calculations` (protected) or the dedicated `/calculate/exponent` route (if you add a separate TypeScript handler) to interact programmatically.

## Running Tests

All suites run through a single command:

```bash
python3 -m pytest
```

This launches the unit, integration, and Playwright E2E tests (it spins up the FastAPI server + Playwright browser as needed). Make sure Playwright browsers are installed beforehand. If you want selective runs, the tests are organized into `tests/unit/`, `tests/integration/`, and `tests/e2e/`.

## Docker

### Build

```bash
docker build -t test-calculator .
```

### Run

```bash
docker run --rm -p 8000:8000 \
  -e DATABASE_URL="postgresql://postgres:postgres@db-host:5432/fastapi_db" \
  -e JWT_SECRET_KEY="your-secure-key" \
  -e JWT_REFRESH_SECRET_KEY="your-refresh-key" \
  -e REDIS_URL="redis://redis-host:6379/0" \
  test-calculator
```

Replace `db-host`/`redis-host` with the appropriate PostgreSQL and Redis hosts (Docker service names, `localhost`, etc.), and set JWT secrets to production-safe values. Once the container is running, verify it by curling `http://localhost:8000/health` or opening `http://localhost:8000/dashboard` in the browser.

Alternatively, lift the full stack with Docker Compose (`web`, `db`, `pgadmin`), which wires up `postgres:17` and exposes the calculator at `http://localhost:8000` and pgAdmin at `http://localhost:5050` (use `admin@example.com` / `admin`).

## Docker Hub Image

The pipeline publishes `solaimon/module14_is601` (latest and SHA-tagged) to Docker Hub. Browse the pushed image here:

https://hub.docker.com/r/solaimon/module14_is601

## CI/CD

`.github/workflows/test.yml` now:

1. Checks out the code and sets up Python 3.10.
2. Installs dependencies, Playwright, and runs `python3 -m pytest` with coverage + JUnit output.
3. Builds an intermediate Docker image and scans it with Trivy (fails on critical/high findings).
4. Logs in to Docker Hub and pushes the image as `solaimon/module14_is601:latest` and `solaimon/module14_is601:${{ github.sha }}` once tests/security scan pass.

Look for log lines like `Login Succeeded` and `pushed image solaimon/module14_is601:latest` to confirm success.

## Reflection

See `REFLECTION.md` for a recap of what was implemented, obstacles encountered, how testing was performed, and how CI/CD/deployment currently works.# Calculator BREAD App

FastAPI + SQLAlchemy + Playwright starter for the Module 14 calculator assignment. Users can register, authenticate, and perform full BREAD (Browse / Read / Edit / Add / Delete) calculations that stay scoped to their account.

The latest feature adds an **Exponentiation** (power) operation so users can calculate `base ^ exponent`, see the result immediately in the dashboard refresh, and persist it alongside addition, subtraction, multiplication, and division records.

## Requirements

- Python 3.10+ (tested with 3.10.13)
- PostgreSQL (local or Docker)
- [Playwright](https://playwright.dev/python/docs/intro) for the UI tests
- Docker / Docker Compose for containerized runs

## Local Setup

1. Create and activate the project virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Upgrade pip and install the pinned dependencies:

```bash
pip install --upgrade pip
pip install -r requirements.txt
playwright install
```

3. Keep the virtual environment active whenever you work in this repo. You can also prefix tools with `.venv/bin/` (e.g., `.venv/bin/pytest`) if you forget to activate; this guarantees the same dependency set without relying on the system Python.

4. Copy `.env.example` (if present) or export the required environment variables such as `DATABASE_URL`, `JWT_SECRET_KEY`, etc. Defaults in `app/core/config.py` point at `postgresql://postgres:postgres@localhost:5432/fastapi_db`.

## Running the App

### Local Run

Make sure Postgres is running (local or Docker). Grow the schema and start the dev server with:

```bash
python -m app.database_init
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Head to `http://localhost:8000`, log in, pick the new **Power** operation, supply a base/exponent pair, and watch it appear in your calculation history alongside the other BREAD operations.

### Containerized Run

You can also run the app inside a Docker container:

```bash
docker build -t solaimon/module14_is601:latest .
docker run --rm -p 8000:8000 solaimon/module14_is601:latest
```

Or boot everything with Compose (web + Postgres + pgAdmin):

```bash
docker-compose up --build
```

The Compose stack exposes the calculator at `http://localhost:8000` and pgAdmin at `http://localhost:5050` (admin@example.com / admin). The power operation is available in the same dashboard form.

You can automate a full rebuild and log inspection with the helper script:

```bash
chmod +x scripts/docker_rebuild_logs.sh
scripts/docker_rebuild_logs.sh
```

## Running Tests Locally

```bash
source .venv/bin/activate
pytest tests/unit/
pytest tests/integration/
pytest tests/e2e/
```

Playwright-based E2E tests exercise login + BREAD flows through the UI. The `tests/conftest.py` fixture boots the FastAPI server and a Playwright browser session automatically.
The Playwright suite now covers the new Power operation, so remember to run `playwright install` before hitting `tests/e2e/` if you have not installed the browsers yet.

## Docker

Build the image and run a container:

```bash
docker build -t solaimon/module14_is601:latest .
docker run --rm -p 8000:8000 solaimon/module14_is601:latest
```

Or use Docker Compose to run the web app alongside PostgreSQL and pgAdmin:

```bash
docker-compose up --build
```

The Compose file exposes the calculator at `http://localhost:8000` and pgAdmin at `http://localhost:5050` (admin@example.com / admin).

You can automate a full rebuild and log check with the supplied helper script:

```bash
chmod +x scripts/docker_rebuild_logs.sh
scripts/docker_rebuild_logs.sh
```
This script runs `docker-compose down`, rebuilds the services with `--no-cache`, brings everything up detached, and streams the latest logs so you can verify startup.

## CI/CD & Docker Hub

GitHub Actions (`.github/workflows/test.yml`) now:

1. Boots a PostgreSQL service
2. Installs dependencies + Playwright browsers
3. Runs unit, integration, and E2E suites (pytest)
4. Builds a Docker image and scans it with Trivy
5. Pushes multi-arch image to Docker Hub as `solaimon/module14_is601:latest` and `solaimon/module14_is601:${{ github.sha }}` when `DOCKERHUB_USERNAME`/`DOCKERHUB_TOKEN` secrets are provided and the `main` branch is updated

Verify the workflow run and Docker Hub tags via the GitHub Actions logs/history for grading artifacts.
Browse the pushed image on Docker Hub: https://hub.docker.com/r/solaimon/module14_is601.

## Reflection / Follow-up

- See `REFLECTION.md` for prompts you can expand on before submission.
- Update the `docs/` directory if you extend the feature set beyond the base assignment.
