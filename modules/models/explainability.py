
import numpy as np
import pandas as pd
import shap


def explain_prediction(model, preprocessor, student_data, feature_columns):
    input_df = pd.DataFrame(
        [[student_data[col] for col in feature_columns]],
        columns=feature_columns,
    )

    processed_data = preprocessor.transform(input_df)

    if hasattr(processed_data, "toarray"):
        processed_data = processed_data.toarray()

    processed_data = np.asarray(processed_data)

    feature_names = preprocessor.get_feature_names_out()

    if processed_data.shape[1] != len(feature_names):
        raise ValueError("Processed feature count does not match feature names.")

    if processed_data.shape[1] != model.n_features_in_:
        raise ValueError("Processed feature count does not match model input.")

    explainer = shap.TreeExplainer(model)
    shap_result = explainer(processed_data)

    values = np.asarray(shap_result.values).reshape(-1)
    baseline = float(np.asarray(shap_result.base_values).reshape(-1)[0])

    if len(values) != len(feature_names):
        raise ValueError("SHAP values do not match feature dimensions.")

    prediction = float(model.predict(processed_data)[0])

    reconstructed_prediction = baseline + float(np.sum(values))

    additivity_check = bool(
        np.isclose(
            prediction,
            reconstructed_prediction,
            atol=1e-3,
            rtol=1e-3,
        )
    )

    contributions = sorted(
        zip(feature_names, values),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    top_features = [
        {
            "feature": str(name),
            "contribution": round(float(value), 4),
            "effect": (
                "increases prediction" if value > 0
                else "decreases prediction" if value < 0
                else "no contribution"
            ),
        }
        for name, value in contributions[:5]
    ]

    return {
        "baseline_prediction": round(baseline, 4),
        "predicted_grade": round(prediction, 4),
        "reconstructed_prediction": round(
            reconstructed_prediction, 4
        ),
        "additivity_check": additivity_check,
        "top_features": top_features,
    }
