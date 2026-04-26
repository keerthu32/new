from sqlalchemy.orm import Session

from models import Notification


def push_notification(db: Session, user_id: int, message: str) -> Notification:
    notice = Notification(user_id=user_id, message=message)
    db.add(notice)
    db.commit()
    db.refresh(notice)
    return notice
