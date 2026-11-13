# Diccionario de Datos — Capa Oro (`data/oro/`)

**Proyecto:** CITRO-DATA LAB COLIMA — Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano en Colima
**Estudiante:** Norberto Daniel Escareño Montaño (`23460323`)
**Etapa:** E1 · Trusted Data Lab (Capa Plata, Limpieza, Puerta de Calidad y Pronóstico)
**Cobertura Temporal:** Enero 2021 – Diciembre 2025 (`60` meses continuos)
**Archivos Documentados:**
1. `data/oro/serie_mensual_oro_60m.csv` (`60` filas × `29` columnas) — Serie maestra mensual integrada para análisis de series de tiempo y pronóstico.
2. `data/oro/panel_integrado_municipio_mercado_oro.csv` (`240` filas × `43` columnas) — Panel multivariado por municipio productor (`4` municipios × `60` meses) enriquecido con precios mayoristas.

---

## 1. Resolución de Conflictos de Integración (*Entity Resolution* y Esquema)

| Conflicto Detectado | Fuente 1 (`Open-Meteo`) | Fuente 2 (`SNIIM - Economía`) | Regla de Resolución en Capa Oro |
| :--- | :--- | :--- | :--- |
| **Granularidad Temporal** | Diaria (`YYYY-MM-DD`, `7,304` registros) | Mensual (`YYYY-MM`, `240` registros) | Agregación física mensual por municipio (`mean` para temperaturas y radiación; `sum` para precipitación, $ET_0$, déficit hídrico y $GDD$; `max` para rachas de viento) bajo llave canónica `anio_mes`. |
| **Granularidad Espacial (*Entity Resolution*)** | Municipios productores de Colima (`6009` Tecomán, `6001` Armería, `6007` Manzanillo, `6002` Colima) | Centrales de abasto (`MKT-COL`, `MKT-GDL`, `MKT-CDMX`, `MKT-MTY`) | Cruce por `anio_mes` vinculando el precio en origen (`MKT-COL`) con el epicentro productivo (`Tecomán 6009`) y con el índice climático ponderado de la cuenca citrícola estatal (pesos SIAP: Tecomán `0.55`, Armería `0.22`, Manzanillo `0.15`, Colima `0.08`). |
| **Unidades de Medida** | `°C`, `mm/día`, `km/h`, `MJ/m²` | Arpilla `20 kg` prorrateada a `MXN/kg` y `Toneladas` | Estandarización al Sistema Internacional y métrico decimal con sufijo explícito en cada columna (`_c`, `_mm`, `_mj_m2`, `_mxn_kg`, `_ton`). |
| **Codificación y Zona Horaria** | `UTF-8`, corte horario `UTC` | `ISO-8859-1` / `UTF-8`, corte local `America/Mexico_City` | Conversión íntegra a `UTF-8` sin caracteres ambiguos en llaves y corte diario/mensual en `America/Mexico_City (UTC-6)`. |

---

## 2. Catálogo de Variables de `serie_mensual_oro_60m.csv`

