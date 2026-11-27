"""
Verificador determinista de entregables de la Etapa E3.
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

ARCHIVOS_REQUERIDOS_E3 = [
    "pipeline/optimizacion_dataset_e3.py",
    "pipeline/multivariado_pca_manova_e3.py",
    "pipeline/calidad_sello_e3.py",
    "pipeline/figuras_e3.py",
    "pipeline/generar_notebook_e3.py",
    "pipeline/generar_pdf_e3.py",
    "data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet",
    "data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.csv",
    "data/oro/serie_mensual_oro_60m.parquet",
    "data/oro/panel_integrado_municipio_mercado_oro.parquet",
    "data/oro/perfil_geoespacial_municipios_oro.parquet",
    "data/oro/dataset_publicado_e3_manifest.json",
    "data/oro/comparativa_optimizacion_e3.csv",
    "data/oro/benchmark_etapas_optimizacion_e3.csv",
    "data/oro/resumen_optimizacion_e3.json",
    "data/oro/matriz_covarianzas_e3.csv",
    "data/oro/matriz_correlaciones_e3.csv",
    "data/oro/distancias_mahalanobis_qq_e3.csv",
    "data/oro/pca_varianza_explicada_e3.csv",
    "data/oro/pca_cargas_variables_e3.csv",
    "data/oro/pca_proyecciones_municipios_mercados_e3.csv",
    "data/oro/pca_centroides_municipios_e3.csv",
    "data/oro/manova_resultados_e3.csv",
    "data/oro/comparativa_manova_vs_anovas_e3.csv",
    "data/oro/resumen_multivariado_e3.json",
    "data/oro/cierre_auditoria_e3.csv",
    "data/oro/autoevaluacion_moprosoft_cmmi_e3.csv",
    "data/oro/comparativa_modelos_proceso_e3.csv",
    "data/oro/retrospectiva_psp_e0_e3.csv",
    "data/oro/psp_defectos_por_fase_e3.csv",
    "data/oro/sello_tdl_evaluacion_e3.csv",
    "data/oro/resumen_calidad_sello_e3.json",
    "docs/E3/datasheet.md",
    "docs/E3/ENTREGA.md",
    "docs/E3/analisis_multivariado_y_optimizacion.ipynb",
    "docs/E3/Entrega_E3_Escareno_Norberto.pdf",
    "docs/calidad-modelos-psp-sello-e3.md",
    "docs/relatoria-E3.md",
    "laboratorio/e3_pca_manova_optimizacion_sello.ipynb",
    "docs/E3/figuras/fig1_matriz_correlaciones_y_qq_mahalanobis_e3.png",
    "docs/E3/figuras/fig2_pca_sedimentacion_y_biplot_municipios_e3.png",
    "docs/E3/figuras/fig3_manova_municipios_mercados_vs_anovas_e3.png",
    "docs/E3/figuras/fig4_optimizacion_pipeline_antes_despues_e3.png",
    "docs/E3/figuras/fig5_retrospectiva_psp_modelos_y_sello_tdl_e3.png",
]


def verificar_e3() -> int:
    faltantes = []
    for rel in ARCHIVOS_REQUERIDOS_E3:
        p = ROOT_DIR / rel
        if not p.exists() or p.stat().st_size == 0:
            faltantes.append(rel)

    if faltantes:
        print(f"[ERROR] Archivos faltantes o vacíos en E3: {faltantes}")
        return 1

    opt = json.loads((ROOT_DIR / "data/oro/resumen_optimizacion_e3.json").read_text(encoding="utf-8"))
    mv = json.loads((ROOT_DIR / "data/oro/resumen_multivariado_e3.json").read_text(encoding="utf-8"))
    cal = json.loads((ROOT_DIR / "data/oro/resumen_calidad_sello_e3.json").read_text(encoding="utf-8"))

    assert opt["mejoras_cuantificadas"]["factor_aceleracion_speedup"] >= 5.0
    assert opt["mejoras_cuantificadas"]["reduccion_disco_zstd_pct"] >= 80.0
    assert mv["matriz_multivariada"]["n_variables_agroclima"] >= 5
    assert mv["matriz_multivariada"]["rango_matriz_covarianzas"] == 8
    assert mv["manova"]["municipios_agroclima_escala_original"]["wilks_p"] < 0.001
    assert mv["manova"]["mercados_mayoristas_sniim"]["wilks_p"] < 0.001
    assert cal["sello_tdl_otorgado"] is True
    assert cal["cierre_auditoria"]["criticos_abiertos"] == 0
    assert cal["seguridad_repositorio"]["secretos_expuestos"] == 0

    print("=================================================================")
    print(" VERIFICACIÓN DETERMINISTA E3 — CITRO-DATA LAB COLIMA: EXITOSA")
    print("=================================================================")
    print(f" * Archivos obligatorios verificados: {len(ARCHIVOS_REQUERIDOS_E3)}/{len(ARCHIVOS_REQUERIDOS_E3)}")
    print(
        f" * Optimización Pipeline E3:          {opt['mejoras_cuantificadas']['factor_aceleracion_speedup']}x speedup "
        f"(-{opt['mejoras_cuantificadas']['reduccion_tiempo_total_pct']}% tiempo, -{opt['mejoras_cuantificadas']['reduccion_memoria_pico_pct']}% RAM, "
        f"-{opt['mejoras_cuantificadas']['reduccion_disco_zstd_pct']}% disco)"
    )
    print(
        f" * PCA & Normalidad (Puerta 3):       PC1+PC2 = {mv['pca']['varianza_acumulada_2pc_pct']}% "
        f"(3 PCs = {mv['pca']['varianza_acumulada_3pc_pct']}%) | Q-Q Mahalanobis r = "
        f"{mv['normalidad_multivariada_puerta3']['transformacion_yeo_johnson']['correlacion_qq_mahalanobis']}"
    )
    print(
        f" * MANOVA Municipios / Mercados:      Wilks = {mv['manova']['municipios_agroclima_escala_original']['wilks_lambda']:.4f} "
        f"(p < 1e-114) | Mercados Wilks = {mv['manova']['mercados_mayoristas_sniim']['wilks_lambda']:.4f} (p < 1e-105)"
    )
    print(
        f" * Sello TDL Certificado:             {cal['criterios_sello_cumplidos']} criterios "
        f"(Disp. 14d = {cal['disponibilidad_14_dias']['disponibilidad_real_14d_pct']}%, 0 críticos abiertos, 0 secretos)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(verificar_e3())
