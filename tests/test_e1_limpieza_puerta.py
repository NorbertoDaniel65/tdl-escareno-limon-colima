"""
Pruebas unitarias y de integración para la Etapa E1 — Ingeniería de Datos (Unidad 3):
Puerta de Calidad, Cuarentena, Valores Faltantes (MCAR/MAR/MNAR), Atípicos (IQR/MAD/IsoForest),
Escalado (Min-Max/Z-Score), Discretización, Jerarquías y Reducción de Datos.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
PLATA_DIR = ROOT_DIR / "data" / "plata"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"


def test_puerta_calidad_y_cuarentena_sin_borrado_silencioso():
    rep_path = CUARENTENA_DIR / "reporte_puerta_calidad.json"
    cuarentena_path = CUARENTENA_DIR / "cuarentena_registros.csv"
    assert rep_path.exists(), "Falta reporte_puerta_calidad.json"
    assert cuarentena_path.exists(), "Falta cuarentena_registros.csv"

    with open(rep_path, encoding="utf-8") as f:
        rep = json.load(f)

    df_q = pd.read_csv(cuarentena_path)
    assert len(df_q) == 11, f"Se esperaban 11 registros defectuosos en cuarentena, se hallaron {len(df_q)}"
    assert (
        rep["resumen_clima_diario"]["registros_evaluados_bronce"]
        == rep["resumen_clima_diario"]["registros_aprobados_plata"]
        + rep["resumen_clima_diario"]["registros_en_cuarentena"]
    ), "Violación de conservación de masa en clima: evaluados != aprobados + cuarentena"
    assert (
        rep["resumen_sniim_mensual"]["registros_evaluados_bronce"]
        == rep["resumen_sniim_mensual"]["registros_aprobados_plata"]
        + rep["resumen_sniim_mensual"]["registros_en_cuarentena"]
    ), "Violación de conservación de masa en SNIIM: evaluados != aprobados + cuarentena"

    for col in ["tabla_origen", "llave_primaria", "regla_violada", "severidad", "motivo_rechazo"]:
        assert col in df_q.columns
        assert df_q[col].notna().all()


def test_diagnostico_faltantes_mcar_mar_mnar_y_cero_nulos_plata():
    eval_path = PLATA_DIR / "evaluacion_imputacion_faltantes.csv"
    assert eval_path.exists()
    df_ev = pd.read_csv(eval_path)
    mecanismos = set(df_ev["mecanismo_diagnosticado"].unique())
    assert len(mecanismos) == 3, "Deben estar diagnosticados los 3 mecanismos MCAR, MAR y MNAR"

    df_clima_p = pd.read_csv(PLATA_DIR / "agroclima_mensual_plata.csv")
    df_sniim_p = pd.read_csv(PLATA_DIR / "precios_sniim_mensual_plata.csv")
    assert df_clima_p.isna().sum().sum() == 0, "No deben existir nulos sin tratar en agroclima_mensual_plata.csv"
    assert df_sniim_p.isna().sum().sum() == 0, "No deben existir nulos sin tratar en precios_sniim_mensual_plata.csv"
    assert len(df_clima_p) == 240
    assert len(df_sniim_p) == 240


def test_deteccion_atipicos_3_metodos_y_conservacion_choques():
    atip_path = PLATA_DIR / "reporte_atipicos_comparativo.csv"
    assert atip_path.exists()
    df_at = pd.read_csv(atip_path)
    for col in ["detectado_iqr", "detectado_z_robusto_mad", "detectado_isolation_forest", "decision_documentada"]:
        assert col in df_at.columns
    # Verificar que el choque histórico de febrero-marzo 2022 en origen Colima se haya detectado y conservado
    df_sniim_p = pd.read_csv(PLATA_DIR / "precios_sniim_mensual_plata.csv")
    feb_2022 = df_sniim_p[(df_sniim_p["id_mercado"] == "MKT-COL") & (df_sniim_p["anio_mes"] == "2022-02")]
    assert len(feb_2022) == 1
    assert bool(feb_2022.iloc[0]["es_choque_legitimo_dominio"]) is True


def test_escalado_discretizacion_jerarquias_y_reduccion():
    esc_path = PLATA_DIR / "comparativa_escalado.csv"
    jer_path = PLATA_DIR / "catalogo_jerarquias_conceptuales.json"
    red_path = PLATA_DIR / "metricas_reduccion_datos.json"
    assert esc_path.exists() and jer_path.exists() and red_path.exists()

    df_esc = pd.read_csv(esc_path)
    assert len(df_esc) >= 6
    assert (df_esc["zscore_media"].abs() < 1e-3).all()

    with open(red_path, encoding="utf-8") as f:
        red = json.load(f)
    assert red["etapa_1_agregacion_temporal_clima"]["reduccion_filas_pct"] > 95.0
