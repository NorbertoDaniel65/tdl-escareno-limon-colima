# Entrega E2 · CITRO-DATA LAB COLIMA

**Equipo:** Norberto Daniel Escareño Montaño (`No. Control: 23460323` · `@NorbertoDaniel65` · modalidad individual) · **Etiqueta:** `e2` · **Repositorio:** [`https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima`](https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima) · **Tablero:** `streamlit run tablero/app.py`

## Resumen en tres líneas

En la Etapa **E2** se integró la **Fuente Especializada Geoespacial** de OpenStreetMap (Nominatim + Overpass API + claves INEGI de los 10 municipios de Colima) con unión espacial `GeoPandas` (`1,074` nodos válidos + `90` fuera de límite en cuarentena, `0` PII), se formalizó la **Declaración de Ética y Legalidad (`docs/etica-datos.md`)** y se garantizó **100% de linaje registro-a-registro** (`310/310` registros de Capa Oro rastreables hasta archivo Bronce, `SHA-256` y fecha UTC). En paralelo, se ejecutó un **Experimento Factorial Real $2^3$**, un **ANOVA de Dos Vías ($2 \times 3$)** y la comparativa **$2^4$ vs. $2^{4-1}$ fraccionado (Resolución IV)** demostrando con corrida de confirmación ($n=5$ dentro del IC 95%) una reducción de **`78.95%` en latencia (`4.75×` más rápido)** y **`91.13%` en disco** con `0.0%` de error, además de evaluar cuantitativamente el observatorio bajo **ISO/IEC 25010 (`95.38/100`)** e **ISO/IEC 25012 (`97.58/100`)**.

---

## Ingeniería de Datos (Unidad 4: Fuente Especializada, Ética y Linaje de Datos)

| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
| :--- | :--- | :--- |
| **1. Fuente especializada integrada al pipeline y visible en el tablero, sin datos personales (45 pts)** | • Extractor: [`extractores/geoespacial_osm.py`](../../extractores/geoespacial_osm.py)<br>• Unión espacial `GeoPandas`: [`pipeline/geoespacial_e2.py`](../../pipeline/geoespacial_e2.py)<br>• Bronce: `data/bronce/geoespacial/municipios_colima_osm.geojson` y `infraestructura_agrologistica_colima_osm.geojson`<br>• Cuarentena geoespacial: [`data/cuarentena/cuarentena_geoespacial_e2.csv`](../../data/cuarentena/cuarentena_geoespacial_e2.csv)<br>• Capa Oro GeoJSON: [`data/oro/perfil_geoespacial_municipios_oro.geojson`](../../data/oro/perfil_geoespacial_municipios_oro.geojson)<br>• Mapa y Tablero: [`docs/E2/figuras/fig1_mapa_geoespacial_colima_e2.png`](figuras/fig1_mapa_geoespacial_colima_e2.png) y [`tablero/app.py`](../../tablero/app.py) | Se capturaron en vivo `10` polígonos municipales de Colima (`EPSG:4326`) y `1,164` nodos agrologísticos reales de OpenStreetMap. La unión `gpd.sjoin(puntos, poligonos, predicate="within")` aprobó `1,074` nodos dentro de Colima (`874` huertas, `169` empaque/bodega, `18` mercados, `13` comercio frutícola) y envió `90` nodos de Jalisco/Michoacán a cuarentena. Métricas de superficie y distancias al Puerto de Manzanillo y Autopista 54D proyectadas en `EPSG:32613`. **`0` columnas PII** verificado en `pytest`. |
| **2. Declaración de ética y legalidad de datos (30 pts)** | • Documento principal: [`docs/etica-datos.md`](../etica-datos.md)<br>• Ficha Fuente 3: [`docs/fuentes/osm_geoespacial.md`](../fuentes/osm_geoespacial.md)<br>• Evidencias `robots.txt`: `data/bronce/robots_txt/` (`open-meteo`, `sniim`, `nominatim`, `overpass-api.de`) | Análisis específico por cada una de las 3 fuentes: base legal (Art. 6°, LGTAIP, LFPDPPP), `robots.txt` archivados, términos de servicio, licencias (`CC BY 4.0`, `Libre Uso MX`, `ODbL 1.0`), lista blanca 0 PII, sesgos reales identificados (cobertura VGI en OSM Ixtlahuacán vs. Tecomán, resolución ERA5-Land, eslabón mayorista SNIIM, MultiPolygon insular Revillagigedo) y estrategias concretas de mitigación. |
| **3. Linaje y trazabilidad de datos Bronce $\to$ Oro (15 pts)** | • Módulo: [`pipeline/linaje_datos.py`](../../pipeline/linaje_datos.py)<br>• Manifiesto DAG: [`data/oro/linaje_datos_e2.json`](../../data/oro/linaje_datos_e2.json)<br>• Catálogo completo: [`data/oro/catalogo_linaje_oro_bronce.csv`](../../data/oro/catalogo_linaje_oro_bronce.csv)<br>• Diccionario actualizado: [`data/oro/diccionario_datos.md`](../../data/oro/diccionario_datos.md)<br>• Diagrama: [`docs/E2/figuras/fig2_arquitectura_linaje_bronce_oro_e2.png`](figuras/fig2_arquitectura_linaje_bronce_oro_e2.png) | **100.0% de cobertura (`310 / 310` registros)** en `serie_mensual_oro_60m.csv`, `panel_integrado_municipio_mercado_oro.csv` y `perfil_geoespacial_municipios_oro.csv` cuentan con `linaje_id_registro`, `linaje_fuentes_bronce`, `linaje_archivos_bronce`, `linaje_sha256_bronce`, `linaje_fecha_ingesta_utc` y `linaje_version_pipeline`. Rastreo verificable con `rastrear_registro_oro()` en `pytest` y en el tablero. |

