"""
Verificador determinista de entregables de la Etapa E2.
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]

ARCHIVOS_REQUERIDOS_E2 = [
    "extractores/geoespacial_osm.py",
    "pipeline/geoespacial_e2.py",
    "pipeline/linaje_datos.py",
    "pipeline/experimento_doe_e2.py",
    "pipeline/evaluacion_iso_e2.py",
    "pipeline/figuras_e2.py",
    "data/bronce/geoespacial/municipios_colima_osm.geojson",
    "data/bronce/geoespacial/municipios_colima_osm.geojson.meta.json",
    "data/bronce/geoespacial/infraestructura_agrologistica_colima_osm.geojson",
    "data/bronce/geoespacial/infraestructura_agrologistica_colima_osm.geojson.meta.json",
    "data/bronce/robots_txt/nominatim.openstreetmap.org_robots.txt",
    "data/bronce/robots_txt/overpass-api.de_robots.txt",
    "data/plata/infraestructura_agrologistica_colima_plata.geojson",
    "data/cuarentena/cuarentena_geoespacial_e2.csv",
    "data/oro/perfil_geoespacial_municipios_oro.geojson",
    "data/oro/perfil_geoespacial_municipios_oro.csv",
    "data/oro/resumen_geoespacial_e2.json",
    "data/oro/linaje_datos_e2.json",
    "data/oro/catalogo_linaje_oro_bronce.csv",
    "data/oro/experimento_factorial_2_3_corridas_e2.csv",
    "data/oro/anova_factorial_2_3_e2.csv",
    "data/oro/efectos_factorial_2_3_e2.csv",
    "data/oro/experimento_dos_factores_2x3_e2.csv",
    "data/oro/anova_dos_vias_2x3_e2.csv",
    "data/oro/matriz_2_4_completo_vs_fraccionado_e2.csv",
    "data/oro/estructura_alias_2_4_fraccionado_e2.csv",
    "data/oro/corrida_confirmacion_optimo_e2.csv",
    "data/oro/resumen_experimento_doe_e2.json",
    "data/oro/evaluacion_iso_25010_e2.csv",
    "data/oro/evaluacion_iso_25012_e2.csv",
    "data/oro/resumen_evaluacion_iso_e2.json",
    "docs/etica-datos.md",
    "docs/evaluacion-iso-25010-25012.md",
    "docs/relatoria-E2.md",
    "docs/E2/ENTREGA.md",
    "docs/E2/experimento_y_geodatos.ipynb",
    "laboratorio/e2_geoespacial_experimento_linaje.ipynb",
    "docs/E2/figuras/fig1_mapa_geoespacial_colima_e2.png",
    "docs/E2/figuras/fig2_arquitectura_linaje_bronce_oro_e2.png",
    "docs/E2/figuras/fig3_doe_factorial_2_3_efectos_pareto.png",
    "docs/E2/figuras/fig4_anova_dos_vias_y_supuestos_residuos.png",
    "docs/E2/figuras/fig5_fraccionado_2_4_y_confirmacion_optimo.png",
]


def verificar_e2() -> int:
    faltantes = []
    for rel in ARCHIVOS_REQUERIDOS_E2:
        p = ROOT_DIR / rel
        if not p.exists() or p.stat().st_size == 0:
            faltantes.append(rel)

    if faltantes:
        print(f"[ERROR] Archivos faltantes o vacíos en E2: {faltantes}")
        return 1

    geo = json.loads((ROOT_DIR / "data/oro/resumen_geoespacial_e2.json").read_text(encoding="utf-8"))
    lin = json.loads((ROOT_DIR / "data/oro/linaje_datos_e2.json").read_text(encoding="utf-8"))
    doe = json.loads((ROOT_DIR / "data/oro/resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))
    iso = json.loads((ROOT_DIR / "data/oro/resumen_evaluacion_iso_e2.json").read_text(encoding="utf-8"))

    assert geo["tasa_conservacion_masa_ok"] is True
    assert geo["columnas_pii_detectadas"] == 0
    assert lin["cobertura_trazabilidad_pct"] == 100.0
    assert iso["seguridad_estatica"]["secretos_expuestos"] == 0

    print("=================================================================")
    print(" VERIFICACIÓN DETERMINISTA E2 — CITRO-DATA LAB COLIMA: EXITOSA")
    print("=================================================================")
    print(f" * Archivos obligatorios verificados: {len(ARCHIVOS_REQUERIDOS_E2)}/{len(ARCHIVOS_REQUERIDOS_E2)}")
    print(f" * Geoespacial Colima (sjoin within): {geo['puntos_aprobados_dentro_colima_plata']} válidos + {geo['puntos_enviados_cuarentena_fuera_colima']} cuarentena (0 PII)")
    print(f" * Linaje Capa Oro:                   {lin['total_registros_oro_rastreados']} registros ({lin['cobertura_trazabilidad_pct']}%)")
    print(f" * Óptimo DOE 2^3 confirmado:         {doe['diseno_2_3']['tratamiento_optimo']} (-{doe['corrida_confirmacion']['mejora_tiempo_pct']}% tiempo, -{doe['corrida_confirmacion']['reduccion_disco_pct']}% disco)")
    print(f" * ISO/IEC 25010 / 25012:             {iso['iso_25010_promedio_100']}/100 | {iso['iso_25012_promedio_100']}/100 (0 secretos)")
    return 0


if __name__ == "__main__":
    sys.exit(verificar_e2())
