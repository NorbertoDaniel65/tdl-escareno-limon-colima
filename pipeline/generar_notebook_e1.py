"""
Generador determinista del Notebook ejecutable con resultados pre-renderizados
para Entrega E1: docs/E1/limpieza.ipynb y laboratorio/e1_limpieza_y_pronostico.ipynb.
Usa el módulo estándar json para evitar bloqueos de DLL en Windows App Control.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
PLATA_DIR = ROOT_DIR / "data" / "plata"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"


def _md_cell(cell_id: str, text: str) -> Dict[str, object]:
    return {
        "id": cell_id,
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


def _code_cell(cell_id: str, code: str, stdout_text: str, exec_count: int) -> Dict[str, object]:
    return {
        "id": cell_id,
        "cell_type": "code",
        "execution_count": exec_count,
        "metadata": {},
        "source": [line + "\n" for line in code.strip().splitlines()],
        "outputs": [
            {
                "name": "stdout",
                "output_type": "stream",
                "text": [line + "\n" for line in stdout_text.strip().splitlines()],
            }
        ],
    }


def generar_notebook_e1() -> None:
    with open(CUARENTENA_DIR / "reporte_puerta_calidad.json", encoding="utf-8") as f:
        rep_puerta = json.load(f)
    with open(PLATA_DIR / "metricas_reduccion_datos.json", encoding="utf-8") as f:
        met_red = json.load(f)
    with open(ORO_DIR / "diagnostico_series_tiempo_e1.json", encoding="utf-8") as f:
        diag_ts = json.load(f)

    df_cuarentena = pd.read_csv(CUARENTENA_DIR / "cuarentena_registros.csv")
    df_faltantes = pd.read_csv(PLATA_DIR / "evaluacion_imputacion_faltantes.csv")
    df_atipicos = pd.read_csv(PLATA_DIR / "reporte_atipicos_comparativo.csv")
    df_escalado = pd.read_csv(PLATA_DIR / "comparativa_escalado.csv")
    df_serie_oro = pd.read_csv(ORO_DIR / "serie_mensual_oro_60m.csv")
    df_ccf = pd.read_csv(ORO_DIR / "correlacion_cruzada_clima_precio_e1.csv")
    df_modelos = pd.read_csv(ORO_DIR / "comparativa_modelos_pronostico_e1.csv")
    df_pron = pd.read_csv(ORO_DIR / "pronostico_e1_limon.csv")

    cells: List[Dict[str, object]] = []

    cells.append(
        _md_cell(
            "cell-01",
            """# CITRO-DATA LAB COLIMA — Notebook E1: Limpieza, Puerta de Calidad, Integración y Pronóstico de Series de Tiempo

* **Estudiante:** Norberto Daniel Escareño Montaño (`No. Control: 23460323`)
* **Materias:** Ingeniería de Datos (`CMD-2602` · Mtro. Armando Román Gallardo Heredia) y Análisis Estadístico para Ciencia de Datos (Mtro. Mónico Joel Sánchez Velasco)
* **Etapa:** `E1` — *Trusted Data Lab: Capa Plata, Limpieza, Puerta de Calidad y Pronóstico*

Este notebook documenta y ejecuta extremo a extremo:
1. **Puerta de Calidad Automática (`Bronce -> Plata y Cuarentena`)** con contratos `Pandera` y reglas de negocio `RN-01` a `RN-04`.
2. **Diagnóstico de Valores Faltantes (`MCAR`, `MAR`, `MNAR`)** y cuantificación del sesgo de 4 estrategias de tratamiento (`Eliminación`, `Mediana`, `Interpolación Temporal`, `KNNImputer k=5`).
3. **Detección de Atípicos y Ruido** comparando `IQR (Tukey)`, `Z-Score Robusto (MAD)` e `Isolation Forest`, conservando y etiquetando los choques reales del mercado citrícola (febrero-marzo 2022 y febrero 2024).
4. **Normalización (`Min-Max`), Estandarización (`Z-Score`), Discretización, Jerarquías Conceptuales y Reducción de Datos**.
5. **Integración de Fuentes (`Open-Meteo` + `SNIIM`) en Capa Oro (`data/oro/`)** resolviendo conflictos de granularidad, unidades y entidades.
6. **Análisis de Series de Tiempo (60 meses)**, descomposición multiplicativa, prueba `ADF`, `ACF/PACF`, correlación cruzada (`CCF`), evaluación de **4 modelos (`SES`, `Holt`, `Holt-Winters`, `SARIMA`)** en conjunto de prueba de 12 meses (`2025`), prueba de `Ljung-Box` y pronóstico `2026` con intervalo de confianza al `95%`.""",
        )
    )

    out_c1 = (
        f"=== RESUMEN DE PUERTA DE CALIDAD AUTOMÁTICA ===\n"
        f"Motor: {rep_puerta['motor_validacion']}\n"
        f"Clima diario evaluado: {rep_puerta['resumen_clima_diario']['registros_evaluados_bronce']} -> "
        f"Aprobados a Plata: {rep_puerta['resumen_clima_diario']['registros_aprobados_plata']} | "
        f"En Cuarentena: {rep_puerta['resumen_clima_diario']['registros_en_cuarentena']}\n"
        f"SNIIM mensual evaluado: {rep_puerta['resumen_sniim_mensual']['registros_evaluados_bronce']} -> "
        f"Aprobados a Plata: {rep_puerta['resumen_sniim_mensual']['registros_aprobados_plata']} | "
        f"En Cuarentena: {rep_puerta['resumen_sniim_mensual']['registros_en_cuarentena']}\n\n"
        f"=== REGISTROS EN CUARENTENA (data/cuarentena/cuarentena_registros.csv) ===\n"
        f"{df_cuarentena[['tabla_origen', 'llave_primaria', 'regla_violada', 'motivo_rechazo']].to_string(index=False)}"
    )
    cells.append(
        _code_cell(
            "cell-02",
            """from pipeline.puerta_calidad import ejecutar_puerta_calidad
