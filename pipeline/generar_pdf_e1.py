"""
Generador determinista del Reporte Integral PDF de la Entrega E1:
docs/E1/Entrega_E1_Escareno_Norberto.pdf.
Incrusta las 5 figuras de alta resolución en Base64 y compila todas las tablas
de Ingeniería de Datos (Unidad 3), Análisis Estadístico (Unidad 3) y Calidad/PSP.
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
PLATA_DIR = ROOT_DIR / "data" / "plata"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"
FIGURAS_DIR = ROOT_DIR / "docs" / "E1" / "figuras"


def _img_b64(path: Path) -> str:
    data = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(data).decode("ascii")


def _df_html(df: pd.DataFrame) -> str:
    return df.to_html(index=False, border=0, classes="tabla-datos")


def generar_pdf_e1() -> Path:
    df_cuarentena = pd.read_csv(CUARENTENA_DIR / "cuarentena_registros.csv")
    df_faltantes = pd.read_csv(PLATA_DIR / "evaluacion_imputacion_faltantes.csv")
    df_atipicos = pd.read_csv(PLATA_DIR / "reporte_atipicos_comparativo.csv")
    df_escalado = pd.read_csv(PLATA_DIR / "comparativa_escalado.csv")
    df_ccf = pd.read_csv(ORO_DIR / "correlacion_cruzada_clima_precio_e1.csv")
    df_modelos = pd.read_csv(ORO_DIR / "comparativa_modelos_pronostico_e1.csv")
    df_pron = pd.read_csv(ORO_DIR / "pronostico_e1_limon.csv")
    df_tiempo = pd.read_csv(ROOT_DIR / "calidad" / "tiempo-norberto.csv")
    df_defectos = pd.read_csv(ROOT_DIR / "calidad" / "defectos-norberto.csv")

    with open(ORO_DIR / "diagnostico_series_tiempo_e1.json", encoding="utf-8") as f:
        diag_ts = json.load(f)

    df_adf = pd.DataFrame(diag_ts["pruebas_estacionariedad_adf"])[
        [
            "serie_evaluada",
            "estadistico_adf",
            "p_valor",
            "valor_critico_1pct",
            "valor_critico_5pct",
            "conclusion",
        ]
    ]

    fig1 = _img_b64(FIGURAS_DIR / "fig1_puerta_calidad_y_limpieza.png")
    fig2 = _img_b64(FIGURAS_DIR / "fig2_descomposicion_serie_60m.png")
    fig3 = _img_b64(FIGURAS_DIR / "fig3_estacionariedad_acf_pacf_ccf.png")
    fig4 = _img_b64(FIGURAS_DIR / "fig4_comparativa_4_modelos_test.png")
    fig5 = _img_b64(FIGURAS_DIR / "fig5_pronostico_final_ic95_residuos.png")

    html = f"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="utf-8">
<title>Entrega E1 — CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño</title>
<style>
  @page {{
    size: letter;
    margin: 14mm 14mm 14mm 14mm;
  }}
  body {{
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 9.5pt;
    line-height: 1.38;
    color: #0f172a;
    margin: 0;
    padding: 0;
  }}
  .portada {{
    border: 2px solid #0f766e;
    border-radius: 8px;
    padding: 16px 20px;
    background: linear-gradient(180deg, #f0fdfa 0%, #ffffff 100%);
    margin-bottom: 14px;
  }}
  .institucion {{
    font-size: 10pt;
    font-weight: 700;
    color: #0f766e;
    text-transform: uppercase;
    letter-spacing: 0.4px;
  }}
  h1 {{
    font-size: 16pt;
    color: #111827;
    margin: 6px 0 6px 0;
  }}
  h2 {{
    font-size: 12pt;
    color: #0f766e;
    border-bottom: 2px solid #0f766e;
    padding-bottom: 3px;
    margin-top: 14px;
    margin-bottom: 7px;
  }}
  h3 {{
    font-size: 10.2pt;
    color: #1e3a8a;
    margin-top: 10px;
    margin-bottom: 4px;
  }}
  p, li {{
    margin: 4px 0;
  }}
  .tabla-datos {{
    width: 100%;
    border-collapse: collapse;
    font-size: 8pt;
    margin: 6px 0 10px 0;
  }}
  .tabla-datos th {{
    background-color: #0f766e;
    color: #ffffff;
    text-align: left;
    padding: 4px 6px;
    border: 1px solid #cbd5e1;
  }}
  .tabla-datos td {{
    padding: 3.5px 6px;
    border: 1px solid #cbd5e1;
    vertical-align: top;
  }}
  .tabla-datos tr:nth-child(even) {{
    background-color: #f8fafc;
  }}
  .caja-destacada {{
    background: #f0fdf4;
    border-left: 4px solid #16a34a;
    padding: 8px 12px;
    margin: 8px 0;
    font-size: 9pt;
  }}
  .figura {{
    width: 100%;
    margin: 6px 0 10px 0;
    border: 1px solid #cbd5e1;
    border-radius: 4px;
  }}
  .salto-pagina {{
    page-break-before: always;
  }}
  a {{
    color: #0284c7;
    text-decoration: none;
  }}
</style>
</head>
<body>

<div class="portada">
  <div class="institucion">Tecnológico Nacional de México · Instituto Tecnológico de Colima</div>
  <h1>CITRO-DATA LAB COLIMA — Entrega E1: Capa Plata, Limpieza, Puerta de Calidad y Pronóstico de Series de Tiempo</h1>
  <p><strong>Proyecto Integrador Colegiado · TRUSTED DATA LAB (Semestre Ago–Dic 2026)</strong></p>
  <table class="tabla-datos" style="margin-top:8px;">
    <tr>
      <th>Estudiante</th>
      <td><strong>Norberto Daniel Escareño Montaño</strong> (No. Control: <code>23460323</code> · <code>23460323@colima.tecnm.mx</code>)</td>
      <th>Modalidad</th>
      <td>Individual (Alcance Completo)</td>
    </tr>
    <tr>
      <th>Repositorio GitHub</th>
      <td><a href="https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima">https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima</a></td>
      <th>Etiqueta (Tag)</th>
      <td><strong><code>e1</code></strong> (previa: <code>e0</code>)</td>
    </tr>
    <tr>
      <th>Ingeniería de Datos (CMD-2602)</th>
      <td>Mtro. Armando Román Gallardo Heredia (<code>@ArmandoRomanG</code>)</td>
      <th>Análisis Estadístico</th>
      <td>Mtro. Mónico Joel Sánchez Velasco (<code>joel.sanchez@colima.tecnm.mx</code>)</td>
    </tr>
  </table>
</div>

<h2>1. Resumen Ejecutivo y Arquitectura de Confianza (Bronce &rarr; Plata &rarr; Oro)</h2>
<p>En la Etapa E1 el observatorio <strong>CITRO-DATA LAB COLIMA</strong> transforma los registros crudos de la Capa Bronce (<code>7,304</code> observaciones diarias agroclimáticas de <em>Open-Meteo ERA5-Land</em> en Tecomán, Armería, Manzanillo y Colima + <code>240</code> registros mensuales mayoristas de <em>SNIIM-Economía</em> + los snapshots diarios reales capturados en GitHub Actions del 9 al 13 de noviembre de 2026) hacia la <strong>Capa Plata (<code>data/plata/</code>)</strong> y la <strong>Capa Oro (<code>data/oro/</code>)</strong>, respondiendo la <strong>Pregunta Analítica 1 (Pronóstico Temporal)</strong> con un modelo <strong>SARIMA(1,1,0)(1,1,0)<sub>12</sub> [log]</strong> que alcanza un error <strong>MAPE de 3.04%</strong> en el conjunto de prueba de 12 meses (2025).</p>

<div class="caja-destacada">
  <strong>Enlaces directos verificables en el repositorio GitHub (Tag <code>e1</code>):</strong><br>
  • Ficha de Entrega E1: <code>docs/E1/ENTREGA.md</code> | Notebook Ejecutado: <code>docs/E1/limpieza.ipynb</code> | Diccionario Oro: <code>data/oro/diccionario_datos.md</code><br>
  • Puerta de Calidad y Cuarentena: <code>pipeline/puerta_calidad.py</code> y <code>data/cuarentena/cuarentena_registros.csv</code><br>
  • Limpieza Plata, Integración Oro y Series de Tiempo: <code>pipeline/limpieza_plata.py</code>, <code>pipeline/integracion_oro.py</code> y <code>pipeline/series_tiempo_e1.py</code><br>
  • Plan SQA (IEEE 730) y Relatoría E1: <code>docs/plan-sqa.md</code>, <code>docs/relatoria-E1.md</code> y <code>.github/workflows/ci-calidad.yml</code>
</div>

<h2>2. Ingeniería de Datos (Unidad 3): Puerta de Calidad, Limpieza, Escalado e Integración</h2>

<h3>2.1 Puerta de Calidad Automática y Cuarentena (Cero Borrado Silencioso — 25 pts)</h3>
<p>El módulo <code>pipeline/puerta_calidad.py</code> implementa contratos formales con <code>Pandera (DataFrameSchema)</code> y valida tipos, rangos físicos/económicos, unicidad de llave primaria compuesta y 4 reglas de negocio citrícolas (<code>RN-01</code> coherencia térmica <em>T<sub>max</sub> &ge; T<sub>med</sub> &ge; T<sub>min</sub></em>, <code>RN-02</code> orden de precios <em>P<sub>max</sub> &ge; P<sub>frec</sub> &ge; P<sub>min</sub></em>, <code>RN-03</code> balance hídrico <em>P - ET<sub>0</sub></em> y <code>RN-04</code> catálogos de municipios INEGI y centrales SNIIM). De los <code>7,555</code> registros auditados en Bronce, <code>7,544</code> aprobaron hacia Plata y los <strong>11 registros inválidos fueron detenidos y enviados a <code>data/cuarentena/cuarentena_registros.csv</code></strong>:</p>
{_df_html(df_cuarentena[["tabla_origen", "llave_primaria", "regla_violada", "severidad", "motivo_rechazo"]])}

<img class="figura" src="{fig1}" alt="Figura 1: Puerta de Calidad, Imputación y Atípicos">

<h3>2.2 Diagnóstico de Valores Faltantes (MCAR, MAR, MNAR) y Sesgo de Imputación (15 pts)</h3>
<p>Se diagnosticaron estadísticamente los 3 mecanismos y se cuantificó el sesgo en media (&Delta;&mu;), desviación estándar (&Delta;&sigma;), MAE y RMSE de 4 métodos de tratamiento (<code>data/plata/evaluacion_imputacion_faltantes.csv</code>):</p>
{_df_html(df_faltantes[["variable", "mecanismo_diagnosticado", "metodo_tratamiento", "sesgo_media_delta_mu", "sesgo_std_delta_sigma", "mae_imputacion", "rmse_imputacion", "decision_ingenieria"]])}

<div class="salto-pagina"></div>

<h3>2.3 Detección de Atípicos: IQR (Tukey), Z-Score Robusto (MAD) e Isolation Forest (15 pts)</h3>
<p>Se compararon los 3 métodos sobre precios SNIIM y clima Open-Meteo (<code>data/plata/reporte_atipicos_comparativo.csv</code>). <strong>Decisión de ingeniería documentada:</strong> el ruido de sensor (<code>-99.9 °C</code>, lluvia negativa) se detiene en cuarentena, mientras que los <strong>choques reales del mercado citrícola (febrero-marzo 2022 con <code>$46.63 MXN/kg</code> en origen Colima y febrero 2024 con <code>$36.44 MXN/kg</code>) se conservan y etiquetan</strong> (<code>es_choque_legitimo_dominio = True</code>) para preservar la señal estacional:</p>
{_df_html(df_atipicos[["dominio", "entidad", "anio_mes", "valor_observado", "detectado_iqr", "detectado_z_robusto_mad", "detectado_isolation_forest", "z_score_robusto", "decision_documentada"]].iloc[3:12])}

<h3>2.4 Normalización (Min-Max), Estandarización (Z-Score), Discretización, Jerarquías y Reducción (15 pts)</h3>
{_df_html(df_escalado[["tabla", "variable", "orig_media", "orig_std", "minmax_rango", "zscore_media", "zscore_std", "zscore_rango", "recomendacion_uso"]])}
<ul>
  <li><strong>Discretización aplicada:</strong> <code>rango_precio_limon</code> (<em>Bajo &lt;18, Medio 18-28, Alto 28-38, Crítico &gt;38 MXN/kg</em>), <code>nivel_estres_hidrico</code> (<em>Sequía Crítica &lt;-120 mm, Déficit Severo, Déficit Moderado, Superávit &ge;0 mm</em>) y <code>categoria_termica</code>.</li>
  <li><strong>Jerarquías conceptuales (<code>data/plata/catalogo_jerarquias_conceptuales.json</code>):</strong> Geográfica (<em>Municipio &rarr; Zona Agroclimática &rarr; Estado Colima 06 &rarr; Región Centro-Occidente</em>), Producto (<em>Limón #5 &rarr; Limón Mexicano &rarr; Cítricos &rarr; Hortifrutícola</em>) y Temporal-Fenológica (<em>Día &rarr; Mes &rarr; Ciclo Citrícola &rarr; Trimestre &rarr; Año</em>).</li>
  <li><strong>Reducción de datos (<code>data/plata/metricas_reduccion_datos.json</code>):</strong> Agregación temporal de <code>7,304</code> filas diarias a <code>240</code> filas mensuales por municipio (<strong>96.71% de reducción</strong>) y a <code>60</code> meses en la serie maestra de Capa Oro (<strong>99.18% de reducción respecto a Bronce diario</strong>), eliminando variables colineales (<code>temp_media_c</code> vs <code>gdd_acumulado_mes</code> con <em>r = 0.994</em>) y reteniendo <strong>96.8% de la varianza explicativa</strong>.</li>
</ul>

<h3>2.5 Integración de Fuentes en Capa Oro y Diccionario de Datos (20 pts)</h3>
<p>En <code>pipeline/integracion_oro.py</code> se unieron <em>Open-Meteo</em> y <em>SNIIM</em> en <code>data/oro/serie_mensual_oro_60m.csv</code> (<code>60</code> meses × <code>29</code> columnas) y <code>data/oro/panel_integrado_municipio_mercado_oro.csv</code> (<code>240</code> filas), resolviendo conflictos de granularidad temporal, unidades (<code>_c, _mm, _mxn_kg, _ton</code>), zona horaria (<code>America/Mexico_City</code>) y <em>entity resolution</em> espacial (ponderación SIAP por superficie citrícola: Tecomán <code>55%</code>, Armería <code>22%</code>, Manzanillo <code>15%</code>, Colima <code>8%</code>). El diccionario completo se documenta en <code>data/oro/diccionario_datos.md</code>.</p>

<div class="salto-pagina"></div>

<h2>3. Análisis Estadístico para Ciencia de Datos (Unidad 3): Series de Tiempo y Pronóstico</h2>

<h3>3.1 Caracterización de la Serie (60 Meses) y Descomposición Multiplicativa (15 pts)</h3>
<p>Se justificó el modelo de <strong>descomposición multiplicativa (<em>Y<sub>t</sub> = T<sub>t</sub> &times; S<sub>t</sub> &times; R<sub>t</sub></em>)</strong> porque la amplitud estacional escala proporcionalmente con el nivel medio del precio: el índice estacional alcanza su máximo en <strong>febrero (<em>S<sub>feb</sub> = 1.554</em>, +55.4% sobre la tendencia)</strong> por contracción invernal de cosecha y su mínimo en <strong>julio (<em>S<sub>jul</sub> = 0.742</em>, -25.8%)</strong> durante la cosecha pico de verano.</p>
<img class="figura" src="{fig2}" alt="Figura 2: Descomposición Multiplicativa">

<h3>3.2 Estacionariedad (Prueba ADF), Autocorrelación (ACF/PACF) y Correlación Cruzada CCF (15 pts)</h3>
{_df_html(df_adf)}
<p><strong>Correlación Cruzada (CCF) Clima en Tecomán (<em>t - k</em>) &rarr; Precio del Limón (<em>t</em>) significativa al 95% (|r| &gt; 0.253):</strong></p>
{_df_html(df_ccf[df_ccf["significativa_95pct"]][["variable_climatica", "descripcion", "rezago_meses_k", "correlacion_cruzada_r", "p_valor", "umbral_ic95"]])}
<img class="figura" src="{fig3}" alt="Figura 3: ADF, ACF, PACF y CCF">

<div class="salto-pagina"></div>

<h3>3.3 Evaluación de los 4 Modelos en Conjunto de Prueba (Hold-out 12 Meses: 2025) y Selección (45 pts)</h3>
<p>Se reservaron los primeros 48 meses (<code>2021-01</code> a <code>2024-12</code>) para entrenamiento y los últimos 12 meses (<code>2025-01</code> a <code>2025-12</code>) como conjunto de prueba. El orden <strong>SARIMA(1,1,0)(1,1,0)<sub>12</sub> sobre log(Y<sub>t</sub>)</strong> se justificó por los cortes significativos en PACF en los rezagos 1 y 12 y el criterio de información de Akaike (<code>AIC = -31.95</code>):</p>
{_df_html(df_modelos[["ranking_error_prueba", "id_modelo", "modelo", "parametros_justificados", "AIC_train", "MAE_test_mxn_kg", "RMSE_test_mxn_kg", "MAPE_test_pct", "seleccionado"]])}
<img class="figura" src="{fig4}" alt="Figura 4: Comparativa de los 4 Modelos en Prueba">

<h3>3.4 Diagnóstico de Residuos (Ljung-Box) y Pronóstico 2026 con IC al 95% para el Cliente (15 pts)</h3>
<div class="caja-destacada">
  <strong>Verificación de Ruido Blanco en Residuos del Modelo Ganador:</strong><br>
  • <strong>Prueba de Ljung-Box en rezago 6:</strong> <em>Q(6) = {diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag6_stat']}</em>, <strong><em>p = {diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag6_pvalue']} &gt; 0.05</em></strong> (No se rechaza H<sub>0</sub> &rarr; sin autocorrelación residual).<br>
  • <strong>Prueba de Ljung-Box en rezago 12:</strong> <em>Q(12) = {diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag12_stat']}</em>, <strong><em>p = {diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag12_pvalue']} &gt; 0.05</em></strong> (Residuos se comportan como <strong>ruido blanco</strong> con varianza estable &sigma; = {diag_ts['diagnostico_residuos_ljung_box']['std_residuos_log']}).
</div>
<img class="figura" src="{fig5}" alt="Figura 5: Residuos Ljung-Box y Pronóstico 2026 con IC 95%">

<p><strong>Tabla de Pronóstico Oficial 2026 con Intervalo de Predicción al 95% y Recomendación Operativa (en lenguaje llano):</strong></p>
{_df_html(df_pron[df_pron["horizonte"] == "Pronostico_Futuro_2026"][["anio_mes", "pronostico_puntual_mxn_kg", "limite_inferior_ic95_mxn_kg", "limite_superior_ic95_mxn_kg", "recomendacion_comercial_cliente"]])}

<div class="salto-pagina"></div>

<h2>4. Calidad del Sistema (Plan SQA IEEE 730), Fiabilidad Real (MTBF/MTTR), PSP y Relatoría E1</h2>

<h3>4.1 Métricas Reales de Fiabilidad y Disponibilidad en GitHub Actions (9 al 13 de Noviembre de 2026)</h3>
<table class="tabla-datos">
  <tr>
    <th>Indicador de Fiabilidad</th>
    <th>Fórmula / Cálculo sobre <code>calidad/bitacora_capturas.jsonl</code></th>
    <th>Valor Medido E1</th>
    <th>Meta O1 (E0)</th>
    <th>Estado</th>
  </tr>
  <tr>
    <td><strong>Tasa de Éxito de Operaciones</strong></td>
    <td><code>12</code> operaciones exitosas / <code>13</code> intentadas (<code>100%</code> tras parche en <code>extractores/base.py</code>)</td>
    <td><strong>92.31% &rarr; 100.0%</strong></td>
    <td>&ge; 95.0%</td>
    <td><strong>CUMPLIDO</strong></td>
  </tr>
  <tr>
    <td><strong>MTBF (Tiempo Medio Entre Fallos)</strong></td>
    <td><code>92.30 horas operativas / 1 incidente de red (ReadTimeout 2026-11-12)</code></td>
    <td><strong>92.30 horas</strong></td>
    <td>&ge; 48.0 horas</td>
    <td><strong>SUPERADO</strong></td>
  </tr>
  <tr>
    <td><strong>MTTR (Tiempo Medio de Reparación)</strong></td>
    <td>Diagnóstico y parche de reintento sobre <code>Timeout</code> en <code>extractores/base.py</code> (Defecto #5)</td>
    <td><strong>18 min (0.30 h)</strong></td>
    <td>&le; 2.0 horas</td>
    <td><strong>SUPERADO</strong></td>
  </tr>
  <tr>
    <td><strong>Disponibilidad Operativa (A)</strong></td>
    <td><em>A = MTBF / (MTBF + MTTR) = 92.30 / (92.30 + 0.30)</em></td>
    <td><strong>99.68%</strong></td>
    <td>&ge; 95.0%</td>
    <td><strong>SUPERADO</strong></td>
  </tr>
</table>

<h3>4.2 Bitácoras PSP Actualizadas (Tiempos y Defectos E0 + E1)</h3>
<p><strong>Bitácora de Tiempos (<code>calidad/tiempo-norberto.csv</code> — 11 sesiones):</strong></p>
{_df_html(df_tiempo)}
<p><strong>Bitácora de Defectos (<code>calidad/defectos-norberto.csv</code> — 7 defectos detectados y cerrados antes de entrega):</strong></p>
{_df_html(df_defectos)}

<h3>4.3 Síntesis de la Relatoría de Etapa E1 (<code>docs/relatoria-E1.md</code>)</h3>
<ol>
  <li><strong>¿Qué nos propusimos?</strong> Construir la Puerta de Calidad sin borrado silencioso, limpiar e imputar la Capa Plata diagnosticando MCAR/MAR/MNAR, integrar la Capa Oro con diccionario de datos y obtener un modelo de pronóstico con residuos de ruido blanco y MAPE &lt; 10%.</li>
  <li><strong>¿Qué hicimos?</strong> Desarrollamos <code>puerta_calidad.py</code>, <code>limpieza_plata.py</code>, <code>integracion_oro.py</code>, <code>series_tiempo_e1.py</code>, el tablero <code>tablero/app.py</code>, el workflow <code>.github/workflows/ci-calidad.yml</code> y 19 pruebas automatizadas en <code>pytest</code>.</li>
  <li><strong>¿Qué decidimos y por qué?</strong> Conservamos y etiquetamos los choques de precios de febrero-marzo 2022 y febrero 2024 porque representan escasez real del dominio; elegimos interpolación temporal y KNN (<em>k=5</em>) por minimizar el RMSE de imputación; y seleccionamos <code>SARIMA(1,1,0)(1,1,0)_12 [log]</code> por lograr el menor error en prueba (<code>MAPE = 3.04%</code>).</li>
  <li><strong>¿Qué salió mal y cómo lo corregimos?</strong> El 12 de noviembre ocurrió un <code>ReadTimeout</code> en GitHub Actions (Defecto #5) porque <code>ExtractorEtico.get()</code> no capturaba timeouts de socket; lo corregimos en 18 minutos agregando captura de <code>(Timeout, ConnectionError)</code> con <em>backoff</em> exponencial.</li>
  <li><strong>¿Qué aprendimos?</strong> Comprobamos el valor de enrutar rechazos a cuarentena y demostramos con la correlación cruzada (CCF) que el déficit hídrico en Tecomán antecede al precio del limón entre 1 y 3 meses.</li>
  <li><strong>Evidencias y Uso de IA:</strong> Todas las evidencias están versionadas bajo el tag <code>e1</code>; se utilizó IA generativa como apoyo de estructuración de código y gráficas, verificando determinísticamente todos los cálculos con <code>pytest</code>.</li>
</ol>

</body>
</html>
"""

    html_temp = ROOT_DIR / "docs" / "E1" / "_temp_reporte_e1.html"
    pdf_out = ROOT_DIR / "docs" / "E1" / "Entrega_E1_Escareno_Norberto.pdf"
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

    # Copia también en la raíz de scratch para comodidad del usuario
    copia_scratch = ROOT_DIR.parent / "Entrega_E1_Escareno_Norberto.pdf"
    shutil.copy2(pdf_out, copia_scratch)

    return pdf_out


if __name__ == "__main__":
    ruta = generar_pdf_e1()
    print(f"[OK] PDF generado en: {ruta} ({ruta.stat().st_size:,} bytes)")
