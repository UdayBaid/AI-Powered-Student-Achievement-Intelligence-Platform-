from pathlib import Path
import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from .recommendation import generate_recommendations
from .interpretation import interpret_grade
from .explainability import explain_prediction
app = FastAPI(
    title="Student Achievement Intelligence API",
    description="Predicts an estimated final student grade using a trained ML model.",
    version="1.0.0",
)
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"
MODEL_PATH = MODEL_DIR / "regression_model.joblib"
PREPROCESSOR_PATH = MODEL_DIR / "preprocessor.joblib"
model = None
preprocessor = None
FEATURE_COLUMNS = [
    "school", "sex", "age", "address", "famsize", "Pstatus",
    "Medu", "Fedu", "Mjob", "Fjob", "reason", "guardian",
    "traveltime", "studytime", "failures", "schoolsup",
    "famsup", "paid", "activities", "nursery", "higher",
    "internet", "romantic", "famrel", "freetime", "goout",
    "Dalc", "Walc", "health", "absences",
]
class StudentInput(BaseModel):
    school: str = Field(description="GP or MS")
    sex: str = Field(description="F or M")
    age: int = Field(ge=15, le=22)
    address: str
    famsize: str
    Pstatus: str
    Medu: int = Field(ge=0, le=4)
    Fedu: int = Field(ge=0, le=4)
    Mjob: str
    Fjob: str
    reason: str
    guardian: str
    traveltime: int = Field(ge=1, le=4)
    studytime: int = Field(ge=1, le=4)
    failures: int = Field(ge=0, le=4)
    schoolsup: str
    famsup: str
    paid: str
    activities: str
    nursery: str
    higher: str
    internet: str
    romantic: str
    famrel: int = Field(ge=1, le=5)
    freetime: int = Field(ge=1, le=5)
    goout: int = Field(ge=1, le=5)
    Dalc: int = Field(ge=1, le=5)
    Walc: int = Field(ge=1, le=5)
    health: int = Field(ge=1, le=5)
    absences: int = Field(ge=0)
@app.on_event("startup")
def load_artifacts():
    global model, preprocessor
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Model file not found: {MODEL_PATH}")
    if not PREPROCESSOR_PATH.exists():
        raise RuntimeError(
            f"Preprocessor file not found: {PREPROCESSOR_PATH}"
        )
    model = joblib.load(MODEL_PATH)
    preprocessor = joblib.load(PREPROCESSOR_PATH)
@app.get("/")
def home():
    return {
        "message": "Student Achievement Intelligence API is running",
        "docs": "/docs",
    }
@app.get("/health")
def health():
    return {
        "status": "healthy" if model is not None and preprocessor is not None
        else "not_ready",
        "model_loaded": model is not None,
        "preprocessor_loaded": preprocessor is not None,
    }
@app.post("/predict")
def predict_grade(student: StudentInput):
    if model is None or preprocessor is None:
        raise HTTPException(
            status_code=503,
            detail="Model artifacts are not loaded.",
        )

    try:
        student_data = student.model_dump()
        input_df = pd.DataFrame(
            [[student_data[col] for col in FEATURE_COLUMNS]],
            columns=FEATURE_COLUMNS,
        )
        processed_data = preprocessor.transform(input_df)
        prediction = float(model.predict(processed_data)[0])
        recommendations = generate_recommendations(
            student_data,
            prediction,
        )
        explanations = explain_prediction(
            model,
            preprocessor,
            student_data,
            FEATURE_COLUMNS,
        )

        return {
            "predicted_g3": round(prediction, 2),
            "interpretation": interpret_grade(prediction),
            "recommendations": recommendations,
            "explanations": explanations,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(exc)}",
        ) from exc
