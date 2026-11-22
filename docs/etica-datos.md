# Declaración de Ética, Legalidad, Privacidad y Mitigación de Sesgos de Datos (`docs/etica-datos.md`)

* **Observatorio:** **CITRO-DATA LAB COLIMA** — Observatorio Agroclimático, Geoespacial y de Precios Mayoristas del Limón Mexicano (*Citrus aurantifolia*)
* **Estudiante / Responsable:** Norberto Daniel Escareño Montaño (`No. Control: 23460323` · Correo institucional: `23460323@colima.tecnm.mx` · GitHub: `@NorbertoDaniel65`)
* **Institución:** Tecnológico Nacional de México — Instituto Tecnológico de Colima (Ingeniería en Sistemas Computacionales)
* **Etapa:** `E2` — *Trusted Data Lab: Fuente Especializada, Ética y Linaje de Datos* (`Tag: e2`)
* **Fecha de emisión y revisión:** 22 de noviembre de 2026

---

## 1. Marco Legal, Ético y Principios Rectores del Observatorio

El observatorio **CITRO-DATA LAB COLIMA** opera bajo cuatro pilares legales y éticos no negociables, implementados directamente como controles deterministas en código (`extractores/base.py`, `extractores/geoespacial_osm.py`, `pipeline/puerta_calidad.py` y `tests/`):

1. **Derecho de Acceso a la Información y Datos Abiertos (México):** Fundamentado en el **Artículo 6° Constitucional** y la **Ley General de Transparencia y Acceso a la Información Pública (LGTAIP)** respecto a información estadística, económica y geoestadística pública (SNIIM-SE e INEGI).
2. **Protección de Datos Personales — Cero PII (LFPDPPP):** Conforme a la **Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)**, el observatorio **no recolecta, almacena, procesa ni publica dato personal alguno** (nombres de personas físicas, teléfonos, correos personales, RFC, CURP, domicilios particulares ni perfiles de redes sociales). Cualquier atributo no autorizado se elimina mediante **lista blanca estricta** antes de persistir en Capa Bronce.
3. **Extracción Ética y Respeto a Infraestructura Ajena (`ExtractorEtico`):** Todas las consultas automatizadas se identifican mediante un encabezado `User-Agent` transparente con correo institucional (`TDL-Observatorio-Limon-Colima/1.0 (proyecto academico TecNM Colima; contacto: 23460323@colima.tecnm.mx)`), imponen una **pausa mínima obligatoria $\ge 1.5\text{ s}$** entre solicitudes al mismo dominio, aplican **espera exponencial** (`1.5 * 2^i s`) ante códigos `HTTP 429/5xx` o *timeouts*, y archivan la evidencia de `robots.txt` en `data/bronce/robots_txt/`.
4. **Propiedad Intelectual, Licenciamiento Abierto y Trazabilidad:** Cada archivo en Capa Bronce cuenta con su ficha `.meta.json` (hash `SHA-256`, URL origen, licencia exacta y marca temporal UTC), y el **100% de los 310 registros maestros de Capa Oro** preserva su linaje explícito hasta su fuente original (`data/oro/linaje_datos_e2.json` y `data/oro/catalogo_linaje_oro_bronce.csv`).

---

## 2. Matriz Ético-Legal Detallada por Fuente de Datos

### 2.1 Fuente 1 — Open-Meteo Archive & Forecast API (Reanálisis Copernicus ERA5-Land)

