from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import math

app = FastAPI()

# Enable CORS for POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class LatencyRequest(BaseModel):
    regions: List[str]
    threshold_ms: float


def calculate_p95(values: List[float]) -> float:
    if not values:
        return 0.0
    values = sorted(values)
    idx = 0.95 * (len(values) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return values[lo]
    frac = idx - lo
    return values[lo] * (1 - frac) + values[hi] * frac


# IMPORTANT: route is "/" — Vercel handles /api/latency
@app.post("/")
async def latency_metrics(request: LatencyRequest):
    data = [
        # ---- apac ----
        {"region": "apac", "latency_ms": 196.92, "uptime_pct": 97.52},
        {"region": "apac", "latency_ms": 215.23, "uptime_pct": 98.142},
        {"region": "apac", "latency_ms": 178.05, "uptime_pct": 99.124},
        {"region": "apac", "latency_ms": 187.17, "uptime_pct": 97.967},
        {"region": "apac", "latency_ms": 201.07, "uptime_pct": 98.284},
        {"region": "apac", "latency_ms": 106.28, "uptime_pct": 97.326},
        {"region": "apac", "latency_ms": 210.01, "uptime_pct": 97.963},
        {"region": "apac", "latency_ms": 208.43, "uptime_pct": 97.15},
        {"region": "apac", "latency_ms": 180.81, "uptime_pct": 99.15},
        {"region": "apac", "latency_ms": 181.06, "uptime_pct": 98.27},
        {"region": "apac", "latency_ms": 110.59, "uptime_pct": 97.685},
        {"region": "apac", "latency_ms": 145.25, "uptime_pct": 98.555},

        # ---- emea ----
        {"region": "emea", "latency_ms": 207.35, "uptime_pct": 98.063},
        {"region": "emea", "latency_ms": 218.31, "uptime_pct": 97.977},
        {"region": "emea", "latency_ms": 229.28, "uptime_pct": 97.288},
        {"region": "emea", "latency_ms": 185.18, "uptime_pct": 98.834},
        {"region": "emea", "latency_ms": 139.58, "uptime_pct": 98.413},
        {"region": "emea", "latency_ms": 130.32, "uptime_pct": 97.45},
        {"region": "emea", "latency_ms": 144.9, "uptime_pct": 97.865},
        {"region": "emea", "latency_ms": 144.18, "uptime_pct": 97.552},
        {"region": "emea", "latency_ms": 195.86, "uptime_pct": 98.869},
        {"region": "emea", "latency_ms": 159.95, "uptime_pct": 97.614},
        {"region": "emea", "latency_ms": 216.72, "uptime_pct": 98.289},
        {"region": "emea", "latency_ms": 224.75, "uptime_pct": 99.003},

        # ---- amer ----
        {"region": "amer", "latency_ms": 136.17, "uptime_pct": 97.238},
        {"region": "amer", "latency_ms": 118.85, "uptime_pct": 98.276},
        {"region": "amer", "latency_ms": 137.36, "uptime_pct": 98.956},
        {"region": "amer", "latency_ms": 168.64, "uptime_pct": 98.682},
        {"region": "amer", "latency_ms": 190.73, "uptime_pct": 98.58},
        {"region": "amer", "latency_ms": 113.19, "uptime_pct": 99.49},
        {"region": "amer", "latency_ms": 204.79, "uptime_pct": 98.8},
        {"region": "amer", "latency_ms": 122.95, "uptime_pct": 98.943},
        {"region": "amer", "latency_ms": 143.84, "uptime_pct": 98.273},
        {"region": "amer", "latency_ms": 172.84, "uptime_pct": 98.882},
        {"region": "amer", "latency_ms": 129.01, "uptime_pct": 98.817},
        {"region": "amer", "latency_ms": 178.29, "uptime_pct": 97.92},
    ]

    results = []

    for region in request.regions:
        rows = [r for r in data if r["region"] == region]
        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        results.append({
            "region": region,
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(calculate_p95(latencies), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(1 for l in latencies if l > request.threshold_ms),
        })

    return results
