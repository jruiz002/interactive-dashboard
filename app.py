"""Observatorio de Turismo Sostenible - Laboratorio 10 (Plotly Dash).

Ejecutar:  python app.py   ->  http://127.0.0.1:8050
Datos: viajeros internacionales a Guatemala 2009-2026 (Lab 1). Modelos: Lab 1 (sin modelos nuevos).
Estructura: una pestaña por módulo en src/pages/ (cada integrante trabaja en su archivo).
"""
from dash import Dash, Input, Output, dcc, html

from src.pages import explorar, modelos

app = Dash(__name__, title="Observatorio de Turismo Sostenible", suppress_callback_exceptions=True)
server = app.server

app.layout = html.Div([
    html.Header([
        html.H1("Observatorio de Turismo Sostenible – Guatemala"),
        html.P("Explore cuántos viajeros internacionales llegan, de dónde vienen y qué esperar a futuro."),
    ]),
    dcc.Store(id="sel-region", data=None),
    dcc.Tabs(id="tabs", value="explorar", children=[
        dcc.Tab(label="Explorar datos", value="explorar"),
        dcc.Tab(label="Predicciones y modelos", value="modelos"),
        dcc.Tab(label="Cómo leer este tablero", value="ayuda"),
    ]),
    html.Div(id="contenido", className="content"),
])


def layout_ayuda():
    return html.Div(className="note", children=[
        html.H3("Cómo leer este tablero"),
        html.Ul([
            html.Li("Azul = dato observado. Naranja = estimación de un modelo. Gris = contexto."),
            html.Li("Haga clic en una barra de 'Viajeros por región de origen' para enlazar las demás gráficas."),
            html.Li("Los modelos son simples (Laboratorio 1) y sirven de apoyo, no de garantía."),
            html.Li("Los datos muestran QUÉ pasó; no permiten afirmar POR QUÉ."),
        ]),
    ])


@app.callback(Output("contenido", "children"), Input("tabs", "value"))
def render_tab(tab):
    return {"explorar": explorar.layout, "modelos": modelos.layout, "ayuda": layout_ayuda}[tab]()


if __name__ == "__main__":
    app.run(debug=True)
