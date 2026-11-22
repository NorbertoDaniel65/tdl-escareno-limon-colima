"""Extractor ético Fuente 3 (Especializada E2): Geoespacial — OpenStreetMap (Nominatim + Overpass API)
e integración con Claves Geoestadísticas Municipales INEGI para el Estado de Colima.

Cumplimiento estricto LFPDPPP (Cero datos personales):
- Se aplica una lista blanca de atributos técnicos/geográficos antes de persistir en Capa Bronce.
- Se descartan explícitamente teléfonos, correos electrónicos, perfiles sociales, propietarios o domicilios particulares.
- Se respetan robots.txt (archivados en data/bronce/robots_txt/), User-Agent institucional y pausa >= 1.5 s.
"""
from __future__ import annotations

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point, shape

from .base import ROOT_DIR, ExtractorEtico, guardar_con_metadatos, registrar_bitacora

BRONCE_GEO_DIR = ROOT_DIR / "data" / "bronce" / "geoespacial"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# Catálogo oficial INEGI de los 10 municipios del Estado de Colima (Entidad 06)
# Los 4 municipios con en_observatorio_citricola=True conforman el núcleo del observatorio.
CATALOGO_MUNICIPIOS_COLIMA: list[dict[str, Any]] = [
    {"id_municipio": 6009, "cvegeo": "06009", "municipio": "Tecoman", "nombre_oficial": "Tecomán", "zona": "Valle Citricola Sur", "en_observatorio_citricola": True, "peso_siap_limon": 0.55, "osm_query": "Municipio de Tecomán, Colima, Mexico"},
    {"id_municipio": 6001, "cvegeo": "06001", "municipio": "Armeria", "nombre_oficial": "Armería", "zona": "Corredor Costero", "en_observatorio_citricola": True, "peso_siap_limon": 0.22, "osm_query": "Municipio de Armería, Colima, Mexico"},
    {"id_municipio": 6007, "cvegeo": "06007", "municipio": "Manzanillo", "nombre_oficial": "Manzanillo", "zona": "Costa Portuaria", "en_observatorio_citricola": True, "peso_siap_limon": 0.15, "osm_query": "Municipio de Manzanillo, Colima, Mexico"},
    {"id_municipio": 6002, "cvegeo": "06002", "municipio": "Colima", "nombre_oficial": "Colima", "zona": "Valle Central", "en_observatorio_citricola": True, "peso_siap_limon": 0.08, "osm_query": "Municipio de Colima, Colima, Mexico"},
    {"id_municipio": 6003, "cvegeo": "06003", "municipio": "Comala", "nombre_oficial": "Comala", "zona": "Zona Norte Volcanica", "en_observatorio_citricola": False, "peso_siap_limon": 0.00, "osm_query": "Municipio de Comala, Colima, Mexico"},
    {"id_municipio": 6004, "cvegeo": "06004", "municipio": "Coquimatlan", "nombre_oficial": "Coquimatlán", "zona": "Valle Poniente", "en_observatorio_citricola": False, "peso_siap_limon": 0.00, "osm_query": "Municipio de Coquimatlán, Colima, Mexico"},
    {"id_municipio": 6005, "cvegeo": "06005", "municipio": "Cuauhtemoc", "nombre_oficial": "Cuauhtémoc", "zona": "Zona Norte Alta", "en_observatorio_citricola": False, "peso_siap_limon": 0.00, "osm_query": "Municipio de Cuauhtémoc, Colima, Mexico"},
    {"id_municipio": 6006, "cvegeo": "06006", "municipio": "Ixtlahuacan", "nombre_oficial": "Ixtlahuacán", "zona": "Sierra Sur", "en_observatorio_citricola": False, "peso_siap_limon": 0.00, "osm_query": "Municipio de Ixtlahuacán, Colima, Mexico"},
    {"id_municipio": 6008, "cvegeo": "06008", "municipio": "Minatitlan", "nombre_oficial": "Minatitlán", "zona": "Sierra Noroeste", "en_observatorio_citricola": False, "peso_siap_limon": 0.00, "osm_query": "Municipio de Minatitlán, Colima, Mexico"},
    {"id_municipio": 6010, "cvegeo": "06010", "municipio": "Villa de Alvarez", "nombre_oficial": "Villa de Álvarez", "zona": "Zona Metropolitana", "en_observatorio_citricola": False, "peso_siap_limon": 0.00, "osm_query": "Municipio de Villa de Álvarez, Colima, Mexico"},
]

