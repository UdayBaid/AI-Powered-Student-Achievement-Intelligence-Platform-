from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from xgboost import XGBRegressor

from modules.api.schemas import FEATURE_COLUMNS
from modules.models.explainability import explain_prediction
from modules.models.interpretation import interpret_grade
from modules.models.recommendation import generate_recommendations

MODEL_DIR = Path(__file__).resolve().parents[2] / "models"
MODEL_PATH = MODEL_DIR / "regression_model.joblib"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.joblib"

_model: XGBRegressor | None = None
_preprocessor: ColumnTransformer | None = None


def load_artifacts() -> None:
    global _model, _preprocessor

    if not MODEL_PATH.is_file():
        raise FileNotFoundError(f"Model file not found: {MODEL_PATH}")
    if not PREPROCESSOR_PATH.is_file():
        raise FileNotFoundError(f"Preprocessor file not found: {PREPROCESSOR_PATH}")

    loaded_model = joblib.load(MODEL_PATH)
    loaded_preprocessor = joblib.load(PREPROCESSOR_PATH)
    feature_count = len(loaded_preprocessor.get_feature_names_out())
    if loaded_model.n_features_in_ != feature_count:
        raise ValueError("Model and preprocessor feature counts do not match.")

    _model = loaded_model
    _preprocessor = loaded_preprocessor


def health_status() -> dict[str, str | bool]:
    ready = _model is not None and _preprocessor is not None
    return {
        "status": "healthy" if ready else "not_ready",
        "model_loaded": _model is not None,
        "preprocessor_loaded": _preprocessor is not None,
    }


def predict_student(student_data: dict[str, Any]) -> dict[str, Any]:
    if _model is None or _preprocessor is None:
        raise RuntimeError("Model artifacts are not loaded.")

    input_df = pd.DataFrame(
        [[student_data[column] for column in FEATURE_COLUMNS]],
        columns=FEATURE_COLUMNS,
    )
    processed_data = _preprocessor.transform(input_df)
    prediction = float(_model.predict(processed_data)[0])

    return {
        "predicted_g3": round(prediction, 2),
        "interpretation": interpret_grade(prediction),
        "recommendations": generate_recommendations(student_data, prediction),
        "explanations": explain_prediction(
            _model,
            _preprocessor,
            student_data,
            FEATURE_COLUMNS,
        ),
    }
