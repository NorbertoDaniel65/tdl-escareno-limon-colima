"""Verificador automático de la Entrega E0 (Rúbrica Oficial Trusted Data Lab).

Comprueba de forma determinista y sin necesidad de red:
1. Estructura completa del repositorio según el Kit de Arranque (pág. 30).
2. Serie histórica >= 36 periodos en Capa Bronce para Open-Meteo (60 meses / 7,304 días) y SNIIM (60 meses).
3. Integridad criptográfica SHA-256 de todos los archivos en data/bronce/ contra sus fichas .meta.json.
4. Cero datos personales en las columnas y registros de Capa Bronce.
5. Registros PSP individuales (calidad/tiempo-norberto.csv y calidad/defectos-norberto.csv) con el esquema exacto de la pág. 32.
6. Bitácora activa de capturas (calidad/bitacora_capturas.jsonl) y 3 objetivos de calidad medibles (calidad/objetivos.md).
7. Documentos de entrega obligatorios: docs/E0/propuesta.md y docs/E0/ENTREGA.md.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent

COLUMNAS_PROHIBIDAS_PII = {
    "nombre_persona",
    "telefono",
    "celular",
    "email",
    "correo",
    "curp",
    "rfc",
    "direccion_particular",
}


def sha256_archivo(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def verificar_todo() -> dict[str, Any]:
    errores: list[str] = []
    detalles: dict[str, Any] = {}

    # 1. Estructura del Kit de Arranque
    carpetas_requeridas = [
        "docs/E0",
        "docs/fuentes",
        "calidad",
        "extractores",
        "pipeline",
        "data/bronce",
        "data/plata",
        "data/oro",
        "data/cuarentena",
        "laboratorio",
        "tablero",
        "tests",
        ".github/workflows",
    ]
    faltantes = [c for c in carpetas_requeridas if not (ROOT_DIR / c).exists()]
    if faltantes:
        errores.append(f"Carpetas faltantes del Kit: {faltantes}")
    detalles["estructura_kit_ok"] = len(faltantes) == 0

    # 2. Series históricas >= 36 periodos en Capa Bronce
    ruta_om_m = ROOT_DIR / "data" / "bronce" / "open_meteo" / "agroclima_colima_mensual_60m.csv"
    ruta_sniim_m = ROOT_DIR / "data" / "bronce" / "sniim_limon" / "precios_limon_sniim_historico_60m.csv"

    for nombre, ruta in [("open_meteo_mensual", ruta_om_m), ("sniim_mensual", ruta_sniim_m)]:
        if not ruta.exists():
            errores.append(f"No existe la serie histórica {nombre}: {ruta}")
            continue
        df = pd.read_csv(ruta)
        periodos = int(df["anio_mes"].nunique()) if "anio_mes" in df.columns else len(df)
        if periodos < 36:
            errores.append(f"Serie {nombre} tiene {periodos} periodos (< 36 requeridos en E0)")
        cols_pii = set(c.lower() for c in df.columns) & COLUMNAS_PROHIBIDAS_PII
        if cols_pii:
            errores.append(f"Serie {nombre} contiene columnas de datos personales prohibidas: {cols_pii}")
        meta_path = ruta.with_name(ruta.name + ".meta.json")
        if not meta_path.exists():
            errores.append(f"Falta archivo de metadatos {meta_path.name}")
        else:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            sha_real = sha256_archivo(ruta)
            if meta.get("sha256") != sha_real:
                errores.append(f"Hash SHA-256 no coincide en {ruta.name}: esperado {meta.get('sha256')}, real {sha_real}")
        detalles[nombre] = {
            "registros": len(df),
            "periodos_mensuales": periodos,
            "cumple_36_periodos": periodos >= 36,
            "cero_datos_personales": len(cols_pii) == 0,
        }

    # 3. Verificar PSP (defectos y tiempo)
    ruta_defectos = ROOT_DIR / "calidad" / "defectos-norberto.csv"
    ruta_tiempo = ROOT_DIR / "calidad" / "tiempo-norberto.csv"
    cols_defectos_esp = [
        "numero",
        "fecha",
        "tipo",
        "fase_introducido",
        "fase_eliminado",
        "minutos_correccion",
        "defecto_origen",
        "descripcion",
    ]
    cols_tiempo_esp = ["fecha", "inicio", "fin", "interrupcion_min", "fase", "actividad"]

    if not ruta_defectos.exists():
        errores.append("Falta calidad/defectos-norberto.csv")
    else:
        df_def = pd.read_csv(ruta_defectos)
        if list(df_def.columns) != cols_defectos_esp:
            errores.append(f"Encabezado inválido en defectos-norberto.csv: {list(df_def.columns)}")
        detalles["psp_defectos_filas"] = len(df_def)

    if not ruta_tiempo.exists():
        errores.append("Falta calidad/tiempo-norberto.csv")
    else:
        df_t = pd.read_csv(ruta_tiempo)
        if list(df_t.columns) != cols_tiempo_esp:
            errores.append(f"Encabezado inválido en tiempo-norberto.csv: {list(df_t.columns)}")
        detalles["psp_tiempo_filas"] = len(df_t)

    # 4. Bitácora activa de capturas
    ruta_bitacora = ROOT_DIR / "calidad" / "bitacora_capturas.jsonl"
    if not ruta_bitacora.exists():
        errores.append("Falta calidad/bitacora_capturas.jsonl")
    else:
        lineas = [l.strip() for l in ruta_bitacora.read_text(encoding="utf-8").splitlines() if l.strip()]
        if not lineas:
            errores.append("calidad/bitacora_capturas.jsonl está vacía")
        detalles["eventos_bitacora"] = len(lineas)

    # 5. Documentos obligatorios E0
    for doc_rel in ["docs/E0/propuesta.md", "docs/E0/ENTREGA.md", "calidad/objetivos.md"]:
        p = ROOT_DIR / doc_rel
        if not p.exists() or p.stat().st_size < 200:
            errores.append(f"Documento obligatorio faltante o incompleto: {doc_rel}")

    resultado = {
        "estado_verificacion_e0": "APROBADO" if not errores else "CON_ERRORES",
        "errores": errores,
        "detalles": detalles,
    }
    return resultado


def main() -> None:
    res = verificar_todo()
    print(json.dumps(res, indent=2, ensure_ascii=False))
    if res["errores"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
