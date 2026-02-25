from sqlalchemy import Column, Integer, String, DateTime, func
from .database import Base

class GameEvent(Base):
    __tablename__ = "game_events"

    id = Column(Integer, primary_key=True, index=True)
    game_name = Column(String(255), nullable=False)
    platform = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