---

## Análisis Estadístico para Ciencia de Datos (Unidad 4: Diseño de Experimentos)

| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
| :--- | :--- | :--- |
| **1. Diseño factorial $2^3$ real y principios: aleatorización, réplicas y bloqueo (25 pts)** | • Código: [`pipeline/experimento_doe_e2.py`](../../pipeline/experimento_doe_e2.py)<br>• Corridas: [`data/oro/experimento_factorial_2_3_corridas_e2.csv`](../../data/oro/experimento_factorial_2_3_corridas_e2.csv)<br>• ANOVA y Efectos: [`data/oro/anova_factorial_2_3_e2.csv`](../../data/oro/anova_factorial_2_3_e2.csv), [`data/oro/efectos_factorial_2_3_e2.csv`](../../data/oro/efectos_factorial_2_3_e2.csv)<br>• Figura: [`docs/E2/figuras/fig3_doe_factorial_2_3_efectos_pareto.png`](figuras/fig3_doe_factorial_2_3_efectos_pareto.png) | Ruta Ingeniería sobre copias locales de Capa Bronce (`0` tráfico externo): **Factor A** Paralelismo I/O (`1` vs `4` hilos), **Factor B** Validación (`Iterativa` vs `Pandera Vectorizado`), **Factor C** Formato (`CSV` vs `Parquet Snappy`). `24` corridas aleatorizadas (`semilla=23460323`), $r=3$ réplicas y `3` bloques (`B1–B3`). $R^2 = 0.9981$; efectos dominantes: **C (`-126.2 ms`, $|t|=60.8$)**, **B (`-123.8 ms`, $|t|=59.6$)** y **A (`-8.3 ms`, $|t|=4.0$)**. |
| **2. Diseño de dos factores con $\ge 3$ niveles y ANOVA de dos vías con interacción (20 pts)** | • Corridas: [`data/oro/experimento_dos_factores_2x3_e2.csv`](../../data/oro/experimento_dos_factores_2x3_e2.csv)<br>• ANOVA $2 \times 3$: [`data/oro/anova_dos_vias_2x3_e2.csv`](../../data/oro/anova_dos_vias_2x3_e2.csv)<br>• Tukey HSD: [`data/oro/tukey_hsd_formatos_2x3_e2.csv`](../../data/oro/tukey_hsd_formatos_2x3_e2.csv)<br>• Figura: [`docs/E2/figuras/fig4_anova_dos_vias_y_supuestos_residuos.png`](figuras/fig4_anova_dos_vias_y_supuestos_residuos.png) | Diseño $2 \times 3$ (`18` corridas aleatorizadas): Motor (`Iterativo`, `Pandera`) $\times$ Formato (`CSV UTF-8`, `Parquet Snappy`, `Parquet ZSTD`). Interacción $B \times C$ no significativa ($p = 0.774$), confirmando ganancia aditiva limpia. `Parquet ZSTD` logra `-92.8%` en disco (`140.1 KB` vs `1,936.8 KB`) y `70.61 ms` de latencia. |
| **3. Diseño $2^4$ completo vs. $2^{4-1}$ fraccionado, alias y ahorro cuantificado (20 pts)** | • Matrices: [`data/oro/matriz_2_4_completo_vs_fraccionado_e2.csv`](../../data/oro/matriz_2_4_completo_vs_fraccionado_e2.csv)<br>• Tabla de Alias: [`data/oro/estructura_alias_2_4_fraccionado_e2.csv`](../../data/oro/estructura_alias_2_4_fraccionado_e2.csv)<br>• Figura: [`docs/E2/figuras/fig5_fraccionado_2_4_y_confirmacion_optimo.png`](figuras/fig5_fraccionado_2_4_y_confirmacion_optimo.png) | Incorporando Factor D (`Partición 4 archivos` vs `Consolidado`): $2^4$ (`16` tratamientos) vs. $2^{4-1}$ (`8` tratamientos, relación definitoria $I = ABCD$, generador $D=ABC$, **Resolución IV**). **Ahorro exacto de `50.0%` de corridas**. Estructura de alias demostrada: efectos principales limpios de 2FI ($A=BCD, B=ACD, C=ABD, D=ABC$) y 2FI aliadas por pares ($AB=CD, AC=BD, AD=BC$). |
| **4. Análisis, validación de supuestos (Puerta 3) y corrida de confirmación del óptimo (25 pts)** | • Resumen JSON: [`data/oro/resumen_experimento_doe_e2.json`](../../data/oro/resumen_experimento_doe_e2.json)<br>• Confirmación ($n=5$): [`data/oro/corrida_confirmacion_optimo_e2.csv`](../../data/oro/corrida_confirmacion_optimo_e2.csv)<br>• Notebook: [`docs/E2/experimento_y_geodatos.ipynb`](experimento_y_geodatos.ipynb) | **Puerta 3 APROBADA en escala lineal y logarítmica:** Normalidad Shapiro-Wilk $W=0.9582$ ($p=0.4026$), Homocedasticidad Levene $F=0.5732$ ($p=0.7674$), Independencia Durbin-Watson $DW=2.0277$. **Confirmación del óptimo `A+B+C+` ($n=5$):** media observada **`70.93 ms`** dentro del IC 95% predicho **`[56.93, 82.90] ms`** $\implies$ **`-78.95%` tiempo (`4.75×` speedup, $p_{\text{Welch}} = 2.37 \times 10^{-7}$)** y **`-91.13%` disco** con `0.0%` error. |

