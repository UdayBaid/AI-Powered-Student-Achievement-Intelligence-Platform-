
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

    feature_names = preprocessor.get_feature_names_out()

    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(processed_data)

    values = np.asarray(shap_values).reshape(-1)

    contributions = sorted(
        zip(feature_names, values),
        key=lambda item: abs(item[1]),
        reverse=True,
    )

    return [
        {
            "feature": str(name),
            "contribution": round(float(value), 4),
            "effect": "increases prediction" if value > 0
            else "decreases prediction" if value < 0
            else "no contribution",
        }
        for name, value in contributions[:5]
    ]
