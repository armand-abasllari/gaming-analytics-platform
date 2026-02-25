from fastapi import Depends, FastAPI, Query
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from api.database import SessionLocal
from api import models
from api.schemas import (
    GameEventCreate,
    GameEventOut,
    PlatformCount,
    GameCount,
)

app = FastAPI(title="Gaming Analytics API")


# ---------------------------
# DB Dependency
# ---------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ---------------------------
# Health Endpoints
# ---------------------------
@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/health/db")
def health_db(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"db": "ok"}


# ---------------------------
# Create Event
# ---------------------------
@app.post("/events", response_model=GameEventOut)
def create_event(payload: GameEventCreate, db: Session = Depends(get_db)):
    event = models.GameEvent(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# ---------------------------
# List Events
# ---------------------------
@app.get("/events", response_model=list[GameEventOut])
def list_events(
    db: Session = Depends(get_db),
    platform: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    q = db.query(models.GameEvent)

    if platform:
        q = q.filter(models.GameEvent.platform.ilike(platform))

    return (
        q.order_by(models.GameEvent.id.desc())
        .limit(limit)
        .offset(offset)
        .all()
    )


# ---------------------------
# Platform Stats
# ---------------------------
@app.get("/stats/platforms", response_model=list[PlatformCount])
def stats_platforms(db: Session = Depends(get_db)):
    rows = (
        db.query(
            models.GameEvent.platform,
            func.count(models.GameEvent.id)
        )
        .group_by(models.GameEvent.platform)
        .order_by(func.count(models.GameEvent.id).desc())
        .all()
    )

    return [
        {"platform": platform, "count": count}
        for platform, count in rows
    ]


# ---------------------------
# Top Games
# ---------------------------
@app.get("/stats/top-games", response_model=list[GameCount])
def top_games(
    db: Session = Depends(get_db),
    limit: int = Query(default=10, ge=1, le=50),
    platform: str | None = Query(default=None),
):
    q = db.query(
        models.GameEvent.game_name,
        func.count(models.GameEvent.id).label("count"),
    )

    if platform:
        q = q.filter(models.GameEvent.platform.ilike(platform))

    rows = (
        q.group_by(models.GameEvent.game_name)
        .order_by(func.count(models.GameEvent.id).desc())
        .limit(limit)
        .all()
    )

    return [
        {"game_name": name, "count": count}
        for name, count in rows
    ]