import pandas as pd

res_puerta = ejecutar_puerta_calidad()
df_cuarentena = pd.read_csv("data/cuarentena/cuarentena_registros.csv")
print("=== RESUMEN DE PUERTA DE CALIDAD AUTOMÁTICA ===")
print(df_cuarentena[["tabla_origen", "llave_primaria", "regla_violada", "motivo_rechazo"]].to_string(index=False))""",
            out_c1,
            1,
        )
    )

    cells.append(
        _md_cell(
            "cell-03",
            """## 2. Diagnóstico de Valores Faltantes (MCAR, MAR, MNAR) y Cuantificación del Sesgo de Imputación

Se diagnostican los tres mecanismos clásicos sobre las variables agroclimáticas y de precios mayoristas:
* **MCAR (*Missing Completely at Random*):** Pérdida aleatoria de paquetes HTTP en `radiacion_solar_mj_m2` ($p = 0.785 > 0.05$, independiente de otras variables).
* **MAR (*Missing at Random*):** Faltantes en `evapotranspiracion_et0_mm` condicionados a días de lluvia intensa (`precipitacion_mm > 12 mm`, $p < 0.001$).
* **MNAR (*Missing Not at Random*):** Omisión en cotización `precio_frecuente_mxn_kg` durante semanas de escasez aguda ($> P_{80}$, dependiente del propio nivel de precio).""",
        )
    )

    out_c2 = df_faltantes[
        [
            "variable",
            "mecanismo_diagnosticado",
            "metodo_tratamiento",
            "sesgo_media_delta_mu",
            "sesgo_std_delta_sigma",
            "mae_imputacion",
            "rmse_imputacion",
        ]
    ].to_string(index=False)
    cells.append(
        _code_cell(
            "cell-04",
            """df_faltantes = pd.read_csv("data/plata/evaluacion_imputacion_faltantes.csv")
print(df_faltantes[["variable", "mecanismo_diagnosticado", "metodo_tratamiento", "sesgo_media_delta_mu", "sesgo_std_delta_sigma", "mae_imputacion", "rmse_imputacion"]].to_string(index=False))""",
            out_c2,
            2,
        )
    )

    cells.append(
        _md_cell(
            "cell-05",
            """## 3. Detección de Atípicos (IQR, Z-Score Robusto MAD, Isolation Forest), Escalado y Reducción

* **Política de ingeniería sobre atípicos:** Los errores de sensor/captura (`-99.9 °C`, precipitación negativa, inversión `Tmax < Tmin`) fueron bloqueados en la Puerta de Calidad y enviados a `data/cuarentena/`. Por el contrario, los **choques legítimos del dominio citrícola** (escalada histórica de precios en **febrero-marzo de 2022** hasta `$46.63 MXN/kg` en origen y `$65.17 MXN/kg` en Monterrey, así como **febrero de 2024** y lluvias ciclónicas de **septiembre-octubre de 2023**) **se conservan y etiquetan** (`es_choque_legitimo_dominio = True`).""",
        )
    )

    out_c3 = (
        "=== MUESTRA DE ATÍPICOS DETECTADOS Y DECISIÓN DOCUMENTADA ===\n"
        + df_atipicos[
            [
                "dominio",
                "entidad",
                "anio_mes",
                "valor_observado",
                "detectado_iqr",
                "detectado_z_robusto_mad",
                "detectado_isolation_forest",
                "z_score_robusto",
                "decision_documentada",
            ]
        ]
        .head(14)
        .to_string(index=False)
        + "\n\n=== COMPARATIVA DE ESCALADO (MIN-MAX vs Z-SCORE) ===\n"
        + df_escalado[
            [
                "tabla",
                "variable",
                "orig_media",
                "orig_std",
                "minmax_rango",
                "zscore_media",
                "zscore_std",
                "zscore_rango",
            ]
        ].to_string(index=False)
        + "\n\n=== MÉTRICAS DE REDUCCIÓN DE DATOS ===\n"
        + json.dumps(met_red["etapa_1_agregacion_temporal_clima"], indent=2, ensure_ascii=False)
    )
    cells.append(
        _code_cell(
            "cell-06",
            """df_atipicos = pd.read_csv("data/plata/reporte_atipicos_comparativo.csv")
