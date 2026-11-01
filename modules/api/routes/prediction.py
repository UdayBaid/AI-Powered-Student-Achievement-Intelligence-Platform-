from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from modules.api.database import get_db
from modules.api.dependencies import get_current_user
from modules.api.models import User
from modules.api.schemas import PredictionHistoryItem, StudentInput
from modules.api.services.history import list_predictions, save_prediction
from modules.api.services.prediction import health_status, predict_student
import logging

logger = logging.getLogger(__name__)

router = APIRouter()
AuthenticatedUser = Annotated[User, Depends(get_current_user)]
DatabaseSession = Annotated[Session, Depends(get_db)]


@router.get("/")
def home() -> dict[str, str]:
    return {
        "message": "Student Achievement Intelligence API is running",
        "docs": "/docs",
    }


@router.get("/health")
def health() -> dict[str, str | bool]:
    return health_status()


@router.post("/predict")
def predict_grade(
    student: StudentInput,
    user: AuthenticatedUser,
    db: DatabaseSession,
) -> dict[str, object]:
    try:
        student_data = student.model_dump()
        result = predict_student(student_data)
        save_prediction(
            db,
            user_id=user.id,
            student_data=student_data,
            result=result,
        )
        return result
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except Exception:
        logger.exception("Prediction failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Prediction failed. Please try again.",
        )


@router.get("/predictions", response_model=list[PredictionHistoryItem])
def prediction_history(
    user: AuthenticatedUser,
    db: DatabaseSession,
    limit: int = Query(default=50, ge=1, le=100),
) -> list[PredictionHistoryItem]:
    return [
        PredictionHistoryItem.model_validate(record)
        for record in list_predictions(db, user_id=user.id, limit=limit)
    ]