# Patrón de sanitización para eliminar posibles teléfonos o correos embebidos en etiquetas públicas OSM
_PATRON_PII_TEXTO = re.compile(
    r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+|\+?\d[\d\s\-()]{7,}\d)"
)


def _sanitizar_etiqueta_publica(valor: str | None) -> str:
    """Elimina cualquier rastro de correo electrónico o número telefónico de nombres de sitios públicos."""
    if not valor:
        return "Sin_Denominacion_Publica"
    limpio = _PATRON_PII_TEXTO.sub("[REDACTADO]", str(valor)).strip()
    return limpio[:90] if limpio else "Sin_Denominacion_Publica"


def _clasificar_nodo_agrologistico(tags: dict[str, Any]) -> tuple[str, str]:
    """Clasifica un elemento OSM en categorías relevantes para la cadena de valor del limón mexicano."""
    if tags.get("landuse") == "orchard" or tags.get("crop") in ("citrus", "lime", "lemon"):
        return "Zona_Huerta_Citricola", f"landuse={tags.get('landuse', 'orchard')}"
    if tags.get("landuse") == "farmland":
        return "Area_Agricola", "landuse=farmland"
    if tags.get("amenity") == "marketplace":
        return "Mercado_Abasto", "amenity=marketplace"
    if tags.get("shop") in ("greengrocer", "wholesale", "farm"):
        return "Comercio_Fruticola_Mayorista", f"shop={tags.get('shop')}"
    if tags.get("landuse") == "port" or tags.get("industrial") == "port":
        return "Nodo_Portuario_Exportacion", "landuse=port"
    if tags.get("building") in ("warehouse", "industrial") or tags.get("landuse") == "industrial" or "industrial" in tags:
        sub = tags.get("industrial") or tags.get("building") or tags.get("landuse") or "industrial"
        return "Infraestructura_Empaque_Bodega", f"industrial={sub}"
    return "Otro_Nodo_Logistico", "osm_general"


