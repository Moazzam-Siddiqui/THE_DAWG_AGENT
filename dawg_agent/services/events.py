"""Save a diary entry whenever the robot does something important."""
import json

from sqlalchemy.orm import Session

from dawg_agent.models import Event


def record_event(
    database: Session,
    event_name: str,
    post_id: str | None = None,
    **details,
) -> None:
    """Write one event to the database."""
    event = Event(
        post_id=post_id,
        event_type=event_name,
        details=json.dumps(details, default=str),
    )
    database.add(event)
    database.commit()
