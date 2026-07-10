# NMT Agent Infrastructure and Development

This folder contains infrastructure configuration for local development and
docker-compose-based deployment.

Contents:
- docker-compose.yml: Compose stack for Postgres, MinIO, FastAPI backend, and ML service.
- .env.example: template for every optional backend value (secrets, SMTP, OAuth, Stripe). Copy to `.env` and fill in real values — `.env` is gitignored, `.env.example` is the committed template.

## Setting real values (production / commercialization)

1. `cp infra/.env.example infra/.env`
2. Edit `infra/.env` — every variable there has a comment on what it does and where to get the real value (Stripe Dashboard, Google Cloud Console, GitHub OAuth Apps, your email provider, etc.). Everything is optional; leave a value blank to keep that feature gracefully disabled.
3. Run `docker compose` **from inside this `infra/` directory** so it picks up `infra/.env` automatically:
   ```bash
   cd infra
   docker compose up --build
   ```
4. Backend API available at http://localhost:8000/docs
5. MinIO Console at http://localhost:9001 (user: minioadmin / pass: minioadmin)

Changing a value in `infra/.env` requires restarting the `backend` container
(`docker compose up -d --force-recreate backend` or a full `docker compose up`) —
no code or migration changes are ever needed for these.
