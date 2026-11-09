"""Pruebas unitarias para el sistema PSP (tiempo, defectos, bitácora y objetivos de calidad)."""
from __future__ import annotations

import json
import pandas as pd

from pipeline.verificar_e0 import ROOT_DIR

TIPOS_PSP_VALIDOS = {
    "documentacion",
    "sintaxis",
    "construccion",
    "asignacion",
    "interfaz",
    "verificacion",
    "datos",
    "funcion",
    "sistema",
    "entorno",
}


def test_registro_defectos_psp_valido() -> None:
    ruta = ROOT_DIR / "calidad" / "defectos-norberto.csv"
    assert ruta.exists()
    df = pd.read_csv(ruta)
    assert list(df.columns) == [
        "numero",
        "fecha",
        "tipo",
        "fase_introducido",
        "fase_eliminado",
        "minutos_correccion",
        "defecto_origen",
        "descripcion",
    ]
    assert len(df) >= 3
    assert set(df["tipo"]).issubset(TIPOS_PSP_VALIDOS)
    assert (df["minutos_correccion"] > 0).all()


def test_registro_tiempo_psp_valido() -> None:
    ruta = ROOT_DIR / "calidad" / "tiempo-norberto.csv"
    assert ruta.exists()
    df = pd.read_csv(ruta)
    assert list(df.columns) == [
        "fecha",
        "inicio",
        "fin",
        "interrupcion_min",
        "fase",
        "actividad",
    ]
    assert len(df) >= 4
    assert (df["interrupcion_min"] >= 0).all()


def test_bitacora_capturas_jsonl_activa() -> None:
    ruta = ROOT_DIR / "calidad" / "bitacora_capturas.jsonl"
    assert ruta.exists()
    lineas = [l.strip() for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(lineas) >= 4
    for linea in lineas:
        obj = json.loads(linea)
        assert "timestamp_utc" in obj
        assert "fuente" in obj
        assert obj["estado"] == "EXITO"
        assert obj["registros_capturados"] > 0
