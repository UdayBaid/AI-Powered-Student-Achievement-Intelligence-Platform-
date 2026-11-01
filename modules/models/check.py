from pathlib import Path

import joblib

model_dir = Path(__file__).resolve().parent
model = joblib.load(model_dir / "regression_model.joblib")
preprocessor = joblib.load(model_dir / "preprocessor.joblib")

print("Model:", type(model))
print("Preprocessor:", type(preprocessor))
print("Model features:", getattr(model, "n_features_in_", "Unknown"))

try:
    names = preprocessor.get_feature_names_out()
    print("Processed feature count:", len(names))
    print("Feature names:", names)
except Exception as e:
    print("Feature name error:", e)

print("Model parameters:", model.get_params())