"""
Integración de Fuentes y Construcción de Capa Oro (data/oro/).
CITRO-DATA LAB COLIMA — Entrega E1.
Autor: Norberto Daniel Escareño Montaño (23460323)

Integra las fuentes heterogéneas Open-Meteo (agroclima municipal en Colima) y
SNIIM-Economía (precios mayoristas de limón mexicano en origen y destino)
resolviendo conflictos de esquema, unidades, formatos de fecha y granularidad
espacial/temporal (entity resolution).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd

from pipeline.limpieza_plata import ejecutar_limpieza_plata

ROOT_DIR = Path(__file__).resolve().parents[1]
PLATA_DIR = ROOT_DIR / "data" / "plata"
ORO_DIR = ROOT_DIR / "data" / "oro"

# Ponderadores productivos basados en superficie sembrada de limón mexicano en Colima (SIAP-SADER):
# Tecomán concentra ~55% de la producción estatal, Armería ~22%, Manzanillo ~15% y Colima ~8%.
PESOS_PRODUCCION_CITRICOLA = {
    6009: 0.55,  # Tecomán (Valle Citrícola Sur)
    6001: 0.22,  # Armería (Corredor Costero)
    6007: 0.15,  # Manzanillo (Corredor Costero)
    6002: 0.08,  # Colima (Valle Central)
}


def construir_capa_oro() -> Dict[str, object]:
    """
    Ejecuta la integración Plata -> Oro y escribe los conjuntos analíticos y el
    diccionario de datos completo en data/oro/.
    """
    ORO_DIR.mkdir(parents=True, exist_ok=True)
    res_plata = ejecutar_limpieza_plata()

    df_clima = res_plata["clima_plata"].copy()
    df_sniim = res_plata["sniim_plata"].copy()

    # 1. Resolución de Entidades Espaciales (Entity Resolution) en Clima:
    # A) Indicadores específicos del epicentro productor: Tecomán (id_municipio = 6009)
    df_tecoman = (
        df_clima[df_clima["id_municipio"] == 6009]
        .sort_values("anio_mes")
        .set_index("anio_mes")
    )

    # B) Índice agroclimático ponderado de la cuenca citrícola estatal (4 municipios)
    df_clima["peso_productivo"] = df_clima["id_municipio"].map(PESOS_PRODUCCION_CITRICOLA)
    registros_cuenca = []
    for anio_mes, grp in df_clima.groupby("anio_mes"):
        w = grp["peso_productivo"].to_numpy()
        registros_cuenca.append(
            {
                "anio_mes": anio_mes,
                "temp_max_cuenca_pond_c": round(float(np.sum(grp["temp_max_promedio_c"] * w)), 2),
                "temp_media_cuenca_pond_c": round(float(np.sum(grp["temp_media_c"] * w)), 2),
                "precipitacion_cuenca_pond_mm": round(float(np.sum(grp["precipitacion_acum_mm"] * w)), 2),
                "et0_cuenca_pond_mm": round(float(np.sum(grp["evapotranspiracion_acum_mm"] * w)), 2),
                "deficit_hidrico_cuenca_pond_mm": round(float(np.sum(grp["deficit_hidrico_acum_mm"] * w)), 2),
                "dias_estres_35c_max_estatal": int(grp["dias_estres_termico_35c"].max()),
            }
        )
    df_cuenca = pd.DataFrame(registros_cuenca).set_index("anio_mes")

    # 2. Resolución de Entidades Comerciales en Precios Mayoristas SNIIM:
    # A) Precio frecuente en origen Colima (MKT-COL: Empacadoras Tecomán/Colima)
    df_mkt_col = (
        df_sniim[df_sniim["id_mercado"] == "MKT-COL"]
        .sort_values("anio_mes")
        .set_index("anio_mes")
    )

    # B) Precio frecuente promedio en mercados nacionales de destino (GDL, CDMX, MTY)
    df_destinos = (
        df_sniim[df_sniim["id_mercado"].isin(["MKT-GDL", "MKT-CDMX", "MKT-MTY"])]
        .groupby("anio_mes")
        .agg(
            precio_frecuente_destinos_mxn_kg=("precio_frecuente_mxn_kg", lambda s: round(float(s.mean()), 2)),
            precio_max_nacional_mxn_kg=("precio_max_mxn_kg", lambda s: round(float(s.max()), 2)),
            margen_intermediacion_promedio_mxn_kg=("diferencial_vs_origen_mxn_kg", lambda s: round(float(s.mean()), 2)),
            volumen_total_nacional_ton=("volumen_comercializado_ton", "sum"),
        )
    )

    # 3. Ensamble de la Serie Mensual Maestra de Capa Oro (60 meses: 2021-01 a 2025-12)
    serie_oro = pd.DataFrame(index=df_mkt_col.index)
    serie_oro["fecha_corte"] = serie_oro.index + "-01"
    serie_oro["anio"] = df_mkt_col["anio"].astype(int)
    serie_oro["mes"] = df_mkt_col["mes"].astype(int)
    serie_oro["jerarquia_trimestre"] = df_mkt_col["jerarquia_trimestre"]
    serie_oro["jerarquia_ciclo_citricola"] = df_mkt_col["jerarquia_ciclo_citricola"]

    # Variables económicas de precios y volumen (SNIIM)
    serie_oro["precio_frecuente_origen_colima_mxn_kg"] = df_mkt_col["precio_frecuente_mxn_kg"].round(2)
    serie_oro["precio_min_origen_colima_mxn_kg"] = df_mkt_col["precio_min_mxn_kg"].round(2)
    serie_oro["precio_max_origen_colima_mxn_kg"] = df_mkt_col["precio_max_mxn_kg"].round(2)
    serie_oro["precio_frecuente_destinos_mxn_kg"] = df_destinos["precio_frecuente_destinos_mxn_kg"]
    serie_oro["margen_intermediacion_mxn_kg"] = df_destinos["margen_intermediacion_promedio_mxn_kg"]
    serie_oro["volumen_origen_colima_ton"] = df_mkt_col["volumen_comercializado_ton"].astype(int)
    serie_oro["volumen_total_4mercados_ton"] = (
        df_mkt_col["volumen_comercializado_ton"] + df_destinos["volumen_total_nacional_ton"]
    ).astype(int)
    serie_oro["rango_precio_limon"] = df_mkt_col["rango_precio_limon"]
    serie_oro["es_choque_legitimo_precio"] = df_mkt_col["es_choque_legitimo_dominio"].astype(bool)

    # Variables agroclimáticas en Tecomán (epicentro) y Cuenca Citrícola Estatal
    serie_oro["temp_max_tecoman_c"] = df_tecoman["temp_max_promedio_c"].round(2)
    serie_oro["temp_media_tecoman_c"] = df_tecoman["temp_media_c"].round(2)
    serie_oro["precipitacion_tecoman_mm"] = df_tecoman["precipitacion_acum_mm"].round(2)
    serie_oro["et0_tecoman_mm"] = df_tecoman["evapotranspiracion_acum_mm"].round(2)
    serie_oro["deficit_hidrico_tecoman_mm"] = df_tecoman["deficit_hidrico_acum_mm"].round(2)
    serie_oro["gdd_tecoman_mes"] = df_tecoman["gdd_acumulado_mes"].round(2)
    serie_oro["radiacion_tecoman_mj_m2"] = df_tecoman["radiacion_media_mj_m2"].round(2)
    serie_oro["nivel_estres_hidrico_tecoman"] = df_tecoman["nivel_estres_hidrico"]

    # Variables ponderadas de cuenca estatal
    serie_oro["temp_max_cuenca_pond_c"] = df_cuenca["temp_max_cuenca_pond_c"]
    serie_oro["precipitacion_cuenca_pond_mm"] = df_cuenca["precipitacion_cuenca_pond_mm"]
    serie_oro["deficit_hidrico_cuenca_pond_mm"] = df_cuenca["deficit_hidrico_cuenca_pond_mm"]

    # Variables escaladas listas para modelado estadístico
    serie_oro["precio_origen_zscore"] = df_mkt_col["precio_frecuente_mxn_kg_zscore"]
    serie_oro["precio_origen_minmax"] = df_mkt_col["precio_frecuente_mxn_kg_minmax"]
    serie_oro["deficit_tecoman_zscore"] = df_tecoman["deficit_hidrico_acum_mm_zscore"]

    serie_oro = serie_oro.reset_index()
    serie_oro.to_csv(ORO_DIR / "serie_mensual_oro_60m.csv", index=False)

    # 4. Panel Multivariado Municipio-Mercado en Capa Oro (240 filas climáticas con referencia de precio en origen)
    panel_oro = df_clima.merge(
        serie_oro[
            [
                "anio_mes",
                "precio_frecuente_origen_colima_mxn_kg",
                "precio_frecuente_destinos_mxn_kg",
                "margen_intermediacion_mxn_kg",
                "volumen_origen_colima_ton",
                "rango_precio_limon",
                "es_choque_legitimo_precio",
            ]
        ],
        on="anio_mes",
        how="left",
    )
    panel_oro.to_csv(ORO_DIR / "panel_integrado_municipio_mercado_oro.csv", index=False)

    # 5. Registro auditable de resolución de conflictos de integración
    conflictos = {
        "conflicto_1_granularidad_temporal": {
            "fuente_a": "Open-Meteo (frecuencia diaria YYYY-MM-DD, 7,304 registros)",
            "fuente_b": "SNIIM Economía (frecuencia mensual YYYY-MM, 240 registros)",
            "resolucion": "Agregación física mensual por municipio (promedios térmicos, sumas acumuladas de precipitación, ET0, déficit hídrico y GDD) sincronizada con llave canónica anio_mes (YYYY-MM) y fecha_corte (YYYY-MM-01).",
        },
        "conflicto_2_resolucion_entidades_espaciales": {
            "fuente_a": "Identificadores geoestadísticos municipales INEGI (6009 Tecomán, 6001 Armería, 6007 Manzanillo, 6002 Colima)",
            "fuente_b": "Identificadores de centrales de abasto SNIIM (MKT-COL, MKT-GDL, MKT-CDMX, MKT-MTY)",
            "resolucion": "Entity Resolution de dos niveles: (1) Vinculación directa del mercado en origen MKT-COL con el epicentro productivo Tecomán (6009) y (2) Construcción del índice climático ponderado de la cuenca citrícola de Colima según participación en superficie sembrada SIAP (Tecomán 55%, Armería 22%, Manzanillo 15%, Colima 8%).",
        },
        "conflicto_3_unidades_y_esquema": {
            "fuente_a": "Variables meteorológicas en °C, mm/día y MJ/m² con nombres en inglés en el JSON crudo de Open-Meteo",
            "fuente_b": "Cotizaciones en Arpilla de 20 kg y Kilogramo en tablas HTML de SNIIM",
            "resolucion": "Renombrado canónico snake_case con sufijo explícito de unidad (_c, _mm, _mj_m2, _mxn_kg, _ton) y prorrateo homogéneo de arpilla de 20 kg a MXN/kg.",
        },
        "conflicto_4_codificacion_y_zona_horaria": {
            "fuente_a": "Timestamps UTC en API REST Open-Meteo",
            "fuente_b": "Fechas locales CST (America/Mexico_City) e ISO-8859-1 en portal SNIIM",
            "resolucion": "Alineación a zona horaria America/Mexico_City y normalización de texto en UTF-8 sin caracteres especiales ambiguos en llaves.",
        },
    }
    with open(ORO_DIR / "resolucion_conflictos_integracion.json", "w", encoding="utf-8") as f:
        json.dump(conflictos, f, indent=2, ensure_ascii=False)

    # 6. Generar Diccionario de Datos Completo en data/oro/diccionario_datos.md
    escribir_diccionario_datos_oro(serie_oro, panel_oro)

    return {
        "serie_oro": serie_oro,
        "panel_oro": panel_oro,
        "conflictos": conflictos,
        "res_plata": res_plata,
    }


def escribir_diccionario_datos_oro(serie_oro: pd.DataFrame, panel_oro: pd.DataFrame) -> None:
    """Escribe el diccionario de datos formal de la Capa Oro en data/oro/diccionario_datos.md."""
    contenido = rf"""# Diccionario de Datos — Capa Oro (`data/oro/`)

