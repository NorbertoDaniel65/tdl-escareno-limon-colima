# Plan de Aseguramiento de la Calidad del Software (SQA — IEEE 730) y Métricas de Fiabilidad Real (E1)

* **Proyecto:** CITRO-DATA LAB COLIMA — Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano en Colima
* **Estudiante:** Norberto Daniel Escareño Montaño (`No. Control: 23460323`, GitHub: `@NorbertoDaniel65`)
* **Materias Integradas:** Ingeniería de Datos (`CMD-2602` · Mtro. Armando Román Gallardo Heredia) y Análisis Estadístico para Ciencia de Datos (Mtro. Mónico Joel Sánchez Velasco)
* **Etapa:** `E1` — *Trusted Data Lab: Capa Plata, Limpieza, Puerta de Calidad y Pronóstico*
* **Estándar de Referencia:** IEEE Std 730-2014 (*Software Quality Assurance Processes*) e ISO/IEC 25010 / 25012 (*Calidad de Producto y Calidad de Datos*)

---

## 1. Propósito y Alcance (Sección 1 IEEE 730)

El presente Plan de Aseguramiento de la Calidad del Software (SQA) establece los procesos, controles automatizados, estándares de codificación, auditorías de seguridad y métricas cuantitativas que garantizan que el pipeline **CITRO-DATA LAB COLIMA** transforme las capturas de la Capa Bronce (`data/bronce/`) en series limpias y trazables en la Capa Plata (`data/plata/`) y en conjuntos integrados de alta confiabilidad en la Capa Oro (`data/oro/`), bloqueando cualquier registro corrupto mediante una **Puerta de Calidad Automática** (`pipeline/puerta_calidad.py`) que envía rechazos a cuarentena (`data/cuarentena/`) sin borrado silencioso.

---

## 2. Documentos de Referencia y Estándares (Sección 2 IEEE 730)

1. **IEEE Std 730-2014:** Estructura del Plan de Aseguramiento de la Calidad de Software.
2. **ISO/IEC 25012:** Modelo de Calidad de Datos (Exactitud, Completitud, Consistencia, Credibilidad y Actualidad).
3. **ISO/IEC 25010:** Modelo de Calidad de Software (Fiabilidad, Madurez, Disponibilidad y Mantenibilidad).
4. **PSP (*Personal Software Process* — Humphrey):** Bitácoras individuales de tiempo (`calidad/tiempo-norberto.csv`) y defectos (`calidad/defectos-norberto.csv`).
5. **Contratos de Datos Deterministas:** Esquemas formales con `Pandera` (`DataFrameSchema`) y pruebas automatizadas en `pytest` ejecutadas en Integración Continua (`.github/workflows/ci-calidad.yml`).

---

## 3. Gestión, Roles y Responsabilidades (Sección 3 IEEE 730)

Al tratarse de un proyecto individual de alcance completo, las funciones de ingeniería y aseguramiento de calidad están separadas por fase dentro del ciclo PSP:

| Rol Funcional | Responsable | Actividades de Calidad en Etapa E1 |
| :--- | :--- | :--- |
| **Ingeniero de Datos y Arquitecto de Pipeline** | Norberto Daniel Escareño Montaño (`@NorbertoDaniel65`) | Diseño e implementación de extractores éticos (`extractores/`), limpieza en Capa Plata (`pipeline/limpieza_plata.py`) e integración en Capa Oro (`pipeline/integracion_oro.py`). |
| **Analista Estadístico y Modelador de Series** | Norberto Daniel Escareño Montaño (`@NorbertoDaniel65`) | Descomposición multiplicativa, pruebas ADF/ACF/PACF/CCF, evaluación en prueba de los 4 modelos (SES, Holt, Holt-Winters, SARIMA) y diagnóstico Ljung-Box (`pipeline/series_tiempo_e1.py`). |
| **Auditor SQA y Automatización CI/CD** | Norberto Daniel Escareño Montaño (`@NorbertoDaniel65`) | Mantenimiento de la Puerta de Calidad (`pipeline/puerta_calidad.py`), suite de pruebas (`tests/`), workflows de GitHub Actions (`captura-bronce.yml` y `ci-calidad.yml`) y bitácoras PSP (`calidad/`). |

---

## 4. Especificación de Requerimientos Verificables del Sistema (Sección 4 IEEE 730)

Todos los requerimientos de la Etapa E1 se formulan con criterios cuantitativos verificables de forma determinista por `pytest` y `pipeline/verificar_e1.py`:

