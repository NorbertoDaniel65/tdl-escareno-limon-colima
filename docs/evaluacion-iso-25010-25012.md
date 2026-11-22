# Evaluación de Calidad con Normas ISO/IEC 25010 e ISO/IEC 25012, Antecedentes Normativos y Auditoría Técnica (E2)

* **Observatorio:** **CITRO-DATA LAB COLIMA** — Observatorio Agroclimático, Geoespacial y de Precios Mayoristas del Limón Mexicano
* **Estudiante:** Norberto Daniel Escareño Montaño (`No. Control: 23460323`, `@NorbertoDaniel65`)
* **Etapa:** `E2` — *Trusted Data Lab: Experimento, Fuente Especializada, Linaje y Evaluación Normativa*
* **Artefactos de Datos Medidos:** `data/oro/evaluacion_iso_25010_e2.csv`, `data/oro/evaluacion_iso_25012_e2.csv`, `data/oro/resumen_evaluacion_iso_e2.json`
* **Fecha de Evaluación:** 22 de noviembre de 2026

---

## 1. Antecedentes Normativos: Relación entre ISO/IEC 9126, Familia ISO/IEC 25000 (SQuaRE) e ISO 9001

Para sustentar técnicamente la evaluación del observatorio, el siguiente cuadro relaciona los tres marcos normativos internacionales del temario, evitando confusiones entre calidad de **proceso**, calidad de **producto de software** y calidad de **datos**:

| Norma Internacional | Objeto Principal de Evaluación | Alcance y Evolución Histórica | Aplicación Concreta en CITRO-DATA LAB COLIMA |
| :--- | :--- | :--- | :--- |
| **ISO/IEC 9126** *(1991 / 2001 — Histórica)* | Calidad del **producto de software** | Definió originalmente 6 características (Funcionalidad, Fiabilidad, Usabilidad, Eficiencia, Mantenibilidad y Portabilidad). Fue **formalmente sustituida y reemplazada** en 2011 por la familia **ISO/IEC 25000 (SQuaRE)**. | Sirve como referente histórico conceptual; en el proyecto se migran sus 6 dimensiones a las 8 características vigentes de **ISO/IEC 25010** (agregando *Seguridad* y *Compatibilidad* como pilares de primer nivel). |
| **ISO/IEC 25000 (SQuaRE) — ISO/IEC 25010** *(Vigente)* | Calidad del **producto de software** | *System and Software Quality Requirements and Evaluation.* Sucesora directa de ISO/IEC 9126. Evalúa 8 características medibles: Adecuación Funcional, Eficiencia de Desempeño, Compatibilidad, Capacidad de Interacción (Usabilidad), Fiabilidad, Seguridad, Mantenibilidad y Portabilidad. | Se evalúan las 8 características con métricas objetivas ejecutadas en `pipeline/evaluacion_iso_e2.py`. El **Experimento Factorial $2^3$** aporta evidencia empírica de *Eficiencia de Desempeño* y las bitácoras de GitHub Actions sustentan *Fiabilidad*. |
| **ISO/IEC 25000 (SQuaRE) — ISO/IEC 25012** *(Vigente)* | Calidad de los **datos** | Complementa a 25010 definiendo 15 características de calidad de datos agrupadas en dos puntos de vista: **Inherentes** (exactitud, completitud, consistencia, credibilidad, actualidad) y **Dependientes del sistema** (disponibilidad, portabilidad, recuperabilidad), más características mixtas (trazabilidad, confidencialidad, conformidad, eficiencia, precisión, accesibilidad, comprensibilidad). | Se mide directamente sobre las 3 tablas maestras de la **Capa Oro (`310` registros)** verificando `100.0%` de completitud (`0` nulos), `100.0%` de trazabilidad (linaje), `0` PII y conservación de masa en la Puerta de Calidad. |
| **ISO 9001:2015** *(Vigente)* | Sistema de Gestión de la Calidad — **Enfoque a Procesos** | No evalúa código ni datos de forma aislada, sino la **capacidad del proceso organizacional** para entregar valor consistente mediante el ciclo **PHVA (Planificar–Hacer–Verificar–Actuar)**, gestión de riesgos, evidencia documentada y mejora continua. | Se materializa en el **Plan SQA (IEEE 730)**, los registros individuales **PSP** (`tiempo-norberto.csv`, `defectos-norberto.csv`), la **Integración Continua** en GitHub Actions y el ciclo de hallazgos y acciones correctivas de auditoría. |

---

## 2. Evaluación Cuantitativa del Producto de Software — ISO/IEC 25010

Todas las calificaciones se calcularon programáticamente mediante `pipeline/evaluacion_iso_e2.py` (promedio general: **`95.38 / 100`**):

