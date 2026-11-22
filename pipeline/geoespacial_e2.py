"""
Procesamiento Geoespacial, Unión Espacial (GeoPandas sjoin) e Integración a Capa Oro (E2).
CITRO-DATA LAB COLIMA — Norberto Daniel Escareño Montaño (23460323).

Ejecuta:
  1. Validación geoespacial (CRS EPSG:4326, validez de geometrías, cero PII).
  2. Unión espacial point-in-polygon: gpd.sjoin(puntos, poligonos, predicate="within").
  3. Enrutamiento a cuarentena (data/cuarentena/cuarentena_geoespacial_e2.csv) de los
     puntos del bounding box que caen fuera de los polígonos estatales de Colima (cero borrado silencioso).
  4. Reproyección métrica a EPSG:32613 (UTM Zona 13N) para densidad agrologística y distancias
     al Puerto de Manzanillo y al corredor carretero Colima-Guadalajara (Autopista 54D).
  5. Integración en Capa Oro (perfil_geoespacial_municipios_oro.geojson y .csv) con linaje
     trazable hasta cada archivo de Capa Bronce y su fecha de ingesta UTC.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path
from typing import Any

import geopandas as gpd
import numpy as np
import pandas as pd
from shapely.geometry import Point

ROOT_DIR = Path(__file__).resolve().parents[1]
BRONCE_GEO_DIR = ROOT_DIR / "data" / "bronce" / "geoespacial"
PLATA_DIR = ROOT_DIR / "data" / "plata"
ORO_DIR = ROOT_DIR / "data" / "oro"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"

COLUMNAS_PROHIBIDAS_PII = {
    "nombre_persona",
    "telefono",
    "phone",
    "celular",
    "correo",
    "email",
    "rfc",
    "curp",
    "direccion_personal",
    "owner",
    "contact:phone",
    "contact:email",
}

# Coordenadas geográficas (WGS84) de nodos logísticos de referencia
PUERTO_MANZANILLO_WGS84 = Point(-104.2940, 19.0550)
CORREDOR_GDL_54D_WGS84 = Point(-103.6860, 19.2770)


def _leer_meta(ruta_archivo: Path) -> dict[str, Any]:
    meta_path = ruta_archivo.with_name(ruta_archivo.name + ".meta.json")
    return json.loads(meta_path.read_text(encoding="utf-8"))


def ejecutar_pipeline_geoespacial_e2() -> dict[str, Any]:
    """Ejecuta el flujo completo Geoespacial Bronce -> Puerta/Cuarentena -> Plata -> Oro."""
    PLATA_DIR.mkdir(parents=True, exist_ok=True)
    ORO_DIR.mkdir(parents=True, exist_ok=True)
    CUARENTENA_DIR.mkdir(parents=True, exist_ok=True)

    ruta_mun_bronce = BRONCE_GEO_DIR / "municipios_colima_osm.geojson"
    ruta_inf_bronce = BRONCE_GEO_DIR / "infraestructura_agrologistica_colima_osm.geojson"
    meta_mun = _leer_meta(ruta_mun_bronce)
    meta_inf = _leer_meta(ruta_inf_bronce)

    gdf_mun = gpd.read_file(ruta_mun_bronce)
    gdf_pts = gpd.read_file(ruta_inf_bronce)

    # 1. Validación estricta de CRS, geometrías y cero PII
    if gdf_mun.crs is None or gdf_mun.crs.to_epsg() != 4326:
        gdf_mun = gdf_mun.to_crs("EPSG:4326")
    if gdf_pts.crs is None or gdf_pts.crs.to_epsg() != 4326:
        gdf_pts = gdf_pts.to_crs("EPSG:4326")

    cols_detectadas_pii = (
        ({c.lower() for c in gdf_mun.columns} | {c.lower() for c in gdf_pts.columns}) & COLUMNAS_PROHIBIDAS_PII
    )
    if cols_detectadas_pii:
        raise ValueError(f"Violación LFPDPPP: columnas PII detectadas en fuente geoespacial: {cols_detectadas_pii}")

    # Reparar geometrías no válidas si existieran
    gdf_mun["geometry"] = gdf_mun["geometry"].apply(lambda g: g if g.is_valid else g.buffer(0))

    # 2. Unión Espacial Point-in-Polygon (GeoPandas sjoin predicate="within")
    cols_mun_join = [
        "id_municipio",
        "cvegeo",
        "municipio",
        "nombre_oficial",
        "zona",
        "en_observatorio_citricola",
        "geometry",
    ]
    gdf_joined = gpd.sjoin(
        gdf_pts,
        gdf_mun[cols_mun_join],
        how="left",
        predicate="within",
    )
    # Resolver posible empate de borde entre dos polígonos quedándonos con la primera coincidencia determinista
    gdf_joined = gdf_joined.drop_duplicates(subset=["osm_uid"], keep="first").reset_index(drop=True)

    # 3. Separación Puerta de Calidad Geoespacial: dentro de Colima -> Plata; fuera de Colima -> Cuarentena
    ts_utc = dt.datetime.now(dt.timezone.utc).isoformat()
    mask_dentro = gdf_joined["id_municipio"].notna()
    gdf_plata = gdf_joined.loc[mask_dentro].drop(columns=["index_right"], errors="ignore").copy()
    gdf_plata["id_municipio"] = gdf_plata["id_municipio"].astype(int)

    df_cuarentena_geo = (
        gdf_joined.loc[~mask_dentro]
        .drop(columns=["geometry", "index_right"], errors="ignore")
        .copy()
    )
    df_cuarentena_geo["timestamp_cuarentena_utc"] = ts_utc
    df_cuarentena_geo["tabla_origen"] = "osm_overpass_infraestructura_colima"
    df_cuarentena_geo["llave_primaria"] = df_cuarentena_geo["osm_uid"].astype(str)
    df_cuarentena_geo["regla_violada"] = "RN-GEO-01_FUERA_POLIGONO_COLIMA"
    df_cuarentena_geo["severidad"] = "MEDIA"
    df_cuarentena_geo["accion_puerta"] = "ENVIADO_A_CUARENTENA_GEOESPACIAL"
    df_cuarentena_geo["motivo_rechazo"] = (
        "Coordenada dentro del bounding box rectangular pero fuera de los límites administrativos oficiales del Estado de Colima (Jalisco/Michoacán)."
    )

    cols_q_geo = [
        "timestamp_cuarentena_utc",
        "tabla_origen",
        "llave_primaria",
        "categoria_agrologistica",
        "latitud",
        "longitud",
        "regla_violada",
        "severidad",
        "accion_puerta",
        "motivo_rechazo",
    ]
    df_cuarentena_geo[cols_q_geo].to_csv(CUARENTENA_DIR / "cuarentena_geoespacial_e2.csv", index=False, encoding="utf-8")

    # Persistir Capa Plata Geoespacial
    gdf_plata.to_file(PLATA_DIR / "infraestructura_agrologistica_colima_plata.geojson", driver="GeoJSON", encoding="utf-8")
    gdf_plata.drop(columns=["geometry"]).to_csv(
        PLATA_DIR / "infraestructura_agrologistica_colima_plata.csv", index=False, encoding="utf-8"
    )

    # 4. Métricas espaciales en proyección métrica EPSG:32613 (UTM Zona 13N)
    # Nota técnica: el municipio de Tecomán (06009) es un MultiPolygon que incluye el archipiélago oceánico
    # de Revillagigedo en el Pacífico; para centroides continentales y distancias logísticas reales se utiliza
    # el polígono continental de mayor superficie de cada municipio.
    def _poligono_continental(geom: Any) -> Any:
        if geom.geom_type == "MultiPolygon":
            return max(geom.geoms, key=lambda p: p.area)
        return geom

    gdf_mun_utm = gdf_mun.to_crs("EPSG:32613")
    geoms_continentales_utm = gpd.GeoSeries(
        [_poligono_continental(g) for g in gdf_mun_utm.geometry],
        index=gdf_mun_utm.index,
        crs="EPSG:32613",
    )
    puerto_utm = gpd.GeoSeries([PUERTO_MANZANILLO_WGS84], crs="EPSG:4326").to_crs("EPSG:32613").iloc[0]
    corr_gdl_utm = gpd.GeoSeries([CORREDOR_GDL_54D_WGS84], crs="EPSG:4326").to_crs("EPSG:32613").iloc[0]

    centroides_utm = geoms_continentales_utm.centroid
    centroides_wgs = gpd.GeoSeries(centroides_utm, crs="EPSG:32613").to_crs("EPSG:4326")

    gdf_perfil = gdf_mun.copy()
    gdf_perfil["superficie_km2"] = (geoms_continentales_utm.area / 1_000_000.0).round(2)
    gdf_perfil["centroide_lon"] = centroides_wgs.x.round(5)
    gdf_perfil["centroide_lat"] = centroides_wgs.y.round(5)
    gdf_perfil["dist_puerto_manzanillo_km"] = (centroides_utm.distance(puerto_utm) / 1000.0).round(2)
    gdf_perfil["dist_corredor_gdl_54d_km"] = (centroides_utm.distance(corr_gdl_utm) / 1000.0).round(2)

    # Agregación por municipio desde la unión espacial
    piv = (
        gdf_plata.pivot_table(
            index="id_municipio",
            columns="categoria_agrologistica",
            values="osm_uid",
            aggfunc="count",
            fill_value=0,
        )
        .reset_index()
    )
    mapeo_cols = {
        "Zona_Huerta_Citricola": "n_huertas_citricolas_osm",
        "Infraestructura_Empaque_Bodega": "n_empaque_bodega_osm",
        "Mercado_Abasto": "n_mercados_abasto_osm",
        "Comercio_Fruticola_Mayorista": "n_comercio_fruticola_osm",
        "Nodo_Portuario_Exportacion": "n_nodos_portuarios_osm",
    }
    for orig, dest in mapeo_cols.items():
        if orig not in piv.columns:
            piv[orig] = 0
    piv = piv.rename(columns=mapeo_cols)
    cols_conteo = list(mapeo_cols.values())
    piv["n_nodos_agrologisticos_total"] = piv[cols_conteo].sum(axis=1)

    gdf_perfil = gdf_perfil.merge(piv[["id_municipio", *cols_conteo, "n_nodos_agrologisticos_total"]], on="id_municipio", how="left")
    for c in [*cols_conteo, "n_nodos_agrologisticos_total"]:
        gdf_perfil[c] = gdf_perfil[c].fillna(0).astype(int)

    gdf_perfil["densidad_agrologistica_100km2"] = (
        100.0 * gdf_perfil["n_nodos_agrologisticos_total"] / gdf_perfil["superficie_km2"]
    ).round(2)

    # 5. Integración con Clima Histórico (Capa Plata) y Precio Promedio Origen (Capa Oro)
    clima_plata = pd.read_csv(PLATA_DIR / "agroclima_mensual_plata.csv")
    clima_resumen = (
        clima_plata.groupby("id_municipio", as_index=False)
        .agg(
            temp_max_5a_c=("temp_max_promedio_c", lambda s: round(float(s.mean()), 2)),
            precipitacion_anual_prom_mm=("precipitacion_acum_mm", lambda s: round(float(s.sum() / 5.0), 1)),
            deficit_hidrico_anual_prom_mm=("deficit_hidrico_acum_mm", lambda s: round(float(s.sum() / 5.0), 1)),
            dias_estres_35c_anual_prom=("dias_estres_termico_35c", lambda s: round(float(s.sum() / 5.0), 1)),
        )
    )
    gdf_perfil = gdf_perfil.merge(clima_resumen, on="id_municipio", how="left")
    # Para los 6 municipios de contexto sin estación agroclimática en E0, etiquetar explícitamente con -1/NA documentado o promedio estatal?
    # Mejor mantener 0.0 / sin_monitoreo explícito en columnas auxiliares y mantener valores numéricos reales sin NaN en columnas clave de linaje.
    gdf_perfil["estado_monitoreo_clima"] = np.where(
        gdf_perfil["en_observatorio_citricola"], "ACTIVO_60_MESES", "CONTEXTO_ESTATAL"
    )
    for col_cl in [
        "temp_max_5a_c",
        "precipitacion_anual_prom_mm",
        "deficit_hidrico_anual_prom_mm",
        "dias_estres_35c_anual_prom",
    ]:
        gdf_perfil[col_cl] = gdf_perfil[col_cl].fillna(0.0)

    # 6. Columnas de Linaje de Datos por Registro (E2)
    gdf_perfil["linaje_id_registro"] = gdf_perfil["cvegeo"].apply(lambda c: f"ORO-GEO-{c}")
    gdf_perfil["linaje_fuentes_bronce"] = np.where(
        gdf_perfil["en_observatorio_citricola"],
        "osm_nominatim_geo+osm_overpass_geo+open_meteo_archive",
        "osm_nominatim_geo+osm_overpass_geo",
    )
    gdf_perfil["linaje_archivos_bronce"] = (
        f"{meta_mun['ruta_relativa']}|{meta_inf['ruta_relativa']}"
    )
    gdf_perfil["linaje_sha256_bronce"] = f"{meta_mun['sha256'][:16]}+{meta_inf['sha256'][:16]}"
    gdf_perfil["linaje_fecha_ingesta_utc"] = str(meta_inf["capturado_en_utc"])
    gdf_perfil["linaje_version_pipeline"] = "e2-geoespacial-v2.0"

    gdf_perfil = gdf_perfil.sort_values(
        ["en_observatorio_citricola", "peso_siap_limon", "n_nodos_agrologisticos_total"],
        ascending=[False, False, False],
    ).reset_index(drop=True)

    ruta_oro_geojson = ORO_DIR / "perfil_geoespacial_municipios_oro.geojson"
    ruta_oro_csv = ORO_DIR / "perfil_geoespacial_municipios_oro.csv"
    gdf_perfil.to_file(ruta_oro_geojson, driver="GeoJSON", encoding="utf-8")
    gdf_perfil.drop(columns=["geometry"]).to_csv(ruta_oro_csv, index=False, encoding="utf-8")

    resumen = {
        "timestamp_procesamiento_utc": ts_utc,
        "crs_almacenamiento": "EPSG:4326 (WGS84)",
        "crs_calculo_metrico": "EPSG:32613 (WGS84 / UTM Zona 13N - Colima)",
        "operacion_union_espacial": "geopandas.sjoin(puntos, poligonos_colima, how='left', predicate='within')",
        "poligonos_municipales_colima": int(len(gdf_perfil)),
        "municipios_nucleo_citricola": int(gdf_perfil["en_observatorio_citricola"].sum()),
        "puntos_bronce_evaluados": int(len(gdf_pts)),
        "puntos_aprobados_dentro_colima_plata": int(len(gdf_plata)),
        "puntos_enviados_cuarentena_fuera_colima": int(len(df_cuarentena_geo)),
        "tasa_conservacion_masa_ok": bool(len(gdf_pts) == len(gdf_plata) + len(df_cuarentena_geo)),
        "columnas_pii_detectadas": 0,
        "desglose_categorias_en_colima": gdf_plata["categoria_agrologistica"].value_counts().to_dict(),
        "top_municipios_nodos": gdf_perfil[
            [
                "cvegeo",
                "nombre_oficial",
                "en_observatorio_citricola",
                "superficie_km2",
                "n_huertas_citricolas_osm",
                "n_empaque_bodega_osm",
                "n_mercados_abasto_osm",
                "n_comercio_fruticola_osm",
                "n_nodos_agrologisticos_total",
                "densidad_agrologistica_100km2",
                "dist_puerto_manzanillo_km",
            ]
        ].to_dict(orient="records"),
    }
    with open(ORO_DIR / "resumen_geoespacial_e2.json", "w", encoding="utf-8") as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)

    return resumen


if __name__ == "__main__":
    res = ejecutar_pipeline_geoespacial_e2()
    print(json.dumps(res, indent=2, ensure_ascii=False))
