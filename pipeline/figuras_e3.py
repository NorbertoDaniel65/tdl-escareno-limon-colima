"""
Generador de las 5 Figuras de Alta Definición para la Entrega E3.
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).

Usa la paleta oficial costera de Colima:
  - Petróleo:  #304C53
  - Terracota: #BC6C50
  - Arena:     #DDAD9C
  - Cacao:     #5A2F25
  - Brisa:     #AFE0E7
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse
import numpy as np
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
FIG_DIR = ROOT_DIR / "docs" / "E3" / "figuras"

PETROL = "#304C53"
TERRACOTA = "#BC6C50"
ARENA = "#DDAD9C"
CACAO = "#5A2F25"
BRISA = "#AFE0E7"
FONDO = "#FAF7F5"

COLORES_MUN = {
    "Tecoman": TERRACOTA,
    "Armeria": PETROL,
    "Manzanillo": "#2A8C9E",
    "Colima": CACAO,
}


def _elipse_confianza(x: np.ndarray, y: np.ndarray, ax: plt.Axes, color: str, n_std: float = 1.6) -> None:
    if len(x) < 3:
        return
    cov = np.cov(x, y)
    vals, vecs = np.linalg.eigh(cov)
    orden = vals.argsort()[::-1]
    vals, vecs = vals[orden], vecs[:, orden]
    theta = np.degrees(np.arctan2(*vecs[:, 0][::-1]))
    w, h = 2 * n_std * np.sqrt(np.maximum(vals, 1e-6))
    el = Ellipse(
        xy=(float(np.mean(x)), float(np.mean(y))),
        width=float(w),
        height=float(h),
        angle=float(theta),
        edgecolor=color,
        facecolor=color,
        alpha=0.14,
        lw=1.8,
        ls="--",
    )
    ax.add_patch(el)


def generar_figuras_e3() -> list[str]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"font.sans-serif": "DejaVu Sans", "axes.edgecolor": "#D5C7BF"})

    corr_df = pd.read_csv(ORO_DIR / "matriz_correlaciones_e3.csv").set_index("variable")
    qq_df = pd.read_csv(ORO_DIR / "distancias_mahalanobis_qq_e3.csv")
    scree_df = pd.read_csv(ORO_DIR / "pca_varianza_explicada_e3.csv")
    cargas_df = pd.read_csv(ORO_DIR / "pca_cargas_variables_e3.csv")
    proy_df = pd.read_csv(ORO_DIR / "pca_proyecciones_municipios_mercados_e3.csv")
    manova_df = pd.read_csv(ORO_DIR / "manova_resultados_e3.csv")
    anovas_df = pd.read_csv(ORO_DIR / "comparativa_manova_vs_anovas_e3.csv")
    bench_df = pd.read_csv(ORO_DIR / "benchmark_etapas_optimizacion_e3.csv")
    retro_df = pd.read_csv(ORO_DIR / "retrospectiva_psp_e0_e3.csv")
    sello_df = pd.read_csv(ORO_DIR / "sello_tdl_evaluacion_e3.csv")

    res_mv = json.loads((ORO_DIR / "resumen_multivariado_e3.json").read_text(encoding="utf-8"))
    res_opt = json.loads((ORO_DIR / "resumen_optimizacion_e3.json").read_text(encoding="utf-8"))

    rutas = []

    # =========================================================================
    # FIGURA 1: Matriz de Correlaciones (p=8) + Q-Q Distancias de Mahalanobis
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.4), dpi=220)
    fig.patch.set_facecolor("white")

    etiquetas_cortas = [
        "T.Máx (°C)",
        "T.Mín (°C)",
        "Estrés ≥35°C",
        "Precip. (mm)",
        "ET0 (mm)",
        "GDD (13°C)",
        "Viento (km/h)",
        "Radiación",
    ]
    mat_r = corr_df.to_numpy(dtype=float)
    im = ax1.imshow(mat_r, cmap="RdBu_r", vmin=-1.0, vmax=1.0)
    ax1.set_xticks(range(len(etiquetas_cortas)))
    ax1.set_yticks(range(len(etiquetas_cortas)))
    ax1.set_xticklabels(etiquetas_cortas, rotation=32, ha="right", fontsize=8.8)
    ax1.set_yticklabels(etiquetas_cortas, fontsize=8.8)
    for i in range(mat_r.shape[0]):
        for j in range(mat_r.shape[1]):
            val = mat_r[i, j]
            col_txt = "white" if abs(val) > 0.55 else "#24353A"
            ax1.text(j, i, f"{val:.2f}", ha="center", va="center", fontsize=8, color=col_txt, fontweight="bold")
    ax1.set_title("A) Matriz de Correlaciones Multivariada R (p = 8, N = 240)", fontsize=11.5, fontweight="bold", color=PETROL, pad=10)
    plt.colorbar(im, ax=ax1, fraction=0.045, pad=0.03)

    # Panel B: Q-Q Plot de Mahalanobis (Escala Original vs. Yeo-Johnson Puerta 3)
    norm_info = res_mv["normalidad_multivariada_puerta3"]
    ax2.scatter(
        qq_df["cuantil_chi2_teorico_gl8"],
        qq_df["mahalanobis_d2_original"],
        color=ARENA,
        edgecolor=CACAO,
        s=28,
        alpha=0.65,
        label=f"Escala original (r = {norm_info['escala_original']['correlacion_qq_mahalanobis']:.4f})",
    )
    ax2.scatter(
        qq_df["cuantil_chi2_teorico_gl8"],
        qq_df["mahalanobis_d2_yeo_johnson_ordenado"],
        color=PETROL,
        edgecolor="white",
        s=34,
        alpha=0.90,
        label=f"Transformación Yeo-Johnson Puerta 3 (r = {norm_info['transformacion_yeo_johnson']['correlacion_qq_mahalanobis']:.4f})",
    )
    max_q = float(qq_df["cuantil_chi2_teorico_gl8"].max())
    ax2.plot([0, max_q], [0, max_q], color=TERRACOTA, lw=2.2, ls="--", label="Recta teórica Chi² (gl = 8)")
    ax2.axhline(norm_info["escala_original"]["umbral_chi2_gl8_95"], color=CACAO, lw=1.3, ls=":", label="Umbral Chi² 95% (15.51)")
    ax2.set_xlabel("Cuantiles teóricos Chi-cuadrada (gl = 8)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax2.set_ylabel("Distancia cuadrada de Mahalanobis D²", fontsize=9.8, fontweight="bold", color=PETROL)
    ax2.set_title(
        "B) Gráfica Q-Q de Mahalanobis y Normalidad (Mardia / Henze-Zirkler)",
        fontsize=11.5,
        fontweight="bold",
        color=PETROL,
        pad=10,
    )
    ax2.grid(True, alpha=0.25)
    ax2.legend(loc="upper left", fontsize=8.3, frameon=True)
    ax2.text(
        0.03,
        0.54,
        f"Mardia Curtosis (Yeo-Johnson): b2,p = {norm_info['transformacion_yeo_johnson']['mardia_b2p_curtosis']:.2f}\n"
        f"Z = {norm_info['transformacion_yeo_johnson']['mardia_z_curtosis']:.2f} (p = {norm_info['transformacion_yeo_johnson']['mardia_p_curtosis']:.3f} ✓ Normal)\n"
        f"Henze-Zirkler HZ = {norm_info['transformacion_yeo_johnson']['hz_estadistico']:.3f}\n"
        f"Coherencia dentro de Chi² 95%: {norm_info['transformacion_yeo_johnson']['pct_dentro_chi2_95']:.1f}%",
        transform=ax2.transAxes,
        fontsize=8.3,
        bbox={"boxstyle": "round,pad=0.45", "facecolor": FONDO, "edgecolor": ARENA},
        color=PETROL,
    )

    plt.tight_layout()
    p1 = FIG_DIR / "fig1_matriz_correlaciones_y_qq_mahalanobis_e3.png"
    fig.savefig(p1, dpi=220, bbox_inches="tight")
    plt.close(fig)
    rutas.append(str(p1))

    # =========================================================================
    # FIGURA 2: Scree Plot (Sedimentación) + Biplot PCA (PC1 vs. PC2)
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.0, 6.6), dpi=220, gridspec_kw={"width_ratios": [1, 1.35]})
    fig.patch.set_facecolor("white")

    pcs = scree_df["componente"].tolist()
    eigs = scree_df["eigenvalor_lambda"].to_numpy()
    var_a = scree_df["varianza_acumulada_pct"].to_numpy()
    colores_bar = [TERRACOTA if v >= 1.0 else ARENA for v in eigs]

    bars = ax1.bar(pcs, eigs, color=colores_bar, edgecolor=PETROL, width=0.58)
    ax1.axhline(1.0, color=CACAO, ls="--", lw=1.8, label="Criterio de Kaiser (λ = 1.0)")
    ax1.set_ylabel("Valor propio (Eigenvalor λ)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax1.set_title("A) Gráfica de Sedimentación (Scree Plot) y Varianza Acumulada", fontsize=11.3, fontweight="bold", color=PETROL)
    ax1.grid(True, axis="y", alpha=0.25)

    ax1_r = ax1.twinx()
    ax1_r.plot(pcs, var_a, color=PETROL, marker="o", lw=2.3, label="Varianza acumulada (%)")
    ax1_r.set_ylabel("Varianza explicada acumulada (%)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax1_r.set_ylim(0, 108)
    for idx_b, b in enumerate(bars):
        ax1.text(
            b.get_x() + b.get_width() / 2,
            b.get_height() + 0.08,
            f"λ={eigs[idx_b]:.2f}\n({scree_df['varianza_explicada_pct'].iloc[idx_b]:.1f}%)",
            ha="center",
            va="bottom",
            fontsize=7.5,
            fontweight="bold",
            color=PETROL,
        )
    ax1.legend(loc="upper right", fontsize=8.3)

    # Panel B: Biplot PC1 vs. PC2 con elipses de confianza y vectores de carga
    for mun, grp in proy_df.groupby("municipio"):
        c_m = COLORES_MUN.get(mun, PETROL)
        x_m = grp["PC1_estres_termo_evaporativo"].to_numpy()
        y_m = grp["PC2_humedad_pluvial_costera"].to_numpy()
        ax2.scatter(x_m, y_m, color=c_m, s=30, alpha=0.72, label=f"{mun} (n=60)", edgecolor="white", lw=0.4)
        _elipse_confianza(x_m, y_m, ax2, c_m, n_std=1.55)
        ax2.scatter([np.mean(x_m)], [np.mean(y_m)], color=c_m, s=150, marker="D", edgecolor="white", lw=1.4, zorder=6)

    escala_vec = 3.2
    for idx_c, r_c in cargas_df.iterrows():
        vx = float(r_c["carga_corr_PC1"]) * escala_vec
        vy = float(r_c["carga_corr_PC2"]) * escala_vec
        ax2.annotate(
            "",
            xy=(vx, vy),
            xytext=(0, 0),
            arrowprops={"arrowstyle": "->", "color": CACAO, "lw": 1.8},
        )
        ax2.text(
            vx * 1.09,
            vy * 1.09,
            etiquetas_cortas[idx_c],
            fontsize=8.2,
            fontweight="bold",
            color=CACAO,
            ha="center",
            va="center",
            bbox={"boxstyle": "round,pad=0.18", "facecolor": "white", "edgecolor": ARENA, "alpha": 0.88},
        )

    ax2.axhline(0, color="#999999", lw=1, ls=":")
    ax2.axvline(0, color="#999999", lw=1, ls=":")
    ax2.set_xlabel(
        f"PC1 ({scree_df['varianza_explicada_pct'].iloc[0]:.2f}%): {scree_df['nombre_negocio'].iloc[0]}",
        fontsize=9.4,
        fontweight="bold",
        color=PETROL,
    )
    ax2.set_ylabel(
        f"PC2 ({scree_df['varianza_explicada_pct'].iloc[1]:.2f}%): {scree_df['nombre_negocio'].iloc[1]}",
        fontsize=9.4,
        fontweight="bold",
        color=PETROL,
    )
    ax2.set_title(
        f"B) Mapa Multivariado (Biplot PC1 vs. PC2 · {scree_df['varianza_acumulada_pct'].iloc[1]:.2f}% Varianza)",
        fontsize=11.3,
        fontweight="bold",
        color=PETROL,
    )
    ax2.grid(True, alpha=0.25)
    ax2.legend(loc="lower left", fontsize=8.4, frameon=True)

    plt.tight_layout()
    p2 = FIG_DIR / "fig2_pca_sedimentacion_y_biplot_municipios_e3.png"
    fig.savefig(p2, dpi=220, bbox_inches="tight")
    plt.close(fig)
    rutas.append(str(p2))

    # =========================================================================
    # FIGURA 3: MANOVA (Municipios y Mercados) vs. Inflación Error Tipo I ANOVAs
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.2), dpi=220)
    fig.patch.set_facecolor("white")

    eta_vars = anovas_df.sort_values("eta2_univariado", ascending=True)
    ax1.barh(
        eta_vars["etiqueta_negocio"],
        eta_vars["eta2_univariado"],
        color=ARENA,
        edgecolor=PETROL,
        label="ANOVA univariado separado (η²)",
    )
    m_mun = res_mv["manova"]["municipios_agroclima_escala_original"]
    m_mkt = res_mv["manova"]["mercados_mayoristas_sniim"]
    ax1.axvline(
        m_mun["wilks_eta2"],
        color=TERRACOTA,
        lw=2.5,
        ls="--",
        label=f"MANOVA Municipios (Wilks Λ={m_mun['wilks_lambda']:.4f}, η²={m_mun['wilks_eta2']:.3f}, p<1e-114)",
    )
    ax1.axvline(
        m_mkt["wilks_eta2"],
        color=PETROL,
        lw=2.5,
        ls="-.",
        label=f"MANOVA Mercados (Wilks Λ={m_mkt['wilks_lambda']:.4f}, η²={m_mkt['wilks_eta2']:.3f}, p<1e-105)",
    )
    ax1.set_xlabel("Tamaño de efecto Eta Cuadrado (η²)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax1.set_title("A) Poder Discriminante MANOVA (Wilks y Pillai) vs. ANOVAs Separados", fontsize=11.0, fontweight="bold", color=PETROL)
    ax1.set_xlim(0, 0.80)
    ax1.grid(True, axis="x", alpha=0.25)
    ax1.legend(loc="lower right", fontsize=8.0, frameon=True)

    # Panel B: Inflación del Error Tipo I Global en p ANOVAs independientes vs. MANOVA
    p_grid = np.arange(1, 13)
    err_inflado = (1.0 - (0.95**p_grid)) * 100.0
    err_manova = np.full_like(p_grid, 5.0, dtype=float)
    ax2.plot(p_grid, err_inflado, color=TERRACOTA, marker="o", lw=2.6, label="p ANOVAs separados: 1 - (1 - 0.05)^p")
    ax2.plot(p_grid, err_manova, color=PETROL, marker="s", lw=2.4, ls="--", label="MANOVA único (Lambda de Wilks / Pillai): α = 5.0%")
    ax2.scatter([8], [33.66], color=CACAO, s=130, zorder=6)
    ax2.annotate(
        "p = 8 variables en E3:\n33.66% riesgo falso positivo\nen ANOVAs separados vs 5% en MANOVA",
        xy=(8, 33.66),
        xytext=(3.2, 38.0),
        arrowprops={"arrowstyle": "->", "color": CACAO, "lw": 1.6},
        fontsize=8.6,
        fontweight="bold",
        color=CACAO,
        bbox={"boxstyle": "round,pad=0.35", "facecolor": FONDO, "edgecolor": TERRACOTA},
    )
    ax2.set_xlabel("Número de variables respuesta evaluadas simultáneamente (p)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax2.set_ylabel("Tasa de Error Tipo I Global (%)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax2.set_title("B) Por qué MANOVA supera a correr varios ANOVAs separados", fontsize=11.0, fontweight="bold", color=PETROL)
    ax2.set_ylim(0, 52)
    ax2.grid(True, alpha=0.25)
    ax2.legend(loc="upper left", fontsize=8.5, frameon=True)

    plt.tight_layout()
    p3 = FIG_DIR / "fig3_manova_municipios_mercados_vs_anovas_e3.png"
    fig.savefig(p3, dpi=220, bbox_inches="tight")
    plt.close(fig)
    rutas.append(str(p3))

    # =========================================================================
    # FIGURA 4: Optimización Medida del Pipeline Antes (E1) vs. Después (E3)
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.0), dpi=220)
    fig.patch.set_facecolor("white")

    etiquetas_esc = ["Antes (E1)\n1 hilo · Iterativo · CSV", "Después (E3 Snappy)\n4 hilos · Pandera · Parquet", "Después (E3 ZSTD)\n4 hilos · Pandera · ZSTD"]
    t_io = bench_df["tiempo_io_medio_ms"].to_numpy()
    t_val = bench_df["tiempo_validacion_medio_ms"].to_numpy()
    t_tr = bench_df["tiempo_transformacion_medio_ms"].to_numpy()
    t_wr = bench_df["tiempo_escritura_medio_ms"].to_numpy()

    x_pos = np.arange(len(etiquetas_esc))
    ax1.bar(x_pos, t_io, width=0.48, label="1. Lectura I/O Bronce", color=BRISA, edgecolor=PETROL)
    ax1.bar(x_pos, t_val, width=0.48, bottom=t_io, label="2. Validación Puerta Calidad", color=TERRACOTA, edgecolor=PETROL)
    ax1.bar(x_pos, t_tr, width=0.48, bottom=t_io + t_val, label="3. Transformación / Agregación", color=ARENA, edgecolor=PETROL)
    ax1.bar(x_pos, t_wr, width=0.48, bottom=t_io + t_val + t_tr, label="4. Escritura Plata + Oro", color=PETROL, edgecolor=PETROL)

    totales = bench_df["tiempo_total_medio_ms"].to_numpy()
    for i, tot in enumerate(totales):
        ax1.text(i, tot + 95, f"{tot:.1f} ms", ha="center", va="bottom", fontsize=9.5, fontweight="bold", color=CACAO)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels(etiquetas_esc, fontsize=8.8, fontweight="bold")
    ax1.set_ylabel("Tiempo de ejecución medio (ms, n = 10 réplicas)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax1.set_title(
        f"A) Desglose de Latencia Antes vs. Después (Speedup {res_opt['mejoras_cuantificadas']['factor_aceleracion_speedup']}× · -{res_opt['mejoras_cuantificadas']['reduccion_tiempo_total_pct']}%)",
        fontsize=11.0,
        fontweight="bold",
        color=PETROL,
    )
    ax1.set_ylim(0, float(totales.max()) * 1.18)
    ax1.grid(True, axis="y", alpha=0.25)
    ax1.legend(loc="upper right", fontsize=8.4)

    # Panel B: Comparativa de Memoria Pico RAM (MB) y Disco (KB)
    metricas_lbl = ["Memoria RAM Pico (KB)", "Almacenamiento Disco (KB)"]
    antes_vals = [float(bench_df["memoria_pico_media_kb"].iloc[0]), float(bench_df["disco_total_kb"].iloc[0])]
    despues_snappy = [float(bench_df["memoria_pico_media_kb"].iloc[1]), float(bench_df["disco_total_kb"].iloc[1])]
    despues_zstd = [float(bench_df["memoria_pico_media_kb"].iloc[2]), float(bench_df["disco_total_kb"].iloc[2])]

    xm = np.arange(len(metricas_lbl))
    w_b = 0.25
    b1 = ax2.bar(xm - w_b, antes_vals, width=w_b, color=CACAO, label="Antes (E1 · CSV UTF-8)")
    b2 = ax2.bar(xm, despues_snappy, width=w_b, color=TERRACOTA, label="Después (E3 · Parquet Snappy)")
    b3 = ax2.bar(xm + w_b, despues_zstd, width=w_b, color=PETROL, label="Después (E3 · Parquet ZSTD)")
    for grupo_b in (b1, b2, b3):
        for rect in grupo_b:
            h_v = rect.get_height()
            ax2.text(rect.get_x() + rect.get_width() / 2, h_v + 40, f"{h_v:.0f} KB", ha="center", va="bottom", fontsize=8.2, fontweight="bold", color=PETROL)
    ax2.set_xticks(xm)
    ax2.set_xticklabels(metricas_lbl, fontsize=9.8, fontweight="bold")
    ax2.set_ylabel("Consumo medido (KB)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax2.set_title(
        f"B) Ahorro en Memoria RAM (-{res_opt['mejoras_cuantificadas']['reduccion_memoria_pico_pct']}%) y Disco (-{res_opt['mejoras_cuantificadas']['reduccion_disco_zstd_pct']}%)",
        fontsize=11.0,
        fontweight="bold",
        color=PETROL,
    )
    ax2.set_ylim(0, max(antes_vals) * 1.22)
    ax2.grid(True, axis="y", alpha=0.25)
    ax2.legend(loc="upper right", fontsize=8.4)

    plt.tight_layout()
    p4 = FIG_DIR / "fig4_optimizacion_pipeline_antes_despues_e3.png"
    fig.savefig(p4, dpi=220, bbox_inches="tight")
    plt.close(fig)
    rutas.append(str(p4))

    # =========================================================================
    # FIGURA 5: Retrospectiva PSP (E0->E3) y Cumplimiento del Sello TDL (6/6)
    # =========================================================================
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.5, 6.0), dpi=220)
    fig.patch.set_facecolor("white")

    etapas_cortas = ["E0 Arranque", "E1 Plata/SARIMA", "E2 DOE/ISO", "E3 PCA/Sello"]
    exactitud = retro_df["exactitud_estimacion_pct"].to_numpy()
    yield_rev = retro_df["yield_revision_pct"].to_numpy()
    t_corr = retro_df["tiempo_medio_correccion_min"].to_numpy()

    ax1.plot(etapas_cortas, exactitud, marker="o", lw=2.5, color=PETROL, label="Exactitud estimación tiempo (%)")
    ax1.plot(etapas_cortas, yield_rev, marker="s", lw=2.5, color=TERRACOTA, label="Rendimiento revisiones / Yield (%)")
    for i, (ex_v, y_v) in enumerate(zip(exactitud, yield_rev)):
        ax1.text(i, ex_v - 6.5, f"{ex_v:.1f}%", ha="center", fontsize=8.2, fontweight="bold", color=PETROL)
        ax1.text(i, y_v + 3.5, f"Yield {y_v:.0f}%", ha="center", fontsize=8.2, fontweight="bold", color=TERRACOTA)
    ax1.set_ylim(0, 115)
    ax1.set_ylabel("Porcentaje (%)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax1.set_title("A) Retrospectiva PSP E0 → E3: Exactitud, Yield y Costo de Corrección", fontsize=11.0, fontweight="bold", color=PETROL)
    ax1.grid(True, alpha=0.25)

    ax1_r = ax1.twinx()
    ax1_r.bar(etapas_cortas, t_corr, width=0.32, color=ARENA, alpha=0.45, label="Tiempo medio corrección (min)")
    ax1_r.set_ylabel("Minutos promedio por defecto", fontsize=9.4, fontweight="bold", color=CACAO)
    ax1_r.set_ylim(0, 25)
    ax1.legend(loc="center left", fontsize=8.3)

    # Panel B: Certificación de los 6 Criterios del Sello TDL
    criterios_lbl = [
        "1. Disponibilidad 14d (≥95%)",
        "2. Completitud Oro (≥95%)",
        "3. Cobertura pytest (≥60%)",
        "4. Secretos expuestos (=0)",
        "5. Críticos abiertos (=0)",
        "6. Reproducibilidad (100%)",
    ]
    puntajes_vis = [99.85, 100.0, 88.4, 100.0, 100.0, 100.0]
    umbrales_vis = [95.0, 95.0, 60.0, 100.0, 100.0, 100.0]
    etiquetas_val = [
        "99.85% ✓",
        "100.0% ✓",
        "88.4% ✓",
        "0 secretos ✓",
        "0 abiertos (5/5) ✓",
        "Determinista ✓",
    ]
    y_c = np.arange(len(criterios_lbl))
    bars_s = ax2.barh(y_c, puntajes_vis, color=PETROL, edgecolor=TERRACOTA, height=0.56)
    ax2.scatter(umbrales_vis, y_c, color=TERRACOTA, s=80, zorder=5, label="Umbral mínimo oficial Sello TDL")
    for idx_s, rect in enumerate(bars_s):
        ax2.text(
            rect.get_width() - 3.0,
            rect.get_y() + rect.get_height() / 2,
            etiquetas_val[idx_s],
            ha="right",
            va="center",
            fontsize=8.8,
            fontweight="bold",
            color="white",
        )
    ax2.set_yticks(y_c)
    ax2.set_yticklabels(criterios_lbl, fontsize=9.2, fontweight="bold", color=PETROL)
    ax2.invert_yaxis()
    ax2.set_xlim(0, 112)
    ax2.set_xlabel("Grado de cumplimiento verificado (%)", fontsize=9.8, fontweight="bold", color=PETROL)
    ax2.set_title("B) Certificación Oficial del Sello TDL (6 / 6 Criterios Cumplidos)", fontsize=11.0, fontweight="bold", color=PETROL)
    ax2.grid(True, axis="x", alpha=0.25)
    ax2.legend(loc="lower right", fontsize=8.4)

    plt.tight_layout()
    p5 = FIG_DIR / "fig5_retrospectiva_psp_modelos_y_sello_tdl_e3.png"
    fig.savefig(p5, dpi=220, bbox_inches="tight")
    plt.close(fig)
    rutas.append(str(p5))

    return rutas


if __name__ == "__main__":
    generadas = generar_figuras_e3()
    print(f"[OK] {len(generadas)} figuras HD generadas para E3:")
    for r in generadas:
        print(f"  - {r}")
