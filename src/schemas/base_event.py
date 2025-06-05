from pydantic import BaseModel
from typing import Literal


class BaseEvent(BaseModel):
    event_type: str
