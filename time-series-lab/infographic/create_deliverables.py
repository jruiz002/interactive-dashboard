"""Create the executive tourism infographic from the laboratory dataset."""

from __future__ import annotations

import json
import sys
import warnings
from pathlib import Path

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import adfuller

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = Path(__file__).resolve().parent / "output"
sys.path.insert(0, str(PROJECT_ROOT))
warnings.filterwarnings("ignore")

from src.data_loader import get_clean_data
from src.metrics import compute_mae, compute_rmse
from src.series_builder import (
    build_tipo_viajero_series,
    build_total_series,
    build_via_series,
)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Azul petróleo = confianza; verde = recuperación; arena = contexto;
# coral = alerta. El fondo cálido baja la fatiga visual en pantalla.
NAVY = "#123047"
TEAL = "#167C80"
SAND = "#D8B36A"
CORAL = "#DE6B48"
INK = "#17212B"
MUTED = "#596773"
BACKGROUND = "#F7F5F0"
TRAIN_RATIO = 0.70
SEASONAL_PERIODS = 12


def compact_number(value: float) -> str:
    """Display traveller counts compactly in the KPI cards."""
    return f"{value / 1e6:.1f} M" if abs(value) >= 1e6 else f"{value / 1e3:.0f} mil"


def metric_row(
    actual: pd.Series,
    forecast: pd.Series,
    aic: float | None = None,
    bic: float | None = None,
) -> dict[str, float | None]:
    return {
        "MAE": compute_mae(actual, forecast),
        "RMSE": compute_rmse(actual, forecast),
        "AIC": aic,
        "BIC": bic,
    }


def residual_interval(
    forecast: pd.Series, fitted: pd.Series, observed: pd.Series
) -> tuple[pd.Series, pd.Series]:
    """Build a residual-based 95% interval for non-ARIMA forecasts."""
    margin = 1.96 * np.std(observed - fitted, ddof=1)
    return forecast - margin, forecast + margin


def add_result(
    results: list[dict[str, object]],
    name: str,
    forecast: pd.Series,
    actual: pd.Series,
    lower: pd.Series,
    upper: pd.Series,
    aic: float | None = None,
    bic: float | None = None,
) -> None:
    results.append(
        {
            "name": name,
            "forecast": forecast,
            "metrics": metric_row(actual, forecast, aic, bic),
            "lower": lower,
            "upper": upper,
        }
    )


def evaluate_models(
    series: pd.Series,
) -> tuple[pd.Series, pd.Series, list[dict[str, object]]]:
    """Evaluate the laboratory model family on a 70/30 chronological split."""
    split_at = int(len(series) * TRAIN_RATIO)
    train, test = series.iloc[:split_at], series.iloc[split_at:]
    results: list[dict[str, object]] = []

    arima_specs = [
        ("ARIMA(1,1,1)", (1, 1, 1), (0, 0, 0, 0)),
        ("SARIMA(1,1,1)(1,1,1)[12]", (1, 1, 1), (1, 1, 1, 12)),
    ]
    for name, order, seasonal_order in arima_specs:
        fit = SARIMAX(
            train,
            order=order,
            seasonal_order=seasonal_order,
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)
        forecast_object = fit.get_forecast(len(test))
        forecast = pd.Series(forecast_object.predicted_mean.values, index=test.index)
        interval = forecast_object.conf_int(alpha=0.05)
        add_result(
            results,
            name,
            forecast,
            test,
            pd.Series(interval.iloc[:, 0].values, index=test.index),
            pd.Series(interval.iloc[:, 1].values, index=test.index),
            fit.aic,
            fit.bic,
        )

    for name, trend, seasonal in [
        ("Holt-Winters aditivo", "add", "add"),
        ("Holt-Winters multiplicativo", "mul", "mul"),
    ]:
        fit = ExponentialSmoothing(
            train,
            trend=trend,
            seasonal=seasonal,
            seasonal_periods=SEASONAL_PERIODS,
        ).fit(optimized=True)
        forecast = pd.Series(fit.forecast(len(test)).values, index=test.index)
        lower, upper = residual_interval(forecast, fit.fittedvalues, train)
        add_result(results, name, forecast, test, lower, upper, fit.aic, fit.bic)

    fit = ExponentialSmoothing(train).fit(optimized=True)
    forecast = pd.Series(fit.forecast(len(test)).values, index=test.index)
    lower, upper = residual_interval(forecast, fit.fittedvalues, train)
    add_result(
        results,
        "Suavizamiento exponencial",
        forecast,
        test,
        lower,
        upper,
        fit.aic,
        fit.bic,
    )

    naive = pd.Series(
        [train.iloc[-SEASONAL_PERIODS + i % SEASONAL_PERIODS] for i in range(len(test))],
        index=test.index,
    )
    add_result(results, "Naïve estacional", naive, test, naive * 0.80, naive * 1.20)
    results.sort(key=lambda result: result["metrics"]["MAE"])
    return train, test, results


