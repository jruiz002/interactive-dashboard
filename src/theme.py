"""Paleta y tipografía únicas del tablero. Cada color tiene UN significado fijo en toda la app."""

# Significado semántico (justificación en el documento de diseño, sección 4.1)
COLORS = {
    "primary": "#1F6F8B",    # turismo / valor observado (hallazgos)
    "estimate": "#E08E2B",   # predicción o estimación del modelo (nunca un dato observado)
    "positive": "#3A9D6B",   # mejora / sostenibilidad favorable
    "negative": "#C8553D",   # alerta / deterioro
    "neutral": "#8A94A0",    # contexto, categorías sin énfasis
    "bg": "#F5F7F9",
    "card": "#FFFFFF",
    "text": "#1E2A33",
    "muted": "#5B6770",
}

# Secuencial de un solo matiz (valores bajos -> altos)
SEQUENTIAL = ["#D6E9F0", "#9CCADB", "#5AA5BF", "#1F6F8B", "#0F3F52"]

FONT_FAMILY = "Inter, 'Segoe UI', Roboto, Arial, sans-serif"


def style_fig(fig, title=None, height=360):
    """Estilo común para que todas las gráficas se vean como un solo sistema."""
    fig.update_layout(
        title=dict(text=title, x=0, font=dict(size=16, color=COLORS["text"])) if title else None,
        font=dict(family=FONT_FAMILY, size=13, color=COLORS["text"]),
        paper_bgcolor=COLORS["card"],
        plot_bgcolor=COLORS["card"],
        margin=dict(l=50, r=20, t=50 if title else 20, b=45),
        height=height,
        legend=dict(orientation="h", y=-0.2),
        hoverlabel=dict(font_size=13),
    )
    fig.update_xaxes(showgrid=False, linecolor="#CBD2D9")
    fig.update_yaxes(gridcolor="#E4E9ED", zeroline=False)
    return fig


def empty_fig(message="No hay información disponible para esta selección."):
    """Mensaje claro cuando una selección no tiene datos (requisito de la rúbrica)."""
    import plotly.graph_objects as go

    fig = go.Figure()
    fig.add_annotation(text=message, showarrow=False, font=dict(size=15, color=COLORS["muted"]))
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return style_fig(fig)
