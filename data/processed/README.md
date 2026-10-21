# Datos procesados (generados desde el Lab 1)
Se generan con `time-series-lab/venv/bin/python scripts/exportar_datos_lab1.py` y **sí se versionan**
(así el equipo no necesita el Excel original, que está ignorado por git por su tamaño).

- `viajeros_detalle.csv`: fecha (YYYY-MM-01), via, tipo_viajero, region, viajeros (suma mensual).
- `viajeros_pais_anual.csv`: anio, region, pais, viajeros.
- `../models/predicciones.csv`: serie, modelo, fecha, conjunto (entrenamiento/prueba), real, prediccion.
- `../models/metricas.csv`: serie, modelo, MAE, RMSE, MAPE, AIC, BIC.

Fuente: Base de Migración 2009–2026 (jun) del Laboratorio 1.
Nota: la categoría "Viajero" se redefinió en 2022-2023; para series comparables use Turista + Excursionista.
