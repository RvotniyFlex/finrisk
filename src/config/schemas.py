# src/config/schemas.py
"""
Схемы данных и helper-функции для валидации.

* Pandera (DataFrameSchema / SchemaModel) → проверка паркет-таблиц
* Pydantic (BaseModel)                  → JSON / YAML конфиги и метрики
"""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Dict, Literal, Union

import pandas as pd
import pandera as pa
from pandera import Column, Check, DataFrameSchema
from pydantic import BaseModel, Field, validator

# ------------------------------------------------------------------------------
# 1️⃣  Pandera: схемы для Parquet-таблиц
# ------------------------------------------------------------------------------

# --- yield_curve.parquet ------------------------------------------------------
yield_curve_schema = DataFrameSchema(
    name="yield_curve",
    columns={
        "date":      Column(pa.DateTime, nullable=False),
        "maturity":  Column(pa.Float,    Check.ge(0.0), description="Годы до погашения"),
        "rate":      Column(
            pa.Float,
            Check.in_range(-0.10, 1.00),
            description="Годовая ставка (10 % = 0.10)",
        ),
    },
    strict=True,
    coerce=True,
)

# --- risk_factors.parquet -----------------------------------------------------
risk_factors_schema = DataFrameSchema(
    name="risk_factors",
    columns={
        "date":       Column(pa.DateTime, nullable=False),
        "factor_id":  Column(pa.String,   Check.str_length(1, 40)),
        "value":      Column(pa.Float,    nullable=False),
    },
    strict=True,
    coerce=True,
    checks=Check.unique_combination(["date", "factor_id"]),
)

# --- portfolio_value.parquet --------------------------------------------------
portfolio_value_schema = DataFrameSchema(
    name="portfolio_value",
    columns={
        "date":        Column(pa.DateTime, nullable=False),
        "scenario_id": Column(pa.Int,      Check.ge(0)),
        "value":       Column(pa.Float,    nullable=False),
    },
    strict=True,
    coerce=True,
    checks=[
        Check.unique_combination(["date", "scenario_id"]),
        Check.isin("scenario_id", range(0, 10_000_000)),
    ],
)

# Реестр для простой адресации
PANDERA_SCHEMAS: Dict[str, DataFrameSchema] = {
    schema.name: schema
    for schema in [
        yield_curve_schema,
        risk_factors_schema,
        portfolio_value_schema,
    ]
}

def validate(df: pd.DataFrame, schema_name: str) -> pd.DataFrame:
    """
    Центральная точка проверки таблиц внутри DAG-ов.

    >>> df = validate(raw_df, "yield_curve")
    """
    schema = PANDERA_SCHEMAS[schema_name]
    return schema.validate(df, lazy=True)         # lazy=True → собирает ВСЕ ошибки


# ------------------------------------------------------------------------------
# 2️⃣  Pydantic: JSON-структуры (backtest_metrics, конфиги и т.д.)
# ------------------------------------------------------------------------------

class VaRMetric(BaseModel):
    confidence: Literal[0.95, 0.99, 0.995]
    horizon_days: int = Field(..., ge=1, le=30)
    value: float

class KupiecTest(BaseModel):
    alpha: float = Field(..., ge=0.0, le=1.0)
    failures: int = Field(..., ge=0)
    p_value: float

class BacktestMetrics(BaseModel):
    """Содержимое backtest_metrics.json"""
    as_of: date
    portfolio: str
    var: VaRMetric
    es: VaRMetric
    kupiec: KupiecTest

    # Обратная совместимость со старым ключом "VaR"
    @validator("var", pre=True)
    def _alias_var(cls, v):
        return v or {}

# Реестр для JSON-валидации
PYDANTIC_MODELS: Dict[str, type[BaseModel]] = {
    "backtest_metrics": BacktestMetrics,
}

def validate_json(payload: dict, model_name: str) -> BaseModel:
    """
    Проверка JSON/Dict перед сохранением в S3.

    >>> metrics = validate_json(message, "backtest_metrics")
    """
    model = PYDANTIC_MODELS[model_name]
    return model.parse_obj(payload)
