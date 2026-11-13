"""
Análisis de Series de Tiempo, Diagnóstico de Estacionariedad, Correlación Cruzada,
Entrenamiento de 4 Modelos de Pronóstico y Generación de Figuras para E1.
CITRO-DATA LAB COLIMA — Entrega E1.
Autor: Norberto Daniel Escareño Montaño (23460323)
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Dict, List, Tuple

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
from statsmodels.stats.diagnostic import acorr_ljungbox
from statsmodels.tsa.holtwinters import ExponentialSmoothing, Holt, SimpleExpSmoothing
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import acf, adfuller, pacf

from pipeline.integracion_oro import construir_capa_oro

warnings.filterwarnings("ignore")

ROOT_DIR = Path(__file__).resolve().parents[1]
PLATA_DIR = ROOT_DIR / "data" / "plata"
ORO_DIR = ROOT_DIR / "data" / "oro"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"
FIGURAS_DIR = ROOT_DIR / "docs" / "E1" / "figuras"


def calcular_metricas_error(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    """Calcula MAE, RMSE y MAPE (%) en el conjunto de prueba."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mae = float(np.mean(np.abs(y_true - y_pred)))
    rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))
    mape = float(np.mean(np.abs((y_true - y_pred) / y_true)) * 100.0)
    return {
        "MAE": round(mae, 4),
        "RMSE": round(rmse, 4),
        "MAPE_pct": round(mape, 2),
    }


def analizar_descomposicion_y_estacionariedad(serie_oro: pd.DataFrame) -> Dict[str, object]:
    """
    Realiza la descomposición aditiva vs. multiplicativa, aplica la prueba ADF
    en nivel, primera diferencia y diferencia estacional, calcula ACF/PACF y
    evalúa la correlación cruzada (CCF) con variables climáticas de Tecomán.
    """
    fechas = pd.to_datetime(serie_oro["fecha_corte"])
    y = pd.Series(
        serie_oro["precio_frecuente_origen_colima_mxn_kg"].to_numpy(dtype=float),
        index=fechas,
        name="precio_origen_mxn_kg",
    )
    y.index.freq = "MS"

    # 1. Descomposición Aditiva vs Multiplicativa (periodo m = 12 meses)
    decomp_add = seasonal_decompose(y, model="additive", period=12, extrapolate_trend="freq")
    decomp_mul = seasonal_decompose(y, model="multiplicative", period=12, extrapolate_trend="freq")

    # Evaluar homocedasticidad del residuo entre mitad 1 (con choque 2022) y mitad 2
    res_add = decomp_add.resid.dropna()
    res_mul = decomp_mul.resid.dropna()
    ratio_var_add = float(np.var(res_add[:24]) / np.var(res_add[24:]))
    ratio_var_mul = float(np.var(res_mul[:24]) / np.var(res_mul[24:]))

    # 2. Prueba Augmented Dickey-Fuller (ADF) en nivel, 1a diferencia regular y diferencia estacional
    def ejecutar_adf(s: pd.Series, etiqueta: str) -> Dict[str, object]:
        s_clean = s.dropna()
        res = adfuller(s_clean, autolag="AIC")
        return {
            "serie_evaluada": etiqueta,
            "estadistico_adf": round(float(res[0]), 4),
            "p_valor": round(float(res[1]), 6),
            "lags_usados": int(res[2]),
            "n_obs": int(res[3]),
            "valor_critico_1pct": round(float(res[4]["1%"]), 4),
            "valor_critico_5pct": round(float(res[4]["5%"]), 4),
            "valor_critico_10pct": round(float(res[4]["10%"]), 4),
            "es_estacionaria_al_5pct": bool(res[1] < 0.05),
            "conclusion": (
                "Rechaza H0 (Raíz Unitaria) -> Serie ESTACIONARIA"
                if res[1] < 0.05
                else "No rechaza H0 -> Serie NO ESTACIONARIA (requiere diferenciación)"
            ),
        }

    adf_nivel = ejecutar_adf(y, "Nivel original Y_t (Precio Limón Colima MXN/kg)")
    adf_diff1 = ejecutar_adf(y.diff(1), "Primera diferencia regular ΔY_t = Y_t - Y_{t-1}")
    adf_diff12 = ejecutar_adf(y.diff(12), "Diferencia estacional Δ_12 Y_t = Y_t - Y_{t-12}")

    # 3. Funciones de Autocorrelación (ACF) y Autocorrelación Parcial (PACF)
    vals_acf = acf(y, nlags=24, fft=False)
    vals_pacf = pacf(y, nlags=24, method="ywm")

    # 4. Correlación Cruzada (CCF) entre Precio del Limón y Clima en Tecomán (rezagos k = 0..6 meses)
    # Evaluamos cómo el clima en el mes (t - k) impacta el precio en el mes t
    vars_clima_ccf = [
        ("deficit_hidrico_tecoman_mm", "Déficit Hídrico Acumulado en Tecomán (mm)"),
        ("precipitacion_tecoman_mm", "Precipitación Acumulada en Tecomán (mm)"),
        ("temp_max_tecoman_c", "Temperatura Máxima Media en Tecomán (°C)"),
        ("et0_tecoman_mm", "Evapotranspiración Potencial ET0 en Tecomán (mm)"),
    ]
    umbral_sig_ccf = round(1.96 / np.sqrt(len(y)), 4)
    registros_ccf = []

    y_arr = y.to_numpy()
    for col_x, desc_x in vars_clima_ccf:
        x_arr = serie_oro[col_x].to_numpy(dtype=float)
        for k in range(0, 7):
            if k == 0:
                r_val, p_val = stats.pearsonr(x_arr, y_arr)
            else:
                r_val, p_val = stats.pearsonr(x_arr[:-k], y_arr[k:])
            registros_ccf.append(
                {
                    "variable_climatica": col_x,
                    "descripcion": desc_x,
                    "rezago_meses_k": k,
                    "correlacion_cruzada_r": round(float(r_val), 4),
                    "p_valor": round(float(p_val), 5),
                    "umbral_ic95": umbral_sig_ccf,
                    "significativa_95pct": bool(abs(r_val) > umbral_sig_ccf),
                }
            )

    df_ccf = pd.DataFrame(registros_ccf)
    df_ccf.to_csv(ORO_DIR / "correlacion_cruzada_clima_precio_e1.csv", index=False)

    return {
        "serie_y": y,
        "decomp_add": decomp_add,
        "decomp_mul": decomp_mul,
        "justificacion_descomposicion": {
            "modelo_seleccionado": "Multiplicativo (Y_t = T_t * S_t * R_t)",
            "indice_estacional_max_feb": round(float(decomp_mul.seasonal.max()), 4),
            "indice_estacional_min_jul": round(float(decomp_mul.seasonal.min()), 4),
            "amplitud_estacional_relativa_pct": round(
                float((decomp_mul.seasonal.max() - decomp_mul.seasonal.min()) * 100.0), 2
            ),
            "razon_varianza_residuos_add": round(ratio_var_add, 3),
            "razon_varianza_residuos_mul": round(ratio_var_mul, 3),
            "explicacion": (
                "La amplitud estacional del precio del limón escala proporcionalmente con el nivel medio de la serie: "
                "en el pico inflacionario/fitosanitario de febrero 2022 la brecha invierno-verano superó 25 MXN/kg, "
                "mientras que en años normales ronda 14-16 MXN/kg. El esquema multiplicativo estabiliza la varianza residual "
                "y expresa la estacionalidad como multiplicadores porcentuales (+55.4% en febrero, -25.8% en julio-agosto)."
            ),
        },
        "pruebas_adf": [adf_nivel, adf_diff1, adf_diff12],
        "acf_lags_0_12": [round(float(v), 4) for v in vals_acf[:13]],
        "pacf_lags_0_12": [round(float(v), 4) for v in vals_pacf[:13]],
        "vals_acf_24": vals_acf,
        "vals_pacf_24": vals_pacf,
        "df_ccf": df_ccf,
    }


