"""Pestaña 'Predicciones y modelos' (Nicolle).

V6 Real vs. predicción, V7 Errores del modelo, V8 Comparación de los 3 modelos + tabla comparativa.
Enlace: clic en una barra de V8 selecciona el modelo que muestran V6 y V7 (y la tabla lo resalta).
Datos: src.data.load_predictions() y load_metrics() (3 modelos del Lab 1, sin modelos nuevos).
"""
import plotly.graph_objects as go
from dash import Input, Output, callback, dcc, html

from src.components import card
from src.data import load_metrics, load_predictions
from src.theme import COLORS, empty_fig, style_fig

PRED = load_predictions()
MET = load_metrics()
SERIES = list(dict.fromkeys(PRED["serie"]))  # conserva el orden del Lab 1
MODELOS = list(dict.fromkeys(PRED["modelo"]))
INICIO_PRUEBA = PRED.loc[PRED["conjunto"] == "prueba", "fecha"].min()
FIN_PRUEBA = PRED["fecha"].max()

GRIS_SEL = "#C9D6DD"          # mismo gris de "no seleccionado" que V1
NARANJA_SUAVE = "#F2C48D"     # otras estimaciones (mismo matiz naranja = estimación)
# Cada modelo tiene un patrón de línea fijo; los no seleccionados usan otro tono del mismo naranja
# (naranja = estimación en toda la app). El patrón distingue a los modelos sin depender solo del color.
ESTILO_MODELO = {
    "Suavizamiento exponencial": dict(dash="dash", tono="#9A5414"),
    "ARIMA(1,1,1)": dict(dash="dot", tono="#B86A1C"),
    "Holt-Winters multiplicativo": dict(dash="dashdot", tono="#E3A55A"),
}

METRICAS_TXT = {
    "MAE": "MAE (error absoluto medio): cuántos viajeros por mes se equivoca el modelo, en promedio.",
    "RMSE": "RMSE (raíz del error cuadrático medio): como el MAE, pero castiga más los errores grandes.",
}


def _fmt(n):
    return f"{n:,.0f}"


def _datos(serie, modelo):
    return PRED[(PRED["serie"] == serie) & (PRED["modelo"] == modelo)].sort_values("fecha")


def layout():
    return html.Div([
        html.Div(className="note", children=[
            html.B("Cómo interpretar: "),
            "la línea azul es lo que realmente ocurrió (dato observado); la naranja es una ESTIMACIÓN del modelo. "
            "Los 3 modelos son simples y se construyeron en el Laboratorio 1 con datos hasta marzo de 2021; "
            "aquí se evalúan contra lo ocurrido de abril 2021 a junio 2026 (periodo de prueba)."]),
        html.Div(className="controls", children=[
            html.Div([html.Label("Serie a analizar"), dcc.Dropdown(
                id="m-serie", options=SERIES, value=SERIES[0], clearable=False, persistence=True, persistence_type="session")], className="ctl wide"),
            html.Div([html.Label("Modelo"), dcc.Dropdown(
                id="m-modelo", options=MODELOS, value=MODELOS[0], clearable=False)], className="ctl wide"),
            html.Div([html.Label("Métrica de error"), dcc.RadioItems(
                id="m-metrica", options=["MAE", "RMSE"], value="MAE", inline=True, persistence=True, persistence_type="session")], className="ctl"),
            html.Div([html.Label("Nivel de detalle"), dcc.RadioItems(
                id="m-rango", inline=True, value="prueba", persistence=True, persistence_type="session", options=[
                    {"label": "Solo periodo de prueba", "value": "prueba"},
                    {"label": "Serie completa 2009–2026", "value": "todo"}])], className="ctl"),
            html.Div([html.Label("Comparar en «Real vs. predicción»"), dcc.Checklist(
                id="m-otros", options=[{"label": "Mostrar también los otros 2 modelos", "value": "si"}], value=["si"], inline=True, persistence=True, persistence_type="session")],
                className="ctl"),
        ]),
        html.Div(id="m-resumen", className="note"),
        html.Div(className="grid grid-2", children=[
            card("Real vs. predicción",
                 "¿Qué tan cerca estuvo el modelo de lo que realmente pasó? La zona sombreada es el periodo "
                 "de prueba (datos que el modelo no vio).", "g6"),
            card("Errores del modelo por mes",
                 "Real − predicción. Barras arriba de 0: llegaron MÁS viajeros de los estimados (el modelo "
                 "subestimó); abajo de 0: llegaron menos (sobrestimó).", "g7"),
            card("Comparación de los 3 modelos",
                 "Error promedio de cada modelo en el periodo de prueba: barra más corta = modelo más preciso. "
                 "Haga clic en una barra para ver ese modelo en las otras gráficas.", "g8"),
            html.Div(className="card", children=[
                html.H3("Tabla comparativa de modelos"),
                html.P("Mismas métricas en números exactos para la serie elegida. Fila resaltada = modelo "
                       "seleccionado; ★ = menor error.", className="sub"),
                html.Div(id="m-tabla"),
                html.Ul(className="sub", children=[
                    html.Li(METRICAS_TXT["MAE"]),
                    html.Li(METRICAS_TXT["RMSE"]),
                    html.Li("MAPE: el mismo error expresado como porcentaje de lo observado "
                            "(30 % = se equivoca en promedio en 3 de cada 10 viajeros)."),
                ]),
            ]),
        ]),
        html.Div(className="note", style={"marginTop": "16px"}, children=[
            html.B("Limitaciones: "),
            html.Ul([
                html.Li("Los modelos aprendieron con datos que terminan en marzo de 2021, en plena pandemia; "
                        "por eso no anticiparon la recuperación del turismo y sus errores en el periodo de "
                        "prueba son altos (MAPE entre 30 % y 78 %)."),
                html.Li("Son modelos simples de series de tiempo: solo usan la historia de la propia serie, "
                        "no factores externos (economía, eventos, política migratoria)."),
                html.Li("Las predicciones sirven para comparar tendencias y estacionalidad, no como cifra exacta "
                        "para planificar. No se construyeron modelos nuevos para este tablero."),
                html.Li("Que un modelo tenga menor error indica que se ajustó mejor en este periodo; no explica "
                        "por qué cambió el número de viajeros."),
            ]),
        ]),
    ])


