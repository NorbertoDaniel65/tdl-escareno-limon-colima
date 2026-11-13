"""
Tablero Interactivo de Datos de Confianza y Pronóstico (E1).
CITRO-DATA LAB COLIMA — Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano.
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
FIGURAS_DIR = ROOT_DIR / "docs" / "E1" / "figuras"

st.set_page_config(
    page_title="CITRO-DATA LAB COLIMA · Tablero E1",
    page_icon="🍋",
    layout="wide",
)

st.title("🍋 CITRO-DATA LAB COLIMA — Observatorio Agroclimático y de Precios del Limón Mexicano")
st.caption(
    "**Entrega E1 · Trusted Data Lab: Capa Plata, Limpieza, Puerta de Calidad y Pronóstico** | "
    "Estudiante: Norberto Daniel Escareño Montaño (23460323)"
)

serie_oro = pd.read_csv(ORO_DIR / "serie_mensual_oro_60m.csv")
pronostico = pd.read_csv(ORO_DIR / "pronostico_e1_limon.csv")
comp_modelos = pd.read_csv(ORO_DIR / "comparativa_modelos_pronostico_e1.csv")
cuarentena = pd.read_csv(CUARENTENA_DIR / "cuarentena_registros.csv")
with open(CUARENTENA_DIR / "reporte_puerta_calidad.json", encoding="utf-8") as f:
    rep_puerta = json.load(f)
with open(ORO_DIR / "diagnostico_series_tiempo_e1.json", encoding="utf-8") as f:
    diag_ts = json.load(f)

ganador = comp_modelos.iloc[0]

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "Registros Aprobados a Plata",
    f"{rep_puerta['resumen_clima_diario']['registros_aprobados_plata'] + rep_puerta['resumen_sniim_mensual']['registros_aprobados_plata']:,}",
    f"{len(cuarentena)} en cuarentena (0 borrados)",
)
col2.metric(
    "Serie Maestra Capa Oro",
    f"{len(serie_oro)} meses",
    "2021-01 a 2025-12 (100% íntegra)",
)
col3.metric(
    "Modelo Ganador en Prueba (12m)",
    ganador["id_modelo"],
    f"MAPE: {ganador['MAPE_test_pct']:.2f}% | RMSE: {ganador['RMSE_test_mxn_kg']:.2f} MXN/kg",
)
col4.metric(
    "Diagnóstico Ljung-Box (Lag 12)",
    f"p = {diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag12_pvalue']:.3f}",
    "Residuos = Ruido Blanco (p > 0.05)",
)

tab1, tab2, tab3 = st.tabs(
    [
        "📈 Pronóstico 2026 con IC 95% y Recomendación al Cliente",
        "🔬 Descomposición, Estacionariedad (ADF) y 4 Modelos",
        "🛡️ Puerta de Calidad, Cuarentena y Capa Oro",
    ]
)

with tab1:
    st.subheader("Pronóstico Oficial 2026 con Intervalo de Predicción al 95% (En Lenguaje de Negocio)")
    st.markdown(
        """
        **Explicación para el productor y empacador citrícola de Colima (sin jerga técnica):**
        * **Ventana de Alta Rentabilidad (Enero – Marzo 2026):** Se proyecta el pico estacional de precios por menor corte de invierno, alcanzando entre **$28.00 y $33.50 MXN/kg** (con techo de hasta **$42.00 MXN/kg** en el escenario superior al 95%). Se recomienda programar riegos de auxilio en Tecomán y Armería desde noviembre-diciembre para asegurar fruta calibre #4 y #5 en esta ventana.
        * **Valle Estacional de Cosecha Pico (Junio – Septiembre 2026):** Con la entrada de lluvias de verano aumenta la oferta nacional y el precio en origen desciende a la banda de **$15.00 a $18.00 MXN/kg**. Se recomienda desviar fruta de segunda a la industria procesadora (aceite esencial destilado y cáscara deshidratada en Tecomán) y evitar ventas spot sin piso contractual.
        """
    )
    st.image(str(FIGURAS_DIR / "fig5_pronostico_final_ic95_residuos.png"), use_container_width=True)
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

with tab2:
    st.subheader("Comparativa de los 4 Modelos en Conjunto de Prueba (2025-01 a 2025-12)")
    st.dataframe(comp_modelos, use_container_width=True)
    st.image(str(FIGURAS_DIR / "fig4_comparativa_4_modelos_test.png"), use_container_width=True)
    st.subheader("Descomposición Multiplicativa y Pruebas ADF / ACF / PACF / CCF")
    st.image(str(FIGURAS_DIR / "fig2_descomposicion_serie_60m.png"), use_container_width=True)
    st.image(str(FIGURAS_DIR / "fig3_estacionariedad_acf_pacf_ccf.png"), use_container_width=True)

with tab3:
    st.subheader("Auditoría de Puerta de Calidad Automática y Registros en Cuarentena")
    st.image(str(FIGURAS_DIR / "fig1_puerta_calidad_y_limpieza.png"), use_container_width=True)
    st.markdown("**Registros detenidos en `data/cuarentena/cuarentena_registros.csv` (Cero eliminación silenciosa):**")
    st.dataframe(cuarentena, use_container_width=True)
    st.markdown("**Serie Maestra Integrada en Capa Oro (`data/oro/serie_mensual_oro_60m.csv`):**")
    st.dataframe(serie_oro, use_container_width=True)