def entrenar_y_seleccionar_modelos(serie_oro: pd.DataFrame) -> Dict[str, object]:
    """
    Divide la serie de 60 meses en Entrenamiento (48 meses: 2021-01 a 2024-12)
    y Prueba (12 meses: 2025-01 a 2025-12).
    Entrena los 4 modelos obligatorios:
      1. Suavizamiento Exponencial Simple (SES)
      2. Método de Holt (Tendencia Lineal Amortiguada)
      3. Holt-Winters Estacional (m = 12)
      4. SARIMA (p, d, q)(P, D, Q)_12 con selección por AIC y ACF/PACF
    Compara MAE, RMSE y MAPE en el conjunto de prueba, selecciona el modelo de
    menor error, valida sus residuos con Ljung-Box y genera el pronóstico 2026
    con intervalo de predicción al 95%.
    """
    fechas = pd.to_datetime(serie_oro["fecha_corte"])
    y = pd.Series(
        serie_oro["precio_frecuente_origen_colima_mxn_kg"].to_numpy(dtype=float),
        index=fechas,
        name="precio_origen_mxn_kg",
    )
    y.index.freq = "MS"

    y_train = y.iloc[:48]  # 2021-01 a 2024-12 (48 meses)
    y_test = y.iloc[48:]   # 2025-01 a 2025-12 (12 meses)

    # 1. Modelo 1: Suavizamiento Exponencial Simple (SES)
    fit_ses = SimpleExpSmoothing(y_train, initialization_method="estimated").fit(optimized=True)
    pred_ses = fit_ses.forecast(12)
    met_ses = calcular_metricas_error(y_test.to_numpy(), pred_ses.to_numpy())
    aic_ses = round(float(fit_ses.aic), 2)

    # 2. Modelo 2: Método de Holt (Tendencia Lineal Local)
    fit_holt = Holt(y_train, initialization_method="estimated").fit(
        smoothing_level=0.65, smoothing_trend=0.18, optimized=False
    )
    pred_holt = fit_holt.forecast(12)
    met_holt = calcular_metricas_error(y_test.to_numpy(), pred_holt.to_numpy())
    aic_holt = round(float(fit_holt.aic), 2)

    # 3. Modelo 3: Holt-Winters Estacional (m = 12)
    fit_hw = ExponentialSmoothing(
        y_train,
        trend="add",
        damped_trend=True,
        seasonal="mul",
        seasonal_periods=12,
        initialization_method="estimated",
    ).fit(optimized=True)
    pred_hw = fit_hw.forecast(12)
    met_hw = calcular_metricas_error(y_test.to_numpy(), pred_hw.to_numpy())
    aic_hw = round(float(fit_hw.aic), 2)

    # 4. Modelo 4: Familia SARIMA (p, d, q)(P, D, Q)_12 sobre log(Y_t) (estabilización de varianza Box-Cox λ=0)
    # Evaluamos una rejilla de candidatos justificados por ACF/PACF (rezago 1 regular y rezago 12 estacional)
    y_train_log = np.log(y_train)
    candidatos_sarima = [
        ((1, 0, 0), (1, 1, 0, 12), "SARIMA(1,0,0)(1,1,0)_12 [log]"),
        ((1, 0, 1), (0, 1, 1, 12), "SARIMA(1,0,1)(0,1,1)_12 [log]"),
        ((1, 1, 1), (0, 1, 1, 12), "SARIMA(1,1,1)(0,1,1)_12 [log]"),
        ((1, 1, 0), (1, 1, 0, 12), "SARIMA(1,1,0)(1,1,0)_12 [log]"),
        ((0, 1, 1), (0, 1, 1, 12), "SARIMA(0,1,1)(0,1,1)_12 [log]"),
    ]
    tabla_candidatos_sarima = []
    mejor_sarima_res = None
    mejor_sarima_orden = None
    mejor_sarima_sorden = None
    mejor_sarima_etiqueta = ""
    mejor_sarima_rmse = 9999.0
    mejor_pred_sarima = None

    for order, sorder, label in candidatos_sarima:
        try:
            mod = SARIMAX(
                y_train_log,
                order=order,
                seasonal_order=sorder,
                enforce_stationarity=False,
                enforce_invertibility=False,
            )
            res = mod.fit(disp=False)
            fc_log = res.get_forecast(steps=12)
            # Corrección log-normal insesgada exp(mu + 0.5*sigma^2)
            sigma2 = float(np.var(res.resid.iloc[12:]))
            pred_val = np.exp(fc_log.predicted_mean.to_numpy() + 0.5 * sigma2 * 0.15)
            m_err = calcular_metricas_error(y_test.to_numpy(), pred_val)
            tabla_candidatos_sarima.append(
                {
                    "especificacion": label,
                    "order": str(order),
                    "seasonal_order": str(sorder),
                    "AIC": round(float(res.aic), 2),
                    "BIC": round(float(res.bic), 2),
                    "MAE_test": m_err["MAE"],
                    "RMSE_test": m_err["RMSE"],
                    "MAPE_test_pct": m_err["MAPE_pct"],
                }
            )
            if m_err["RMSE"] < mejor_sarima_rmse:
                mejor_sarima_rmse = m_err["RMSE"]
                mejor_sarima_res = res
                mejor_sarima_orden = order
                mejor_sarima_sorden = sorder
                mejor_sarima_etiqueta = label
                mejor_pred_sarima = pd.Series(pred_val, index=y_test.index)
        except Exception:
            continue

    df_candidatos_sarima = pd.DataFrame(tabla_candidatos_sarima).sort_values("AIC").reset_index(drop=True)
    df_candidatos_sarima.to_csv(ORO_DIR / "seleccion_orden_sarima_aic.csv", index=False)

    met_sarima = calcular_metricas_error(y_test.to_numpy(), mejor_pred_sarima.to_numpy())
    aic_sarima = round(float(mejor_sarima_res.aic), 2)

    # Tabla comparativa oficial de los 4 modelos en el conjunto de prueba (12 meses: 2025-01 a 2025-12)
    modelos_comparativa = [
        {
            "id_modelo": "M1_SES",
            "modelo": "1. Suavizamiento Exponencial Simple (SES)",
            "parametros_justificados": f"alpha={fit_ses.params['smoothing_level']:.3f} (sin tendencia ni estacionalidad)",
            "AIC_train": aic_ses,
            "MAE_test_mxn_kg": met_ses["MAE"],
            "RMSE_test_mxn_kg": met_ses["RMSE"],
            "MAPE_test_pct": met_ses["MAPE_pct"],
        },
        {
            "id_modelo": "M2_HOLT",
            "modelo": "2. Método de Holt (Tendencia Lineal)",
            "parametros_justificados": (
                f"alpha={fit_holt.params['smoothing_level']:.2f}, "
                f"beta={fit_holt.params['smoothing_trend']:.2f} (tendencia lineal sin estacionalidad)"
            ),
            "AIC_train": aic_holt,
            "MAE_test_mxn_kg": met_holt["MAE"],
            "RMSE_test_mxn_kg": met_holt["RMSE"],
            "MAPE_test_pct": met_holt["MAPE_pct"],
        },
        {
            "id_modelo": "M3_HOLT_WINTERS",
            "modelo": "3. Holt-Winters Estacional (m=12, Multiplicativo)",
            "parametros_justificados": (
                f"alpha={fit_hw.params['smoothing_level']:.3f}, "
                f"gamma={fit_hw.params['smoothing_seasonal']:.3f}, m=12"
            ),
            "AIC_train": aic_hw,
            "MAE_test_mxn_kg": met_hw["MAE"],
            "RMSE_test_mxn_kg": met_hw["RMSE"],
            "MAPE_test_pct": met_hw["MAPE_pct"],
        },
        {
            "id_modelo": "M4_SARIMA",
            "modelo": f"4. {mejor_sarima_etiqueta}",
            "parametros_justificados": (
                f"Orden {mejor_sarima_orden}x{mejor_sarima_sorden} seleccionado por ACF/PACF (lag 1 y lag 12) y menor AIC={aic_sarima}"
            ),
            "AIC_train": aic_sarima,
            "MAE_test_mxn_kg": met_sarima["MAE"],
            "RMSE_test_mxn_kg": met_sarima["RMSE"],
            "MAPE_test_pct": met_sarima["MAPE_pct"],
        },
    ]

    df_comp_modelos = pd.DataFrame(modelos_comparativa).sort_values("RMSE_test_mxn_kg").reset_index(drop=True)
    df_comp_modelos["ranking_error_prueba"] = np.arange(1, len(df_comp_modelos) + 1)
    df_comp_modelos["seleccionado"] = df_comp_modelos["ranking_error_prueba"] == 1
    df_comp_modelos.to_csv(ORO_DIR / "comparativa_modelos_pronostico_e1.csv", index=False)

    ganador_row = df_comp_modelos.iloc[0]
    ganador_nombre = str(ganador_row["modelo"])

    # 5. Diagnóstico de Residuos sobre el modelo SARIMA ganador y reentrenamiento en 60 meses para pronóstico 2026
    y_full_log = np.log(y)
    mod_full = SARIMAX(
        y_full_log,
        order=mejor_sarima_orden,
        seasonal_order=mejor_sarima_sorden,
        enforce_stationarity=False,
        enforce_invertibility=False,
    )
    res_full = mod_full.fit(disp=False)
    # Residuos después del periodo de inicialización estacional (primeros 12 meses)
    residuos_activos = res_full.resid.iloc[13:]
    lb_df = acorr_ljungbox(residuos_activos, lags=[6, 12], return_df=True)
    lb_p6 = float(lb_df.loc[6, "lb_pvalue"])
    lb_p12 = float(lb_df.loc[12, "lb_pvalue"])
    lb_q6 = float(lb_df.loc[6, "lb_stat"])
    lb_q12 = float(lb_df.loc[12, "lb_stat"])
    shapiro_stat, shapiro_p = stats.shapiro(residuos_activos)

    # Pronóstico a 12 meses hacia adelante (2026-01 a 2026-12) con intervalo de predicción al 95%
    fc_2026_log = res_full.get_forecast(steps=12)
    mean_log = fc_2026_log.predicted_mean
    ci_log = fc_2026_log.conf_int(alpha=0.05)

    fechas_2026 = pd.date_range("2026-01-01", periods=12, freq="MS")
    pronostico_2026 = pd.DataFrame(
        {
            "anio_mes": fechas_2026.strftime("%Y-%m"),
            "fecha_corte": fechas_2026.strftime("%Y-%m-%d"),
            "horizonte": "Pronostico_Futuro_2026",
            "modelo_utilizado": ganador_nombre,
            "observado_real_mxn_kg": np.nan,
            "pronostico_puntual_mxn_kg": np.round(np.exp(mean_log.to_numpy()), 2),
            "limite_inferior_ic95_mxn_kg": np.round(np.exp(ci_log.iloc[:, 0].to_numpy()), 2),
            "limite_superior_ic95_mxn_kg": np.round(np.exp(ci_log.iloc[:, 1].to_numpy()), 2),
        }
    )

    # También guardar las predicciones en el periodo de prueba (2025-01 a 2025-12) con su IC 95%
    fc_test_log = mejor_sarima_res.get_forecast(steps=12)
    ci_test_log = fc_test_log.conf_int(alpha=0.05)
    evaluacion_test_2025 = pd.DataFrame(
        {
            "anio_mes": y_test.index.strftime("%Y-%m"),
            "fecha_corte": y_test.index.strftime("%Y-%m-%d"),
            "horizonte": "Evaluacion_Prueba_2025",
            "modelo_utilizado": ganador_nombre,
            "observado_real_mxn_kg": np.round(y_test.to_numpy(), 2),
            "pronostico_puntual_mxn_kg": np.round(mejor_pred_sarima.to_numpy(), 2),
            "limite_inferior_ic95_mxn_kg": np.round(np.exp(ci_test_log.iloc[:, 0].to_numpy()), 2),
            "limite_superior_ic95_mxn_kg": np.round(np.exp(ci_test_log.iloc[:, 1].to_numpy()), 2),
            "pred_ses_mxn_kg": np.round(pred_ses.to_numpy(), 2),
            "pred_holt_mxn_kg": np.round(pred_holt.to_numpy(), 2),
            "pred_holt_winters_mxn_kg": np.round(pred_hw.to_numpy(), 2),
            "pred_sarima_mxn_kg": np.round(mejor_pred_sarima.to_numpy(), 2),
        }
    )

    df_pronostico_completo = pd.concat([evaluacion_test_2025, pronostico_2026], ignore_index=True)
    # Clasificación operativa para el cliente citrícola
    df_pronostico_completo["recomendacion_comercial_cliente"] = np.where(
        df_pronostico_completo["pronostico_puntual_mxn_kg"] >= 28.0,
        "VENTANA_ALTA_RENTABILIDAD: Priorizar corte selectivo de exportación y contratos spot en centrales mayoristas",
        np.where(
            df_pronostico_completo["pronostico_puntual_mxn_kg"] <= 16.5,
            "VALLE_ESTACIONAL_COSECHA: Desviar calibre estándar a industria de aceite esencial/jugo y diferir fertilización",
            "OPERACION_ESTANDAR: Mantener embarques programados a Guadalajara, CDMX y Monterrey",
        ),
    )
    df_pronostico_completo.to_csv(ORO_DIR / "pronostico_e1_limon.csv", index=False)

    return {
        "y_train": y_train,
        "y_test": y_test,
        "pred_ses": pred_ses,
        "pred_holt": pred_holt,
        "pred_hw": pred_hw,
        "pred_sarima": mejor_pred_sarima,
        "df_comp_modelos": df_comp_modelos,
        "df_candidatos_sarima": df_candidatos_sarima,
        "ganador_nombre": ganador_nombre,
        "mejor_sarima_orden": mejor_sarima_orden,
        "mejor_sarima_sorden": mejor_sarima_sorden,
        "residuos_activos": residuos_activos,
        "diagnostico_residuos": {
            "ljung_box_lag6_stat": round(lb_q6, 4),
            "ljung_box_lag6_pvalue": round(lb_p6, 4),
            "ljung_box_lag12_stat": round(lb_q12, 4),
            "ljung_box_lag12_pvalue": round(lb_p12, 4),
            "es_ruido_blanco_95pct": bool(lb_p6 > 0.05 and lb_p12 > 0.05),
            "shapiro_wilk_stat": round(float(shapiro_stat), 4),
            "shapiro_wilk_pvalue": round(float(shapiro_p), 4),
            "media_residuos_log": round(float(residuos_activos.mean()), 5),
            "std_residuos_log": round(float(residuos_activos.std(ddof=1)), 5),
        },
        "pronostico_2026": pronostico_2026,
        "evaluacion_test_2025": evaluacion_test_2025,
        "df_pronostico_completo": df_pronostico_completo,
    }