# ---- Enlace: clic en V8 -> modelo seleccionado ----------------------------------------
@callback(Output("m-modelo", "value"), Input("g8", "clickData"), prevent_initial_call=True)
def elegir_modelo(click):
    return click["points"][0]["y"]


# ---- Resumen: hallazgo observado vs. estimación vs. interpretación -------------------
@callback(Output("m-resumen", "children"), Input("m-serie", "value"), Input("m-modelo", "value"))
def resumen(serie, modelo):
    p = _datos(serie, modelo)
    p = p[p["conjunto"] == "prueba"]
    if p.empty:
        return "No hay información disponible para esta selección."
    real, pred = p["real"].mean(), p["prediccion"].mean()
    dif = (real - pred) / real * 100
    return [
        html.B(f"{serie} · {modelo}. "),
        html.Span(f"Observado: entre {INICIO_PRUEBA:%m/%Y} y {FIN_PRUEBA:%m/%Y} llegaron en promedio "
                  f"{_fmt(real)} viajeros por mes. "),
        html.Span(f"Estimación del modelo: {_fmt(pred)} por mes "
                  f"({abs(dif):.0f} % {'menos' if dif > 0 else 'más'} que lo observado). "),
        html.I("Interpretación: el modelo " + ("subestimó" if dif > 0 else "sobrestimó") +
               " la llegada de viajeros en este periodo; úselo como referencia de tendencia, no como cifra exacta."),
    ]


# ---- V6: real vs. predicción ----------------------------------------------------------
@callback(Output("g6", "figure"), Input("m-serie", "value"), Input("m-modelo", "value"),
          Input("m-rango", "value"), Input("m-otros", "value"))
def fig_g6(serie, modelo, rango, otros):
    p = _datos(serie, modelo)
    if p.empty:
        return empty_fig()
    if rango == "prueba":
        p = p[p["conjunto"] == "prueba"]
    fig = go.Figure()
    fig.add_vrect(x0=INICIO_PRUEBA, x1=FIN_PRUEBA, fillcolor=COLORS["estimate"], opacity=0.08, line_width=0,
                  annotation_text="Periodo de prueba", annotation_position="top left",
                  annotation_font=dict(color=COLORS["muted"], size=12))
    fig.add_trace(go.Scatter(x=p["fecha"], y=p["real"], name="Observado", mode="lines",
                             line=dict(color=COLORS["primary"], width=2.5),
                             hovertemplate="%{x|%b %Y}<br>Observado: %{y:,.0f}<extra></extra>"))
    if "si" in (otros or []):
        for m in MODELOS:
            if m == modelo:
                continue
            o = _datos(serie, m)
            o = o[o["conjunto"] == "prueba"]
            est = ESTILO_MODELO.get(m, dict(dash="dot", tono=NARANJA_SUAVE))
            fig.add_trace(go.Scatter(x=o["fecha"], y=o["prediccion"], name=m, mode="lines", opacity=0.9,
                                     line=dict(color=est["tono"], width=1.8, dash=est["dash"]),
                                     hovertemplate=f"%{{x|%b %Y}}<br>{m}: %{{y:,.0f}}<extra></extra>"))
    t = p[p["conjunto"] == "prueba"]
    fig.add_trace(go.Scatter(x=t["fecha"], y=t["prediccion"], name=f"Estimación: {modelo}", mode="lines",
                             line=dict(color=COLORS["estimate"], width=3.5,
                                       dash=ESTILO_MODELO.get(modelo, {}).get("dash", "dash")),
                             hovertemplate="%{x|%b %Y}<br>Estimación: %{y:,.0f}<extra></extra>"))
    fig.update_yaxes(title="Viajeros por mes", rangemode="tozero")
    fig.update_xaxes(title=None)
    fig.update_layout(hovermode="x unified")
    return style_fig(fig, height=380)


