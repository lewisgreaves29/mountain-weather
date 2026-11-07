# UK Mountain Weather Service (`mountain-weather`)

A production-grade, self-hosted UK mountain weather forecast service and ridge hazard engine tailored for K3s. Ingests high-resolution deterministic weather data from the UK Met Office via Open-Meteo (UKMO Seamless 2km model), evaluates summit ridge hazards against valley baselines, securely consumes configuration and secrets via 1Password Connect, and presents a responsive dark-mode Vue 3 dashboard.

---

## Architecture Overview

- **Hermetic Container:** Serves both high-speed FastAPI endpoints (`/api/v1/weather`, `/healthz`, `/readyz`) and pre-compiled Vue 3 SPA assets.
- **UKMO 2km Weather Ingestor:** Background polling worker (`APScheduler` + `httpx`) fetching deterministic weather for UK mountain summits and valley baselines.
- **Mountain Hazard Logic Engine:** Evaluates summit wind gusts, freezing levels, wind chill, and cloud clag against valley baselines to produce actionable safety bulletins (`GREEN`, `AMBER`, `RED`).
- **1Password Connect Integration:** Zero plaintext secrets in git; consumes `OnePasswordItem` CRD in namespace `apps`.

---

## Local Development

### 1. Backend

```bash
# Using 1Password CLI (op)
op run --env-file=.env.example -- uvicorn backend.app.main:app --reload

# Or set environment variables manually:
export AUTH_SECRET_TOKEN="dev-secret-token"
python -m pytest backend/tests --cov=backend/app --cov-report=term-missing
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
npm run test:run
npm run build
```

---

## Kubernetes Deployment (K3s)

```bash
kubectl apply -k deploy/kubernetes/
```

- **Domain:** `https://mountains.greaveslabs.io` & `https://mountain-weather.greaveslabs.io`
- **Namespace:** `apps`
- **Secrets:** `mountain-weather-secrets` provisioned automatically via 1Password Connect Operator.

---

## License

MIT © Lewis Greaves / GreavesLabs.
