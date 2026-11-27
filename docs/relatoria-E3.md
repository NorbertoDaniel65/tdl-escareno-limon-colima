# Relatoría E3 · CITRO-DATA LAB COLIMA

**Equipo:** Norberto Daniel Escareño Montaño (`No. Control: 23460323` · `@NorbertoDaniel65` · modalidad individual) · **Periodo:** `2026-11-23` a `2026-11-27`

---

## 1. Qué nos propusimos

En la Etapa **E3** nos propusimos tres objetivos medibles que cierran el ciclo técnico del observatorio antes del Demo Day: **(1)** aplicar en producción la configuración ganadora del experimento factorial $2^3$ (`4 hilos + Pandera vectorizado + Apache Parquet Snappy/ZSTD`) logrando al menos `5×` de reducción de tiempo y `>80%` de ahorro en disco, y publicar el dataset curado de Capa Oro con licencia abierta **CC BY 4.0** y su ficha técnica estandarizada (*Datasheet for Datasets*); **(2)** construir la matriz multivariada de rango completo ($p=8$ variables bioclimáticas en $g=4$ municipios de Colima y $p=5$ variables comerciales en $g=4$ mercados nacionales, $N=240$), evaluar la normalidad multivariada (Mardia, Henze-Zirkler y Q-Q de Mahalanobis con Puerta 3), reducir dimensiones con **PCA** (nombrando cada componente para el negocio citrícola y proyectando el Mapa Multivariado en el tablero) y contrastar simultáneamente los grupos con **MANOVA** ($\Lambda$ de Wilks y Traza de Pillai); y **(3)** cerrar al `100%` los hallazgos de auditoría (`0` críticos abiertos), autoevaluar el proceso frente a **MoProSoft** y **CMMI**, realizar la retrospectiva cuantitativa **PSP (`E0→E3`)** y acreditar los **`6/6` criterios del Sello TDL**.

---

## 2. Qué hicimos (cronología con fechas, responsable y horas)

De acuerdo con las 6 sesiones de la Etapa `E3` registradas en [`calidad/tiempo-norberto.csv`](../calidad/tiempo-norberto.csv) (`735 min = 12.25 horas netas` en `E3`; acumulado total del proyecto `E0–E3`: `22` sesiones, `2,725 min = 45.42 horas netas`):

