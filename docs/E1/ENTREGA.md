# Ficha Oficial de Entrega — Etapa E1 (`[E1] Trusted Data Lab: Capa Plata, Limpieza, Puerta de Calidad y Pronóstico`)

## 1. Datos de Identificación del Proyecto

| Campo | Detalle |
| :--- | :--- |
| **Nombre del Proyecto** | **CITRO-DATA LAB COLIMA:** Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano en Colima |
| **Modalidad** | Individual (Alcance completo de equipo de 1 integrante) |
| **Estudiante** | **Norberto Daniel Escareño Montaño** (`No. Control: 23460323` · Correo: `23460323@colima.tecnm.mx`) |
| **Usuario de GitHub** | [`@NorbertoDaniel65`](https://github.com/NorbertoDaniel65) |
| **Repositorio Oficial** | [`https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima`](https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima) |
| **Etiqueta Git de Entrega** | [`e1`](https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima/releases/tag/e1) (anterior: [`e0`](https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima/releases/tag/e0)) |
| **Materias Integradas** | 1. **Ingeniería de Datos (`CMD-2602`)** — Mtro. Armando Román Gallardo Heredia (`armando.gallardo@colima.tecnm.mx`, `@ArmandoRomanG`)<br>2. **Análisis Estadístico para Ciencia de Datos** — Mtro. Mónico Joel Sánchez Velasco (`joel.sanchez@colima.tecnm.mx`) |
| **Fecha de Entrega E1** | 13 de noviembre de 2026 |

---

## 2. Tabla de Evidencias por Criterio de Rúbrica E1

### 2.1 Materia 1 — Ingeniería de Datos (Unidad 3: Preprocesamiento, Limpieza, Integración y Puerta de Calidad)

| Criterio de Evaluación (Ponderación) | Artefacto / Archivo de Evidencia en el Repositorio | Resumen de Cumplimiento Cuantitativo |
| :--- | :--- | :--- |
| **1. Valores faltantes: diagnóstico MCAR, MAR, MNAR y sesgo de imputación (15%)** | • Código: `pipeline/limpieza_plata.py`<br>• Tabla de sesgo: `data/plata/evaluacion_imputacion_faltantes.csv`<br>• Muestra Bronce: `data/bronce/muestra_diagnostico_faltantes_bronce.csv`<br>• Notebook: `docs/E1/limpieza.ipynb` (Sección 2) | Se diagnosticaron estadísticamente los 3 mecanismos (`MCAR` en radiación solar $p=0.785$, `MAR` en $ET_0$ bajo lluvia $>12\text{ mm}$ $p<0.001$, y `MNAR` en precios $>P_{80}$ $p<0.001$). Se compararon 4 tratamientos (`Eliminación por lista`, `Mediana`, `Interpolación Temporal`, `KNNImputer k=5`) midiendo $\Delta\mu$, $\Delta\sigma$, MAE y RMSE. `0` valores nulos en Capa Plata y Oro. |
| **2. Atípicos y ruido: IQR, Z-Score Robusto (MAD) e Isolation Forest (15%)** | • Código: `pipeline/limpieza_plata.py`<br>• Reporte comparativo: `data/plata/reporte_atipicos_comparativo.csv`<br>• Figura: `docs/E1/figuras/fig1_puerta_calidad_y_limpieza.png` | Se aplicaron los 3 métodos sobre precios SNIIM y clima Open-Meteo. Decisión documentada por tipo: el ruido de sensor (`-99.9 °C`, lluvias negativas) se bloquea en cuarentena, mientras que los **choques reales de escasez citrícola (feb-mar 2022 con `$46.63 MXN/kg` y feb 2024 con `$36.44 MXN/kg`) se conservan y etiquetan** (`es_choque_legitimo_dominio=True`). |
| **3. Normalización, estandarización, discretización, jerarquías y reducción (15%)** | • Escalado: `data/plata/comparativa_escalado.csv`<br>• Jerarquías: `data/plata/catalogo_jerarquias_conceptuales.json`<br>• Reducción: `data/plata/metricas_reduccion_datos.json`<br>• Datos Plata: `data/plata/agroclima_mensual_plata.csv`, `data/plata/precios_sniim_mensual_plata.csv` | Comparación estadística antes/después de **Min-Max $[0,1]$** y **Z-Score ($\mu=0,\sigma=1$)**. Discretización en `rango_precio_limon`, `nivel_estres_hidrico` y `categoria_termica`. Jerarquías geográfica, comercial, de producto y fenológica. Reducción por agregación (`7,304` filas diarias $\to$ `240` mensuales $\to$ `60` en serie maestra Oro = **`96.71%` a `99.18%` de reducción**) y eliminación de colinealidades ($r=0.994$). |
| **4. Integración de fuentes en Capa Oro y Diccionario de Datos (20%)** | • Código: `pipeline/integracion_oro.py`<br>• Serie Oro: `data/oro/serie_mensual_oro_60m.csv`<br>• Panel Oro: `data/oro/panel_integrado_municipio_mercado_oro.csv`<br>• Diccionario: `data/oro/diccionario_datos.md`<br>• Conflictos: `data/oro/resolucion_conflictos_integracion.json` | Resolución de 4 conflictos entre `Open-Meteo` y `SNIIM`: granularidad temporal (diaria vs. mensual), resolución de entidades espaciales (*entity resolution* con pesos SIAP de superficie citrícola: Tecomán `55%`, Armería `22%`, Manzanillo `15%`, Colima `8%`), estandarización de unidades (`_c`, `_mm`, `_mxn_kg`, `_ton`) y zona horaria (`America/Mexico_City`). |
| **5. Puerta de calidad automática y cuarentena (25%)** | • Código: `pipeline/puerta_calidad.py`<br>• Cuarentena consolidada: `data/cuarentena/cuarentena_registros.csv`<br>• Reporte JSON: `data/cuarentena/reporte_puerta_calidad.json`<br>• Pruebas: `tests/test_e1_limpieza_puerta.py` | Validación automática con esquemas `Pandera` y reglas `RN-01` a `RN-04` antes de pasar de Bronce a Plata. De `7,555` registros auditados, `7,544` pasaron a Capa Plata y **`11` registros inválidos fueron detenidos y enviados a `data/cuarentena/` con regla violada, severidad y motivo (`0` registros eliminados en silencio)**. |

---

### 2.2 Materia 2 — Análisis Estadístico para Ciencia de Datos (Unidad 3: Series de Tiempo y Pronóstico)

| Criterio de Evaluación (Ponderación) | Artefacto / Archivo de Evidencia en el Repositorio | Resumen de Resultados Estadísticos |
| :--- | :--- | :--- |
| **1. Caracterización y descomposición de la serie histórica (15%)** | • Código: `pipeline/series_tiempo_e1.py`<br>• Figura: `docs/E1/figuras/fig2_descomposicion_serie_60m.png`<br>• Resumen JSON: `data/oro/diagnostico_series_tiempo_e1.json` | Serie mensual de `60` observaciones (`2021-01` a `2025-12`). Se justificó la **descomposición multiplicativa ($Y_t = T_t \times S_t \times R_t$)** porque la amplitud estacional escala con el nivel del precio: factor estacional máximo en **febrero ($S_{\text{feb}} = 1.554$, $+55.4\%$)** por escasez invernal y mínimo en **julio ($S_{\text{jul}} = 0.742$, $-25.8\%$)** por cosecha de verano. |
| **2. Estacionariedad (ADF), ACF/PACF y Correlación Cruzada CCF (15%)** | • Figura: `docs/E1/figuras/fig3_estacionariedad_acf_pacf_ccf.png`<br>• Tabla CCF: `data/oro/correlacion_cruzada_clima_precio_e1.csv`<br>• Notebook: `docs/E1/limpieza.ipynb` (Sección 4) | • **ADF en nivel ($Y_t$):** $\tau = -3.8617, p = 0.0023 < 0.05$.<br>• **ADF en 1ª diferencia ($\Delta Y_t$):** $\tau = -5.7720, p = 5.36 \times 10^{-7}$ (fuertemente estacionaria).<br>• **ACF y PACF:** Inercia autorregresiva en rezago $k=1$ ($r_1 = 0.713$) y ciclo anual en rezago $k=12$ ($r_{12} = 0.612$).<br>• **CCF Clima $\to$ Precio:** Correlación cruzada estadísticamente significativa al $95\%$ ($|r| > 0.253$) entre déficit hídrico / precipitación / temperatura en Tecomán y el precio del limón en rezagos $k = 0..3$ meses. |
| **3. Cuatro modelos de pronóstico justificados (25%)** | • Código: `pipeline/series_tiempo_e1.py`<br>• Selección AIC: `data/oro/seleccion_orden_sarima_aic.csv`<br>• Comparativa: `data/oro/comparativa_modelos_pronostico_e1.csv` | Se ajustaron los 4 modelos requeridos sobre los `48` meses de entrenamiento (`2021-01` a `2024-12`):<br>1. **SES** ($\alpha = 0.995$)<br>2. **Holt Lineal** ($\alpha = 0.65, \beta = 0.18$)<br>3. **Holt-Winters Estacional Multiplicativo** ($m=12$)<br>4. **SARIMA$(1,1,0)(1,1,0)_{12}$ sobre $\log(Y_t)$** justificado por cortes en PACF (lags 1 y 12) y criterio AIC (`-31.95`). |
| **4. Selección de modelo por error en prueba (Hold-out 12 meses: 2025) (20%)** | • Tabla oficial: `data/oro/comparativa_modelos_pronostico_e1.csv`<br>• Figura: `docs/E1/figuras/fig4_comparativa_4_modelos_test.png` | Evaluación en los `12` meses de prueba (`2025-01` a `2025-12`):<br>• **#1 Ganador — `SARIMA(1,1,0)(1,1,0)_12 [log]`:** `MAE = 0.89 MXN/kg`, `RMSE = 1.23 MXN/kg`, **`MAPE = 3.04%`**.<br>• **#2 `Holt-Winters (m=12)`:** `MAE = 2.19`, `RMSE = 3.64`, `MAPE = 6.66%`.<br>• **#3 `SES`:** `MAE = 5.72`, `RMSE = 6.84`, `MAPE = 21.74%`.<br>• **#4 `Holt`:** `MAE = 6.43`, `RMSE = 7.47`, `MAPE = 24.22%`. |
| **5. Análisis de residuos (Ljung-Box) y pronóstico 2026 con IC 95% (15%)** | • Pronóstico CSV: `data/oro/pronostico_e1_limon.csv`<br>• Figura: `docs/E1/figuras/fig5_pronostico_final_ic95_residuos.png`<br>• Tablero: `tablero/app.py` | • **Prueba de Ljung-Box:** $Q(6) = 2.482$ ($p = 0.8706 > 0.05$) y $Q(12) = 8.113$ ($p = 0.7767 > 0.05$) $\implies$ los residuos son **ruido blanco** sin autocorrelación remanente.<br>• **Pronóstico 2026 con IC 95%:** Publicado en `data/oro/pronostico_e1_limon.csv` y en `tablero/app.py` con recomendaciones comerciales en lenguaje llano para el productor citrícola. |

---

### 2.3 Calidad del Sistema, PSP, Integración Continua y Relatoría

| Criterio | Archivo de Evidencia | Resultado |
| :--- | :--- | :--- |
| **Fiabilidad Real (MTBF, MTTR, Disponibilidad)** | `docs/plan-sqa.md` y `calidad/bitacora_capturas.jsonl` | $\text{MTBF} = 92.30\text{ h}$, $\text{MTTR} = 0.30\text{ h}$ (`18 min`), **Disponibilidad $A = 99.68\%$** ($\ge 95\%$ meta O1). |
| **Plan SQA (IEEE 730) y Requerimientos Verificables** | `docs/plan-sqa.md` | 6 secciones IEEE 730 + matriz de 7 requerimientos verificables (`REQ-E1-01` a `REQ-E1-07`) + auditoría de `0` secretos expuestos. |
| **Bitácoras PSP Actualizadas (E0 + E1)** | `calidad/tiempo-norberto.csv` y `calidad/defectos-norberto.csv` | `11` sesiones de trabajo registradas y `7` defectos documentados y cerrados antes de la entrega (`100%` eliminados en revisión/pruebas). |
| **Integración Continua (GitHub Actions)** | `.github/workflows/ci-calidad.yml` y `.github/workflows/captura-bronce.yml` | Ejecución automática de `pytest`, `pipeline/verificar_e0.py` y `pipeline/verificar_e1.py` en cada `push`. |
| **Relatoría de Etapa E1 (6 preguntas + uso de IA)** | `docs/relatoria-E1.md` | Respuestas completas en orden a las 6 preguntas guía y declaración transparente del uso de IA generativa. |

---

## 3. Instrucciones de Reproducción Determinista

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar Puerta de Calidad, Limpieza Plata, Integración Oro y Series de Tiempo E1
python -m pipeline.series_tiempo_e1

# 3. Ejecutar suite completa de pruebas automatizadas y verificador E1
pytest -v
python -m pipeline.verificar_e1

# 4. Iniciar el tablero interactivo con el pronóstico e IC 95%
streamlit run tablero/app.py
```
