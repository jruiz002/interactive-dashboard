"""Pestaña 'Explorar datos'.

AVANCE (Jose Ruiz): V1 y V2 funcionando y enlazadas (clic en V1 filtra V2).
PENDIENTE (Juarez): V3, V4, V5 y selección de gráficas visibles (ver docs/TAREAS_PENDIENTES.md).
"""
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, dcc, html

from src.components import card, pendiente
from src.data import load_detalle
from src.theme import COLORS, empty_fig, style_fig

DET = load_detalle()
VIAS = sorted(DET["via"].unique())
TIPOS = sorted(DET["tipo_viajero"].unique())
TIPOS_DEF = ["Turista", "Excursionista"]  # comparables en todo el periodo (ver data/processed/README.md)
ANIOS = [int(a) for a in sorted(DET["anio"].unique())]  # int nativo: Dash no serializa np.int32


def filtrar(anios, tipos, vias, region=None):
    """Filtro común a todas las gráficas de exploración (úsese también en V3–V5)."""
    d = DET[(DET["anio"] >= anios[0]) & (DET["anio"] <= anios[1])]
    d = d[d["tipo_viajero"].isin(tipos or []) & d["via"].isin(vias or [])]
    return d[d["region"] == region] if region else d


def layout():
    marks = {a: str(a) for a in ANIOS if a % 3 == 0 or a == ANIOS[-1]}
    return html.Div([
        html.Div(className="controls", children=[
            html.Div([html.Label("Años"), dcc.RangeSlider(
                id="f-anios", min=ANIOS[0], max=ANIOS[-1], step=1, value=[ANIOS[0], ANIOS[-1]],
                marks=marks, tooltip={"placement": "bottom"})], className="ctl wide"),
            html.Div([html.Label("Nivel de detalle temporal"), dcc.RadioItems(
                id="f-detalle", options=[{"label": "Anual", "value": "anio"}, {"label": "Mensual", "value": "mes"}],
                value="anio", inline=True)], className="ctl"),
            html.Div([html.Label("Tipo de viajero"), dcc.Dropdown(
                id="f-tipos", options=TIPOS, value=TIPOS_DEF, multi=True, clearable=False)], className="ctl wide"),
            html.Div([html.Label("Vía de ingreso"), dcc.Dropdown(
                id="f-vias", options=VIAS, value=VIAS, multi=True, clearable=False)], className="ctl wide"),
            html.Button("Quitar selección de región", id="btn-reset", n_clicks=0),
        ]),
        html.Div(id="msg-sel", className="hint"),
        html.Div(className="grid", children=[
            card("Viajeros por región de origen",
                 "Haga clic en una barra para ver el detalle de esa región en las demás gráficas.", "g1"),
            card("Evolución en el tiempo",
                 "Cómo cambia la llegada de viajeros. Cambie el nivel de detalle arriba (anual o mensual).", "g2"),
            pendiente("Países de origen", "Top 10 países de la región elegida (aumenta el nivel de detalle).", "Juarez"),
            pendiente("Calendario mes × año", "Meses más intensos (color más oscuro = más viajeros).", "Juarez"),
            pendiente("Vía de ingreso", "Por dónde entran los viajeros cada año: aérea, terrestre o marítima.", "Juarez"),
        ]),
        html.P("2026 incluye datos hasta junio. 'Viajero' cambió de definición en 2022-2023; por eso Turista + "
               "Excursionista es la combinación comparable en todo el periodo.", className="hint"),
    ])


# ---- Selección enlazada: clic en V1 -> región seleccionada ----------------------------
@callback(Output("sel-region", "data"), Input("g1", "clickData"), Input("btn-reset", "n_clicks"),
          State("sel-region", "data"), prevent_initial_call=True)
def set_region(click, _n, actual):
    if ctx.triggered_id == "btn-reset" or not click:
        return None
    nueva = click["points"][0]["y"]
    return None if nueva == actual else nueva


@callback(Output("msg-sel", "children"), Input("sel-region", "data"))
def mensaje(sel):
    return (f"Mostrando el detalle de la región: {sel}" if sel else
            "Mostrando todas las regiones. Haga clic en una barra para ver el detalle de una región.")


# ---- V1: barras por región (interactiva) ---------------------------------------------
@callback(Output("g1", "figure"), Input("f-anios", "value"), Input("f-tipos", "value"),
          Input("f-vias", "value"), Input("sel-region", "data"))
def fig_g1(anios, tipos, vias, sel):
    d = filtrar(anios, tipos, vias).groupby("region", as_index=False)["viajeros"].sum().sort_values("viajeros")
    if d.empty:
        return empty_fig()
    colores = [COLORS["primary"] if (not sel or x == sel) else "#C9D6DD" for x in d["region"]]
    fig = go.Figure(go.Bar(x=d["viajeros"], y=d["region"], orientation="h", marker_color=colores,
                           hovertemplate="%{y}: %{x:,.0f} viajeros<extra></extra>"))
    fig.update_xaxes(title="Viajeros en el periodo")
    return style_fig(fig)


# ---- V2: línea temporal enlazada con V1 (anual <-> mensual) ---------------------------
@callback(Output("g2", "figure"), Input("f-anios", "value"), Input("f-tipos", "value"),
          Input("f-vias", "value"), Input("sel-region", "data"), Input("f-detalle", "value"))
def fig_g2(anios, tipos, vias, sel, detalle):
    d = filtrar(anios, tipos, vias, sel)
    if d.empty:
        return empty_fig()
    col = "anio" if detalle == "anio" else "fecha"
    t = d.groupby(col, as_index=False)["viajeros"].sum()
    fig = px.line(t, x=col, y="viajeros", markers=(detalle == "anio"), color_discrete_sequence=[COLORS["primary"]])
    fig.update_xaxes(title=None)
    fig.update_yaxes(title="Viajeros")
    return style_fig(fig)
