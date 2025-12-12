# Valorant Coach

This FastAPI + SQLAlchemy + JS frontend experience bridges Valorant-inspired coaching tools with a secure JWT backend and SQLite/Postgres persistence depending on the environment. Log matches, track strategies, and push squadwork through a polished dashboard instead of the old calculator workflows.

## Environment & Local Run

- The application reads `DATABASE_URL`, `JWT_SECRET_KEY`, and `JWT_REFRESH_SECRET_KEY` from `app/core/config.py` and fails early if any values are missing, so exporting them before startup is mandatory. Use the same secrets in Docker Compose via `.env.production` or your own env file for local runs.
- For local development you only need SQLite + the static secrets shown below. Run the app with:

```bash
DATABASE_URL=sqlite:///./app.db \
JWT_SECRET_KEY=dev-secret \
JWT_REFRESH_SECRET_KEY=dev-refresh \
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Keep the terminal open while the server spins up. The landing page, login, registration, and dashboard templates (all under `templates/`) hit the auth and match routes described in `app/routes/` directly.

## Containerization

- The Dockerfile is built on `python:3.12-slim`, installs the dependencies listed in `requirements.txt`, exposes port **8000** inside the container, and launches `uvicorn app.main:app --host 0.0.0.0 --port 8000` so Compose can route traffic to it on port 9000.
- Compose uses the published image `solaimon/valo-project-1:latest` along with a Postgres 15 service. The app service loads secrets from `.env.production`, depends on `db`, and forwards host port 9000 to the container port 8000 used by Uvicorn.
- The Postgres service is configured with the matching database/user/password expected by the app (`valo_db`, `valo_user`, `valo_pass`) and stores data in the named volume `postgres-data` so your match/strategy history survives restarts.

### Sample `.env.production`

Create this file (outside of version control) before running Compose so the app and tests share the same credentials:

```dotenv
DATABASE_URL=postgresql://valo_user:valo_pass@db:5432/valo_db
JWT_SECRET_KEY=replace-with-secure-secret
JWT_REFRESH_SECRET_KEY=replace-with-refresh-secret
```

## Tests & CI

- Run every suite locally or in CI with the same environment variables the tests currently expect:

```bash
DATABASE_URL=sqlite:///./test.db \
JWT_SECRET_KEY=test \
JWT_REFRESH_SECRET_KEY=test \
python -m pytest
```

- This command keeps the in-memory SQLite database, the JWT secrets, and the FastAPI app aligned with the newer Valorant architecture, so the unit/integration suite and coverage tools all share the same context.

## DigitalOcean Deployment

Run these commands on your DigitalOcean droplet so the Valorant Coach stack lives under `/opt/valo-project-1` and exposes port 9000 (while Project 14 remains on port 8000):

```bash
sudo mkdir -p /opt/valo-project-1
cd /opt/valo-project-1
if [ -d .git ]; then
  git fetch origin
  git reset --hard origin/main
  git pull origin main
else
  git clone https://github.com/solaimon-sharifi/Develop-an-Advanced-Feature-and-Finalize-the-Application.git .
fi
```

Create or overwrite the production env file with secure secrets before running the stack (replace the placeholders):

```bash
cat <<'EOF' > .env.production
DATABASE_URL=postgresql://valo_user:valo_pass@db:5432/valo_db
JWT_SECRET_KEY=<your-production-access-secret>
JWT_REFRESH_SECRET_KEY=<your-production-refresh-secret>
EOF
```

Then pull the latest image and bring the services up on port 9000 (Project 14 continues to use 8000 nearby):

```bash
docker compose pull
docker compose up -d
```

Use `docker compose ps` to verify the `valorant-app` container is bound to port 9000 and `docker compose logs valorant-app` if you need debugging details.