| Fecha | Horario | Minutos Netos (Interrupción) | Fase PSP | Responsable | Actividad Realizada y Artefacto Generado |
| :---: | :---: | :---: | :---: | :---: | :--- |
| `2026-11-23` | `16:30–18:30` | `110 min` (`10m`) | `planeacion` | Norberto Escareño (`23460323`) | Diseño de la matriz multivariada de rango completo ($p=8$ variables agroclimáticas y $p=5$ comerciales), plan de cierre de los 5 hallazgos `AUD-01..AUD-05` y estructura del *Datasheet* (Gebru et al., 2021). |
| `2026-11-24` | `17:00–19:15` | `125 min` (`10m`) | `diseno` | Norberto Escareño (`23460323`) | Formulación matemática de las pruebas de Mardia ($b_{1,p}, b_{2,p}$), Henze-Zirkler ($HZ$), distancias de Mahalanobis ($D_i^2$), transformación Yeo-Johnson (Puerta 3), PCA y MANOVA (detección del **Defecto #11** en revisión). |
| `2026-11-25` | `15:30–18:15` | `150 min` (`15m`) | `codigo` | Norberto Escareño (`23460323`) | Rediseño integral del tablero Streamlit (`tablero/app.py`) sin barra lateral con paleta costera de Colima (`#304C53`, `#BC6C50`, `#DDAD9C`, `#5A2F25`, `#AFE0E7`), logotipo y corrección del **Defecto #12** (formato D3 `$.2f`). |
| `2026-11-26` | `16:00–18:45` | `155 min` (`10m`) | `codigo` | Norberto Escareño (`23460323`) | Implementación de `pipeline/optimizacion_dataset_e3.py`, `pipeline/multivariado_pca_manova_e3.py`, `pipeline/calidad_sello_e3.py` y corrección del **Defecto #13** (`import pandera.pandas as pa`). |
| `2026-11-27` | `10:00–12:30` | `140 min` (`10m`) | `revision` | Norberto Escareño (`23460323`) | Revisión de código y cierre de auditoría (`5/5` hallazgos), autoevaluación MoProSoft/CMMI, retrospectiva PSP `E0→E3`, documento de tendencias (`DataOps` + `ISO/IEC 42001`) y `docs/E3/datasheet.md`. |
| `2026-11-27` | `13:30–16:00` | `145 min` (`5m`) | `pruebas` | Norberto Escareño (`23460323`) | Generación de 5 figuras HD (`pipeline/figuras_e3.py`), notebooks reproducibles, integración del Mapa Multivariado y Sello TDL en `tablero/app.py`, suite `pytest` (`35/35` pruebas), `verificar_e3.py` y reporte PDF TecNM. |

---

## 3. Qué decidimos y por qué (alternativas descartadas)

1. **Vector de $p = 8$ variables bioclimáticas linealmente independientes vs. incluir variables derivadas colineales:**
   - *Decisión:* Seleccionamos las 8 variables físicas primarias linealmente independientes (`temp_max_promedio_c`, `temp_min_promedio_c`, `dias_estres_termico_35c`, `precipitacion_acum_mm`, `evapotranspiracion_acum_mm`, `gdd_acumulado_mes`, `viento_max_extremo_kmh`, `radiacion_media_mj_m2`) con rango matricial completo $\text{rank}(\mathbf{S}) = 8$.
   - *Alternativa descartada:* Incluir simultáneamente `deficit_hidrico_acum_mm = P - ET0` y `amplitud_termica = Tmax - Tmin` junto con sus componentes. Se descartó en la revisión de diseño (**Defecto #11**) porque una combinación lineal exacta hace singular la matriz de covarianzas ($\det(\mathbf{S}) = 0$), invalidando la inversión exacta $\mathbf{S}^{-1}$ en las distancias de Mahalanobis y en la matriz $\mathbf{E}^{-1}\mathbf{H}$ del MANOVA.

2. **Cumplimiento riguroso de la Puerta 3 ante asimetría pluvial tropical (Transformación Yeo-Johnson + Traza de Pillai + MANOVA por Permutación):**
   - *Decisión:* Dado que la precipitación estacional en Colima presenta meses secos con $0\text{ mm}$ y lluvias ciclónicas en verano, la prueba de Mardia en escala cruda rechaza normalidad ($b_{1,p} = 43.89, HZ = 2.882$). En lugar de publicar un MANOVA paramétrico ciego, aplicamos la **Puerta 3**: transformamos con **Yeo-Johnson** (logrando normalidad en curtosis multivariada de Mardia con $Z = -1.35, p = 0.178 > 0.05$ y elevando el ajuste Q-Q de Mahalanobis de $r = 0.8422$ a **$r = 0.9986$** con `96.67%` dentro de $\chi^2_{8, 0.95}$) y respaldamos el contraste con la **Traza de Pillai** y un **MANOVA no paramétrico de $1,000$ permutaciones** ($p = 0.000999$).
   - *Alternativa descartada:* Ignorar la asimetría o eliminar los meses de tormentas tropicales. Se descartó porque borrar lluvias reales destruiría el fenómeno bioclimático que explica la cosecha pico de limón.

3. **Persistencia dual en Capa Oro (`Apache Parquet ZSTD/Snappy` + espejo `CSV UTF-8`):**
   - *Decisión:* Publicamos el dataset maestro `CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1` y las tablas de Capa Oro en **Apache Parquet (`ZSTD` y `Snappy`)** para consumo analítico de alta velocidad (`12.15×` speedup, `-87.31%` disco) manteniendo en paralelo el archivo `.csv` con su hash `SHA-256`.
   - *Alternativa descartada:* Eliminar por completo los archivos CSV. Se descartó para garantizar que cualquier productor, docente o auditor pueda inspeccionar los datos directamente en GitHub o Excel sin herramientas adicionales.

---

## 4. Qué salió mal y cómo lo corregimos (con número de defecto)

En [`calidad/defectos-norberto.csv`](../calidad/defectos-norberto.csv) se documentaron y cerraron **3 defectos reales en `E3`** (`#11`, `#12` y `#13`; **todos detectados y eliminados en la fase de `revision` antes de pruebas, logrando `Yield = 100.0%`**):

- **Defecto `#11` (`2026-11-24`, tipo `datos`, introducido en `diseno`, eliminado en `revision`, `14 min`):** En el diseño preliminar de la matriz multivariada se incluyó `deficit_hidrico_acum_mm` ($P - ET_0$) junto a `precipitacion_acum_mm` ($P$) y `evapotranspiracion_acum_mm` ($ET_0$). Al revisar el condicionamiento de la matriz de covarianzas $\mathbf{S}$, se detectó colinealidad exacta ($\det(\mathbf{S}) \approx 0$). *Corrección:* Se depuró el vector a las $p = 8$ variables continuas linealmente independientes verificando $\text{rank}(\mathbf{S}) = 8$.
- **Defecto `#12` (`2026-11-25`, tipo `interfaz`, introducido en `codigo`, eliminado en `revision`, `8 min`):** Al rediseñar el tablero Streamlit (`tablero/app.py`), un tooltip de Altair/Vega-Lite tenía formato estilo `printf` (`format="$%.2f"`), lo que disparaba `Error: invalid format: $%.2f` en la consola JavaScript del navegador. *Corrección:* Se estandarizó a sintaxis D3 (`format="$.2f"`), verificando `0` errores en consola en las pestañas del tablero.
- **Defecto `#13` (`2026-11-26`, tipo `sintaxis`, introducido en `codigo`, eliminado en `revision`, `10 min`, origen `#5` / `AUD-05`):** La importación raíz `import pandera as pa` en `pipeline/puerta_calidad.py` y `pipeline/experimento_doe_e2.py` emitía `FutureWarning` en Pandera $\ge 0.20$. *Corrección:* Se migró a `import pandera.pandas as pa` con bloque `try/except` retrocompatible, cerrando definitivamente el hallazgo de auditoría `AUD-05` con `0` advertencias.

---

## 5. Qué aprendimos

### Ingeniería de Datos
Comprobamos en producción que las conclusiones de un Diseño de Experimentos no deben quedarse en el papel: al llevar el tratamiento ganador `A+B+C+` (`ThreadPoolExecutor` de 4 hilos + validación vectorizada C/NumPy con `pandera.pandas` + escritura columnar `Apache Parquet Snappy/ZSTD`) al pipeline completo en `pipeline/optimizacion_dataset_e3.py`, redujimos el tiempo de ejecución de **`4,253.18 ms` a `349.93 ms` (`12.15×` más rápido, `-91.77%`)**, el pico de memoria RAM de **`2,718.5 KB` a `412.2 KB` (`-84.84%`)** y el volumen en disco en **`-87.31%`** con `0.0%` de errores. Asimismo, redactar el *Datasheet for Datasets* (`docs/E3/datasheet.md`) nos enseñó que publicar datos abiertos de calidad profesional exige declarar con total transparencia no solo cómo se limpiaron, sino también para qué casos de uso **no** deben emplearse.

### Análisis Estadístico
Aprendimos por qué el análisis multivariado revela estructuras que las gráficas univariadas ocultan. Con el **PCA** reducimos 8 variables bioclimáticas a tres índices latentes con sentido directo para el productor citrícola (`PC1` *Estrés Termo-Evaporativo y Calor Citrícola* = `36.08%`, `PC2` *Humedad Pluvial Tropical y Moderación Costera* = `29.75%`, `PC3` *Turbulencia Eólica Costera vs. Valle* = `13.56%`; **`79.39%` de varianza acumulada**). En el Biplot del tablero se observa con claridad cómo **Colima capital** se desplaza hacia el cuadrante de alto calor seco diurno (`PC1 = +0.990`), mientras **Manzanillo y Tecomán** comparten moderación térmica y brisa marítima (`PC3 = +0.422` y `+0.513`). Con el **MANOVA** demostramos diferencias multivariadas contundentes tanto entre los 4 municipios ($\Lambda_{\text{Wilks}} = 0.0706, V_{\text{Pillai}} = 1.3334, p = 6.78 \times 10^{-115}$) como entre las 4 centrales de abasto nacionales ($\Lambda_{\text{Wilks}} = 0.0991, V_{\text{Pillai}} = 0.9088, p = 8.59 \times 10^{-106}$), evitando la inflación del **`33.66%` en la tasa de Error Tipo I global** ($1 - 0.95^8$) en la que caeríamos si corriéramos 8 ANOVAs separados.

### Calidad en los Sistemas de Información
Aprendimos a cerrar el ciclo completo de aseguramiento de calidad conectando normas de producto/datos (**ISO/IEC 25010 y 25012**) con modelos de capacidad y madurez de procesos (**MoProSoft `NMX-I-059-NYCE`**, **CMMI v2.0**, **SPICE `ISO/IEC 33000`**, **ISO 9001** y **PSP/TSP**). La retrospectiva empírica sobre nuestras `22` sesiones (`45.42 h`) y `13` defectos en PSP nos demostró que invertir tiempo en la fase de `revision` elevó nuestro *Yield* de remoción temprana de `0%` en `E1` a **`100.0%` en `E3`** y redujo el costo medio de corrección de `16.0 min` a **`10.67 min`**. Finalmente, integrar prácticas de **DataOps**, **Observabilidad de Datos**, **DevSecOps** y gobernanza **ISO/IEC 42001** nos permitió cumplir con holgura los **`6/6` criterios del Sello TDL** (`99.85%` disponibilidad en los últimos 14 días, `100%` completitud en Capa Oro, `88.4%` cobertura de pruebas, `0` secretos expuestos, `0` hallazgos críticos abiertos y `100%` reproducibilidad).

---

## 6. Evidencias (enlaces a commits, notebooks y capturas)

* **Módulos de código E3:** [`pipeline/optimizacion_dataset_e3.py`](../pipeline/optimizacion_dataset_e3.py), [`pipeline/multivariado_pca_manova_e3.py`](../pipeline/multivariado_pca_manova_e3.py), [`pipeline/calidad_sello_e3.py`](../pipeline/calidad_sello_e3.py), [`pipeline/figuras_e3.py`](../pipeline/figuras_e3.py), [`pipeline/verificar_e3.py`](../pipeline/verificar_e3.py).
* **Dataset publicado y Datasheet:** [`data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet`](../data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet), [`data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.csv`](../data/oro/CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.csv), [`data/oro/dataset_publicado_e3_manifest.json`](../data/oro/dataset_publicado_e3_manifest.json) y [`docs/E3/datasheet.md`](E3/datasheet.md).
* **Artefactos multivariados y de calidad en Capa Oro:** [`data/oro/resumen_multivariado_e3.json`](../data/oro/resumen_multivariado_e3.json), [`data/oro/pca_proyecciones_municipios_mercados_e3.csv`](../data/oro/pca_proyecciones_municipios_mercados_e3.csv), [`data/oro/manova_resultados_e3.csv`](../data/oro/manova_resultados_e3.csv), [`data/oro/comparativa_manova_vs_anovas_e3.csv`](../data/oro/comparativa_manova_vs_anovas_e3.csv), [`data/oro/resumen_optimizacion_e3.json`](../data/oro/resumen_optimizacion_e3.json), [`data/oro/resumen_calidad_sello_e3.json`](../data/oro/resumen_calidad_sello_e3.json) y [`docs/calidad-modelos-psp-sello-e3.md`](calidad-modelos-psp-sello-e3.md).
* **Notebooks reproducibles:** [`docs/E3/analisis_multivariado_y_optimizacion.ipynb`](E3/analisis_multivariado_y_optimizacion.ipynb) y [`laboratorio/e3_pca_manova_optimizacion_sello.ipynb`](../laboratorio/e3_pca_manova_optimizacion_sello.ipynb).
* **5 Figuras HD de la Etapa E3:**
  1. [`docs/E3/figuras/fig1_matriz_correlaciones_y_qq_mahalanobis_e3.png`](E3/figuras/fig1_matriz_correlaciones_y_qq_mahalanobis_e3.png)
  2. [`docs/E3/figuras/fig2_pca_sedimentacion_y_biplot_municipios_e3.png`](E3/figuras/fig2_pca_sedimentacion_y_biplot_municipios_e3.png)
  3. [`docs/E3/figuras/fig3_manova_municipios_mercados_vs_anovas_e3.png`](E3/figuras/fig3_manova_municipios_mercados_vs_anovas_e3.png)
  4. [`docs/E3/figuras/fig4_optimizacion_pipeline_antes_despues_e3.png`](E3/figuras/fig4_optimizacion_pipeline_antes_despues_e3.png)
  5. [`docs/E3/figuras/fig5_retrospectiva_psp_modelos_y_sello_tdl_e3.png`](E3/figuras/fig5_retrospectiva_psp_modelos_y_sello_tdl_e3.png)
* **Reporte Ejecutivo Oficial PDF (Molde TecNM):** [`docs/E3/Entrega_E3_Escareno_Norberto.pdf`](E3/Entrega_E3_Escareno_Norberto.pdf).

---

## Uso de IA generativa (herramienta y para qué)

En cumplimiento de las reglas de transparencia académica del proyecto y de nuestro marco de gobernanza **ISO/IEC 42001:2023**, se declara el uso de **Antigravity (Google DeepMind / Gemini)** como asistente de ingeniería de software y visualización para: **(1)** generación del logotipo vectorial del observatorio (`tablero/assets/logo_citrodata.png`) y estilizado CSS responsivo del tablero Streamlit sin barra lateral con la paleta costera de Colima; **(2)** estructuración modular de los scripts de benchmark con `tracemalloc`, cálculo matricial de las pruebas de Mardia y Henze-Zirkler, y generación de gráficas con `Matplotlib` y `Altair`; y **(3)** revisión ortotipográfica de la documentación técnica (`datasheet.md`, `calidad-modelos-psp-sello-e3.md` y maquetación HTML→PDF en molde oficial TecNM). Todas las decisiones estadísticas, selección de variables linealmente independientes, ejecución real de benchmarks, interpretación agronómica y validación de pruebas `pytest` fueron verificadas determinísticamente sobre los datos reales del repositorio.
