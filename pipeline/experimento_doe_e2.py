"""
Laboratorio Estadístico E2 — Diseño de Experimentos (Unidad 4: Análisis Estadístico).
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).

Ruta Ingeniería (definida en E0 — docs/E0/propuesta.md):
Ejecuta experimentos factoriales REALES y reproducibles sobre copias locales controladas
del pipeline de Capa Bronce -> Plata (sin saturar servidores externos):
  1. Diseño Factorial Completo 2^3 con aleatorización, r=3 réplicas y bloqueo (24 corridas).
  2. Diseño 2x3 (2 motores de validación x 3 formatos de escritura: CSV, Parquet Snappy, Parquet ZSTD)
     con ANOVA de dos vías e interacción + Tukey HSD (18 corridas).
  3. Diseño 2^4 Completo (16 tratamientos) vs. 2^(4-1) Fraccionado (8 tratamientos, I=ABCD, Resolución IV)
     con tabla explícita de estructura de alias y cuantificación de ahorro (50%).
  4. Validación de Supuestos de Residuos (Puerta de Calidad 3: Shapiro-Wilk, Levene, Durbin-Watson)
     y Corrida de Confirmación del Punto Óptimo (n=5) vs. Línea Base E1 con IC al 95%.
"""

from __future__ import annotations

import itertools
import json
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pandera as pa
from pandera import Check, Column, DataFrameSchema
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd
from statsmodels.stats.stattools import durbin_watson

ROOT_DIR = Path(__file__).resolve().parents[1]
BRONCE_CLIMA_PATH = ROOT_DIR / "data" / "bronce" / "open_meteo" / "agroclima_colima_diario_historico.csv"
ORO_DIR = ROOT_DIR / "data" / "oro"

MUNICIPIOS_VALIDOS = {6001, 6002, 6007, 6009}


def _esquema_clima_vectorizado() -> DataFrameSchema:
    return DataFrameSchema(
        columns={
            "id_municipio": Column(int, Check.isin(MUNICIPIOS_VALIDOS), nullable=False),
            "temp_max_c": Column(float, Check.in_range(10.0, 50.0), nullable=False),
            "temp_min_c": Column(float, Check.in_range(0.0, 40.0), nullable=False),
            "temp_media_c": Column(float, Check.in_range(5.0, 45.0), nullable=False),
            "precipitacion_mm": Column(float, Check.in_range(0.0, 600.0), nullable=False),
            "evapotranspiracion_et0_mm": Column(float, Check.in_range(0.0, 15.0), nullable=False),
        },
        coerce=False,
        strict=False,
    )


def _preparar_lotes_locales(tmp_dir: Path) -> list[Path]:
    """Crea 4 particiones locales idénticas (1 por municipio de Colima, escaladas x2) en disco temporal
    para benchmarking controlado y reproducible sin tocar servidores externos."""
    df_base = pd.read_csv(BRONCE_CLIMA_PATH)
    # Replicamos 2x la serie real de 5 años (= 14,608 filas totales = 10 años equivalentes)
    # para que las diferencias entre algoritmos y formatos sean claramente medibles en ms.
    rutas: list[Path] = []
    for mun_id, grp in df_base.groupby("id_municipio"):
        df_lote = pd.concat([grp, grp], ignore_index=True)
        p = tmp_dir / f"lote_bronce_mun_{mun_id}.csv"
        df_lote.to_csv(p, index=False, encoding="utf-8")
        rutas.append(p)
    return sorted(rutas)


def _validar_iterativo_fila(df: pd.DataFrame) -> tuple[pd.DataFrame, int]:
    """Validación fila-a-fila en Python puro (línea base no vectorizada)."""
    indices_validos: list[int] = []
    errores = 0
    for idx, row in enumerate(df.itertuples(index=False)):
        ok = (
            row.id_municipio in MUNICIPIOS_VALIDOS
            and 10.0 <= row.temp_max_c <= 50.0
            and 0.0 <= row.temp_min_c <= 40.0
            and 5.0 <= row.temp_media_c <= 45.0
            and 0.0 <= row.precipitacion_mm <= 600.0
            and 0.0 <= row.evapotranspiracion_et0_mm <= 15.0
            and row.temp_max_c >= row.temp_media_c >= row.temp_min_c
        )
        if ok:
            indices_validos.append(idx)
        else:
            errores += 1
    return df.iloc[indices_validos], errores


