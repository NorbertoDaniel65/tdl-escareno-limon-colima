"""
Pruebas unitarias y de integración para la Etapa E2 — Ingeniería de Datos (Unidad 4) y Calidad ISO:
Fuente Especializada Geoespacial (OSM + INEGI con GeoPandas), Cero PII, Ética/robots.txt,
Linaje 100% registro-a-registro (Bronce -> Oro) y Evaluación ISO/IEC 25010 & 25012.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import geopandas as gpd
import pandas as pd

from pipeline.geoespacial_e2 import COLUMNAS_PROHIBIDAS_PII
from pipeline.linaje_datos import COLUMNAS_LINAJE, rastrear_registro_oro
from pipeline.verificar_e0 import sha256_archivo

ROOT_DIR = Path(__file__).resolve().parents[1]
BRONCE_GEO_DIR = ROOT_DIR / "data" / "bronce" / "geoespacial"
ORO_DIR = ROOT_DIR / "data" / "oro"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"


def test_bronce_geoespacial_sha256_y_cero_pii():
    for nombre in [
        "municipios_colima_osm.geojson",
        "infraestructura_agrologistica_colima_osm.geojson",
        "infraestructura_agrologistica_colima_osm.csv",
    ]:
        p = BRONCE_GEO_DIR / nombre
        meta_p = p.with_name(p.name + ".meta.json")
        assert p.exists() and meta_p.exists(), f"Falta archivo o metadato: {nombre}"
        meta = json.loads(meta_p.read_text(encoding="utf-8"))
        assert meta["sha256"] == sha256_archivo(p)
        assert meta["datos_personales_incluidos"] is False

    df_inf = pd.read_csv(BRONCE_GEO_DIR / "infraestructura_agrologistica_colima_osm.csv")
    assert len(df_inf) >= 500
    assert not ({c.lower() for c in df_inf.columns} & COLUMNAS_PROHIBIDAS_PII)
    patron_email = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    assert not df_inf["nombre_publico_lugar"].astype(str).apply(lambda s: bool(patron_email.search(s))).any()


def test_union_espacial_geopandas_conservacion_masa_y_crs():
    res_geo = json.loads((ORO_DIR / "resumen_geoespacial_e2.json").read_text(encoding="utf-8"))
    assert res_geo["tasa_conservacion_masa_ok"] is True
    assert res_geo["columnas_pii_detectadas"] == 0
    assert (
        res_geo["puntos_bronce_evaluados"]
        == res_geo["puntos_aprobados_dentro_colima_plata"] + res_geo["puntos_enviados_cuarentena_fuera_colima"]
    )

    gdf_oro = gpd.read_file(ORO_DIR / "perfil_geoespacial_municipios_oro.geojson")
    assert gdf_oro.crs.to_epsg() == 4326
    assert len(gdf_oro) == 10
    assert int(gdf_oro["en_observatorio_citricola"].sum()) == 4

    # Verificar corrección Defecto #9: centroide continental de Tecomán dentro de Colima (no en Revillagigedo)
    tecoman = gdf_oro[gdf_oro["cvegeo"] == "06009"].iloc[0]
    assert -104.05 <= tecoman["centroide_lon"] <= -103.65
    assert 18.70 <= tecoman["centroide_lat"] <= 19.05
    assert 40.0 <= tecoman["dist_puerto_manzanillo_km"] <= 70.0

    df_q_geo = pd.read_csv(CUARENTENA_DIR / "cuarentena_geoespacial_e2.csv")
    assert len(df_q_geo) == res_geo["puntos_enviados_cuarentena_fuera_colima"]
    assert (df_q_geo["regla_violada"] == "RN-GEO-01_FUERA_POLIGONO_COLIMA").all()


def test_linaje_completo_100pct_capa_oro_hasta_bronce():
    linaje = json.loads((ORO_DIR / "linaje_datos_e2.json").read_text(encoding="utf-8"))
    assert linaje["cobertura_trazabilidad_pct"] == 100.0
    assert linaje["total_registros_oro_rastreados"] == 310

    for tabla in [
        "serie_mensual_oro_60m.csv",
        "panel_integrado_municipio_mercado_oro.csv",
        "perfil_geoespacial_municipios_oro.csv",
    ]:
        df = pd.read_csv(ORO_DIR / tabla)
        for col in COLUMNAS_LINAJE:
            assert col in df.columns, f"Falta columna de linaje {col} en {tabla}"
            assert df[col].notna().all(), f"Valores nulos en columna de linaje {col} de {tabla}"

    # Verificar rastreo individual en las 3 tablas de Capa Oro
    for rid in ["ORO-SERIE-2022-02", "ORO-PANEL-2025-12-06009", "ORO-GEO-06009"]:
        traza = rastrear_registro_oro(rid)
        assert len(traza["origenes_bronce_verificados"]) >= 2
        for nodo in traza["origenes_bronce_verificados"]:
            assert len(nodo["sha256_completo"]) == 64
            assert "T" in nodo["capturado_en_utc"]


def test_declaracion_etica_robots_y_evaluacion_iso():
    etica = (ROOT_DIR / "docs" / "etica-datos.md").read_text(encoding="utf-8")
    for termino in ["Open-Meteo", "SNIIM", "OpenStreetMap", "LFPDPPP", "ODbL 1.0", "CC BY 4.0", "robots.txt"]:
        assert termino in etica, f"Falta mención obligatoria de '{termino}' en docs/etica-datos.md"

    for rob in [
        "api.open-meteo.com_robots.txt",
        "www.economia-sniim.gob.mx_robots.txt",
        "nominatim.openstreetmap.org_robots.txt",
        "overpass-api.de_robots.txt",
    ]:
        assert (ROOT_DIR / "data" / "bronce" / "robots_txt" / rob).exists()

    iso_res = json.loads((ORO_DIR / "resumen_evaluacion_iso_e2.json").read_text(encoding="utf-8"))
    assert iso_res["seguridad_estatica"]["secretos_expuestos"] == 0
    assert iso_res["completitud_capa_oro_pct"] == 100.0
    assert len(pd.read_csv(ORO_DIR / "evaluacion_iso_25010_e2.csv")) == 8
    assert len(pd.read_csv(ORO_DIR / "evaluacion_iso_25012_e2.csv")) == 15
