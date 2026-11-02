# Pathways: accessible campus routing (portfolio prototype)

A **working full-stack learning project** exploring how walking routes can account for mobility needs. A FastAPI service runs an A* graph search with stair, slope, surface and simulated-closure constraints. A React/TypeScript interface visualizes the route on a fictional campus-style network.



## What works

- A* route selection with a provably admissible straight-line lower-bound heuristic on the illustrative graph
- Wheelchair mode that excludes stairs and steep slopes; paved-only mode
- Simulation of blocked paths that recalculates route alternatives
- React/TypeScript dashboard with a legible SVG network and responsive layouts
- Reports API that stores **pending** observations without allowing unverified reports to alter route planning
- Python unit and HTTP API tests

## Technology

React, TypeScript, Vite, Python, FastAPI, Pydantic and pytest. Data is in-memory and resets when the backend restarts; no production database is included.

## Run locally

Requires Python 3.10+ and Node 18+.

**Terminal 1 — API**

```bash
cd backend
python -m venv .venv
source .venv/bin/activate    # Windows PowerShell: .venv\\Scripts\\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — UI**

```bash
cd frontend
npm install
npm run dev
```

Visit <http://localhost:5173>. API docs: <http://localhost:8000/docs>.

## Test

```bash
cd backend && pytest -q
cd ../frontend && npm run build
```

## Core design decisions

1. **Accessibility filters are explicit.** The route search filters stairs and slopes before calculating shortest feasible paths. It does not claim to know real-world ADA compliance.
2. **Heuristic stays admissible.** Demo coordinates are schematic, so the heuristic scales straight-line distances by the smallest observed edge-length/coordinate-distance ratio. Weighted accessibility penalties are nonnegative.
3. **Crowdsourcing needs moderation.** User reports are queued as `pending_review`; they never silently change route availability. In production, authenticated reviewers, timestamps, audit logs, abuse prevention and verification would be required.
4. **One clear result.** The route returns both the actual distance in meters and the optimization cost, since slope penalties make them different.

## API endpoints

| Method | URL | Purpose |
|---|---|---|
| GET | `/api/network` | Return schematic graph |
| POST | `/api/route` | Compute route with constraints |
| POST | `/api/reports` | Submit unverified access concern |
| GET | `/api/reports` | Inspect demo report queue |

Sample request:

```bash
curl -X POST http://localhost:8000/api/route \
  -H 'Content-Type: application/json' \
  -d '{"start":"west","destination":"science","wheelchair":true,"max_slope_percent":6,"avoid_unpaved":false,"blocked_edges":[]}'
```


## License

MIT (see `LICENSE`).