def compare_series(series_by_name: dict[str, pd.Series]) -> pd.DataFrame:
    """Calculate seasonality, trend, volatility, and COVID impact by series."""
    rows = []
    for name, series in series_by_name.items():
        try:
            decomposition = seasonal_decompose(
                series, model="additive", period=SEASONAL_PERIODS
            )
            seasonal = decomposition.seasonal.dropna()
            residual = decomposition.resid.dropna()
            strength = np.var(seasonal) / (np.var(seasonal) + np.var(residual))
            trend = decomposition.trend.dropna()
            slope = np.polyfit(np.arange(len(trend)), trend, 1)[0]
        except (ValueError, np.linalg.LinAlgError):
            strength, slope = np.nan, np.nan

        annual = series.resample("YS").sum()
        covid_drop = (
            annual.get(pd.Timestamp("2020-01-01"), np.nan)
            / annual.get(pd.Timestamp("2019-01-01"), np.nan)
            - 1
        ) * 100
        rows.append(
            {
                "serie": name,
                "estacionalidad": strength,
                "tendencia": slope,
                "volatilidad": series.std() / series.mean(),
                "caida_covid": covid_drop,
            }
        )
    return pd.DataFrame(rows)


def panel(figure: plt.Figure, position: list[float], title: str) -> plt.Axes:
    """Create a chart panel that follows the visual system."""
    axis = figure.add_axes(position, facecolor="white")
    for spine in axis.spines.values():
        spine.set_visible(False)
    axis.set_title(title, loc="left", fontsize=10.5, fontweight="bold", color=INK, pad=7)
    axis.tick_params(labelsize=7, colors=MUTED)
    axis.grid(axis="y", color="#DDE2E2", lw=0.55)
    axis.set_axisbelow(True)
    return axis


def kpi_card(
    canvas: plt.Axes,
    x: float,
    label: str,
    value: str,
    detail: str,
    accent: str,
) -> None:
    """Draw a single KPI card in its reserved header area."""
    y, width, height = 0.790, 0.27, 0.076
    canvas.add_patch(
        FancyBboxPatch(
            (x, y),
            width,
            height,
            boxstyle="round,pad=0.012,rounding_size=0.018",
            ec="none",
            fc="white",
            transform=canvas.transAxes,
        )
    )
    canvas.add_patch(
        FancyBboxPatch(
            (x + 0.025, y + height - 0.020),
            0.060,
            0.006,
            boxstyle="round,pad=0,rounding_size=.004",
            ec="none",
            fc=accent,
            transform=canvas.transAxes,
        )
    )
    canvas.text(x + 0.025, y + height - 0.022, label, transform=canvas.transAxes,
                fontsize=7.2, color=MUTED, weight="bold", va="top")
    canvas.text(x + 0.025, y + 0.024, value, transform=canvas.transAxes,
                fontsize=17, color=INK, weight="bold", va="bottom")
    canvas.text(x + 0.025, y + 0.008, detail, transform=canvas.transAxes,
                fontsize=7.1, color=MUTED, va="bottom")


