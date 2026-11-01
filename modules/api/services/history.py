from sqlalchemy import select
from sqlalchemy.orm import Session

from modules.api.models import PredictionRecord


def save_prediction(
    db: Session,
    *,
    user_id: int,
    student_data: dict,
    result: dict,
) -> PredictionRecord:
    record = PredictionRecord(
        user_id=user_id,
        student_data=student_data,
        result=result,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_predictions(
    db: Session,
    *,
    user_id: int,
    limit: int = 50,
) -> list[PredictionRecord]:
    statement = (
        select(PredictionRecord)
        .where(PredictionRecord.user_id == user_id)
        .order_by(PredictionRecord.created_at.desc(), PredictionRecord.id.desc())
        .limit(limit)
    )
    return list(db.scalars(statement))
