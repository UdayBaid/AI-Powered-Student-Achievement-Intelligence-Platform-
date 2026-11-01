from fastapi import APIRouter

from modules.api.routes.auth import router as auth_router
from modules.api.routes.prediction import router as prediction_router

router = APIRouter()
router.include_router(auth_router)
router.include_router(prediction_router)
