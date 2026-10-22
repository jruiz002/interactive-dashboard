"""Pestaña 'Predicciones y modelos'.

PENDIENTE (Nicolle): V6, V7, V8 y tabla comparativa (ver docs/TAREAS_PENDIENTES.md).
Datos listos: src.data.load_predictions() y load_metrics() (3 modelos del Lab 1, sin modelos nuevos).
"""
from dash import html

from src.components import pendiente


def layout():
    return html.Div([
        html.Div(className="note", children=[
            html.B("Cómo interpretar: "),
            "la línea naranja es una ESTIMACIÓN del modelo, no un dato observado. Los modelos son simples (Lab 1)."]),
        html.Div(className="grid", children=[
            pendiente("Real vs. predicción", "¿Qué tan cerca está el modelo de lo observado?", "Nicolle"),
            pendiente("Errores del modelo", "Real − predicción por mes: ¿sobrestima o subestima?", "Nicolle"),
            pendiente("Comparación de modelos", "MAE/RMSE de los 3 modelos; clic para elegir uno.", "Nicolle"),
        ]),
    ])