def descargar_poligonos_municipios_colima(extractor: ExtractorEtico | None = None) -> dict[str, Any]:
    """Descarga los polígonos administrativos reales (EPSG:4326) de los 10 municipios de Colima vía Nominatim OSM."""
    ext = extractor or ExtractorEtico(pausa=1.5)
    BRONCE_GEO_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    hoy_utc = datetime.now(timezone.utc).isoformat()

    features: list[dict[str, Any]] = []
    for item in CATALOGO_MUNICIPIOS_COLIMA:
        params = {
            "q": item["osm_query"],
            "format": "jsonv2",
            "polygon_geojson": 1,
            "addressdetails": 0,
            "limit": 5,
        }
        resp = ext.get(NOMINATIM_URL, params=params, es_api_rest=True, timeout=30)
        candidatos = resp.json()
        elegido = None
        for c in candidatos:
            geom = c.get("geojson", {})
            if geom.get("type") in ("Polygon", "MultiPolygon"):
                elegido = c
                break
        if elegido is None:
            raise RuntimeError(f"No se obtuvo polígono válido en Nominatim para {item['nombre_oficial']}")

        geom_shape = shape(elegido["geojson"])
        if not geom_shape.is_valid:
            geom_shape = geom_shape.buffer(0)

        features.append(
            {
                "id_municipio": int(item["id_municipio"]),
                "cvegeo": item["cvegeo"],
                "municipio": item["municipio"],
                "nombre_oficial": item["nombre_oficial"],
                "zona": item["zona"],
                "en_observatorio_citricola": bool(item["en_observatorio_citricola"]),
                "peso_siap_limon": float(item["peso_siap_limon"]),
                "osm_place_id": int(elegido.get("place_id", 0)),
                "osm_id": int(elegido.get("osm_id", 0)),
                "fecha_captura_utc": hoy_utc,
                "fuente_api": "openstreetmap-nominatim-v2",
                "geometry": geom_shape,
            }
        )

    gdf = gpd.GeoDataFrame(features, geometry="geometry", crs="EPSG:4326")
    # Cálculo métrico en EPSG:32613 (UTM Zona 13N - Colima, México) para área real en km² y centroides exactos
    gdf_utm = gdf.to_crs("EPSG:32613")
    gdf["superficie_km2"] = (gdf_utm.geometry.area / 1_000_000.0).round(2)
    centroides_wgs84 = gpd.GeoSeries(gdf_utm.geometry.centroid, crs="EPSG:32613").to_crs("EPSG:4326")
    gdf["centroide_lon"] = centroides_wgs84.x.round(5)
    gdf["centroide_lat"] = centroides_wgs84.y.round(5)

    ruta_geojson = BRONCE_GEO_DIR / "municipios_colima_osm.geojson"
    gdf.to_file(ruta_geojson, driver="GeoJSON", encoding="utf-8")

    duracion = time.time() - t0
    meta = guardar_con_metadatos(
        ruta_archivo=ruta_geojson,
        fuente="OpenStreetMap Nominatim API (Límites Municipales Colima / Claves INEGI)",
        url_origen=NOMINATIM_URL,
        registros=len(gdf),
        periodos=1,
        licencia="ODbL 1.0 (OpenStreetMap Contributors) + Catálogo INEGI",
        notas="Polígonos municipales reales WGS84 (EPSG:4326) de los 10 municipios de Colima (4 núcleos citrícolas + 6 vecinos).",
    )
    registrar_bitacora(
        fuente="osm_nominatim_geo",
        operacion="captura_poligonos_municipios_colima",
        estado="EXITO",
        duracion_seg=duracion,
        registros=len(gdf),
        archivo_salida=meta["ruta_relativa"],
        sha256=meta["sha256"],
        detalle=f"Descargados {len(gdf)} polígonos municipales reales de Colima en GeoJSON (EPSG:4326).",
    )
    return meta