| Dimensión Ético-Legal | Análisis Técnico y Evidencia Verificable |
| :--- | :--- |
| **Endpoints y Cobertura** | `https://archive-api.open-meteo.com/v1/archive` (histórico 60 meses, `7,304` filas diarias) y `https://api.open-meteo.com/v1/forecast` (captura diaria automatizada vía GitHub Actions en 4 municipios de Colima). |
| **Base Legal y Términos de Uso** | Uso académico no comercial autorizado expresamente por los *Open-Meteo Terms of Use* (cuota gratuita: hasta `10,000` llamadas/día; nuestro observatorio realiza únicamente **`4` llamadas/día**, es decir, `< 0.04%` de la cuota permitida). |
| **Análisis de `robots.txt`** | Evidencia archivada en `data/bronce/robots_txt/archive-api.open-meteo.com_robots.txt` y `api.open-meteo.com_robots.txt`. Ambos subdominios API declaran `User-agent: * / Disallow: /` exclusivamente para impedir que buscadores web (Googlebot/Bingbot) indexen respuestas JSON dinámicas; el consumo programático está habilitado vía API REST pública (`es_api_rest=True` en `extractores/base.py`, manteniendo pausa $\ge 1.5\text{ s}$ y backoff). |
| **Licencia y Atribución** | **Creative Commons Attribution 4.0 International (CC BY 4.0)** — Open-Meteo.com / Copernicus Climate Change Service (C3S) ERA5-Land. Se otorga atribución visible en `README.md`, `.meta.json`, diccionario de datos y tablero. |
| **Riesgos de Privacidad (LFPDPPP)** | **Nulo (0% riesgo PII).** Los registros contienen exclusivamente variables geofísicas agregadas por coordenada municipal (temperatura, precipitación, $ET_0$, viento, radiación solar). |
| **Sesgos Conocidos** | 1. **Sesgo de resolución espacial de rejilla (~9–11 km en ERA5-Land):** Los valores representan celdas de reanálisis satelital/modelo y pueden suavizar eventos hiperlocales de tormenta o microclimas de barranca frente a pluviómetros puntuales en huerta.<br>2. **Sesgo de representatividad puntual:** Se consulta el centroide agroclimático de cada municipio (`Tecomán`, `Armería`, `Manzanillo`, `Colima`), pudiendo diferir ligeramente en zonas serranas altas. |
| **Estrategia de Mitigación** | Se construye un índice agroclimático estatal ponderado por superficie citrícola SIAP (`Tecomán 55%, Armería 22%, Manzanillo 15%, Colima 8%`), se valida coherencia física mediante reglas `RN-01` y `RN-03` en la Puerta de Calidad (`pipeline/puerta_calidad.py`), y se comunica explícitamente que los indicadores son de escala municipal y no sustituyen estaciones agrometeorológicas de parcela. |

---

### 2.2 Fuente 2 — SNIIM (Sistema Nacional de Información e Integración de Mercados — Secretaría de Economía)

| Dimensión Ético-Legal | Análisis Técnico y Evidencia Verificable |
| :--- | :--- |
| **Endpoints y Cobertura** | `http://www.economia-sniim.gob.mx/nuevo/Consultas/MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx` (`60` meses × `4` mercados mayoristas: Colima, Guadalajara, CDMX y Monterrey = `240` registros + monitoreo ético diario). |
| **Base Legal y Términos de Uso** | Portal público federal de la Secretaría de Economía de México. Información estadística pública de precios mayoristas agrícolas sujeta al **Decreto de Datos Abiertos** y la **LGTAIP**. El monitoreo automatizado realiza solo **1 petición HTTP GET diaria** con pausa $\ge 1.5\text{ s}$ sin provocar carga sobre el servidor gubernamental. |
| **Análisis de `robots.txt`** | Evidencia archivada en `data/bronce/robots_txt/www.economia-sniim.gob.mx_robots.txt` y su `.meta.json` (`HTTP 404` — sin restricciones de rastreo declaradas para consultas públicas). |
| **Licencia y Atribución** | **Términos de Libre Uso de Datos Abiertos del Gobierno de México** (`datos.gob.mx` / Secretaría de Economía — SNIIM). Se cita la fuente oficial en todos los entregables y visualizaciones. |
| **Riesgos de Privacidad (LFPDPPP)** | **Nulo (0% riesgo PII).** Las cotizaciones representan precios agregados por central de abasto y producto (`Limón con semilla #5`), sin identificar vendedores, bodegueros ni compradores individuales. |
| **Sesgos Conocidos** | 1. **Sesgo de eslabón de la cadena:** SNIIM reporta precios mayoristas en centrales de abasto (bodega destino), los cuales incluyen flete, merma e intermediación, y suelen ser superiores al precio recibido por el productor a pie de huerta/báscula en Tecomán.<br>2. **Sesgo de cobertura de calidad/calibre:** En meses de escasez crítica (ej. feb-mar 2022) puede disminuir el número de cotizaciones diarias de calibre #5 (patrón `MNAR` diagnosticado en E1). |
| **Estrategia de Mitigación** | Se modela explícitamente el diferencial comercial (`margen_intermediacion_mxn_kg`), se preservan y etiquetan los choques reales de escasez (`es_choque_legitimo_dominio=True`) en lugar de amputarlos, y se acompañan todos los pronósticos con **Intervalos de Predicción al 95%** explicados en lenguaje llano al productor. |