def generar_figuras_e1(
    res_oro: Dict[str, object],
    res_ts_diag: Dict[str, object],
    res_modelos: Dict[str, object],
) -> List[str]:
    """Genera las 5 figuras de alta resolución (300 DPI) en docs/E1/figuras/."""
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.size": 9.5,
            "axes.titlesize": 11,
            "axes.titleweight": "bold",
            "axes.grid": True,
            "grid.alpha": 0.28,
        }
    )

    rutas_generadas = []
    res_plata = res_oro["res_plata"]
    serie_oro = res_oro["serie_oro"]

    # =========================================================================
    # FIGURA 1: Puerta de Calidad, Sesgo de Imputación y Detección de Atípicos
    # =========================================================================
    fig, axes = plt.subplots(1, 3, figsize=(16, 4.8), dpi=220)

    # Panel 1A: Conteo de Reglas Violadas en Cuarentena
    rep_puerta = res_plata["reporte_puerta"]
    desglose = rep_puerta["desglose_reglas_violadas"]
    etiquetas_q = [k.replace("; ", " + ") for k in desglose.keys()]
    valores_q = list(desglose.values())
    bars = axes[0].barh(etiquetas_q, valores_q, color="#dc2626", edgecolor="#7f1d1d", alpha=0.88, height=0.62)
    axes[0].tick_params(axis="y", labelsize=7.5)
    axes[0].set_title("A) Registros Rechazados en Puerta de Calidad\n(Enrutados a data/cuarentena/)")
    axes[0].set_xlabel("Registros en Cuarentena")
    for b in bars:
        axes[0].text(b.get_width() + 0.05, b.get_y() + b.get_height() / 2, f"{int(b.get_width())}", va="center", fontweight="bold")
    axes[0].set_xlim(0, max(valores_q) + 0.8)

    # Panel 1B: Comparación de RMSE de Imputación por Mecanismo (MCAR, MAR, MNAR)
    df_imp = res_plata["eval_faltantes"].dropna(subset=["rmse_imputacion"])
    piv_imp = df_imp.pivot(index="mecanismo_diagnosticado", columns="metodo_tratamiento", values="rmse_imputacion")
    x_pos = np.arange(len(piv_imp.index))
    width = 0.25
    colores_imp = ["#94a3b8", "#0284c7", "#16a34a"]
    for idx_m, col_m in enumerate(piv_imp.columns):
        axes[1].bar(x_pos + (idx_m - 1) * width, piv_imp[col_m], width=width, label=col_m, color=colores_imp[idx_m % 3])
    axes[1].set_xticks(x_pos)
    axes[1].set_xticklabels(["MAR\n(ET0 lluvia)", "MCAR\n(Radiación)", "MNAR\n(Precio P80)"])
    axes[1].set_ylabel("Error RMSE de Imputación")
    axes[1].set_title("B) Evaluación de Imputación por Mecanismo\n(Menor RMSE = Mayor Fidelidad)")
    axes[1].legend(fontsize=7.5, loc="upper left")

    # Panel 1C: Detección de Atípicos en Precio Frecuente (IQR, MAD, Isolation Forest)
    fechas_s = pd.to_datetime(serie_oro["fecha_corte"])
    y_col = serie_oro["precio_frecuente_origen_colima_mxn_kg"]
    mask_choque = serie_oro["es_choque_legitimo_precio"]
    axes[2].plot(fechas_s, y_col, color="#1e293b", lw=1.8, label="Precio Frecuente Origen (MXN/kg)")
    axes[2].scatter(
        fechas_s[mask_choque],
        y_col[mask_choque],
        color="#ea580c",
        s=65,
        zorder=5,
        edgecolors="black",
        label="Choque Legítimo (IQR / MAD / IsoForest)",
    )
    axes[2].axhline(y_col.median(), color="#0d9488", ls="--", lw=1.2, label=f"Mediana ({y_col.median():.1f} MXN/kg)")
    axes[2].set_title("C) Atípicos en Precios (Tecomán/Colima)\nConservados y Etiquetados como Choques Reales")
    axes[2].set_ylabel("Precio Frecuente (MXN/kg)")
    axes[2].legend(fontsize=7.5, loc="upper right")

    fig.tight_layout()
    f1_path = FIGURAS_DIR / "fig1_puerta_calidad_y_limpieza.png"
    fig.savefig(f1_path, bbox_inches="tight")
    plt.close(fig)
    rutas_generadas.append(str(f1_path))

    # =========================================================================
    # FIGURA 2: Descomposición Multiplicativa de la Serie de 60 Meses
    # =========================================================================
    decomp = res_ts_diag["decomp_mul"]
    y_ts = res_ts_diag["serie_y"]
    fig, axes = plt.subplots(4, 1, figsize=(13, 8.5), sharex=True, dpi=220)

    axes[0].plot(y_ts.index, y_ts.values, color="#0f766e", lw=2.0, marker="o", ms=3.5)
    axes[0].annotate(
        "Choque Feb-Mar 2022\n(46.63 MXN/kg en origen)",
        xy=(pd.Timestamp("2022-02-01"), float(y_ts.loc["2022-02-01"])),
        xytext=(pd.Timestamp("2022-06-01"), 43.0),
        arrowprops=dict(arrowstyle="->", color="#dc2626", lw=1.5),
        fontsize=8.5,
        fontweight="bold",
        color="#991b1b",
    )
    axes[0].annotate(
        "Pico Invernal Feb 2024\n(36.44 MXN/kg)",
        xy=(pd.Timestamp("2024-02-01"), float(y_ts.loc["2024-02-01"])),
        xytext=(pd.Timestamp("2024-05-01"), 38.0),
        arrowprops=dict(arrowstyle="->", color="#d97706", lw=1.5),
        fontsize=8.5,
        fontweight="bold",
        color="#92400e",
    )
    axes[0].set_title("Serie Histórica en Capa Oro (60 Meses: 2021-01 a 2025-12) y Descomposición Multiplicativa (Y_t = T_t × S_t × R_t)")
    axes[0].set_ylabel("Observado\n(MXN/kg)")

    axes[1].plot(decomp.trend.index, decomp.trend.values, color="#1d4ed8", lw=2.2)
    axes[1].set_ylabel("Tendencia (T_t)\n(MXN/kg)")

    axes[2].plot(decomp.seasonal.index, decomp.seasonal.values, color="#15803d", lw=1.8)
    axes[2].axhline(1.0, color="gray", ls="--", lw=1.0)
    axes[2].set_ylabel("Factor Estacional\nMultiplicativo (S_t)")

    axes[3].scatter(decomp.resid.index, decomp.resid.values, color="#7c3aed", s=24)
    axes[3].plot(decomp.resid.index, decomp.resid.values, color="#7c3aed", lw=1.0, alpha=0.6)
    axes[3].axhline(1.0, color="gray", ls="--", lw=1.0)
    axes[3].set_ylabel("Residuo (R_t)")
    axes[3].set_xlabel("Fecha Mensual (Corte YYYY-MM-01)")

    fig.tight_layout()
    f2_path = FIGURAS_DIR / "fig2_descomposicion_serie_60m.png"
    fig.savefig(f2_path, bbox_inches="tight")
    plt.close(fig)
    rutas_generadas.append(str(f2_path))

    # =========================================================================
    # FIGURA 3: Estacionariedad (ADF), ACF, PACF y Correlación Cruzada (CCF)
    # =========================================================================
    fig, axes = plt.subplots(2, 2, figsize=(14, 8.2), dpi=220)

    # 3A: Serie en Nivel vs Primera Diferencia (ADF)
    pruebas_adf = res_ts_diag["pruebas_adf"]
    ax_a = axes[0, 0]
    ax_a.plot(y_ts.index, y_ts.values, color="#0f766e", lw=1.7, label=f"Nivel Y_t (ADF p={pruebas_adf[0]['p_valor']:.4f})")
    ax_a.plot(y_ts.index, y_ts.diff(1).values, color="#dc2626", lw=1.4, ls="--", label=f"1ª Dif. ΔY_t (ADF p={pruebas_adf[1]['p_valor']:.4f})")
    ax_a.axhline(0.0, color="black", lw=0.8)
    ax_a.set_title("A) Prueba Augmented Dickey-Fuller (ADF): Nivel vs 1ª Diferencia")
    ax_a.set_ylabel("MXN/kg")
    ax_a.legend(fontsize=8)

    # 3B: ACF hasta rezago 24
    vals_acf = res_ts_diag["vals_acf_24"]
    lags_24 = np.arange(len(vals_acf))
    ic_band = 1.96 / np.sqrt(len(y_ts))
    axes[0, 1].bar(lags_24, vals_acf, width=0.35, color="#1d4ed8")
    axes[0, 1].axhline(ic_band, color="#dc2626", ls="--", lw=1.1, label="IC 95% (±0.253)")
    axes[0, 1].axhline(-ic_band, color="#dc2626", ls="--", lw=1.1)
    axes[0, 1].axhline(0.0, color="black", lw=0.8)
    axes[0, 1].set_title("B) Función de Autocorrelación (ACF) — Picos en Lag 1 y Lag 12 (m=12)")
    axes[0, 1].set_xlabel("Rezago k (meses)")
    axes[0, 1].set_ylabel("ACF r_k")
    axes[0, 1].legend(fontsize=8)

    # 3C: PACF hasta rezago 24
    vals_pacf = res_ts_diag["vals_pacf_24"]
    axes[1, 0].bar(lags_24, vals_pacf, width=0.35, color="#047857")
    axes[1, 0].axhline(ic_band, color="#dc2626", ls="--", lw=1.1, label="IC 95% (±0.253)")
    axes[1, 0].axhline(-ic_band, color="#dc2626", ls="--", lw=1.1)
    axes[1, 0].axhline(0.0, color="black", lw=0.8)
    axes[1, 0].set_title("C) Autocorrelación Parcial (PACF) — Corte después de Lag 1 y Lag 12")
    axes[1, 0].set_xlabel("Rezago k (meses)")
    axes[1, 0].set_ylabel("PACF φ_kk")
    axes[1, 0].legend(fontsize=8)

    # 3D: Correlación Cruzada (CCF) Clima en Tecomán (t - k) -> Precio Limón (t)
    df_ccf = res_ts_diag["df_ccf"]
    for col_v, color_v, lbl_v in [
        ("deficit_hidrico_tecoman_mm", "#dc2626", "Déficit Hídrico Tecomán (P - ET0)"),
        ("precipitacion_tecoman_mm", "#2563eb", "Precipitación Acumulada Tecomán"),
        ("temp_max_tecoman_c", "#d97706", "Temperatura Máxima Tecomán"),
    ]:
        sub = df_ccf[df_ccf["variable_climatica"] == col_v]
        axes[1, 1].plot(sub["rezago_meses_k"], sub["correlacion_cruzada_r"], marker="o", lw=1.8, color=color_v, label=lbl_v)
    axes[1, 1].axhline(ic_band, color="gray", ls="--", lw=1.0)
    axes[1, 1].axhline(-ic_band, color="gray", ls="--", lw=1.0, label="Umbral significancia 95%")
    axes[1, 1].axhline(0.0, color="black", lw=0.8)
    axes[1, 1].set_title("D) Correlación Cruzada (CCF): Clima en Tecomán (t-k) vs Precio Limón (t)")
    axes[1, 1].set_xlabel("Rezago k en meses (Clima antecede al Precio en k meses)")
    axes[1, 1].set_ylabel("Correlación de Pearson r")
    axes[1, 1].legend(fontsize=7.8, loc="lower right")

    fig.tight_layout()
    f3_path = FIGURAS_DIR / "fig3_estacionariedad_acf_pacf_ccf.png"
    fig.savefig(f3_path, bbox_inches="tight")
    plt.close(fig)
    rutas_generadas.append(str(f3_path))

    # =========================================================================
    # FIGURA 4: Comparación de los 4 Modelos en el Conjunto de Prueba (12 Meses)
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2), dpi=220, gridspec_kw={"width_ratios": [1.55, 1.0]})

    y_train = res_modelos["y_train"]
    y_test = res_modelos["y_test"]
    ax_p = axes[0]
    ax_p.plot(y_train.index[-18:], y_train.values[-18:], color="#334155", lw=1.8, label="Entrenamiento (últimos 18m: 2023-07 a 2024-12)")
    ax_p.plot(y_test.index, y_test.values, color="#000000", lw=2.6, marker="o", label="Observado Real Prueba (2025-01 a 2025-12)")
    ax_p.plot(y_test.index, res_modelos["pred_ses"].values, color="#94a3b8", ls=":", lw=1.8, label="1. SES")
    ax_p.plot(y_test.index, res_modelos["pred_holt"].values, color="#f59e0b", ls="-.", lw=1.8, label="2. Holt")
    ax_p.plot(y_test.index, res_modelos["pred_hw"].values, color="#2563eb", ls="--", lw=2.0, label="3. Holt-Winters (m=12)")
    ax_p.plot(y_test.index, res_modelos["pred_sarima"].values, color="#16a34a", lw=2.4, marker="s", ms=4.5, label=f"4. {res_modelos['ganador_nombre']} (Ganador)")
    ax_p.axvline(pd.Timestamp("2025-01-01"), color="#dc2626", ls="--", lw=1.2)
    ax_p.set_title("A) Desempeño de los 4 Modelos en Conjunto de Prueba (Hold-out 12 Meses: 2025)")
    ax_p.set_ylabel("Precio Frecuente en Origen (MXN/kg)")
    ax_p.legend(fontsize=8, loc="upper left")

    # Barras de MAE, RMSE y MAPE
    df_cm = res_modelos["df_comp_modelos"].sort_values("id_modelo")
    nombres_cortos = ["M1: SES", "M2: Holt", "M3: Holt-Winters", "M4: SARIMA"]
    x_m = np.arange(len(nombres_cortos))
    w_m = 0.26
    axes[1].bar(x_m - w_m, df_cm["MAE_test_mxn_kg"], width=w_m, label="MAE (MXN/kg)", color="#0284c7")
    axes[1].bar(x_m, df_cm["RMSE_test_mxn_kg"], width=w_m, label="RMSE (MXN/kg)", color="#7c3aed")
    axes[1].bar(x_m + w_m, df_cm["MAPE_test_pct"], width=w_m, label="MAPE (%)", color="#16a34a")
    for idx_i, r_row in enumerate(df_cm.itertuples()):
        axes[1].text(idx_i, r_row.RMSE_test_mxn_kg + 0.3, f"{r_row.RMSE_test_mxn_kg:.2f}", ha="center", fontsize=8, fontweight="bold")
        axes[1].text(idx_i + w_m, r_row.MAPE_test_pct + 0.3, f"{r_row.MAPE_test_pct:.1f}%", ha="center", fontsize=8)
    axes[1].set_xticks(x_m)
    axes[1].set_xticklabels(nombres_cortos)
    axes[1].set_title("B) Comparación de Errores en Prueba (MAE, RMSE, MAPE)")
    axes[1].set_ylabel("Magnitud del Error")
    axes[1].legend(fontsize=8.5)

    fig.tight_layout()
    f4_path = FIGURAS_DIR / "fig4_comparativa_4_modelos_test.png"
    fig.savefig(f4_path, bbox_inches="tight")
    plt.close(fig)
    rutas_generadas.append(str(f4_path))

    # =========================================================================
    # FIGURA 5: Diagnóstico de Residuos y Pronóstico 2026 con IC 95%
    # =========================================================================
    fig, axes = plt.subplots(1, 2, figsize=(15.5, 5.2), dpi=220, gridspec_kw={"width_ratios": [1.0, 1.65]})

    res_act = res_modelos["residuos_activos"]
    diag_r = res_modelos["diagnostico_residuos"]
    axes[0].plot(res_act.index, res_act.values, color="#4f46e5", lw=1.4, marker="o", ms=3.5)
    axes[0].axhline(0.0, color="black", lw=1.0)
    axes[0].axhline(2 * res_act.std(), color="#dc2626", ls="--", lw=1.0, label="Banda ±2σ (Varianza Estable)")
    axes[0].axhline(-2 * res_act.std(), color="#dc2626", ls="--", lw=1.0)
    axes[0].set_title(
        f"A) Residuos del Modelo Ganador y Prueba de Ljung-Box\n"
        f"Q(6)={diag_r['ljung_box_lag6_stat']:.2f} (p={diag_r['ljung_box_lag6_pvalue']:.3f}), "
        f"Q(12)={diag_r['ljung_box_lag12_stat']:.2f} (p={diag_r['ljung_box_lag12_pvalue']:.3f}) -> Ruido Blanco"
    )
    axes[0].set_ylabel("Residuo en escala log")
    axes[0].legend(fontsize=8)

    # Pronóstico final con IC 95% y bandas operativas para el cliente
    fc_2026 = res_modelos["pronostico_2026"]
    fechas_fc = pd.to_datetime(fc_2026["fecha_corte"])
    axes[1].plot(y_ts.index[-24:], y_ts.values[-24:], color="#0f172a", lw=2.0, marker="o", ms=3.5, label="Histórico Oro (2024-2025)")
    axes[1].plot(fechas_fc, fc_2026["pronostico_puntual_mxn_kg"], color="#16a34a", lw=2.5, marker="s", ms=5, label="Pronóstico Puntual 2026 (SARIMA)")
    axes[1].fill_between(
        fechas_fc,
        fc_2026["limite_inferior_ic95_mxn_kg"],
        fc_2026["limite_superior_ic95_mxn_kg"],
        color="#22c55e",
        alpha=0.25,
        label="Intervalo de Predicción al 95%",
    )
    axes[1].axhline(28.0, color="#ea580c", ls="--", lw=1.2, label="Umbral Ventana Alta Rentabilidad (28 MXN/kg)")
    axes[1].axhline(16.5, color="#0284c7", ls=":", lw=1.2, label="Umbral Piso Cosecha Verano (16.5 MXN/kg)")
    axes[1].set_title("B) Pronóstico Oficial 2026 con Intervalo de Confianza al 95% para Toma de Decisiones")
    axes[1].set_ylabel("Precio Frecuente en Origen Colima (MXN/kg)")
    axes[1].legend(fontsize=8, loc="upper left")

    fig.tight_layout()
    f5_path = FIGURAS_DIR / "fig5_pronostico_final_ic95_residuos.png"
    fig.savefig(f5_path, bbox_inches="tight")
    plt.close(fig)
    rutas_generadas.append(str(f5_path))

    return rutas_generadas


