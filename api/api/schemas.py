from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class GameEventCreate(BaseModel):
    game_name: str = Field(min_length=1)
    platform: str = Field(min_length=1)

class GameEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    game_name: str
    platform: str
    created_at: datetime

class PlatformCount(BaseModel):
    platform: str
    count: int

class GameCount(BaseModel):
    game_name: str
    count: int
