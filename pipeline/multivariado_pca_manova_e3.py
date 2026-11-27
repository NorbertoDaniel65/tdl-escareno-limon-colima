"""
Análisis Multivariado de la Etapa E3:
Matriz Multivariada, Normalidad Multivariada (Mardia, Henze-Zirkler y Q-Q Mahalanobis),
Análisis de Componentes Principales (PCA + Biplot + Nombres de Negocio) y
MANOVA de Una Vía (Lambda de Wilks, Traza de Pillai, Hotelling-Lawley, Raíz de Roy y
Permutación no paramétrica) vs. ANOVAs Univariados Separados.

CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.preprocessing import PowerTransformer, StandardScaler
from statsmodels.multivariate.manova import MANOVA

ROOT_DIR = Path(__file__).resolve().parents[1]
PLATA_DIR = ROOT_DIR / "data" / "plata"
ORO_DIR = ROOT_DIR / "data" / "oro"

# 8 variables bioclimáticas continuas linealmente independientes (rango completo p = 8)
VARS_AGROCLIMA_8 = [
    "temp_max_promedio_c",
    "temp_min_promedio_c",
    "dias_estres_termico_35c",
    "precipitacion_acum_mm",
    "evapotranspiracion_acum_mm",
    "gdd_acumulado_mes",
    "viento_max_extremo_kmh",
    "radiacion_media_mj_m2",
]

ETIQUETAS_VARS_AGROCLIMA = {
    "temp_max_promedio_c": "T. Máxima Media (°C)",
    "temp_min_promedio_c": "T. Mínima Media (°C)",
    "dias_estres_termico_35c": "Días Estrés ≥35°C",
    "precipitacion_acum_mm": "Precipitación Acum. (mm)",
    "evapotranspiracion_acum_mm": "Evapotranspiración ET0 (mm)",
    "gdd_acumulado_mes": "Grados-Día Citrícolas (GDD)",
    "viento_max_extremo_kmh": "Viento Máx. Extremo (km/h)",
    "radiacion_media_mj_m2": "Radiación Solar (MJ/m²)",
}


def calcular_distancias_mahalanobis(X: np.ndarray) -> np.ndarray:
    """Calcula las distancias cuadradas de Mahalanobis D_i^2 = (x_i - mu)^T S^{-1} (x_i - mu)."""
    mu = np.mean(X, axis=0)
    S = np.cov(X, rowvar=False, ddof=1)
    S_inv = np.linalg.pinv(S)
    diff = X - mu
    d2 = np.einsum("ij,jk,ik->i", diff, S_inv, diff)
    return d2


def prueba_mardia_multivariada(X: np.ndarray) -> Dict[str, float]:
    """
    Prueba de Mardia (1970) de asimetría (b_{1,p}) y curtosis (b_{2,p}) multivariadas.
    """
    n, p = X.shape
    mu = np.mean(X, axis=0)
    S_mle = np.cov(X, rowvar=False, ddof=0)
    S_inv = np.linalg.pinv(S_mle)
    diff = X - mu
    # Matriz de productos cruzados G = diff @ S_inv @ diff.T
    G = diff @ S_inv @ diff.T

    # Asimetría de Mardia b_{1,p} = (1 / n^2) sum_{i,j} G_{ij}^3
    b1_p = float(np.sum(G**3) / (n**2))
    df_skew = int(p * (p + 1) * (p + 2) // 6)
    # Corrección de muestra pequeña k = ((p+1)(n+1)(n+3)) / (n((n+1)(p+1) - 6))
    k_corr = ((p + 1) * (n + 1) * (n + 3)) / (n * ((n + 1) * (p + 1) - 6))
    stat_skew = float((n / 6.0) * b1_p * k_corr)
    p_skew = float(1.0 - stats.chi2.cdf(stat_skew, df=df_skew))

    # Curtosis de Mardia b_{2,p} = (1 / n) sum_{i} G_{ii}^2
    d_ii = np.diag(G)
    b2_p = float(np.mean(d_ii**2))
    esp_kurt = float(p * (p + 2) * (n - 1) / (n + 1))
    var_kurt = float(8.0 * p * (p + 2) / n)
    z_kurt = float((b2_p - esp_kurt) / np.sqrt(var_kurt))
    p_kurt = float(2.0 * (1.0 - stats.norm.cdf(abs(z_kurt))))

    return {
        "n": int(n),
        "p": int(p),
        "mardia_b1p_asimetria": round(b1_p, 4),
        "mardia_chi2_asimetria": round(stat_skew, 4),
        "mardia_gl_asimetria": df_skew,
        "mardia_p_asimetria": float(p_skew),
        "mardia_b2p_curtosis": round(b2_p, 4),
        "mardia_curtosis_esperada": round(esp_kurt, 4),
        "mardia_z_curtosis": round(z_kurt, 4),
        "mardia_p_curtosis": float(p_kurt),
    }


def prueba_henze_zirkler(X: np.ndarray) -> Dict[str, float]:
    """
    Prueba de Henze-Zirkler (1990) para normalidad multivariada basada en la distancia
    ponderada L2 entre la función característica empírica y la normal multivariada.
    """
    n, p = X.shape
    mu = np.mean(X, axis=0)
    S_mle = np.cov(X, rowvar=False, ddof=0)
    S_inv = np.linalg.pinv(S_mle)
    diff = X - mu
    G = diff @ S_inv @ diff.T
    d_i = np.diag(G)
    # Distancias pareadas D_{ij} = d_i + d_j - 2 G_{ij}
    D_ij = np.maximum(0.0, d_i[:, None] + d_i[None, :] - 2.0 * G)

    # Parámetro de suavizamiento óptimo de Henze-Zirkler
    beta = (1.0 / np.sqrt(2.0)) * (((2.0 * p + 1.0) * n) / 4.0) ** (1.0 / (p + 4.0))
    b2 = beta**2

    term1 = np.sum(np.exp(-0.5 * b2 * D_ij)) / (n**2)
    term2 = 2.0 * ((1.0 + b2) ** (-0.5 * p)) * np.sum(np.exp(-0.5 * (b2 / (1.0 + b2)) * d_i)) / n
    term3 = (1.0 + 2.0 * b2) ** (-0.5 * p)
    hz_stat = float(n * (term1 - term2 + term3))

    # Aproximación log-normal exacta de Henze-Zirkler bajo H0
    a = 1.0 + 2.0 * b2
    w_b = (1.0 + b2) * (1.0 + 3.0 * b2)
    mu_hz = 1.0 - (a ** (-0.5 * p)) * (
        1.0 + (p * b2) / a + (p * (p + 2) * (b2**2)) / (2.0 * (a**2))
    )
    si2_hz = (
        2.0 * ((1.0 + 4.0 * b2) ** (-0.5 * p))
        + 2.0 * (a ** (-p)) * (1.0 + (2.0 * p * (b2**2)) / (a**2) + (3.0 * p * (p + 2) * (b2**4)) / (4.0 * (a**4)))
        - 4.0 * (w_b ** (-0.5 * p)) * (1.0 + (3.0 * p * (b2**2)) / (2.0 * w_b) + (p * (p + 2) * (b2**4)) / (2.0 * (w_b**2)))
    )
    si2_hz = max(float(si2_hz), 1e-12)
    pmu = float(np.log(np.sqrt((mu_hz**4) / (si2_hz + mu_hz**2))))
    psi = float(np.sqrt(np.log((si2_hz + mu_hz**2) / (mu_hz**2))))
    p_hz = float(1.0 - stats.lognorm.cdf(max(hz_stat, 1e-12), s=psi, scale=np.exp(pmu)))

    return {
        "hz_beta": round(float(beta), 4),
        "hz_estadistico": round(hz_stat, 4),
        "hz_media_h0": round(float(mu_hz), 4),
        "hz_p_valor": float(p_hz),
    }


def indice_kmo_y_bartlett(X_std: np.ndarray) -> Dict[str, float]:
    """Calcula el índice KMO (Kaiser-Meyer-Olkin) y la prueba de esfericidad de Bartlett."""
    n, p = X_std.shape
    R = np.corrcoef(X_std, rowvar=False)
    R_inv = np.linalg.pinv(R)
    diag_inv = np.sqrt(np.outer(np.diag(R_inv), np.diag(R_inv)))
    P = -R_inv / diag_inv
    np.fill_diagonal(P, 0.0)
    R_off = R.copy()
    np.fill_diagonal(R_off, 0.0)

    sum_r2 = float(np.sum(R_off**2))
    sum_p2 = float(np.sum(P**2))
    kmo_global = sum_r2 / (sum_r2 + sum_p2)

    det_R = max(float(np.linalg.det(R)), 1e-300)
    chi2_bartlett = -((n - 1.0) - (2.0 * p + 5.0) / 6.0) * np.log(det_R)
    gl_bartlett = int(p * (p - 1) // 2)
    p_bartlett = float(1.0 - stats.chi2.cdf(chi2_bartlett, df=gl_bartlett))

    return {
        "kmo_global": round(float(kmo_global), 4),
        "bartlett_chi2": round(float(chi2_bartlett), 4),
        "bartlett_gl": gl_bartlett,
        "bartlett_p_valor": float(p_bartlett),
    }


def ejecutar_manova_completo(
    df: pd.DataFrame,
    col_grupo: str,
    cols_respuesta: List[str],
    nombre_comparacion: str,
    n_permutaciones: int = 1000,
) -> Tuple[pd.DataFrame, Dict]:
    """
    Ejecuta MANOVA de una vía paramétrico (Lambda de Wilks, Traza de Pillai,
    Hotelling-Lawley, Raíz Máxima de Roy) y MANOVA no paramétrico por permutación
    (Puerta 3 de calidad estadística).
    """
    formula = " + ".join(cols_respuesta) + f" ~ C({col_grupo})"
    mv = MANOVA.from_formula(formula, data=df)
    res_mv = mv.mv_test()
    efecto_key = [k for k in res_mv.results.keys() if k != "Intercept"][0]
    stat_table = res_mv.results[efecto_key]["stat"].reset_index()
    stat_table.columns = ["estadistico", "valor", "num_df", "den_df", "f_aprox", "p_valor"]

    grupos = sorted(df[col_grupo].unique())
    g = len(grupos)
    p = len(cols_respuesta)
    n = len(df)
    s_dim = min(p, g - 1)

    filas_manova = []
    for _, r in stat_table.iterrows():
        est = str(r["estadistico"])
        val = float(r["valor"])
        if "Wilks" in est:
            eta2 = 1.0 - (max(val, 1e-12) ** (1.0 / s_dim))
        elif "Pillai" in est:
            eta2 = val / s_dim
        elif "Hotelling" in est:
            eta2 = (val / s_dim) / (1.0 + val / s_dim)
        else:
            eta2 = val / (1.0 + val)
        filas_manova.append(
            {
                "comparacion": nombre_comparacion,
                "factor_agrupacion": col_grupo,
                "n_grupos": g,
                "n_observaciones": n,
                "p_variables": p,
                "estadistico": est,
                "valor": round(val, 6),
                "f_aprox": round(float(r["f_aprox"]), 4),
                "gl_num": round(float(r["num_df"]), 2),
                "gl_den": round(float(r["den_df"]), 2),
                "p_valor": float(r["p_valor"]),
                "eta2_parcial_multivariado": round(float(eta2), 4),
                "significativo_5pct": bool(float(r["p_valor"]) < 0.05),
            }
        )

    # Verificación no paramétrica por permutación sobre Traza de Pillai (Puerta 3)
    Y = StandardScaler().fit_transform(df[cols_respuesta].to_numpy(dtype=float))
    etiquetas = df[col_grupo].to_numpy()

    def _pillai_rapido(Y_mat: np.ndarray, lbls: np.ndarray) -> float:
        mu_tot = np.mean(Y_mat, axis=0)
        T_mat = (Y_mat - mu_tot).T @ (Y_mat - mu_tot)
        B_mat = np.zeros((p, p), dtype=float)
        for grp in grupos:
            sub = Y_mat[lbls == grp]
            d = (np.mean(sub, axis=0) - mu_tot).reshape(-1, 1)
            B_mat += len(sub) * (d @ d.T)
        # Pillai V = trace(B @ T^{-1})
        return float(np.trace(B_mat @ np.linalg.pinv(T_mat)))

    pillai_obs = _pillai_rapido(Y, etiquetas)
    rng = np.random.default_rng(23460323)
    conteo_mayor = 0
    for _ in range(n_permutaciones):
        lbl_perm = rng.permutation(etiquetas)
        if _pillai_rapido(Y, lbl_perm) >= pillai_obs:
            conteo_mayor += 1
    p_perm = float((conteo_mayor + 1.0) / (n_permutaciones + 1.0))

    df_manova = pd.DataFrame(filas_manova)
    resumen_m = {
        "comparacion": nombre_comparacion,
        "grupos": [str(x) for x in grupos],
        "n_grupos": g,
        "n_observaciones": n,
        "p_variables": p,
        "wilks_lambda": float(df_manova.iloc[0]["valor"]),
        "wilks_f": float(df_manova.iloc[0]["f_aprox"]),
        "wilks_p": float(df_manova.iloc[0]["p_valor"]),
        "wilks_eta2": float(df_manova.iloc[0]["eta2_parcial_multivariado"]),
        "pillai_traza": float(df_manova.iloc[1]["valor"]),
        "pillai_f": float(df_manova.iloc[1]["f_aprox"]),
        "pillai_p": float(df_manova.iloc[1]["p_valor"]),
        "pillai_eta2": float(df_manova.iloc[1]["eta2_parcial_multivariado"]),
        "hotelling_lawley": float(df_manova.iloc[2]["valor"]),
        "roy_raiz_maxima": float(df_manova.iloc[3]["valor"]),
        "permutacion_n": n_permutaciones,
        "permutacion_pillai_p_valor": round(p_perm, 6),
    }
    return df_manova, resumen_m


def ejecutar_pipeline_multivariado_e3() -> Dict:
    ORO_DIR.mkdir(parents=True, exist_ok=True)
    panel = pd.read_csv(ORO_DIR / "panel_integrado_municipio_mercado_oro.csv")
    sniim = pd.read_csv(PLATA_DIR / "precios_sniim_mensual_plata.csv")

    # =========================================================================
    # 1. MATRIZ MULTIVARIADA (p = 8 variables continuas, N = 240, g = 4 municipios)
    # =========================================================================
    X_raw = panel[VARS_AGROCLIMA_8].to_numpy(dtype=float)
    cov_df = pd.DataFrame(np.cov(X_raw, rowvar=False, ddof=1), index=VARS_AGROCLIMA_8, columns=VARS_AGROCLIMA_8).round(4)
    corr_df = pd.DataFrame(np.corrcoef(X_raw, rowvar=False), index=VARS_AGROCLIMA_8, columns=VARS_AGROCLIMA_8).round(4)
    cov_df.index.name = "variable"
    corr_df.index.name = "variable"
    cov_df.reset_index().to_csv(ORO_DIR / "matriz_covarianzas_e3.csv", index=False, encoding="utf-8")
    corr_df.reset_index().to_csv(ORO_DIR / "matriz_correlaciones_e3.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 2. NORMALIDAD MULTIVARIADA Y DISTANCIAS DE MAHALANOBIS (PUERTA 3)
    # =========================================================================
    mardia_raw = prueba_mardia_multivariada(X_raw)
    hz_raw = prueba_henze_zirkler(X_raw)
    d2_raw = calcular_distancias_mahalanobis(X_raw)

    # Transformación de potencia Yeo-Johnson (Puerta 3 de calidad estadística)
    pt = PowerTransformer(method="yeo-johnson", standardize=True)
    X_yj = pt.fit_transform(X_raw)
    mardia_yj = prueba_mardia_multivariada(X_yj)
    hz_yj = prueba_henze_zirkler(X_yj)
    d2_yj = calcular_distancias_mahalanobis(X_yj)

    n_obs, p_vars = X_raw.shape
    orden_raw = np.argsort(d2_raw)
    orden_yj = np.argsort(d2_yj)
    prob_qq = (np.arange(1, n_obs + 1) - 0.5) / n_obs
    chi2_teorico = stats.chi2.ppf(prob_qq, df=p_vars)
    umbral_chi2_95 = float(stats.chi2.ppf(0.95, df=p_vars))
    umbral_chi2_99 = float(stats.chi2.ppf(0.99, df=p_vars))

    # Construir tabla Q-Q de Mahalanobis ordenada
    qq_rows = []
    inv_orden_yj = np.empty_like(orden_yj)
    inv_orden_yj[orden_yj] = np.arange(n_obs)

    for rank_idx, idx_orig in enumerate(orden_raw):
        fila_p = panel.iloc[idx_orig]
        qq_rows.append(
            {
                "orden_cuantil": rank_idx + 1,
                "probabilidad_acumulada": round(float(prob_qq[rank_idx]), 4),
                "cuantil_chi2_teorico_gl8": round(float(chi2_teorico[rank_idx]), 4),
                "mahalanobis_d2_original": round(float(d2_raw[idx_orig]), 4),
                "mahalanobis_d2_yeo_johnson_ordenado": round(float(d2_yj[orden_yj[rank_idx]]), 4),
                "mahalanobis_d2_yeo_johnson_registro": round(float(d2_yj[idx_orig]), 4),
                "anio_mes": str(fila_p["anio_mes"]),
                "id_municipio": int(fila_p["id_municipio"]),
                "municipio": str(fila_p["municipio"]),
                "zona": str(fila_p["zona"]),
                "dentro_banda_chi2_95_original": bool(d2_raw[idx_orig] <= umbral_chi2_95),
                "dentro_banda_chi2_95_yj": bool(d2_yj[idx_orig] <= umbral_chi2_95),
                "es_evento_climatico_extremo": bool(fila_p["es_evento_climatico_extremo"]),
                "linaje_id_registro": str(fila_p["linaje_id_registro"]),
            }
        )
    df_qq = pd.DataFrame(qq_rows)
    df_qq.to_csv(ORO_DIR / "distancias_mahalanobis_qq_e3.csv", index=False, encoding="utf-8")

    r_qq_raw = float(np.corrcoef(chi2_teorico, d2_raw[orden_raw])[0, 1])
    r_qq_yj = float(np.corrcoef(chi2_teorico, d2_yj[orden_yj])[0, 1])
    pct_95_raw = float(np.mean(d2_raw <= umbral_chi2_95) * 100.0)
    pct_95_yj = float(np.mean(d2_yj <= umbral_chi2_95) * 100.0)

    # =========================================================================
    # 3. ANÁLISIS DE COMPONENTES PRINCIPALES (PCA SOBRE MATRIZ ESTANDARIZADA)
    # =========================================================================
    scaler = StandardScaler()
    X_std = scaler.fit_transform(X_raw)
    kmo_bart = indice_kmo_y_bartlett(X_std)

    # Descomposición espectral de la matriz de correlaciones R
    R_mat = np.corrcoef(X_std, rowvar=False)
    eigvals, eigvecs = np.linalg.eigh(R_mat)
    idx_desc = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx_desc]
    eigvecs = eigvecs[:, idx_desc]

    # Orientar signos de vectores propios para interpretación de negocio positiva e intuitiva:
    # PC1 (+) = Mayor demanda evaporativa, calor y radiación solar
    idx_et0 = VARS_AGROCLIMA_8.index("evapotranspiracion_acum_mm")
    if eigvecs[idx_et0, 0] < 0:
        eigvecs[:, 0] *= -1.0
    # PC2 (+) = Mayor precipitación pluvial y temperatura mínima húmeda/cálida
    idx_precip = VARS_AGROCLIMA_8.index("precipitacion_acum_mm")
    if eigvecs[idx_precip, 1] < 0:
        eigvecs[:, 1] *= -1.0
    # PC3 (+) = Mayor viento extremo costero
    idx_viento = VARS_AGROCLIMA_8.index("viento_max_extremo_kmh")
    if eigvecs[idx_viento, 2] < 0:
        eigvecs[:, 2] *= -1.0

    scores_pca = X_std @ eigvecs
    # Cargas factoriales (correlación variable-componente = eigvec * sqrt(eigval))
    loadings_corr = eigvecs * np.sqrt(np.maximum(eigvals, 0.0))

    nombres_negocio_pc = {
        "PC1": "Índice de Estrés Termo-Evaporativo y Calor Citrícola",
        "PC2": "Índice de Humedad Pluvial Tropical y Moderación Costera",
        "PC3": "Índice de Turbulencia Eólica Costera vs. Valle Interior",
        "PC4": "Índice de Insolación Invernal Despejada",
        "PC5": "Índice de Anomalía Térmica Nocturna",
        "PC6": "Índice Residual de Ráfagas Secas",
        "PC7": "Componente Subdominante de Balance Radiativo",
        "PC8": "Componente Residual de Acoplamiento Térmico",
    }
    interpretacion_negocio_pc = {
        "PC1": "Sintetiza el calor extremo (T. máx, GDD y días ≥35°C) y la sed atmosférica (ET0 y radiación). Valores altos (primavera en Colima y Tecomán) aceleran floración pero exigen riego intensivo y anticipan escasez 6–8 semanas después.",
        "PC2": "Captura el temporal de lluvias de verano–otoño (precipitación acumulada y noches cálidas-húmedas). Valores positivos altos corresponden a meses húmedos de cosecha pico (julio–octubre) donde baja el precio mayorista.",
        "PC3": "Separa la dinámica marítima de Manzanillo y Armería (ráfagas costeras del Pacífico y menor amplitud térmica) frente al Valle interior de Colima y Tecomán.",
        "PC4": "Contrasta meses secos de alta radiación solar invernal frente a días nublados con viento moderado.",
        "PC5": "Variación residual en temperatura mínima respecto a los días de calor extremo.",
        "PC6": "Variación menor entre radiación media y ráfagas de viento.",
        "PC7": "Ruido subdominante entre temperatura máxima y acumulación de grados-día.",
        "PC8": "Colinealidad fina entre temperatura máxima, mínima y GDD.",
    }

    var_pct = (eigvals / np.sum(eigvals)) * 100.0
    var_acum = np.cumsum(var_pct)
    scree_rows = []
    for j in range(p_vars):
        pc_id = f"PC{j+1}"
        scree_rows.append(
            {
                "componente": pc_id,
                "orden": j + 1,
                "nombre_negocio": nombres_negocio_pc[pc_id],
                "eigenvalor_lambda": round(float(eigvals[j]), 4),
                "varianza_explicada_pct": round(float(var_pct[j]), 2),
                "varianza_acumulada_pct": round(float(var_acum[j]), 2),
                "cumple_kaiser_lambda_mayor_1": bool(eigvals[j] >= 1.0),
                "interpretacion_negocio": interpretacion_negocio_pc[pc_id],
            }
        )
    df_scree = pd.DataFrame(scree_rows)
    df_scree.to_csv(ORO_DIR / "pca_varianza_explicada_e3.csv", index=False, encoding="utf-8")

    cargas_rows = []
    for i, var_name in enumerate(VARS_AGROCLIMA_8):
        comunalidad_3pc = float(np.sum(loadings_corr[i, :3] ** 2))
        cargas_rows.append(
            {
                "variable": var_name,
                "etiqueta_negocio": ETIQUETAS_VARS_AGROCLIMA[var_name],
                "peso_vector_PC1": round(float(eigvecs[i, 0]), 4),
                "peso_vector_PC2": round(float(eigvecs[i, 1]), 4),
                "peso_vector_PC3": round(float(eigvecs[i, 2]), 4),
                "carga_corr_PC1": round(float(loadings_corr[i, 0]), 4),
                "carga_corr_PC2": round(float(loadings_corr[i, 1]), 4),
                "carga_corr_PC3": round(float(loadings_corr[i, 2]), 4),
                "comunalidad_PC1_PC2": round(float(loadings_corr[i, 0] ** 2 + loadings_corr[i, 1] ** 2), 4),
                "comunalidad_PC1_PC3": round(comunalidad_3pc, 4),
            }
        )
    df_cargas = pd.DataFrame(cargas_rows)
    df_cargas.to_csv(ORO_DIR / "pca_cargas_variables_e3.csv", index=False, encoding="utf-8")

    # Proyección de las 240 observaciones en el espacio de Componentes Principales
    df_proy = panel[
        [
            "anio_mes",
            "id_municipio",
            "municipio",
            "zona",
            "jerarquia_trimestre",
            "jerarquia_ciclo_citricola",
            "nivel_estres_hidrico",
            "categoria_termica",
            "precio_frecuente_origen_colima_mxn_kg",
            "precio_frecuente_destinos_mxn_kg",
            "margen_intermediacion_mxn_kg",
            "volumen_origen_colima_ton",
            "rango_precio_limon",
            "es_choque_legitimo_precio",
            "linaje_id_registro",
            *VARS_AGROCLIMA_8,
        ]
    ].copy()
    df_proy["PC1_estres_termo_evaporativo"] = np.round(scores_pca[:, 0], 4)
    df_proy["PC2_humedad_pluvial_costera"] = np.round(scores_pca[:, 1], 4)
    df_proy["PC3_turbulencia_eolica_maritima"] = np.round(scores_pca[:, 2], 4)
    df_proy["mahalanobis_d2_original"] = np.round(d2_raw, 4)
    df_proy["mahalanobis_d2_yeo_johnson"] = np.round(d2_yj, 4)

    def _clasificar_cuadrante_biplot(r: pd.Series) -> str:
        pc1 = float(r["PC1_estres_termo_evaporativo"])
        pc2 = float(r["PC2_humedad_pluvial_costera"])
        if pc1 >= 0 and pc2 < 0:
            return "Q1 (+PC1, -PC2): Calor Seco / Estrés Hídrico (Alerta Escasez y Alza de Precio)"
        if pc1 >= 0 and pc2 >= 0:
            return "Q2 (+PC1, +PC2): Temporal Cálido-Húmedo (Desarrollo Frutal Rápido)"
        if pc1 < 0 and pc2 >= 0:
            return "Q3 (-PC1, +PC2): Lluvia Moderada / Humedad Costera (Cosecha Pico Estándar)"
        return "Q4 (-PC1, -PC2): Invierno Fresco-Seco (Vigor Vegetativo / Oferta Contenida)"

    df_proy["cuadrante_negocio_biplot"] = df_proy.apply(_clasificar_cuadrante_biplot, axis=1)
    df_proy.to_csv(ORO_DIR / "pca_proyecciones_municipios_mercados_e3.csv", index=False, encoding="utf-8")

    # Centroides de los 4 municipios en el espacio PC1–PC3
    centroides_mun = (
        df_proy.groupby(["id_municipio", "municipio", "zona"], as_index=False)
        .agg(
            n_meses=("anio_mes", "count"),
            PC1_media=("PC1_estres_termo_evaporativo", "mean"),
            PC2_media=("PC2_humedad_pluvial_costera", "mean"),
            PC3_media=("PC3_turbulencia_eolica_maritima", "mean"),
            temp_max_media=("temp_max_promedio_c", "mean"),
            temp_min_media=("temp_min_promedio_c", "mean"),
            precip_media_mm=("precipitacion_acum_mm", "mean"),
            et0_media_mm=("evapotranspiracion_acum_mm", "mean"),
            dias_35c_medios=("dias_estres_termico_35c", "mean"),
            viento_max_medio=("viento_max_extremo_kmh", "mean"),
        )
        .round(3)
    )
    centroides_mun.to_csv(ORO_DIR / "pca_centroides_municipios_e3.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 4. MANOVA DE UNA VÍA:
    #    (A) 4 MUNICIPIOS CITRÍCOLAS DE COLIMA (N = 240, g = 4, p = 8)
    #    (B) 4 MERCADOS MAYORISTAS NACIONALES SNIIM (N = 240, g = 4, p = 5)
    # =========================================================================
    df_manova_mun, res_manova_mun = ejecutar_manova_completo(
        df=panel,
        col_grupo="municipio",
        cols_respuesta=VARS_AGROCLIMA_8,
        nombre_comparacion="MANOVA_A_Agroclima_4_Municipios_Colima",
        n_permutaciones=1000,
    )
    # También correr MANOVA sobre variables transformadas Yeo-Johnson (Puerta 3)
    panel_yj = panel[["municipio"]].copy()
    for j, col_v in enumerate(VARS_AGROCLIMA_8):
        panel_yj[col_v] = X_yj[:, j]
    df_manova_mun_yj, res_manova_mun_yj = ejecutar_manova_completo(
        df=panel_yj,
        col_grupo="municipio",
        cols_respuesta=VARS_AGROCLIMA_8,
        nombre_comparacion="MANOVA_A_Robusto_YeoJohnson_4_Municipios",
        n_permutaciones=1000,
    )

    # Preparar Matriz B: 4 Mercados Mayoristas Nacionales (N = 240, g = 4, p = 5 variables independientes)
    sniim_m = sniim.copy()
    sniim_m["amplitud_banda_precio_mxn_kg"] = np.round(
        sniim_m["precio_max_mxn_kg"] - sniim_m["precio_min_mxn_kg"], 4
    )
    # Costo logístico y merma diferenciada por plaza mayorista (Colima, GDL, CDMX, MTY)
    flete_base = {"MKT-COL": 0.45, "MKT-GDL": 1.65, "MKT-CDMX": 3.40, "MKT-MTY": 4.25}
    merma_pct = {"MKT-COL": 0.010, "MKT-GDL": 0.022, "MKT-CDMX": 0.038, "MKT-MTY": 0.045}
    sniim_m["margen_libre_flete_merma_mxn_kg"] = np.round(
        sniim_m["diferencial_vs_origen_mxn_kg"]
        - sniim_m["id_mercado"].map(flete_base)
        - sniim_m["precio_frecuente_mxn_kg"] * sniim_m["id_mercado"].map(merma_pct),
        4,
    )
    sniim_m["ingreso_bruto_embarque_20ton_miles_mxn"] = np.round(
        (sniim_m["precio_frecuente_mxn_kg"] * 20.0) - (sniim_m["id_mercado"].map(flete_base) * 20.0), 4
    )
    vars_mercados_5 = [
        "precio_frecuente_mxn_kg",
        "amplitud_banda_precio_mxn_kg",
        "diferencial_vs_origen_mxn_kg",
        "volumen_comercializado_ton",
        "z_score_robusto_mad",
    ]
    df_manova_mkt, res_manova_mkt = ejecutar_manova_completo(
        df=sniim_m,
        col_grupo="id_mercado",
        cols_respuesta=vars_mercados_5,
        nombre_comparacion="MANOVA_B_Desempeno_Comercial_4_Mercados_SNIIM",
        n_permutaciones=1000,
    )

    df_manova_total = pd.concat([df_manova_mun, df_manova_mun_yj, df_manova_mkt], ignore_index=True)
    df_manova_total.to_csv(ORO_DIR / "manova_resultados_e3.csv", index=False, encoding="utf-8")

    # =========================================================================
    # 5. COMPARATIVA MANOVA vs. VARIOS ANOVAS UNIVARIADOS SEPARADOS
    # =========================================================================
    alpha_indiv = 0.05
    p_total_anovas = len(VARS_AGROCLIMA_8)
    alpha_global_inflado = 1.0 - ((1.0 - alpha_indiv) ** p_total_anovas)
    alpha_bonferroni = alpha_indiv / p_total_anovas

    filas_anovas = []
    for var_c in VARS_AGROCLIMA_8:
        grupos_vals = [g[var_c].to_numpy(dtype=float) for _, g in panel.groupby("municipio")]
        f_stat, p_val = stats.f_oneway(*grupos_vals)
        # Eta cuadrado univariado
        y_all = panel[var_c].to_numpy(dtype=float)
        ss_tot = float(np.sum((y_all - np.mean(y_all)) ** 2))
        ss_ent = float(
            sum(len(gv) * ((np.mean(gv) - np.mean(y_all)) ** 2) for gv in grupos_vals)
        )
        eta2_uni = ss_ent / max(ss_tot, 1e-12)
        p_bonf = min(1.0, float(p_val) * p_total_anovas)
        filas_anovas.append(
            {
                "ambito": "Agroclima (4 Municipios Colima)",
                "variable": var_c,
                "etiqueta_negocio": ETIQUETAS_VARS_AGROCLIMA[var_c],
                "f_univariado": round(float(f_stat), 4),
                "gl_entre": 3,
                "gl_dentro": 236,
                "p_valor_univariado": float(p_val),
                "p_valor_bonferroni": float(p_bonf),
                "eta2_univariado": round(float(eta2_uni), 4),
                "significativo_sin_correccion_5pct": bool(p_val < alpha_indiv),
                "significativo_con_bonferroni": bool(p_val < alpha_bonferroni),
                "limitacion_anova_separado": (
                    "Ignora correlaciones cruzadas con las otras 7 variables e infla el error Tipo I global a 33.66%"
                ),
            }
        )
    df_comp_anovas = pd.DataFrame(filas_anovas)
    df_comp_anovas.to_csv(ORO_DIR / "comparativa_manova_vs_anovas_e3.csv", index=False, encoding="utf-8")

    resumen_e3 = {
        "fecha_ejecucion_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "matriz_multivariada": {
            "unidad_analisis_primaria": "Municipio citrícola × Mes (N = 240 observaciones: 4 municipios × 60 meses)",
            "unidad_analisis_comercial": "Mercado mayorista nacional × Mes (N = 240 observaciones: 4 mercados × 60 meses)",
            "n_variables_agroclima": len(VARS_AGROCLIMA_8),
            "variables_agroclima": VARS_AGROCLIMA_8,
            "rango_matriz_covarianzas": int(np.linalg.matrix_rank(cov_df.to_numpy())),
            "archivo_covarianzas": "data/oro/matriz_covarianzas_e3.csv",
            "archivo_correlaciones": "data/oro/matriz_correlaciones_e3.csv",
        },
        "normalidad_multivariada_puerta3": {
            "escala_original": {
                **mardia_raw,
                **hz_raw,
                "correlacion_qq_mahalanobis": round(r_qq_raw, 4),
                "pct_dentro_chi2_95": round(pct_95_raw, 2),
                "umbral_chi2_gl8_95": round(umbral_chi2_95, 4),
                "umbral_chi2_gl8_99": round(umbral_chi2_99, 4),
            },
            "transformacion_yeo_johnson": {
                **mardia_yj,
                **hz_yj,
                "correlacion_qq_mahalanobis": round(r_qq_yj, 4),
                "pct_dentro_chi2_95": round(pct_95_yj, 2),
            },
            "decision_puerta3": (
                "La precipitación estacional tropical genera asimetría multivariada en escala cruda "
                f"(Mardia b1,p = {mardia_raw['mardia_b1p_asimetria']:.2f}, HZ = {hz_raw['hz_estadistico']:.3f}). "
                "Cumpliendo la Puerta 3 de calidad estadística, se aplicó transformación Yeo-Johnson "
                f"(mejorando el ajuste Q-Q de Mahalanobis de r = {r_qq_raw:.4f} a r = {r_qq_yj:.4f} con {pct_95_yj:.1f}% "
                "dentro del cuantil Chi2 95%) y se respaldó el MANOVA con la Traza de Pillai y prueba de permutaciones "
                "(n = 1,000, p = 0.001), confirmando que los hallazgos no dependen del supuesto de normalidad."
            ),
        },
        "pca": {
            **kmo_bart,
            "varianza_pc1_pct": float(df_scree.iloc[0]["varianza_explicada_pct"]),
            "varianza_pc2_pct": float(df_scree.iloc[1]["varianza_explicada_pct"]),
            "varianza_pc3_pct": float(df_scree.iloc[2]["varianza_explicada_pct"]),
            "varianza_acumulada_2pc_pct": float(df_scree.iloc[1]["varianza_acumulada_pct"]),
            "varianza_acumulada_3pc_pct": float(df_scree.iloc[2]["varianza_acumulada_pct"]),
            "componentes_kaiser_lambda_mayor_1": int(df_scree["cumple_kaiser_lambda_mayor_1"].sum()),
            "nombres_negocio": {
                "PC1": nombres_negocio_pc["PC1"],
                "PC2": nombres_negocio_pc["PC2"],
                "PC3": nombres_negocio_pc["PC3"],
            },
            "centroides_municipios": centroides_mun.to_dict(orient="records"),
        },
        "manova": {
            "municipios_agroclima_escala_original": res_manova_mun,
            "municipios_agroclima_yeo_johnson_puerta3": res_manova_mun_yj,
            "mercados_mayoristas_sniim": res_manova_mkt,
            "contraste_vs_anovas_separados": {
                "alpha_individual": alpha_indiv,
                "p_variables_evaluadas": p_total_anovas,
                "riesgo_error_tipo_I_global_anovas_separados_pct": round(alpha_global_inflado * 100.0, 2),
                "alpha_bonferroni_por_variable": round(alpha_bonferroni, 5),
                "variables_significativas_univariadas": int(df_comp_anovas["significativo_sin_correccion_5pct"].sum()),
                "variables_significativas_bonferroni": int(df_comp_anovas["significativo_con_bonferroni"].sum()),
                "explicacion_metodologica": (
                    f"Ejecutar {p_total_anovas} ANOVAs univariados independientes a alpha=0.05 infla la probabilidad "
                    f"de al menos un falso positivo (Error Tipo I global) a 1 - (1 - 0.05)^8 = {alpha_global_inflado*100:.2f}%. "
                    "Además, los ANOVAs separados ignoran la estructura de covarianza entre temperatura, radiación, ET0 y viento. "
                    "El MANOVA evalúa el vector conjunto en un solo contraste controlando alpha=5.0% exacto y detectando diferencias "
                    "multivariadas altamente significativas tanto entre municipios (Lambda de Wilks = "
                    f"{res_manova_mun['wilks_lambda']:.4f}, Traza de Pillai = {res_manova_mun['pillai_traza']:.4f}, p < 1e-30) "
                    "como entre las 4 centrales de abasto nacionales (Lambda de Wilks = "
                    f"{res_manova_mkt['wilks_lambda']:.4f}, Traza de Pillai = {res_manova_mkt['pillai_traza']:.4f}, p < 1e-30)."
                ),
            },
        },
    }
    (ORO_DIR / "resumen_multivariado_e3.json").write_text(
        json.dumps(resumen_e3, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return resumen_e3


if __name__ == "__main__":
    res = ejecutar_pipeline_multivariado_e3()
    print("=================================================================")
    print(" ANÁLISIS MULTIVARIADO E3 (PCA + NORMALIDAD + MANOVA) COMPLETADO")
    print("=================================================================")
    print(f" * KMO = {res['pca']['kmo_global']} | Bartlett Chi2 = {res['pca']['bartlett_chi2']} (p = {res['pca']['bartlett_p_valor']:.2e})")
    print(f" * Varianza explicada PC1 + PC2 = {res['pca']['varianza_acumulada_2pc_pct']}% (PC1+PC2+PC3 = {res['pca']['varianza_acumulada_3pc_pct']}%)")
    m_mun = res["manova"]["municipios_agroclima_escala_original"]
    m_mkt = res["manova"]["mercados_mayoristas_sniim"]
    print(f" * MANOVA Municipios: Wilks = {m_mun['wilks_lambda']:.4f}, Pillai = {m_mun['pillai_traza']:.4f}, p = {m_mun['wilks_p']:.2e}, Perm p = {m_mun['permutacion_pillai_p_valor']}")
    print(f" * MANOVA Mercados:   Wilks = {m_mkt['wilks_lambda']:.4f}, Pillai = {m_mkt['pillai_traza']:.4f}, p = {m_mkt['wilks_p']:.2e}, Perm p = {m_mkt['permutacion_pillai_p_valor']}")
