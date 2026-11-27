# Datasheet for Datasets · CITRO-DATA LAB COLIMA (Capa Oro v3.0 · Entrega E3)

**Estándar de referencia:** *Datasheets for Datasets* (Gebru et al., *Communications of the ACM*, 2021)  
**Identificador del Dataset:** `tdl-colima-limon-oro-v3.0-e3`  
**Autor y Curador:** Norberto Daniel Escareño Montaño (`No. Control: 23460323` · `@NorbertoDaniel65`)  
**Institución:** Tecnológico Nacional de México — Instituto Tecnológico de Colima  
**Licencia Abierta de Publicación:** **Creative Commons Attribution 4.0 International (`CC BY 4.0`)**  
**Fecha de Publicación:** 27 de noviembre de 2026 · **Etiqueta Git:** `e3`

---

## 1. Motivación (*Motivation*)

1. **¿Con qué propósito se creó este conjunto de datos?**  
   Se creó como activo central certificado de la **Capa Oro** del observatorio **CITRO-DATA LAB COLIMA** dentro del Proyecto Integrador Colegiado *Trusted Data Lab*. Su propósito es cerrar la brecha de asimetría de información que enfrentan productores, cooperativas y empacadoras de **limón mexicano con semilla #5 (*Citrus aurantifolia*)** en el estado de Colima, quienes históricamente negocian precios en báscula con base en rumores sin contar con una base integrada, limpia y verificable que vincule el **estrés agroclimático municipal**, la **infraestructura agrologística georreferenciada** y los **precios mayoristas oficiales en las 4 principales centrales de abasto de México**.

2. **¿Quién creó el dataset y quién financió su creación?**  
   Fue diseñado, extraído, curado, auditado bajo normas **ISO/IEC 25012** y publicado por **Norberto Daniel Escareño Montaño** (`23460323`), estudiante de Ingeniería en Sistemas Computacionales del **TecNM — Instituto Tecnológico de Colima**, bajo la supervisión colegiada del Mtro. Armando Román Gallardo Heredia (*Ingeniería de Datos*), Mtro. Mónico Joel Sánchez Velasco (*Análisis Estadístico para Ciencia de Datos*) y la academia de *Calidad en los Sistemas de Información*. El proyecto opera con infraestructura abierta de costo `$0 USD/mes`.

3. **¿Qué dolor económico concreto resuelve?**  
   Un diferencial de $\$3.00$ a $\$6.00\text{ MXN/kg}$ en un embarque estándar de $20\text{ toneladas}$ equivale a **$\$60,000$ – $\$120,000\text{ MXN}$ por camión**. El dataset permite anticipar con 1 a 3 meses de ventaja el impacto del déficit hídrico ($P - ET_0$) y calor extremo ($\ge 35^\circ\text{C}$) sobre la oferta y el precio mayorista, así como comparar el margen neto hacia Guadalajara, CDMX y Monterrey.

---

## 2. Composición (*Composition*)

1. **¿Qué representan las instancias que componen el dataset?**  
   El paquete publicado en `data/oro/` está compuesto por **cuatro artefactos tabulares y vectoriales sincronizados** (todos en formato columnar optimizado **Apache Parquet ZSTD** y espejo **CSV UTF-8 / GeoJSON**):

| Archivo Publicado en `data/oro/` | Unidad de Análisis (Fila) | Filas ($N$) | Columnas ($p$) | Formato Publicado | Completitud ISO 25012 |
| :--- | :--- | :---: | :---: | :---: | :---: |
| **`CITRO_DATA_LAB_COLIMA_DATASET_ORO_v1.parquet`** *(y `.csv`)* | Municipio citrícola $\times$ Mes con precios en las 4 plazas nacionales e infraestructura OSM | `240` | `64` | Parquet ZSTD (`47.7 KB`) + CSV (`228.5 KB`) | **100.0%** (`0` nulos) |
| **`panel_integrado_municipio_mercado_oro.parquet`** *(y `.csv`)* | Municipio citrícola de Colima (`06001`, `06002`, `06007`, `06009`) $\times$ Mes (`2021-01` a `2025-12`) | `240` | `49` | Parquet ZSTD (`42.8 KB`) + CSV (`195.1 KB`) | **100.0%** (`0` nulos) |
| **`serie_mensual_oro_60m.parquet`** *(y `.csv`)* | Mes calendario (`2021-01` a `2025-12`) agregado para la cuenca citrícola de Colima | `60` | `39` | Parquet ZSTD (`20.4 KB`) + CSV (`31.6 KB`) | **100.0%** (`0` nulos) |
| **`perfil_geoespacial_municipios_oro.parquet`** *(y `.csv` / `.geojson`)* | Municipio del estado de Colima (`06001` a `06010`) con nodos OSM validados y distancias UTM 13N | `10` | `26` | Parquet ZSTD (`8.0 KB`) + CSV (`5.5 KB`) + GeoJSON | **100.0%** (`0` nulos) |

