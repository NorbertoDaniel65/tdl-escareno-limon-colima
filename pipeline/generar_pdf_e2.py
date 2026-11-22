"""
Generador determinista del Reporte Integral PDF de la Entrega E2:
docs/E2/Entrega_E2_Escareno_Norberto.pdf (y copia en scratch/).
Aplica estrictamente el Molde Oficial TecNM — Instituto Tecnológico de Colima:
  - Encabezado con Logo TecNM (izquierda) y Escudo IT Colima (derecha) repetido en TODAS las páginas.
  - Portada limpia en Página 1 (fondo blanco, tipografía Arial negra centrada en negrita).
  - Contenido sobrio en páginas 2+ con tablas limpias y las 5 figuras HD en Base64.
"""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
FIGURAS_DIR = ROOT_DIR / "docs" / "E2" / "figuras"
PLANTILLA_DIR = ROOT_DIR.parent / "plantilla_tecnm"


def _img_b64(path: Path) -> str:
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def _df_html(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0, classes="tabla-datos")


def generar_pdf_e2() -> Path:
    logo_tecnm = _img_b64(PLANTILLA_DIR / "logo_tecnm.png")
    logo_itc = _img_b64(PLANTILLA_DIR / "logo_itcolima.png")

    fig1 = _img_b64(FIGURAS_DIR / "fig1_mapa_geoespacial_colima_e2.png")
    fig2 = _img_b64(FIGURAS_DIR / "fig2_arquitectura_linaje_bronce_oro_e2.png")
    fig3 = _img_b64(FIGURAS_DIR / "fig3_doe_factorial_2_3_efectos_pareto.png")
    fig4 = _img_b64(FIGURAS_DIR / "fig4_anova_dos_vias_y_supuestos_residuos.png")
    fig5 = _img_b64(FIGURAS_DIR / "fig5_fraccionado_2_4_y_confirmacion_optimo.png")

    df_geo = pd.read_csv(ORO_DIR / "perfil_geoespacial_municipios_oro.csv")
    df_cat_lin = pd.read_csv(ORO_DIR / "catalogo_linaje_oro_bronce.csv")
    df_anova_23 = pd.read_csv(ORO_DIR / "anova_factorial_2_3_e2.csv")
    df_ef_23 = pd.read_csv(ORO_DIR / "efectos_factorial_2_3_e2.csv")
    df_anova_2x3 = pd.read_csv(ORO_DIR / "anova_dos_vias_2x3_e2.csv")
    df_alias = pd.read_csv(ORO_DIR / "estructura_alias_2_4_fraccionado_e2.csv")
    df_iso10 = pd.read_csv(ORO_DIR / "evaluacion_iso_25010_e2.csv")
    df_iso12 = pd.read_csv(ORO_DIR / "evaluacion_iso_25012_e2.csv")
    df_tiempo = pd.read_csv(ROOT_DIR / "calidad" / "tiempo-norberto.csv").tail(5).copy()
    df_defectos = pd.read_csv(ROOT_DIR / "calidad" / "defectos-norberto.csv").tail(3).copy()
    df_defectos["defecto_origen"] = df_defectos["defecto_origen"].apply(
        lambda v: "—" if pd.isna(v) else str(int(v))
    )

    res_geo = json.loads((ORO_DIR / "resumen_geoespacial_e2.json").read_text(encoding="utf-8"))
    res_lin = json.loads((ORO_DIR / "linaje_datos_e2.json").read_text(encoding="utf-8"))
    res_doe = json.loads((ORO_DIR / "resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))
    res_iso = json.loads((ORO_DIR / "resumen_evaluacion_iso_e2.json").read_text(encoding="utf-8"))

    # Muestra representativa de linaje (2 filas por cada una de las 3 tablas de Capa Oro)
    muestra_lin = pd.concat(
        [
            df_cat_lin[df_cat_lin["tabla_oro"] == "serie_mensual_oro_60m.csv"].iloc[[0, 13]],
            df_cat_lin[df_cat_lin["tabla_oro"] == "panel_integrado_municipio_mercado_oro.csv"].iloc[[0, -1]],
            df_cat_lin[df_cat_lin["tabla_oro"] == "perfil_geoespacial_municipios_oro.csv"].iloc[[0, 2]],
        ],
        ignore_index=True,
    )[["tabla_oro", "linaje_id_registro", "linaje_fuentes_bronce", "linaje_sha256_bronce", "linaje_fecha_ingesta_utc"]]

    geo_cols = df_geo[
        [
            "cvegeo",
            "nombre_oficial",
            "en_observatorio_citricola",
            "superficie_km2",
            "n_huertas_citricolas_osm",
            "n_empaque_bodega_osm",
            "n_mercados_abasto_osm",
            "n_nodos_agrologisticos_total",
            "dist_puerto_manzanillo_km",
            "dist_corredor_gdl_54d_km",
        ]
    ].rename(
        columns={
            "cvegeo": "CVEGEO",
            "nombre_oficial": "Municipio",
            "en_observatorio_citricola": "Núcleo",
            "superficie_km2": "Área (km²)",
            "n_huertas_citricolas_osm": "Huertas",
            "n_empaque_bodega_osm": "Empaque/Bod.",
            "n_mercados_abasto_osm": "Mercados",
            "n_nodos_agrologisticos_total": "Total Nodos",
            "dist_puerto_manzanillo_km": "Dist. Pto (km)",
            "dist_corredor_gdl_54d_km": "Dist. 54D (km)",
        }
    )

    sup_lin = res_doe["diseno_2_3"]["supuestos_residuos_escala_lineal"]
    conf = res_doe["corrida_confirmacion"]

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Entrega E2 — CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño</title>
<style>
  @page {{
    size: letter;
    margin: 12mm 15mm 14mm 15mm;
  }}
  body {{
    font-family: Arial, Calibri, 'Segoe UI', sans-serif;
    font-size: 10pt;
    line-height: 1.42;
    color: #000000;
    background: #ffffff;
    margin: 0;
    padding: 0;
  }}
  table.marco-pagina {{
    width: 100%;
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
    font-size: 11.5pt;
    font-weight: 700;
    color: #000000;
    border-bottom: 1.5px solid #111827;
    padding-bottom: 2px;
    margin: 12px 0 6px 0;
    page-break-after: avoid;
  }}
  h3 {{
    font-size: 10pt;
    font-weight: 700;
    color: #111827;
    margin: 9px 0 4px 0;
    page-break-after: avoid;
  }}
  p, li {{
    margin: 3.5px 0;
    text-align: justify;
  }}
  .tabla-datos {{
    width: 100%;
    border-collapse: collapse;
    font-size: 7.5pt;
    margin: 5px 0 9px 0;
    page-break-inside: avoid;
  }}
  .tabla-datos th {{
    background-color: #f3f4f6;
    color: #000000;
    font-weight: 700;
    text-align: left;
    padding: 3.5px 5px;
    border: 1px solid #9ca3af;
  }}
  .tabla-datos td {{
    padding: 3px 5px;
    border: 1px solid #d1d5db;
    vertical-align: top;
    overflow-wrap: break-word;
  }}
  .tabla-datos tr:nth-child(even) {{
    background-color: #fafafa;
  }}
  .cuadro-nota {{
    border: 1px solid #9ca3af;
    border-left: 3.5px solid #111827;
    background-color: #f9fafb;
    padding: 6px 9px;
    margin: 7px 0;
    font-size: 8.8pt;
    page-break-inside: avoid;
  }}
  .figura {{
    width: 100%;
    height: auto;
    margin: 5px 0 8px 0;
    border: 1px solid #d1d5db;
    page-break-inside: avoid;
  }}
  code {{
    font-family: Consolas, 'Courier New', monospace;
    font-size: 8.6pt;
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
            <div class="portada-sub">Proyecto Integrador Colegiado con Análisis Estadístico para Ciencia de Datos</div>

            <div class="portada-campo-etiq">Actividad:</div>
            <div class="portada-campo-val">[E2] Trusted Data Lab: Fuente Especializada, Ética y Linaje de Datos</div>
            <div class="portada-sub">Observatorio CITRO-DATA LAB COLIMA · Etiqueta Git: <code>e2</code></div>

            <div class="portada-campo-etiq">Alumno:</div>
            <div class="portada-campo-val">Norberto Daniel Escareño Montaño</div>
            <div class="portada-campo-val">23460323</div>
            <div class="portada-sub">Repositorio: https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima</div>

            <div class="portada-campo-etiq">Docente:</div>
            <div class="portada-campo-val">ARMANDO ROMÁN GALLARDO HEREDIA</div>
            <div class="portada-sub">Análisis Estadístico: Mónico Joel Sánchez Velasco</div>
          </div>

          <div class="portada-pie">
            Villa de Álvarez, Colima; 22 de noviembre de 2026
          </div>
        </div>

        <!-- ==================== PÁGINA 2: RESUMEN Y FUENTE GEOESPACIAL ==================== -->
        <div class="salto-pagina"></div>

        <h2>1. Resumen Ejecutivo de la Entrega E2 (Tag <code>e2</code>)</h2>
        <p>La Etapa <strong>E2</strong> del observatorio <strong>CITRO-DATA LAB COLIMA</strong> consolida la evolución del proyecto integrador hacia una arquitectura de datos avanzada, ética y completamente auditable. Se incorporó una tercera fuente especializada geoespacial basada en <strong>OpenStreetMap (Nominatim + Overpass API)</strong> y claves geoestadísticas <strong>INEGI</strong> para el Estado de Colima, se redactó la declaración formal de ética y legalidad (<code>docs/etica-datos.md</code>), se instrumentó un <strong>100% de trazabilidad de linaje</strong> registro-a-registro desde Capa Bronce hasta Capa Oro (<code>310/310</code> registros maestros), se ejecutó un <strong>Experimento Factorial Real 2³</strong> junto con un <strong>ANOVA de Dos Vías (2×3)</strong> y la comparativa <strong>2⁴ vs. 2⁴⁻¹ fraccionado (Resolución IV)</strong>, y se evaluó cuantitativamente el observatorio bajo <strong>ISO/IEC 25010</strong> e <strong>ISO/IEC 25012</strong>.</p>

        <div class="cuadro-nota">
          <strong>Enlaces verificables en GitHub (<code>https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima</code> · Tag <code>e2</code>):</strong><br>
          • Ficha de Entrega E2: <code>docs/E2/ENTREGA.md</code> | Relatoría E2: <code>docs/relatoria-E2.md</code> | Notebook: <code>docs/E2/experimento_y_geodatos.ipynb</code><br>
          • Ética y Legalidad: <code>docs/etica-datos.md</code> | Evaluación Normativa: <code>docs/evaluacion-iso-25010-25012.md</code> | Tablero: <code>tablero/app.py</code><br>
          • Geoespacial y Linaje: <code>extractores/geoespacial_osm.py</code>, <code>pipeline/geoespacial_e2.py</code>, <code>pipeline/linaje_datos.py</code><br>
          • Experimento DOE y Pruebas: <code>pipeline/experimento_doe_e2.py</code>, <code>pipeline/verificar_e2.py</code> y <code>27/27</code> pruebas en <code>pytest</code>.
        </div>

        <h2>2. Fuente Especializada Integrada: Geoespacial Colima (GeoPandas + OSM/INEGI)</h2>
        <p>Mediante <code>extractores/geoespacial_osm.py</code> (usando <code>ExtractorEtico</code> con pausa &ge; 1.5 s, <code>User-Agent</code> institucional y lista blanca estricta de cero PII) se capturaron en vivo los <strong>10 polígonos administrativos oficiales de Colima</strong> (<code>EPSG:4326</code>) y <strong>{res_geo['puntos_bronce_evaluados']:,} nodos de infraestructura agrologística</strong>. En <code>pipeline/geoespacial_e2.py</code> se ejecutó la unión espacial <code>gpd.sjoin(puntos, poligonos, predicate="within")</code>, aprobando <strong>{res_geo['puntos_aprobados_dentro_colima_plata']:,} nodos válidos dentro de Colima</strong> hacia Capa Plata y enrutando <strong>{res_geo['puntos_enviados_cuarentena_fuera_colima']} puntos</strong> pertenecientes a Jalisco/Michoacán hacia <code>data/cuarentena/cuarentena_geoespacial_e2.csv</code> (conservación de masa exacta, cero borrado silencioso). Las áreas y distancias al Puerto de Manzanillo y la Autopista 54D (Guadalajara) se proyectaron a <code>EPSG:32613</code> (UTM Zona 13N), corrigiendo además el <em>MultiPolygon</em> oceánico de Revillagigedo en Tecomán (Defecto #9).</p>

        <img class="figura" src="{fig1}" alt="Mapa Geoespacial Citrícola de Colima">
        {_df_html(geo_cols)}

        <!-- ==================== SECCIÓN 3: ÉTICA Y LINAJE DE DATOS ==================== -->

        <h2>3. Declaración de Ética, Legalidad, Privacidad y Sesgos (<code>docs/etica-datos.md</code>)</h2>
        <p>Cada fuente operativa del observatorio fue auditada contra su marco legal mexicano (Art. 6° Constitucional, LGTAIP y LFPDPPP), su archivo <code>robots.txt</code> archivado en <code>data/bronce/robots_txt/</code>, sus términos de uso, licencias y sesgos conocidos:</p>
        <table class="tabla-datos">
          <tr>
            <th>Fuente</th>
            <th>robots.txt y Términos</th>
            <th>Licencia</th>
            <th>Privacidad (LFPDPPP)</th>
            <th>Sesgos Conocidos y Mitigación</th>
          </tr>
          <tr>
            <td><strong>F1 · Open-Meteo API</strong><br>(ERA5-Land)</td>
            <td><code>Disallow: /</code> para indexadores web; API académica &lt;0.04% cuota (4 req/día, pausa &ge;1.5 s).</td>
            <td><strong>CC BY 4.0</strong> (Open-Meteo / Copernicus)</td>
            <td><strong>0 PII</strong> (variables geofísicas municipales).</td>
            <td>Rejilla satelital ~9 km suaviza microclimas locales. Mitigación: índice ponderado SIAP (55/22/15/8%) y reglas RN-01/RN-03.</td>
          </tr>
          <tr>
            <td><strong>F2 · SNIIM (SE)</strong><br>(Precios Limón #5)</td>
            <td><code>HTTP 404</code> (sin bloqueo); 1 petición GET diaria respetuosa sobre portal público federal.</td>
            <td><strong>Libre Uso Datos Abiertos MX</strong></td>
            <td><strong>0 PII</strong> (precios agregados por central).</td>
            <td>Refleja precio mayorista en bodega (no a pie de huerta) y menor muestreo en escasez (MNAR). Mitigación: spread y preservación de choques 2022/2024.</td>
          </tr>
          <tr>
            <td><strong>F3 · OpenStreetMap + INEGI</strong><br>(Geoespacial E2)</td>
            <td><code>robots.txt</code> archivado (<code>nominatim</code> y <code>overpass-api.de</code>); batch único con caché local.</td>
            <td><strong>ODbL 1.0</strong> (© OSM Contributors) + INEGI</td>
            <td><strong>0 PII</strong>: lista blanca + regex elimina teléfonos y correos en Bronce.</td>
            <td>Sesgo VGI voluntario (Ixtlahuacán 496 huertas vs Tecomán 167) y MultiPolygon Revillagigedo. Mitigación: triangulación SIAP y polígono continental.</td>
          </tr>
        </table>

        <h2>4. Linaje y Trazabilidad Completa de Datos (Capa Bronce &rarr; Capa Oro)</h2>
        <p>El módulo <code>pipeline/linaje_datos.py</code> garantiza que el <strong>{res_lin['cobertura_trazabilidad_pct']}% de los {res_lin['total_registros_oro_rastreados']} registros maestros de Capa Oro</strong> (<code>60</code> en <code>serie_mensual_oro_60m.csv</code>, <code>240</code> en <code>panel_integrado_municipio_mercado_oro.csv</code> y <code>10</code> en <code>perfil_geoespacial_municipios_oro.csv</code>) incluyan explícitamente 6 columnas de trazabilidad (<code>linaje_id_registro</code>, <code>linaje_fuentes_bronce</code>, <code>linaje_archivos_bronce</code>, <code>linaje_sha256_bronce</code>, <code>linaje_fecha_ingesta_utc</code> y <code>linaje_version_pipeline</code>), respaldadas por el manifiesto DAG <code>data/oro/linaje_datos_e2.json</code> y la función verificable <code>rastrear_registro_oro()</code>:</p>

        <img class="figura" src="{fig2}" alt="Arquitectura de Linaje Bronce a Oro">
        <p><strong>Muestra verificada del catálogo registro-a-registro (<code>data/oro/catalogo_linaje_oro_bronce.csv</code>):</strong></p>
        {_df_html(muestra_lin)}

        <!-- ==================== SECCIÓN 5: EXPERIMENTO FACTORIAL 2^3 Y ANOVA 2x3 ==================== -->

        <h2>5. Diseño de Experimentos (Análisis Estadístico — Unidad 4)</h2>
        <h3>5.1 Experimento Factorial Completo 2³ (Ruta Ingeniería, Aleatorizado, r = 3, 3 Bloques)</h3>
        <p>Se ejecutaron <strong>24 corridas reales</strong> sobre particiones locales controladas de Capa Bronce (0 tráfico externo) combinando <strong>Factor A</strong> (Paralelismo I/O: 1 vs. 4 hilos), <strong>Factor B</strong> (Motor de Validación: Iterativo vs. Pandera Vectorizado) y <strong>Factor C</strong> (Formato de Escritura: CSV UTF-8 vs. Parquet Snappy), aleatorizadas con semilla <code>23460323</code> en 3 bloques temporales (<code>B1–B3</code>). El modelo explica <strong>R² = {sup_lin['r2_modelo']:.4f}</strong> (R² ajustado = {sup_lin['r2_ajustado']:.4f}) con <strong>0.0% de tasa de error</strong>:</p>
        <img class="figura" src="{fig3}" alt="Diagrama de Pareto y Efectos Principales 2^3">
        {_df_html(df_ef_23[["descripcion", "efecto_estimado_ms", "estadistico_t", "p_valor", "significativo_5pct"]])}

        <h3>5.2 ANOVA de Dos Vías (2×3 con Interacción) y Puerta de Calidad 3 (Supuestos de Residuos)</h3>
        <p>Extendiendo el Factor C a 3 niveles (<code>CSV UTF-8</code>, <code>Parquet Snappy</code> y <code>Parquet ZSTD</code>; 18 corridas), la interacción Motor &times; Formato resultó no significativa (<em>p</em> = {res_doe['diseno_dos_vias_2x3']['p_valor_interaccion_BxC']:.3f}), demostrando que las mejoras de vectorización y almacenamiento columnar son aditivas. <strong>Puerta 3 APROBADA:</strong> Normalidad Shapiro-Wilk <em>W</em> = {sup_lin['shapiro_wilk_W']:.4f} (<em>p</em> = {sup_lin['shapiro_wilk_p']:.4f} &ge; 0.05), Homocedasticidad Levene <em>F</em> = {sup_lin['levene_F']:.4f} (<em>p</em> = {sup_lin['levene_p']:.4f} &ge; 0.05) e Independencia Durbin-Watson <em>DW</em> = {sup_lin['durbin_watson']:.4f}.</p>
        <img class="figura" src="{fig4}" alt="ANOVA 2x3 y Diagnóstico de Supuestos de Residuos">

        <!-- ==================== SECCIÓN 5.3: 2^4 VS FRACCIONADO, CONFIRMACIÓN E ISO ==================== -->

        <h3>5.3 Diseño 2⁴ Completo vs. 2⁴⁻¹ Fraccionado (Resolución IV, I = ABCD) y Confirmación del Óptimo</h3>
        <p>Al añadir el <strong>Factor D</strong> (<em>Partición por municipio vs. Archivo consolidado</em>), el diseño fraccionado <strong>2⁴⁻¹</strong> (generador <em>D = ABC</em>, <strong>8 corridas vs. 16 del completo = 50.0% de ahorro</strong>) mantiene todos los efectos principales libres de interacciones dobles (<em>A = BCD, B = ACD, C = ABD, D = ABC</em>) mientras las interacciones de 2 factores se alían por pares (<em>AB = CD, AC = BD, AD = BC</em>). En la <strong>corrida de confirmación (n = 5)</strong>, la combinación óptima <strong>A+B+C+</strong> obtuvo una media real de <strong>{conf['observado_optimo_media_ms']:.2f} ms</strong>, cayendo dentro del <strong>IC 95% predicho [{conf['ic95_prediccion_ms'][0]:.2f}, {conf['ic95_prediccion_ms'][1]:.2f}] ms</strong>, confirmando una reducción de <strong>{conf['mejora_tiempo_pct']}% en tiempo ({conf['factor_aceleracion_speedup']}× más rápido, p<sub>Welch</sub> = {conf['p_valor_welch_confirmacion']})</strong> y <strong>{conf['reduccion_disco_pct']}% menos espacio en disco</strong> (1,936.8 KB &rarr; 171.7 KB).</p>
        <img class="figura" src="{fig5}" alt="Fraccionado 2^(4-1), Confirmación e ISO 25010">
        {_df_html(df_alias)}

        <h2>6. Evaluación ISO/IEC 25010–25012, Antecedentes Normativos, PSP y Relatoría E2</h2>
        <p>Siguiendo los antecedentes normativos (<strong>ISO/IEC 9126</strong> &rarr; reemplazada por <strong>ISO/IEC 25000 SQuaRE [25010 producto + 25012 datos]</strong>, complementada por el enfoque a procesos PHVA de <strong>ISO 9001:2015</strong>), se midieron objetivamente todas las características del observatorio (<code>docs/evaluacion-iso-25010-25012.md</code>): <strong>ISO/IEC 25010 = {res_iso['iso_25010_promedio_100']}/100</strong> (Fiabilidad real en 306 h de GitHub Actions: <strong>A = {res_iso['fiabilidad_acumulada_e0_e2']['disponibilidad_real_pct']}%</strong>, MTBF = {res_iso['fiabilidad_acumulada_e0_e2']['mtbf_horas']} h; Seguridad: <strong>0 secretos en {res_iso['seguridad_estatica']['archivos_escaneados']} archivos</strong>) e <strong>ISO/IEC 25012 = {res_iso['iso_25012_promedio_100']}/100</strong> (Completitud 100%, Linaje 100%, 0 PII).</p>
        {_df_html(df_iso10[["caracteristica", "valor_medido", "puntaje_100"]])}

        <!-- ==================== SECCIÓN 6.1: BITÁCORAS PSP Y RELATORÍA E2 ==================== -->

        <h3>6.1 Bitácoras PSP de la Etapa E2 (Tiempos y Defectos Cerrados)</h3>
        <p><strong>Sesiones registradas en E2 (<code>calidad/tiempo-norberto.csv</code> — 10.75 h netas):</strong></p>
        {_df_html(df_tiempo)}
        <p><strong>Defectos detectados y cerrados en E2 (<code>calidad/defectos-norberto.csv</code>):</strong></p>
        {_df_html(df_defectos)}

        <h3>6.2 Síntesis de la Relatoría de Etapa E2 (<code>docs/relatoria-E2.md</code>)</h3>
        <ol>
          <li><strong>¿Qué nos propusimos?</strong> Integrar la fuente geoespacial OSM/INEGI con unión espacial sin PII, documentar la ética/legalidad de las 3 fuentes, garantizar 100% de linaje en Capa Oro, ejecutar los diseños factoriales 2³, 2×3 y 2⁴⁻¹ con confirmación e integrar la evaluación ISO/IEC 25010–25012.</li>
          <li><strong>¿Qué hicimos?</strong> En 5 sesiones (18–22 nov, 10.75 h) desarrollamos <code>geoespacial_osm.py</code>, <code>geoespacial_e2.py</code>, <code>linaje_datos.py</code>, <code>experimento_doe_e2.py</code>, <code>evaluacion_iso_e2.py</code>, <code>figuras_e2.py</code>, el tablero ampliado <code>tablero/app.py</code> y 8 nuevas pruebas <code>pytest</code> (27/27 en verde).</li>
          <li><strong>¿Qué decidimos y por qué?</strong> Elegimos fuente geoespacial por su vínculo directo con logística portuaria/carretera en Colima; incrustamos 6 columnas de linaje en cada registro Oro para trazabilidad autónoma; y ejecutamos el DOE en copias locales para garantizar 0 carga a sitios externos.</li>
          <li><strong>¿Qué salió mal y cómo lo corregimos?</strong> Cerramos 3 defectos reales: <strong>Defecto #8</strong> (registro de código HTTP 429/5xx en <code>extractores/base.py</code> tras incidentes de Open-Meteo del 17–18 nov), <strong>Defecto #9</strong> (centroide continental de Tecomán excluyendo Revillagigedo) y <strong>Defecto #10</strong> (optimización de consulta Overpass QL).</li>
          <li><strong>¿Qué aprendimos?</strong> Confirmamos la importancia de reproyectar a <code>EPSG:32613</code> y documentar sesgos VGI en OSM, comprobamos causalmente la supremacía de Parquet + Pandera en el ANOVA 2³ con Puerta 3 aprobada, y articulamos evidencia objetiva de DOE y bitácoras para ISO/IEC 25010 y 25012.</li>
          <li><strong>Evidencias y Uso de IA Generativa:</strong> Todo vive bajo el tag <code>e2</code> verificado por CI. Se usó asistencia de IA generativa (Antigravity) para estructuración de código, gráficas y pruebas, verificando determinísticamente todas las capturas en vivo, corridas experimentales y cálculos en Python.</li>
        </ol>
      </td>
    </tr>
  </tbody>
</table>

</body>
</html>
"""

    html_temp = ROOT_DIR / "docs" / "E2" / "_temp_reporte_e2.html"
    pdf_out = ROOT_DIR / "docs" / "E2" / "Entrega_E2_Escareno_Norberto.pdf"
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

    copia_scratch = ROOT_DIR.parent / "Entrega_E2_Escareno_Norberto.pdf"
    shutil.copy2(pdf_out, copia_scratch)
    return pdf_out


if __name__ == "__main__":
    ruta = generar_pdf_e2()
    print(f"[OK] PDF E2 generado: {ruta} ({ruta.stat().st_size:,} bytes)")
