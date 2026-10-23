# Datos procesados (generados desde el Lab 1)
Se generan con `time-series-lab/venv/bin/python scripts/exportar_datos_lab1.py` y **sí se versionan**
(así el equipo no necesita el Excel original, que está ignorado por git por su tamaño).

- `viajeros_detalle.csv` (6 984 filas): fecha (YYYY-MM-01), via, tipo_viajero, region, viajeros (suma mensual).
  Periodo: enero 2009 – junio 2026.
- `viajeros_pais_anual.csv` (2 843 filas): anio, region, pais, viajeros. Periodo: 2009 – 2026 (2026 hasta junio).
- `../models/predicciones.csv` (2 520 filas): serie, modelo, fecha, conjunto (entrenamiento/prueba), real, prediccion.
- `../models/metricas.csv` (12 filas): serie, modelo, MAE, RMSE, MAPE, AIC, BIC. 4 series × 3 modelos.

Fuente: Base de Migración 2009–2026 (jun) del Laboratorio 1 (ver `docs/FUENTES.md`).

## Verificación del contenido
- Sin valores nulos y con `viajeros` entero (redondeado al exportar). Los dos archivos de viajeros suman casi lo mismo
  (52 287 933 en el detalle y 52 287 944 por país; la diferencia son 11 viajeros por redondeo).
- `via`: Aérea, Marítima y Terrestre. `tipo_viajero`: Turista, Excursionista, Viajero y Cruceristas.
- Las series de modelos son: Total viajeros, Vía Aérea, Vía Terrestre y Tipo: Turista; cada una con los 3 modelos.

## Advertencias para usar los datos
- **Tipo de viajero.** "Viajero" cambia de volumen y de definición (crece desde 2016 y se dispara en 2022); por eso Turista +
  Excursionista es la combinación comparable en todo el periodo. "Cruceristas" existe de 2009 a 2022 (en 2022 con la
  región "Cruceros") y no hay registros después; todos los cruceristas entran por vía marítima.
- **`viajeros_pais_anual.csv` no tiene tipo de viajero ni vía.** Incluye todos los tipos, así que no se puede filtrar por ellos.
- **Filas sin país real.** En las regiones "Cruceristas" y "Cruceros" el país es igual a la región (no hay detalle por país);
  la región "0" tiene 2 filas (2022: Islas Vírgenes Americanas y República Democrática del Congo). "Otros Paises Del Mundo"
  solo tiene datos de 2009 a 2022. El tablero excluye las filas de cruceros en V3.
- **Cobertura por región.** El número de países varía mucho: América Del Norte tiene 3 (Estados Unidos, México y Canadá);
  Europa, 60.
- **Guatemala figura como país de origen** (es el segundo de América Del Centro); es un origen reportado en la base, no un error.
- 2026 llega hasta junio: no comparar el total de 2026 con años completos.
