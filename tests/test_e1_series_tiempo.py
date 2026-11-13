"""
Pruebas unitarias y de integración para la Etapa E1 — Análisis Estadístico (Unidad 3)
e Integración en Capa Oro:
Serie maestra de 60 meses, Diccionario de Datos, Pruebas ADF, ACF/PACF, CCF,
Comparación de 4 Modelos (SES, Holt, Holt-Winters, SARIMA), Prueba de Ljung-Box y
Pronóstico 2026 con IC al 95%.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
FIGURAS_DIR = ROOT_DIR / "docs" / "E1" / "figuras"


def test_integracion_capa_oro_y_diccionario_datos():
    serie_path = ORO_DIR / "serie_mensual_oro_60m.csv"
    panel_path = ORO_DIR / "panel_integrado_municipio_mercado_oro.csv"
    dic_path = ORO_DIR / "diccionario_datos.md"

    assert serie_path.exists() and panel_path.exists() and dic_path.exists()
    df_oro = pd.read_csv(serie_path)
    df_panel = pd.read_csv(panel_path)

    assert len(df_oro) == 60, "La serie maestra de Capa Oro debe tener exactamente 60 meses"
    assert df_oro["anio_mes"].is_monotonic_increasing
    assert df_oro["anio_mes"].nunique() == 60
    assert df_oro.isna().sum().sum() == 0
    assert len(df_panel) == 240
    assert dic_path.stat().st_size > 2500


def test_estacionariedad_adf_acf_pacf_y_ccf():
    diag_path = ORO_DIR / "diagnostico_series_tiempo_e1.json"
    ccf_path = ORO_DIR / "correlacion_cruzada_clima_precio_e1.csv"
    assert diag_path.exists() and ccf_path.exists()

    with open(diag_path, encoding="utf-8") as f:
        diag = json.load(f)

    assert len(diag["pruebas_estacionariedad_adf"]) == 3
    # La primera diferencia debe ser estacionaria al 5%
    assert diag["pruebas_estacionariedad_adf"][1]["p_valor"] < 0.05

    df_ccf = pd.read_csv(ccf_path)
    assert len(df_ccf) == 28  # 4 variables climáticas x 7 rezagos (0..6)
    assert df_ccf["significativa_95pct"].any(), "Debe existir correlación cruzada significativa clima-precio"


def test_cuatro_modelos_seleccion_y_residuos_ljung_box():
    comp_path = ORO_DIR / "comparativa_modelos_pronostico_e1.csv"
    pron_path = ORO_DIR / "pronostico_e1_limon.csv"
    diag_path = ORO_DIR / "diagnostico_series_tiempo_e1.json"

    df_comp = pd.read_csv(comp_path)
    assert len(df_comp) == 4, "Se deben comparar exactamente los 4 modelos obligatorios (SES, Holt, HW, SARIMA)"
    for col in ["MAE_test_mxn_kg", "RMSE_test_mxn_kg", "MAPE_test_pct", "seleccionado"]:
        assert col in df_comp.columns

    ganador = df_comp.iloc[0]
    assert bool(ganador["seleccionado"]) is True
    assert ganador["MAPE_test_pct"] < 10.0, f"MAPE del modelo ganador debe ser < 10%, obtenido={ganador['MAPE_test_pct']}"

    with open(diag_path, encoding="utf-8") as f:
        diag = json.load(f)
    lb = diag["diagnostico_residuos_ljung_box"]
    assert lb["ljung_box_lag6_pvalue"] > 0.05
    assert lb["ljung_box_lag12_pvalue"] > 0.05
    assert lb["es_ruido_blanco_95pct"] is True

    df_pron = pd.read_csv(pron_path)
    futuro = df_pron[df_pron["horizonte"] == "Pronostico_Futuro_2026"]
    assert len(futuro) == 12
    assert (futuro["limite_inferior_ic95_mxn_kg"] < futuro["pronostico_puntual_mxn_kg"]).all()
    assert (futuro["pronostico_puntual_mxn_kg"] < futuro["limite_superior_ic95_mxn_kg"]).all()


def test_figuras_y_notebook_e1_generados():
    for nombre in [
        "fig1_puerta_calidad_y_limpieza.png",
        "fig2_descomposicion_serie_60m.png",
        "fig3_estacionariedad_acf_pacf_ccf.png",
        "fig4_comparativa_4_modelos_test.png",
        "fig5_pronostico_final_ic95_residuos.png",
    ]:
        p = FIGURAS_DIR / nombre
        assert p.exists() and p.stat().st_size > 20000, f"Figura faltante o vacía: {nombre}"

    nb_path = ROOT_DIR / "docs" / "E1" / "limpieza.ipynb"
    assert nb_path.exists() and nb_path.stat().st_size > 5000
