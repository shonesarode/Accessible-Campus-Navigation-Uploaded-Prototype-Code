"""Demo API for accessible route planning with an unverified reports queue."""
from __future__ import annotations
from datetime import datetime, timezone
from itertools import count
from threading import Lock
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .demo_data import NETWORK

app = FastAPI(title="Accessible Campus Navigation — Demonstration", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

class ReportInput(BaseModel):
    edge_id: str
    description: str = Field(min_length=5, max_length=500)

class RouteInput(BaseModel):
    start: str
    destination: str
    wheelchair: bool = True
    max_slope_percent: float = Field(default=6, ge=0, le=30)
    avoid_unpaved: bool = False
    blocked_edges: list[str] = Field(default_factory=list)

_report_lock = Lock()
_report_ids = count(1)
_reports: list[dict] = []

@app.get("/api/network")
def get_network():
    return {
        "nodes": [vars(n) for n in NETWORK.nodes.values()],
        "edges": [vars(e) for e in NETWORK.edges.values()],
        "notice": "Fictional network for a portfolio demo; not real navigation advice.",
    }

@app.post("/api/route")
def compute_route(request: RouteInput):
    try:
        result = NETWORK.route(
            request.start,
            request.destination,
            wheelchair=request.wheelchair,
            max_slope_percent=request.max_slope_percent,
            avoid_unpaved=request.avoid_unpaved,
            blocked_edges=request.blocked_edges,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    if result is None:
        raise HTTPException(status_code=404, detail="No path meets these constraints")
    return {
        "node_ids": result.node_ids,
        "edge_ids": result.edge_ids,
        "distance_meters": round(result.distance_meters, 1),
        "weighted_cost": round(result.weighted_cost, 1),
        "note": "Illustrative route only; do not use for physical navigation.",
    }

@app.post("/api/reports", status_code=201)
def submit_report(report: ReportInput):
    if report.edge_id not in NETWORK.edges:
        raise HTTPException(status_code=422, detail="Unknown path segment")
    with _report_lock:
        entry = {
            "id": next(_report_ids),
            "edge_id": report.edge_id,
            "description": report.description,
            "status": "pending_review",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        _reports.append(entry)
    # Reports do not alter routing until a trusted verifier reviews them.
    return entry

@app.get("/api/reports")
def list_reports(limit: int = Query(default=25, ge=1, le=100)):
    with _report_lock:
        return list(reversed(_reports[-limit:]))
