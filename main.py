from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sklearn.datasets import load_iris
from sklearn.linear_model import LogisticRegression

from db import insert_prediction, list_predictions as list_db_predictions

app = FastAPI()


def _pole_z_lokalizacji(loc):
    czesci = [str(p) for p in loc if p not in ("body", "query", "path")]
    return ".".join(czesci) if czesci else "body"


@app.exception_handler(RequestValidationError)
async def blad_walidacji(request: Request, exc: RequestValidationError):
    problemy = []
    for e in exc.errors():
        pole = _pole_z_lokalizacji(e.get("loc", ()))
        typ = e.get("type", "")
        if typ == "missing":
            problemy.append(
                {
                    "pole": pole,
                    "komunikat": f"brak wymaganej wartości dla cechy: {pole}",
                }
            )
        elif typ.endswith("_parsing") or typ.startswith("type_error"):
            problemy.append(
                {
                    "pole": pole,
                    "komunikat": "wartość musi być liczbą (np. float)",
                }
            )
        else:
            problemy.append(
                {
                    "pole": pole,
                    "komunikat": e.get("msg", "nieprawidłowa wartość"),
                }
            )
    return JSONResponse(
        status_code=422,
        content={
            "error": "nieprawidłowe dane wejściowe",
            "problemy": problemy,
        },
    )

data = load_iris()
X, y = data.data, data.target
model = LogisticRegression(max_iter=200)
model.fit(X, y)

class IrisInput(BaseModel):
    sepal_length: float
    sepal_width: float
    petal_length: float
    petal_width: float

@app.get("/")
def home():
    return {"message": "witaj"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/info")
def info():
    return {
        "model_type": type(model).__name__,
        "n_features": int(model.n_features_in_),
        "feature_names": list(data.feature_names),
        "n_classes": int(len(model.classes_)),
        "class_names": [str(x) for x in data.target_names],
        "dataset": "iris",
    }


@app.post("/predict")
def predict(iris: IrisInput):
    features = [[iris.sepal_length, iris.sepal_width, iris.petal_length, iris.petal_width]]

    prediction = model.predict(features)
    probability = model.predict_proba(features).max()

    species = data.target_names[prediction[0]]
    probability_float = float(probability)
    db_id = insert_prediction(
        sepal_length=iris.sepal_length,
        sepal_width=iris.sepal_width,
        petal_length=iris.petal_length,
        petal_width=iris.petal_width,
        prediction=str(species),
        probability=probability_float,
    )

    return {
        "prediction": species,
        "probability": round(probability_float, 4),
        "prediction_id": db_id,
    }


@app.get("/predictions")
def list_predictions(limit: int = 50, offset: int = 0):
    items = list_db_predictions(limit=limit, offset=offset)
    return {"items": items}