| Característica ISO/IEC 25010 | Métrica Objetiva Definida | Resultado Medido (Evidencia Real) | Puntaje (/100) | Artefacto de Evidencia |
| :--- | :--- | :--- | :---: | :--- |
| **1. Adecuación Funcional** | % de requerimientos verificables cumplidos (E0+E1+E2) | `12 / 12` requerimientos verificados (`100.0%`) | **98** | `pipeline/verificar_e0.py`, `verificar_e1.py`, `verificar_e2.py` |
| **2. Eficiencia de Desempeño** | Reducción de tiempo (`ms`) y disco (`KB`) en Experimento Factorial $2^3$ + Confirmación ($n=5$) | **`-78.95%` tiempo (`4.75×` speedup: `336.96 → 70.93 ms`)** y **`-91.13%` disco** | **97** | `data/oro/resumen_experimento_doe_e2.json`, `corrida_confirmacion_optimo_e2.csv` |
| **3. Compatibilidad** | Interoperabilidad sin pérdida entre 3 fuentes heterogéneas y estándares abiertos | `3/3` fuentes integradas (`JSON`, `HTML`, `GeoJSON RFC 7946 / EPSG:4326`, `Parquet`) | **95** | `data/oro/resolucion_conflictos_integracion.json`, `resumen_geoespacial_e2.json` |
| **4. Capacidad de Interacción** | Módulos interactivos, cartografía e interpretación en lenguaje llano para el cliente | Tablero Streamlit de `6` pestañas temáticas y `10` figuras HD con guía de negocio | **93** | `tablero/app.py`, `docs/E1..E2/figuras/` |
| **5. Fiabilidad** | Disponibilidad real $A = \text{MTBF}/(\text{MTBF}+\text{MTTR})$ en `306 h` de operación continua (9–22 nov) | **`A = 99.74%`** (`MTBF = 101.73 h`, `MTTR = 0.27 h`; `26/29` ops = `89.66%` por 3 incidentes transitorios de Open-Meteo) | **92** | `calidad/bitacora_capturas.jsonl`, GitHub Actions Runs y Defectos `#5` y `#8` |
| **6. Seguridad** | Escaneo estático de secretos expuestos, auditoría PII y privilegios mínimos en CI | **`0` secretos** en `144` archivos; **`0` columnas PII**; `GITHUB_TOKEN` restringido | **98** | `pipeline/evaluacion_iso_e2.py`, `docs/etica-datos.md` |
| **7. Mantenibilidad** | Arquitectura modular desacoplada, trazabilidad PSP y CI automatizado en `push` | `11` módulos desacoplados, `100%` defectos PSP cerrados y suite `pytest` en verde | **94** | `.github/workflows/ci-calidad.yml`, `tests/`, `calidad/defectos-norberto.csv` |
| **8. Portabilidad** | Reproducibilidad verificada en múltiples sistemas operativos y costo `$0` | Verificado en Windows 11 (`Python 3.13`) y Ubuntu Linux CI (`Python 3.11`) | **96** | `requirements.txt`, `.github/workflows/ci-calidad.yml` |

---

## 3. Evaluación Cuantitativa de Calidad de Datos — ISO/IEC 25012 (sobre Capa Oro)

Medida sobre las 3 tablas maestras de Capa Oro (`serie_mensual_oro_60m.csv`, `panel_integrado_municipio_mercado_oro.csv`, `perfil_geoespacial_municipios_oro.csv` — promedio general: **`97.58 / 100`**):

| Característica ISO/IEC 25012 | Punto de Vista | Medición Verificada sobre Capa Oro | Puntaje (/100) |
| :--- | :---: | :--- | :---: |
| **Exactitud** | Inherente | Error de pronóstico en prueba `MAPE = 3.04%`; `0` violaciones `RN-01..RN-03`; áreas proyectadas `EPSG:32613` | **97.0** |
| **Completitud** | Inherente | **`0` valores nulos** en la totalidad de celdas de las 3 tablas maestras de Capa Oro (`100.0%`) | **100.0** |
| **Consistencia** | Inherente | Conservación exacta de masa: Puerta Tabular (`7,544 + 11 = 7,555`) y Geoespacial (`1,074 + 90 = 1,164`) | **100.0** |
| **Credibilidad** | Inherente | `3` fuentes primarias institucionales/abiertas verificables (Copernicus ERA5-Land, SNIIM-SE, OSM/INEGI) | **94.0** |
| **Actualidad** | Inherente | Captura diaria automática vigente al `2026-11-21` + captura geoespacial del `2026-11-22` | **95.0** |
| **Accesibilidad** | Mixta | Datasets abiertos en CSV/GeoJSON/JSON versionados en GitHub y tablero público Streamlit | **96.0** |
| **Conformidad** | Mixta | Estándares ISO-8601, UTF-8, GeoJSON RFC 7946 (`EPSG:4326`), LFPDPPP, CC BY 4.0 y ODbL 1.0 | **98.0** |
| **Confidencialidad** | Mixta | **`0` datos personales (PII)** en todas las capas; lista blanca + sanitizador regex en Bronce | **100.0** |
| **Eficiencia** | Mixta | Compresión `Parquet` (`-91.13%` a `-92.76%` disco) y reducción de filas Bronce $\to$ Oro (`99.18%`) | **96.0** |
| **Precisión** | Mixta | Precios/clima a 2 decimales y coordenadas WGS84 a 5–6 decimales (`~0.1–1 m`) | **97.0** |
| **Trazabilidad (Linaje)** | Mixta | **`310 / 310` registros Oro (`100.0%`)** con `linaje_id_registro`, archivo Bronce, `SHA-256` y fecha UTC | **100.0** |
| **Comprensibilidad** | Mixta | Diccionario formal completo (`data/oro/diccionario_datos.md`) + interpretación comercial llana | **95.0** |
| **Disponibilidad** | Dependiente del Sistema | Disponibilidad operativa real **`A = 99.74%`** sobre `306 h` continuas en GitHub Actions | **99.7** |
| **Portabilidad** | Dependiente del Sistema | Formatos abiertos no propietarios (`CSV`, `GeoJSON`, `Parquet`, `JSON`) | **98.0** |
| **Recuperabilidad** | Dependiente del Sistema | Capa Bronce inmutable con `SHA-256` + Cuarentena preservada (reconstrucción 100% determinista) | **98.0** |

