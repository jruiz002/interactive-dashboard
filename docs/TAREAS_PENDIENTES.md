# Tareas pendientes para la ENTREGA FINAL (domingo 25-oct-2026)
Reparto entre **Nicolle, Alex y Juarez**. Cada quien trabaja en SU archivo (menos conflictos de git) y hace commits propios
en una rama `feat/<tarea>-<nombre>` + Pull Request a `main`. La rúbrica revisa el historial.

Cómo arrancar: ver `README.md`. Estilos/colores: `src/theme.py` (usar solo esos colores). Tarjetas: `src/components.py`.
Para implementar una visualización: reemplazar la tarjeta `pendiente(...)` por `card(...)` y agregar su `@callback` en el mismo módulo.

## Juarez – Visualizaciones de exploración + datos  (`src/pages/explorar.py`, `docs/FUENTES.md`)
- [x] V3 Países de origen (top 10 de la región seleccionada). Datos: `data/processed/viajeros_pais_anual.csv` (`src.data.load_paises()`); filtra por años y por `sel-region`.
- [x] V4 Calendario mes × año (mapa de calor, escala `SEQUENTIAL`). Usar `filtrar(...)`.
- [ ] V5 Vía de ingreso por año (barras apiladas). Usar `filtrar(...)`.
- [ ] Req. 3.3: casillas para que el usuario elija qué gráficas ver.
- [ ] Completar `docs/FUENTES.md` (institución que publica la base) y verificar `data/processed/README.md`.

## Nicolle – Modelos  (`src/pages/modelos.py`)
- [x] Controles: serie (`load_predictions()["serie"]`), modelo y métrica (MAE/RMSE).
- [x] V6 Real vs. predicción (observado azul, estimación naranja, sombrear el periodo de prueba).
- [x] V7 Errores del modelo (real − predicción por mes).
- [x] V8 Comparación de los 3 modelos (MAE/RMSE; clic selecciona el modelo). Tabla comparativa (elemento complementario, no cuenta como visualización).
- [x] Textos explicativos y limitaciones (MAPE alto en el periodo de prueba; los modelos son simples; no se construyen modelos nuevos).
- Los 3 modelos y sus métricas ya están exportados en `models/` (generados con `scripts/exportar_datos_lab1.py`).

## Alex – Calidad, documento final y PDF  (`docs/`)
- [ ] Completar el documento de diseño final: 4.2 (explicar el tipo de gráfica de las 8 visualizaciones) y limitaciones; insertar capturas reales.
- [ ] Pruebas de usabilidad y legibilidad: contraste de colores (WebAIM), textos, ejes, leyendas; mensajes cuando una selección no tiene datos.
- [ ] Revisar que todo funcione sin errores y sea interactivo (20 pts de la rúbrica).
- [ ] Exportar el PDF final y verificar apellidos, URL del repo y marcas `[COMPLETAR]`.
