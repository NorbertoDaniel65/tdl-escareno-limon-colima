# Relatoría de Etapa E1 — *Trusted Data Lab: Capa Plata, Limpieza, Puerta de Calidad y Pronóstico*

* **Proyecto:** CITRO-DATA LAB COLIMA — Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano en Colima
* **Estudiante:** Norberto Daniel Escareño Montaño (`No. Control: 23460323`, GitHub: `@NorbertoDaniel65`)
* **Materias:** Ingeniería de Datos (`CMD-2602` · Mtro. Armando Román Gallardo Heredia) y Análisis Estadístico para Ciencia de Datos (Mtro. Mónico Joel Sánchez Velasco)
* **Fecha de Corte E1:** 13 de noviembre de 2026
* **Etiqueta de Versión:** `e1`

---

## 1. ¿Qué nos propusimos en esta etapa?

En la Etapa E1 nos propusimos construir la **Capa Plata (`data/plata/`)**, la **Puerta de Calidad Automática (`data/cuarentena/`)** y la **Capa Oro (`data/oro/`)** del observatorio **CITRO-DATA LAB COLIMA**, así como responder con rigor estadístico la **Pregunta 1 (Temporal)** formulada en E0:
> *«¿Cómo evolucionará el precio mayorista frecuente del limón mexicano (`MXN/kg`) en origen Colima durante los próximos 12 meses, y cómo se relaciona su estacionalidad con el régimen de déficit hídrico y temperatura máxima en el valle de Tecomán?»*

Las metas cuantitativas fueron:
1. Garantizar que **ningún registro corrupto ingrese a la Capa Plata ni se elimine en silencio**, enviando el `100%` de las violaciones de esquema, rango, unicidad y reglas de negocio a `data/cuarentena/cuarentena_registros.csv`.
2. Diagnosticar formalmente los mecanismos de valores faltantes (`MCAR`, `MAR`, `MNAR`) y seleccionar el método de imputación con menor sesgo ($\Delta\mu, \Delta\sigma$) y menor RMSE.
3. Distinguir entre ruido de sensor y choques reales del mercado citrícola (febrero-marzo 2022 y febrero 2024) usando `IQR`, `Z-Score Robusto (MAD)` e `Isolation Forest`.
4. Integrar las fuentes `Open-Meteo` y `SNIIM` en una serie maestra mensual de 60 meses (`2021-01` a `2025-12`) en `data/oro/serie_mensual_oro_60m.csv` y entrenar los 4 modelos de pronóstico (`SES`, `Holt`, `Holt-Winters`, `SARIMA`) superando el criterio de ruido blanco en residuos ($p_{\text{Ljung-Box}} > 0.05$) y alcanzando un error $\text{MAPE} < 10\%$ en los 12 meses de prueba (`2025`).

---

## 2. ¿Qué hicimos?

1. **Sincronización y Auditoría de Capturas Reales de GitHub Actions (`2026-11-09` a `2026-11-13`):**
   * Recopilamos los snapshots diarios generados automáticamente en `.github/workflows/captura-bronce.yml` (`captura_diaria_2026-11-09.csv`, `2026-11-10.csv`, `2026-11-11.csv`, `2026-11-13.csv` y sus pares de monitoreo SNIIM) junto con la bitácora `calidad/bitacora_capturas.jsonl`, calculando las métricas reales de fiabilidad ($\text{MTBF} = 92.30\text{ h}$, $\text{MTTR} = 0.30\text{ h}$, Disponibilidad $A = 99.68\%$).
2. **Construcción de la Puerta de Calidad Automática (`pipeline/puerta_calidad.py`):**
   * Implementamos contratos de datos con `Pandera` (`DataFrameSchema`) y 4 reglas de negocio citrícolas (`RN-01` coherencia térmica $T_{\max} \ge T_{\text{med}} \ge T_{\min}$, `RN-02` orden de cotizaciones $P_{\max} \ge P_{\text{frec}} \ge P_{\min}$, `RN-03` balance hídrico $P - ET_0$, y `RN-04` catálogos autorizados de municipios INEGI y centrales SNIIM).
   * Auditamos `7,310` registros climáticos y `245` registros de precios; la puerta aprobó `7,304` y `240` registros limpios respectivamente y detuvo los `11` registros defectuosos en `data/cuarentena/cuarentena_registros.csv`.