---

## 4. Auditoría Técnica sobre el Estado de Entrega `e1` (Hallazgos Clasificados por Severidad)

> **Nota de modalidad:** Dado que el alumno desarrolla el proyecto en modalidad individual dentro de las asignaturas de Ingeniería de Datos y Análisis Estadístico (sin par asignado en Classroom de Calidad en SI), se ejecutó una **auditoría técnica rigurosa estilo consultoría externa sobre el estado etiquetado `e1`** aplicando las listas de comprobación de **ISO/IEC 25010** e **ISO/IEC 25012**, documentando los hallazgos reales detectados y las acciones correctivas aplicadas en `e2` (o programadas para cierre definitivo en `e3`):

| ID | Severidad | Norma / Característica | Hallazgo Detectado (con Evidencia Real) | Recomendación y Acción Correctiva | Estado en E2 |
| :---: | :---: | :--- | :--- | :--- | :---: |
| **AUD-01** | **MAYOR** | ISO 25010 · Fiabilidad | En los runs de GitHub Actions `#44168162030` (`2026-11-17`) y `#44384386430` (`2026-11-18`), `api.open-meteo.com` respondió HTTP `5xx/429` agotando los 3 reintentos; además `ExtractorEtico.get()` reportó `ultimo_error: None` ocultando el código HTTP exacto (**Defecto #8**). | Registrar explícitamente `RuntimeError(f"HTTP {r.status_code}")` en `extractores/base.py`, añadir soporte `POST` resiliente y evaluar aumento de reintentos/backoff en E3. | **CORREGIDO EN E2** |
| **AUD-02** | **MAYOR** | ISO 25012 · Trazabilidad | En el estado `e1`, los archivos `serie_mensual_oro_60m.csv` y `panel_integrado_municipio_mercado_oro.csv` dependían de metadatos externos (`.meta.json`) pero no incluían columnas de linaje por registro individual. | Inyectar 6 columnas de linaje (`linaje_id_registro`, `linaje_fuentes_bronce`, `linaje_archivos_bronce`, `linaje_sha256_bronce`, `linaje_fecha_ingesta_utc`, `linaje_version_pipeline`) y generar `linaje_datos_e2.json` + `catalogo_linaje_oro_bronce.csv`. | **CORREGIDO EN E2** |
| **AUD-03** | **MENOR** | ISO 25010 · Eficiencia / ISO 25012 · Eficiencia | La persistencia en Capa Plata y Oro de `e1` utilizaba exclusivamente `CSV UTF-8`, lo que consume `11.3×` más espacio en disco y `4.75×` mayor latencia que la combinación óptima demostrada en el DOE $2^3$ (`4 hilos + Pandera + Parquet`). | Adoptar `Apache Parquet (Snappy/ZSTD)` como formato analítico optimizado en la optimización medida de la Etapa **E3** manteniendo espejo CSV para inspección humana. | **PLANIFICADO PARA E3** |
| **AUD-04** | **MENOR** | ISO 25012 · Exactitud Espacial | Al integrar la fuente geoespacial OSM, el polígono administrativo de Tecomán (`06009`) incluye el archipiélago oceánico de Revillagigedo (`MultiPolygon`), desplazando el centroide hacia el Pacífico y distorsionando la distancia al Puerto de Manzanillo (**Defecto #9**). | Extraer el polígono continental de mayor superficie para cálculo de centroides y distancias métricas en `EPSG:32613` dentro de `pipeline/geoespacial_e2.py`. | **CORREGIDO EN E2** |
| **AUD-05** | **MENOR** | ISO 25010 · Mantenibilidad | Advertencia de deprecación `FutureWarning` en importación raíz `import pandera as pa` en versiones recientes de Pandera (`>=0.20`). | Estandarizar importación moderna y medir cobertura de pruebas con `pytest --cov` en CI para superar el umbral $\ge 60\%$ del Sello TDL en E3. | **EN SEGUIMIENTO (E3)** |
