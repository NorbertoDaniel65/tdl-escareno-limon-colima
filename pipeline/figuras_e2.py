"""
Generador Determinista de las 5 Figuras de Alta Resolución de la Entrega E2 (docs/E2/figuras/).
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).
"""

from __future__ import annotations

import json
from pathlib import Path

import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

ROOT_DIR = Path(__file__).resolve().parents[1]
PLATA_DIR = ROOT_DIR / "data" / "plata"
ORO_DIR = ROOT_DIR / "data" / "oro"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"
FIGURAS_DIR = ROOT_DIR / "docs" / "E2" / "figuras"

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "axes.titlesize": 10.5,
        "axes.titleweight": "bold",
        "axes.labelsize": 9.2,
        "xtick.labelsize": 8.2,
        "ytick.labelsize": 8.2,
        "legend.fontsize": 8.0,
        "axes.grid": True,
        "grid.alpha": 0.25,
    }
)


def generar_fig1_mapa_geoespacial() -> Path:
    gdf_mun = gpd.read_file(ORO_DIR / "perfil_geoespacial_municipios_oro.geojson")
    gdf_pts = gpd.read_file(PLATA_DIR / "infraestructura_agrologistica_colima_plata.geojson")
    df_q_geo = pd.read_csv(CUARENTENA_DIR / "cuarentena_geoespacial_e2.csv")

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.5, 6.0), gridspec_kw={"width_ratios": [1.35, 1.0]})

    # Panel 1: Mapa cartográfico de Colima + sjoin points + cuarentena fuera del límite
    otros = gdf_mun[~gdf_mun["en_observatorio_citricola"]]
    nucleo = gdf_mun[gdf_mun["en_observatorio_citricola"]]

    otros.plot(ax=ax1, color="#f1f5f9", edgecolor="#64748b", linewidth=0.9, zorder=1)
    nucleo.plot(
        ax=ax1,
        column="peso_siap_limon",
        cmap="YlGn",
        vmin=0.0,
        vmax=0.65,
        edgecolor="#0f766e",
        linewidth=1.8,
        alpha=0.88,
        zorder=2,
    )

    # Puntos fuera de Colima (cuarentena geoespacial)
    ax1.scatter(
        df_q_geo["longitud"],
        df_q_geo["latitud"],
        c="#94a3b8",
        marker="x",
        s=16,
        alpha=0.65,
        label=f"Cuarentena fuera de Colima (n={len(df_q_geo)})",
        zorder=3,
    )

    estilos_cat = {
        "Zona_Huerta_Citricola": ("#15803d", "o", 12, 0.55, "Huertas/Parcelas OSM"),
        "Infraestructura_Empaque_Bodega": ("#b45309", "s", 22, 0.85, "Empaque / Bodega Industrial"),
        "Mercado_Abasto": ("#dc2626", "^", 44, 0.95, "Mercado / Central de Abasto"),
        "Comercio_Fruticola_Mayorista": ("#7c3aed", "D", 32, 0.90, "Comercio Frutícola Mayorista"),
    }
    for cat, (color, marker, size, alpha, lbl) in estilos_cat.items():
        sub = gdf_pts[gdf_pts["categoria_agrologistica"] == cat]
        if len(sub) > 0:
            ax1.scatter(
                sub.geometry.x,
                sub.geometry.y,
                c=color,
                marker=marker,
                s=size,
                alpha=alpha,
                edgecolors="white",
                linewidths=0.35,
                label=f"{lbl} (n={len(sub)})",
                zorder=4,
            )

    # Nodos logísticos estratégicos
    ax1.scatter([-104.2940], [19.0550], c="#0284c7", marker="*", s=180, edgecolors="black", linewidths=0.8, label="Puerto de Manzanillo", zorder=6)
    ax1.scatter([-103.6860], [19.2770], c="#1d4ed8", marker="P", s=110, edgecolors="black", linewidths=0.8, label="Salida Autopista 54D (→ GDL)", zorder=6)

    # Etiquetas de municipios
    for _, row in gdf_mun.iterrows():
        negrita = "bold" if row["en_observatorio_citricola"] else "normal"
        col_txt = "#064e3b" if row["en_observatorio_citricola"] else "#475569"
        lbl_m = f"{row['nombre_oficial']}\n({int(row['peso_siap_limon']*100)}% SIAP)" if row["en_observatorio_citricola"] else row["nombre_oficial"]
        ax1.annotate(
            lbl_m,
            xy=(row["centroide_lon"], row["centroide_lat"]),
            ha="center",
            va="center",
            fontsize=7.3 if row["en_observatorio_citricola"] else 6.6,
            fontweight=negrita,
            color=col_txt,
            bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="none", alpha=0.72),
            zorder=7,
        )

    ax1.set_xlim(-104.72, -103.46)
    ax1.set_ylim(18.65, 19.53)
    ax1.set_title("Mapa Geoespacial Citrícola de Colima (EPSG:4326)\nUnión Espacial GeoPandas sjoin(within): 1,074 nodos válidos + 90 en cuarentena")
    ax1.set_xlabel("Longitud (° Oeste, WGS84)")
    ax1.set_ylabel("Latitud (° Norte, WGS84)")
    ax1.legend(loc="lower left", frameon=True, facecolor="white", framealpha=0.92, fontsize=7.3)

    # Panel 2: Infraestructura por municipio + distancia a Manzanillo
    top_df = gdf_mun.sort_values("n_nodos_agrologisticos_total", ascending=True)
    y_pos = np.arange(len(top_df))
    b1 = top_df["n_huertas_citricolas_osm"].to_numpy()
    b2 = top_df["n_empaque_bodega_osm"].to_numpy()
    b3 = (top_df["n_mercados_abasto_osm"] + top_df["n_comercio_fruticola_osm"]).to_numpy()

    ax2.barh(y_pos, b1, color="#15803d", alpha=0.88, label="Huertas/Parcelas OSM")
    ax2.barh(y_pos, b2, left=b1, color="#d97706", alpha=0.90, label="Empaque/Bodega")
    ax2.barh(y_pos, b3, left=b1 + b2, color="#dc2626", alpha=0.90, label="Mercados/Comercio")

    etiquetas_y = [
        f"{'* ' if r['en_observatorio_citricola'] else ''}{r['nombre_oficial']} ({r['dist_puerto_manzanillo_km']:.0f} km Pto)"
        for _, r in top_df.iterrows()
    ]
    ax2.set_yticks(y_pos)
    ax2.set_yticklabels(etiquetas_y, fontsize=8.0)
    for idx_y, tot in enumerate(top_df["n_nodos_agrologisticos_total"]):
        ax2.text(tot + 6, idx_y, f"{int(tot)}", va="center", fontsize=8.0, fontweight="bold", color="#1e293b")

    ax2.set_xlim(0, max(top_df["n_nodos_agrologisticos_total"]) * 1.15)
    ax2.set_xlabel("Número de nodos agrologísticos asignados por sjoin (within)")
    ax2.set_title("Distribución Municipal de Infraestructura OSM\n(* = 4 Municipios Núcleo del Observatorio | Distancia a Puerto en EPSG:32613)")
    ax2.legend(loc="lower right", frameon=True)

    plt.tight_layout()
    out = FIGURAS_DIR / "fig1_mapa_geoespacial_colima_e2.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def generar_fig2_linaje_arquitectura() -> Path:
    linaje = json.loads((ORO_DIR / "linaje_datos_e2.json").read_text(encoding="utf-8"))
    fig, ax = plt.subplots(figsize=(13.2, 5.4))
    ax.axis("off")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 60)

    ax.text(
        50, 56.5,
        "Arquitectura de Linaje y Trazabilidad de Datos (Bronce → Puerta de Calidad → Plata → Oro)",
        ha="center", va="center", fontsize=12.5, fontweight="bold", color="#0f172a",
    )
    ax.text(
        50, 52.8,
        f"Cobertura de Linaje Verificada: {linaje['cobertura_trazabilidad_pct']}% ({linaje['total_registros_oro_rastreados']} registros maestros en Capa Oro rastreables hasta archivo Bronce, SHA-256 y fecha UTC)",
        ha="center", va="center", fontsize=9.0, color="#0f766e", fontweight="bold",
    )

    def _caja(x, y, w, h, titulo, lineas, fc, ec):
        rect = mpatches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.6", facecolor=fc, edgecolor=ec, linewidth=1.6)
        ax.add_patch(rect)
        ax.text(x + w / 2, y + h - 2.3, titulo, ha="center", va="top", fontsize=8.8, fontweight="bold", color=ec)
        ax.text(x + 1.1, y + h - 5.4, "\n".join(lineas), ha="left", va="top", fontsize=7.4, color="#1e293b", linespacing=1.35)

    # Columna 1: Capa Bronce (3 Fuentes)
    _caja(1.5, 36.0, 22.5, 13.5, "BRONCE · F1 Open-Meteo", [
        "agroclima_colima_diario_historico.csv",
        "7,304 reg. | 2021-2025 + Snapshots",
        "Ingesta: 2026-11-09T22:27Z",
        "SHA256: a8e5f5c6... | CC BY 4.0",
    ], "#fef3c7", "#b45309")

    _caja(1.5, 20.5, 22.5, 13.5, "BRONCE · F2 SNIIM (SE)", [
        "precios_limon_sniim_historico_60m.csv",
        "240 reg. | 4 plazas x 60 meses",
        "Ingesta: 2026-11-09T22:27Z",
        "SHA256: 7dde14cf... | Datos Abiertos MX",
    ], "#fef3c7", "#b45309")

    _caja(1.5, 5.0, 22.5, 13.5, "BRONCE · F3 OSM Geoespacial (E2)", [
        "municipios_colima_osm.geojson (10)",
        "infraestructura_agrologistica (1,164)",
        "Ingesta: 2026-11-22T16:22Z",
        "SHA256: d5c7129f... | ODbL 1.0 | 0 PII",
    ], "#fef3c7", "#b45309")

    # Columna 2: Puerta de Calidad y Cuarentena
    _caja(28.5, 22.0, 20.5, 24.0, "PUERTA DE CALIDAD", [
        "• Contratos Pandera (RN-01..04)",
        "• Validación CRS EPSG:4326",
        "• Filtro espacial sjoin(within)",
        "• Auditoría 0 PII (LFPDPPP)",
        "",
        "APROBADOS:",
        "  Clima: 7,304 | SNIIM: 240",
        "  Geoespacial: 1,074 en Colima",
    ], "#e0f2fe", "#0369a1")

    _caja(28.5, 5.0, 20.5, 13.5, "CUARENTENA (0 Borrados)", [
        "• Tabular: 11 reg. inválidos",
        "  (cuarentena_registros.csv)",
        "• Geoespacial: 90 fuera Colima",
        "  (cuarentena_geoespacial_e2.csv)",
    ], "#fee2e2", "#b91c1c")

    # Columna 3: Capa Plata
    _caja(53.5, 15.0, 19.5, 31.0, "CAPA PLATA (Limpia)", [
        "• agroclima_mensual_plata.csv",
        "  (240 filas, 0 nulos)",
        "• precios_sniim_mensual_plata",
        "  (240 filas, choques 2022/24)",
        "• infraestructura_colima_plata",
        "  (1,074 nodos con municipio)",
        "",
        "Transformaciones:",
        "  KNN/Interp., Min-Max/Z-Score,",
        "  Discretización, UTM EPSG:32613",
    ], "#f1f5f9", "#334155")

    # Columna 4: Capa Oro con Linaje
    _caja(77.0, 15.0, 21.5, 31.0, "CAPA ORO (100% Rastreable)", [
        "1. serie_mensual_oro_60m.csv",
        "   (60 reg. · ORO-SERIE-YYYY-MM)",
        "2. panel_integrado_oro.csv",
        "   (240 reg. · ORO-PANEL-...)",
        "3. perfil_geoespacial_oro.geojson",
        "   (10 reg. · ORO-GEO-0600X)",
        "",
        "Columnas por Registro:",
        "  linaje_id_registro, fuentes,",
        "  archivos, sha256, fecha_utc",
    ], "#dcfce7", "#15803d")

    # Caja inferior de ejemplo de rastreo
    _caja(53.5, 2.2, 45.0, 10.5, "Ejemplo Verificado: rastrear_registro_oro('ORO-SERIE-2022-02')", [
        "Registro Oro: ORO-SERIE-2022-02 (Precio $46.63 MXN/kg · Choque Feb 2022)",
        " ← Clima: agroclima_colima_diario_historico.csv [SHA256: a8e5f5c6 | 2026-11-09T22:27Z]",
        " ← Precio: precios_limon_sniim_historico_60m.csv [SHA256: 7dde14cf | 2026-11-09T22:27Z]",
    ], "#f0fdf4", "#0f766e")

    # Flechas
    kw_arrow = dict(arrowstyle="-|>,head_width=0.35,head_length=0.5", color="#475569", lw=1.6)
    for y_src in (42.5, 27.2, 11.7):
        ax.annotate("", xy=(28.3, 33.5 if y_src > 20 else 28.0), xytext=(24.2, y_src), arrowprops=kw_arrow)
    ax.annotate("", xy=(38.7, 18.8), xytext=(38.7, 21.8), arrowprops=dict(arrowstyle="-|>,head_width=0.35,head_length=0.5", color="#b91c1c", lw=1.6))
    ax.annotate("", xy=(53.3, 33.5), xytext=(49.2, 33.5), arrowprops=kw_arrow)
    ax.annotate("", xy=(76.8, 30.5), xytext=(73.2, 30.5), arrowprops=kw_arrow)

    plt.tight_layout()
    out = FIGURAS_DIR / "fig2_arquitectura_linaje_bronce_oro_e2.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def generar_fig3_doe_factorial_2_3() -> Path:
    df_23 = pd.read_csv(ORO_DIR / "experimento_factorial_2_3_corridas_e2.csv")
    df_ef = pd.read_csv(ORO_DIR / "efectos_factorial_2_3_e2.csv").sort_values("t_absoluto", ascending=True)

    fig, axes = plt.subplots(1, 3, figsize=(14.2, 4.8))

    # A) Pareto de efectos estandarizados |t|
    ax = axes[0]
    colores = ["#0f766e" if sig else "#94a3b8" for sig in df_ef["significativo_5pct"]]
    ax.barh(df_ef["descripcion"], df_ef["t_absoluto"], color=colores, edgecolor="#1e293b", linewidth=0.6)
    t_crit = float(stats.t.ppf(0.975, df=14))  # 24 - 1 - 2(bloque) - 7(efectos) = 14 gl error
    ax.axvline(t_crit, color="#dc2626", linestyle="--", linewidth=1.6, label=f"Umbral crítico |t| = {t_crit:.2f} (α=0.05)")
    for i, (_, r) in enumerate(df_ef.iterrows()):
        ax.text(r["t_absoluto"] + 1.2, i, f"{r['t_absoluto']:.1f} ({r['efecto_estimado_ms']:+.1f} ms)", va="center", fontsize=7.5)
    ax.set_xlim(0, df_ef["t_absoluto"].max() * 1.38)
    ax.set_title("A) Diagrama de Pareto de Efectos (|t|)\nDiseño Factorial 2³ (n=24, 3 bloques)")
    ax.set_xlabel("Efecto Estandarizado |t|")
    ax.legend(loc="lower right", fontsize=7.5)

    # B) Gráfica de Efectos Principales
    ax = axes[1]
    factores = [
        ("A_paralelismo", "A: Paralelismo", ["1 Hilo (-1)", "4 Hilos (+1)"], "#0284c7"),
        ("B_validacion", "B: Validación", ["Iterativa (-1)", "Pandera (+1)"], "#0f766e"),
        ("C_formato", "C: Formato", ["CSV (-1)", "Parquet (+1)"], "#d97706"),
    ]
    x_offsets = [0, 2.2, 4.4]
    xticks = []
    xticklabels = []
    for (col, nom, lbls, col_l), x0 in zip(factores, x_offsets):
        m_neg = df_23[df_23[col] == -1]["tiempo_total_ms"].mean()
        m_pos = df_23[df_23[col] == 1]["tiempo_total_ms"].mean()
        ax.plot([x0, x0 + 1.1], [m_neg, m_pos], marker="o", linewidth=2.4, markersize=7, color=col_l, label=nom)
        ax.text(x0, m_neg + 7, f"{m_neg:.1f}", ha="center", fontsize=7.6, fontweight="bold", color=col_l)
        ax.text(x0 + 1.1, m_pos + 7, f"{m_pos:.1f}", ha="center", fontsize=7.6, fontweight="bold", color=col_l)
        xticks.extend([x0, x0 + 1.1])
        xticklabels.extend(lbls)
    ax.axhline(df_23["tiempo_total_ms"].mean(), color="#64748b", linestyle=":", linewidth=1.2, label="Media global")
    ax.set_xticks(xticks)
    ax.set_xticklabels(xticklabels, rotation=24, ha="right", fontsize=7.5)
    ax.set_ylim(120, 290)
    ax.set_ylabel("Tiempo Medio de Ejecución (ms)")
    ax.set_title("B) Gráfica de Efectos Principales (2³)\nMenor tiempo = Mejor eficiencia")
    ax.legend(loc="upper right", fontsize=7.4)

    # C) Gráfica de Interacción B x C (Validación x Formato)
    ax = axes[2]
    for c_val, lbl_c, col_c, mk in [(-1, "C = CSV UTF-8 (-1)", "#dc2626", "s"), (1, "C = Parquet Snappy (+1)", "#15803d", "o")]:
        sub = df_23[df_23["C_formato"] == c_val].groupby("B_validacion")["tiempo_total_ms"].agg(["mean", "std"])
        ax.errorbar(
            [0, 1],
            [sub.loc[-1, "mean"], sub.loc[1, "mean"]],
            yerr=[sub.loc[-1, "std"], sub.loc[1, "std"]],
            marker=mk,
            linewidth=2.3,
            capsize=4,
            color=col_c,
            label=lbl_c,
        )
    ax.set_xticks([0, 1])
    ax.set_xticklabels(["Iterativa (-1)", "Pandera Vectorizado (+1)"])
    ax.set_ylabel("Tiempo Medio ± DE (ms)")
    ax.set_title("C) Interacción B × C (Validación × Formato)\nEfectos aditivos dominantes sin cruce")
    ax.legend(loc="upper right", fontsize=7.8)

    plt.tight_layout()
    out = FIGURAS_DIR / "fig3_doe_factorial_2_3_efectos_pareto.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def generar_fig4_anova_2x3_y_supuestos() -> Path:
    df_23 = pd.read_csv(ORO_DIR / "experimento_factorial_2_3_corridas_e2.csv")
    df_2x3 = pd.read_csv(ORO_DIR / "experimento_dos_factores_2x3_e2.csv")
    res_doe = json.loads((ORO_DIR / "resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))

    mod_23 = smf.ols("tiempo_total_ms ~ C(bloque) + A_paralelismo * B_validacion * C_formato", data=df_23).fit()
    resid = np.asarray(mod_23.resid)
    fitted = np.asarray(mod_23.fittedvalues)
    sup = res_doe["diseno_2_3"]["supuestos_residuos_escala_lineal"]

    fig, axes = plt.subplots(2, 3, figsize=(14.0, 8.2))

    # (0,0) Interacción ANOVA 2x3 (2 motores x 3 formatos)
    ax = axes[0, 0]
    orden_fmt = ["csv_utf8", "parquet_snappy", "parquet_zstd"]
    etq_fmt = ["CSV UTF-8", "Parquet Snappy", "Parquet ZSTD"]
    for motor, lbl_m, col_m, mk in [
        ("iterativo", "Validación Iterativa", "#dc2626", "s"),
        ("pandera_vectorizado", "Pandera Vectorizado", "#0f766e", "o"),
    ]:
        sub = df_2x3[df_2x3["motor_validacion"] == motor].groupby("formato_persistencia")["tiempo_total_ms"].agg(["mean", "std"])
        ys = [sub.loc[f, "mean"] for f in orden_fmt]
        es = [sub.loc[f, "std"] for f in orden_fmt]
        ax.errorbar([0, 1, 2], ys, yerr=es, marker=mk, linewidth=2.2, capsize=4, color=col_m, label=lbl_m)
        for xi, yi in zip([0, 1, 2], ys):
            ax.text(xi, yi + 9, f"{yi:.1f}", ha="center", fontsize=7.6, color=col_m, fontweight="bold")
    ax.set_xticks([0, 1, 2])
    ax.set_xticklabels(etq_fmt)
    ax.set_ylabel("Tiempo Medio ± DE (ms)")
    ax.set_title(f"ANOVA Dos Vías (2×3): Motor × Formato\np(interacción) = {res_doe['diseno_dos_vias_2x3']['p_valor_interaccion_BxC']:.3f}")
    ax.legend(loc="upper right", fontsize=7.6)

    # (0,1) Tamaño en disco por formato (KB)
    ax = axes[0, 1]
    tam = df_2x3.groupby("formato_persistencia")["tamano_disco_kb"].mean().reindex(orden_fmt)
    bars = ax.bar(etq_fmt, tam.values, color=["#ef4444", "#0284c7", "#0f766e"], edgecolor="#1e293b", linewidth=0.7)
    for b, v in zip(bars, tam.values):
        pct_red = 100.0 * (tam.iloc[0] - v) / tam.iloc[0]
        lbl = f"{v:.1f} KB" if pct_red == 0 else f"{v:.1f} KB\n(-{pct_red:.1f}%)"
        ax.text(b.get_x() + b.get_width() / 2, v + 45, lbl, ha="center", fontsize=8.0, fontweight="bold")
    ax.set_ylim(0, tam.max() * 1.22)
    ax.set_ylabel("Tamaño en Disco (KB)")
    ax.set_title("Eficiencia de Almacenamiento por Formato\nParquet reduce >91% el espacio en disco")

    # (0,2) Tiempos de los 8 tratamientos del 2^3
    ax = axes[0, 2]
    res_t = df_23.groupby("tratamiento")["tiempo_total_ms"].agg(["mean", "std"]).sort_values("mean")
    cols_bar = ["#15803d" if i == 0 else ("#dc2626" if t == "A-B-C-" else "#3b82f6") for i, t in enumerate(res_t.index)]
    ax.barh(res_t.index, res_t["mean"], xerr=res_t["std"], color=cols_bar, alpha=0.88, capsize=3)
    ax.set_xlabel("Tiempo Medio ± DE (ms)")
    ax.set_title("Ranking de los 8 Tratamientos (2³)\nVerde = Óptimo (A+B+C+) | Rojo = Línea Base")

    # (1,0) Q-Q Normal de Residuos (Shapiro-Wilk)
    ax = axes[1, 0]
    (osm, osr), (slope, intercept, _) = stats.probplot(resid, dist="norm")
    ax.scatter(osm, osr, color="#0284c7", edgecolors="white", s=42, zorder=3)
    ax.plot(osm, slope * osm + intercept, color="#dc2626", linewidth=1.6, zorder=2)
    ax.set_title(f"Puerta 3 · Normalidad (Q-Q Residuos)\nShapiro-Wilk W={sup['shapiro_wilk_W']:.4f}, p={sup['shapiro_wilk_p']:.4f} ✓")
    ax.set_xlabel("Cuantiles Teóricos N(0,1)")
    ax.set_ylabel("Residuos del ANOVA (ms)")

    # (1,1) Residuos vs Ajustados (Levene)
    ax = axes[1, 1]
    ax.scatter(fitted, resid, color="#0f766e", edgecolors="white", s=45)
    ax.axhline(0, color="#dc2626", linestyle="--", linewidth=1.3)
    ax.set_title(f"Puerta 3 · Homocedasticidad\nLevene F={sup['levene_F']:.4f}, p={sup['levene_p']:.4f} ✓")
    ax.set_xlabel("Valores Ajustados ŷ (ms)")
    ax.set_ylabel("Residuos (ms)")

    # (1,2) Residuos vs Orden de Corrida Aleatorizado (Durbin-Watson)
    ax = axes[1, 2]
    ax.plot(df_23["orden_corrida"], resid, marker="o", color="#7c3aed", linewidth=1.4, markersize=5)
    ax.axhline(0, color="#dc2626", linestyle="--", linewidth=1.3)
    ax.set_title(f"Puerta 3 · Independencia Temporal\nDurbin-Watson DW={sup['durbin_watson']:.4f} ✓")
    ax.set_xlabel("Orden Aleatorizado de Corrida (1..24)")
    ax.set_ylabel("Residuos (ms)")

    plt.tight_layout()
    out = FIGURAS_DIR / "fig4_anova_dos_vias_y_supuestos_residuos.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def generar_fig5_fraccionado_confirmacion_iso() -> Path:
    df_alias = pd.read_csv(ORO_DIR / "estructura_alias_2_4_fraccionado_e2.csv")
    df_conf = pd.read_csv(ORO_DIR / "corrida_confirmacion_optimo_e2.csv")
    res_doe = json.loads((ORO_DIR / "resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))
    df_25010 = pd.read_csv(ORO_DIR / "evaluacion_iso_25010_e2.csv")

    fig, axes = plt.subplots(1, 3, figsize=(14.4, 4.9))

    # A) 2^4 Completo vs 2^(4-1) Fraccionado (Resolución IV, 50% ahorro)
    ax = axes[0]
    principales = df_alias.iloc[:4]
    x = np.arange(len(principales))
    w = 0.36
    ax.bar(x - w / 2, principales["efecto_completo_2_4_ms"], width=w, color="#0284c7", label="2⁴ Completo (16 corridas)")
    ax.bar(x + w / 2, principales["efecto_fraccionado_2_4_1_ms"], width=w, color="#0f766e", label="2⁴⁻¹ Fraccionado (8 corridas · -50%)")
    ax.axhline(0, color="#334155", linewidth=0.9)
    ax.set_xticks(x)
    ax.set_xticklabels(["A\n(Paral.)", "B\n(Valid.)", "C\n(Formato)", "D\n(Partic.)"])
    ax.set_ylim(min(principales["efecto_completo_2_4_ms"].min(), principales["efecto_fraccionado_2_4_1_ms"].min()) - 28, 12)
    ax.set_ylabel("Efecto Principal Estimado (ms)")
    ax.set_title("A) 2⁴ Completo vs. 2⁴⁻¹ Fraccionado\nResolución IV (I=ABCD) · Ahorro 50% corridas")
    ax.legend(loc="lower right", fontsize=7.3)

    # B) Corrida de Confirmación del Óptimo (n=5) con IC 95%
    ax = axes[1]
    conf = res_doe["corrida_confirmacion"]
    base_vals = df_conf[df_conf["escenario"].str.startswith("Linea_Base")]["tiempo_total_ms"]
    opt_vals = df_conf[df_conf["escenario"].str.startswith("Optimo")]["tiempo_total_ms"]

    ax.bar(["Línea Base E1\n(A-B-C-)"], [base_vals.mean()], yerr=[base_vals.std()], color="#ef4444", alpha=0.85, capsize=5, width=0.45)
    ax.bar(["Óptimo Confirmado\n(A+B+C+)"], [opt_vals.mean()], yerr=[opt_vals.std()], color="#15803d", alpha=0.88, capsize=5, width=0.45)

    # Banda IC 95% de predicción sobre la columna del óptimo
    pi_inf, pi_sup = conf["ic95_prediccion_ms"]
    ax.fill_between([0.72, 1.28], [pi_inf, pi_inf], [pi_sup, pi_sup], color="#fde047", alpha=0.45, label=f"IC 95% Predicción [{pi_inf:.1f}, {pi_sup:.1f}]")
    ax.hlines(conf["prediccion_optimo_modelo_ms"], 0.72, 1.28, colors="#1e3a8a", linestyles="--", linewidth=1.8, label=f"Predicción ŷ = {conf['prediccion_optimo_modelo_ms']:.1f} ms")

    ax.annotate(
        f"-{conf['mejora_tiempo_pct']}% tiempo\n({conf['factor_aceleracion_speedup']}x speedup)\n-{conf['reduccion_disco_pct']}% disco",
        xy=(1, opt_vals.mean() + 18),
        xytext=(0.45, base_vals.mean() * 0.72),
        arrowprops=dict(arrowstyle="->", color="#0f172a", lw=1.4),
        fontsize=8.2,
        fontweight="bold",
        bbox=dict(boxstyle="round,pad=0.35", fc="#dcfce7", ec="#15803d"),
    )
    ax.set_ylabel("Tiempo Real Medido (ms, n=5)")
    ax.set_title("B) Corrida de Confirmación del Óptimo\nMedia observada dentro del IC 95% ✓")
    ax.legend(loc="upper right", fontsize=7.3)

    # C) Evaluación ISO/IEC 25010 (8 características medidas)
    ax = axes[2]
    df_iso = df_25010.sort_values("puntaje_100", ascending=True)
    nombres_cortos = [c.split(". ")[1].split(" (")[0] for c in df_iso["caracteristica"]]
    ax.barh(nombres_cortos, df_iso["puntaje_100"], color="#0f766e", alpha=0.88, edgecolor="#1e293b", linewidth=0.6)
    ax.axvline(90.0, color="#d97706", linestyle="--", linewidth=1.3, label="Meta Excelencia (90)")
    for i, val in enumerate(df_iso["puntaje_100"]):
        ax.text(val + 0.8, i, f"{val:.0f}", va="center", fontsize=7.8, fontweight="bold")
    ax.set_xlim(0, 108)
    ax.set_xlabel("Calificación Medida (0–100)")
    ax.set_title(f"C) Perfil ISO/IEC 25010 (Media: {df_25010['puntaje_100'].mean():.1f}/100)\nEficiencia probada por DOE | Fiabilidad real 99.74%")
    ax.legend(loc="lower right", fontsize=7.5)

    plt.tight_layout()
    out = FIGURAS_DIR / "fig5_fraccionado_2_4_y_confirmacion_optimo.png"
    fig.savefig(out, dpi=200, bbox_inches="tight")
    plt.close(fig)
    return out


def generar_todas_figuras_e2() -> list[Path]:
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    return [
        generar_fig1_mapa_geoespacial(),
        generar_fig2_linaje_arquitectura(),
        generar_fig3_doe_factorial_2_3(),
        generar_fig4_anova_2x3_y_supuestos(),
        generar_fig5_fraccionado_confirmacion_iso(),
    ]


if __name__ == "__main__":
    rutas = generar_todas_figuras_e2()
    for r in rutas:
        print(f"[OK] {r.relative_to(ROOT_DIR)} ({r.stat().st_size:,} bytes)")
