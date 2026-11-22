# Relatoría E2 · CITRO-DATA LAB COLIMA

**Equipo:** Norberto Daniel Escareño Montaño (`No. Control: 23460323`, `@NorbertoDaniel65`, modalidad individual) · **Periodo:** `2026-11-18` a `2026-11-22` · **Etiqueta Git:** `e2`

---

## 1. Qué nos propusimos

En la Etapa E2 nos propusimos tres objetivos medibles:
1. **Ingeniería de Datos (U4):** Integrar la **Fuente Especializada Geoespacial** (polígonos municipales de Colima + infraestructura agrologística real de OpenStreetMap vía Nominatim y Overpass API con `GeoPandas`, `0` datos personales), publicar la **Declaración de Ética y Legalidad (`docs/etica-datos.md`)** para las 3 fuentes y asegurar **100% de linaje registro-a-registro** desde Capa Bronce hasta Capa Oro (con archivo origen, `SHA-256` y fecha UTC), todo visible en el tablero `tablero/app.py`.
2. **Análisis Estadístico (U4):** Ejecutar el **Experimento Factorial Real $2^3$** (Ruta Ingeniería sobre copias locales del pipeline, $r=3$ réplicas, aleatorizado y bloqueado en 3 bloques), un **ANOVA de Dos Vías $2 \times 3$ con interacción** (`CSV`, `Parquet Snappy`, `Parquet ZSTD`), la comparativa **$2^4$ completo vs. $2^{4-1}$ fraccionado (Resolución IV, 50% ahorro)**, aprobar la **Puerta de Calidad 3** en supuestos de residuos y confirmar el punto óptimo con $n=5$ corridas dentro del IC 95%.
3. **Calidad y Evaluación Normativa:** Medir cuantitativamente el observatorio con **ISO/IEC 25010** (8 características) e **ISO/IEC 25012** (15 características sobre Capa Oro), actualizar las bitácoras PSP y cerrar los incidentes operativos registrados en GitHub Actions durante la semana.

---

## 2. Qué hicimos (cronología con fechas, responsable y horas)

Registro trazado contra [`calidad/tiempo-norberto.csv`](../calidad/tiempo-norberto.csv) (total etapa E2: **10.75 horas netas** en 5 sesiones, todas ejecutadas por **Norberto Daniel Escareño Montaño**):

| Fecha | Horario (Neto) | Fase PSP | Actividad Realizada y Artefactos Producidos |
| :---: | :---: | :---: | :--- |
| `2026-11-18` | `17:30–19:00` (`1.33 h`) | `revision` | Panel de medio término y diagnóstico de los 2 fallos reales de GitHub Actions (`Run #44168162030` del 17 nov y `Run #44384386430` del 18 nov por respuestas HTTP `5xx/429` de `api.open-meteo.com`). |
| `2026-11-19` | `16:00–18:15` (`2.08 h`) | `diseno` | Diseño de la Fuente 3 geoespacial (`OSM Nominatim/Overpass + claves INEGI`), contrato de las 6 columnas de linaje por registro en Capa Oro y matrices experimentales $2^3$, $2 \times 3$ y $2^4 / 2^{4-1}$. |
| `2026-11-20` | `17:00–19:30` (`2.25 h`) | `codigo` | Corrección de `extractores/base.py` (registro de código HTTP en `ultimo_error` y nuevo método `post()` ético), construcción de `extractores/geoespacial_osm.py` (captura real de `10` polígonos y `1,164` nodos en Colima) y `pipeline/geoespacial_e2.py` (`gpd.sjoin(within)`, cuarentena de `90` puntos fuera de Colima). |
| `2026-11-21` | `15:30–18:30` (`2.83 h`) | `codigo` | Implementación de `pipeline/linaje_datos.py` (`310/310` registros Oro rastreables), `pipeline/experimento_doe_e2.py` (`84` corridas experimentales reales) y `pipeline/evaluacion_iso_e2.py` (ISO/IEC 25010 y 25012). |
| `2026-11-22` | `09:30–12:00` (`2.33 h`) | `pruebas` | Generación de `5` figuras HD (`pipeline/figuras_e2.py`), actualización interactiva de `tablero/app.py`, redacción de `docs/etica-datos.md`, `docs/evaluacion-iso-25010-25012.md`, `docs/E2/ENTREGA.md`, `docs/relatoria-E2.md`, pruebas `pytest` E2 y PDF oficial TecNM. |

