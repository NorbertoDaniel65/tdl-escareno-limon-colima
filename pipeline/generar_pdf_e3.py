"""
Generador determinista del Reporte Integral PDF de la Entrega E3:
docs/E3/Entrega_E3_Escareno_Norberto.pdf (y copia en scratch/).
Aplica estrictamente el Molde Oficial TecNM — Instituto Tecnológico de Colima:
  - Encabezado con Logo TecNM (izquierda) y Escudo IT Colima (derecha) repetido en TODAS las páginas.
  - Portada limpia en Página 1 (fondo blanco, tipografía Arial negra centrada en negrita).
  - Contenido sobrio en páginas 2+ con tablas limpias y las 5 figuras HD en Base64.
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
import shutil
import subprocess

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
FIGURAS_DIR = ROOT_DIR / "docs" / "E3" / "figuras"
PLANTILLA_DIR = ROOT_DIR.parent / "plantilla_tecnm"


def _img_b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _df_html(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0, classes="tabla-datos")


def generar_pdf_e3() -> Path:
    logo_tecnm = _img_b64(PLANTILLA_DIR / "logo_tecnm.png")
    logo_itc = _img_b64(PLANTILLA_DIR / "logo_itcolima.png")

    fig1 = _img_b64(FIGURAS_DIR / "fig1_matriz_correlaciones_y_qq_mahalanobis_e3.png")
    fig2 = _img_b64(FIGURAS_DIR / "fig2_pca_sedimentacion_y_biplot_municipios_e3.png")
    fig3 = _img_b64(FIGURAS_DIR / "fig3_manova_municipios_mercados_vs_anovas_e3.png")
    fig4 = _img_b64(FIGURAS_DIR / "fig4_optimizacion_pipeline_antes_despues_e3.png")
    fig5 = _img_b64(FIGURAS_DIR / "fig5_retrospectiva_psp_modelos_y_sello_tdl_e3.png")

    df_scree = pd.read_csv(ORO_DIR / "pca_varianza_explicada_e3.csv")
    df_cargas = pd.read_csv(ORO_DIR / "pca_cargas_variables_e3.csv")
    df_manova = pd.read_csv(ORO_DIR / "manova_resultados_e3.csv")
    df_anovas = pd.read_csv(ORO_DIR / "comparativa_manova_vs_anovas_e3.csv")
    df_bench = pd.read_csv(ORO_DIR / "benchmark_etapas_optimizacion_e3.csv")
    df_aud = pd.read_csv(ORO_DIR / "cierre_auditoria_e3.csv")
    df_auto = pd.read_csv(ORO_DIR / "autoevaluacion_moprosoft_cmmi_e3.csv")
    df_comp_mod = pd.read_csv(ORO_DIR / "comparativa_modelos_proceso_e3.csv")
    df_retro = pd.read_csv(ORO_DIR / "retrospectiva_psp_e0_e3.csv")
    df_sello = pd.read_csv(ORO_DIR / "sello_tdl_evaluacion_e3.csv")

    res_mv = json.loads((ORO_DIR / "resumen_multivariado_e3.json").read_text(encoding="utf-8"))
    res_opt = json.loads((ORO_DIR / "resumen_optimizacion_e3.json").read_text(encoding="utf-8"))
    res_cal = json.loads((ORO_DIR / "resumen_calidad_sello_e3.json").read_text(encoding="utf-8"))

    m_mun = res_mv["manova"]["municipios_agroclima_escala_original"]
    m_mkt = res_mv["manova"]["mercados_mayoristas_sniim"]
    norm_yj = res_mv["normalidad_multivariada_puerta3"]["transformacion_yeo_johnson"]
    mej = res_opt["mejoras_cuantificadas"]
    disp14 = res_cal["disponibilidad_14_dias"]

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Entrega E3 — CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño</title>
<style>
  @page {{
    size: letter;
    margin: 12mm 15mm 14mm 15mm;
  }}
  body {{
    font-family: Arial, Calibri, 'Segoe UI', sans-serif;
    font-size: 9.8pt;
    line-height: 1.40;
    color: #000000;
    background: #ffffff;
    margin: 0;
    padding: 0;
  }}
  table.marco-pagina {{
    width: 100%;
    max-width: 100%;
    table-layout: fixed;
    border-collapse: collapse;
  }}
  table.marco-pagina thead {{
    display: table-header-group;
  }}
  .encabezado-institucional {{
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 10px;
    border-bottom: 1px solid #d1d5db;
    padding-bottom: 4px;
  }}
  .encabezado-institucional td {{
    vertical-align: middle;
    padding: 0 0 6px 0;
  }}
  .logo-izq {{
    height: 48px;
    width: auto;
  }}
  .logo-der {{
    height: 52px;
    width: auto;
  }}
  .portada-bloque {{
    text-align: center;
    padding-top: 28px;
    min-height: 205mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
  }}
  .portada-linea-inst {{
    font-size: 14pt;
    font-weight: 700;
    margin: 4px 0;
    letter-spacing: 0.3px;
  }}
  .portada-depto {{
    font-size: 12pt;
    font-weight: 700;
    margin: 12px 0 4px 0;
  }}
  .portada-carrera {{
    font-size: 12.5pt;
    font-weight: 700;
    margin: 2px 0 22px 0;
  }}
  .portada-campo-etiq {{
    font-size: 11pt;
    font-weight: 700;
    margin: 16px 0 3px 0;
  }}
  .portada-campo-val {{
    font-size: 11.5pt;
    font-weight: 700;
    margin: 2px 0;
  }}
  .portada-sub {{
    font-size: 10pt;
    font-weight: 400;
    margin: 2px 0;
  }}
  .portada-pie {{
    text-align: right;
    font-size: 10.5pt;
    font-weight: 700;
    margin-top: 32px;
  }}
  .salto-pagina {{
    page-break-before: always;
  }}
  h2 {{
    font-size: 11.3pt;
    font-weight: 700;
    color: #000000;
    border-bottom: 1.5px solid #111827;
    padding-bottom: 2px;
    margin: 11px 0 5px 0;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 9.9pt;
    font-weight: 700;
    color: #111827;
    margin: 8px 0 3px 0;
    page-break-after: avoid;
  }}
  p, li {{
    margin: 3px 0;
    text-align: justify;
  }}
  .tabla-datos {{
    width: 100%;
    max-width: 100%;
    table-layout: auto;
    border-collapse: collapse;
    font-size: 7.2pt;
    margin: 4px 0 8px 0;
    page-break-inside: avoid;
  }}
  .tabla-datos th {{
    background-color: #f3f4f6;
    color: #000000;
    font-weight: 700;
    text-align: left;
    padding: 3px 4px;
    border: 1px solid #9ca3af;
    word-break: break-word;
    overflow-wrap: anywhere;
  }}
  .tabla-datos td {{
    padding: 2.8px 4px;
    border: 1px solid #d1d5db;
    vertical-align: top;
    word-break: break-word;
    overflow-wrap: anywhere;
  }}
  .tabla-datos tr:nth-child(even) {{
    background-color: #fafafa;
  }}
  .cuadro-nota {{
    border: 1px solid #9ca3af;
    border-left: 3.5px solid #111827;
    background-color: #f9fafb;
    padding: 6px 9px;
    margin: 6px 0;
    font-size: 8.6pt;
    page-break-inside: avoid;
  }}
  .figura {{
    width: 100%;
    height: auto;
    margin: 4px 0 7px 0;
    border: 1px solid #d1d5db;
    page-break-inside: avoid;
  }}
  code {{
    font-family: Consolas, 'Courier New', monospace;
    font-size: 8.4pt;
    background: #f3f4f6;
    padding: 0 2px;
  }}
</style>
</head>
<body>

<table class="marco-pagina">
  <thead>
    <tr>
      <td>
        <table class="encabezado-institucional">
          <tr>
            <td style="text-align:left; width:50%;"><img class="logo-izq" src="{logo_tecnm}" alt="TecNM"></td>
            <td style="text-align:right; width:50%;"><img class="logo-der" src="{logo_itc}" alt="IT Colima"></td>
          </tr>
        </table>
      </td>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>
        <!-- ==================== PÁGINA 1: PORTADA OFICIAL TECNM ==================== -->
        <div class="portada-bloque">
          <div>
            <div class="portada-linea-inst">TECNOLÓGICO NACIONAL DE MÉXICO</div>
            <div class="portada-linea-inst">INSTITUTO TECNOLÓGICO DE COLIMA</div>
            <div class="portada-depto">Departamento de Sistemas y Computación</div>
            <div class="portada-carrera">INGENIERÍA EN SISTEMAS COMPUTACIONALES</div>

            <div class="portada-campo-etiq">Asignatura:</div>
            <div class="portada-campo-val">INGENIERÍA DE DATOS (CMD-2602)</div>
            <div class="portada-sub">Proyecto Integrador Colegiado con Análisis Estadístico para Ciencia de Datos y Calidad en SI</div>

            <div class="portada-campo-etiq">Actividad:</div>
            <div class="portada-campo-val">[E3] Trusted Data Lab: Capa Oro, Optimización, Mapa Multivariado y Sello TDL</div>
            <div class="portada-sub">Observatorio CITRO-DATA LAB COLIMA · Etiqueta Git: <code>e3</code> · Sello TDL: <code>6/6 Certificado</code></div>

            <div class="portada-campo-etiq">Alumno:</div>
            <div class="portada-campo-val">Norberto Daniel Escareño Montaño</div>
            <div class="portada-campo-val">23460323</div>
            <div class="portada-sub">Repositorio: https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima</div>

            <div class="portada-campo-etiq">Docente:</div>
            <div class="portada-campo-val">ARMANDO ROMÁN GALLARDO HEREDIA</div>
            <div class="portada-sub">Análisis Estadístico: Mónico Joel Sánchez Velasco</div>
          </div>

          <div class="portada-pie">
            Villa de Álvarez, Colima; 27 de noviembre de 2026
          </div>
        </div>

        <!-- ==================== PÁGINA 2: RESUMEN, MATRIZ MULTIVARIADA Y NORMALIDAD ==================== -->
        <div class="salto-pagina"></div>

        <h2>1. Resumen Ejecutivo de la Entrega E3 (Tag <code>e3</code> · Sello TDL Certificado)</h2>
        <p>En la Etapa <strong>E3</strong> el observatorio <strong>CITRO-DATA LAB COLIMA</strong> culmina la integración analítica, de ingeniería y de calidad previa al Demo Day. En <strong>Análisis Estadístico (Unidad 5)</strong> se construyó la matriz multivariada de rango completo (<em>p</em> = 8 variables bioclimáticas continuas sobre <em>N</em> = 240 observaciones mensuales de los 4 municipios citrícolas de Colima y <em>p</em> = 5 variables comerciales en las 4 centrales de abasto nacionales), se verificó la normalidad multivariada en la <strong>Puerta 3</strong> (pruebas de Mardia y Henze-Zirkler + transformación Yeo-Johnson con correlación Q-Q de Mahalanobis <strong>r = {norm_yj['correlacion_qq_mahalanobis']:.4f}</strong>), se redujo la dimensionalidad con <strong>PCA</strong> sintetizando el <strong>{res_mv['pca']['varianza_acumulada_3pc_pct']}% de la varianza</strong> en 3 índices con nombre de negocio (<strong>{res_mv['pca']['varianza_acumulada_2pc_pct']}%</strong> en PC1+PC2 proyectados en el Biplot interactivo del tablero) y se demostró con <strong>MANOVA</strong> (&Lambda; de Wilks, Traza de Pillai y permutación) la separación estadísticamente significativa entre municipios (<em>p</em> &lt; 10<sup>-114</sup>) y mercados (<em>p</em> &lt; 10<sup>-105</sup>). En <strong>Ingeniería de Datos (Unidad 4.2)</strong> se llevó a producción la configuración óptima del DOE 2³ (<code>4 hilos + Pandera vectorizado + Apache Parquet Snappy/ZSTD</code>), logrando una aceleración medida de <strong>{mej['factor_aceleracion_speedup']}× (-{mej['reduccion_tiempo_total_pct']}% en tiempo)</strong>, <strong>-{mej['reduccion_memoria_pico_pct']}% en memoria RAM pico</strong> y <strong>-{mej['reduccion_disco_zstd_pct']}% en disco</strong>, y se publicó el dataset curado bajo licencia abierta <strong>CC BY 4.0</strong> con su <strong>Datasheet for Datasets (<code>docs/E3/datasheet.md</code>)</strong>. En <strong>Calidad (Unidad 4.3–4.7)</strong> se cerró el <strong>100% de los hallazgos de auditoría (5/5 cerrados, 0 críticos abiertos)</strong>, se realizó la autoevaluación <strong>MoProSoft y CMMI (Nivel 3 Definido)</strong>, la retrospectiva <strong>PSP (E0&rarr;E3 con Yield = 100% en E3)</strong>, el análisis de tendencias (<strong>DataOps, Observabilidad, DevSecOps e ISO/IEC 42001</strong>) y se acreditaron los <strong>6/6 criterios del Sello TDL</strong>.</p>

        <div class="cuadro-nota">
          <strong>Enlaces directos a la evidencia en GitHub (Tag <code>e3</code>):</strong><br>
          • Ficha de Entrega: <code>docs/E3/ENTREGA.md</code> | Datasheet CC BY 4.0: <code>docs/E3/datasheet.md</code> | Relatoría E3: <code>docs/relatoria-E3.md</code><br>
          • Calidad, Modelos, PSP y Sello TDL: <code>docs/calidad-modelos-psp-sello-e3.md</code> | Notebook: <code>docs/E3/analisis_multivariado_y_optimizacion.ipynb</code><br>
          • Código E3: <code>pipeline/optimizacion_dataset_e3.py</code>, <code>pipeline/multivariado_pca_manova_e3.py</code>, <code>pipeline/calidad_sello_e3.py</code>, <code>pipeline/verificar_e3.py</code><br>
          • Dataset Publicado: <code>data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet</code> (y <code>.csv</code>) | Tablero con Mapa PCA y Sello TDL: <code>tablero/app.py</code>.
        </div>

        <h2>2. Análisis Multivariado: Matriz, Normalidad (Puerta 3), PCA y MANOVA (Unidad 5)</h2>
        <h3>2.1 Matriz Multivariada (p = 8 Variables Continuas) y Normalidad Multivariada (Mardia, Henze-Zirkler y Q-Q Mahalanobis)</h3>
        <p>La matriz multivariada evalúa simultáneamente <strong>8 variables bioclimáticas continuas linealmente independientes</strong> (<code>rank(S) = 8</code>, corrigiendo en revisión de diseño el Defecto #11 de colinealidad) sobre <em>N</em> = 240 observaciones (60 meses &times; 4 municipios: <code>Tecomán</code>, <code>Armería</code>, <code>Manzanillo</code> y <code>Colima</code>). En escala original, el régimen de lluvias tropicales introduce asimetría (Mardia <em>b</em><sub>1,p</sub> = 43.89, Henze-Zirkler <em>HZ</em> = 2.882). Cumpliendo la <strong>Puerta 3 de calidad estadística</strong>, se aplicó la transformación de potencia <strong>Yeo-Johnson</strong>, alcanzando normalidad en la curtosis multivariada de Mardia (<strong>b<sub>2,p</sub> = {norm_yj['mardia_b2p_curtosis']:.2f} vs. esperada {norm_yj['mardia_curtosis_esperada']:.2f}, Z = {norm_yj['mardia_z_curtosis']:.2f}, p = {norm_yj['mardia_p_curtosis']:.3f} &gt; 0.05 ✓</strong>) y elevando la correlación Q-Q de las distancias cuadradas de Mahalanobis (<em>D<sub>i</sub>² &sim; &chi;²<sub>8</sub></em>) de <code>r = 0.8422</code> a <strong><code>r = {norm_yj['correlacion_qq_mahalanobis']:.4f}</code></strong> con <strong>{norm_yj['pct_dentro_chi2_95']:.2f}%</strong> dentro del cuantil 95% (&chi;²<sub>8, 0.95</sub> = 15.51):</p>

        <img class="figura" src="{fig1}" alt="Matriz de Correlaciones y Gráfica Q-Q de Mahalanobis">

        <h3>2.2 Análisis de Componentes Principales (PCA), Nombres de Negocio y Biplot</h3>
        <p>Tras estandarizar a puntaje Z (&mu; = 0, &sigma; = 1) y verificar la prueba de esfericidad de Bartlett (<strong>&chi;² = {res_mv['pca']['bartlett_chi2']:.2f}, gl = 28, p &lt; 10<sup>-300</sup></strong>), los <strong>3 primeros componentes cumplen el criterio de Kaiser (&lambda; &ge; 1.0)</strong> y sintetizan el <strong>{res_mv['pca']['varianza_acumulada_3pc_pct']}% de la varianza total</strong> (<strong>{res_mv['pca']['varianza_acumulada_2pc_pct']}% en PC1 + PC2</strong>):</p>
        <img class="figura" src="{fig2}" alt="Gráfica de Sedimentación y Biplot PCA">
        {_df_html(df_scree[["componente", "nombre_negocio", "eigenvalor_lambda", "varianza_explicada_pct", "varianza_acumulada_pct", "interpretacion_negocio"]])}
        <p><strong>Cargas factoriales (correlaciones variable–componente) y comunalidades:</strong></p>
        {_df_html(df_cargas[["etiqueta_negocio", "carga_corr_PC1", "carga_corr_PC2", "carga_corr_PC3", "comunalidad_PC1_PC2", "comunalidad_PC1_PC3"]])}

        <h3>2.3 MANOVA (Lambda de Wilks y Traza de Pillai) vs. ANOVAs Univariados Separados</h3>
        <p>Se ejecutó el <strong>MANOVA de una vía</strong> sobre los dos ejes de agrupación definidos desde E0, respaldado por la <strong>Traza de Pillai</strong>, la transformación <strong>Yeo-Johnson</strong> y una prueba no paramétrica de <strong>1,000 permutaciones</strong> (Puerta 3):</p>
        <ul>
          <li><strong>MANOVA Geográfico-Agroclimático (4 Municipios de Colima, N = 240, p = 8):</strong> <strong>Lambda de Wilks &Lambda; = {m_mun['wilks_lambda']:.4f}</strong> (<em>F</em> = {m_mun['wilks_f']:.2f}, <em>p</em> = 6.78 &times; 10<sup>-115</sup>, &eta;² = {m_mun['wilks_eta2']:.4f}) y <strong>Traza de Pillai V = {m_mun['pillai_traza']:.4f}</strong> (<em>F</em> = {m_mun['pillai_f']:.2f}, <em>p</em> = 1.28 &times; 10<sup>-72</sup>; Permutación <em>p</em> = {m_mun['permutacion_pillai_p_valor']}).</li>
          <li><strong>MANOVA Comercial (4 Centrales Mayoristas SNIIM: Colima, Guadalajara, CDMX, Monterrey, N = 240, p = 5):</strong> <strong>Lambda de Wilks &Lambda; = {m_mkt['wilks_lambda']:.4f}</strong> (<em>F</em> = {m_mkt['wilks_f']:.2f}, <em>p</em> = 8.59 &times; 10<sup>-106</sup>, &eta;² = {m_mkt['wilks_eta2']:.4f}) y <strong>Traza de Pillai V = {m_mkt['pillai_traza']:.4f}</strong> (<em>F</em> = {m_mkt['pillai_f']:.2f}, <em>p</em> = 8.68 &times; 10<sup>-46</sup>; Permutación <em>p</em> = {m_mkt['permutacion_pillai_p_valor']}).</li>
          <li><strong>¿Por qué MANOVA no equivale a correr varios ANOVAs separados?</strong> Ejecutar <em>p</em> = 8 ANOVAs univariados independientes a &alpha; = 0.05 infla la tasa de Error Tipo I global a <strong>1 - (1 - 0.05)<sup>8</sup> = 33.66%</strong> e ignora las correlaciones fuera de la diagonal entre temperatura, radiación, <em>ET</em><sub>0</sub> y viento. El MANOVA controla &alpha; = 5.0% exacto y evalúa combinaciones lineales discriminantes conjuntas.</li>
        </ul>
        <img class="figura" src="{fig3}" alt="MANOVA vs ANOVAs Separados e Inflación Error Tipo I">
        {_df_html(df_manova[["comparacion", "estadistico", "valor", "f_aprox", "gl_num", "gl_den", "p_valor", "eta2_parcial_multivariado"]])}

        <!-- ==================== SECCIÓN 3: INGENIERÍA DE DATOS (OPTIMIZACIÓN Y DATASET) ==================== -->
        <h2>3. Ingeniería de Datos: Optimización Medida del Pipeline y Dataset Publicado (Unidad 4.2)</h2>
        <h3>3.1 Comparativa Cuantitativa Antes (E1 CSV) vs. Después (E3 Parquet + Pandera + 4 Hilos)</h3>
        <p>En <code>pipeline/optimizacion_dataset_e3.py</code> se aplicó en producción el tratamiento óptimo del DOE 2³ (<code>ThreadPoolExecutor</code> de 4 hilos + validación vectorizada C/NumPy con <code>pandera.pandas</code> + persistencia columnar <code>Apache Parquet Snappy y ZSTD</code>) cerrando los hallazgos <code>AUD-03</code> y <code>AUD-05</code>. Sobre <em>n</em> = 10 réplicas aleatorizadas del flujo completo Bronce &rarr; Plata &rarr; Oro, la latencia total cayó de <strong>{res_opt['configuracion_antes_e1']['tiempo_total_medio_ms']:.2f} ms a {res_opt['configuracion_despues_e3_snappy']['tiempo_total_medio_ms']:.2f} ms ({mej['factor_aceleracion_speedup']}× más rápido, -{mej['reduccion_tiempo_total_pct']}% tiempo, p<sub>Welch</sub> &lt; 10<sup>-15</sup>)</strong>, el consumo pico de memoria RAM medido con <code>tracemalloc</code> disminuyó de <strong>{res_opt['configuracion_antes_e1']['memoria_pico_media_kb']:.1f} KB a {res_opt['configuracion_despues_e3_snappy']['memoria_pico_media_kb']:.1f} KB (-{mej['reduccion_memoria_pico_pct']}%)</strong> y el espacio en disco se redujo de <strong>{res_opt['configuracion_antes_e1']['disco_total_kb']:.1f} KB (CSV) a {res_opt['configuracion_despues_e3_zstd']['disco_total_kb']:.1f} KB (-{mej['reduccion_disco_zstd_pct']}% en Parquet ZSTD, factor {mej['factor_compresion_disco_zstd']}×)</strong> con <strong>0.0% de errores</strong>:</p>
        <img class="figura" src="{fig4}" alt="Optimización Medida del Pipeline Antes vs Después">
        {_df_html(df_bench[["escenario", "tiempo_io_medio_ms", "tiempo_validacion_medio_ms", "tiempo_transformacion_medio_ms", "tiempo_escritura_medio_ms", "tiempo_total_medio_ms", "memoria_pico_media_kb", "disco_total_kb"]])}

        <h3>3.2 Dataset Curado Publicado con Licencia Abierta (CC BY 4.0) y Datasheet (<code>docs/E3/datasheet.md</code>)</h3>
        <p>Se publicó el paquete oficial <code>data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet</code> (<code>47.7 KB</code>) y su espejo <code>.csv</code> (<code>228.5 KB</code>, <code>240 filas &times; 64 columnas</code>, <code>100.0% completitud</code>, <code>0 PII</code>, verificado con <code>SHA-256</code> en <code>dataset_publicado_e3_manifest.json</code>) bajo licencia abierta <strong>Creative Commons Attribution 4.0 International (CC BY 4.0)</strong>, acompañado de su ficha técnica estandarizada <strong>Datasheet for Datasets (Gebru et al., 2021)</strong> en <code>docs/E3/datasheet.md</code> con sus 7 secciones (motivación, composición, recolección ética, preprocesamiento, usos recomendados y prohibidos, distribución y mantenimiento).</p>

        <!-- ==================== SECCIÓN 4: CALIDAD EN SI, MODELOS, PSP, TENDENCIAS Y SELLO TDL ==================== -->
        <h2>4. Calidad en SI: Cierre de Auditoría, MoProSoft/CMMI, Retrospectiva PSP, Tendencias y Sello TDL</h2>
        <h3>4.1 Cierre del 100% de Hallazgos de Auditoría (5 / 5 Cerrados · 0 Críticos Abiertos)</h3>
        {_df_html(df_aud[["id_hallazgo", "severidad", "norma_criterio", "accion_correctiva_aplicada", "estado_final_e3"]])}

        <h3>4.2 Autoevaluación contra MoProSoft (NMX-I-059-NYCE) y CMMI v2.0 + Comparativa de los 5 Modelos</h3>
        <p>El observatorio alcanza el <strong>Nivel 3 (Definido)</strong> tanto en las 3 categorías de <strong>MoProSoft (DIR, GER, OPE)</strong> como en las áreas de práctica de <strong>CMMI v2.0 (RDM, TS, VV, PQA, CM, CAR)</strong>, con prácticas de Nivel 4 en Análisis Causal (<code>CAR</code> / DOE 2³):</p>
        {_df_html(df_auto[["marco", "categoria_o_dominio", "proceso_o_area", "nivel_alcanzado", "brecha_para_nivel_4_5"]])}
        <p><strong>Tabla comparativa de los 5 modelos normativos del temario:</strong></p>
        {_df_html(df_comp_mod)}

        <h3>4.3 Retrospectiva PSP (E0 a E3), Tendencias (DataOps / ISO 42001) y Certificación del Sello TDL (6 / 6)</h3>
        <p>Sobre las <strong>22 sesiones registradas (45.42 horas netas)</strong> en <code>calidad/tiempo-norberto.csv</code> y los <strong>13 defectos cerrados</strong> en <code>calidad/defectos-norberto.csv</code>, la exactitud de estimación convergió de <code>73.15%</code> en E0 a <strong>94.38% global</strong>, el rendimiento de revisión temprana (<em>Yield</em>) subió de <code>0%</code> en E1 a <strong>100.0% en E3</strong> (los 3 defectos <code>#11–#13</code> fueron eliminados en fase de revisión antes de pruebas) y el tiempo medio de corrección bajó un <strong>33.3%</strong> (de <code>16.00 min</code> a <strong>10.67 min</strong>). En <code>docs/calidad-modelos-psp-sello-e3.md</code> se documenta además la aplicación de <strong>DataOps</strong>, los <strong>5 pilares de Observabilidad de Datos</strong>, <strong>DevSecOps</strong> y gobernanza de IA bajo <strong>ISO/IEC 42001:2023</strong>.</p>
        <img class="figura" src="{fig5}" alt="Retrospectiva PSP E0-E3 y Certificación Sello TDL 6/6">
        {_df_html(df_retro[["etapa", "sesiones_registradas", "horas_reales_netas", "exactitud_estimacion_pct", "defectos_totales_etapa", "yield_revision_pct", "tiempo_medio_correccion_min"]])}
        <p><strong>Evidencia de cumplimiento de los 6 criterios oficiales del Sello TDL (APROBADO 6 / 6):</strong></p>
        {_df_html(df_sello[["id_criterio", "criterio_sello_tdl", "umbral_minimo_oficial", "resultado_medido_observatorio", "evidencia_verificable"]])}
      </td>
    </tr>
  </tbody>
</table>

</body>
</html>
"""

    html_temp = ROOT_DIR / "docs" / "E3" / "_temp_reporte_e3.html"
    pdf_out = ROOT_DIR / "docs" / "E3" / "Entrega_E3_Escareno_Norberto.pdf"
    html_temp.parent.mkdir(parents=True, exist_ok=True)
    html_temp.write_text(html, encoding="utf-8")

    edge_candidates = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    edge_exe = next((p for p in edge_candidates if Path(p).exists()), None)
    if not edge_exe:
        raise FileNotFoundError("No se encontró Microsoft Edge para renderizar el PDF.")

    cmd = [
        edge_exe,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_out.resolve()}",
        html_temp.resolve().as_uri(),
    ]
    subprocess.run(cmd, check=True)
    if html_temp.exists():
        html_temp.unlink()

    copia_scratch = ROOT_DIR.parent / "Entrega_E3_Escareno_Norberto.pdf"
    shutil.copy2(pdf_out, copia_scratch)
    return pdf_out


if __name__ == "__main__":
    ruta = generar_pdf_e3()
    print(f"[OK] PDF E3 generado: {ruta} ({ruta.stat().st_size:,} bytes)")
