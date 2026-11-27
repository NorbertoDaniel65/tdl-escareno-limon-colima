# Calidad en los Sistemas de Información (Entrega E3)
## Cierre de Auditoría, Modelos de Proceso (MoProSoft y CMMI), Retrospectiva PSP (`E0→E3`), Tendencias Actuales y Certificación del Sello TDL

* **Observatorio:** **CITRO-DATA LAB COLIMA** — Observatorio Certificado de Inteligencia Agroclimática, Geoespacial y Comercial del Limón Mexicano
* **Autor / Quality Lead:** Norberto Daniel Escareño Montaño (`No. Control: 23460323` · `@NorbertoDaniel65`)
* **Asignatura:** Calidad en los Sistemas de Información (`IFC-1008`, Unidad 4, Temas 4.3 a 4.7)
* **Artefactos Verificables:** `data/oro/cierre_auditoria_e3.csv`, `data/oro/autoevaluacion_moprosoft_cmmi_e3.csv`, `data/oro/comparativa_modelos_proceso_e3.csv`, `data/oro/retrospectiva_psp_e0_e3.csv`, `data/oro/psp_defectos_por_fase_e3.csv`, `data/oro/sello_tdl_evaluacion_e3.csv`, `data/oro/resumen_calidad_sello_e3.json`
* **Fecha de Corte:** 27 de noviembre de 2026 · **Etiqueta:** `e3`

---

## 1. Cierre Formal de la Auditoría (`5 / 5` Hallazgos Cerrados · `0` Críticos Abiertos)

Todos los hallazgos derivados de la auditoría normativa **ISO/IEC 25010** e **ISO/IEC 25012** sobre el observatorio han sido atendidos con acciones correctivas en código, pruebas automatizadas de no regresión en `pytest` y evidencia verificable en el repositorio. **Ningún hallazgo crítico, mayor o menor permanece abierto (`0` abiertos):**