3. **Limpieza, Imputación, Escalado, Discretización y Reducción en Capa Plata (`pipeline/limpieza_plata.py`):**
   * Evaluamos 4 tratamientos de faltantes bajo mecanismos `MCAR`, `MAR` y `MNAR`, documentando resultados en `data/plata/evaluacion_imputacion_faltantes.csv`.
   * Aplicamos `IQR`, `Z-Score Robusto (MAD)` e `Isolation Forest` (`data/plata/reporte_atipicos_comparativo.csv`), normalización `Min-Max` y `Z-Score` (`data/plata/comparativa_escalado.csv`), discretización de precios y estrés hídrico, jerarquías conceptuales (`data/plata/catalogo_jerarquias_conceptuales.json`) y reducción dimensional (`96.71%` de reducción de filas diarias a mensuales).
4. **Integración en Capa Oro (`pipeline/integracion_oro.py`) y Diccionario de Datos (`data/oro/diccionario_datos.md`):**
   * Resolvimos los conflictos de granularidad temporal y espacial mediante *entity resolution* ponderado por superficie citrícola SIAP (`Tecomán 55%`, `Armería 22%`, `Manzanillo 15%`, `Colima 8%`), produciendo `data/oro/serie_mensual_oro_60m.csv` (`60` meses × `29` variables) y `data/oro/panel_integrado_municipio_mercado_oro.csv` (`240` filas).
5. **Modelado de Series de Tiempo y Tablero (`pipeline/series_tiempo_e1.py` y `tablero/app.py`):**
   * Ejecutamos descomposición multiplicativa, prueba `ADF`, `ACF/PACF`, correlación cruzada (`CCF`) clima-precio, entrenamiento y evaluación de `SES`, `Holt`, `Holt-Winters` y `SARIMA` en prueba (`2025`), diagnóstico `Ljung-Box` y pronóstico `2026` con IC al `95%`.

---

## 3. ¿Qué decidimos y por qué?