---

## 3. Qué decidimos y por qué (alternativas descartadas)

1. **Decisión 1 — Fuente Especializada Geoespacial (OSM Nominatim + Overpass API + Claves INEGI) en lugar de API de Redes Sociales:**
   * *Alternativa descartada:* Extracción de menciones en Mastodon/Reddit o YouTube Data API.
   * *Justificación:* En la cadena agroindustrial del limón en Colima, la ubicación física de huertas, bodegas/empacadoras y distancias métricas al **Puerto de Manzanillo** (`54.1 km` desde Tecomán, `31.5 km` desde Armería) y a la **Autopista 54D hacia Guadalajara** explican directamente el costo logístico y el *spread* de precios que el productor describió en la entrevista de E0. Además elimina por completo el riesgo de capturar perfiles de personas físicas (LFPDPPP).
2. **Decisión 2 — Linaje embebido en cada registro de Capa Oro + Manifiesto DAG (`linaje_datos_e2.json`) en lugar de solo metadatos a nivel archivo:**
   * *Alternativa descartada:* Confiar únicamente en los archivos `.meta.json` de Capa Bronce sin columnas de trazabilidad en las tablas Oro.
   * *Justificación:* Si un auditor o cliente exporta una sola fila de `serie_mensual_oro_60m.csv` (por ejemplo, `ORO-SERIE-2022-02` con `$46.63 MXN/kg`), las 6 columnas embebidas permiten rastrear inmediatamente los dos archivos de Capa Bronce, sus hashes `SHA-256` y sus marcas UTC de ingesta sin perder contexto.
3. **Decisión 3 — Ruta Ingeniería en entorno local aislado para el Experimento Factorial $2^3$ en lugar de pruebas de estrés contra APIs externas:**
   * *Alternativa descartada:* Variar concurrencia HTTP directamente contra `sniim.gob.mx` u `open-meteo.com`.
   * *Justificación:* La ética del proyecto prohíbe saturar servidores ajenos. Correr las `84` corridas sobre particiones locales reales de Capa Bronce en `tempfile.TemporaryDirectory` garantizó `0` impacto externo, reproducibilidad exacta ($R^2 = 0.9981$) y evidencia directa para la característica *Eficiencia de Desempeño* de ISO/IEC 25010 (`-78.95%` tiempo y `-91.13%` disco).

---

## 4. Qué salió mal y cómo lo corregimos (con número de defecto)

1. **Fallos transitorios HTTP `5xx/429` en GitHub Actions sin código de error registrado (`Defecto #8`, `15 min`):**
   * *Qué salió mal:* Los días `17` y `18 de noviembre` (`Runs #44168162030` y `#44384386430`), `api.open-meteo.com` devolvió errores de servidor y `ExtractorEtico.get()` lanzó `RuntimeError(...: None)` porque la rama `if r.status_code == 429 or r.status_code >= 500` no asignaba `ultimo_error`.
   * *Corrección:* En `extractores/base.py` se registró `ultimo_error = RuntimeError(f"HTTP {r.status_code} ({r.reason})")` y se añadió `ExtractorEtico.post()` con el mismo control ético; las capturas del `19, 20 y 21 de noviembre` volvieron a completar con éxito (`100%`).