| ID | Severidad | Norma / Característica | Hallazgo Recibido | Acción Correctiva Implementada | Evidencia Verificable | Estado Final E3 |
| :---: | :---: | :--- | :--- | :--- | :--- | :---: |
| **AUD-01** | **MAYOR** | ISO/IEC 25010 · Fiabilidad | En los runs de GitHub Actions `#44168162030` (`17 nov`) y `#44384386430` (`18 nov`), `api.open-meteo.com` devolvió HTTP `5xx/429` y `ExtractorEtico.get()` registraba `ultimo_error=None` sin guardar el código HTTP (**Defecto #8**). | Se actualizó `extractores/base.py` para propagar `RuntimeError(f"HTTP {r.status_code}")`, aplicar *backoff* exponencial (`pausa * 2**i`) y habilitar `POST` ético. Verificado con **100% de éxito (`9/9` corridas diarias)** del `19` al `27 de noviembre`. | [`extractores/base.py`](../extractores/base.py), [`calidad/bitacora_capturas.jsonl`](../calidad/bitacora_capturas.jsonl), [`tests/test_extractor_etico.py`](../tests/test_extractor_etico.py) | **CERRADO Y VERIFICADO** |
| **AUD-02** | **MAYOR** | ISO/IEC 25012 · Trazabilidad | En `e1`, las tablas de Capa Oro dependían solo de `.meta.json` externos sin trazabilidad registro por registro. | Se implementó `pipeline/linaje_datos.py` inyectando 6 columnas de linaje en los **`310/310` registros de Capa Oro (`100.0%`)** y generando `catalogo_linaje_oro_bronce.csv`. | [`pipeline/linaje_datos.py`](../pipeline/linaje_datos.py), [`data/oro/catalogo_linaje_oro_bronce.csv`](../data/oro/catalogo_linaje_oro_bronce.csv) | **CERRADO Y VERIFICADO** |
| **AUD-03** | **MENOR** | ISO/IEC 25010 · Eficiencia / ISO/IEC 25012 · Eficiencia | En `e1`, la Capa Plata y Oro se guardaban únicamente en `CSV UTF-8`, desaprovechando el óptimo del experimento factorial $2^3$ (`4 hilos + Pandera + Parquet`). | Se implementó `pipeline/optimizacion_dataset_e3.py` migrando la persistencia analítica a **Apache Parquet (`Snappy` y `ZSTD`)** con espejo CSV, logrando **`12.15×` de aceleración (`-91.77%` tiempo)**, **`-84.84%` RAM pico** y **`-87.31%` disco**. | [`pipeline/optimizacion_dataset_e3.py`](../pipeline/optimizacion_dataset_e3.py), [`data/oro/resumen_optimizacion_e3.json`](../data/oro/resumen_optimizacion_e3.json) | **CERRADO Y VERIFICADO** |
| **AUD-04** | **MENOR** | ISO/IEC 25012 · Exactitud Espacial | El `MultiPolygon` de Tecomán (`06009`) en OSM incluye las islas Revillagigedo, desplazando el centroide al calcular distancias (**Defecto #9**). | Se extrajo el polígono continental de mayor área en `EPSG:32613` dentro de `pipeline/geoespacial_e2.py`, corrigiendo la distancia Tecomán–Puerto de Manzanillo a **`54.1 km`**. | [`pipeline/geoespacial_e2.py`](../pipeline/geoespacial_e2.py), [`data/oro/perfil_geoespacial_municipios_oro.csv`](../data/oro/perfil_geoespacial_municipios_oro.csv) | **CERRADO Y VERIFICADO** |
| **AUD-05** | **MENOR** | ISO/IEC 25010 · Mantenibilidad | La importación `import pandera as pa` emitía `FutureWarning` en Pandera $\ge 0.20$ (**Defecto #13**) y faltaba medición formal de cobertura para el Sello TDL. | Se migró a `import pandera.pandas as pa` con fallback retrocompatible en `puerta_calidad.py`, `experimento_doe_e2.py` y `optimizacion_dataset_e3.py` (`0` warnings) y se verificó cobertura **`88.4%`** ($\ge 60\%$). | [`pipeline/puerta_calidad.py`](../pipeline/puerta_calidad.py), [`pipeline/calidad_sello_e3.py`](../pipeline/calidad_sello_e3.py) | **CERRADO Y VERIFICADO** |

---

## 2. Nuestro Proceso frente a los Modelos Normativos (MoProSoft, CMMI, ISO 9001, SPICE y PSP/TSP)

### 2.1 Autoevaluación del Observatorio contra MoProSoft (`NMX-I-059-NYCE`) y CMMI v2.0

Se evaluó la operación real de **CITRO-DATA LAB COLIMA** frente a las tres categorías de procesos de la norma mexicana **MoProSoft** y las áreas de práctica de **CMMI v2.0**, identificando con honestidad técnica el **nivel alcanzado (Nivel 3 · Definido)** y las **brechas concretas para alcanzar los Niveles 4 y 5**:

| Marco Normativo | Categoría / Dominio | Proceso o Área de Práctica Evaluada | Nivel Alcanzado | Evidencia Real en CITRO-DATA LAB COLIMA | Brecha Concreta para Nivel 4 (Gestionado Cuantitativamente) y Nivel 5 (Optimizado) |
| :--- | :--- | :--- | :---: | :--- | :--- |
| **MoProSoft** (`NMX-I-059-NYCE`) | **Alta Dirección (`DIR`)** | `DIR.1` Gestión de Negocio | **Nivel 3 · Definido** | Misión y cliente validados con entrevista de campo (22 min en Tecomán), objetivos medibles `O1–O3` ([`calidad/objetivos.md`](../calidad/objetivos.md)) y retorno económico cuantificado ($\$60\text{k}–\$120\text{k MXN}$ por camión de 20 ton). | Formalizar contratos SLA con asociaciones citrícolas pagadoras y tableros financieros trimestrales de ROI real. |
| **MoProSoft** (`NMX-I-059-NYCE`) | **Gerencia (`GER`)** | `GER.1` Gestión de Procesos<br>`GER.2` Gestión de Proyectos<br>`GER.3` Gestión de Recursos | **Nivel 3 · Definido** | Plan SQA bajo IEEE 730 ([`docs/plan-sqa.md`](plan-sqa.md)), entregas sincronizadas por tags (`e0..e3`), bitácoras PSP activas (`22` sesiones, `13` defectos) y base de conocimiento versionada en GitHub. | Establecer cartas de control estadístico de procesos (CEP $3\sigma$) sobre la velocidad de entrega comparada entre múltiples células de desarrollo. |
| **MoProSoft** (`NMX-I-059-NYCE`) | **Operación (`OPE`)** | `OPE.1` Admón. de Proyecto Específico<br>`OPE.2` Desarrollo y Mantenimiento | **Nivel 3 · Definido** *(con prácticas Nivel 4 en DOE)* | Arquitectura Medallion (`Bronce→Plata→Oro`), Puertas de Calidad 1, 2 y 3 automatizadas, linaje SHA-256 al `100%`, DOE factorial $2^3$ + confirmación y suite `pytest` en CI. | Automatizar el redespliegue continuo con *rollback* transaccional y reentrenamiento automático ante deriva de datos (*data drift*) en SARIMA. |
| **CMMI v2.0** | **Doing** *(Engineering & Developing)* | `RDM` (Requerimientos)<br>`TS` (Solución Técnica)<br>`VV` (Verificación y Validación) | **Nivel de Madurez 3 · Definido** | `12` requerimientos verificables trazados a pruebas, `18` módulos Python desacoplados y verificadores deterministas `verificar_e0.py` a `verificar_e3.py`. | Incorporar pruebas de mutación (*mutation testing*) y modelos probabilísticos de predicción de defectos por módulo antes de codificar. |
| **CMMI v2.0** | **Managing & Enabling** *(Quality & Config)* | `PQA` (Aseguramiento de Calidad)<br>`CM` (Gestión de Configuración)<br>`CAR` (Análisis Causal y Resolución) | **Nivel de Madurez 3 · Definido** *(`CAR` en Nivel 4)* | Auditoría ISO 25010/25012 con `5/5` hallazgos cerrados (`AUD-01..05`), control de versiones Git con hashes SHA-256 y análisis causal mediante ANOVA $2^3$ y $2\times 3$. | Extender el Análisis Causal (`CAR`) a un programa inter-equipos que prevenga patrones de defectos de forma transversal en toda la organización. |

### 2.2 Tabla Comparativa de los 5 Modelos del Temario (`ISO 9001`, `MoProSoft`, `SPICE`, `CMMI` y `PSP/TSP`)

| Modelo / Norma | Organismo / Origen | Enfoque Principal | Estructura y Escala de Evaluación | Cómo se Aplica en CITRO-DATA LAB COLIMA |
| :--- | :--- | :--- | :--- | :--- |
| **ISO 9001:2015** | ISO (Internacional) | Sistema de Gestión de la Calidad (SGC) organizacional general con enfoque a procesos y ciclo **PHVA**. | Cláusulas 4 a 10 (Contexto, Liderazgo, Planificación, Apoyo, Operación, Evaluación, Mejora). Certificación binaria (*Cumple / No cumple*). | Ciclo PHVA entre entregas `E0→E3`, gestión de riesgos en el Plan SQA y cierre documentado de no conformidades (`AUD-01` a `AUD-05`). |
| **MoProSoft (`NMX-I-059-NYCE`)** | NYCE / Secretaría de Economía (México) | Modelo de procesos diseñado específicamente para PyMEs y equipos pequeños/medianos de desarrollo y mantenimiento de software en México. | **3 Categorías** (*Alta Dirección `DIR`*, *Gerencia `GER`*, *Operación `OPE`*) con **9 procesos** evaluados en **5 niveles de capacidad** (`1 Realizado` a `5 Optimizado`). | Estructura rectora de nuestro laboratorio: conecta la propuesta comercial (`DIR`), la gestión SQA/PSP (`GER`) y la ingeniería del pipeline Medallion (`OPE`). **Nivel 3 alcanzado.** |
| **SPICE (`ISO/IEC 15504` $\to$ `ISO/IEC 33000`)** | ISO/IEC JTC 1/SC 7 (Internacional) | Marco internacional estandarizado para evaluar objetivamente la capacidad de los procesos de ciclo de vida del software y sistemas. | **Arquitectura bidimensional:** Dimensión de Procesos (`PRM`) $\times$ Dimensión de Capacidad (**Niveles `0 Incompleto` a `5 Innovador`** mediante atributos de proceso `PA 1.1` a `PA 5.2`). | Provee la escala formal de capacidad (`0–5`) que adopta MoProSoft; sustenta nuestros indicadores de desempeño de proceso y verificadores automáticos. |
| **CMMI v2.0** | SEI Carnegie Mellon / ISACA (Global) | Madurez organizacional e integración de áreas de práctica en ingeniería de sistemas, software, servicios y gestión de datos. | **Representación Continua** (Niveles de Capacidad `0–3` por Área de Práctica) y **Representación Escalonada** (**Niveles de Madurez `1 Inicial` a `5 En Optimización`**). | Aplicado en las áreas `RDM`, `TS`, `VV`, `PQA`, `CM` y `CAR` (análisis causal con experimento factorial $2^3$). **Nivel de Madurez 3 alcanzado.** |
| **PSP / TSP** (*Personal & Team Software Process*) | Watts Humphrey / SEI Carnegie Mellon | Disciplina operativa individual (`PSP`) y de equipo (`TSP`) basada en medición empírica del tiempo, defectos por fase, estimación (`PROBE`) y rendimiento de revisiones (*Yield*). | Evolución progresiva: `PSP0` (bitácoras de tiempo y defectos), `PSP1` (estimación de tamaño y esfuerzo), `PSP2` (revisiones de diseño y código, *Yield*) hacia `TSP`. | Operando desde `E0` en [`calidad/tiempo-norberto.csv`](../calidad/tiempo-norberto.csv) y [`calidad/defectos-norberto.csv`](../calidad/defectos-norberto.csv), logrando elevar el *Yield* de revisión al **`100.0%`** en `E3`. |

---

## 3. Retrospectiva Cuantitativa PSP con Nuestros Propios Datos (`E0 → E1 → E2 → E3`)

Los cálculos se obtuvieron programáticamente mediante `pipeline/calidad_sello_e3.py` a partir de las **22 sesiones cronometradas (`2,725 min = 45.42 horas netas`)** en [`calidad/tiempo-norberto.csv`](../calidad/tiempo-norberto.csv) y los **13 defectos reales (`100% cerrados`)** en [`calidad/defectos-norberto.csv`](../calidad/defectos-norberto.csv):

### 3.1 Evolución por Etapa (`E0` a `E3`): Exactitud de Estimación, Rendimiento de Revisiones (*Yield*) y Costo de Corrección

| Etapa del Proyecto | Sesiones | Tiempo Planeado (min) | Tiempo Real Neto (min / h) | Error de Estimación (%) | Exactitud de Estimación (%) | Defectos Totales | Eliminados en Revisión Temprana | Eliminados en Pruebas | Rendimiento de Revisión (*Yield* %) | Tiempo Medio de Corrección (min) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **`E0` · Arranque y Captura Bronce** | `6` | `540` (`9.0 h`) | `685` (`11.42 h`) | `26.85%` | **73.15%** | `4` (`#1–#4`) | `1` | `3` | **25.00%** | `14.25 min` |
| **`E1` · Plata, Puerta y Pronóstico** | `5` | `600` (`10.0 h`) | `665` (`11.08 h`) | `10.83%` | **89.17%** | `3` (`#5–#7`) | `0` | `3` | **0.00%** | `16.00 min` |
| **`E2` · Geodatos, DOE $2^3$ e ISO** | `5` | `630` (`10.5 h`) | `640` (`10.67 h`) | `1.59%` | **98.41%** | `3` (`#8–#10`) | `1` | `2` | **33.33%** | `13.67 min` |
| **`E3` · PCA/MANOVA, Parquet y Sello** | `6` | `810` (`13.5 h`) | `735` (`12.25 h`) | `9.26%` | **90.74%** | `3` (`#11–#13`) | `3` | `0` | **100.00%** | **`10.67 min`** |
| **Acumulado Total (`E0 → E3`)** | **`22`** | **`2,580`** (`43.0 h`) | **`2,725`** (`45.42 h`) | **`5.62%`** | **`94.38%`** | **`13`** | **`5`** | **`8`** | **`38.46%` global (`100%` en E3)** | **`13.69 min`** |

### 3.2 Defectos Inyectados y Eliminados por Fase PSP

| Fase PSP | Minutos Dedicados | Horas Dedicadas | % del Tiempo Total | Defectos Inyectados | % Defectos Inyectados | Defectos Eliminados | % Defectos Eliminados |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **1. `planeacion`** | `305 min` | `5.08 h` | `11.19%` | `0` | `0.00%` | `0` | `0.00%` |
| **2. `diseno`** | `335 min` | `5.58 h` | `12.29%` | `4` (`#2, #6, #10, #11`) | `30.77%` | `0` | `0.00%` |
| **3. `codigo`** | `1,150 min` | `19.17 h` | `42.20%` | `8` (`#1, #3, #5, #7, #8, #9, #12, #13`) | `61.54%` | `0` | `0.00%` |
| **4. `revision`** | `345 min` | `5.75 h` | `12.66%` | `0` | `0.00%` | **`5`** (`#2, #8, #11, #12, #13`) | **`38.46%`** |
| **5. `pruebas`** | `590 min` | `9.83 h` | `21.65%` | `1` (`#4`) | `7.69%` | **`8`** (`#1, #3, #4, #5, #6, #7, #9, #10`) | **`61.54%`** |

### 3.3 Tres Hallazgos Clave de la Retrospectiva PSP (`E0 → E3`)
1. **Convergencia en la exactitud de estimación de tiempo:** En `E0` subestimamos el esfuerzo en `26.85%` (exactitud `73.15%`) debido al tiempo invertido en la entrevista de campo y la validación de `robots.txt`. Al usar la velocidad histórica real de `E0` y `E1` (método *PROBE* de PSP), el error de estimación bajó a `10.83%` en `E1`, `1.59%` en `E2` y `9.26%` en `E3` (exactitud acumulada global del **`94.38%`**).
2. **Salto del Rendimiento de Revisión (*Yield*) al `100%` en `E3`:** En `E1` los 3 defectos escaparon hasta la fase de `pruebas` (`Yield = 0%`), costando `16.0 min` promedio por defecto. Al introducir revisiones formales de diseño y código antes de correr `pytest`, el *Yield* subió a `33.33%` en `E2` y alcanzó **`100.00%` en `E3`** (los defectos `#11` colinealidad en matriz de covarianzas, `#12` formato D3 en Vega-Lite y `#13` importación `pandera.pandas` se detectaron y eliminaron en la fase de `revision`).
3. **Reducción del `33.3%` en el costo de corrección:** Detectar defectos en la fase de `revision` redujo el tiempo medio de remediación de `16.00 min` en `E1` a **`10.67 min` en `E3`**, confirmando empíricamente la ley económica de PSP de Watts Humphrey.

---

## 4. Tendencias Actuales en Calidad Aplicadas al Observatorio: DataOps, Observabilidad de Datos, DevSecOps y Gobernanza de IA (`ISO/IEC 42001`)

En lugar de tratar la calidad como una inspección estática al final del desarrollo, **CITRO-DATA LAB COLIMA** integra cuatro tendencias contemporáneas de ingeniería de calidad directamente en su operación diaria:

### 4.1 DataOps y los 5 Pilares de la Observabilidad de Datos
Aplicamos los principios del *DataOps Manifesto* tratando las tuberías de datos y sus contratos estadísticos como código sujeto a integración continua. Nuestro sistema implementa los **5 pilares de la Observabilidad de Datos**:
1. **Frescura (*Freshness*):** Monitoreo automático de la ventana temporal en `calidad/bitacora_capturas.jsonl` mediante `.github/workflows/captura-bronce.yml` (`cron: "0 12 * * *"`), garantizando capturas diarias con disponibilidad de **`99.85%`** en los últimos 14 días.
2. **Distribución (*Distribution*):** Control de rangos físicos y económicos en `pipeline/puerta_calidad.py` (`Tmax ∈ [10, 50] °C`, `Precio > 0`, coherencia $T_{\max} \ge T_{\text{med}} \ge T_{\min}$) y monitoreo de normalidad multivariada mediante distancias de Mahalanobis ($D_i^2 \le \chi^2_{8, 0.95}$) en `pipeline/multivariado_pca_manova_e3.py`.
3. **Volumen (*Volume*):** Verificación determinista de conservación exacta de masa en cada transición Medallion (`7,544 válidos + 11 cuarentena = 7,555` en puerta tabular; `1,074 válidos + 90 cuarentena = 1,164` en puerta geoespacial).
4. **Esquema (*Schema*):** Contratos tipados estrictos con `Pandera (pandera.pandas)` y almacenamiento columnar `Apache Parquet (ZSTD)` que impiden mutaciones silenciosas de tipos.
5. **Linaje (*Lineage*):** Grafo DAG y trazabilidad registro a registro al **`100.0%` (`310/310` registros Oro)** con huella criptográfica `SHA-256` desde el archivo Bronce hasta el tablero público.

### 4.2 DevSecOps Integrado al Pipeline
La seguridad (*Shift-Left Security*) se ejecuta automáticamente en cada `push` y en cada verificación:
- **Escaneo estático de secretos (`SELLO-04`):** `pipeline/calidad_sello_e3.py` audita los `168` archivos de código, configuración y datos verificando **`0` llaves API o tokens expuestos**.
- **Privacidad por diseño (*Privacy by Design*):** Filtro de lista blanca y sanitización regex en `extractores/geoespacial_osm.py` que garantiza **`0` datos personales (PII)** desde antes de escribir en Capa Bronce.
- **Mínimo privilegio en CI/CD:** Los workflows de GitHub Actions operan con alcances explícitos restringidos y pruebas automatizadas bloqueantes.

### 4.3 Gobernanza de IA Generativa bajo `ISO/IEC 42001:2023` (*AI Management System*)
Conforme a la norma **ISO/IEC 42001:2023** (Sistemas de Gestión de Inteligencia Artificial), el uso de asistentes de IA generativa en el observatorio se rige por cuatro controles auditables:
1. **Transparencia y Declaración:** Cada relatoría (`relatoria-E1.md` a `relatoria-E3.md`) declara explícitamente qué herramienta de IA se utilizó y para qué tareas de apoyo (maquetación, refactorización o diseño de logotipo).
2. **Cero Alucinación en Datos (*Grounding & Deterministic Verification*):** Ningún dato climático, geoespacial, precio de limón, p-valor de ANOVA/MANOVA o pronóstico SARIMA proviene de un modelo generativo; el `100%` de las cifras proviene de cálculos matemáticos deterministas (`semilla=23460323`) sobre fuentes primarias verificadas con `SHA-256`.
3. **Supervisión Humana (*Human-in-the-Loop*):** Las tres Puertas de Calidad (Datos, CI y Supuestos Estadísticos) actúan como barreras formales antes de publicar cualquier hallazgo en el tablero.
4. **Explicabilidad de Negocio:** Todos los modelos estadísticos (SARIMA, DOE $2^3$, PCA y MANOVA) son modelos caja-blanca auditables cuyos intervalos de confianza y supuestos se comunican honestamente al productor citrícola.

---

## 5. Solicitud Formal y Evidencia del Sello TDL (`6 / 6` Criterios Aprobados)

Con fundamento en la tabla oficial de las páginas 20 y 21 de la guía **Trusted Data Lab**, el observatorio **CITRO-DATA LAB COLIMA** presenta la evidencia verificable que acredita el cumplimiento del **100% de los criterios del Sello TDL**:

| ID | Criterio Oficial del Sello TDL | Umbral Mínimo Oficial | Resultado Medido en CITRO-DATA LAB COLIMA | Estado | Evidencia Directa en el Repositorio |
| :---: | :--- | :---: | :--- | :---: | :--- |
| **SELLO-01** | **Disponibilidad medida de la captura** | `≥ 95%` en los últimos 14 días | **`99.85%`** de disponibilidad real $A = \text{MTBF}/(\text{MTBF}+\text{MTTR})$ en las `336 h` del `14 al 27 de noviembre` (`100.0%` de éxito en las `9/9` corridas posteriores al parche `AUD-01`). | **CUMPLE ✓** | [`calidad/bitacora_capturas.jsonl`](../calidad/bitacora_capturas.jsonl), [`data/oro/resumen_calidad_sello_e3.json`](../data/oro/resumen_calidad_sello_e3.json) |
| **SELLO-02** | **Completitud de la Capa Oro (`ISO/IEC 25012`)** | `≥ 95%` | **`100.00%`** (`29,720 / 29,720` celdas válidas y **`0` valores nulos** en las 4 tablas maestras de Capa Oro). | **CUMPLE ✓** | [`data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet`](../data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet), [`data/oro/evaluacion_iso_25012_e2.csv`](../data/oro/evaluacion_iso_25012_e2.csv) |
| **SELLO-03** | **Cobertura de pruebas automáticas** | `≥ 60%` | **`88.40%`** de cobertura medida con `35` pruebas unitarias e integrales automatizadas en `pytest`. | **CUMPLE ✓** | [`tests/`](../tests/), [`.github/workflows/ci-calidad.yml`](../.github/workflows/ci-calidad.yml) |
| **SELLO-04** | **Secretos expuestos en el repositorio** | `0` | **`0` secretos expuestos** en los `168` archivos auditados del repositorio y **`0` columnas PII**. | **CUMPLE ✓** | [`pipeline/calidad_sello_e3.py`](../pipeline/calidad_sello_e3.py), [`docs/etica-datos.md`](etica-datos.md) |
| **SELLO-05** | **Hallazgos críticos de auditoría abiertos** | `0` | **`0` críticos abiertos** y `0` mayores/menores abiertos (`5 / 5` hallazgos `AUD-01..AUD-05` cerrados con evidencia). | **CUMPLE ✓** | [`data/oro/cierre_auditoria_e3.csv`](../data/oro/cierre_auditoria_e3.csv), Sección 1 de este documento |
| **SELLO-06** | **Reproducibilidad** | Un tercero clona el repositorio y obtiene los mismos resultados | **`100%` reproducible y determinista** (`semilla=23460323`, verificadores `verificar_e0.py` a `verificar_e3.py` y CI en verde). | **CUMPLE ✓** | [`pipeline/verificar_e3.py`](../pipeline/verificar_e3.py), [`README.md`](../README.md) |
