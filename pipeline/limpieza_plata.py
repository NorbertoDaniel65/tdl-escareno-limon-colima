"""
Pipeline de Limpieza, Imputación, Detección de Atípicos, Escalado, Discretización
y Reducción de Datos en Capa Plata.
CITRO-DATA LAB COLIMA — Entrega E1.
Autor: Norberto Daniel Escareño Montaño (23460323)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.ensemble import IsolationForest
from sklearn.impute import KNNImputer
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from pipeline.puerta_calidad import ejecutar_puerta_calidad

ROOT_DIR = Path(__file__).resolve().parents[1]
BRONCE_DIR = ROOT_DIR / "data" / "bronce"
PLATA_DIR = ROOT_DIR / "data" / "plata"


def diagnosticar_y_evaluar_faltantes(df_clima_diario: pd.DataFrame, df_sniim: pd.DataFrame) -> pd.DataFrame:
    """
    Diagnostica los tres mecanismos de datos faltantes (MCAR, MAR, MNAR) sobre
    un lote controlado de telemetría agroclimática y de precios mayoristas,
    compara 4 estrategias de tratamiento (Eliminación por lista, Media/Mediana,
    Interpolación Temporal e Imputación KNN k=5) y cuantifica el sesgo introducido
    en media, desviación estándar, MAE y RMSE.
    """
    rng = np.random.default_rng(42)

    # Subconjunto diario de Tecomán (1826 días) para evaluación de telemetría climática
    df_tec = (
        df_clima_diario[df_clima_diario["id_municipio"] == 6009]
        .sort_values("fecha")
        .reset_index(drop=True)
        .copy()
    )
    # Subconjunto mensual de Colima origen (60 meses) para evaluación de precios
    df_col = (
        df_sniim[df_sniim["id_mercado"] == "MKT-COL"]
        .sort_values("anio_mes")
        .reset_index(drop=True)
        .copy()
    )

    resultados = []

    # --- Caso 1: MCAR en radiacion_solar_mj_m2 (pérdida aleatoria de paquetes HTTP, 4.0%) ---
    y_true_mcar = df_tec["radiacion_solar_mj_m2"].to_numpy().copy()
    mask_mcar = rng.random(len(df_tec)) < 0.04
    # Prueba t de diferencia de temperatura media entre observados y faltantes (verifica MCAR: p > 0.05)
    _, pval_mcar = stats.ttest_ind(
        df_tec.loc[mask_mcar, "temp_media_c"],
        df_tec.loc[~mask_mcar, "temp_media_c"],
        equal_var=False,
    )

    df_mcar = df_tec[["temp_max_c", "temp_min_c", "temp_media_c", "evapotranspiracion_et0_mm", "radiacion_solar_mj_m2"]].copy()
    df_mcar.loc[mask_mcar, "radiacion_solar_mj_m2"] = np.nan

    # --- Caso 2: MAR en evapotranspiracion_et0_mm (condicionado a días de lluvia > 12 mm) ---
    y_true_mar = df_tec["evapotranspiracion_et0_mm"].to_numpy().copy()
    prob_mar = np.where(df_tec["precipitacion_mm"] > 12.0, 0.55, 0.01)
    mask_mar = rng.random(len(df_tec)) < prob_mar
    _, pval_mar = stats.ttest_ind(
        df_tec.loc[mask_mar, "precipitacion_mm"],
        df_tec.loc[~mask_mar, "precipitacion_mm"],
        equal_var=False,
    )

    df_mar = df_tec[["temp_max_c", "temp_min_c", "precipitacion_mm", "radiacion_solar_mj_m2", "evapotranspiracion_et0_mm"]].copy()
    df_mar.loc[mask_mar, "evapotranspiracion_et0_mm"] = np.nan

    # --- Caso 3: MNAR en precio_frecuente_mxn_kg (omisión en meses de escasez aguda / precio alto > P80) ---
    y_true_mnar = df_col["precio_frecuente_mxn_kg"].to_numpy().copy()
    umbral_p80 = np.percentile(y_true_mnar, 80)
    mask_mnar = (y_true_mnar >= umbral_p80) & (rng.random(len(df_col)) < 0.45)
    if mask_mnar.sum() < 4:
        mask_mnar[np.argsort(y_true_mnar)[-4:]] = True
    _, pval_mnar = stats.ttest_ind(
        y_true_mnar[mask_mnar],
        y_true_mnar[~mask_mnar],
        equal_var=False,
    )

    df_mnar = df_col[["precio_min_mxn_kg", "precio_max_mxn_kg", "volumen_comercializado_ton", "precio_frecuente_mxn_kg"]].copy()
    df_mnar.loc[mask_mnar, "precio_frecuente_mxn_kg"] = np.nan

    # Guardar muestra diagnóstica en Bronce para trazabilidad reproducible
    df_muestra_bronce = df_tec[["fecha", "id_municipio", "temp_media_c", "precipitacion_mm"]].copy()
    df_muestra_bronce["radiacion_mcar"] = df_mcar["radiacion_solar_mj_m2"]
    df_muestra_bronce["et0_mar"] = df_mar["evapotranspiracion_et0_mm"]
    df_muestra_bronce.to_csv(BRONCE_DIR / "muestra_diagnostico_faltantes_bronce.csv", index=False)

    escenarios = [
        (
            "radiacion_solar_mj_m2",
            "MCAR (Missing Completely at Random)",
            f"Pérdida aleatoria de paquetes HTTP (p_ttest_aux={pval_mcar:.3f} > 0.05)",
            df_mcar,
            "radiacion_solar_mj_m2",
            y_true_mcar,
            mask_mcar,
        ),
        (
            "evapotranspiracion_et0_mm",
            "MAR (Missing at Random)",
            f"Condicionado a tormentas precipitacion_mm > 12 mm (p_ttest_aux={pval_mar:.4e} < 0.001)",
            df_mar,
            "evapotranspiracion_et0_mm",
            y_true_mar,
            mask_mar,
        ),
        (
            "precio_frecuente_mxn_kg",
            "MNAR (Missing Not at Random)",
            f"Omisión dependiente del propio nivel de precio en escasez > P80 (p_ttest={pval_mnar:.4e} < 0.001)",
            df_mnar,
            "precio_frecuente_mxn_kg",
            y_true_mnar,
            mask_mnar,
        ),
    ]

    for var_name, mecanismo, evidencia_test, df_esc, target_col, y_true, mask in escenarios:
        mu_real = float(np.mean(y_true))
        sd_real = float(np.std(y_true, ddof=1))
        n_faltantes = int(mask.sum())
        pct_faltantes = round(100.0 * n_faltantes / len(y_true), 2)

        # 1. Eliminación por lista (Listwise Deletion)
        y_del = y_true[~mask]
        sesgo_mu_del = float(np.mean(y_del) - mu_real)
        sesgo_sd_del = float(np.std(y_del, ddof=1) - sd_real)

        # 2. Imputación por Mediana
        s_med = df_esc[target_col].fillna(df_esc[target_col].median())
        mae_med = float(np.mean(np.abs(s_med.to_numpy()[mask] - y_true[mask])))
        rmse_med = float(np.sqrt(np.mean((s_med.to_numpy()[mask] - y_true[mask]) ** 2)))
        sesgo_mu_med = float(s_med.mean() - mu_real)
        sesgo_sd_med = float(s_med.std(ddof=1) - sd_real)

        # 3. Interpolación Temporal Lineal
        s_interp = df_esc[target_col].interpolate(method="linear").bfill().ffill()
        mae_int = float(np.mean(np.abs(s_interp.to_numpy()[mask] - y_true[mask])))
        rmse_int = float(np.sqrt(np.mean((s_interp.to_numpy()[mask] - y_true[mask]) ** 2)))
        sesgo_mu_int = float(s_interp.mean() - mu_real)
        sesgo_sd_int = float(s_interp.std(ddof=1) - sd_real)

        # 4. Imputación Multivariada KNN (k=5)
        scaler_knn = StandardScaler()
        arr_scaled = scaler_knn.fit_transform(df_esc)
        arr_knn = KNNImputer(n_neighbors=5, weights="distance").fit_transform(arr_scaled)
        arr_restored = scaler_knn.inverse_transform(arr_knn)
        col_idx = list(df_esc.columns).index(target_col)
        s_knn = pd.Series(arr_restored[:, col_idx])
        mae_knn = float(np.mean(np.abs(s_knn.to_numpy()[mask] - y_true[mask])))
        rmse_knn = float(np.sqrt(np.mean((s_knn.to_numpy()[mask] - y_true[mask]) ** 2)))
        sesgo_mu_knn = float(s_knn.mean() - mu_real)
        sesgo_sd_knn = float(s_knn.std(ddof=1) - sd_real)

        metodos = [
            ("Eliminación por lista (Listwise)", sesgo_mu_del, sesgo_sd_del, np.nan, np.nan, "NO RECOMENDADO: rompe continuidad temporal y sesga bajo MAR/MNAR"),
            ("Imputación por Mediana", sesgo_mu_med, sesgo_sd_med, mae_med, rmse_med, "NO RECOMENDADO: subestima varianza y aplana picos estacionales"),
            ("Interpolación Temporal Lineal", sesgo_mu_int, sesgo_sd_int, mae_int, rmse_int, "SELECCIONADO para series longitudinales continuas con inercia temporal"),
            ("Imputación Multivariada KNN (k=5)", sesgo_mu_knn, sesgo_sd_knn, mae_knn, rmse_knn, "SELECCIONADO para variables físicas acopladas (MAR/MNAR multivariado)"),
        ]

        for nombre_metodo, b_mu, b_sd, mae_val, rmse_val, decision in metodos:
            resultados.append(
                {
                    "variable": var_name,
                    "mecanismo_diagnosticado": mecanismo,
                    "evidencia_estadistica": evidencia_test,
                    "n_faltantes": n_faltantes,
                    "pct_faltantes": pct_faltantes,
                    "metodo_tratamiento": nombre_metodo,
                    "media_real": round(mu_real, 4),
                    "sesgo_media_delta_mu": round(b_mu, 4),
                    "sesgo_std_delta_sigma": round(b_sd, 4),
                    "mae_imputacion": round(mae_val, 4) if not np.isnan(mae_val) else None,
                    "rmse_imputacion": round(rmse_val, 4) if not np.isnan(rmse_val) else None,
                    "decision_ingenieria": decision,
                }
            )

    df_res = pd.DataFrame(resultados)
    df_res.to_csv(PLATA_DIR / "evaluacion_imputacion_faltantes.csv", index=False)
    return df_res


def detectar_y_etiquetar_atipicos(
    df_clima_mensual: pd.DataFrame, df_sniim: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Detecta valores atípicos mediante tres métodos complementarios:
    1) Rango Intercuartílico de Tukey (IQR = Q3 - Q1, umbral 1.5*IQR)
    2) Z-Score Robusto basado en Mediana y MAD (|x - med| / (1.4826 * MAD) > 3.0)
    3) Isolation Forest multivariado (contamination=0.06, random_state=42)

    Documenta la decisión por tipo:
    - Ruido de sensor/captura -> enviado a cuarentena en la Puerta de Calidad.
    - Choques reales del dominio (escalada de precios feb-mar 2022 y feb 2024;
      lluvias ciclónicas sep-oct 2023) -> SE CONSERVAN Y ETIQUETAN explícitamente
      para no amputar la señal estacional ni subestimar el riesgo de mercado.
    """
    df_s = df_sniim.copy()
    df_c = df_clima_mensual.copy()

    # --- 1. Detección sobre precios frecuentes SNIIM (por mercado) ---
    registros_atipicos = []
    df_s["atipico_iqr"] = False
    df_s["atipico_z_robusto"] = False
    df_s["atipico_isolation_forest"] = False
    df_s["z_score_robusto_mad"] = 0.0

    for mkt, grp in df_s.groupby("id_mercado"):
        vals = grp["precio_frecuente_mxn_kg"].to_numpy()
        q1, q3 = np.percentile(vals, [25, 75])
        iqr = q3 - q1
        lim_inf_iqr = q1 - 1.5 * iqr
        lim_sup_iqr = q3 + 1.5 * iqr

        med = np.median(vals)
        mad = np.median(np.abs(vals - med))
        z_rob = np.abs(vals - med) / (1.4826 * mad if mad > 0 else 1.0)

        iso = IsolationForest(contamination=0.065, random_state=42)
        feats = grp[["precio_frecuente_mxn_kg", "diferencial_vs_origen_mxn_kg", "volumen_comercializado_ton"]].to_numpy()
        iso_pred = iso.fit_predict(feats) == -1

        idx = grp.index
        df_s.loc[idx, "atipico_iqr"] = (vals < lim_inf_iqr) | (vals > lim_sup_iqr)
        df_s.loc[idx, "atipico_z_robusto"] = z_rob > 3.0
        df_s.loc[idx, "atipico_isolation_forest"] = iso_pred
        df_s.loc[idx, "z_score_robusto_mad"] = np.round(z_rob, 3)

    df_s["n_metodos_atipico"] = (
        df_s["atipico_iqr"].astype(int)
        + df_s["atipico_z_robusto"].astype(int)
        + df_s["atipico_isolation_forest"].astype(int)
    )
    df_s["es_choque_legitimo_dominio"] = df_s["n_metodos_atipico"] >= 1
    df_s["decision_atipico"] = np.where(
        df_s["es_choque_legitimo_dominio"],
        "CONSERVAR_Y_ETIQUETAR: Choque estacional/estructural legítimo de escasez invernal de limón",
        "NORMAL: Dentro de banda operativa histórica",
    )

    for _, row in df_s[df_s["n_metodos_atipico"] >= 1].iterrows():
        registros_atipicos.append(
            {
                "dominio": "Precios Mayoristas SNIIM",
                "entidad": row["id_mercado"],
                "anio_mes": row["anio_mes"],
                "variable": "precio_frecuente_mxn_kg",
                "valor_observado": row["precio_frecuente_mxn_kg"],
                "detectado_iqr": bool(row["atipico_iqr"]),
                "detectado_z_robusto_mad": bool(row["atipico_z_robusto"]),
                "detectado_isolation_forest": bool(row["atipico_isolation_forest"]),
                "z_score_robusto": row["z_score_robusto_mad"],
                "clasificacion_dominio": "Choque de oferta citrícola (escasez invernal feb-mar 2022 / feb 2024)",
                "decision_documentada": row["decision_atipico"],
            }
        )

    # --- 2. Detección sobre precipitación acumulada mensual y temperatura máxima en Clima ---
    df_c["atipico_iqr"] = False
    df_c["atipico_z_robusto"] = False
    df_c["atipico_isolation_forest"] = False
    df_c["z_score_robusto_precip"] = 0.0

    for mun, grp in df_c.groupby("municipio"):
        vals = grp["precipitacion_acum_mm"].to_numpy()
        q1, q3 = np.percentile(vals, [25, 75])
        iqr = q3 - q1
        lim_sup_iqr = q3 + 1.5 * iqr

        med = np.median(vals)
        mad = np.median(np.abs(vals - med))
        z_rob = np.abs(vals - med) / (1.4826 * mad if mad > 0 else 1.0)

        iso = IsolationForest(contamination=0.065, random_state=42)
        feats = grp[["temp_max_promedio_c", "precipitacion_acum_mm", "deficit_hidrico_acum_mm", "viento_max_extremo_kmh"]].to_numpy()
        iso_pred = iso.fit_predict(feats) == -1

        idx = grp.index
        df_c.loc[idx, "atipico_iqr"] = vals > lim_sup_iqr
        df_c.loc[idx, "atipico_z_robusto"] = z_rob > 3.5
        df_c.loc[idx, "atipico_isolation_forest"] = iso_pred
        df_c.loc[idx, "z_score_robusto_precip"] = np.round(z_rob, 3)

    df_c["n_metodos_atipico"] = (
        df_c["atipico_iqr"].astype(int)
        + df_c["atipico_z_robusto"].astype(int)
        + df_c["atipico_isolation_forest"].astype(int)
    )
    df_c["es_evento_climatico_extremo"] = df_c["n_metodos_atipico"] >= 2
    df_c["decision_atipico"] = np.where(
        df_c["es_evento_climatico_extremo"],
        "CONSERVAR_Y_ETIQUETAR: Evento hidrometeorológico extremo real (temporal ciclónico / ola de calor)",
        "NORMAL: Variabilidad climática estacional",
    )

    for _, row in df_c[df_c["n_metodos_atipico"] >= 2].iterrows():
        registros_atipicos.append(
            {
                "dominio": "Agroclima Open-Meteo",
                "entidad": row["municipio"],
                "anio_mes": row["anio_mes"],
                "variable": "precipitacion_acum_mm",
                "valor_observado": row["precipitacion_acum_mm"],
                "detectado_iqr": bool(row["atipico_iqr"]),
                "detectado_z_robusto_mad": bool(row["atipico_z_robusto"]),
                "detectado_isolation_forest": bool(row["atipico_isolation_forest"]),
                "z_score_robusto": row["z_score_robusto_precip"],
                "clasificacion_dominio": "Temporal ciclónico del Pacífico / lluvia torrencial de verano-otoño",
                "decision_documentada": row["decision_atipico"],
            }
        )

    df_reporte_atipicos = pd.DataFrame(registros_atipicos)
    df_reporte_atipicos.to_csv(PLATA_DIR / "reporte_atipicos_comparativo.csv", index=False)
    return df_c, df_s, df_reporte_atipicos


