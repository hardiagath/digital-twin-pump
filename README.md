# Digital Twin — Centrifugal Pump Monitor

An AI-assisted digital twin for a centrifugal pump: live sensor ingestion,
Isolation Forest anomaly detection, per-part risk alerts, Gemini-generated
maintenance recommendations, a 3D model of the pump, and historical trend
charts — behind a single-admin login.

## Architecture

```
backend/    FastAPI + MySQL + scikit-learn (Isolation Forest)
frontend/   Next.js 16 (App Router) + Tailwind v4 + react-three-fiber + Plotly
```

Sensor readings flow: **generate/ingest -> score (ML) -> threshold check ->
alert -> (optional) Gemini recommendation**. The frontend polls the API
for the dashboard, the 3D view, and the trends page.

## Features

- Live dashboard — latest readings, anomaly score, active alerts, AI
  recommendations per alert
- 3D pump viewer (`/pump`) — real GLB model with colored risk hotspots
  per part (bearing / seal / motor / impeller), plus an in-app calibrator
  to reposition them
- Trends (`/trends`) — sensor history, anomaly score history, risk
  distribution, with a 6h / 24h / 7d range selector
- Single-admin JWT auth — no signup, one operator
- Light / dark mode
- "Simulate reading" — inject a synthetic normal or fault reading without
  waiting for real sensor data

## Backend setup

```bash
cd backend
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # fill in DB_*, GEMINI_API_KEY, JWT_SECRET_KEY
```

Create your admin password:

```bash
python generate_password_hash.py
# paste the printed ADMIN_PASSWORD_HASH line into .env
```

Seed the database (creates the equipment row, generates synthetic sensor
history, trains the anomaly model, and raises alerts from it):

```bash
python seed.py
# python seed.py --reset                  # wipe and reseed
# python seed.py --with-recommendations   # also call Gemini for each alert (uses API quota)
```

Run the API:

```bash
uvicorn app.main:app --reload
```

Every route except `POST /auth/login` requires a bearer token now — get
one from that endpoint (or just log in from the frontend).

## Frontend setup

```bash
cd frontend
npm install
cp .env.example .env.local        # NEXT_PUBLIC_API_URL, defaults to localhost:8000
npm run dev
```

Open `http://localhost:3000`, log in with the admin username/password you
set above.

## Notes on the 3D pump viewer

The GLB (`frontend/public/models/pump.glb`, a Sketchfab "Centrifugal Pump"
model by ENGIPROS, CC-BY-4.0) has no per-part names in its geometry — every
node is just `Material2`, `Material3`, etc. So the four risk hotspots
(bearing/seal/motor/impeller) are placed by hand-tuned coordinates in
`frontend/lib/hotspots.ts`, not by inspecting mesh names.

## Known limitations / things worth revisiting

- `gemini_service.py` uses the now end-of-life `google.generativeai`
  package (prints a deprecation warning on import). It still works, but
  migrating to `google.genai` would be worth doing before this goes
  anywhere long-lived.
- The admin password is a single bcrypt hash in `.env`, not a user table —
  fine for a one-operator project, not for multi-user access.
- `npm audit` currently reports some high-severity advisories in
  transitive dependencies (mostly via `plotly.js`); worth a look before
  a public deployment.

## API overview

| Router            | Prefix              | Auth |
|--------------------|----------------------|------|
| `auth`             | `/auth`              | public |
| `equipment`        | `/equipment`         | bearer token |
| `sensors`          | `/sensors`           | bearer token |
| `alerts`           | `/alerts`            | bearer token |
| `recommendations`  | `/recommendations`   | bearer token |
| `trends`           | `/trends`            | bearer token |

Full interactive docs at `http://localhost:8000/docs` once the API is running.
