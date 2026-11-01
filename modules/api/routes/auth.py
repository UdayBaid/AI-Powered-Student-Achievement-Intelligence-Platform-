import logging
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from modules.api.database import get_db
from modules.api.dependencies import get_current_user
from modules.api.models import User
from modules.api.schemas.auth import (
    ForgotPasswordRequest,
    MessageResponse,
    ResetPasswordRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from modules.api.security import create_access_token
from modules.api.services.auth import authenticate_user, create_user
from modules.api.services.password_reset import (
    ResetEmailDeliveryError,
    complete_password_reset,
    email_delivery_configured,
    request_password_reset,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
DatabaseSession = Annotated[Session, Depends(get_db)]
AuthenticatedUser = Annotated[User, Depends(get_current_user)]
logger = logging.getLogger(__name__)
RESET_REQUEST_MESSAGE = "If an account exists for this email, reset instructions will be sent."


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(payload: UserRegister, db: DatabaseSession) -> User:
    try:
        return create_user(
            db,
            name=payload.name,
            email=str(payload.email),
            password=payload.password,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        ) from exc


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: DatabaseSession) -> TokenResponse:
    user = authenticate_user(
        db,
        email=str(payload.email),
        password=payload.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        token, expires_in = create_access_token(user.id, user.token_version)
    except RuntimeError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication is not configured. Set JWT_SECRET.",
        ) from exc

    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def current_user(user: AuthenticatedUser) -> User:
    return user


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: DatabaseSession,
) -> MessageResponse:
    if not email_delivery_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Password reset email is not configured. Contact the administrator.",
        )

    try:
        request_password_reset(db, str(payload.email))
    except ResetEmailDeliveryError:
        logger.warning("Password reset email delivery failed.")

    return MessageResponse(message=RESET_REQUEST_MESSAGE)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(
    payload: ResetPasswordRequest,
    db: DatabaseSession,
) -> MessageResponse:
    updated = complete_password_reset(
        db,
        token=payload.token,
        new_password=payload.password,
    )
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password reset link is invalid or expired.",
        )
    return MessageResponse(message="Password reset. You can now sign in.")
