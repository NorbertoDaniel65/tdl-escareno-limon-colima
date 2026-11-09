# Propuesta Técnica y Analítica del Observatorio (Entrega E0)
## Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano en Colima (`CITRO-DATA LAB COLIMA`)

**Proyecto Integrador Colegiado · TRUSTED DATA LAB (Semestre Ago–Dic 2026)**  
**Institución:** Tecnológico Nacional de México · Instituto Tecnológico de Colima  
**Asignaturas Integradas:** Ingeniería de Datos (`CMD-2602`, Mtro. Armando Román Gallardo Heredia) · Análisis Estadístico para Ciencia de Datos (Mtro. Mónico Joel Sánchez Velasco)  
**Autor / Equipo:** Norberto Daniel Escareño Montaño (`No. Control: 23460323` · GitHub: `@NorbertoDaniel65`)  
**Fecha de Entrega E0:** 9 de noviembre de 2026 · **Etiqueta de versión:** `e0`

---

## 1. Ficha del Observatorio

| Elemento | Definición Específica del Observatorio |
|---|---|
| **Nombre del Observatorio** | **CITRO-DATA LAB COLIMA:** Observatorio Certificado de Inteligencia Agroclimática y Precios Mayoristas del Limón Mexicano (*Citrus aurantifolia*) |
| **Sector Económico (Vertical)** | Agroindustria Citrícola y Comercialización Hortofrutícola Mayorista (Cadena de Valor del Limón con Semilla #5). |
| **Región de Estudio** | **Origen Productivo (4 Municipios de Colima):** Tecomán (`06009`), Armería (`06001`), Manzanillo (`06007`) y Colima (`06002`).<br>**Destino Comercial (4 Mercados Nacionales):** Colima (Empacadoras Regionales), Guadalajara (Mercado de Abastos), CDMX (Central de Abasto Iztapalapa) y Monterrey (Mercado Estrella). |
| **Pregunta Central Detonadora** | *¿En qué semanas del año y hacia qué central de abasto nacional conviene a los productores y empacadoras de Colima colocar su producción de limón mexicano #5, anticipando con 1 a 3 meses de ventaja el impacto del estrés térmico e hídrico de Tecomán y Armería sobre la escalada de precios mayoristas?* |
| **Cliente Potencial Identificado** | **1. Empacadoras y comercializadoras citrícolas del Valle de Tecomán y Armería** (ej. asociaciones de productores y consejos estatales de limón).<br>**2. Compradores mayoristas de cadenas de autoservicio y centrales de abasto en Guadalajara y CDMX.** |
| **Motivo Económico para Pagar** | Una variación de **$\$3.00$ a $\$6.00\text{ MXN/kg}$** en un embarque estándar de $20\text{ toneladas}$ representa entre **$\$60,000$ y $\$120,000\text{ MXN}$ de diferencia por camión**. Hoy los productores venden a ciegas al precio que fija el intermediario ("coyote") en báscula local sin conocer el diferencial real (*spread*) frente a Guadalajara o CDMX ni cómo el déficit hídrico acumulado restringirá la oferta en las siguientes 6 a 8 semanas. |

---

## 2. Validación de Campo: Entrevista con Actor Real del Sector (22 minutos)

Con el objetivo de validar que la pregunta central responde a un dolor económico real y no a una suposición académica, el **martes 3 de noviembre de 2026** se realizó una entrevista semiestructurada de **22 minutos** con un actor activo de la cadena citrícola en el corredor **Tecomán–Colima** (productor y encargado de comercialización de huerta y empaque de limón mexicano con semilla; se preserva el anonimato de datos personales conforme a las reglas de privacidad LFPDPPP del proyecto).

### 2.1 Las 5 Preguntas Realizadas y Respuestas Obtenidas

1. **Pregunta 1 (Decisión crítica de negocio):** *¿Cuál es la decisión más costosa que toman cada semana al cortar y vender la arpilla o caja de limón mexicano?*
   > **Respuesta:** *"Decidir qué día cortar fuerte y a quién venderle: si entregar aquí en las empacadoras de Tecomán al precio del día o mandar viaje directo a Guadalajara. Muchas veces vendemos barato el martes porque nos dicen que la plaza está saturada, y para el viernes en Guadalajara el kilo ya subió cinco o seis pesos."*

2. **Pregunta 2 (Fuentes actuales e incertidumbre):** *¿Cómo se enteran hoy de los precios en Guadalajara, CDMX o Monterrey y qué tan confiable es esa información?*
   > **Respuesta:** *"Por llamadas de WhatsApp con comisionistas o rumores entre productores en la mañana. Casi nadie revisa las tablas del gobierno (SNIIM) porque su página es vieja y tediosa de consultar día por día, así que nos quedamos con el dato que nos dice el comprador, que obviamente siempre tira el precio hacia abajo."*

3. **Pregunta 3 (Relación entre clima en la huerta y precio futuro):** *¿Qué señales del clima en Tecomán o Armería les avisan que va a escasear el limón o que va a cambiar el calibre (#5 vs. #4)?*
   > **Respuesta:** *"El calor extremo de más de 35 grados combinado con semanas secas sin lluvia y mucho sol (evaporación alta) estresa el árbol: tira flor o el limón se queda chico y amarillea antes. Cuando pega una racha así o vientos fuertes en floración, sabemos que mes y medio o dos meses después va a faltar fruta de calidad y el precio se dispara, pero nadie lleva el conteo exacto con números."*

4. **Pregunta 4 (Diferencias entre zonas de Colima):** *¿Se comporta igual la producción y el clima en Tecomán, Armería, Manzanillo y la zona norte hacia Colima capital?*
   > **Respuesta:** *"No, son microclimas distintos. Tecomán y Armería son mucho más cálidos y secos en estiaje; Manzanillo tiene más humedad costera y rachas de viento cuando entran sistemas del Pacífico; y hacia el valle de Colima la temperatura mínima baja más en invierno, lo que retrasa los cortes."*

5. **Pregunta 5 (Valor de un observatorio automatizado):** *Si tuviera un tablero en línea que cada mañana le mostrara el precio oficial en las 4 plazas, el margen libre de flete y un pronóstico estadístico de precios a 4 semanas con alertas de estrés climático, ¿le serviría y pagaría una suscripción?*
   > **Respuesta:** *"Totalmente. Si una alerta nos ayuda a negociar aunque sea un peso más por kilo en una sola corrida semanal de 10 toneladas, son diez mil pesos recuperados en una semana. Una suscripción mensual accesible para el empaque o la cooperativa se paga sola con un solo embarque."*

### 2.2 Aprendizajes Clave que Moldearon el Diseño del Observatorio
- **Aprendizaje 1 (Métrica de margen regional):** No basta con reportar el precio aislado; es indispensable calcular la variable derivada `diferencial_vs_origen_mxn_kg` (*spread* comercial entre Guadalajara/CDMX/Monterrey y el precio base en Colima).
- **Aprendizaje 2 (Variables bioclimáticas fisiológicas):** En lugar de usar solo temperatura media cruda, el extractor de Open-Meteo calcula **Grados-Día de Desarrollo Citrícola (`grados_dia_citricos_gdd`, base $13^\circ\text{C}$)**, **Balance Hídrico FAO (`precipitacion_mm - evapotranspiracion_et0_mm`)** y **Días de Estrés Térmico ($\ge 35^\circ\text{C}$)**, que capturan directamente el mecanismo fisiológico descrito en la entrevista.
- **Aprendizaje 3 (Necesidad de serie larga con rezagos):** Dado que el daño climático en floración tarda entre $4$ y $8$ semanas en reflejarse en la oferta de fruta cortada, la serie histórica de 60 meses permite evaluar correlaciones cruzadas con rezagos ($k = 1, 2, 3$ meses) en la entrega `E1`.

---

## 3. Las Tres Preguntas Analíticas del Proyecto (E1, E2 y E3)

Cada etapa posterior del proyecto responde una pregunta analítica rigurosa, verificable y vinculada a las técnicas del programa de **Análisis Estadístico para Ciencia de Datos** e **Ingeniería de Datos**:

### 3.1 Pregunta E1 · Series de Tiempo y Pronóstico (Unidad 3)
- **Pregunta analítica:** *¿Cuál es la trayectoria esperada del precio mayorista frecuente del limón mexicano (`precio_frecuente_mxn_kg`, en $\text{MXN/kg}$) para los próximos 3 periodos mensuales (con intervalos de predicción al $95\%$), cómo se descompone su fuerte estacionalidad invernal-primaveral (picos de febrero–abril vs. valles de julio–septiembre) y cuál es la correlación cruzada con el déficit hídrico acumulado ($P - ET_0$) rezagado en Tecomán?*
- **Variable respuesta ($Y_t$):** `precio_frecuente_mxn_kg` mensual (serie de $T = 60$ meses continuos: `2021-01` a `2025-12`).
- **Variable exógena para correlación cruzada ($X_{t-k}$):** `deficit_hidrico_acum_mm` y `dias_estres_termico_35c` en Tecomán (`06009`).
- **Metodología estadística en E1:**
  1. Descomposición clásica y STL (aditiva vs. multiplicativa, justificando según la amplitud estacional proporcional al nivel).
  2. Prueba de raíz unitaria **Dickey-Fuller Aumentada (ADF)** y análisis de correlogramas **ACF y PACF**.
  3. Entrenamiento y validación *out-of-sample* (separando los últimos 12 meses como conjunto de prueba) de cuatro modelos: **Suavizamiento Exponencial Simple (SES)**, **Método de Holt**, **Holt-Winters Estacional** y **ARIMA/SARIMA** seleccionado por AIC.
  4. Selección del modelo ganador mediante **MAE, RMSE y MAPE** y verificación de ruido blanco en residuos con la prueba de **Ljung-Box**.

### 3.2 Pregunta E2 · Diseño de Experimentos Factorial $2^3$ y ANOVA de Dos Vías (Unidad 4)
- **Pregunta analítica (Ruta Ingeniería sobre el Pipeline del Observatorio):** *¿Qué combinación de factores de ingeniería del pipeline de captura y transformación (Factor A: Estrategia de concurrencia HTTP secuencial vs. pool de hilos con control de dominio; Factor B: Motor de validación y parseo `pandas` nativo vs. `Pandera` vectorizado; Factor C: Formato de persistencia en almacenamiento `CSV UTF-8` vs. `Apache Parquet Snappy`) minimiza significativamente el tiempo total de ejecución ($\text{ms}$) y el consumo de disco/memoria sin incrementar la tasa de error?*
- **Diseño experimental:**
  1. **Diseño factorial completo $2^3$** con al menos $r = 3$ réplicas aleatorizadas por tratamiento ($8 \times 3 = 24$ corridas ejecutadas sobre copias locales controladas en Capa Bronce, sin saturar servidores externos).
  2. **ANOVA de dos vías con interacción** extendiendo el Factor C a 3 niveles (`CSV`, `Parquet Snappy`, `Parquet ZSTD`) cruzado con el Factor B.
  3. **Comparativa teórica y práctica $2^4$ completo vs. $2^{4-1}$ fraccionado** (Resolución IV, generador $D = ABC$), identificando estructura de alias y ahorro del $50\%$ de corridas, más corrida de confirmación en el punto óptimo.

### 3.3 Pregunta E3 · Análisis Multivariado: PCA y MANOVA (Unidad 5)
- **Pregunta analítica:** *¿Existen diferencias multivariadas estadísticamente significativas ($\alpha = 0.05$) en el vector conjunto de condiciones bioclimáticas y desempeño comercial entre los **4 municipios citrícolas de Colima** (`Tecomán`, `Armería`, `Manzanillo` y `Colima`, $g = 4$ grupos) y entre las **4 centrales mayoristas nacionales** (`Colima`, `Guadalajara`, `CDMX`, `Monterrey`), y qué índices latentes (Componentes Principales) sintetizan el riesgo agroclimático y la rentabilidad por plaza?*
- **Grupos a comparar ($g = 4 \ge 3$ requeridos):**
  - Agrupación Geográfica A (Agroclima): `Tecoman` vs. `Armeria` vs. `Manzanillo` vs. `Colima` ($N = 240$ observaciones mensuales; $60$ por municipio).
  - Agrupación Comercial B (Mercados): `MKT-COL` vs. `MKT-GDL` vs. `MKT-CDMX` vs. `MKT-MTY` ($N = 240$ observaciones mensuales; $60$ por mercado).
- **Vector de variables numéricas ($\ge 7$ variables continuas simultáneas):**
  `temp_max_promedio_c`, `temp_min_promedio_c`, `precipitacion_acum_mm`, `evapotranspiracion_acum_mm`, `deficit_hidrico_acum_mm`, `gdd_acumulado_mes`, `viento_max_extremo_kmh` y `radiacion_media_mj_m2` (más `precio_frecuente_mxn_kg` y `diferencial_vs_origen_mxn_kg` en la matriz integrada).
- **Metodología estadística en E3:**
  1. Matriz de covarianzas y correlaciones, evaluación de normalidad multivariada (**Prueba de Henze-Zirkler / Mardia** y gráfico Q-Q de **Distancias de Mahalanobis**).
  2. **Análisis de Componentes Principales (PCA)** sobre variables estandarizadas: gráfico de sedimentación (*scree plot*), varianza explicada acumulada, interpretación de cargas factoriales (ej. *PC1: Índice de Aridez y Demanda Evaporativa*, *PC2: Régimen Térmico Costero vs. Valle*) y *Biplot* proyectado en el tablero.
  3. **MANOVA de una vía** evaluando simultáneamente el vector de respuestas con los estadísticos **Lambda de Wilks ($\Lambda$)** y **Traza de Pillai**, contrastando por qué controla la tasa de error Tipo I global frente a múltiples ANOVAs univariados independientes.

---

## 4. Plan de Recopilación de Datos y Análisis Ético-Legal (`robots.txt` y Términos de Uso)

El observatorio opera desde `E0` con **dos fuentes reales en producción** dentro de la Capa Bronce y prepara una tercera fuente geoespacial especializada para `E2`:

| Atributo | Fuente 1: Open-Meteo Archive & Forecast API | Fuente 2: SNIIM (Secretaría de Economía) | Fuente 3 (Planeada para E2): INEGI DENUE / Overpass OSM |
|---|---|---|---|
| **Rol en el Observatorio** | Captura meteorológica histórica (60 meses) y diaria automática (`GitHub Actions`) para los 4 municipios de Colima. | Precios mayoristas históricos (60 meses) y monitoreo ético de Limón con semilla #5 en 4 mercados nacionales. | Georreferenciación de empacadoras, centros de acopio e infraestructura carretera en Colima. |
| **Endpoints / URLs** | `https://archive-api.open-meteo.com/v1/archive`<br>`https://api.open-meteo.com/v1/forecast` | `http://www.economia-sniim.gob.mx/nuevo/Consultas/.../ConsultaFrutasYHortalizas.aspx` | `https://overpass-api.de/api/interpreter` / API DENUE INEGI |
| **Formato Origen → Bronce** | `JSON` columnar UTF-8 → `CSV` + `.meta.json` (SHA-256) | `HTML` / Tablas Estadísticas → `CSV` + `.meta.json` (SHA-256) | `GeoJSON (RFC 7946)` WGS84 (`EPSG:4326`) |
| **Frecuencia de Actualización** | **Diaria automática** (`cron: "0 12 * * *"` en GitHub Actions) | **Diaria / Semanal** en corrida programada de GitHub Actions | Batch por entrega en `E2` con caché espacial |
| **Método de Acceso** | `ExtractorEtico.get(..., es_api_rest=True)` con `requests.Session` | `ExtractorEtico.get(...)` + parseo con `BeautifulSoup4` | Consulta REST / Overpass QL con `GeoPandas` |
| **Análisis de `robots.txt`** | Subdominio API sirve `Disallow: /` para evitar indexación en buscadores web (Googlebot); evidencia archivada en `data/bronce/robots_txt/`. | `http://www.economia-sniim.gob.mx/robots.txt` devuelve `HTTP 404` (sin restricciones de robots); evidencia archivada en `data/bronce/robots_txt/`. | Respeta políticas de cuota y cabecera identificadora obligatoria. |
| **Términos de Uso y Licencia** | **CC BY 4.0** (Open-Meteo Non-Commercial / Academic Terms of Use, hasta 10,000 req/día). | **Libre Uso de Datos Abiertos del Gobierno de México** (Secretaría de Economía / SNIIM). | **ODbL 1.0** (OpenStreetMap) / Libre Uso INEGI. |
| **Control Ético y Privacidad** | Pausa $\ge 1.5\text{ s}$ entre peticiones, `User-Agent` con correo institucional (`23460323@colima.tecnm.mx`) y **0 datos personales**. | Pausa $\ge 1.5\text{ s}$, 1 sola petición de verificación por corrida diaria y **0 datos personales**. | Exclusión total de nombres de personas físicas, teléfonos o correos en Capa Bronce. |

---

## 5. Evidencia de Serie Histórica en Capa Bronce ($\ge 36$ Periodos Cumplidos)

En cumplimiento estricto de la rúbrica de `E0` (que exige al menos $36$ periodos históricos en la Capa Bronce), el repositorio cuenta ya con **60 periodos mensuales continuos (`2021-01` a `2025-12`)** verificados mediante hash **SHA-256**:

1. **Serie Agroclimática Mensual (`data/bronce/open_meteo/agroclima_colima_mensual_60m.csv`):**
   - **Periodos:** **60 meses continuos** ($240$ registros = $60\text{ meses} \times 4\text{ municipios}$).
   - **Respaldo diario crudo (`agroclima_colima_diario_historico.csv`):** **1,826 días continuos** ($7,304$ registros diarios).
   - **Hash SHA-256 verificado:** `6aad451dfcd2d2f033352a9a6182fac3800a818bc3b92fb2baa73cc7bd2ae240`
2. **Serie de Precios Mayoristas SNIIM (`data/bronce/sniim_limon/precios_limon_sniim_historico_60m.csv`):**
   - **Periodos:** **60 meses continuos** ($240$ registros = $60\text{ meses} \times 4\text{ mercados mayoristas}$).
   - **Rango observado en Colima (`MKT-COL`):** Mínimo frecuente de $\$12.01\text{ MXN/kg}$ en temporada de lluvias (agosto 2021) a pico máximo frecuente de $\$54.88\text{ MXN/kg}$ en escasez crítica (marzo 2022).
   - **Hash SHA-256 verificado:** `7dde14cf7f818a89294b73c91a15647315794c91ef7021c29fb276edd598adc2`
3. **Captura Diaria Activa (`data/bronce/open_meteo/captura_diaria_2026-11-09.csv` y `monitoreo_sniim_2026-11-09.csv`):**
   - Ejecutándose automáticamente en `.github/workflows/captura-bronce.yml` y registrando cada corrida en `calidad/bitacora_capturas.jsonl`.

---

## 6. Arranque del Sistema de Calidad (PSP) y Sostenibilidad del Observatorio

- **Registros PSP Individuales Abiertos:**
  - [`calidad/tiempo-norberto.csv`](../../calidad/tiempo-norberto.csv): 6 sesiones de trabajo cronometradas por fase (`planeacion`, `diseno`, `codigo`, `pruebas`, `revision`).
  - [`calidad/defectos-norberto.csv`](../../calidad/defectos-norberto.csv): 4 defectos reales documentados durante la construcción de `E0` con su fase de inyección, fase de remoción y minutos de corrección.
- **Tres Objetivos de Calidad Medibles ([`calidad/objetivos.md`](../../calidad/objetivos.md)):**
  - **O1 (Disponibilidad):** $A = \text{MTBF}/(\text{MTBF}+\text{MTTR}) \ge 95\%$ en las capturas programadas.
  - **O2 (Completitud e Integridad):** $\ge 98\%$ de completitud en series de bronce y $100\%$ de validación criptográfica SHA-256.
  - **O3 (Privacidad y Cobertura):** $0$ datos personales en bronce, $0$ secretos expuestos y $\ge 80\%$ de cobertura en pruebas automáticas `pytest`.
- **Modelo de Sostenibilidad Preliminar:** Esquema híbrido de **Reporte de Inteligencia por Suscripción** para empacadoras y asociaciones citrícolas de Tecomán/Armería (con alertas semanales de arbitraje de precios entre plazas y pronóstico a 4 semanas) + **Tablero Público Abierto** para consulta comunitaria de productores locales, operando con costo de infraestructura de **$\$0\text{ USD/mes}$** mediante fuentes abiertas, GitHub Actions y Streamlit Community Cloud.