| # | Columna | Tipo | Unidad | Fuente Origen | Rango Válido / Dominio | Fórmula / Transformación y Significado de Negocio |
| :---: | :--- | :---: | :---: | :---: | :--- | :--- |
| 1 | `anio_mes` | `string` | `YYYY-MM` | Integrada | `2021-01` a `2025-12` | **Llave primaria temporal** mensual de la serie maestra. |
| 2 | `fecha_corte` | `date (str)` | `YYYY-MM-DD` | Derivada | Primer día del mes | Fecha canónica ISO-8601 (`YYYY-MM-01`) para indexación en `statsmodels` y `pandas`. |
| 3 | `anio` | `int64` | Año | SNIIM / Clima | `[2021, 2025]` | Año calendario de la observación. |
| 4 | `mes` | `int64` | Mes | SNIIM / Clima | `[1, 12]` | Mes calendario (`1 = Enero`, ..., `12 = Diciembre`). |
| 5 | `jerarquia_trimestre` | `string` | Categoría | Jerarquía Temporal | `{Q1, Q2, Q3, Q4}` | Nivel trimestral de la jerarquía conceptual temporal. |
| 6 | `jerarquia_ciclo_citricola` | `string` | Categoría | Jerarquía Dominio | `4 fases fenológicas` | Fase del ciclo citrícola en Colima (Escasez Invernal, Floración Primavera, Cosecha Pico Verano, Transición Otoño). |
| 7 | `precio_frecuente_origen_colima_mxn_kg` | `float64` | `MXN/kg` | SNIIM (`MKT-COL`) | `[3.0, 120.0]` | **Variable objetivo principal ($Y_t$):** Precio mayorista frecuente del limón mexicano #5 en empacadoras de Colima/Tecomán. |
| 8 | `precio_min_origen_colima_mxn_kg` | `float64` | `MXN/kg` | SNIIM (`MKT-COL`) | `[2.0, 110.0]` | Cotización mínima mensual en origen Colima ($\le$ precio frecuente). |
| 9 | `precio_max_origen_colima_mxn_kg` | `float64` | `MXN/kg` | SNIIM (`MKT-COL`) | `[4.0, 150.0]` | Cotización máxima mensual en origen Colima ($\ge$ precio frecuente). |
| 10 | `precio_frecuente_destinos_mxn_kg` | `float64` | `MXN/kg` | SNIIM (`GDL, CDMX, MTY`) | `[3.0, 130.0]` | Promedio del precio frecuente en las 3 centrales mayoristas de destino extrarregional. |
| 11 | `margen_intermediacion_mxn_kg` | `float64` | `MXN/kg` | Derivada SNIIM | `[-5.0, 40.0]` | Diferencial comercial promedio entre centrales de destino y precio en origen Colima. |
| 12 | `volumen_origen_colima_ton` | `int64` | `Toneladas` | SNIIM / SIAP | `[500, 20000]` | Volumen mensual estimado comercializado desde empacadoras de Colima. |
| 13 | `volumen_total_4mercados_ton` | `int64` | `Toneladas` | SNIIM / SIAP | `[2000, 60000]` | Suma del volumen mensual operado en las 4 plazas monitoreadas. |
| 14 | `rango_precio_limon` | `string` | Categoría | Discretización | `4 niveles` | Discretización de precio: `Bajo (<18)`, `Medio (18-28)`, `Alto (28-38)`, `Critico_Escasez (>38 MXN/kg)`. |
| 15 | `es_choque_legitimo_precio` | `bool` | Booleano | Detección Atípicos | `True / False` | Bandera que identifica choques reales de mercado (feb-mar 2022, feb 2024) conservados deliberadamente. |
| 16 | `temp_max_tecoman_c` | `float64` | `°C` | Open-Meteo (`6009`) | `[20.0, 45.0]` | Promedio mensual de la temperatura máxima diaria en Tecomán. |
| 17 | `temp_media_tecoman_c` | `float64` | `°C` | Open-Meteo (`6009`) | `[15.0, 38.0]` | Temperatura media mensual en Tecomán. |
| 18 | `precipitacion_tecoman_mm` | `float64` | `mm` | Open-Meteo (`6009`) | `[0.0, 800.0]` | Lámina de lluvia acumulada mensual en Tecomán ($\sum P_d$). |
| 19 | `et0_tecoman_mm` | `float64` | `mm` | Open-Meteo (`6009`) | `[50.0, 300.0]` | Evapotranspiración potencial FAO-56 Penman-Monteith acumulada mensual en Tecomán ($\sum ET_{0,d}$). |
| 20 | `deficit_hidrico_tecoman_mm` | `float64` | `mm` | Derivada Clima | `[-300.0, 600.0]` | **Indicador agroclimático clave ($X_t$):** Balance hídrico acumulado mensual ($P - ET_0$) en Tecomán; valores negativos indican déficit hídrico que requiere riego de auxilio. |
| 21 | `gdd_tecoman_mes` | `float64` | `°C·día` | Derivada Clima | `[100.0, 700.0]` | Grados-Día de Desarrollo citrícola acumulados en el mes ($\sum \max(0, T_{\text{med}} - 13^\circ\text{C})$). |
| 22 | `radiacion_tecoman_mj_m2` | `float64` | `MJ/m²/día` | Open-Meteo (`6009`) | `[8.0, 35.0]` | Radiación solar de onda corta promedio mensual en Tecomán. |
| 23 | `nivel_estres_hidrico_tecoman` | `string` | Categoría | Discretización | `4 niveles` | Discretización del balance hídrico (`Sequia_Critica`, `Deficit_Severo`, `Deficit_Moderado`, `Superavit_Hidrico`). |
| 24 | `temp_max_cuenca_pond_c` | `float64` | `°C` | Integrada Clima | `[20.0, 45.0]` | Temperatura máxima mensual ponderada por superficie citrícola en los 4 municipios. |
| 25 | `precipitacion_cuenca_pond_mm` | `float64` | `mm` | Integrada Clima | `[0.0, 800.0]` | Precipitación acumulada mensual ponderada en la cuenca citrícola de Colima. |
| 26 | `deficit_hidrico_cuenca_pond_mm` | `float64` | `mm` | Integrada Clima | `[-300.0, 600.0]` | Déficit hídrico acumulado mensual ponderado en la cuenca citrícola de Colima. |
| 27 | `precio_origen_zscore` | `float64` | `σ (adim.)` | Escalado Z-Score | `[-3.0, +5.0]` | Precio frecuente en origen estandarizado ($Z = (Y - \mu)/\sigma$). |
| 28 | `precio_origen_minmax` | `float64` | `[0, 1]` | Escalado Min-Max | `[0.0, 1.0]` | Precio frecuente en origen normalizado al intervalo $[0, 1]$. |
| 29 | `deficit_tecoman_zscore` | `float64` | `σ (adim.)` | Escalado Z-Score | `[-3.0, +5.0]` | Déficit hídrico de Tecomán estandarizado ($Z = (X - \mu)/\sigma$). |