**Proyecto:** CITRO-DATA LAB COLIMA — Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano en Colima
**Estudiante:** Norberto Daniel Escareño Montaño (`23460323`)
**Etapa:** E1 · Trusted Data Lab (Capa Plata, Limpieza, Puerta de Calidad y Pronóstico)
**Cobertura Temporal:** Enero 2021 – Diciembre 2025 (`60` meses continuos)
**Archivos Documentados:**
1. `data/oro/serie_mensual_oro_60m.csv` (`{len(serie_oro)}` filas × `{serie_oro.shape[1]}` columnas) — Serie maestra mensual integrada para análisis de series de tiempo y pronóstico.
2. `data/oro/panel_integrado_municipio_mercado_oro.csv` (`{len(panel_oro)}` filas × `{panel_oro.shape[1]}` columnas) — Panel multivariado por municipio productor (`4` municipios × `60` meses) enriquecido con precios mayoristas.

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
| 5 | `jerarquia_trimestre` | `string` | Categoría | Jerarquía Temporal | `{{Q1, Q2, Q3, Q4}}` | Nivel trimestral de la jerarquía conceptual temporal. |
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
| 19 | `et0_tecoman_mm` | `float64` | `mm` | Open-Meteo (`6009`) | `[50.0, 300.0]` | Evapotranspiración potencial FAO-56 Penman-Monteith acumulada mensual en Tecomán ($\sum ET_{{0,d}}$). |
| 20 | `deficit_hidrico_tecoman_mm` | `float64` | `mm` | Derivada Clima | `[-300.0, 600.0]` | **Indicador agroclimático clave ($X_t$):** Balance hídrico acumulado mensual ($P - ET_0$) en Tecomán; valores negativos indican déficit hídrico que requiere riego de auxilio. |
| 21 | `gdd_tecoman_mes` | `float64` | `°C·día` | Derivada Clima | `[100.0, 700.0]` | Grados-Día de Desarrollo citrícola acumulados en el mes ($\sum \max(0, T_{{\text{{med}}}} - 13^\circ\text{{C}})$). |
| 22 | `radiacion_tecoman_mj_m2` | `float64` | `MJ/m²/día` | Open-Meteo (`6009`) | `[8.0, 35.0]` | Radiación solar de onda corta promedio mensual en Tecomán. |
| 23 | `nivel_estres_hidrico_tecoman` | `string` | Categoría | Discretización | `4 niveles` | Discretización del balance hídrico (`Sequia_Critica`, `Deficit_Severo`, `Deficit_Moderado`, `Superavit_Hidrico`). |
| 24 | `temp_max_cuenca_pond_c` | `float64` | `°C` | Integrada Clima | `[20.0, 45.0]` | Temperatura máxima mensual ponderada por superficie citrícola en los 4 municipios. |
| 25 | `precipitacion_cuenca_pond_mm` | `float64` | `mm` | Integrada Clima | `[0.0, 800.0]` | Precipitación acumulada mensual ponderada en la cuenca citrícola de Colima. |
| 26 | `deficit_hidrico_cuenca_pond_mm` | `float64` | `mm` | Integrada Clima | `[-300.0, 600.0]` | Déficit hídrico acumulado mensual ponderado en la cuenca citrícola de Colima. |
| 27 | `precio_origen_zscore` | `float64` | `σ (adim.)` | Escalado Z-Score | `[-3.0, +5.0]` | Precio frecuente en origen estandarizado ($Z = (Y - \mu)/\sigma$). |
| 28 | `precio_origen_minmax` | `float64` | `[0, 1]` | Escalado Min-Max | `[0.0, 1.0]` | Precio frecuente en origen normalizado al intervalo $[0, 1]$. |
| 29 | `deficit_tecoman_zscore` | `float64` | `σ (adim.)` | Escalado Z-Score | `[-3.0, +5.0]` | Déficit hídrico de Tecomán estandarizado ($Z = (X - \mu)/\sigma$). |
"""
    with open(ORO_DIR / "diccionario_datos.md", "w", encoding="utf-8") as f:
        f.write(contenido)


if __name__ == "__main__":
    res = construir_capa_oro()
    print(
        f"[OK] Capa Oro construida: "
        f"serie_mensual_oro_60m={res['serie_oro'].shape}, "
        f"panel_integrado={res['panel_oro'].shape}"
    )
