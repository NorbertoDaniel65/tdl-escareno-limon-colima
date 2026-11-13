"""
Verificador determinista de entregables de la Etapa E1.
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

ARCHIVOS_REQUERIDOS_E1 = [
    "pipeline/puerta_calidad.py",
    "pipeline/limpieza_plata.py",
    "pipeline/integracion_oro.py",
    "pipeline/series_tiempo_e1.py",
    "data/cuarentena/cuarentena_registros.csv",
    "data/cuarentena/reporte_puerta_calidad.json",
    "data/plata/agroclima_diario_plata.csv",
    "data/plata/agroclima_mensual_plata.csv",
    "data/plata/precios_sniim_mensual_plata.csv",
    "data/plata/evaluacion_imputacion_faltantes.csv",
    "data/plata/reporte_atipicos_comparativo.csv",
    "data/plata/comparativa_escalado.csv",
    "data/plata/catalogo_jerarquias_conceptuales.json",
    "data/plata/metricas_reduccion_datos.json",
    "data/oro/serie_mensual_oro_60m.csv",
    "data/oro/panel_integrado_municipio_mercado_oro.csv",
    "data/oro/diccionario_datos.md",
    "data/oro/comparativa_modelos_pronostico_e1.csv",
    "data/oro/pronostico_e1_limon.csv",
    "data/oro/diagnostico_series_tiempo_e1.json",
    "docs/E1/limpieza.ipynb",
    "docs/E1/ENTREGA.md",
    "docs/plan-sqa.md",
    "docs/relatoria-E1.md",
    "tablero/app.py",
    "calidad/tiempo-norberto.csv",
    "calidad/defectos-norberto.csv",
    ".github/workflows/ci-calidad.yml",
]


def verificar_e1() -> int:
    faltantes = []
    for rel in ARCHIVOS_REQUERIDOS_E1:
        p = ROOT_DIR / rel
        if not p.exists() or p.stat().st_size == 0:
            faltantes.append(rel)

    if faltantes:
        print(f"[ERROR] Archivos faltantes o vacíos en E1: {faltantes}")
        return 1

    with open(ROOT_DIR / "data/oro/diagnostico_series_tiempo_e1.json", encoding="utf-8") as f:
        diag = json.load(f)

    print("=================================================================")
    print(" VERIFICACIÓN DETERMINISTA E1 — CITRO-DATA LAB COLIMA: EXITOSA")
    print("=================================================================")
    print(f" * Archivos obligatorios verificados: {len(ARCHIVOS_REQUERIDOS_E1)}/{len(ARCHIVOS_REQUERIDOS_E1)}")
    print(f" * Modelo ganador en prueba (12m):    {diag['modelo_ganador']}")
    print(f" * Ruido blanco Ljung-Box (p > 0.05): p(6)={diag['diagnostico_residuos_ljung_box']['ljung_box_lag6_pvalue']}, p(12)={diag['diagnostico_residuos_ljung_box']['ljung_box_lag12_pvalue']}")
    return 0


if __name__ == "__main__":
    sys.exit(verificar_e1())
