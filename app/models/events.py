from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column
from typing import Any

from database import Model

class EventsModel(Model):
    __tablename__ = "events"

    event_id: Mapped[str] = mapped_column(primary_key=True) # X-Github-Delivery
    event_type: Mapped[str] # x-github-event
    action: Mapped[str | None] # payload.action 
    sender: Mapped[str] # payload.sender.login 
    repository_full_name: Mapped[str] #payload.repository.full_name
    payload: Mapped[dict[str, Any]] = mapped_column(JSON)