# ---- V7: errores mes a mes ------------------------------------------------------------
@callback(Output("g7", "figure"), Input("m-serie", "value"), Input("m-modelo", "value"))
def fig_g7(serie, modelo):
    p = _datos(serie, modelo)
    p = p[p["conjunto"] == "prueba"]
    if p.empty:
        return empty_fig()
    err = p["real"] - p["prediccion"]
    fig = go.Figure(go.Bar(
        x=p["fecha"], y=err, marker_color=[COLORS["estimate"] if e >= 0 else NARANJA_SUAVE for e in err],
        customdata=p[["real", "prediccion"]].values,
        hovertemplate=("%{x|%b %Y}<br>Error: %{y:,.0f} viajeros<br>Observado: %{customdata[0]:,.0f}"
                       "<br>Estimado: %{customdata[1]:,.0f}<extra></extra>")))
    fig.add_hline(y=0, line_color=COLORS["text"], line_width=1)
    fig.update_yaxes(title="Real − predicción (viajeros)")
    fig.update_xaxes(title=None)
    return style_fig(fig, height=380)


# ---- V8: comparación de modelos (clic = seleccionar) ----------------------------------
@callback(Output("g8", "figure"), Input("m-serie", "value"), Input("m-modelo", "value"),
          Input("m-metrica", "value"))
def fig_g8(serie, modelo, metrica):
    m = MET[MET["serie"] == serie].sort_values(metrica, ascending=False)
    if m.empty:
        return empty_fig()
    colores = [COLORS["estimate"] if x == modelo else GRIS_SEL for x in m["modelo"]]
    fig = go.Figure(go.Bar(
        x=m[metrica], y=m["modelo"], orientation="h", marker_color=colores,
        text=[_fmt(v) for v in m[metrica]], textposition="auto",
        customdata=m["MAPE"], hovertemplate=(f"%{{y}}<br>{metrica}: %{{x:,.0f}} viajeros/mes"
                                             "<br>MAPE: %{customdata:.1f} %<extra>Clic para seleccionar</extra>")))
    fig.update_xaxes(title=f"{metrica}: viajeros por mes (menor = mejor)")
    fig.update_yaxes(title=None)
    return style_fig(fig, height=320).update_layout(margin=dict(r=40))


# ---- Tabla comparativa (elemento complementario) --------------------------------------
@callback(Output("m-tabla", "children"), Input("m-serie", "value"), Input("m-modelo", "value"),
          Input("m-metrica", "value"))
def tabla(serie, modelo, metrica):
    m = MET[MET["serie"] == serie].sort_values(metrica)
    if m.empty:
        return html.P("No hay información disponible para esta selección.", className="hint")
    mejor = {c: m[c].min() for c in ["MAE", "RMSE", "MAPE"]}
    th = {"textAlign": "right", "padding": "8px 10px", "borderBottom": f"2px solid {COLORS['muted']}"}
    td = {"textAlign": "right", "padding": "8px 10px", "borderBottom": "1px solid #E4E9ED"}

    def celda(fila, c, txt):
        return html.Td(txt + (" ★" if fila[c] == mejor[c] else ""), style=td)

    filas = []
    for _, f in m.iterrows():
        sel = f["modelo"] == modelo
        filas.append(html.Tr(style={"background": "#FCEBD7" if sel else "transparent",
                                    "fontWeight": 600 if sel else 400}, children=[
            html.Td(f["modelo"], style={**td, "textAlign": "left"}),
            celda(f, "MAE", _fmt(f["MAE"])),
            celda(f, "RMSE", _fmt(f["RMSE"])),
            celda(f, "MAPE", f"{f['MAPE']:.1f} %"),
        ]))
    return html.Table(style={"width": "100%", "borderCollapse": "collapse", "fontSize": "14px"}, children=[
        html.Thead(html.Tr([html.Th("Modelo", style={**th, "textAlign": "left"}),
                            html.Th("MAE", style=th), html.Th("RMSE", style=th), html.Th("MAPE", style=th)])),
        html.Tbody(filas),
    ])
