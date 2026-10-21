"""Exporta los datos y resultados del Laboratorio 1 (time-series-lab/) al formato que consume el dashboard.

Reutiliza el código del Lab 1 (NO crea modelos nuevos, como pide el Lab 10). Genera:
  data/processed/viajeros_detalle.csv      fecha, via, tipo_viajero, region, viajeros
  data/processed/viajeros_pais_anual.csv   anio, region, pais, viajeros
  models/predicciones.csv                  serie, modelo, fecha, conjunto, real, prediccion
  models/metricas.csv                      serie, modelo, MAE, RMSE, MAPE, AIC, BIC

Ejecutar (requiere el .xlsx del Lab 1 y las dependencias de time-series-lab/requirements.txt):
    time-series-lab/venv/bin/python scripts/exportar_datos_lab1.py
Los CSV resultantes SÍ se versionan para que el equipo no necesite el Excel.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LAB1 = ROOT / "time-series-lab"
sys.path.insert(0, str(LAB1))

import pandas as pd

from src.data_loader import get_clean_data
from src.models import fit_arima, fit_holt_winters, fit_simple_exp_smoothing
from src.series_builder import build_total_series, build_tipo_viajero_series, build_via_series

TRAIN_RATIO = 0.70  # igual que analysis/03_modelos.py
# Los 3 modelos simples con mejor MAE para la serie total en el Lab 1 (infographic/output/metricas_modelos.csv)
MODELOS = {
    "Suavizamiento exponencial": lambda tr, te: fit_simple_exp_smoothing(tr, te),
    "ARIMA(1,1,1)": lambda tr, te: fit_arima(tr, te, order=(1, 1, 1)),
    "Holt-Winters multiplicativo": lambda tr, te: fit_holt_winters(tr, te, trend="mul", seasonal="mul"),
}


def main() -> None:
    df = get_clean_data()
    (ROOT / "data" / "processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "models").mkdir(exist_ok=True)

    detalle = (df.groupby(["fecha", "via", "tipo_viajero", "region_dos"], as_index=False)["viajeros"].sum()
                 .rename(columns={"region_dos": "region"}))
    detalle["viajeros"] = detalle["viajeros"].round().astype(int)
    detalle.to_csv(ROOT / "data/processed/viajeros_detalle.csv", index=False)

    pais = (df.groupby(["anio", "region_dos", "pais"], as_index=False)["viajeros"].sum()
              .rename(columns={"region_dos": "region"}))
    pais["viajeros"] = pais["viajeros"].round().astype(int)
    pais.to_csv(ROOT / "data/processed/viajeros_pais_anual.csv", index=False)

    series = {"Total viajeros": build_total_series(df)}
    for k, v in build_via_series(df).items():
        series[v.nombre] = v
    for k, v in build_tipo_viajero_series(df).items():
        if k in ("Turista", "Excursionista"):
            series[v.nombre] = v

    pred_rows, met_rows = [], []
    for nombre, info in series.items():
        s = info.serie.asfreq("MS")
        n = int(len(s) * TRAIN_RATIO)
        train, test = s.iloc[:n], s.iloc[n:]
        resultados = {}
        for mname, fit in MODELOS.items():
            try:
                resultados[mname] = fit(train, test)
            except Exception as e:
                print(f"  {nombre} / {mname} falló: {e}")
        if len(resultados) < len(MODELOS):
            # Se omite la serie para comparar siempre los 3 modelos (p. ej. Holt-Winters multiplicativo
            # no admite ceros: Vía Marítima y Excursionista)
            print(f"  -> serie '{nombre}' omitida de la comparación de modelos")
            continue
        for mname, r in resultados.items():
            for f, v in train.items():
                pred_rows.append((nombre, mname, f, "entrenamiento", v, None))
            for f, v in test.items():
                pred_rows.append((nombre, mname, f, "prueba", v, float(r["predicciones"].get(f))))
            m = r["metricas"]
            met_rows.append((nombre, mname, m["MAE"], m["RMSE"], m["MAPE (%)"], m["AIC"], m["BIC"]))

    pd.DataFrame(pred_rows, columns=["serie", "modelo", "fecha", "conjunto", "real", "prediccion"]) \
        .round({"real": 1, "prediccion": 1}) \
        .to_csv(ROOT / "models/predicciones.csv", index=False, date_format="%Y-%m-%d")
    pd.DataFrame(met_rows, columns=["serie", "modelo", "MAE", "RMSE", "MAPE", "AIC", "BIC"]) \
        .to_csv(ROOT / "models/metricas.csv", index=False)
    print("Listo: data/processed/*.csv y models/*.csv")


if __name__ == "__main__":
    main()