---

## Calidad en los Sistemas de Información (ISO/IEC 25010, ISO/IEC 25012, Antecedentes y Auditoría)

| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
| :--- | :--- | :--- |
| **Evaluación ISO/IEC 25010, ISO/IEC 25012, Antecedentes Normativos y Auditoría Técnica de E1** | • Reporte completo: [`docs/evaluacion-iso-25010-25012.md`](../evaluacion-iso-25010-25012.md)<br>• Código de medición: [`pipeline/evaluacion_iso_e2.py`](../../pipeline/evaluacion_iso_e2.py)<br>• Tablas: `data/oro/evaluacion_iso_25010_e2.csv` y `evaluacion_iso_25012_e2.csv`<br>• Bitácoras PSP: [`calidad/tiempo-norberto.csv`](../../calidad/tiempo-norberto.csv) y [`calidad/defectos-norberto.csv`](../../calidad/defectos-norberto.csv) | **ISO/IEC 25010:** promedio **`95.38 / 100`** (8 características medidas; *Eficiencia* probada por DOE, *Fiabilidad* real sobre `306 h` de GitHub Actions `A = 99.74%`, `MTBF = 101.73 h`, *Seguridad* `0` secretos en `144` archivos). **ISO/IEC 25012:** promedio **`97.58 / 100`** (`100%` completitud y `100%` linaje en Capa Oro). Cuadro normativo `ISO 9126 → SQuaRE (25010/25012) ↔ ISO 9001` y auditoría de `e1` con 5 hallazgos clasificados (`AUD-01` a `AUD-05`). |

---

## Relatoría de etapa y Reporte PDF Oficial

* **Relatoría E2 (6 preguntas + Uso de IA):** [`docs/relatoria-E2.md`](../relatoria-E2.md)
* **Reporte Ejecutivo Oficial PDF (Molde TecNM / IT Colima):** [`docs/E2/Entrega_E2_Escareno_Norberto.pdf`](Entrega_E2_Escareno_Norberto.pdf)

## Issues de la entrega anterior (`e1`)

* **Issues de docentes en GitHub:** `0` issues abiertos en `NorbertoDaniel65/tdl-escareno-limon-colima` al corte de `e2`.
* **Incidentes operativos y hallazgos internos cerrados en `e2`:**
  * `Defecto #8` (`AUD-01`): Registro de código HTTP `429/5xx` en `extractores/base.py` y soporte `POST` ético tras fallos de `api.open-meteo.com` el `17–18 nov 2026`.
  * `Defecto #9` (`AUD-04`): Corrección de centroide continental en `MultiPolygon` de Tecomán (islas Revillagigedo) dentro de `pipeline/geoespacial_e2.py`.
  * `Defecto #10`: Optimización de consulta Overpass QL en `extractores/geoespacial_osm.py`.

---

## Instrucciones de Reproducción Determinista

```bash
pip install -r requirements.txt
python -m pipeline.geoespacial_e2
python -m pipeline.linaje_datos
python -m pipeline.experimento_doe_e2
python -m pipeline.evaluacion_iso_e2
python -m pipeline.figuras_e2
python -m pipeline.verificar_e2
pytest -v
streamlit run tablero/app.py
```
