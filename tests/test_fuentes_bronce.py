"""Pruebas de integridad, horizonte histórico (>= 36 periodos) y cero datos personales en Capa Bronce."""
from __future__ import annotations

import json
from pathlib import Path
import pandas as pd

from pipeline.verificar_e0 import COLUMNAS_PROHIBIDAS_PII, ROOT_DIR, sha256_archivo, verificar_todo


def test_serie_historica_open_meteo_cumple_60_meses() -> None:
    ruta = ROOT_DIR / "data" / "bronce" / "open_meteo" / "agroclima_colima_mensual_60m.csv"
    assert ruta.exists(), "Debe existir la serie mensual de Open-Meteo en capa bronce"
    df = pd.read_csv(ruta)
    assert df["anio_mes"].nunique() >= 36
    assert df["anio_mes"].nunique() == 60
    assert set(df["municipio"].unique()) == {"Tecoman", "Armeria", "Manzanillo", "Colima"}
    assert len(df) == 240
    assert df.isna().sum().sum() == 0


def test_serie_historica_sniim_cumple_60_meses() -> None:
    ruta = ROOT_DIR / "data" / "bronce" / "sniim_limon" / "precios_limon_sniim_historico_60m.csv"
    assert ruta.exists(), "Debe existir la serie histórica de precios SNIIM en capa bronce"
    df = pd.read_csv(ruta)
    assert df["anio_mes"].nunique() >= 36
    assert df["anio_mes"].nunique() == 60
    assert df["id_mercado"].nunique() == 4
    assert len(df) == 240
    assert (df["precio_frecuente_mxn_kg"] > 0).all()


def test_hashes_sha256_coinciden_con_metadatos() -> None:
    for sub in ("open_meteo", "sniim_limon"):
        carpeta = ROOT_DIR / "data" / "bronce" / sub
        for csv_path in carpeta.glob("*.csv"):
            meta_path = csv_path.with_name(csv_path.name + ".meta.json")
            assert meta_path.exists(), f"Falta .meta.json para {csv_path.name}"
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            assert meta["sha256"] == sha256_archivo(csv_path)
            assert meta["datos_personales_incluidos"] is False


def test_cero_datos_personales_en_bronce() -> None:
    for sub in ("open_meteo", "sniim_limon"):
        carpeta = ROOT_DIR / "data" / "bronce" / sub
        for csv_path in carpeta.glob("*.csv"):
            df = pd.read_csv(csv_path, nrows=5)
            inter = {c.lower() for c in df.columns} & COLUMNAS_PROHIBIDAS_PII
            assert not inter, f"Columnas prohibidas detectadas en {csv_path.name}: {inter}"


def test_verificador_integral_e0_aprueba_sin_errores() -> None:
    res = verificar_todo()
    assert res["estado_verificacion_e0"] == "APROBADO"
    assert res["errores"] == []
