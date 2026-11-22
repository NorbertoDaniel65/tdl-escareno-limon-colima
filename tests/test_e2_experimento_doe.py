"""
Pruebas unitarias y de integración para la Etapa E2 — Análisis Estadístico (Unidad 4):
Diseño Factorial 2^3 (aleatorizado, réplicas, bloques), ANOVA de Dos Vías 2x3 con Interacción,
Diseño 2^4 Completo vs. 2^(4-1) Fraccionado (Resolución IV, alias, 50% ahorro),
Puerta de Calidad 3 (supuestos de residuos) y Corrida de Confirmación del Óptimo.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
FIGURAS_E2_DIR = ROOT_DIR / "docs" / "E2" / "figuras"


def test_diseno_factorial_2_3_principios_y_puerta_3_supuestos():
    df_23 = pd.read_csv(ORO_DIR / "experimento_factorial_2_3_corridas_e2.csv")
    assert len(df_23) == 24
    assert df_23["tratamiento"].nunique() == 8
    assert df_23["bloque"].nunique() == 3
    assert (df_23["tasa_error_pct"] == 0.0).all()

    res = json.loads((ORO_DIR / "resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))
    sup = res["diseno_2_3"]["supuestos_residuos_escala_lineal"]
    assert sup["r2_modelo"] > 0.90
    assert sup["normalidad_aprobada_5pct"] is True
    assert sup["homocedasticidad_aprobada_5pct"] is True
    assert sup["independencia_aprobada"] is True


def test_anova_dos_vias_2x3_y_reduccion_disco_parquet():
    df_2x3 = pd.read_csv(ORO_DIR / "experimento_dos_factores_2x3_e2.csv")
    assert len(df_2x3) == 18
    assert df_2x3["motor_validacion"].nunique() == 2
    assert df_2x3["formato_persistencia"].nunique() == 3

    df_anova = pd.read_csv(ORO_DIR / "anova_dos_vias_2x3_e2.csv")
    assert df_anova["termino"].str.contains(":").any(), "Falta término de interacción en ANOVA 2x3"

    tam = df_2x3.groupby("formato_persistencia")["tamano_disco_kb"].mean()
    assert tam["parquet_snappy"] < tam["csv_utf8"] * 0.20
    assert tam["parquet_zstd"] < tam["csv_utf8"] * 0.20


def test_diseno_2_4_completo_vs_fraccionado_resolucion_iv_y_alias():
    df_24 = pd.read_csv(ORO_DIR / "matriz_2_4_completo_vs_fraccionado_e2.csv")
    assert len(df_24) == 16
    frac = df_24[df_24["incluida_en_2_4_menos_1"]]
    assert len(frac) == 8
    # Verificar generador definitorio D = A * B * C (I = ABCD) en todas las filas de la fracción
    assert ((frac["A_paralelismo"] * frac["B_validacion"] * frac["C_formato"]) == frac["D_particion"]).all()

    df_alias = pd.read_csv(ORO_DIR / "estructura_alias_2_4_fraccionado_e2.csv")
    assert len(df_alias) == 7
    assert any("AB + CD" in s for s in df_alias["alias_en_2_4_menos_1"])


def test_corrida_confirmacion_optimo_dentro_ic95_y_figuras_e2():
    res = json.loads((ORO_DIR / "resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))
    conf = res["corrida_confirmacion"]
    assert conf["n_confirmacion_por_escenario"] == 5
    assert conf["dentro_intervalo_prediccion_95"] is True
    assert conf["mejora_tiempo_pct"] > 50.0
    assert conf["reduccion_disco_pct"] > 80.0
    assert conf["tasa_error_confirmacion_pct"] == 0.0

    for fig in [
        "fig1_mapa_geoespacial_colima_e2.png",
        "fig2_arquitectura_linaje_bronce_oro_e2.png",
        "fig3_doe_factorial_2_3_efectos_pareto.png",
        "fig4_anova_dos_vias_y_supuestos_residuos.png",
        "fig5_fraccionado_2_4_y_confirmacion_optimo.png",
    ]:
        p = FIGURAS_E2_DIR / fig
        assert p.exists() and p.stat().st_size > 20000

    assert (ROOT_DIR / "docs" / "E2" / "experimento_y_geodatos.ipynb").exists()
    assert (ROOT_DIR / "laboratorio" / "e2_geoespacial_experimento_linaje.ipynb").exists()