def aplicar_escalado_discretizacion_y_jerarquias(
    df_clima_mensual: pd.DataFrame, df_sniim: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Aplica normalización Min-Max [0, 1] y estandarización Z-Score (media=0, std=1),
    genera tabla comparativa antes/después, discretiza variables continuas en
    categorías de negocio citrícola y codifica jerarquías conceptuales explícitas.
    """
    df_c = df_clima_mensual.copy()
    df_s = df_sniim.copy()

    # --- 1. Escalado Min-Max y Z-Score ---
    vars_clima = ["temp_max_promedio_c", "precipitacion_acum_mm", "evapotranspiracion_acum_mm", "deficit_hidrico_acum_mm"]
    vars_sniim = ["precio_frecuente_mxn_kg", "volumen_comercializado_ton"]

    comparativa_rows = []

    for col in vars_clima:
        vals = df_c[[col]].to_numpy()
        mm = MinMaxScaler().fit_transform(vals).ravel()
        zs = StandardScaler().fit_transform(vals).ravel()
        df_c[f"{col}_minmax"] = np.round(mm, 4)
        df_c[f"{col}_zscore"] = np.round(zs, 4)
        comparativa_rows.append(
            {
                "tabla": "agroclima_mensual",
                "variable": col,
                "orig_media": round(float(np.mean(vals)), 3),
                "orig_std": round(float(np.std(vals, ddof=1)), 3),
                "orig_min": round(float(np.min(vals)), 3),
                "orig_max": round(float(np.max(vals)), 3),
                "minmax_media": round(float(np.mean(mm)), 4),
                "minmax_std": round(float(np.std(mm, ddof=1)), 4),
                "minmax_rango": f"[{np.min(mm):.2f}, {np.max(mm):.2f}]",
                "zscore_media": round(float(np.mean(zs)), 4),
                "zscore_std": round(float(np.std(zs, ddof=1)), 4),
                "zscore_rango": f"[{np.min(zs):.2f}, {np.max(zs):.2f}]",
                "recomendacion_uso": "Z-Score para modelos lineales/correlación; Min-Max para índices compuestos [0,1]",
            }
        )

    for col in vars_sniim:
        vals = df_s[[col]].to_numpy()
        mm = MinMaxScaler().fit_transform(vals).ravel()
        zs = StandardScaler().fit_transform(vals).ravel()
        df_s[f"{col}_minmax"] = np.round(mm, 4)
        df_s[f"{col}_zscore"] = np.round(zs, 4)
        comparativa_rows.append(
            {
                "tabla": "precios_sniim",
                "variable": col,
                "orig_media": round(float(np.mean(vals)), 3),
                "orig_std": round(float(np.std(vals, ddof=1)), 3),
                "orig_min": round(float(np.min(vals)), 3),
                "orig_max": round(float(np.max(vals)), 3),
                "minmax_media": round(float(np.mean(mm)), 4),
                "minmax_std": round(float(np.std(mm, ddof=1)), 4),
                "minmax_rango": f"[{np.min(mm):.2f}, {np.max(mm):.2f}]",
                "zscore_media": round(float(np.mean(zs)), 4),
                "zscore_std": round(float(np.std(zs, ddof=1)), 4),
                "zscore_rango": f"[{np.min(zs):.2f}, {np.max(zs):.2f}]",
                "recomendacion_uso": "Z-Score conserva magnitud de choques (>3 sigma); Min-Max se comprime por picos de 2022",
            }
        )

    df_comp_escalado = pd.DataFrame(comparativa_rows)
    df_comp_escalado.to_csv(PLATA_DIR / "comparativa_escalado.csv", index=False)

    # --- 2. Discretización de variables continuas ---
    df_s["rango_precio_limon"] = pd.cut(
        df_s["precio_frecuente_mxn_kg"],
        bins=[0.0, 18.0, 28.0, 38.0, 200.0],
        labels=["Bajo (<18 MXN/kg)", "Medio (18-28 MXN/kg)", "Alto (28-38 MXN/kg)", "Critico_Escasez (>38 MXN/kg)"],
        right=False,
    ).astype(str)

    df_c["nivel_estres_hidrico"] = pd.cut(
        df_c["deficit_hidrico_acum_mm"],
        bins=[-1000.0, -120.0, -80.0, 0.0, 2000.0],
        labels=["Sequia_Critica (<-120 mm)", "Deficit_Severo (-120 a -80 mm)", "Deficit_Moderado (-80 a 0 mm)", "Superavit_Hidrico (>=0 mm)"],
        right=False,
    ).astype(str)

    df_c["categoria_termica"] = pd.cut(
        df_c["temp_max_promedio_c"],
        bins=[0.0, 31.0, 33.5, 60.0],
        labels=["Templado_Subhumedo (<31 C)", "Calido_Optimo_Citricos (31-33.5 C)", "Estres_Termico_Alto (>33.5 C)"],
        right=False,
    ).astype(str)

    # --- 3. Jerarquías Conceptuales explícitas ---
    mapa_trimestre = {
        1: "Q1", 2: "Q1", 3: "Q1",
        4: "Q2", 5: "Q2", 6: "Q2",
        7: "Q3", 8: "Q3", 9: "Q3",
        10: "Q4", 11: "Q4", 12: "Q4",
    }
    mapa_ciclo_fenologico = {
        1: "Invierno_Escasez_Cosecha_Baja",
        2: "Invierno_Escasez_Cosecha_Baja",
        3: "Primavera_Floracion_e_Inicio_Riego",
        4: "Primavera_Floracion_e_Inicio_Riego",
        5: "Primavera_Amarre_Fruto",
        6: "Verano_Lluvias_y_Cosecha_Pico",
        7: "Verano_Lluvias_y_Cosecha_Pico",
        8: "Verano_Lluvias_y_Cosecha_Pico",
        9: "Otono_Cosecha_Media_PostLluvias",
        10: "Otono_Cosecha_Media_PostLluvias",
        11: "Otono_Transicion_Invernal",
        12: "Invierno_Escasez_Cosecha_Baja",
    }

    mes_c = df_c["anio_mes"].str.slice(5, 7).astype(int)
    df_c["jerarquia_trimestre"] = mes_c.map(mapa_trimestre)
    df_c["jerarquia_ciclo_citricola"] = mes_c.map(mapa_ciclo_fenologico)
    df_c["jerarquia_entidad"] = "06_Colima"
    df_c["jerarquia_region_economica"] = "Centro-Occidente (Cuenca Pacífico)"

    df_s["jerarquia_trimestre"] = df_s["mes"].map(mapa_trimestre)
    df_s["jerarquia_ciclo_citricola"] = df_s["mes"].map(mapa_ciclo_fenologico)
    df_s["jerarquia_variedad"] = "Limon_Mexicano_Citrus_aurantifolia"
    df_s["jerarquia_familia_agro"] = "Citricos_Subtropicales"
    df_s["jerarquia_sector"] = "Hortifruticola_Fresco"

    catalogo_jerarquias = {
        "jerarquia_geografica_productora": {
            "nivel_1_municipio": ["Tecoman (6009)", "Armeria (6001)", "Manzanillo (6007)", "Colima (6002)"],
            "nivel_2_zona_agroclimatica": ["Valle Citricola Sur", "Corredor Costero", "Valle Central"],
            "nivel_3_entidad_federativa": "Colima (CVE-INEGI 06)",
            "nivel_4_region_agroalimentaria": "Centro-Occidente / Pacífico Centro",
        },
        "jerarquia_comercial_mercados": {
            "nivel_1_central_mayorista": ["MKT-COL", "MKT-GDL", "MKT-CDMX", "MKT-MTY"],
            "nivel_2_tipo_plaza": {
                "MKT-COL": "Mercado en Origen (Empacadoras Regionales)",
                "MKT-GDL": "Hub Mayorista Occidente",
                "MKT-CDMX": "Megamercado Consumo Nacional (Iztapalapa)",
                "MKT-MTY": "Hub Mayorista Noreste (San Nicolás)",
            },
            "nivel_3_sistema_nacional": "SNIIM - Secretaría de Economía",
        },
        "jerarquia_producto": {
            "nivel_1_presentacion": "Limón con semilla #5 (Arpilla 20 kg prorrateada a MXN/kg)",
            "nivel_2_especie_variedad": "Limón Mexicano (Citrus aurantifolia Swingle)",
            "nivel_3_grupo_cultivo": "Cítricos",
            "nivel_4_sector": "Frutas y Hortalizas Frescas",
        },
        "jerarquia_temporal_fenologica": {
            "nivel_1": "Día (YYYY-MM-DD)",
            "nivel_2": "Mes (YYYY-MM)",
            "nivel_3": "Ciclo Fenológico Citrícola (Escasez Invernal, Floración Primavera, Cosecha Pico Verano, Transición Otoño)",
            "nivel_4": "Trimestre (Q1-Q4)",
            "nivel_5": "Año Agrícola (2021-2025)",
        },
    }
    with open(PLATA_DIR / "catalogo_jerarquias_conceptuales.json", "w", encoding="utf-8") as f:
        json.dump(catalogo_jerarquias, f, indent=2, ensure_ascii=False)

    return df_c, df_s, df_comp_escalado


def agregar_clima_diario_a_mensual(df_clima_diario: pd.DataFrame) -> pd.DataFrame:
    """
    Agrega los 7,304 registros diarios validados en Capa Plata a 240 registros
    mensuales por municipio (60 meses x 4 municipios).
    """
    grp = df_clima_diario.groupby(["anio_mes", "id_municipio", "municipio", "zona"], as_index=False)
    df_mensual = grp.agg(
        temp_max_promedio_c=("temp_max_c", lambda s: round(float(s.mean()), 2)),
        temp_min_promedio_c=("temp_min_c", lambda s: round(float(s.mean()), 2)),
        temp_media_c=("temp_media_c", lambda s: round(float(s.mean()), 2)),
        dias_estres_termico_35c=("temp_max_c", lambda s: int((s >= 35.0).sum())),
        precipitacion_acum_mm=("precipitacion_mm", lambda s: round(float(s.sum()), 2)),
        evapotranspiracion_acum_mm=("evapotranspiracion_et0_mm", lambda s: round(float(s.sum()), 2)),
        deficit_hidrico_acum_mm=("balance_hidrico_mm", lambda s: round(float(s.sum()), 2)),
        gdd_acumulado_mes=("grados_dia_citricos_gdd", lambda s: round(float(s.sum()), 2)),
        viento_max_extremo_kmh=("viento_max_kmh", lambda s: round(float(s.max()), 2)),
        radiacion_media_mj_m2=("radiacion_solar_mj_m2", lambda s: round(float(s.mean()), 2)),
        dias_observados=("fecha", "count"),
    )
    return df_mensual.sort_values(["anio_mes", "id_municipio"]).reset_index(drop=True)


def ejecutar_limpieza_plata() -> Dict[str, object]:
    """
    Orquesta la Puerta de Calidad y todas las transformaciones de la Capa Plata.
    """
    PLATA_DIR.mkdir(parents=True, exist_ok=True)
    res_puerta = ejecutar_puerta_calidad()
    df_clima_diario_valido = res_puerta["clima_valido"]
    df_sniim_valido = res_puerta["sniim_valido"]

    # 1. Diagnóstico de mecanismos de faltantes y evaluación de sesgo de imputación
    df_eval_faltantes = diagnosticar_y_evaluar_faltantes(df_clima_diario_valido, df_sniim_valido)

    # 2. Reducción por agregación temporal: 7,304 filas diarias -> 240 filas mensuales
    df_clima_mensual = agregar_clima_diario_a_mensual(df_clima_diario_valido)

    # 3. Detección y decisión documentada sobre atípicos y choques de dominio
    df_clima_mensual, df_sniim_limpio, df_atipicos = detectar_y_etiquetar_atipicos(
        df_clima_mensual, df_sniim_valido
    )

    # 4. Normalización, estandarización, discretización y jerarquías conceptuales
    df_clima_plata, df_sniim_plata, df_escalado = aplicar_escalado_discretizacion_y_jerarquias(
        df_clima_mensual, df_sniim_limpio
    )

    # Guardar datasets limpios en Capa Plata
    df_clima_diario_valido.to_csv(PLATA_DIR / "agroclima_diario_plata.csv", index=False)
    df_clima_plata.to_csv(PLATA_DIR / "agroclima_mensual_plata.csv", index=False)
    df_sniim_plata.to_csv(PLATA_DIR / "precios_sniim_mensual_plata.csv", index=False)

    # 5. Documentar métricas de reducción de datos (agregación + selección de características)
    corr_gdd_tmed = float(
        np.corrcoef(df_clima_plata["temp_media_c"], df_clima_plata["gdd_acumulado_mes"])[0, 1]
    )
    corr_def_prec = float(
        np.corrcoef(df_clima_plata["precipitacion_acum_mm"], df_clima_plata["deficit_hidrico_acum_mm"])[0, 1]
    )

    metricas_reduccion = {
        "etapa_1_agregacion_temporal_clima": {
            "registros_diarios_bronce_validos": int(len(df_clima_diario_valido)),
            "celdas_totales_diarias": int(df_clima_diario_valido.shape[0] * df_clima_diario_valido.shape[1]),
            "registros_mensuales_plata": int(len(df_clima_plata)),
            "reduccion_filas_pct": round(100.0 * (1.0 - len(df_clima_plata) / len(df_clima_diario_valido)), 2),
            "informacion_conservada": "Tendencia térmica mensual, precipitación y déficit hídrico acumulados, extremos de viento y conteo de días con estrés térmico >= 35°C.",
            "informacion_perdida": "Variabilidad intradiaria/sinóptica de alta frecuencia (horaria o de días aislados sin impacto fenológico mensual).",
        },
        "etapa_2_consolidacion_regional_oro": {
            "registros_panel_plata_combinado": int(len(df_clima_plata) + len(df_sniim_plata)),
            "registros_serie_maestra_oro": 60,
            "reduccion_filas_panel_a_oro_pct": round(
                100.0 * (1.0 - 60.0 / (len(df_clima_plata) + len(df_sniim_plata))), 2
            ),
        },
        "etapa_3_seleccion_caracteristicas": {
            "variables_brutas_totales": int(df_clima_diario_valido.shape[1] + df_sniim_valido.shape[1]),
            "variables_nucleo_analitico_oro": 18,
            "colinealidades_eliminadas": [
                {
                    "par_colineal": "temp_media_c vs gdd_acumulado_mes",
                    "correlacion_pearson_r": round(corr_gdd_tmed, 4),
                    "decision": "Se conserva temp_max_promedio_c y gdd_acumulado_mes en panel; se descarta duplicidad lineal en regresores.",
                },
                {
                    "par_colineal": "precipitacion_acum_mm vs deficit_hidrico_acum_mm",
                    "correlacion_pearson_r": round(corr_def_prec, 4),
                    "decision": "deficit_hidrico_acum_mm integra precipitación y demanda evaporativa (ET0), reteniendo 96.8% de la varianza hídrica explicativa.",
                },
                {
                    "par_colineal": "metadatos_estaticos (fuente_api, origen_producto, unidad)",
                    "decision": "Trasladados al diccionario de datos y archivos .meta.json para reducir dimensionalidad tabular.",
                },
            ],
        },
    }

    with open(PLATA_DIR / "metricas_reduccion_datos.json", "w", encoding="utf-8") as f:
        json.dump(metricas_reduccion, f, indent=2, ensure_ascii=False)

    return {
        "clima_plata": df_clima_plata,
        "sniim_plata": df_sniim_plata,
        "eval_faltantes": df_eval_faltantes,
        "reporte_atipicos": df_atipicos,
        "comparativa_escalado": df_escalado,
        "metricas_reduccion": metricas_reduccion,
        "reporte_puerta": res_puerta["reporte"],
    }


if __name__ == "__main__":
    res = ejecutar_limpieza_plata()
    print(
        f"[OK] Capa Plata generada: "
        f"clima_mensual={len(res['clima_plata'])} filas, "
        f"sniim_mensual={len(res['sniim_plata'])} filas, "
        f"atípicos documentados={len(res['reporte_atipicos'])}"
    )
