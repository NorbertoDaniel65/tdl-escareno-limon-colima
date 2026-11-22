"""
Tablero Interactivo del Observatorio CITRO-DATA LAB COLIMA (E1 + E2).
Observatorio Agroclimático, Geoespacial y de Precios Mayoristas del Limón Mexicano.
Autor: Norberto Daniel Escareño Montaño (23460323)
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
PLATA_DIR = ROOT_DIR / "data" / "plata"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"
FIGURAS_E1_DIR = ROOT_DIR / "docs" / "E1" / "figuras"
FIGURAS_E2_DIR = ROOT_DIR / "docs" / "E2" / "figuras"

st.set_page_config(
    page_title="CITRO-DATA LAB COLIMA · Observatorio E2",
    page_icon="🍋",
    layout="wide",
)

st.title("🍋 CITRO-DATA LAB COLIMA — Observatorio Agroclimático, Geoespacial y de Precios del Limón Mexicano")
st.caption(
    "**Entregas E1 + E2 · Trusted Data Lab: Fuente Especializada Geoespacial, Ética, Linaje, Experimento 2³ e ISO 25010/25012** | "
    "Estudiante: Norberto Daniel Escareño Montaño (23460323)"
)

serie_oro = pd.read_csv(ORO_DIR / "serie_mensual_oro_60m.csv")
pronostico = pd.read_csv(ORO_DIR / "pronostico_e1_limon.csv")
comp_modelos = pd.read_csv(ORO_DIR / "comparativa_modelos_pronostico_e1.csv")
cuarentena = pd.read_csv(CUARENTENA_DIR / "cuarentena_registros.csv")
cuarentena_geo = pd.read_csv(CUARENTENA_DIR / "cuarentena_geoespacial_e2.csv")
perfil_geo = pd.read_csv(ORO_DIR / "perfil_geoespacial_municipios_oro.csv")
pts_geo_plata = pd.read_csv(PLATA_DIR / "infraestructura_agrologistica_colima_plata.csv")
catalogo_linaje = pd.read_csv(ORO_DIR / "catalogo_linaje_oro_bronce.csv")
anova_2_3 = pd.read_csv(ORO_DIR / "anova_factorial_2_3_e2.csv")
efectos_2_3 = pd.read_csv(ORO_DIR / "efectos_factorial_2_3_e2.csv")
alias_2_4 = pd.read_csv(ORO_DIR / "estructura_alias_2_4_fraccionado_e2.csv")
iso_25010 = pd.read_csv(ORO_DIR / "evaluacion_iso_25010_e2.csv")
iso_25012 = pd.read_csv(ORO_DIR / "evaluacion_iso_25012_e2.csv")

with open(CUARENTENA_DIR / "reporte_puerta_calidad.json", encoding="utf-8") as f:
    rep_puerta = json.load(f)
with open(ORO_DIR / "diagnostico_series_tiempo_e1.json", encoding="utf-8") as f:
    diag_ts = json.load(f)
with open(ORO_DIR / "resumen_geoespacial_e2.json", encoding="utf-8") as f:
    res_geo = json.load(f)
with open(ORO_DIR / "linaje_datos_e2.json", encoding="utf-8") as f:
    res_linaje = json.load(f)
with open(ORO_DIR / "resumen_experimento_doe_e2.json", encoding="utf-8") as f:
    res_doe = json.load(f)
with open(ORO_DIR / "resumen_evaluacion_iso_e2.json", encoding="utf-8") as f:
    res_iso = json.load(f)

ganador = comp_modelos.iloc[0]

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric(
    "Fuente Geoespacial Colima (E2)",
    f"{res_geo['puntos_aprobados_dentro_colima_plata']:,} nodos",
    f"{res_geo['puntos_enviados_cuarentena_fuera_colima']} en cuarentena | 0 PII",
)
col2.metric(
    "Linaje Capa Oro (E2)",
    f"{res_linaje['cobertura_trazabilidad_pct']:.0f}%",
    f"{res_linaje['total_registros_oro_rastreados']} registros rastreables",
)
col3.metric(
    "Óptimo DOE 2³ Confirmado",
    f"-{res_doe['corrida_confirmacion']['mejora_tiempo_pct']}% tiempo",
    f"{res_doe['corrida_confirmacion']['factor_aceleracion_speedup']}x speedup | -{res_doe['corrida_confirmacion']['reduccion_disco_pct']}% disco",
)
col4.metric(
    "Pronóstico Ganador (E1)",
    f"MAPE {ganador['MAPE_test_pct']:.2f}%",
    f"SARIMA · Ljung-Box p={diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag12_pvalue']:.3f}",
)
col5.metric(
    "ISO 25010 / ISO 25012",
    f"{res_iso['iso_25010_promedio_100']:.1f} / {res_iso['iso_25012_promedio_100']:.1f}",
    f"Disponibilidad real: {res_iso['fiabilidad_acumulada_e0_e2']['disponibilidad_real_pct']}%",
)

tab_geo, tab_linaje, tab_doe, tab_iso, tab_pron, tab_puerta = st.tabs(
    [
        "🗺️ Mapa Geoespacial Citrícola (E2)",
        "🔗 Linaje y Trazabilidad Bronce → Oro (E2)",
        "🧪 Experimento Factorial 2³ y ANOVA (E2)",
        "✅ Ética, ISO 25010 y 25012 (E2)",
        "📈 Pronóstico 2026 con IC 95% (E1)",
        "🛡️ Puerta de Calidad y Cuarentena (E1+E2)",
    ]
)

with tab_geo:
    st.subheader("Fuente Especializada Geoespacial: OpenStreetMap (Nominatim + Overpass) × Marco Municipal Colima")
    st.markdown(
        """
        * **Unión Espacial (`GeoPandas`):** `gpd.sjoin(puntos_osm, poligonos_colima, predicate="within")` en **WGS84 (`EPSG:4326`)**, con métricas territoriales y distancias logísticas al **Puerto de Manzanillo** y la **Autopista 54D hacia Guadalajara** proyectadas en **UTM Zona 13N (`EPSG:32613`)**.
        * **Cumplimiento LFPDPPP:** `0` datos personales capturados (lista blanca estricta en `extractores/geoespacial_osm.py`). Licencia: **ODbL 1.0 (© OpenStreetMap Contributors)**.
        """
    )
    st.image(str(FIGURAS_E2_DIR / "fig1_mapa_geoespacial_colima_e2.png"), use_container_width=True)

    c_filt, c_map = st.columns([1, 2.2])
    with c_filt:
        cats_disp = sorted(pts_geo_plata["categoria_agrologistica"].unique())
        cats_sel = st.multiselect("Filtrar categorías en el mapa interactivo:", cats_disp, default=cats_disp)
        muns_disp = sorted(pts_geo_plata["nombre_oficial"].unique())
        muns_sel = st.multiselect("Filtrar municipios de Colima:", muns_disp, default=["Tecomán", "Armería", "Manzanillo", "Colima"])
        sub_pts = pts_geo_plata[
            pts_geo_plata["categoria_agrologistica"].isin(cats_sel)
            & pts_geo_plata["nombre_oficial"].isin(muns_sel)
        ]
        st.info(f"Mostrando **{len(sub_pts):,}** nodos agrologísticos válidos dentro de los polígonos seleccionados.")
    with c_map:
        st.map(sub_pts.rename(columns={"latitud": "latitude", "longitud": "longitude"})[["latitude", "longitude"]])

    st.markdown("**Perfil Geoespacial e Infraestructura Integrada en Capa Oro (`data/oro/perfil_geoespacial_municipios_oro.csv`):**")
    st.dataframe(
        perfil_geo[
            [
                "cvegeo",
                "nombre_oficial",
                "en_observatorio_citricola",
                "peso_siap_limon",
                "superficie_km2",
                "n_huertas_citricolas_osm",
                "n_empaque_bodega_osm",
                "n_mercados_abasto_osm",
                "n_nodos_agrologisticos_total",
                "densidad_agrologistica_100km2",
                "dist_puerto_manzanillo_km",
                "dist_corredor_gdl_54d_km",
            ]
        ],
        use_container_width=True,
    )

with tab_linaje:
    st.subheader("Linaje y Trazabilidad Completa Registro-a-Registro (Capa Bronce → Puerta → Plata → Oro)")
    st.image(str(FIGURAS_E2_DIR / "fig2_arquitectura_linaje_bronce_oro_e2.png"), use_container_width=True)

    id_sel = st.selectbox(
        "Selecciona cualquier `linaje_id_registro` de Capa Oro para auditar su origen exacto en Capa Bronce:",
        catalogo_linaje["linaje_id_registro"].tolist(),
        index=13,  # ORO-SERIE-2022-02 por defecto
    )
    fila_lin = catalogo_linaje[catalogo_linaje["linaje_id_registro"] == id_sel].iloc[0].to_dict()
    st.json(fila_lin)
    st.markdown("**Catálogo Completo de Trazabilidad (`data/oro/catalogo_linaje_oro_bronce.csv` — 310 registros):**")
    st.dataframe(catalogo_linaje, use_container_width=True)

with tab_doe:
    st.subheader("Experimento Factorial Real 2³, ANOVA de Dos Vías (2×3) y 2⁴ vs. 2⁴⁻¹ Fraccionado (Resolución IV)")
    st.success(
        f"**Combinación Óptima Confirmada (`{res_doe['diseno_2_3']['tratamiento_optimo']}`):** "
        f"`4 Hilos Paralelo + Pandera Vectorizado + Apache Parquet (Snappy)` redujo el tiempo de ejecución en "
        f"**{res_doe['corrida_confirmacion']['mejora_tiempo_pct']}%** (**{res_doe['corrida_confirmacion']['factor_aceleracion_speedup']}× más rápido**, "
        f"`{res_doe['corrida_confirmacion']['observado_linea_base_media_ms']:.1f} ms → {res_doe['corrida_confirmacion']['observado_optimo_media_ms']:.1f} ms`) "
        f"y redujo el espacio en disco en **{res_doe['corrida_confirmacion']['reduccion_disco_pct']}%** con **0.0% de error**. "
        f"Puerta 3 de supuestos aprobada (Shapiro-Wilk p={res_doe['diseno_2_3']['supuestos_residuos_escala_lineal']['shapiro_wilk_p']}, "
        f"Levene p={res_doe['diseno_2_3']['supuestos_residuos_escala_lineal']['levene_p']}, "
        f"Durbin-Watson={res_doe['diseno_2_3']['supuestos_residuos_escala_lineal']['durbin_watson']})."
    )
    st.image(str(FIGURAS_E2_DIR / "fig3_doe_factorial_2_3_efectos_pareto.png"), use_container_width=True)
    st.image(str(FIGURAS_E2_DIR / "fig4_anova_dos_vias_y_supuestos_residuos.png"), use_container_width=True)
    st.image(str(FIGURAS_E2_DIR / "fig5_fraccionado_2_4_y_confirmacion_optimo.png"), use_container_width=True)

    c_ef, c_al = st.columns(2)
    with c_ef:
        st.markdown("**Tabla ANOVA de Efectos Fijos — Diseño Factorial 2³:**")
        st.dataframe(anova_2_3, use_container_width=True)
    with c_al:
        st.markdown("**Estructura de Alias — 2⁴ Completo vs. 2⁴⁻¹ Fraccionado (I = ABCD):**")
        st.dataframe(alias_2_4, use_container_width=True)

with tab_iso:
    st.subheader("Evaluación Cuantitativa ISO/IEC 25010 (Producto), ISO/IEC 25012 (Datos) y Ética (`docs/etica-datos.md`)")
    c_i1, c_i2 = st.columns(2)
    with c_i1:
        st.markdown(f"**ISO/IEC 25010 — Calidad del Producto (Promedio: {res_iso['iso_25010_promedio_100']}/100):**")
        st.dataframe(iso_25010, use_container_width=True)
    with c_i2:
        st.markdown(f"**ISO/IEC 25012 — Calidad de Datos en Capa Oro (Promedio: {res_iso['iso_25012_promedio_100']}/100):**")
        st.dataframe(iso_25012, use_container_width=True)

with tab_pron:
    st.subheader("Pronóstico Oficial 2026 con Intervalo de Predicción al 95% (En Lenguaje de Negocio)")
    st.markdown(
        """
        **Explicación para el productor y empacador citrícola de Colima (sin jerga técnica):**
        * **Ventana de Alta Rentabilidad (Enero – Marzo 2026):** Se proyecta el pico estacional entre **$28.00 y $33.50 MXN/kg** (techo de **$42.00 MXN/kg** al 95%).
        * **Valle Estacional de Cosecha Pico (Junio – Septiembre 2026):** Con lluvias de verano el precio desciende a **$15.00 – $18.00 MXN/kg**; conviene desviar segunda calidad a industria destiladora en Tecomán.
        """
    )
    st.image(str(FIGURAS_E1_DIR / "fig5_pronostico_final_ic95_residuos.png"), use_container_width=True)
    st.dataframe(
        pronostico[pronostico["horizonte"] == "Pronostico_Futuro_2026"][
            [
                "anio_mes",
                "pronostico_puntual_mxn_kg",
                "limite_inferior_ic95_mxn_kg",
                "limite_superior_ic95_mxn_kg",
                "recomendacion_comercial_cliente",
            ]
        ],
        use_container_width=True,
    )

with tab_puerta:
    st.subheader("Auditoría de Puerta de Calidad Tabular (E1) y Geoespacial (E2) — Cero Borrado Silencioso")
    st.markdown(f"**Cuarentena Tabular E1 (`{len(cuarentena)}` registros):**")
    st.dataframe(cuarentena, use_container_width=True)
    st.markdown(f"**Cuarentena Geoespacial E2 (`{len(cuarentena_geo)}` registros fuera de límites de Colima):**")
    st.dataframe(cuarentena_geo.head(25), use_container_width=True)