def draw_history(figure: plt.Figure, total: pd.Series) -> None:
    """Draw the historical trajectory with the COVID and recovery annotations."""
    # The label sits below the cards with a dedicated gap; title sits within the panel.
    figure.text(0.06, 0.755, "1 · PANORAMA HISTÓRICO", fontsize=10, color=TEAL, weight="bold")
    axis = panel(
        figure,
        [0.06, 0.615, 0.88, 0.11],
        "El flujo se interrumpe en 2020, se recompone desde 2022 y mantiene una pauta mensual visible",
    )
    axis.title.set_y(0.94)
    axis.plot(total.index, total.values / 1e3, color=NAVY, lw=1.45)
    axis.axvspan(
        pd.Timestamp("2020-03-01"), pd.Timestamp("2021-12-01"), color=CORAL, alpha=0.16
    )
    axis.annotate(
        "COVID-19\ncierre y caída abrupta",
        (pd.Timestamp("2020-04-01"), total.loc["2020-04-01"] / 1e3),
        xytext=(pd.Timestamp("2016-10-01"), 80),
        arrowprops={"arrowstyle": "-", "color": CORAL},
        fontsize=7,
        color=CORAL,
    )
    axis.annotate(
        "Recuperación\n2022–2026",
        (pd.Timestamp("2023-01-01"), total.loc["2023-01-01"] / 1e3),
        xytext=(pd.Timestamp("2023-10-01"), 425),
        arrowprops={"arrowstyle": "-", "color": TEAL},
        fontsize=7,
        color=TEAL,
    )
    peak_date = total.loc[:"2019-12-01"].idxmax()
    axis.annotate(
        f"Récord previo: {total.loc[peak_date] / 1e3:.0f} mil\n(dic {peak_date:%Y})",
        (peak_date, total.loc[peak_date] / 1e3),
        xytext=(pd.Timestamp("2016-01-01"), 400),
        arrowprops={"arrowstyle": "-", "color": NAVY},
        fontsize=7,
        color=NAVY,
    )
    axis.set_ylabel("miles de viajeros")
    axis.xaxis.set_major_locator(mdates.YearLocator(2))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def draw_seasonality(figure: plt.Figure, total: pd.Series, via: dict[str, pd.Series], peak_month: int) -> None:
    figure.text(0.06, 0.595, "2 · ESTACIONALIDAD, VÍAS Y MERCADOS", fontsize=10, color=TEAL, weight="bold")
    month_names = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
    monthly_average = total.groupby(total.index.month).mean()
    axis = panel(figure, [0.06, 0.475, 0.42, 0.105], "La demanda tiene meses recurrentes de mayor intensidad")
    colors = [SAND] * 12
    colors[peak_month - 1] = TEAL
    axis.bar(range(1, 13), monthly_average.values / 1e3, color=colors, width=0.72)
    axis.set_xticks(range(1, 13), month_names, fontsize=6.8)
    axis.set_ylabel("miles / mes")
    axis.text(peak_month + 0.4, monthly_average.iloc[peak_month - 1] / 1e3 + 5,
              f"pico: {month_names[peak_month - 1]}\nAguinaldo + fiestas", ha="right", fontsize=7, color=TEAL, weight="bold")
    # Fechas que marcan pauta cada año: Semana Santa, vacaciones/bono 14, aguinaldo.
    for month, label in [(3.5, "Semana\nSanta"), (7, "Vacaciones\n+ Bono 14")]:
        height = monthly_average.loc[int(month)] / 1e3 if month == int(month) else monthly_average.loc[[3, 4]].max() / 1e3
        axis.text(month, height + 22, label, ha="center", fontsize=6, color=INK, linespacing=0.95)
    axis.set_ylim(0, monthly_average.max() / 1e3 * 1.25)

    axis = panel(figure, [0.52, 0.475, 0.42, 0.105], "Vías de ingreso: el peso operativo no es uniforme")
    route_totals = pd.Series({name: series.sum() for name, series in via.items()}).sort_values()
    axis.barh([name.replace("Vía ", "") for name in route_totals.index], route_totals.values / 1e6, color=[SAND, TEAL, NAVY][:len(route_totals)])
    for row, value in enumerate(route_totals.values):
        axis.text(value / 1e6 + 0.15, row, f"{value / route_totals.sum():.0%}", va="center", fontsize=8, color=INK)
    axis.set_xlabel("millones acumulados")


def draw_comparison(figure: plt.Figure, comparison: pd.DataFrame) -> None:
    figure.text(0.06, 0.448, "Cuadrante comparativo del laboratorio · la serie máxima en cada criterio resume dónde priorizar el análisis y la gestión.", fontsize=7.8, color=MUTED)
    axis = panel(figure, [0.06, 0.315, 0.88, 0.115], "Qué serie destaca en cada dimensión")
    axis.axis("off")
    leaders = [
        ("Mayor estacionalidad", comparison.loc[comparison.estacionalidad.idxmax()], "fuerza estacional {row.estacionalidad:.2f} (0–1)", TEAL),
        ("Mayor crecimiento", comparison.loc[comparison.tendencia.idxmax()], "+{row.tendencia:,.0f} viajeros/mes de tendencia", TEAL),
        ("Mayor volatilidad", comparison.loc[comparison.volatilidad.idxmax()], "CV {row.volatilidad:.2f}\n(incluye cambio de definición 2023)", TEAL),
        ("Más golpeada por COVID", comparison.loc[comparison.caida_covid.idxmin()], "{row.caida_covid:.0f}% en 2020 vs. 2019", CORAL),
    ]
    for index, (label, row, template, color) in enumerate(leaders):
        x = 0.01 + index * 0.247
        axis.add_patch(FancyBboxPatch((x, 0.18), 0.225, 0.62, boxstyle="round,pad=.012,rounding_size=.02", fc="#F4F6F4", ec="none", transform=axis.transAxes))
        axis.text(x + 0.014, 0.68, label, transform=axis.transAxes, fontsize=7.5, color=MUTED, weight="bold")
        axis.text(x + 0.014, 0.47, row.serie.replace("Tipo ", ""), transform=axis.transAxes, fontsize=9, color=INK, weight="bold")
        axis.text(x + 0.014, 0.30, template.format(row=row), transform=axis.transAxes, fontsize=8, color=color)