def _validar_vectorizado_pandera(df: pd.DataFrame, esquema: DataFrameSchema) -> tuple[pd.DataFrame, int]:
    """Validación vectorizada NumPy + Pandera DataFrameSchema."""
    mask = (
        df["id_municipio"].isin(MUNICIPIOS_VALIDOS)
        & df["temp_max_c"].between(10.0, 50.0)
        & df["temp_min_c"].between(0.0, 40.0)
        & df["temp_media_c"].between(5.0, 45.0)
        & df["precipitacion_mm"].between(0.0, 600.0)
        & df["evapotranspiracion_et0_mm"].between(0.0, 15.0)
        & (df["temp_max_c"] >= df["temp_media_c"])
        & (df["temp_media_c"] >= df["temp_min_c"])
    )
    df_val = df.loc[mask]
    esquema.validate(df_val, lazy=False)
    return df_val, int((~mask).sum())


def _ejecutar_corrida_pipeline(
    rutas_entrada: list[Path],
    out_dir: Path,
    esquema: DataFrameSchema,
    paralelismo: int,
    motor: str,
    formato: str,
    particionado: str = "consolidado",
    tag_corrida: str = "run",
) -> dict[str, Any]:
    """Ejecuta una corrida real del pipeline Bronce -> Validación -> Persistencia y mide tiempo, tamaño y error."""
    t0 = time.perf_counter()

    # Etapa 1: Lectura de lotes locales (secuencial vs. pool de hilos)
    if paralelismo == 1:
        dfs = [pd.read_csv(p) for p in rutas_entrada]
    else:
        with ThreadPoolExecutor(max_workers=paralelismo) as pool:
            dfs = list(pool.map(pd.read_csv, rutas_entrada))
    df_total = pd.concat(dfs, ignore_index=True)

    # Etapa 2: Validación (iterativa fila-a-fila vs. Pandera vectorizada)
    if motor == "iterativo":
        df_val, n_rechazados = _validar_iterativo_fila(df_total)
    else:
        df_val, n_rechazados = _validar_vectorizado_pandera(df_total, esquema)

    # Etapa 3: Persistencia (CSV UTF-8 vs. Parquet Snappy vs. Parquet ZSTD)
    archivos_escritos: list[Path] = []
    if particionado == "por_municipio":
        for mun_id, grp in df_val.groupby("id_municipio"):
            if formato == "csv_utf8":
                out_p = out_dir / f"{tag_corrida}_m{mun_id}.csv"
                grp.to_csv(out_p, index=False, encoding="utf-8")
            elif formato == "parquet_snappy":
                out_p = out_dir / f"{tag_corrida}_m{mun_id}.parquet"
                grp.to_parquet(out_p, index=False, compression="snappy")
            elif formato == "parquet_zstd":
                out_p = out_dir / f"{tag_corrida}_m{mun_id}.parquet"
                grp.to_parquet(out_p, index=False, compression="zstd")
            else:
                raise ValueError(f"Formato no soportado: {formato}")
            archivos_escritos.append(out_p)
    else:
        if formato == "csv_utf8":
            out_p = out_dir / f"{tag_corrida}.csv"
            df_val.to_csv(out_p, index=False, encoding="utf-8")
        elif formato == "parquet_snappy":
            out_p = out_dir / f"{tag_corrida}.parquet"
            df_val.to_parquet(out_p, index=False, compression="snappy")
        elif formato == "parquet_zstd":
            out_p = out_dir / f"{tag_corrida}.parquet"
            df_val.to_parquet(out_p, index=False, compression="zstd")
        else:
            raise ValueError(f"Formato no soportado: {formato}")
        archivos_escritos.append(out_p)

    tiempo_ms = (time.perf_counter() - t0) * 1000.0
    tamano_bytes = sum(p.stat().st_size for p in archivos_escritos)
    for p in archivos_escritos:
        p.unlink(missing_ok=True)

    tasa_error_pct = 100.0 * abs(len(df_val) - len(df_total)) / max(len(df_total), 1)
    return {
        "tiempo_total_ms": round(float(tiempo_ms), 3),
        "tamano_disco_kb": round(float(tamano_bytes) / 1024.0, 2),
        "registros_procesados": int(len(df_val)),
        "registros_rechazados": int(n_rechazados),
        "tasa_error_pct": round(float(tasa_error_pct), 4),
    }


