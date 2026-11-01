import hashlib
from datetime import datetime, timedelta, timezone
from urllib.parse import parse_qs, urlparse

import jwt
from sqlalchemy import select

from modules.api.models import PasswordResetToken, User
from modules.api.routes import auth as auth_routes
from modules.api.services import password_reset as password_reset_service
from modules.api.services.password_reset import ResetEmailDeliveryError
from tests.conftest import STUDENT_PAYLOAD, TEST_JWT_SECRET

REGISTER_PAYLOAD = {
    "name": "  Student Example  ",
    "email": "Student@Example.com",
    "password": "CorrectHorseBattery123!",
}


def test_registration_hashes_password_and_rejects_duplicate(client, test_session_factory):
    response = client.post("/auth/register", json=REGISTER_PAYLOAD)

    assert response.status_code == 201
    assert response.json()["name"] == "Student Example"
    assert response.json()["email"] == "student@example.com"
    assert "hashed_password" not in response.json()

    with test_session_factory() as db:
        user = db.scalar(select(User).where(User.email == "student@example.com"))
        assert user is not None
        assert user.hashed_password.startswith("$argon2id$")
        assert user.hashed_password != REGISTER_PAYLOAD["password"]

    duplicate = client.post(
        "/auth/register",
        json={**REGISTER_PAYLOAD, "email": "student@example.com"},
    )
    assert duplicate.status_code == 409


def test_registration_validates_email_and_password(client):
    invalid_email = client.post(
        "/auth/register",
        json={**REGISTER_PAYLOAD, "email": "not-an-email"},
    )
    short_password = client.post(
        "/auth/register",
        json={**REGISTER_PAYLOAD, "email": "other@example.com", "password": "short"},
    )

    assert invalid_email.status_code == 422
    assert short_password.status_code == 422


def test_login_current_user_and_expired_or_invalid_tokens(client):
    registered = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert registered.status_code == 201

    wrong_password = client.post(
        "/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "incorrect-password"},
    )
    assert wrong_password.status_code == 401

    login = client.post(
        "/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    assert login.status_code == 200
    token_response = login.json()
    assert token_response["token_type"] == "bearer"
    assert token_response["expires_in"] > 0
    assert "hashed_password" not in token_response["user"]

    claims = jwt.decode(
        token_response["access_token"],
        TEST_JWT_SECRET,
        algorithms=["HS256"],
    )
    assert claims["sub"] == str(registered.json()["id"])
    assert "exp" in claims

    current = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {token_response['access_token']}"},
    )
    invalid = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    expired_token = jwt.encode(
        {
            "sub": str(registered.json()["id"]),
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        TEST_JWT_SECRET,
        algorithm="HS256",
    )
    expired = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert current.status_code == 200
    assert current.json()["email"] == "student@example.com"
    assert invalid.status_code == 401
    assert expired.status_code == 401


def test_prediction_requires_auth_and_health_remains_public(client):
    unauthorized = client.post("/predict", json=STUDENT_PAYLOAD)
    health = client.get("/health")
    assert unauthorized.status_code == 401
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    client.post("/auth/register", json=REGISTER_PAYLOAD)
    login = client.post(
        "/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    token = login.json()["access_token"]
    prediction = client.post(
        "/predict",
        json=STUDENT_PAYLOAD,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert prediction.status_code == 200
    assert set(prediction.json()) == {
        "predicted_g3",
        "interpretation",
        "recommendations",
        "explanations",
    }


def test_password_reset_is_one_time_and_revokes_existing_sessions(
    client,
    test_session_factory,
    monkeypatch,
):
    registered = client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert registered.status_code == 201
    login = client.post(
        "/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    old_access_token = login.json()["access_token"]

    sent_links = []
    monkeypatch.setattr(auth_routes, "email_delivery_configured", lambda: True)
    monkeypatch.setattr(
        password_reset_service,
        "_send_reset_email",
        lambda email, reset_url: sent_links.append((email, reset_url)),
    )

    unknown_email = client.post(
        "/auth/forgot-password",
        json={"email": "unknown@example.com"},
    )
    reset_requested = client.post(
        "/auth/forgot-password",
        json={"email": REGISTER_PAYLOAD["email"]},
    )
    assert unknown_email.status_code == 202
    assert reset_requested.status_code == 202
    assert unknown_email.json() == reset_requested.json()
    assert "token" not in reset_requested.json()
    assert len(sent_links) == 1
    assert sent_links[0][0] == "student@example.com"

    raw_token = parse_qs(urlparse(sent_links[0][1]).query)["reset_token"][0]
    with test_session_factory() as db:
        stored_token = db.scalar(
            select(PasswordResetToken).where(
                PasswordResetToken.user_id == registered.json()["id"]
            )
        )
        assert stored_token is not None
        assert stored_token.token_hash == hashlib.sha256(raw_token.encode()).hexdigest()
        assert stored_token.token_hash != raw_token

    reset_payload = {
        "token": raw_token,
        "password": "NewSecureHorseBattery456!",
    }
    completed = client.post("/auth/reset-password", json=reset_payload)
    replayed = client.post("/auth/reset-password", json=reset_payload)
    old_session = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {old_access_token}"},
    )
    old_password_login = client.post(
        "/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
        },
    )
    new_password_login = client.post(
        "/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": reset_payload["password"],
        },
    )

    assert completed.status_code == 200
    assert replayed.status_code == 400
    assert old_session.status_code == 401
    assert old_password_login.status_code == 401
    assert new_password_login.status_code == 200


def test_password_reset_rejects_expired_tokens(client, test_session_factory):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    raw_token = "expired-reset-token-" + ("x" * 32)
    with test_session_factory() as db:
        user = db.scalar(select(User).where(User.email == "student@example.com"))
        assert user is not None
        db.add(
            PasswordResetToken(
                user_id=user.id,
                token_hash=hashlib.sha256(raw_token.encode()).hexdigest(),
                expires_at=datetime.now(timezone.utc) - timedelta(seconds=1),
            )
        )
        db.commit()

    response = client.post(
        "/auth/reset-password",
        json={"token": raw_token, "password": "AnotherSecurePassphrase123!"},
    )
    assert response.status_code == 400


def test_forgot_password_is_disabled_without_smtp(client, monkeypatch):
    monkeypatch.setattr(auth_routes, "email_delivery_configured", lambda: False)

    known_email = client.post(
        "/auth/forgot-password",
        json={"email": REGISTER_PAYLOAD["email"]},
    )
    unknown_email = client.post(
        "/auth/forgot-password",
        json={"email": "unknown@example.com"},
    )

    assert known_email.status_code == 503
    assert known_email.json() == unknown_email.json()


def test_mail_failure_does_not_leave_a_reset_token(
    client,
    test_session_factory,
    monkeypatch,
):
    client.post("/auth/register", json=REGISTER_PAYLOAD)
    monkeypatch.setattr(auth_routes, "email_delivery_configured", lambda: True)

    def fail_delivery(email, reset_url):
        raise ResetEmailDeliveryError("SMTP unavailable")

    monkeypatch.setattr(password_reset_service, "_send_reset_email", fail_delivery)
    response = client.post(
        "/auth/forgot-password",
        json={"email": REGISTER_PAYLOAD["email"]},
    )

    assert response.status_code == 202
    with test_session_factory() as db:
        token = db.scalar(select(PasswordResetToken))
        assert token is None