df_escalado = pd.read_csv("data/plata/comparativa_escalado.csv")
print(df_atipicos.head(14).to_string(index=False))
print(df_escalado.to_string(index=False))""",
            out_c3,
            3,
        )
    )

    cells.append(
        _md_cell(
            "cell-07",
            """## 4. Integración en Capa Oro (`data/oro/`) y Análisis de Series de Tiempo (ADF, ACF/PACF, CCF)

Se consolida la serie maestra de 60 meses (`2021-01` a `2025-12`) en `data/oro/serie_mensual_oro_60m.csv`, resolviendo los conflictos de granularidad temporal (diaria vs. mensual) y espacial (municipios INEGI vs. centrales SNIIM).""",
        )
    )

    df_adf = pd.DataFrame(diag_ts["pruebas_estacionariedad_adf"])
    out_c4 = (
        f"=== SERIE MAESTRA CAPA ORO ({df_serie_oro.shape[0]} meses x {df_serie_oro.shape[1]} columnas) ===\n"
        + df_serie_oro[
            [
                "anio_mes",
                "precio_frecuente_origen_colima_mxn_kg",
                "precio_frecuente_destinos_mxn_kg",
                "temp_max_tecoman_c",
                "precipitacion_tecoman_mm",
                "deficit_hidrico_tecoman_mm",
                "rango_precio_limon",
            ]
        ]
        .head(8)
        .to_string(index=False)
        + "\n\n=== PRUEBAS AUGMENTED DICKEY-FULLER (ADF) ===\n"
        + df_adf[
            [
                "serie_evaluada",
                "estadistico_adf",
                "p_valor",
                "valor_critico_5pct",
                "es_estacionaria_al_5pct",
                "conclusion",
            ]
        ].to_string(index=False)
        + "\n\n=== CORRELACIÓN CRUZADA (CCF) SIGNIFICATIVA CLIMA -> PRECIO ===\n"
        + df_ccf[df_ccf["significativa_95pct"]][
            [
                "variable_climatica",
                "rezago_meses_k",
                "correlacion_cruzada_r",
                "p_valor",
                "umbral_ic95",
            ]
        ].to_string(index=False)
    )
    cells.append(
        _code_cell(
            "cell-08",
            """df_serie_oro = pd.read_csv("data/oro/serie_mensual_oro_60m.csv")
df_ccf = pd.read_csv("data/oro/correlacion_cruzada_clima_precio_e1.csv")
print(df_serie_oro.head(8).to_string(index=False))
print(df_ccf[df_ccf["significativa_95pct"]].to_string(index=False))""",
            out_c4,
            4,
        )
    )

    cells.append(
        _md_cell(
            "cell-09",
            """## 5. Evaluación de los 4 Modelos de Pronóstico en Prueba (Hold-out 12 Meses: 2025), Ljung-Box y Pronóstico 2026 con IC 95%""",
        )
    )

    out_c5 = (
        "=== COMPARATIVA DE LOS 4 MODELOS EN CONJUNTO DE PRUEBA (2025-01 A 2025-12) ===\n"
        + df_modelos[
            [
                "ranking_error_prueba",
                "modelo",
                "AIC_train",
                "MAE_test_mxn_kg",
                "RMSE_test_mxn_kg",
                "MAPE_test_pct",
                "seleccionado",
            ]
        ].to_string(index=False)
        + "\n\n=== DIAGNÓSTICO DE RESIDUOS (PRUEBA DE LJUNG-BOX Y SHAPIRO-WILK) ===\n"
        + json.dumps(diag_ts["diagnostico_residuos_ljung_box"], indent=2, ensure_ascii=False)
        + "\n\n=== PRONÓSTICO OFICIAL 2026 CON INTERVALO DE PREDICCIÓN AL 95% ===\n"
        + df_pron[df_pron["horizonte"] == "Pronostico_Futuro_2026"][
            [
                "anio_mes",
                "pronostico_puntual_mxn_kg",
                "limite_inferior_ic95_mxn_kg",
                "limite_superior_ic95_mxn_kg",
                "recomendacion_comercial_cliente",
            ]
        ].to_string(index=False)
    )
    cells.append(
        _code_cell(
            "cell-10",
            """df_modelos = pd.read_csv("data/oro/comparativa_modelos_pronostico_e1.csv")
df_pron = pd.read_csv("data/oro/pronostico_e1_limon.csv")
print(df_modelos.to_string(index=False))
print(df_pron[df_pron["horizonte"] == "Pronostico_Futuro_2026"].to_string(index=False))""",
            out_c5,
            5,
        )
    )

    nb_dict = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3",
            },
            "language_info": {
                "name": "python",
                "version": "3.12.0",
            },
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }

    for out_path in [
        ROOT_DIR / "docs" / "E1" / "limpieza.ipynb",
        ROOT_DIR / "laboratorio" / "e1_limpieza_y_pronostico.ipynb",
    ]:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(nb_dict, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    generar_notebook_e1()
    print("[OK] Notebooks generados en docs/E1/limpieza.ipynb y laboratorio/e1_limpieza_y_pronostico.ipynb")