| ID Req. | Categoría | Descripción del Requerimiento Verificable | Umbral / Criterio de Aceptación | Verificador Automatizado | Estado E1 |
| :---: | :--- | :--- | :--- | :--- | :---: |
| **REQ-E1-01** | Fiabilidad de Ingesta | El extractor ético debe reintentar con *backoff* exponencial ante excepciones HTTP (`429/5xx`) y de red (`ReadTimeout`, `ConnectionError`), respetando `robots.txt` y pausa $\ge 1.5\text{ s}$. | `3` reintentos con espera $1.5 \times 2^i\text{ s}$; hash `SHA-256` en `.meta.json`. | `tests/test_extractor_etico.py` | **CUMPLIDO** |
| **REQ-E1-02** | Puerta de Calidad y Cuarentena | Todo registro que viole tipos, rangos físicos/económicos, unicidad de llave primaria o reglas `RN-01` a `RN-04` debe ser detenido antes de Capa Plata y enviado a `data/cuarentena/` con motivo documentado. | `0` registros inválidos en `data/plata/`; `100%` de rechazos en `data/cuarentena/cuarentena_registros.csv`. | `tests/test_e1_limpieza_puerta.py` | **CUMPLIDO** |
| **REQ-E1-03** | Tratamiento de Faltantes | Diagnóstico estadístico de mecanismos `MCAR`, `MAR` y `MNAR` y comparación cuantitativa de 4 métodos de tratamiento midiendo sesgo en media ($\Delta\mu$), desviación estándar ($\Delta\sigma$), MAE y RMSE. | `0` valores `NaN` en las tablas finales de Capa Plata y Capa Oro. | `tests/test_e1_limpieza_puerta.py` | **CUMPLIDO** |
| **REQ-E1-04** | Preservación de Choques de Dominio | Detección de atípicos con 3 métodos (`IQR`, `Z-Score Robusto MAD`, `Isolation Forest`) distinguiendo ruido de sensor (a cuarentena) vs. choques reales de mercado (feb-mar 2022, feb 2024), los cuales se conservan y etiquetan. | Columna booleana `es_choque_legitimo_dominio` presente y documentada. | `tests/test_e1_limpieza_puerta.py` | **CUMPLIDO** |
| **REQ-E1-05** | Integración en Capa Oro | Unión de `Open-Meteo` y `SNIIM` en `data/oro/serie_mensual_oro_60m.csv` resolviendo conflictos de granularidad, esquema, unidades y entidades, acompañada de `data/oro/diccionario_datos.md`. | Exactamente `60` meses continuos (`2021-01` a `2025-12`) sin huecos ni duplicados. | `tests/test_e1_series_tiempo.py` | **CUMPLIDO** |
| **REQ-E1-06** | Selección y Diagnóstico de Pronóstico | Comparación de 4 modelos (`SES`, `Holt`, `Holt-Winters`, `SARIMA`) sobre 12 meses de prueba (`2025`), selección por menor RMSE/MAPE, residuos con ruido blanco en Ljung-Box ($p > 0.05$) y pronóstico `2026` con IC al `95%`. | $\text{MAPE}_{\text{test}} < 10\%$ y $p_{\text{Ljung-Box}}(12) > 0.05$. | `tests/test_e1_series_tiempo.py` | **CUMPLIDO** |
| **REQ-E1-07** | Integración Continua y Seguridad | Ejecución automática de pruebas y puerta de calidad en cada `push` mediante `.github/workflows/ci-calidad.yml` y auditoría de cero secretos expuestos en el repositorio. | Workflow en verde y `0` credenciales o tokens hardcodeados en código. | `.github/workflows/ci-calidad.yml` | **CUMPLIDO** |

---

## 5. Medición Real de Fiabilidad, MTBF, MTTR y Disponibilidad (E0 $\to$ E1)

Siguiendo la rúbrica de calidad del proyecto integrador, se calculan los indicadores reales de fiabilidad y disponibilidad del pipeline automatizado a partir de la bitácora operativa `calidad/bitacora_capturas.jsonl` y del historial de ejecuciones programadas de `.github/workflows/captura-bronce.yml` en GitHub Actions entre el **9 de noviembre de 2026 (`22:27 UTC`)** y el **13 de noviembre de 2026 (`19:03 UTC`)** (ventana de observación operativa de $T_{\text{total}} = 92.60\text{ horas}$):

### 5.1 Historial Real de Ejecuciones en GitHub Actions y Bitácora

| Fecha (UTC) | Evento / Run | Operaciones Ejecutadas | Resultado | Detalle Técnico / Incidente |
| :---: | :--- | :--- | :---: | :--- |
| `2026-11-09 22:27` | Inicialización + Captura Diaria `#1` | `4` (`open_meteo_archive`, `sniim_historico`, `open_meteo_forecast`, `sniim_portal_web`) | **ÉXITO** | 4 archivos en Bronce con SHA-256 verificado. |
| `2026-11-09 22:36` | Verificación Workflow `#2` | `2` (`open_meteo_forecast`, `sniim_portal_web`) | **ÉXITO** | Snapshot `2026-11-09` verificado. |
| `2026-11-10 19:10` | Cron Diario Programado `#3` | `2` (`open_meteo_forecast`, `sniim_portal_web`) | **ÉXITO** | Snapshot `2026-11-10` guardado (`11.23 s`). |
| `2026-11-11 19:07` | Cron Diario Programado `#4` | `2` (`open_meteo_forecast`, `sniim_portal_web`) | **ÉXITO** | Snapshot `2026-11-11` guardado (`6.24 s`). |
| `2026-11-12 19:05` | Cron Diario Programado `#5` (`Run #43289949095`) | `1` intento en `open_meteo_forecast` | **FALLO (`ReadTimeout`)** | `requests.exceptions.ReadTimeout` en `api.open-meteo.com`. Detectado y registrado como **Defecto #5**. |
| `2026-11-12 19:23` | Corrección Defecto #5 en `extractores/base.py` | Parche de reintento ante `Timeout`/`ConnectionError` | **CORREGIDO** | Tiempo de diagnóstico y reparación ($\text{MTTR}$) = `18 minutos` (`0.30 h`). |
| `2026-11-13 19:02` | Cron Diario Programado `#6` | `2` (`open_meteo_forecast`, `sniim_portal_web`) | **ÉXITO** | Snapshot `2026-11-13` guardado (`10.33 s`). |