---

### 2.3 Fuente 3 (Especializada E2) — OpenStreetMap (Nominatim & Overpass API) + Catálogo Geoestadístico Municipal INEGI

| Dimensión Ético-Legal | Análisis Técnico y Evidencia Verificable |
| :--- | :--- |
| **Endpoints y Cobertura** | • **Límites Municipales:** `https://nominatim.openstreetmap.org/search` (`10` polígonos administrativos WGS84 `EPSG:4326` de Colima con claves `CVEGEO` INEGI `06001`–`06010`).<br>• **Infraestructura Agrologística:** `https://overpass-api.de/api/interpreter` (`1,164` elementos capturados en el bounding box de Colima; `1,074` validados dentro de Colima vía `gpd.sjoin(..., predicate="within")` y `90` fuera del límite estatal enviados a `data/cuarentena/cuarentena_geoespacial_e2.csv`). |
| **Base Legal y Términos de Uso** | Cumplimiento estricto de la *Nominatim Usage Policy* (máximo 1 req/s — nuestro extractor impone `pausa >= 1.5 s`, sin búsquedas masivas repetidas y con caché local persistente en Capa Bronce) y la *Overpass API Usage Policy* (1 sola consulta agregada batch por entrega, nunca en bucles ni sobre cada carga del tablero). |
| **Análisis de `robots.txt`** | Evidencia archivada en `data/bronce/robots_txt/nominatim.openstreetmap.org_robots.txt` (`HTTP 200`, prohíbe rastreo indiscriminado de `/search` a bots genéricos) y `data/bronce/robots_txt/overpass-api.de_robots.txt` (`HTTP 200`, declara `Disallow: /api/` contra indexadores web). Ambos servicios operan como APIs públicas abiertas con política explícita de uso moderado con `User-Agent` identificable (`es_api_rest=True`). |
| **Licencia y Atribución** | **Open Database License (ODbL 1.0)** — *© OpenStreetMap Contributors* + **Términos de Libre Uso de Información Estadística y Geográfica INEGI** para el catálogo de claves municipales (`CVEGEO`). Se mantiene la atribución obligatoria `© OpenStreetMap contributors (ODbL 1.0)` en el mapa, tablero y reportes. |
| **Riesgos de Privacidad (LFPDPPP)** | **Riesgo potencial moderado en fuente cruda → Mitigado a 0% en Capa Bronce.** Algunos nodos comerciales en OpenStreetMap pueden incluir etiquetas voluntarias `phone`, `contact:phone`, `email`, `operator`, `whatsapp` o domicilios particulares.<br>**Control implementado en `extractores/geoespacial_osm.py`:** (1) Lista blanca estricta que únicamente lee `id`, `type`, `lat/lon`, etiquetas técnicas de uso de suelo (`landuse`, `amenity`, `shop`, `building`, `industrial`) y `name`; (2) Filtro de expresiones regulares (`_PATRON_PII_TEXTO`) que redacta automáticamente cualquier teléfono o correo embebido en nombres; (3) Prueba automatizada `test_cero_datos_personales_geoespacial` en `pytest` que verifica `0` columnas prohibidas y `0` patrones PII. |
| **Sesgos Conocidos** | 1. **Sesgo de Información Geográfica Voluntaria (VGI / cobertura desigual):** En OpenStreetMap, la densidad de mapeo depende de la actividad de colaboradores voluntarios. Esto se evidenció empíricamente en nuestra unión espacial: el municipio vecino de **Ixtlahuacán** registra `496` parcelas etiquetadas como `landuse=orchard` debido a un proyecto puntual de digitalización de huertas, mientras que **Tecomán** (que concentra el `55%` de la producción real según SIAP) muestra `167` huertas `orchard` porque gran parte de su superficie limonera está etiquetada genéricamente como `farmland` o sin polígono individual.<br>2. **Sesgo de geometría insular en polígonos administrativos (Defecto #9):** El municipio de Tecomán incluye administrativamente el archipiélago oceánico de Revillagigedo (`MultiPolygon`), lo que desplaza el centroide total hacia el Pacífico si no se selecciona el polígono continental.<br>3. **Sesgo urbano en infraestructura comercial:** Mercados y bodegas industriales están mejor mapeados en cabeceras urbanas (Manzanillo `74`, Colima `65`) que en empacadoras rurales de brechas ejidales. |
| **Estrategia de Mitigación** | 1. **Triangulación con fuentes oficiales:** Nunca se usa el conteo de huertas OSM como sustituto de superficie productiva oficial; se combina con los ponderadores oficiales **SIAP-SADER** (`55% Tecomán, 22% Armería, 15% Manzanillo, 8% Colima`) y se documenta explícitamente la diferencia entre *cobertura cartográfica VGI* y *superficie agrícola oficial*.<br>2. **Corrección geométrica continental (`pipeline/geoespacial_e2.py`):** Los centroides y distancias logísticas (`EPSG:32613`) se calculan sobre el polígono continental de mayor superficie de cada municipio.<br>3. **Filtro espacial sin borrado silencioso:** Los `90` nodos del bounding box que pertenecen a Jalisco/Michoacán se segregan a `data/cuarentena/cuarentena_geoespacial_e2.csv`. |

---

## 3. Auditoría de Cumplimiento de Uso Secundario y Experimentación Responsable

1. **Uso Secundario Permitido y Límites de Responsabilidad:**
   * Los conjuntos de Capa Oro y los pronósticos del observatorio tienen fines **informativos, analíticos y académicos** para planeación comercial y logística en la cadena citrícola de Colima.
   * **Usos explícitamente no recomendados:** No deben utilizarse para fijación anticompetitiva de precios, toma de decisiones crediticias automatizadas sin verificación agronómica en campo, ni inferencia de identidad o patrimonio de agricultores individuales.
2. **Ética en la Experimentación Factorial $2^3$ y $2^4$ (Unidad 4):**
   * Siguiendo la regla estricta del proyecto (*«nunca saturando un sitio ajeno»*), las **84 corridas experimentales reales** (`24` del diseño $2^3$ + `18` del diseño $2 \times 3$ + `32` del $2^4$/$2^{4-1}$ + `10` de confirmación) se ejecutaron **100% en entorno local aislado** sobre copias de Capa Bronce en disco temporal (`tempfile.TemporaryDirectory`), generando **0 peticiones de red externas** durante el benchmarking.
3. **Verificación Continua en CI (`pytest`):**
   * Toda modificación al repositorio dispara `.github/workflows/ci-calidad.yml`, validando automáticamente: (a) hashes `SHA-256` de Capa Bronce, (b) ausencia de datos personales (`0` PII), (c) ausencia de credenciales o tokens en el historial (`0` secretos en `144` archivos auditados), y (d) integridad del 100% del linaje de Capa Oro.