2. **Desplazamiento oceánico del centroide de Tecomán por el Archipiélago de Revillagigedo (`Defecto #9`, `14 min`):**
   * *Qué salió mal:* Al graficar el mapa de Colima (`fig1`), la etiqueta de **Tecomán** desapareció del mapa y su distancia al Puerto de Manzanillo marcaba `81.43 km` en lugar de `~54 km`, porque administrativamente Tecomán (`06009`) es un `MultiPolygon` que incluye las islas oceánicas de Revillagigedo en el Pacífico.
   * *Corrección:* Se corrigió `pipeline/geoespacial_e2.py` seleccionando el polígono continental de mayor superficie (`max(geom.geoms, key=lambda p: p.area)`) en `EPSG:32613`, obteniendo la superficie continental real (`787.82 km²`), el centroide correcto sobre el valle de Tecomán y la distancia logística real al puerto (`54.05 km`).
3. **Timeout de consulta Overpass API al incluir todos los polígonos `landuse=farmland` (`Defecto #10`, `12 min`):**
   * *Qué salió mal:* La primera consulta Overpass QL sobre el bounding box de Colima excedió `30 s` por el volumen masivo de polígonos genéricos `farmland`.
   * *Corrección:* Se refinó la consulta en `extractores/geoespacial_osm.py` a categorías agrologísticas específicas (`orchard`, `marketplace`, `greengrocer|wholesale|farm`, `warehouse`, `industrial`, `port`), capturando `1,164` nodos reales en `< 25 s` con `0` PII.

---

## 5. Qué aprendimos

### Ingeniería de Datos
Aprendimos que integrar una fuente geoespacial real implica mucho más que graficar puntos: exigir la proyección métrica correcta (`EPSG:32613` para áreas y distancias vs. `EPSG:4326` para almacenamiento GeoJSON), filtrar con `gpd.sjoin(..., predicate="within")` sin borrar silenciosamente los `90` puntos vecinos de Jalisco/Michoacán, corregir anomalías topológicas reales como las islas de Revillagigedo en el `MultiPolygon` de Tecomán, y reconocer críticamente el **sesgo de cobertura VGI** de OpenStreetMap (donde Ixtlahuacán tiene `496` huertas etiquetadas `orchard` frente a `167` en Tecomán por diferencias de mapeo voluntario). Asimismo, incrustar el linaje en cada registro de Capa Oro convierte la trazabilidad en una propiedad auditable del dato y no en una promesa documental.

### Análisis Estadístico
Comprobamos experimentalmente cómo el **Diseño de Experimentos Factorial ($2^3$, $2 \times 3$ y $2^{4-1}$)** cuantifica causalidad real: en nuestro pipeline, cambiar a **Parquet** (`efecto = -126.2 ms`, $|t| = 60.8$) y a **Pandera vectorizado** (`efecto = -123.8 ms`, $|t| = 59.6$) explica prácticamente toda la ganancia de velocidad, mientras que el paralelismo de lectura (`-8.3 ms`, $|t| = 4.0$) aporta una mejora secundaria significativa y las interacciones son no significativas ($p > 0.25$). Validar los supuestos de residuos (Shapiro-Wilk $p=0.4026$, Levene $p=0.7674$, Durbin-Watson $DW=2.0277$) y verificar que la media de las `5` corridas de confirmación (`70.93 ms`) cayó justo dentro del IC 95% predicho (`[56.93, 82.90] ms`) demostró el poder predictivo de un ANOVA bien aleatorizado y bloqueado, además de confirmar que el fraccionado $2^{4-1}$ Resolución IV ahorra `50%` de corridas preservando limpios los efectos principales.

### Calidad en los Sistemas de Información
Comprendimos en la práctica la diferencia precisa entre **ISO 9001** (gestión de procesos PHVA), **ISO/IEC 25010** (calidad del producto de software, heredera de ISO/IEC 9126) e **ISO/IEC 25012** (calidad intrínseca y dependiente del sistema sobre los datos). Conectar directamente el experimento factorial $2^3$ como evidencia de *Eficiencia de Desempeño* (`-78.95%` tiempo, `-91.13%` disco) y las `306 h` reales de GitHub Actions como evidencia de *Fiabilidad* (`A = 99.74%`, `MTBF = 101.73 h`) evitó calificaciones subjetivas y permitió ejecutar una auditoría honesta con hallazgos concretos (`AUD-01` a `AUD-05`).