def descargar_infraestructura_agrologistica_colima(extractor: ExtractorEtico | None = None) -> dict[str, Any]:
    """Consulta Overpass API (OpenStreetMap) para capturar infraestructura agrologística,
    mercados, zonas agrícolas/huertas, almacenes industriales y nodo portuario en Colima.
    Aplica lista blanca estricta (cero PII) antes de escribir en Capa Bronce.
    """
    ext = extractor or ExtractorEtico(pausa=1.5)
    BRONCE_GEO_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    hoy_utc = datetime.now(timezone.utc).isoformat()

    # Bounding box geográfico del Estado de Colima (sur, oeste, norte, este)
    bbox = "18.65,-104.72,19.52,-103.48"
    overpass_ql = f"""[out:json][timeout:45];
(
  nwr["shop"~"^(greengrocer|wholesale|farm)$"]({bbox});
  nwr["amenity"="marketplace"]({bbox});
  nwr["landuse"="orchard"]({bbox});
  nwr["landuse"="port"]({bbox});
  nwr["building"="warehouse"]({bbox});
  node["industrial"]({bbox});
  way["landuse"="industrial"]({bbox});
);
out center tags;"""

    resp = ext.post(OVERPASS_URL, data={"data": overpass_ql}, es_api_rest=True, timeout=60)
    payload = resp.json()
    elementos = payload.get("elements", [])

    filas: list[dict[str, Any]] = []
    vistos: set[tuple[str, int]] = set()
    for el in elementos:
        osm_type = str(el.get("type", "node"))
        osm_id = int(el.get("id", 0))
        if (osm_type, osm_id) in vistos:
            continue
        vistos.add((osm_type, osm_id))

        lat = el.get("lat") if osm_type == "node" else el.get("center", {}).get("lat")
        lon = el.get("lon") if osm_type == "node" else el.get("center", {}).get("lon")
        if lat is None or lon is None:
            continue

        tags = el.get("tags", {}) or {}
        categoria, subtipo = _clasificar_nodo_agrologistico(tags)
        # Lista blanca estricta: jamás leer phone, email, contact:*, owner, operator personal, etc.
        nombre_publico = _sanitizar_etiqueta_publica(tags.get("name"))

        filas.append(
            {
                "osm_uid": f"{osm_type}/{osm_id}",
                "osm_type": osm_type,
                "osm_id": osm_id,
                "categoria_agrologistica": categoria,
                "subtipo_osm": subtipo,
                "nombre_publico_lugar": nombre_publico,
                "latitud": round(float(lat), 6),
                "longitud": round(float(lon), 6),
                "fecha_captura_utc": hoy_utc,
                "fuente_api": "openstreetmap-overpass-v1",
                "licencia": "ODbL-1.0",
            }
        )

    df = pd.DataFrame(filas).sort_values(["categoria_agrologistica", "osm_id"]).reset_index(drop=True)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df["longitud"], df["latitud"])],
        crs="EPSG:4326",
    )

    ruta_geojson = BRONCE_GEO_DIR / "infraestructura_agrologistica_colima_osm.geojson"
    ruta_csv = BRONCE_GEO_DIR / "infraestructura_agrologistica_colima_osm.csv"
    gdf.to_file(ruta_geojson, driver="GeoJSON", encoding="utf-8")
    df.to_csv(ruta_csv, index=False, encoding="utf-8")

    duracion = time.time() - t0
    meta_geojson = guardar_con_metadatos(
        ruta_archivo=ruta_geojson,
        fuente="OpenStreetMap Overpass API (Infraestructura Agrologística y Citrícola Colima)",
        url_origen=OVERPASS_URL,
        registros=len(gdf),
        periodos=1,
        licencia="ODbL 1.0 (OpenStreetMap Contributors)",
        notas="Nodos/centroides reales de huertas, mercados, bodegas/empacadoras y puerto en Colima; 0 PII.",
    )
    meta_csv = guardar_con_metadatos(
        ruta_archivo=ruta_csv,
        fuente="OpenStreetMap Overpass API (Tabla CSV Infraestructura Agrologística Colima)",
        url_origen=OVERPASS_URL,
        registros=len(df),
        periodos=1,
        licencia="ODbL 1.0 (OpenStreetMap Contributors)",
        notas="Representación tabular sincronizada de infraestructura_agrologistica_colima_osm.geojson; 0 PII.",
    )
    registrar_bitacora(
        fuente="osm_overpass_geo",
        operacion="captura_infraestructura_agrologistica_colima",
        estado="EXITO",
        duracion_seg=duracion,
        registros=len(gdf),
        archivo_salida=meta_geojson["ruta_relativa"],
        sha256=meta_geojson["sha256"],
        detalle=f"Capturados {len(gdf)} elementos agrologísticos reales en Colima vía Overpass API (0 PII).",
    )
    return {"meta_geojson": meta_geojson, "meta_csv": meta_csv, "conteo_categorias": df["categoria_agrologistica"].value_counts().to_dict()}


def ejecutar_captura_geoespacial() -> dict[str, Any]:
    """Ejecuta la descarga completa de la Fuente Especializada 3 (Geoespacial) en Capa Bronce."""
    ext = ExtractorEtico(pausa=1.5)
    meta_mun = descargar_poligonos_municipios_colima(extractor=ext)
    res_infra = descargar_infraestructura_agrologistica_colima(extractor=ext)
    return {"municipios": meta_mun, "infraestructura": res_infra}


if __name__ == "__main__":
    res = ejecutar_captura_geoespacial()
    print(json.dumps(res, indent=2, ensure_ascii=False))