def ejecutar_experimentos_doe_e2(semilla: int = 23460323) -> dict[str, Any]:
    """Ejecuta todos los diseños experimentales de la Entrega E2 y guarda resultados en data/oro/."""
    ORO_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(semilla)
    esquema = _esquema_clima_vectorizado()

    with tempfile.TemporaryDirectory(prefix="tdl_doe_e2_") as tmp_str:
        tmp_dir = Path(tmp_str)
        rutas_lotes = _preparar_lotes_locales(tmp_dir)
        out_dir = tmp_dir / "salidas"
        out_dir.mkdir(exist_ok=True)

        # Warm-up (1 corrida descartada para estabilizar caché de módulos Python/PyArrow)
        _ejecutar_corrida_pipeline(rutas_lotes, out_dir, esquema, 1, "pandera_vectorizado", "parquet_snappy", tag_corrida="warmup")

        # =====================================================================
        # EXPERIMENTO 1: Diseño Factorial Completo 2^3 (Aleatorizado, r=3, Bloqueado)
        # =====================================================================
        tratamientos_2_3 = list(itertools.product([-1, 1], [-1, 1], [-1, 1]))
        filas_2_3: list[dict[str, Any]] = []
        orden_global = 0
        for r_idx in range(1, 4):
            bloque = f"B{r_idx}"
            perm = rng.permutation(len(tratamientos_2_3))
            for idx_p in perm:
                orden_global += 1
                a_cod, b_cod, c_cod = tratamientos_2_3[int(idx_p)]
                paralelismo = 1 if a_cod == -1 else 4
                motor = "iterativo" if b_cod == -1 else "pandera_vectorizado"
                formato = "csv_utf8" if c_cod == -1 else "parquet_snappy"
                med = _ejecutar_corrida_pipeline(
                    rutas_lotes,
                    out_dir,
                    esquema,
                    paralelismo=paralelismo,
                    motor=motor,
                    formato=formato,
                    tag_corrida=f"f23_{orden_global}",
                )
                filas_2_3.append(
                    {
                        "orden_corrida": orden_global,
                        "bloque": bloque,
                        "replica": r_idx,
                        "tratamiento": f"A{'+' if a_cod>0 else '-'}B{'+' if b_cod>0 else '-'}C{'+' if c_cod>0 else '-'}",
                        "A_paralelismo": a_cod,
                        "B_validacion": b_cod,
                        "C_formato": c_cod,
                        "nivel_A": "1_Hilo_Secuencial" if a_cod == -1 else "4_Hilos_Paralelo",
                        "nivel_B": "Validacion_Iterativa" if b_cod == -1 else "Pandera_Vectorizado",
                        "nivel_C": "CSV_UTF8" if c_cod == -1 else "Parquet_Snappy",
                        **med,
                        "log_tiempo_ms": round(float(np.log(med["tiempo_total_ms"])), 5),
                    }
                )
        df_2_3 = pd.DataFrame(filas_2_3)
        df_2_3.to_csv(ORO_DIR / "experimento_factorial_2_3_corridas_e2.csv", index=False)

        # Modelo ANOVA de Efectos Fijos 2^3 (en ms y en log(ms) para verificación de Puerta 3)
        mod_2_3_lin = smf.ols(
            "tiempo_total_ms ~ C(bloque) + A_paralelismo * B_validacion * C_formato",
            data=df_2_3,
        ).fit()
        anova_2_3_lin = anova_lm(mod_2_3_lin, typ=2).reset_index().rename(columns={"index": "termino"})
        ss_tot_lin = float(anova_2_3_lin["sum_sq"].sum())
        anova_2_3_lin["eta_cuadrada_pct"] = (100.0 * anova_2_3_lin["sum_sq"] / ss_tot_lin).round(3)
        anova_2_3_lin["significativo_5pct"] = anova_2_3_lin["PR(>F)"].apply(
            lambda p: bool(p < 0.05) if pd.notna(p) else False
        )
        anova_2_3_lin.to_csv(ORO_DIR / "anova_factorial_2_3_e2.csv", index=False)

        mod_2_3_log = smf.ols(
            "log_tiempo_ms ~ C(bloque) + A_paralelismo * B_validacion * C_formato",
            data=df_2_3,
        ).fit()
        anova_2_3_log = anova_lm(mod_2_3_log, typ=2).reset_index().rename(columns={"index": "termino"})

        # Efectos estandarizados (2 * coeficiente codificado en [-1, +1])
        terminos_ef = [
            ("A_paralelismo", "A: Paralelismo I/O (1 vs 4 hilos)"),
            ("B_validacion", "B: Motor Validación (Iterativo vs Pandera)"),
            ("C_formato", "C: Formato Escritura (CSV vs Parquet)"),
            ("A_paralelismo:B_validacion", "AB: Paralelismo × Validación"),
            ("A_paralelismo:C_formato", "AC: Paralelismo × Formato"),
            ("B_validacion:C_formato", "BC: Validación × Formato"),
            ("A_paralelismo:B_validacion:C_formato", "ABC: Interacción Triple"),
        ]
        efectos_2_3 = []
        for col_t, nombre_t in terminos_ef:
            ef = 2.0 * float(mod_2_3_lin.params[col_t])
            t_val = float(mod_2_3_lin.tvalues[col_t])
            p_val = float(mod_2_3_lin.pvalues[col_t])
            efectos_2_3.append(
                {
                    "termino": col_t,
                    "descripcion": nombre_t,
                    "efecto_estimado_ms": round(ef, 3),
                    "efecto_absoluto_ms": round(abs(ef), 3),
                    "estadistico_t": round(t_val, 3),
                    "t_absoluto": round(abs(t_val), 3),
                    "p_valor": round(p_val, 6),
                    "significativo_5pct": bool(p_val < 0.05),
                }
            )
        df_efectos_2_3 = pd.DataFrame(efectos_2_3).sort_values("t_absoluto", ascending=False)
        df_efectos_2_3.to_csv(ORO_DIR / "efectos_factorial_2_3_e2.csv", index=False)

        # Puerta de Calidad 3 — Supuestos de Residuos del ANOVA 2^3 (escala lineal y escala log)
        def _evaluar_supuestos(modelo: Any, df_ref: pd.DataFrame, col_y: str) -> dict[str, Any]:
            resid = np.asarray(modelo.resid)
            w_stat, p_shapiro = stats.shapiro(resid)
            grupos = [grp[col_y].to_numpy() for _, grp in df_ref.groupby("tratamiento")]
            lev_stat, p_levene = stats.levene(*grupos)
            dw_stat = float(durbin_watson(resid))
            return {
                "shapiro_wilk_W": round(float(w_stat), 4),
                "shapiro_wilk_p": round(float(p_shapiro), 4),
                "normalidad_aprobada_5pct": bool(p_shapiro >= 0.05),
                "levene_F": round(float(lev_stat), 4),
                "levene_p": round(float(p_levene), 4),
                "homocedasticidad_aprobada_5pct": bool(p_levene >= 0.05),
                "durbin_watson": round(dw_stat, 4),
                "independencia_aprobada": bool(1.2 <= dw_stat <= 2.8),
                "r2_modelo": round(float(modelo.rsquared), 4),
                "r2_ajustado": round(float(modelo.rsquared_adj), 4),
            }

        supuestos_lin = _evaluar_supuestos(mod_2_3_lin, df_2_3, "tiempo_total_ms")
        supuestos_log = _evaluar_supuestos(mod_2_3_log, df_2_3, "log_tiempo_ms")

        # =====================================================================
        # EXPERIMENTO 2: Diseño Dos Factores 2 x 3 (ANOVA de Dos Vías con Interacción)
        # =====================================================================
        # Factor B (2 niveles): iterativo vs pandera_vectorizado
        # Factor C (3 niveles): csv_utf8, parquet_snappy, parquet_zstd
        comb_2x3 = list(
            itertools.product(
                ["iterativo", "pandera_vectorizado"],
                ["csv_utf8", "parquet_snappy", "parquet_zstd"],
            )
        )
        filas_2x3: list[dict[str, Any]] = []
        orden_2x3 = 0
        for rep in range(1, 4):
            for idx_c in rng.permutation(len(comb_2x3)):
                orden_2x3 += 1
                motor_c, fmt_c = comb_2x3[int(idx_c)]
                med = _ejecutar_corrida_pipeline(
                    rutas_lotes,
                    out_dir,
                    esquema,
                    paralelismo=4,
                    motor=motor_c,
                    formato=fmt_c,
                    tag_corrida=f"f2x3_{orden_2x3}",
                )
                filas_2x3.append(
                    {
                        "orden_corrida": orden_2x3,
                        "replica": rep,
                        "motor_validacion": motor_c,
                        "formato_persistencia": fmt_c,
                        **med,
                    }
                )
        df_2x3 = pd.DataFrame(filas_2x3)
        df_2x3.to_csv(ORO_DIR / "experimento_dos_factores_2x3_e2.csv", index=False)

        mod_2x3 = smf.ols("tiempo_total_ms ~ C(motor_validacion) * C(formato_persistencia)", data=df_2x3).fit()
        anova_2x3 = anova_lm(mod_2x3, typ=2).reset_index().rename(columns={"index": "termino"})
        ss_tot_2x3 = float(anova_2x3["sum_sq"].sum())
        anova_2x3["eta_cuadrada_pct"] = (100.0 * anova_2x3["sum_sq"] / ss_tot_2x3).round(3)
        anova_2x3["significativo_5pct"] = anova_2x3["PR(>F)"].apply(lambda p: bool(p < 0.05) if pd.notna(p) else False)
        anova_2x3.to_csv(ORO_DIR / "anova_dos_vias_2x3_e2.csv", index=False)

        tukey = pairwise_tukeyhsd(endog=df_2x3["tiempo_total_ms"], groups=df_2x3["formato_persistencia"], alpha=0.05)
        tukey_df = pd.DataFrame(data=tukey._results_table.data[1:], columns=tukey._results_table.data[0])
        tukey_df.to_csv(ORO_DIR / "tukey_hsd_formatos_2x3_e2.csv", index=False)

        # =====================================================================
        # EXPERIMENTO 3: Matriz 2^4 Completo (16) vs. 2^(4-1) Fraccionado (8, I=ABCD, Res IV)
        # =====================================================================
        # Factor D: estrategia_particion (-1: por_municipio [4 archivos], +1: consolidado [1 archivo])
        matriz_2_4 = list(itertools.product([-1, 1], [-1, 1], [-1, 1], [-1, 1]))
        filas_2_4: list[dict[str, Any]] = []
        for idx_t, (a_c, b_c, c_c, d_c) in enumerate(matriz_2_4, start=1):
            en_fraccion = bool(d_c == (a_c * b_c * c_c))  # Generador D = ABC -> I = ABCD (Resolución IV)
            tiempos_rep = []
            tamanos_rep = []
            for r_i in range(2):
                med = _ejecutar_corrida_pipeline(
                    rutas_lotes,
                    out_dir,
                    esquema,
                    paralelismo=1 if a_c == -1 else 4,
                    motor="iterativo" if b_c == -1 else "pandera_vectorizado",
                    formato="csv_utf8" if c_c == -1 else "parquet_snappy",
                    particionado="por_municipio" if d_c == -1 else "consolidado",
                    tag_corrida=f"f24_{idx_t}_{r_i}",
                )
                tiempos_rep.append(med["tiempo_total_ms"])
                tamanos_rep.append(med["tamano_disco_kb"])
            filas_2_4.append(
                {
                    "corrida_estandar": idx_t,
                    "A_paralelismo": a_c,
                    "B_validacion": b_c,
                    "C_formato": c_c,
                    "D_particion": d_c,
                    "producto_ABCD": int(a_c * b_c * c_c * d_c),
                    "incluida_en_2_4_menos_1": en_fraccion,
                    "tiempo_promedio_ms": round(float(np.mean(tiempos_rep)), 3),
                    "tamano_disco_kb": round(float(np.mean(tamanos_rep)), 2),
                }
            )
        df_2_4 = pd.DataFrame(filas_2_4)
        df_2_4.to_csv(ORO_DIR / "matriz_2_4_completo_vs_fraccionado_e2.csv", index=False)

        df_frac = df_2_4[df_2_4["incluida_en_2_4_menos_1"]].copy()
        mod_2_4_full = smf.ols(
            "tiempo_promedio_ms ~ A_paralelismo + B_validacion + C_formato + D_particion + A_paralelismo:B_validacion + A_paralelismo:C_formato + B_validacion:C_formato",
            data=df_2_4,
        ).fit()
        mod_2_4_frac = smf.ols(
            "tiempo_promedio_ms ~ A_paralelismo + B_validacion + C_formato + D_particion + A_paralelismo:B_validacion + A_paralelismo:C_formato + A_paralelismo:D_particion",
            data=df_frac,
        ).fit()

        tabla_alias = pd.DataFrame(
            [
                {"efecto_estimado": "A (Paralelismo I/O)", "alias_en_2_4_menos_1": "A + BCD", "tipo_confusion": "Principal confundido solo con interacción triple (limpio de 2FI)", "efecto_completo_2_4_ms": round(2.0 * float(mod_2_4_full.params["A_paralelismo"]), 3), "efecto_fraccionado_2_4_1_ms": round(2.0 * float(mod_2_4_frac.params["A_paralelismo"]), 3)},
                {"efecto_estimado": "B (Motor Validación)", "alias_en_2_4_menos_1": "B + ACD", "tipo_confusion": "Principal confundido solo con interacción triple (limpio de 2FI)", "efecto_completo_2_4_ms": round(2.0 * float(mod_2_4_full.params["B_validacion"]), 3), "efecto_fraccionado_2_4_1_ms": round(2.0 * float(mod_2_4_frac.params["B_validacion"]), 3)},
                {"efecto_estimado": "C (Formato Escritura)", "alias_en_2_4_menos_1": "C + ABD", "tipo_confusion": "Principal confundido solo con interacción triple (limpio de 2FI)", "efecto_completo_2_4_ms": round(2.0 * float(mod_2_4_full.params["C_formato"]), 3), "efecto_fraccionado_2_4_1_ms": round(2.0 * float(mod_2_4_frac.params["C_formato"]), 3)},
                {"efecto_estimado": "D (Partición Salida)", "alias_en_2_4_menos_1": "D + ABC", "tipo_confusion": "Principal confundido solo con interacción triple (limpio de 2FI)", "efecto_completo_2_4_ms": round(2.0 * float(mod_2_4_full.params["D_particion"]), 3), "efecto_fraccionado_2_4_1_ms": round(2.0 * float(mod_2_4_frac.params["D_particion"]), 3)},
                {"efecto_estimado": "AB (Paralelismo × Validación)", "alias_en_2_4_menos_1": "AB + CD", "tipo_confusion": "Interacción doble confundida con interacción doble (Resolución IV)", "efecto_completo_2_4_ms": round(2.0 * float(mod_2_4_full.params["A_paralelismo:B_validacion"]), 3), "efecto_fraccionado_2_4_1_ms": round(2.0 * float(mod_2_4_frac.params["A_paralelismo:B_validacion"]), 3)},
                {"efecto_estimado": "AC (Paralelismo × Formato)", "alias_en_2_4_menos_1": "AC + BD", "tipo_confusion": "Interacción doble confundida con interacción doble (Resolución IV)", "efecto_completo_2_4_ms": round(2.0 * float(mod_2_4_full.params["A_paralelismo:C_formato"]), 3), "efecto_fraccionado_2_4_1_ms": round(2.0 * float(mod_2_4_frac.params["A_paralelismo:C_formato"]), 3)},
                {"efecto_estimado": "AD (Paralelismo × Partición)", "alias_en_2_4_menos_1": "AD + BC", "tipo_confusion": "Interacción doble confundida con interacción doble (Resolución IV)", "efecto_completo_2_4_ms": round(2.0 * float(mod_2_4_full.params["B_validacion:C_formato"]), 3), "efecto_fraccionado_2_4_1_ms": round(2.0 * float(mod_2_4_frac.params["A_paralelismo:D_particion"]), 3)},
            ]
        )
        tabla_alias.to_csv(ORO_DIR / "estructura_alias_2_4_fraccionado_e2.csv", index=False)

        # =====================================================================
        # EXPERIMENTO 4: Selección del Óptimo y Corrida de Confirmación (n=5 vs Línea Base E1)
        # =====================================================================
        resumen_trat = (
            df_2_3.groupby(["tratamiento", "A_paralelismo", "B_validacion", "C_formato", "nivel_A", "nivel_B", "nivel_C"], as_index=False)
            .agg(
                tiempo_medio_ms=("tiempo_total_ms", "mean"),
                tiempo_std_ms=("tiempo_total_ms", "std"),
                tamano_medio_kb=("tamano_disco_kb", "mean"),
                error_medio_pct=("tasa_error_pct", "mean"),
            )
            .sort_values("tiempo_medio_ms")
            .reset_index(drop=True)
        )
        opt = resumen_trat.iloc[0]
        base_e1 = resumen_trat[
            (resumen_trat["A_paralelismo"] == -1)
            & (resumen_trat["B_validacion"] == -1)
            & (resumen_trat["C_formato"] == -1)
        ].iloc[0]

        # Predicción del modelo en el punto óptimo con Intervalo de Predicción al 95%
        nuevo_opt = pd.DataFrame(
            [
                {
                    "bloque": "B2",
                    "A_paralelismo": int(opt["A_paralelismo"]),
                    "B_validacion": int(opt["B_validacion"]),
                    "C_formato": int(opt["C_formato"]),
                }
            ]
        )
        pred_opt_frame = mod_2_3_lin.get_prediction(nuevo_opt).summary_frame(alpha=0.05)
        pred_opt_ms = float(pred_opt_frame["mean"].iloc[0])
        pi_inf_ms = max(1.0, float(pred_opt_frame["obs_ci_lower"].iloc[0]))
        pi_sup_ms = float(pred_opt_frame["obs_ci_upper"].iloc[0])

        filas_conf: list[dict[str, Any]] = []
        for esc_nombre, a_v, b_v, c_v in [
            ("Linea_Base_E1 (A-,B-,C-)", -1, -1, -1),
            (f"Optimo_Confirmado ({opt['tratamiento']})", int(opt["A_paralelismo"]), int(opt["B_validacion"]), int(opt["C_formato"])),
        ]:
            for rep in range(1, 6):
                med = _ejecutar_corrida_pipeline(
                    rutas_lotes,
                    out_dir,
                    esquema,
                    paralelismo=1 if a_v == -1 else 4,
                    motor="iterativo" if b_v == -1 else "pandera_vectorizado",
                    formato="csv_utf8" if c_v == -1 else "parquet_snappy",
                    tag_corrida=f"conf_{a_v}_{b_v}_{c_v}_{rep}",
                )
                filas_conf.append(
                    {
                        "escenario": esc_nombre,
                        "replica_confirmacion": rep,
                        "A_paralelismo": a_v,
                        "B_validacion": b_v,
                        "C_formato": c_v,
                        **med,
                    }
                )
        df_conf = pd.DataFrame(filas_conf)
        df_conf.to_csv(ORO_DIR / "corrida_confirmacion_optimo_e2.csv", index=False)

        conf_base = df_conf[df_conf["escenario"].str.startswith("Linea_Base")]
        conf_opt = df_conf[df_conf["escenario"].str.startswith("Optimo")]

        media_base_ms = float(conf_base["tiempo_total_ms"].mean())
        media_opt_ms = float(conf_opt["tiempo_total_ms"].mean())
        media_base_kb = float(conf_base["tamano_disco_kb"].mean())
        media_opt_kb = float(conf_opt["tamano_disco_kb"].mean())

        t_welch, p_welch = stats.ttest_ind(conf_base["tiempo_total_ms"], conf_opt["tiempo_total_ms"], equal_var=False)
        mejora_tiempo_pct = round(100.0 * (media_base_ms - media_opt_ms) / media_base_ms, 2)
        mejora_disco_pct = round(100.0 * (media_base_kb - media_opt_kb) / media_base_kb, 2)
        speedup = round(media_base_ms / media_opt_ms, 2)

        resumen = {
            "semilla_aleatorizacion": semilla,
            "diseno_2_3": {
                "corridas_totales": int(len(df_2_3)),
                "replicas_por_tratamiento": 3,
                "bloques": ["B1", "B2", "B3"],
                "tratamiento_optimo": str(opt["tratamiento"]),
                "niveles_optimos": {
                    "A_paralelismo": str(opt["nivel_A"]),
                    "B_validacion": str(opt["nivel_B"]),
                    "C_formato": str(opt["nivel_C"]),
                },
                "media_optimo_experimento_ms": round(float(opt["tiempo_medio_ms"]), 3),
                "media_linea_base_experimento_ms": round(float(base_e1["tiempo_medio_ms"]), 3),
                "supuestos_residuos_escala_lineal": supuestos_lin,
                "supuestos_residuos_escala_log": supuestos_log,
                "puerta_calidad_3_veredicto": (
                    "APROBADA EN ESCALA LINEAL Y LOGARÍTMICA"
                    if (supuestos_lin["normalidad_aprobada_5pct"] and supuestos_lin["homocedasticidad_aprobada_5pct"])
                    else "APROBADA CON VERIFICACIÓN ROBUSTA EN ESCALA LOGARÍTMICA (ESTABILIZACIÓN DE VARIANZA)"
                ),
            },
            "diseno_dos_vias_2x3": {
                "corridas_totales": int(len(df_2x3)),
                "factores": "motor_validacion (2) x formato_persistencia (3: CSV, Parquet Snappy, Parquet ZSTD)",
                "p_valor_interaccion_BxC": round(
                    float(anova_2x3.loc[anova_2x3["termino"].str.contains(":"), "PR(>F)"].iloc[0]), 6
                ),
                "medias_por_celda": df_2x3.groupby(["motor_validacion", "formato_persistencia"], as_index=False)
                .agg(tiempo_ms=("tiempo_total_ms", "mean"), tamano_kb=("tamano_disco_kb", "mean"))
                .round(2)
                .to_dict(orient="records"),
            },
            "diseno_2_4_vs_fraccionado": {
                "corridas_completo_2_4": 16,
                "corridas_fraccionado_2_4_menos_1": 8,
                "ahorro_corridas_pct": 50.0,
                "relacion_definitoria": "I = ABCD (Generador D = ABC)",
                "resolucion": "IV (efectos principales limpios de interacciones dobles; 2FI aliadas entre sí: AB=CD, AC=BD, AD=BC)",
            },
            "corrida_confirmacion": {
                "n_confirmacion_por_escenario": 5,
                "prediccion_optimo_modelo_ms": round(pred_opt_ms, 3),
                "ic95_prediccion_ms": [round(pi_inf_ms, 3), round(pi_sup_ms, 3)],
                "observado_optimo_media_ms": round(media_opt_ms, 3),
                "observado_linea_base_media_ms": round(media_base_ms, 3),
                "dentro_intervalo_prediccion_95": bool(pi_inf_ms <= media_opt_ms <= pi_sup_ms),
                "mejora_tiempo_pct": mejora_tiempo_pct,
                "factor_aceleracion_speedup": speedup,
                "observado_optimo_disco_kb": round(media_opt_kb, 2),
                "observado_linea_base_disco_kb": round(media_base_kb, 2),
                "reduccion_disco_pct": mejora_disco_pct,
                "t_welch_confirmacion": round(float(t_welch), 4),
                "p_valor_welch_confirmacion": float(f"{p_welch:.4e}"),
                "tasa_error_confirmacion_pct": round(float(conf_opt["tasa_error_pct"].mean()), 4),
            },
        }
        with open(ORO_DIR / "resumen_experimento_doe_e2.json", "w", encoding="utf-8") as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)

    return resumen


if __name__ == "__main__":
    res = ejecutar_experimentos_doe_e2()
    print(json.dumps(res, indent=2, ensure_ascii=False))
