# Observatorio de Turismo Sostenible – Laboratorio 10 (CC3066 Data Science, UVG)

Tablero interactivo en **Plotly Dash** para directivos y tomadores de decisiones del sector turístico.

## Equipo
Jose Ruiz · Gerardo · Nicolle · Alex · Juarez  (responsables: `docs/PLAN.md`; pendientes: `docs/TAREAS_PENDIENTES.md`)

## Ejecutar
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python app.py        # http://127.0.0.1:8050
```

## Estructura
| Ruta | Contenido |
|---|---|
| `app.py` | Layout general y pestañas |
| `src/pages/explorar.py` | Pestaña Explorar: V1 y V2 enlazadas (avance); V3–V5 y selección de gráficas visibles (Juarez) |
| `src/pages/modelos.py` | Pestaña Modelos: V6–V8 enlazadas y tabla comparativa (Nicolle) |
| `src/theme.py`, `src/components.py` | Paleta/estilo común y tarjetas reutilizables |
| `src/data.py` | Carga de los CSV procesados |
| `time-series-lab/` | Laboratorio 1 (datos, código, modelos e infografía) |
| `scripts/exportar_datos_lab1.py` | Genera `data/processed/` y `models/` desde el Lab 1 |
| `data/processed/`, `models/` | Datos y resultados de los 3 modelos (se versionan) |
| `docs/` | Documento de avance (.docx), plan, checklist, tareas pendientes y fuentes |


