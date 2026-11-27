"""
Suite de pruebas unitarias e integrales para la Entrega E3:
Optimización medida del pipeline, Dataset publicado con Datasheet CC BY 4.0,
Matriz multivariada, Normalidad multivariada (Mardia, Henze-Zirkler, Q-Q Mahalanobis),
PCA con nombres de negocio, MANOVA (Wilks y Pillai vs. ANOVAs separados),
Cierre de auditoría, MoProSoft/CMMI, Retrospectiva PSP y Sello TDL.

CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from pipeline.verificar_e3 import verificar_e3

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"


def test_optimizacion_medida_antes_despues_e3() -> None:
    """Verifica que la optimización E3 reduzca significativamente tiempo, RAM y disco con 0 errores."""
    res_opt = json.loads((ORO_DIR / "resumen_optimizacion_e3.json").read_text(encoding="utf-8"))
    mej = res_opt["mejoras_cuantificadas"]
    assert mej["factor_aceleracion_speedup"] >= 5.0
    assert mej["reduccion_tiempo_total_pct"] >= 80.0
    assert mej["reduccion_memoria_pico_pct"] >= 50.0
    assert mej["reduccion_disco_zstd_pct"] >= 80.0
    assert mej["tasa_error_corrupcion_pct"] == 0.0
    assert mej["welch_p_valor"] < 1e-6


def test_dataset_publicado_parquet_y_datasheet_e3() -> None:
    """Verifica que el dataset publicado exista en Parquet y CSV con licencia CC BY 4.0, 0 nulos y 0 PII."""
    pq_path = ORO_DIR / "CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet"
    csv_path = ORO_DIR / "CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.csv"
    manifest_path = ORO_DIR / "dataset_publicado_e3_manifest.json"
    datasheet_path = ROOT_DIR / "docs" / "E3" / "datasheet.md"

    assert pq_path.exists() and pq_path.stat().st_size > 1000
    assert csv_path.exists() and csv_path.stat().st_size > 1000
    assert manifest_path.exists()
    assert datasheet_path.exists()

    df_pq = pd.read_parquet(pq_path)
    df_csv = pd.read_csv(csv_path)
    assert len(df_pq) == 240
    assert df_pq.shape == df_csv.shape
    assert int(df_pq.isna().sum().sum()) == 0
    assert "linaje_id_registro" in df_pq.columns
    assert "linaje_sha256_bronce" in df_pq.columns

    texto_ds = datasheet_path.read_text(encoding="utf-8")
    for seccion in ["Motivación", "Composición", "Captura", "Preprocesamiento", "Usos Recomendados", "CC BY 4.0", "Mantenimiento"]:
        assert seccion in texto_ds


def test_matriz_multivariada_y_normalidad_puerta3_e3() -> None:
    """Verifica matriz de >=5 variables de rango completo, pruebas de Mardia/Henze-Zirkler y Q-Q Mahalanobis."""
    cov_df = pd.read_csv(ORO_DIR / "matriz_covarianzas_e3.csv").set_index("variable")
    corr_df = pd.read_csv(ORO_DIR / "matriz_correlaciones_e3.csv").set_index("variable")
    qq_df = pd.read_csv(ORO_DIR / "distancias_mahalanobis_qq_e3.csv")
    res_mv = json.loads((ORO_DIR / "resumen_multivariado_e3.json").read_text(encoding="utf-8"))

    assert cov_df.shape == (8, 8)
    assert corr_df.shape == (8, 8)
    assert int(np.linalg.matrix_rank(cov_df.to_numpy())) == 8
    assert np.allclose(np.diag(corr_df.to_numpy()), 1.0, atol=1e-3)
    assert len(qq_df) == 240

    norm_yj = res_mv["normalidad_multivariada_puerta3"]["transformacion_yeo_johnson"]
    assert norm_yj["correlacion_qq_mahalanobis"] >= 0.99
    assert norm_yj["mardia_p_curtosis"] > 0.05
    assert norm_yj["pct_dentro_chi2_95"] >= 93.0


def test_pca_nombres_negocio_y_biplot_e3() -> None:
    """Verifica que el PCA estandarizado tenga componentes nombrados, varianza explicada y proyecciones completas."""
    scree_df = pd.read_csv(ORO_DIR / "pca_varianza_explicada_e3.csv")
    cargas_df = pd.read_csv(ORO_DIR / "pca_cargas_variables_e3.csv")
    proy_df = pd.read_csv(ORO_DIR / "pca_proyecciones_municipios_mercados_e3.csv")

    assert len(scree_df) == 8
    assert abs(float(scree_df["varianza_explicada_pct"].sum()) - 100.0) < 0.1
    assert float(scree_df["varianza_acumulada_pct"].iloc[1]) >= 60.0
    assert float(scree_df["varianza_acumulada_pct"].iloc[2]) >= 75.0
    assert all(scree_df["nombre_negocio"].str.len() > 10)
    assert len(cargas_df) == 8
    assert len(proy_df) == 240
    assert {"PC1_estres_termo_evaporativo", "PC2_humedad_pluvial_costera", "cuadrante_negocio_biplot"}.issubset(proy_df.columns)


def test_manova_wilks_pillai_vs_anovas_e3() -> None:
    """Verifica los contrastes MANOVA (Wilks y Pillai) y la comparativa contra ANOVAs univariados separados."""
    manova_df = pd.read_csv(ORO_DIR / "manova_resultados_e3.csv")
    anovas_df = pd.read_csv(ORO_DIR / "comparativa_manova_vs_anovas_e3.csv")
    res_mv = json.loads((ORO_DIR / "resumen_multivariado_e3.json").read_text(encoding="utf-8"))

    estadisticos = set(manova_df["estadistico"].unique())
    assert any("Wilks" in s for s in estadisticos)
    assert any("Pillai" in s for s in estadisticos)
    assert bool(manova_df["significativo_5pct"].all())
    assert len(anovas_df) == 8
    assert res_mv["manova"]["contraste_vs_anovas_separados"]["riesgo_error_tipo_I_global_anovas_separados_pct"] == 33.66


def test_cierre_auditoria_modelos_y_retrospectiva_psp_e3() -> None:
    """Verifica 0 hallazgos críticos abiertos, autoevaluación MoProSoft/CMMI y retrospectiva PSP E0->E3."""
    aud_df = pd.read_csv(ORO_DIR / "cierre_auditoria_e3.csv")
    auto_df = pd.read_csv(ORO_DIR / "autoevaluacion_moprosoft_cmmi_e3.csv")
    comp_df = pd.read_csv(ORO_DIR / "comparativa_modelos_proceso_e3.csv")
    retro_df = pd.read_csv(ORO_DIR / "retrospectiva_psp_e0_e3.csv")

    assert len(aud_df) == 5
    assert all(aud_df["estado_final_e3"].str.contains("CERRADO"))
    assert len(auto_df) >= 5
    assert len(comp_df) == 5
    assert len(retro_df) == 4
    # En E3 el Yield de revisión temprana alcanza 100%
    e3_row = retro_df[retro_df["etapa"] == "E3_Multivariado_Sello"].iloc[0]
    assert float(e3_row["yield_revision_pct"]) == 100.0


def test_certificacion_sello_tdl_6_criterios_e3() -> None:
    """Verifica que los 6 criterios oficiales del Sello TDL se cumplan al 100%."""
    sello_df = pd.read_csv(ORO_DIR / "sello_tdl_evaluacion_e3.csv")
    res_cal = json.loads((ORO_DIR / "resumen_calidad_sello_e3.json").read_text(encoding="utf-8"))

    assert len(sello_df) == 6
    assert bool(sello_df["cumple"].all())
    assert res_cal["sello_tdl_otorgado"] is True
    assert res_cal["disponibilidad_14_dias"]["disponibilidad_real_14d_pct"] >= 95.0
    assert res_cal["cierre_auditoria"]["criticos_abiertos"] == 0
    assert res_cal["seguridad_repositorio"]["secretos_expuestos"] == 0


def test_verificador_determinista_e3() -> None:
    """Ejecuta el verificador oficial de la Etapa E3 y comprueba código de salida 0."""
    assert verificar_e3() == 0
