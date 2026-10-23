
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, State, callback, ctx, dcc, html

from src.components import card
from src.data import load_detalle, load_paises
from src.theme import COLORS, SEQUENTIAL, empty_fig, style_fig

DET = load_detalle()
PAISES = load_paises()
PAISES = PAISES[PAISES["pais"] != PAISES["region"]]  # cruceros no traen detalle por país (pais == region)
VIAS = sorted(DET["via"].unique())
TIPOS = sorted(DET["tipo_viajero"].unique())
TIPOS_DEF = ["Turista", "Excursionista"]  # comparables en todo el periodo (ver data/processed/README.md)
ANIOS = [int(a) for a in sorted(DET["anio"].unique())]  # int nativo: Dash no serializa np.int32
# Tonos de azul de la paleta: la vía es categórica y no debe parecer observado/estimado/alerta
COLOR_VIA = {"Terrestre": SEQUENTIAL[4], "Aérea": COLORS["primary"], "Marítima": SEQUENTIAL[1]}
GRAFICAS = ["g1", "g2", "g3", "g4", "g5"]
NOMBRES = ["Regiones", "Evolución", "Países", "Calendario", "Vía de ingreso"]
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]


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
            html.Div([html.Label("Gráficas a mostrar"), dcc.Checklist(
                id="f-graficas", options=[{"label": n, "value": g} for g, n in zip(GRAFICAS, NOMBRES)],
                value=GRAFICAS, inline=True)], className="ctl wide"),
            html.Button("Quitar selección de región", id="btn-reset", n_clicks=0),
        ]),
        html.Div(id="msg-sel", className="hint"),
        html.Div(id="msg-vis", className="hint"),
        # Cada tarjeta va en un contenedor "w-gN" para poder ocultarla (req. 3.3) sin perder su estado
        html.Div(className="grid", children=[html.Div(c, id=f"w-{gid}") for gid, c in zip(GRAFICAS, [
            card("Viajeros por región de origen",
                 "Haga clic en una barra para ver el detalle de esa región en las demás gráficas.", "g1"),
            card("Evolución en el tiempo",
                 "Cómo cambia la llegada de viajeros. Cambie el nivel de detalle arriba (anual o mensual).", "g2"),
            card("Países de origen",
                 "Los 10 países con más viajeros de la región elegida (o de todas si no hay selección). "
                 "Responde a los años, no al tipo de viajero ni a la vía. Guatemala figura como origen: "
                 "son residentes que regresan del exterior.", "g3"),
            card("Calendario mes × año",
                 "Meses más intensos (color más oscuro = más viajeros). Responde a todos los filtros y a la región "
                 "elegida. Las celdas vacías son meses sin datos (2026 llega hasta junio).", "g4"),
            card("Vía de ingreso",
                 "Por dónde entran los viajeros cada año: aérea, terrestre o marítima. Responde a los filtros y a la "
                 "región elegida; cada barra suma todas las vías seleccionadas.", "g5"),
        ])]),
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


# ---- Req. 3.3: el usuario elige qué gráficas ver --------------------------------------
@callback([Output(f"w-{g}", "style") for g in GRAFICAS] + [Output("msg-vis", "children")],
          Input("f-graficas", "value"))
def visibilidad(visibles):
    visibles = visibles or []
    estilos = [{} if g in visibles else {"display": "none"} for g in GRAFICAS]
    aviso = "" if visibles else "No hay gráficas seleccionadas. Marque al menos una en 'Gráficas a mostrar'."
    return estilos + [aviso]


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


# ---- V3: top 10 países (aumenta el nivel de detalle de región a país) -----------------
@callback(Output("g3", "figure"), Input("f-anios", "value"), Input("sel-region", "data"))
def fig_g3(anios, sel):
    d = PAISES[(PAISES["anio"] >= anios[0]) & (PAISES["anio"] <= anios[1])]
    if sel:
        d = d[d["region"] == sel]
    if d.empty:
        return empty_fig(f"'{sel}' no tiene detalle por país." if sel else
                         "No hay información disponible para esta selección.")
    top = d.groupby("pais", as_index=False)["viajeros"].sum().nlargest(10, "viajeros").sort_values("viajeros")
    fig = go.Figure(go.Bar(x=top["viajeros"], y=top["pais"], orientation="h", marker_color=COLORS["primary"],
                           hovertemplate="%{y}: %{x:,.0f} viajeros<extra></extra>"))
    fig.update_xaxes(title="Viajeros en el periodo")
    return style_fig(fig, title=f"Top 10 – {sel or 'todas las regiones'}")


# ---- V4: calendario mes x año (mapa de calor) -----------------------------------------
@callback(Output("g4", "figure"), Input("f-anios", "value"), Input("f-tipos", "value"),
          Input("f-vias", "value"), Input("sel-region", "data"))
def fig_g4(anios, tipos, vias, sel):
    d = filtrar(anios, tipos, vias, sel)
    if d.empty:
        return empty_fig()
    t = d.groupby(["anio", "mes"])["viajeros"].sum().unstack("mes").reindex(columns=range(1, 13))
    n = len(SEQUENTIAL) - 1
    fig = go.Figure(go.Heatmap(
        z=t.values, x=MESES, y=[str(a) for a in t.index], colorscale=[[i / n, c] for i, c in enumerate(SEQUENTIAL)],
        xgap=2, ygap=2, hoverongaps=False, colorbar=dict(title="Viajeros"),
        hovertemplate="%{y} · %{x}: %{z:,.0f} viajeros<extra></extra>"))
    fig.update_yaxes(autorange="reversed", type="category")
    fig.update_xaxes(side="top")
    return style_fig(fig, height=440)


# ---- V5: vía de ingreso por año (barras apiladas) -------------------------------------
@callback(Output("g5", "figure"), Input("f-anios", "value"), Input("f-tipos", "value"),
          Input("f-vias", "value"), Input("sel-region", "data"))
def fig_g5(anios, tipos, vias, sel):
    d = filtrar(anios, tipos, vias, sel)
    if d.empty:
        return empty_fig()
    t = d.groupby(["anio", "via"], as_index=False)["viajeros"].sum()
    fig = px.bar(t, x="anio", y="viajeros", color="via", color_discrete_map=COLOR_VIA,
                 category_orders={"via": list(COLOR_VIA)})
    fig.update_traces(hovertemplate="%{x} · %{fullData.name}: %{y:,.0f} viajeros<extra></extra>")
    fig.update_xaxes(title=None, type="category")
    fig.update_yaxes(title="Viajeros")
    fig.update_layout(legend_title_text="Vía")
    return style_fig(fig)
