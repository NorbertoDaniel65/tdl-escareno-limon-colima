"""
Generador del Notebook Reproducible E2:
- laboratorio/e2_geoespacial_experimento_linaje.ipynb
- docs/E2/experimento_y_geodatos.ipynb
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import nbformat as nbf

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"


def generar_notebook_e2() -> tuple[Path, Path]:
    res_geo = json.loads((ORO_DIR / "resumen_geoespacial_e2.json").read_text(encoding="utf-8"))
    res_lin = json.loads((ORO_DIR / "linaje_datos_e2.json").read_text(encoding="utf-8"))
    res_doe = json.loads((ORO_DIR / "resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))
    res_iso = json.loads((ORO_DIR / "resumen_evaluacion_iso_e2.json").read_text(encoding="utf-8"))

    nb = nbf.v4.new_notebook()
    celdas = [
        nbf.v4.new_markdown_cell(
            "# CITRO-DATA LAB COLIMA — Laboratorio Reproducible E2\n"
            "## Fuente Especializada Geoespacial, Linaje de Datos, Diseño de Experimentos ($2^3$, $2\\times 3$, $2^{4-1}$) e ISO/IEC 25010–25012\n\n"
            "* **Estudiante:** Norberto Daniel Escareño Montaño (`23460323` · `@NorbertoDaniel65`)\n"
            "* **Asignaturas:** Ingeniería de Datos (`CMD-2602`) · Análisis Estadístico para Ciencia de Datos\n"
            "* **Etapa:** `E2` (Tag `e2`)\n"
        ),
        nbf.v4.new_markdown_cell(
            "## 1. Fuente Especializada Geoespacial (OpenStreetMap + INEGI) y Unión Espacial `GeoPandas`\n"
            f"- **Polígonos municipales de Colima (`EPSG:4326`):** `{res_geo['poligonos_municipales_colima']}` (`4` núcleos citrícolas + `6` vecinos)\n"
            f"- **Unión espacial `gpd.sjoin(puntos, poligonos, predicate='within')`:** `{res_geo['puntos_bronce_evaluados']}` evaluados $\\to$ "
            f"`{res_geo['puntos_aprobados_dentro_colima_plata']}` aprobados en Colima + `{res_geo['puntos_enviados_cuarentena_fuera_colima']}` en cuarentena (0 borrados silenciosamente, `0` PII)."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import json\n"
            "import pandas as pd\n"
            "import geopandas as gpd\n\n"
            "ROOT = Path('..').resolve() if Path.cwd().name in ('laboratorio', 'E2') else Path('.').resolve()\n"
            "if not (ROOT / 'data').exists():\n"
            "    ROOT = ROOT.parent\n\n"
            "gdf_oro = gpd.read_file(ROOT / 'data/oro/perfil_geoespacial_municipios_oro.geojson')\n"
            "cols = ['cvegeo','nombre_oficial','en_observatorio_citricola','superficie_km2',\n"
            "        'n_huertas_citricolas_osm','n_empaque_bodega_osm','n_mercados_abasto_osm',\n"
            "        'n_nodos_agrologisticos_total','dist_puerto_manzanillo_km','dist_corredor_gdl_54d_km']\n"
            "gdf_oro[cols]"
        ),
        nbf.v4.new_markdown_cell(
            "## 2. Linaje y Trazabilidad Completa de Datos (Capa Bronce $\\to$ Capa Oro)\n"
            f"- **Cobertura verificada:** `{res_lin['cobertura_trazabilidad_pct']}%` (`{res_lin['total_registros_oro_rastreados']}` registros maestros en Capa Oro rastreables hasta archivo Bronce, `SHA-256` y fecha UTC)."
        ),
        nbf.v4.new_code_cell(
            "import sys\n"
            "sys.path.insert(0, str(ROOT))\n"
            "from pipeline.linaje_datos import rastrear_registro_oro\n\n"
            "traza = rastrear_registro_oro('ORO-SERIE-2022-02')\n"
            "print(json.dumps(traza['registro_oro'], indent=2, ensure_ascii=False))\n"
            "print('Etapas DAG:', traza['cadena_etapas'])"
        ),
        nbf.v4.new_markdown_cell(
            "## 3. Experimento Factorial Real $2^3$, ANOVA de Dos Vías ($2\\times 3$) y $2^4$ vs. $2^{4-1}$ Fraccionado\n"
            f"- **Óptimo $2^3$:** `{res_doe['diseno_2_3']['tratamiento_optimo']}` (`4_Hilos_Paralelo + Pandera_Vectorizado + Parquet_Snappy`)\n"
            f"- **Puerta 3 (Supuestos de Residuos):** Shapiro-Wilk `W={res_doe['diseno_2_3']['supuestos_residuos_escala_lineal']['shapiro_wilk_W']}` (`p={res_doe['diseno_2_3']['supuestos_residuos_escala_lineal']['shapiro_wilk_p']}`), "
            f"Levene `p={res_doe['diseno_2_3']['supuestos_residuos_escala_lineal']['levene_p']}`, Durbin-Watson `DW={res_doe['diseno_2_3']['supuestos_residuos_escala_lineal']['durbin_watson']}`.\n"
            f"- **Confirmación ($n=5$):** Observado `{res_doe['corrida_confirmacion']['observado_optimo_media_ms']} ms` dentro de IC 95% `{res_doe['corrida_confirmacion']['ic95_prediccion_ms']}` $\\implies$ "
            f"**`-{res_doe['corrida_confirmacion']['mejora_tiempo_pct']}%` tiempo (`{res_doe['corrida_confirmacion']['factor_aceleracion_speedup']}×` speedup) y `-{res_doe['corrida_confirmacion']['reduccion_disco_pct']}%` disco.**"
        ),
        nbf.v4.new_code_cell(
            "anova_23 = pd.read_csv(ROOT / 'data/oro/anova_factorial_2_3_e2.csv')\n"
            "efectos_23 = pd.read_csv(ROOT / 'data/oro/efectos_factorial_2_3_e2.csv')\n"
            "anova_2x3 = pd.read_csv(ROOT / 'data/oro/anova_dos_vias_2x3_e2.csv')\n"
            "alias_24 = pd.read_csv(ROOT / 'data/oro/estructura_alias_2_4_fraccionado_e2.csv')\n"
            "print('=== ANOVA FACTORIAL 2^3 ===')\n"
            "display(anova_23)\n"
            "print('=== EFECTOS ESTANDARIZADOS 2^3 ===')\n"
            "display(efectos_23)\n"
            "print('=== ANOVA DOS VIAS 2x3 ===')\n"
            "display(anova_2x3)\n"
            "print('=== ESTRUCTURA DE ALIAS 2^(4-1) RESOLUCION IV ===')\n"
            "display(alias_24)"
        ),
        nbf.v4.new_markdown_cell(
            "## 4. Evaluación ISO/IEC 25010 (Producto) e ISO/IEC 25012 (Datos)\n"
            f"- **ISO/IEC 25010 promedio:** `{res_iso['iso_25010_promedio_100']}/100`\n"
            f"- **ISO/IEC 25012 promedio:** `{res_iso['iso_25012_promedio_100']}/100` (Completitud `100.0%`, Linaje `100.0%`, `0` secretos expuestos)."
        ),
        nbf.v4.new_code_cell(
            "iso_25010 = pd.read_csv(ROOT / 'data/oro/evaluacion_iso_25010_e2.csv')\n"
            "iso_25012 = pd.read_csv(ROOT / 'data/oro/evaluacion_iso_25012_e2.csv')\n"
            "display(iso_25010)\n"
            "display(iso_25012)"
        ),
    ]
    nb["cells"] = celdas

    ruta_lab = ROOT_DIR / "laboratorio" / "e2_geoespacial_experimento_linaje.ipynb"
    ruta_docs = ROOT_DIR / "docs" / "E2" / "experimento_y_geodatos.ipynb"
    ruta_lab.parent.mkdir(parents=True, exist_ok=True)
    ruta_docs.parent.mkdir(parents=True, exist_ok=True)

    with ruta_lab.open("w", encoding="utf-8") as f:
        nbf.write(nb, f)
    shutil.copy2(ruta_lab, ruta_docs)
    return ruta_lab, ruta_docs


if __name__ == "__main__":
    r1, r2 = generar_notebook_e2()
    print(f"[OK] Notebooks E2 generados: {r1.relative_to(ROOT_DIR)} y {r2.relative_to(ROOT_DIR)}")
