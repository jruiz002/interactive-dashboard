"""Carga de datos del tablero (generados desde el Laboratorio 1).

Para regenerar los CSV a partir del Excel original:
    time-series-lab/venv/bin/python scripts/exportar_datos_lab1.py
Contrato de archivos: ver data/processed/README.md
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
PROCESSED = ROOT / "data" / "processed"
MODELS = ROOT / "models"


def _leer(path: Path, **kw) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Falta {path.relative_to(ROOT)}. Ejecute: "
            "time-series-lab/venv/bin/python scripts/exportar_datos_lab1.py")
    return pd.read_csv(path, **kw)


def load_detalle() -> pd.DataFrame:
    """Viajeros mensuales por vía, tipo de viajero y región de origen."""
    df = _leer(PROCESSED / "viajeros_detalle.csv", parse_dates=["fecha"])
    df["anio"] = df["fecha"].dt.year
    df["mes"] = df["fecha"].dt.month
    return df


def load_paises() -> pd.DataFrame:
    """Viajeros anuales por región y país (para el detalle de V3)."""
    return _leer(PROCESSED / "viajeros_pais_anual.csv")


def load_predictions() -> pd.DataFrame:
    """Predicciones de los 3 modelos del Lab 1. Columnas: serie, modelo, fecha, conjunto, real, prediccion."""
    return _leer(MODELS / "predicciones.csv", parse_dates=["fecha"])


def load_metrics() -> pd.DataFrame:
    """Métricas de evaluación del Lab 1 (conjunto de prueba). Columnas: serie, modelo, MAE, RMSE, MAPE, AIC, BIC."""
    return _leer(MODELS / "metricas.csv")