def draw_models(figure: plt.Figure, train: pd.Series, test: pd.Series, models: list[dict[str, object]]) -> None:
    figure.text(0.06, 0.288, "3 · MODELOS Y PRONÓSTICO", fontsize=10, color=TEAL, weight="bold")
    table_axis = panel(figure, [0.06, 0.16, 0.42, 0.11], "Prueba fuera de muestra · menor error es mejor")
    table_axis.axis("off")
    for x, label in [(0.01, "MODELO"), (0.63, "MAE"), (0.82, "RMSE")]:
        table_axis.text(x, 0.84, label, transform=table_axis.transAxes, fontsize=7, color=MUTED, weight="bold")
    for index, result in enumerate(models[:5]):
        y = 0.66 - index * 0.15
        color = TEAL if index == 0 else INK
        metric = result["metrics"]
        table_axis.text(0.01, y, result["name"], transform=table_axis.transAxes, fontsize=7.2, color=color, weight="bold" if index == 0 else "normal")
        table_axis.text(0.63, y, f"{metric['MAE'] / 1e3:.1f}k", transform=table_axis.transAxes, fontsize=7.2, color=color)
        table_axis.text(0.82, y, f"{metric['RMSE'] / 1e3:.1f}k", transform=table_axis.transAxes, fontsize=7.2, color=color)

    winner = models[0]
    axis = panel(figure, [0.52, 0.16, 0.42, 0.11], f"Estimación: {winner['name']} (intervalo 95%)")
    axis.plot(train.iloc[-24:].index, train.iloc[-24:].values / 1e3, color="#AAB3B9", lw=1, label="entrenamiento")
    axis.plot(test.index, test.values / 1e3, color=INK, lw=1.2, label="real")
    axis.plot(test.index, winner["forecast"].values / 1e3, color=TEAL, lw=1.5, label="estimación")
    # Los viajeros no pueden ser negativos: el intervalo se recorta en cero.
    axis.fill_between(test.index, winner["lower"].clip(lower=0).values / 1e3, winner["upper"].values / 1e3, color=TEAL, alpha=0.18)
    axis.text(test.index[-1], winner["forecast"].iloc[-1] / 1e3 + 8, "Estimación (IC 95%)", ha="right", fontsize=6.5, color=TEAL, weight="bold")
    axis.text(test.index[-1], test.iloc[-1] / 1e3 + 25, "Real", ha="right", fontsize=6.5, color=INK, weight="bold")
    axis.text(train.index[-24], 20, "Entrenamiento", fontsize=6, color="#7D878E")
    axis.text(0.0, -0.30, "Nota: el entrenamiento termina en plena pandemia; por eso la estimación\nqueda por debajo de la recuperación real.", transform=axis.transAxes, fontsize=6, color=MUTED)
    axis.set_ylabel("miles")
    axis.xaxis.set_major_locator(mdates.YearLocator(2))
    axis.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))


def draw_recommendations(figure: plt.Figure, adf_p_value: float) -> None:
    figure.text(0.06, 0.134, "4 · DECISIONES RECOMENDADAS PARA INGUAT", fontsize=10, color=TEAL, weight="bold")
    recommendations = [
        "Reforzar personal en fronteras y aeropuerto en diciembre (mes pico) y lanzar campañas para septiembre y mayo, los meses más débiles.",
        "Priorizar la vía terrestre (61% del flujo y mayor crecimiento) con agilización fronteriza; la aérea, la más estacional, con ofertas fuera de temporada.",
        "Diseñar un plan de contingencia y diversificación: el COVID redujo 74% el flujo y el excursionista cayó 76%, el segmento más vulnerable.",
        "Reentrenar el pronóstico cada trimestre con datos post-pandemia y alertar cuando el dato real salga del intervalo de estimación.",
    ]
    for index, recommendation in enumerate(recommendations):
        y = 0.108 - index * 0.023
        figure.text(0.07, y, f"{index + 1:02d}", fontsize=9, color=CORAL, weight="bold")
        figure.text(0.10, y, recommendation, fontsize=7.8, color=INK, wrap=True)
    figure.text(0.06, 0.012, "Fuente: Base de Migración 2009–junio 2026, INGUAT/IGM. Serie principal: Turista + Excursionista (criterio de comparabilidad 2009–2026).", fontsize=6.5, color=MUTED)
    figure.text(0.06, 0.003, f"Ficha técnica: datos mensuales; partición entrenamiento/prueba 70/30; ADF p={adf_p_value:.3f}. Elaborado por: José Gerardo Ruiz García (23719) · Gerardo André Fernández Cruz (23763) · Dilary Sarahí Cruz López (231010).", fontsize=6.5, color=MUTED)