2. **¿Cuáles son los grupos y subpoblaciones incluidos?**  
   - **4 Municipios Citrícolas Núcleo de Colima ($g = 4, n = 60$ meses c/u):** `Tecomán (06009)` ($55\%$ peso productivo SIAP), `Armería (06001)` ($22\%$), `Manzanillo (06007)` ($15\%$) y `Colima (06002)` ($8\%$).  
   - **6 Municipios Vecinos de Contexto Cartográfico en Colima:** `Comala (06003)`, `Coquimatlán (06004)`, `Cuauhtémoc (06005)`, `Ixtlahuacán (06006)`, `Minatitlán (06008)` y `Villa de Álvarez (06010)`.  
   - **4 Centrales de Abasto Mayoristas Nacionales ($g = 4, n = 60$ meses c/u):** `MKT-COL` (Empacadoras origen Colima), `MKT-GDL` (Mercado de Abastos Guadalajara), `MKT-CDMX` (CEDA Iztapalapa) y `MKT-MTY` (Mercado Estrella Monterrey).

3. **¿Contiene información confidencial, sensible o datos personales (PII)?**  
   **No (`0` columnas y `0` registros con datos personales).** Cumple estrictamente con la **LFPDPPP**. Todos los registros geoespaciales pasan por una lista blanca de etiquetas y un filtro regex que bloquea nombres de personas físicas, teléfonos, correos y domicilios particulares antes de tocar la Capa Bronce.

---

## 3. Proceso de Captura y Recolección (*Collection Process*)

1. **¿Cómo se adquirieron los datos de cada fuente primaria?**
   - **Fuente 1 — Open-Meteo Historical Archive & Forecast API (Copernicus ERA5-Land):** Consulta HTTP REST mediante `ExtractorEtico` (`extractores/open_meteo.py`) sobre las coordenadas centroide agrícolas de Tecomán, Armería, Manzanillo y Colima (`7,304` registros diarios continuos `2021-01-01` a `2025-12-31` + snapshots diarios automáticos).
   - **Fuente 2 — SNIIM (Secretaría de Economía) / Serie Histórica Agrícola:** Extracción ética (`extractores/sniim_limon.py`) de cotizaciones mayoristas mensuales y monitoreo periódico de *Limón con semilla #5* en las 4 plazas nacionales (`240` registros mensuales).
   - **Fuente 3 — OpenStreetMap (Nominatim + Overpass API) $\times$ Catálogo INEGI:** Extracción geoespacial (`extractores/geoespacial_osm.py`) de los `10` polígonos municipales de Colima y `1,164` nodos agrologísticos en la caja delimitadora estatal.

2. **¿Qué mecanismos éticos y de gobernanza regularon la captura?**
   - Verificación y archivo local de `robots.txt` en `data/bronce/robots_txt/`.
   - Cabecera identificadora honesta: `TDL-CitroDataLab-Colima/1.0 (Proyecto Academico TecNM-ITColima; Responsable: Norberto Daniel Escareno Montano; Contacto: 23460323@colima.tecnm.mx)`.
   - Control de tasa (*rate-limiting*) con pausa mínima $\ge 1.5\text{ s}$ entre peticiones al mismo dominio y *backoff* exponencial (`pausa * 2**i`) ante códigos HTTP `429/5xx`.
   - Orquestación desatendida mediante GitHub Actions (`.github/workflows/captura-bronce.yml`) con disponibilidad medida en los últimos 14 días de **`99.85%`** (`100.0%` tras el cierre del hallazgo `AUD-01`).

---

## 4. Preprocesamiento, Limpieza y Etiquetado (*Preprocessing, Cleaning & Labeling*)

1. **Puerta de Calidad Automática (`pipeline/puerta_calidad.py` y `pipeline/geoespacial_e2.py`):**
   - Validación vectorizada con contratos `Pandera (pandera.pandas)` y 4 reglas de negocio citrícolas (`RN-01` coherencia térmica $T_{\max} \ge T_{\text{med}} \ge T_{\min}$, `RN-02` orden de precios $P_{\max} \ge P_{\text{frec}} \ge P_{\min}$, `RN-03` balance hídrico $P - ET_0$, `RN-04` catálogos INEGI/SNIIM).
   - **Política de cero borrado silencioso:** Los `11` registros tabulares inválidos del lote de auditoría y los `90` nodos geoespaciales ubicados fuera del límite poligonal de Colima (`gpd.sjoin(..., predicate="within")`) se conservan íntegramente en `data/cuarentena/` con su causa documentada.

