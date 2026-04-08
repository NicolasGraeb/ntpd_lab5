import os
from typing import Any, Dict, List, Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    func,
    select,
)
from sqlalchemy.engine import Engine

def _database_url() -> Optional[str]:
    direct_url = os.getenv("DATABASE_URL")
    if direct_url:
        return direct_url

    host = os.getenv("DB_HOST")
    port = os.getenv("DB_PORT", "5432")
    name = os.getenv("DB_NAME")
    user = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")

    if all([host, name, user, password]):
        return f"postgresql://{user}:{password}@{host}:{port}/{name}"
    return None


DATABASE_URL = _database_url()

engine: Optional[Engine] = create_engine(DATABASE_URL) if DATABASE_URL else None

metadata = MetaData()

predictions = Table(
    "predictions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sepal_length", Float, nullable=False),
    Column("sepal_width", Float, nullable=False),
    Column("petal_length", Float, nullable=False),
    Column("petal_width", Float, nullable=False),
    Column("prediction", String, nullable=False),
    Column("probability", Float, nullable=False),
    Column(
        "created_at",
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)


def init_db() -> bool:
    if engine:
        metadata.create_all(engine)
        return True
    return False


def insert_prediction(
    *,
    sepal_length: float,
    sepal_width: float,
    petal_length: float,
    petal_width: float,
    prediction: str,
    probability: float,
) -> Optional[int]:
    if not engine:
        return None

    with engine.begin() as conn:
        result = conn.execute(
            predictions.insert().values(
                sepal_length=sepal_length,
                sepal_width=sepal_width,
                petal_length=petal_length,
                petal_width=petal_width,
                prediction=prediction,
                probability=probability,
            ).returning(predictions.c.id)
        )
        return result.scalar_one()


def list_predictions(*, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
    if not engine:
        return []

    limit = max(1, min(limit, 500))
    offset = max(0, offset)

    stmt = (
        select(
            predictions.c.id,
            predictions.c.sepal_length,
            predictions.c.sepal_width,
            predictions.c.petal_length,
            predictions.c.petal_width,
            predictions.c.prediction,
            predictions.c.probability,
            predictions.c.created_at,
        )
        .order_by(predictions.c.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    with engine.connect() as conn:
        rows = conn.execute(stmt).mappings().all()

    return [dict(r) for r in rows]