---

## 6. Evidencias (enlaces a código, notebooks, datos y capturas)

* **Fuente Geoespacial y Unión Espacial:** [`extractores/geoespacial_osm.py`](../extractores/geoespacial_osm.py), [`pipeline/geoespacial_e2.py`](../pipeline/geoespacial_e2.py), [`data/oro/perfil_geoespacial_municipios_oro.geojson`](../data/oro/perfil_geoespacial_municipios_oro.geojson), [`data/cuarentena/cuarentena_geoespacial_e2.csv`](../data/cuarentena/cuarentena_geoespacial_e2.csv) y [`docs/E2/figuras/fig1_mapa_geoespacial_colima_e2.png`](E2/figuras/fig1_mapa_geoespacial_colima_e2.png).
* **Ética y Legalidad:** [`docs/etica-datos.md`](etica-datos.md), [`docs/fuentes/osm_geoespacial.md`](fuentes/osm_geoespacial.md) y evidencias `robots.txt` en `data/bronce/robots_txt/`.
* **Linaje de Datos:** [`pipeline/linaje_datos.py`](../pipeline/linaje_datos.py), [`data/oro/linaje_datos_e2.json`](../data/oro/linaje_datos_e2.json), [`data/oro/catalogo_linaje_oro_bronce.csv`](../data/oro/catalogo_linaje_oro_bronce.csv) y [`docs/E2/figuras/fig2_arquitectura_linaje_bronce_oro_e2.png`](E2/figuras/fig2_arquitectura_linaje_bronce_oro_e2.png).
* **Experimento Factorial $2^3$, $2 \times 3$ y $2^{4-1}$:** [`pipeline/experimento_doe_e2.py`](../pipeline/experimento_doe_e2.py), [`data/oro/resumen_experimento_doe_e2.json`](../data/oro/resumen_experimento_doe_e2.json), [`laboratorio/e2_geoespacial_experimento_linaje.ipynb`](../laboratorio/e2_geoespacial_experimento_linaje.ipynb) y [`docs/E2/figuras/fig3..fig5.png`](E2/figuras/fig3_doe_factorial_2_3_efectos_pareto.png).
* **ISO/IEC 25010–25012, Tablero y Pruebas:** [`docs/evaluacion-iso-25010-25012.md`](evaluacion-iso-25010-25012.md), [`tablero/app.py`](../tablero/app.py), [`tests/test_e2_geoespacial_linaje.py`](../tests/test_e2_geoespacial_linaje.py) y [`tests/test_e2_experimento_doe.py`](../tests/test_e2_experimento_doe.py).

---

## Uso de IA generativa (herramienta y para qué)

Durante la Etapa E2 se empleó el asistente de ingeniería **Antigravity (Google DeepMind)** como copiloto técnico para:
1. Estructurar la consulta Overpass QL optimizada, el flujo `GeoPandas sjoin` en `pipeline/geoespacial_e2.py` y el diseño modular de las 5 visualizaciones en `matplotlib`.
2. Redactar las plantillas iniciales de pruebas unitarias `pytest` y el generador HTML→PDF conforme al molde oficial del TecNM / IT Colima.
3. Todas las descargas desde OpenStreetMap (Nominatim/Overpass), las `84` corridas experimentales reales en Python, los análisis ANOVA/Shapiro-Wilk/Levene/Durbin-Watson/Tukey HSD, la auditoría de secretos y las verificaciones `pytest` se ejecutaron de manera real y determinista en la máquina local y en GitHub Actions, verificando cada cifra y decisión técnica.
