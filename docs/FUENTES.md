# Fuentes de datos
| Archivo | Fuente | Responsable |
|---|---|---|
| time-series-lab/data/raw/Base_Migracion_2009-2026jun.xlsx (ignorado por git, 9 MB) | Base de Migración 2009–2026 (jun), provista en el Laboratorio 1 del curso. Institución que la publica: Instituto Guatemalteco de Turismo (INGUAT) / Instituto Guatemalteco de Migración (IGM), según la fuente citada en la infografía del Laboratorio 1 (`time-series-lab/infographic/create_deliverables.py`). | Juarez |
| data/processed/*.csv, models/*.csv | Derivados del anterior con `scripts/exportar_datos_lab1.py`; los modelos son los del Laboratorio 1 (no se crearon modelos nuevos) | Jose Ruiz |

## Qué contiene la base
Viajeros internacionales que ingresan a Guatemala, por mes (enero 2009 – junio 2026), vía de ingreso (aérea, terrestre,
marítima), país y región de origen y tipo de viajero. La base solo contiene flujos de viajeros: no incluye causas ni
indicadores ambientales o sociales.

## Qué usa cada visualización
| Visualización | Archivo |
|---|---|
| V1, V2, V4, V5 | `data/processed/viajeros_detalle.csv` |
| V3 | `data/processed/viajeros_pais_anual.csv` (no tiene tipo de viajero ni vía, por eso V3 solo responde a los años y a la región) |
| V6, V7, V8 y tabla de modelos | `models/predicciones.csv`, `models/metricas.csv` |

## Limitaciones de la fuente
- 2026 incluye datos solo hasta junio.
- La categoría "Viajero" cambia de volumen y de definición en el periodo; para series comparables se usa Turista + Excursionista.
- El detalle por país es anual y sin vía ni tipo de viajero (ver `data/processed/README.md`).

## Herramientas
Plotly Dash y Plotly (gráficas), pandas (datos): código abierto, ver `requirements.txt`.