* **Decisión 1 — Conservar y etiquetar los picos de precio de febrero-marzo 2022 y febrero 2024 en lugar de eliminarlos como atípicos:**
  * *Por qué:* Los tres detectores (`IQR`, `MAD` e `Isolation Forest`) marcaron febrero y marzo de 2022 (`$46.63` y `$45.48 MXN/kg` en origen Colima) como valores extremos ($Z_{\text{MAD}} > 4.9$). Sin embargo, no son errores de captura sino choques reales de escasez invernal en la cuenca del Pacífico. Eliminarlos o recortarlos (*winsorizing* agresivo) habría destruido la amplitud estacional de febrero-marzo que el productor necesita prever. Por ello se conservaron con la bandera `es_choque_legitimo_dominio = True` (registrado en **Defecto #6**).
* **Decisión 2 — Seleccionar Imputación por Interpolación Temporal para series longitudinales e Imputación KNN ($k=5$) para variables físicas acopladas:**
  * *Por qué:* En el experimento controlado (`data/plata/evaluacion_imputacion_faltantes.csv`), la eliminación por lista introdujo un sesgo de media de `-1.3357 MXN/kg` bajo mecanismo `MNAR` y rompió la frecuencia regular mensual requerida por `SARIMA`. La imputación por mediana subestimó la desviación estándar ($\Delta\sigma = -0.5778\text{ MXN/kg}$). En cambio, `KNNImputer (k=5)` redujo el RMSE en `MAR` (`ET0`) a `0.1598 mm` (vs. `0.7330 mm` de la mediana) y la interpolación lineal logró un RMSE de `1.8819 MXN/kg` en precios (vs. `15.6579 MXN/kg` de la mediana).
* **Decisión 3 — Esquema Multiplicativo y Transformación Logarítmica en `SARIMA(1,1,0)(1,1,0)_12`:**
  * *Por qué:* La oscilación estacional del limón es proporcional al nivel medio del precio (+55.4% en febrero, -25.8% en julio). Modelar sobre $\log(Y_t)$ estabilizó la varianza residual (**Defecto #7**), reduciendo el MAPE en prueba (`2025`) a **`3.04%`** (`MAE = 0.89 MXN/kg`, `RMSE = 1.23 MXN/kg`), superando ampliamente a `Holt-Winters` (`MAPE = 6.66%`), `SES` (`21.74%`) y `Holt` (`24.22%`).

---

## 4. ¿Qué salió mal y cómo lo corregimos?

1. **Incidente Operativo Real en GitHub Actions (`2026-11-12`, Run `#43289949095`, Defecto #5):**
   * *Qué salió mal:* La ejecución programada diaria del 12 de noviembre falló con `requests.exceptions.ReadTimeout` al consultar `api.open-meteo.com`.
   * *Causa raíz:* El método `ExtractorEtico.get()` en `extractores/base.py` sólo reintentaba cuando recibía un código de estado HTTP `429` o `5xx`, pero no envolvía la llamada `self.session.get()` en un bloque `try/except (requests.exceptions.Timeout, requests.exceptions.ConnectionError)`.
   * *Corrección:* En 18 minutos (`MTTR = 0.30 h`) actualizamos `extractores/base.py` para capturar excepciones de *timeout* y conexión dentro del ciclo de *backoff* exponencial ($1.5 \times 2^i\text{ s}$) y añadimos una prueba unitaria específica en `tests/test_extractor_etico.py`. La ejecución del 13 de noviembre (`2026-11-13T19:02:56Z`) finalizó con éxito al `100%`.
2. **Heterocedasticidad inicial en los residuos del modelo ARIMA directo sobre nivel (Defecto #7):**
   * *Qué salió mal:* El primer ajuste de `SARIMA` directamente sobre el precio en nivel mostraba residuos grandes en el choque de 2022 que distorsionaban los intervalos de confianza.
   * *Corrección:* Se aplicó estabilización de varianza logarítmica $\log(Y_t)$ con corrección insesgada al re-exponenciar, obteniendo residuos con ruido blanco verificado por **Ljung-Box** ($Q(6) = 2.48, p = 0.8706$; $Q(12) = 8.11, p = 0.7767 > 0.05$).

---

## 5. ¿Qué aprendimos?

* Aprendimos en la práctica por qué **una puerta de calidad no debe borrar filas silenciosamente**: conservar los 11 registros rechazados en `data/cuarentena/cuarentena_registros.csv` con la regla violada (`RN-01_COHERENCIA_TERMICA`, `RN-02_ORDEN_PRECIOS`, `RANGO_TEMP_MAX`, etc.) nos permitió auditar qué tipo de fallas provienen de sensores (`-99.9 °C`) y cuáles de errores de captura comercial.
* Comprobamos estadísticamente con la **Función de Correlación Cruzada (`CCF`)** que el déficit hídrico y el régimen térmico en Tecomán anteceden a los movimientos del precio del limón entre $k = 0$ y $k = 3$ meses ($|r| > 0.253$, significativo al $95\%$), confirmando que la fisiología de floración y estrés hídrico del árbol de limón mexicano explica el ciclo estacional de precios mayoristas.

---

## 6. Evidencias y Declaración de Uso de IA Generativa

### 6.1 Enlaces a Evidencias en el Repositorio

* **Puerta de Calidad y Cuarentena:** `pipeline/puerta_calidad.py`, `data/cuarentena/cuarentena_registros.csv` y `data/cuarentena/reporte_puerta_calidad.json`.
* **Limpieza e Imputación en Capa Plata:** `pipeline/limpieza_plata.py`, `data/plata/agroclima_mensual_plata.csv`, `data/plata/precios_sniim_mensual_plata.csv`, `data/plata/evaluacion_imputacion_faltantes.csv`, `data/plata/reporte_atipicos_comparativo.csv` y `data/plata/comparativa_escalado.csv`.
* **Integración y Diccionario en Capa Oro:** `pipeline/integracion_oro.py`, `data/oro/serie_mensual_oro_60m.csv`, `data/oro/panel_integrado_municipio_mercado_oro.csv` y `data/oro/diccionario_datos.md`.
* **Series de Tiempo, Pronóstico y Figuras:** `pipeline/series_tiempo_e1.py`, `data/oro/comparativa_modelos_pronostico_e1.csv`, `data/oro/pronostico_e1_limon.csv`, `docs/E1/limpieza.ipynb` y `docs/E1/figuras/fig1..fig5.png`.
* **Calidad, PSP e Integración Continua:** `docs/plan-sqa.md`, `calidad/tiempo-norberto.csv`, `calidad/defectos-norberto.csv`, `calidad/bitacora_capturas.jsonl` y `.github/workflows/ci-calidad.yml`.

### 6.2 Declaración Transparente de Uso de IA Generativa

Durante el desarrollo de la Etapa E1 se utilizó asistencia de inteligencia artificial generativa como copiloto de ingeniería para:
1. Estructurar la plantilla de contratos `Pandera` en `pipeline/puerta_calidad.py` y el formateo de subgráficas en `matplotlib` (`docs/E1/figuras/`).
2. Automatizar la generación de pruebas unitarias de regresión en `tests/test_e1_limpieza_puerta.py` y `tests/test_e1_series_tiempo.py`.
3. Todas las decisiones de dominio citrícola (umbrales de precios en Colima, conservación de los choques de 2022/2024, ponderadores SIAP por municipio y selección del orden `SARIMA(1,1,0)(1,1,0)_12`), así como los cálculos numéricos y bitácoras PSP, fueron verificados y ejecutados de manera determinista sobre los datos reales del repositorio.