def write_evidence(comparison: pd.DataFrame, models: list[dict[str, object]], summary: dict[str, object]) -> None:
    model_rows = [{"modelo": model["name"], **model["metrics"]} for model in models]
    pd.DataFrame(model_rows).to_csv(OUTPUT_DIR / "metricas_modelos.csv", index=False, encoding="utf-8-sig")
    comparison.to_csv(OUTPUT_DIR / "comparativo_series.csv", index=False, encoding="utf-8-sig")
    (OUTPUT_DIR / "resumen_evidencia.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


def generate() -> dict[str, object]:
    """Calculate evidence, render the page, and save PNG/PDF deliverables."""
    data = get_clean_data()
    total = build_total_series(data).serie
    via = {f"Vía {name}": item.serie for name, item in build_via_series(data).items()}
    traveller_type = {f"Tipo {name}": item.serie for name, item in build_tipo_viajero_series(data).items()}
    comparison = compare_series({"Total viajeros": total, **via, **traveller_type})
    train, test, models = evaluate_models(total)

    annual = total.resample("YS").sum()
    current_year = total[total.index.year == 2026].sum()
    reference_period = total[(total.index.year == 2019) & (total.index.month <= 6)].sum()
    peak_month = int(total.groupby(total.index.month).mean().idxmax())
    covid_drop = (annual.loc["2020-01-01"] / annual.loc["2019-01-01"] - 1) * 100
    adf_p_value = float(adfuller(total.dropna())[1])
    winner = models[0]
    summary = {
        "periodo": f"{total.index.min():%Y-%m} a {total.index.max():%Y-%m}",
        "total_acumulado": float(total.sum()),
        "modelo_ganador": winner["name"],
        "metricas_ganador": winner["metrics"],
        "adf_p_value": adf_p_value,
        "estacionalidad_pico_mes": peak_month,
    }
    write_evidence(comparison, models, summary)

    figure = plt.figure(figsize=(11, 17), facecolor=BACKGROUND)
    canvas = figure.add_axes([0, 0, 1, 1])
    canvas.axis("off")
    figure.text(0.06, 0.970, "17 AÑOS DE TURISMO INTERNACIONAL", fontsize=9, color=TEAL, weight="bold")
    figure.text(0.06, 0.934, "Guatemala: resiliencia turística\ny una recuperación que exige anticipación", fontsize=21, color=INK, weight="bold", linespacing=1.08)
    figure.text(0.06, 0.894, "Flujos mensuales de turistas y excursionistas · enero 2009–junio 2026 · lectura ejecutiva para INGUAT", fontsize=8.5, color=MUTED)
    kpi_card(canvas, 0.06, "VIAJEROS ACUMULADOS", compact_number(total.sum()), "Serie comparable: turistas + excursionistas", TEAL)
    kpi_card(canvas, 0.365, "CHOQUE COVID-19", f"{covid_drop:.0f}%", "Variación del total anual 2020 vs. 2019", CORAL)
    kpi_card(canvas, 0.67, "2026 (ENE–JUN)", compact_number(current_year), f"{(current_year / reference_period - 1) * 100:+.0f}% frente a ene–jun 2019", SAND)
    draw_history(figure, total)
    draw_seasonality(figure, total, via, peak_month)
    draw_comparison(figure, comparison)
    draw_models(figure, train, test, models)
    draw_recommendations(figure, adf_p_value)

    figure.savefig(OUTPUT_DIR / "infografia_turismo_guatemala.png", dpi=180, bbox_inches=None, facecolor=BACKGROUND)
    figure.savefig(OUTPUT_DIR / "infografia_turismo_guatemala_A3_vertical.pdf", bbox_inches=None, facecolor=BACKGROUND)
    plt.close(figure)
    return summary


if __name__ == "__main__":
    print(json.dumps(generate(), ensure_ascii=False, indent=2))
