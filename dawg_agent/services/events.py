import json
from sqlalchemy.orm import Session

from dawg_agent.models import Event


def record_event(db: Session, event_type: str, post_id: str | None = None, **details) -> None:
    db.add(Event(post_id=post_id, event_type=event_type, details=json.dumps(details, default=str)))
    db.commit()