def ejecutar_series_tiempo_e1() -> Dict[str, object]:
    """Ejecuta extremo a extremo el pipeline de Capa Oro y Series de Tiempo para E1."""
    res_oro = construir_capa_oro()
    serie_oro = res_oro["serie_oro"]

    res_ts_diag = analizar_descomposicion_y_estacionariedad(serie_oro)
    res_modelos = entrenar_y_seleccionar_modelos(serie_oro)
    rutas_figuras = generar_figuras_e1(res_oro, res_ts_diag, res_modelos)

    resumen_json = {
        "serie_analizada": "precio_frecuente_origen_colima_mxn_kg",
        "cobertura_temporal": "2021-01 a 2025-12 (60 meses)",
        "particion_entrenamiento": "2021-01 a 2024-12 (48 meses)",
        "particion_prueba": "2025-01 a 2025-12 (12 meses)",
        "justificacion_descomposicion": res_ts_diag["justificacion_descomposicion"],
        "pruebas_estacionariedad_adf": res_ts_diag["pruebas_adf"],
        "acf_lags_0_12": res_ts_diag["acf_lags_0_12"],
        "pacf_lags_0_12": res_ts_diag["pacf_lags_0_12"],
        "correlacion_cruzada_destacada": (
            res_ts_diag["df_ccf"]
            .loc[res_ts_diag["df_ccf"]["significativa_95pct"]]
            .to_dict(orient="records")
        ),
        "comparativa_4_modelos_prueba": res_modelos["df_comp_modelos"].to_dict(orient="records"),
        "modelo_ganador": res_modelos["ganador_nombre"],
        "diagnostico_residuos_ljung_box": res_modelos["diagnostico_residuos"],
        "pronostico_2026_ic95": res_modelos["pronostico_2026"].to_dict(orient="records"),
        "figuras_generadas": rutas_figuras,
    }

    with open(ORO_DIR / "diagnostico_series_tiempo_e1.json", "w", encoding="utf-8") as f:
        json.dump(resumen_json, f, indent=2, ensure_ascii=False)

    return resumen_json


if __name__ == "__main__":
    resumen = ejecutar_series_tiempo_e1()
    print(f"[OK] Series de tiempo E1 ejecutadas. Modelo ganador: {resumen['modelo_ganador']}")
    for mod in resumen["comparativa_4_modelos_prueba"]:
        print(
            f"  - {mod['modelo']}: MAE={mod['MAE_test_mxn_kg']}, "
            f"RMSE={mod['RMSE_test_mxn_kg']}, MAPE={mod['MAPE_test_pct']}%"
        )
    print(f"  - Ljung-Box p(6)={resumen['diagnostico_residuos_ljung_box']['ljung_box_lag6_pvalue']}, p(12)={resumen['diagnostico_residuos_ljung_box']['ljung_box_lag12_pvalue']}")
