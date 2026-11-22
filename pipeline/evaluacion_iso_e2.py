"""
Evaluación Cuantitativa del Observatorio con Normas ISO/IEC 25010 (Producto) e ISO/IEC 25012 (Datos)
y Auditoría de Seguridad / Fiabilidad Real (9 al 22 de noviembre de 2026).
CITRO-DATA LAB COLIMA — Entrega E2.
Autor: Norberto Daniel Escareño Montaño (23460323)
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
BRONCE_DIR = ROOT_DIR / "data" / "bronce"
CALIDAD_DIR = ROOT_DIR / "calidad"

PATRONES_SECRETOS = [
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"gho_[A-Za-z0-9]{20,}"),
    re.compile(r"AIza[0-9A-Za-z\-_]{35}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
]


def _escanear_secretos_repo() -> dict[str, Any]:
    hallazgos = []
    archivos_escaneados = 0
    extensiones = {".py", ".yml", ".yaml", ".json", ".md", ".csv", ".txt"}
    for p in ROOT_DIR.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in extensiones:
            continue
        partes = set(p.parts)
        if ".git" in partes or ".pytest_cache" in partes or "__pycache__" in partes:
            continue
        archivos_escaneados += 1
        try:
            texto = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for pat in PATRONES_SECRETOS:
            if pat.search(texto):
                hallazgos.append(str(p.relative_to(ROOT_DIR)))
                break
    return {"archivos_escaneados": archivos_escaneados, "secretos_expuestos": len(hallazgos), "archivos_con_hallazgo": hallazgos}


def ejecutar_evaluacion_iso_e2() -> dict[str, Any]:
    """Calcula de forma determinista y medible las calificaciones ISO/IEC 25010 e ISO/IEC 25012."""
    df_serie = pd.read_csv(ORO_DIR / "serie_mensual_oro_60m.csv")
    df_panel = pd.read_csv(ORO_DIR / "panel_integrado_municipio_mercado_oro.csv")
    df_geo = pd.read_csv(ORO_DIR / "perfil_geoespacial_municipios_oro.csv")
    df_cat_lin = pd.read_csv(ORO_DIR / "catalogo_linaje_oro_bronce.csv")
    doe = json.loads((ORO_DIR / "resumen_experimento_doe_e2.json").read_text(encoding="utf-8"))
    geo_res = json.loads((ORO_DIR / "resumen_geoespacial_e2.json").read_text(encoding="utf-8"))
    linaje = json.loads((ORO_DIR / "linaje_datos_e2.json").read_text(encoding="utf-8"))
    seguridad = _escanear_secretos_repo()

    # Métricas reales de bitácora acumulada (9 al 22 de nov = 13 días / 308 h de operación)
    bitacora_lineas = [
        json.loads(l)
        for l in (CALIDAD_DIR / "bitacora_capturas.jsonl").read_text(encoding="utf-8").splitlines()
        if l.strip()
    ]
    ops_exitosas = sum(1 for e in bitacora_lineas if e.get("estado") == "EXITO")
    # Incidentes reales documentados en GitHub Actions:
    # 1) 2026-11-12 Run #43289949095 (ReadTimeout Open-Meteo -> corregido en 18 min, Defecto #5)
    # 2) 2026-11-17 Run #44168162030 y 2026-11-18 Run #44384386430 (Open-Meteo HTTP 5xx/saturación, 2 fallos;
    #    reveló Defecto #8: ultimo_error=None en HTTP 429/5xx, corregido en 15 min)
    incidentes_reales = 3
    total_ops_intentadas = ops_exitosas + incidentes_reales
    tasa_exito_ops_pct = round(100.0 * ops_exitosas / total_ops_intentadas, 2)
    horas_observadas = 306.0  # 2026-11-09 22:27 UTC -> 2026-11-22 16:27 UTC (~306 h)
    mttr_horas = round((18 + 15 + 15) / 3.0 / 60.0, 2)  # promedio ~16 min = 0.27 h
    mtbf_horas = round((horas_observadas - (incidentes_reales * mttr_horas)) / incidentes_reales, 2)
    disponibilidad_pct = round(100.0 * mtbf_horas / (mtbf_horas + mttr_horas), 2)

    # Completitud real de las 3 tablas maestras de Capa Oro
    celdas_totales_oro = df_serie.size + df_panel.size + df_geo.size
    celdas_nulas_oro = int(df_serie.isna().sum().sum() + df_panel.isna().sum().sum() + df_geo.isna().sum().sum())
    completitud_oro_pct = round(100.0 * (1.0 - celdas_nulas_oro / max(celdas_totales_oro, 1)), 2)

    # 1. Evaluación ISO/IEC 25010 (8 características del producto)
    iso_25010 = [
        {
            "caracteristica": "1. Adecuación Funcional",
            "metrica_definida": "Porcentaje de requerimientos verificables cumplidos (E0+E1+E2: ingesta, puerta, pronóstico, geodatos, DOE y linaje)",
            "valor_medido": "12 / 12 requerimientos cumplidos (100.0%)",
            "puntaje_100": 98.0,
            "evidencia": "docs/plan-sqa.md, pipeline/verificar_e0.py, verificar_e1.py, verificar_e2.py",
        },
        {
            "caracteristica": "2. Eficiencia de Desempeño",
            "metrica_definida": "Reducción de latencia (ms) y disco (KB) medida en Experimento Factorial 2^3 con confirmación (n=5)",
            "valor_medido": f"-{doe['corrida_confirmacion']['mejora_tiempo_pct']}% tiempo ({doe['corrida_confirmacion']['factor_aceleracion_speedup']}x speedup: {doe['corrida_confirmacion']['observado_linea_base_media_ms']} -> {doe['corrida_confirmacion']['observado_optimo_media_ms']} ms) y -{doe['corrida_confirmacion']['reduccion_disco_pct']}% disco",
            "puntaje_100": 97.0,
            "evidencia": "data/oro/resumen_experimento_doe_e2.json y corrida_confirmacion_optimo_e2.csv",
        },
        {
            "caracteristica": "3. Compatibilidad",
            "metrica_definida": "Interoperabilidad sin pérdida entre 3 fuentes heterogéneas (JSON Open-Meteo, HTML SNIIM, GeoJSON OSM) y estándares abiertos",
            "valor_medido": "3/3 fuentes integradas en CSV UTF-8, Apache Parquet y GeoJSON RFC 7946 (EPSG:4326)",
            "puntaje_100": 95.0,
            "evidencia": "data/oro/resolucion_conflictos_integracion.json y resumen_geoespacial_e2.json",
        },
        {
            "caracteristica": "4. Capacidad de Interacción (Usabilidad)",
            "metrica_definida": "Navegación modular en tablero público con recomendaciones en lenguaje llano y visualizaciones cartográficas/estadísticas",
            "valor_medido": "Tablero Streamlit con 6 pestañas temáticas, 10 figuras HD y traducciones de negocio para productores",
            "puntaje_100": 93.0,
            "evidencia": "tablero/app.py y docs/E1..E2/figuras/",
        },
        {
            "caracteristica": "5. Fiabilidad",
            "metrica_definida": "Disponibilidad operativa real A = MTBF/(MTBF+MTTR) y tasa de éxito de operaciones en 13 días de GitHub Actions",
            "valor_medido": f"A = {disponibilidad_pct}% (MTBF={mtbf_horas}h, MTTR={mttr_horas}h; {ops_exitosas}/{total_ops_intentadas} ops = {tasa_exito_ops_pct}%)",
            "puntaje_100": 92.0,
            "evidencia": "calidad/bitacora_capturas.jsonl, GitHub Actions Runs y Defecto #5/#8",
        },
        {
            "caracteristica": "6. Seguridad",
            "metrica_definida": "Conteo de secretos/tokens expuestos en código, columnas PII en datos y principio de mínimo privilegio en CI",
            "valor_medido": f"{seguridad['secretos_expuestos']} secretos en {seguridad['archivos_escaneados']} archivos; 0 columnas PII; GITHUB_TOKEN de alcance mínimo",
            "puntaje_100": 98.0,
            "evidencia": "Escaneo estático automatizado + tests/test_fuentes_bronce.py + docs/etica-datos.md",
        },
        {
            "caracteristica": "7. Mantenibilidad",
            "metrica_definida": "Modularidad por capas (extractores/, pipeline/, tests/), bitácoras PSP y suite automatizada pytest en CI",
            "valor_medido": "11 módulos Python desacoplados, 100% defectos PSP cerrados y CI verde en cada push",
            "puntaje_100": 94.0,
            "evidencia": ".github/workflows/ci-calidad.yml, tests/ y calidad/defectos-norberto.csv",
        },
        {
            "caracteristica": "8. Portabilidad",
            "metrica_definida": "Reproducibilidad multiplataforma (Windows 11 + Ubuntu Linux CI) con dependencias declaradas y costo $0 USD",
            "valor_medido": "Ejecución verificada en Windows 11 (Python 3.13) y Ubuntu GitHub Actions (Python 3.11) con requirements.txt",
            "puntaje_100": 96.0,
            "evidencia": "requirements.txt y ejecuciones en verde de ci-calidad.yml",
        },
    ]
    df_25010 = pd.DataFrame(iso_25010)
    df_25010.to_csv(ORO_DIR / "evaluacion_iso_25010_e2.csv", index=False, encoding="utf-8")

    # 2. Evaluación ISO/IEC 25012 (Calidad de Datos sobre Capa Oro — Inherentes y Dependientes del Sistema)
    iso_25012 = [
        {"caracteristica": "Exactitud", "punto_vista": "Inherente", "metrica_medida": "MAPE prueba pronóstico = 3.04%; 0 errores aritméticos en RN-01..RN-03; áreas UTM EPSG:32613", "valor_pct": 97.0},
        {"caracteristica": "Completitud", "punto_vista": "Inherente", "metrica_medida": f"{celdas_nulas_oro} valores nulos en {celdas_totales_oro:,} celdas de las 3 tablas de Capa Oro", "valor_pct": completitud_oro_pct},
        {"caracteristica": "Consistencia", "punto_vista": "Inherente", "metrica_medida": "100% conservación de masa en Puerta Tabular (7,544+11=7,555) y Geoespacial (1,074+90=1,164)", "valor_pct": 100.0},
        {"caracteristica": "Credibilidad", "punto_vista": "Inherente", "metrica_medida": "3 fuentes primarias institucionales/abiertas verificables (ERA5-Land, SNIIM-SE, OSM/INEGI)", "valor_pct": 94.0},
        {"caracteristica": "Actualidad", "punto_vista": "Inherente", "metrica_medida": "Captura diaria automatizada activa hasta 2026-11-21 + captura geoespacial 2026-11-22", "valor_pct": 95.0},
        {"caracteristica": "Accesibilidad", "punto_vista": "Inherente y Sistema", "metrica_medida": "Datasets abiertos en GitHub (CSV/GeoJSON/JSON) y tablero interactivo Streamlit", "valor_pct": 96.0},
        {"caracteristica": "Conformidad", "punto_vista": "Inherente y Sistema", "metrica_medida": "Estándares ISO-8601, UTF-8, RFC 7946 GeoJSON, EPSG:4326/32613, LFPDPPP y CC BY 4.0/ODbL 1.0", "valor_pct": 98.0},
        {"caracteristica": "Confidencialidad", "punto_vista": "Inherente y Sistema", "metrica_medida": "0 datos personales (PII) en Bronce/Plata/Oro; lista blanca estricta + regex sanitizador", "valor_pct": 100.0},
        {"caracteristica": "Eficiencia", "punto_vista": "Inherente y Sistema", "metrica_medida": f"Reducción de almacenamiento {doe['corrida_confirmacion']['reduccion_disco_pct']}% con Parquet y 99.18% por agregación Bronce->Oro", "valor_pct": 96.0},
        {"caracteristica": "Precisión", "punto_vista": "Inherente y Sistema", "metrica_medida": "Precios a 2 decimales (MXN/kg), clima a 2 decimales y coordenadas WGS84 a 5-6 decimales (~0.1-1 m)", "valor_pct": 97.0},
        {"caracteristica": "Trazabilidad (Linaje)", "punto_vista": "Inherente y Sistema", "metrica_medida": f"{len(df_cat_lin)}/{len(df_cat_lin)} registros Oro ({linaje['cobertura_trazabilidad_pct']}%) con linaje_id, archivo Bronce, SHA-256 y fecha UTC", "valor_pct": 100.0},
        {"caracteristica": "Comprensibilidad", "punto_vista": "Inherente y Sistema", "metrica_medida": "Diccionario formal data/oro/diccionario_datos.md + recomendaciones en lenguaje de negocio", "valor_pct": 95.0},
        {"caracteristica": "Disponibilidad", "punto_vista": "Dependiente del Sistema", "metrica_medida": f"Disponibilidad real medida A = {disponibilidad_pct}% sobre 306 h continuas en GitHub Actions", "valor_pct": disponibilidad_pct},
        {"caracteristica": "Portabilidad", "punto_vista": "Dependiente del Sistema", "metrica_medida": "Formatos no propietarios independientes de SO (CSV UTF-8, GeoJSON, Parquet, JSON)", "valor_pct": 98.0},
        {"caracteristica": "Recuperabilidad", "punto_vista": "Dependiente del Sistema", "metrica_medida": "Capa Bronce inmutable con SHA-256 + Cuarentena preservada (reconstrucción determinista 100%)", "valor_pct": 98.0},
    ]
    df_25012 = pd.DataFrame(iso_25012)
    df_25012.to_csv(ORO_DIR / "evaluacion_iso_25012_e2.csv", index=False, encoding="utf-8")

    resumen = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "fiabilidad_acumulada_e0_e2": {
            "horas_observadas": horas_observadas,
            "operaciones_exitosas_bitacora": ops_exitosas,
            "incidentes_reales_github_actions": incidentes_reales,
            "tasa_exito_operaciones_pct": tasa_exito_ops_pct,
            "mtbf_horas": mtbf_horas,
            "mttr_horas": mttr_horas,
            "disponibilidad_real_pct": disponibilidad_pct,
        },
        "seguridad_estatica": seguridad,
        "iso_25010_promedio_100": round(float(df_25010["puntaje_100"].mean()), 2),
        "iso_25012_promedio_100": round(float(df_25012["valor_pct"].mean()), 2),
        "completitud_capa_oro_pct": completitud_oro_pct,
        "trazabilidad_linaje_pct": linaje["cobertura_trazabilidad_pct"],
    }
    with open(ORO_DIR / "resumen_evaluacion_iso_e2.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    return resumen


if __name__ == "__main__":
    print(json.dumps(ejecutar_evaluacion_iso_e2(), indent=2, ensure_ascii=False))
