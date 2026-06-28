#!/usr/bin/env python3
"""
Snake Leaderboard API — FastAPI backend.
Stores top 10 scores in scores.json alongside the server script.
Serves on :7071 alongside the static HTTP server on :7070.
"""

import json, os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

SCORES_FILE = Path(__file__).parent / "scores.json"
TOP_N = 10


def load_scores() -> list[dict]:
    if not SCORES_FILE.exists():
        return []
    try:
        return json.loads(SCORES_FILE.read_text())
    except Exception:
        return []


def save_scores(scores: list[dict]) -> None:
    SCORES_FILE.write_text(json.dumps(scores, indent=2))


@app.get("/api/scores")
def get_scores():
    """Return the top {TOP_N} scores, sorted descending."""
    scores = load_scores()
    return JSONResponse(content={"scores": scores[:TOP_N], "count": len(scores)})


@app.post("/api/scores")
def submit_score(payload: dict):
    """
    Submit a new score.
    Body: {"name": "AAA", "score": 42}
    Returns: {"rank": 1, "scores": [...]} or {"rank": null} if not top 10.
    """
    name = (payload.get("name") or "").strip()[:20] or "ANON"
    score: int = payload.get("score", 0)

    if not isinstance(score, int) or score < 0:
        raise HTTPException(status_code=400, detail="Invalid score")

    scores = load_scores()
    scores.append({"name": name, "score": score})
    scores.sort(key=lambda x: x["score"], reverse=True)
    scores = scores[:TOP_N]
    save_scores(scores)

    rank = next((i + 1 for i, s in enumerate(scores) if s["name"] == name and s["score"] == score), None)
    return JSONResponse(content={"rank": rank, "scores": scores})


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=7071, log_level="warning")
