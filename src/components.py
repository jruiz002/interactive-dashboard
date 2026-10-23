from dash import dcc, html


def card(title, subtitle, graph_id):
    """Tarjeta con título claro y subtítulo 'para qué sirve' (req. 3.4)."""
    return html.Div(className="card", children=[
        html.H3(title), html.P(subtitle, className="sub"),
        dcc.Graph(id=graph_id, config={"displaylogo": False}),
    ])


def pendiente(title, que_muestra, responsable, graph_id=None):
    """Tarjeta provisional de una visualización que aún no se implementa.
    Al implementarla: reemplazar por card(...) y agregar su callback en el mismo módulo."""
    return html.Div(className="card pendiente", children=[
        html.H3(title), html.P(que_muestra, className="sub"),
        html.P(f"PENDIENTE – responsable: {responsable}. Ver docs/TAREAS_PENDIENTES.md", className="tag"),
    ])