### 5.2 Cálculo Formal de Métricas de Fiabilidad y Disponibilidad

1. **Tasa de Éxito por Operación de Fuente:**
   $$\text{Tasa de Éxito}_{\text{operaciones}} = \frac{12\text{ operaciones exitosas}}{13\text{ operaciones intentadas}} = 92.31\%$$
   *(Y **100.0%** de éxito en todas las ejecuciones posteriores a la corrección del Defecto #5 en `extractores/base.py`).*

2. **Tiempo Medio Entre Fallos ($\text{MTBF}$):**
   Durante la ventana operativa total de $T_{\text{operativo}} = 92.30\text{ horas}$ (descontando los $18\text{ min} = 0.30\text{ h}$ de corrección del único incidente), ocurrió $N_{\text{fallos}} = 1$ fallo transitorio de red:
   $$\text{MTBF} = \frac{T_{\text{operativo}}}{N_{\text{fallos}}} = \frac{92.30\text{ h}}{1} = 92.30\text{ horas}\quad (\approx 3.85\text{ días de operación continua por incidente})$$

3. **Tiempo Medio de Recuperación / Reparación ($\text{MTTR}$):**
   El incidente `ReadTimeout` del 12 de noviembre fue diagnosticado e instrumentado con *backoff* exponencial sobre `requests.exceptions.Timeout` en `extractores/base.py` en exactamente **18 minutos** (registrado en `calidad/defectos-norberto.csv`, Defecto #5):
   $$\text{MTTR} = 18\text{ minutos} = 0.30\text{ horas}$$

4. **Disponibilidad Operativa Real del Sistema ($A$):**
   $$A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}} = \frac{92.30\text{ h}}{92.30\text{ h} + 0.30\text{ h}} = \frac{92.30}{92.60} = 0.9968 \implies \mathbf{99.68\%}$$

### 5.3 Comparación contra Objetivos de Calidad E0 (`calidad/objetivos.md`)

| Objetivo Definido en E0 | Meta Comprometida | Valor Medido en E1 | Cumplimiento y Análisis |
| :--- | :---: | :---: | :--- |
| **O1 · Fiabilidad y Disponibilidad de Captura** | Disponibilidad $\ge 95\%$ | **Disponibilidad $A = 99.68\%$** (Tasa de operaciones: `92.31%` bruta $\to$ `100%` tras fix) | **CUMPLIDO EN DISPONIBILIDAD ($99.68\% \ge 95\%$)**. El único fallo por `ReadTimeout` reveló que el bloque `try/except` original sólo capturaba códigos HTTP y no timeouts de socket; tras el parche en `extractores/base.py`, la resiliencia ante microcortes quedó blindada. |
| **O2 · Integridad y Completitud en Capa Plata/Oro** | $0\%$ nulos no tratados; $100\%$ trazabilidad SHA-256 | **$0.0\%$ nulos en Plata/Oro** y **$100\%$ SHA-256 válido** | **SUPERADO**. La Puerta de Calidad detuvo el $100\%$ de los $11$ registros defectuosos del lote de auditoría enviándolos a `data/cuarentena/`. |
| **O3 · Calidad del Proceso PSP (Fase de Eliminación)** | $\ge 80\%$ de defectos eliminados antes de entrega | **$100\%$ (`7/7` defectos eliminados en revisión/pruebas)** | **SUPERADO**. Ningún defecto llegó a la rama etiquetada `e1`. |

---

## 6. Auditoría de Seguridad y Gestión de Configuración (Sección 5 IEEE 730)

1. **Verificación de Secretos Expuestos:** Se auditó la totalidad del árbol de archivos del repositorio (`.py`, `.yml`, `.json`, `.md`, `.ipynb`) verificando que **no existe ninguna llave privada, token personal (`PAT`), contraseña ni credencial hardcodeada** (`0` secretos expuestos).
2. **Permisos Mínimos en GitHub Actions:** Tanto `.github/workflows/captura-bronce.yml` como `.github/workflows/ci-calidad.yml` utilizan exclusivamente el token efímero nativo `GITHUB_TOKEN` con alcance restringido.
3. **Trazabilidad Criptográfica:** Cada archivo de la Capa Bronce cuenta con su par `.meta.json` con suma de verificación `SHA-256`, y todos los rechazos de la Puerta de Calidad se conservan de forma inmutable en `data/cuarentena/cuarentena_registros.csv`.
