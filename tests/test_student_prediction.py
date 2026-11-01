from pathlib import Path
import sys

import joblib
import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from modules.api.main import app as api_app
from modules.models.explainability import explain_prediction
from modules.models.main import FEATURE_COLUMNS, app as legacy_app

MODEL_DIR = ROOT_DIR / "modules" / "models"

STUDENT_DATA = {
    "school": "GP",
    "sex": "F",
    "age": 17,
    "address": "U",
    "famsize": "GT3",
    "Pstatus": "T",
    "Medu": 4,
    "Fedu": 3,
    "Mjob": "teacher",
    "Fjob": "other",
    "reason": "course",
    "guardian": "mother",
    "traveltime": 1,
    "studytime": 3,
    "failures": 0,
    "schoolsup": "no",
    "famsup": "yes",
    "paid": "no",
    "activities": "yes",
    "nursery": "yes",
    "higher": "yes",
    "internet": "yes",
    "romantic": "no",
    "famrel": 4,
    "freetime": 3,
    "goout": 3,
    "Dalc": 1,
    "Walc": 2,
    "health": 4,
    "absences": 2,
}


@pytest.fixture(scope="module")
def artifacts():
    model = joblib.load(MODEL_DIR / "regression_model.joblib")
    preprocessor = joblib.load(MODEL_DIR / "preprocessor.joblib")
    return model, preprocessor


def test_model_and_preprocessor_feature_counts_match(artifacts):
    model, preprocessor = artifacts

    assert model.n_features_in_ == len(preprocessor.get_feature_names_out())


def test_legacy_entry_point_matches_modular_api():
    assert legacy_app is api_app


def test_explanation_reconstructs_prediction(artifacts):
    model, preprocessor = artifacts

    result = explain_prediction(
        model,
        preprocessor,
        STUDENT_DATA,
        FEATURE_COLUMNS,
    )

    assert result["additivity_check"] is True
    assert result["predicted_grade"] == pytest.approx(
        result["reconstructed_prediction"],
        abs=1e-3,
    )
    assert len(result["top_features"]) == 5


def test_prediction_api_returns_recommendations_and_explanations(client):
    registration = client.post(
        "/auth/register",
        json={
            "name": "Prediction Test",
            "email": "prediction@example.com",
            "password": "CorrectHorseBattery123!",
        },
    )
    login = client.post(
        "/auth/login",
        json={
            "email": "prediction@example.com",
            "password": "CorrectHorseBattery123!",
        },
    )
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    health = client.get("/health")
    unauthorized = client.post("/predict", json=STUDENT_DATA)
    response = client.post("/predict", json=STUDENT_DATA, headers=headers)

    assert registration.status_code == 201
    assert login.status_code == 200
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"
    assert unauthorized.status_code == 401
    assert response.status_code == 200

    result = response.json()
    assert 0 <= result["predicted_g3"] <= 20
    assert result["interpretation"]
    assert result["recommendations"]
    assert len(result["explanations"]) == 5

    saved = client.get("/predictions", headers=headers)
    assert saved.status_code == 200
    assert len(saved.json()) == 1
    assert saved.json()[0]["result"] == result
    assert saved.json()[0]["student_data"] == STUDENT_DATA


def test_prediction_history_is_private_to_each_user(client):
    first_user = {
        "name": "First User",
        "email": "first.history@example.com",
        "password": "CorrectHorseBattery123!",
    }
    second_user = {
        "name": "Second User",
        "email": "second.history@example.com",
        "password": "CorrectHorseBattery123!",
    }
    client.post("/auth/register", json=first_user)
    client.post("/auth/register", json=second_user)

    first_login = client.post(
        "/auth/login",
        json={"email": first_user["email"], "password": first_user["password"]},
    ).json()
    second_login = client.post(
        "/auth/login",
        json={"email": second_user["email"], "password": second_user["password"]},
    ).json()
    first_headers = {"Authorization": f"Bearer {first_login['access_token']}"}
    second_headers = {"Authorization": f"Bearer {second_login['access_token']}"}

    prediction = client.post("/predict", json=STUDENT_DATA, headers=first_headers)
    first_history = client.get("/predictions", headers=first_headers)
    second_history = client.get("/predictions", headers=second_headers)

    assert prediction.status_code == 200
    assert len(first_history.json()) == 1
    assert second_history.status_code == 200
    assert second_history.json() == []