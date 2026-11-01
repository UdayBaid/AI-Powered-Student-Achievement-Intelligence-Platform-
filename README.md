# AI-Powered Student Achievement Intelligence Platform

A small ML project that estimates Portuguese secondary-school students' final grades from demographic, family, and school-related inputs. It includes a trained regression model, a FastAPI inference API, SHAP explanations, recommendations, and a notebook for training and evaluation.

## Project Layout

```text
archive/legacy/       Preserved files from the older nested project copy
 dataset/             Student Performance dataset
 modules/
  api/
    main.py           FastAPI application
    routes/            Authentication, health, and prediction routes
    schemas/           Request and response models
    services/          Authentication and inference logic
    database.py        SQLite and SQLAlchemy session configuration
  frontend/            React + Vite dashboard and authentication screens
   student_platform.ipynb
   optuna_classfier.py
   best_params.json
   models/
     main.py           Backward-compatible API import path
     explainability.py SHAP explanations
     interpretation.py Grade interpretation text
     recommendation.py Study recommendations
     preprocessor.joblib
     regression_model.joblib
 tests/                Inference and explainability tests
 requirements.txt
```

The `archive/legacy/` files are historical only. Use the root-level `dataset/` and `modules/` files for current development.

## Requirements and Setup

Python 3.14 is the environment used to validate the saved artifacts.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

The requirements pin the versions used by the current model artifacts. Keep scikit-learn, XGBoost, SHAP, NumPy, and joblib compatible with the serialized model and preprocessor when upgrading dependencies.

Before starting the API, replace the `JWT_SECRET` placeholder in `.env` with a random value of at least 32 characters. Generate one with:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

The SQLite database is created at `data/studentai.db` on first startup. `DATABASE_URL` can override this path. Add the deployed frontend origin to `FRONTEND_ORIGINS` as a comma-separated list.

Password reset email requires an SMTP provider. Set `SMTP_HOST`, `SMTP_PORT` (STARTTLS, usually `587`), `SMTP_USERNAME`, `SMTP_PASSWORD`, `SMTP_FROM_EMAIL`, and `FRONTEND_URL` in the ignored `.env` file. No reset token is returned by the API or written to logs. Without SMTP configuration, reset requests return `503` and no token is created.

## Run the API

Run from the repository root:

```powershell
python -m uvicorn modules.api.main:app --host 127.0.0.1 --port 8000 --reload
```

- Health: <http://127.0.0.1:8000/health>
- Interactive API documentation: <http://127.0.0.1:8000/docs>
- Registration: `POST /auth/register` with `name`, `email`, and a password of at least 12 characters.
- Login: `POST /auth/login`; returns a 30-minute JWT and public user information.
- Current user: `GET /auth/me` with `Authorization: Bearer <token>`.
- Request password reset: `POST /auth/forgot-password`; responds generically and sends a one-time email link when SMTP is configured.
- Complete password reset: `POST /auth/reset-password` with the emailed token and a new password. Links expire after 15 minutes; successful resets invalidate existing JWT sessions.
- Prediction: `POST /predict` with `Authorization: Bearer <token>`.
- Saved prediction history: `GET /predictions` with `Authorization: Bearer <token>`; returns only that user's most recent saved records (up to 100).

The request body for prediction is a JSON object with the student features described by the `StudentInput` schema in Swagger. The response includes `predicted_g3`, an interpretation, recommendations, and SHAP explanations. `/health` remains public. Frontend logout removes the browser-stored token; there is no server-side token revocation endpoint.

## Frontend

```powershell
Set-Location frontend
npm install
npm run dev
```

The frontend defaults to the local API at `http://127.0.0.1:8000`. Set `VITE_API_URL` when deploying the frontend elsewhere. Authenticated browser sessions are stored in `sessionStorage` and cleared on logout or when the API rejects the token. Logout is client-side token removal only; it does not revoke a token already issued, which remains valid until expiry.

## Tests

Run from the repository root:

```powershell
python -m pytest -q
```

The tests load the existing model artifacts, check the preprocessor/model feature dimensions, verify SHAP additivity, exercise health/auth/prediction endpoints, and confirm prediction history is user-scoped. They do not retrain models.

## Training and Artifacts

Open `modules/student_platform.ipynb` in VS Code with the project root as the notebook working directory. Running the full notebook performs Optuna searches and can take several minutes. It stratifies train, validation, and test splits; the validation split is used for model selection and the test split for final evaluation. The notebook saves the regression model and preprocessor to `modules/models/`, where the API loads them. Training is not required to run the API.

The active `modules/best_params.json` records the hyperparameters of the currently saved regression model. The notebook updates this file when a new regression training run completes.

The notebook also evaluates a risk classifier, but the current API serves regression only. No classification model artifact or classification API endpoint is included.

## Dataset and Limitations

`dataset/student-por.csv` is the Portuguese-language subset of the UCI Student Performance dataset: <https://archive.ics.uci.edu/dataset/320/student+performance>. It contains 649 student records and 33 columns. The regression pipeline uses `G3` as the target and excludes `G1` and `G2` from its features to avoid leaking earlier grades into the prediction.

This is a small, historical dataset from a specific school context. Predictions are estimates, not guarantees; feature contributions are associations learned by the model, not causal explanations. Recommendations are general study suggestions and should not be used as a substitute for professional educational support.