2. **Tratamiento de valores faltantes, atípicos y escalado (`pipeline/limpieza_plata.py`):**
   - Diagnóstico formal de mecanismos `MCAR`, `MAR` y `MNAR`; imputación comparada donde la interpolación temporal lineal (`RMSE = 0.67°C`) superó a KNN y mediana.
   - Detección triple de atípicos (`IQR`, `Z-Score robusto MAD` e `Isolation Forest`). Los choques reales de escasez (feb–mar 2022 con $\$46.63\text{ MXN/kg}$ en origen y feb 2024) se **preservan y etiquetan** (`es_choque_legitimo_precio = True`) en lugar de amputarse.
   - Escalado dual (`Min-Max [0,1]` y `Z-Score`) y transformación de potencia **Yeo-Johnson** para normalidad multivariada (**Puerta 3**).

3. **Optimización Medida del Pipeline en E3 (`pipeline/optimizacion_dataset_e3.py`):**
   - La adopción en producción del tratamiento óptimo del DOE $2^3$ (`4 hilos + Pandera vectorizado + Apache Parquet Snappy/ZSTD`) redujo la latencia extremo-a-extremo de **`4,253.18 ms` a `349.93 ms` (`12.15×` más rápido, `-91.77%`)**, el pico de memoria RAM en **`-84.84%`** y el volumen en disco en **`-87.31%`**.

---

## 5. Usos Recomendados y No Recomendados (*Uses*)

### 5.1 Casos de Uso Recomendados
- **Planeación comercial y arbitraje logístico citrícola:** Programación de riegos, cortes y selección de mercado destino (`Colima`, `Guadalajara`, `CDMX`, `Monterrey`) usando el pronóstico SARIMA (`MAPE = 3.04%`) y los diferenciales de precio.
- **Modelado estadístico multivariado y econometría agrícola:** Entrenamiento de modelos de series de tiempo (SARIMAX, Prophet), Análisis de Componentes Principales (`PCA`), `MANOVA` y clasificación de riesgo agroclimático.
- **Planeación territorial y logística en Colima:** Análisis de cobertura de huertas, empaques y distancias métricas (`EPSG:32613`) hacia el Puerto de Manzanillo y el corredor carretero `54D`.

### 5.2 Casos de Uso NO Recomendados
- **Prohibido para fijación colusoria de precios o prácticas monopólicas:** Los datos reflejan precios públicos históricos y pronósticos estadísticos abiertos; no deben usarse para coordinar precios artificiales en perjuicio de consumidores o pequeños productores.
- **No apto para micro-predicción parcelaria sin calibración in-situ:** La malla meteorológica ERA5-Land ($\sim 9\text{ km}$) representa el promedio meso-climático del valle agrícola municipal, por lo que no sustituye sensores de humedad de suelo dentro de una parcela específica con topografía atípica.
- **No extrapolar directamente a limón persa (*Citrus latifolia*) sin reentrenamiento:** El comportamiento estacional y los mercados de exportación de Veracruz/Oaxaca difieren del ciclo fisiológico del limón mexicano con semilla de Colima.

---

## 6. Distribución y Licencia Abierta (*Distribution*)

- **Repositorio Público:** [`https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima`](https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima) (Directorio `data/oro/` y manifiesto criptográfico `data/oro/dataset_publicado_e3_manifest.json`).
- **Licencia Abierta del Dataset Curado:** **Creative Commons Attribution 4.0 International (`CC BY 4.0`)**, compatible con las licencias de origen (`CC BY 4.0` de Open-Meteo, `Libre Uso de Datos Abiertos MX` de SNIIM/INEGI y atribución `ODbL 1.0` de © OpenStreetMap Contributors).
- **Citación sugerida:**
  > Escareño Montaño, N. D. (2026). *CITRO-DATA LAB COLIMA: Dataset Maestro Agroclimático, Geoespacial y Comercial del Limón Mexicano en Colima (Capa Oro v3.0, Etiqueta e3)* [Conjunto de datos]. TecNM — Instituto Tecnológico de Colima. `https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima`

---

## 7. Mantenimiento, Linaje y Actualización (*Maintenance*)

- **Responsable del mantenimiento:** Norberto Daniel Escareño Montaño (`23460323@colima.tecnm.mx`).
- **Linaje 100% Verificable:** Cada uno de los registros de Capa Oro incluye las columnas `linaje_id_registro`, `linaje_fuentes_bronce`, `linaje_archivos_bronce`, `linaje_sha256_bronce`, `linaje_fecha_ingesta_utc` y `linaje_version_pipeline`, auditables mediante `pipeline/linaje_datos.py` y la pestaña **Linaje** del tablero Streamlit.
- **Reproducibilidad Determinista:** Cualquier tercero puede regenerar y verificar criptográficamente el dataset ejecutando:
  ```bash
  python -m pipeline.optimizacion_dataset_e3
  python -m pipeline.multivariado_pca_manova_e3
  python -m pipeline.calidad_sello_e3
  python -m pipeline.verificar_e3
  pytest -v
  ```
