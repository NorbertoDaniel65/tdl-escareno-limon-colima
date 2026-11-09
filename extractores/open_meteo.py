"""Extractor ético Fuente 1: Open-Meteo Archive & Forecast API para municipios limoneros de Colima.

Municipios observados (4 grupos comparables para MANOVA/PCA en E3):
- Tecomán (principal productor nacional de limón mexicano)
- Armería (corredor citrícola costero)
- Manzanillo (zona portuaria y microclima húmedo)
- Colima (capital / zona valle norte de referencia)
"""
from __future__ import annotations

import csv
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import pandas as pd

from .base import ROOT_DIR, ExtractorEtico, guardar_con_metadatos, registrar_bitacora

MUNICIPIOS_COLIMA: list[dict[str, Any]] = [
    {"id_municipio": "06009", "municipio": "Tecoman", "zona": "Valle Citricola Sur", "lat": 18.9136, "lon": -103.8753, "altitud_m": 33},
    {"id_municipio": "06001", "municipio": "Armeria", "zona": "Corredor Costero", "lat": 18.9378, "lon": -103.9644, "altitud_m": 31},
    {"id_municipio": "06007", "municipio": "Manzanillo", "zona": "Costa Portuaria", "lat": 19.0522, "lon": -104.3158, "altitud_m": 8},
    {"id_municipio": "06002", "municipio": "Colima", "zona": "Valle Central", "lat": 19.2433, "lon": -103.7247, "altitud_m": 498},
]

ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
BRONCE_OM_DIR = ROOT_DIR / "data" / "bronce" / "open_meteo"

VARIABLES_DIARIAS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "et0_fao_evapotranspiration",
    "wind_speed_10m_max",
    "shortwave_radiation_sum",
]


def descargar_historico_agroclima(
    fecha_inicio: str = "2021-01-01",
    fecha_fin: str = "2025-12-31",
    extractor: ExtractorEtico | None = None,
) -> dict[str, Any]:
    """Descarga la serie histórica real de Open-Meteo Archive API (60 meses / >1,800 días por municipio) y su agregado mensual."""
    ext = extractor or ExtractorEtico(pausa=1.5)
    BRONCE_OM_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    filas_diarias: list[dict[str, Any]] = []
    for m in MUNICIPIOS_COLIMA:
        params = {
            "latitude": m["lat"],
            "longitude": m["lon"],
            "start_date": fecha_inicio,
            "end_date": fecha_fin,
            "daily": ",".join(VARIABLES_DIARIAS),
            "timezone": "America/Mexico_City",
        }
        resp = ext.get(ARCHIVE_URL, params=params, es_api_rest=True)
        payload = resp.json()
        daily = payload.get("daily", {})
        fechas = daily.get("time", [])
        for idx, f_str in enumerate(fechas):
            t_max = daily.get("temperature_2m_max", [None])[idx]
            t_min = daily.get("temperature_2m_min", [None])[idx]
            t_mean = daily.get("temperature_2m_mean", [None])[idx]
            precip = daily.get("precipitation_sum", [None])[idx]
            et0 = daily.get("et0_fao_evapotranspiration", [None])[idx]
            viento = daily.get("wind_speed_10m_max", [None])[idx]
            rad = daily.get("shortwave_radiation_sum", [None])[idx]
            # Grados-día de desarrollo (GDD base 13°C para cítricos)
            gdd = round(max(0.0, (float(t_mean) - 13.0)), 2) if t_mean is not None else None
            # Balance hídrico simple (precipitación - evapotranspiración FAO)
            balance_hidrico = (
                round(float(precip) - float(et0), 2)
                if (precip is not None and et0 is not None)
                else None
            )
            filas_diarias.append(
                {
                    "fecha": f_str,
                    "anio_mes": f_str[:7],
                    "id_municipio": m["id_municipio"],
                    "municipio": m["municipio"],
                    "zona": m["zona"],
                    "latitud": m["lat"],
                    "longitud": m["lon"],
                    "temp_max_c": t_max,
                    "temp_min_c": t_min,
                    "temp_media_c": t_mean,
                    "precipitacion_mm": precip,
                    "evapotranspiracion_et0_mm": et0,
                    "balance_hidrico_mm": balance_hidrico,
                    "grados_dia_citricos_gdd": gdd,
                    "viento_max_kmh": viento,
                    "radiacion_solar_mj_m2": rad,
                    "fuente_api": "open-meteo-archive-v1",
                }
            )

    df_diario = pd.DataFrame(filas_diarias)
    ruta_diaria = BRONCE_OM_DIR / "agroclima_colima_diario_historico.csv"
    df_diario.to_csv(ruta_diaria, index=False, encoding="utf-8")

    # Agregación mensual por municipio (60 meses exactos x 4 municipios = 240 registros mensuales)
    df_mensual = (
        df_diario.groupby(["anio_mes", "id_municipio", "municipio", "zona"], as_index=False)
        .agg(
            temp_max_promedio_c=("temp_max_c", lambda s: round(s.mean(), 2)),
            temp_min_promedio_c=("temp_min_c", lambda s: round(s.mean(), 2)),
            temp_media_c=("temp_media_c", lambda s: round(s.mean(), 2)),
            dias_estres_termico_35c=("temp_max_c", lambda s: int((s >= 35.0).sum())),
            precipitacion_acum_mm=("precipitacion_mm", lambda s: round(s.sum(), 2)),
            evapotranspiracion_acum_mm=("evapotranspiracion_et0_mm", lambda s: round(s.sum(), 2)),
            deficit_hidrico_acum_mm=("balance_hidrico_mm", lambda s: round(s.sum(), 2)),
            gdd_acumulado_mes=("grados_dia_citricos_gdd", lambda s: round(s.sum(), 2)),
            viento_max_extremo_kmh=("viento_max_kmh", lambda s: round(s.max(), 2)),
            radiacion_media_mj_m2=("radiacion_solar_mj_m2", lambda s: round(s.mean(), 2)),
            dias_observados=("fecha", "count"),
        )
        .sort_values(["anio_mes", "municipio"])
    )
    ruta_mensual = BRONCE_OM_DIR / "agroclima_colima_mensual_60m.csv"
    df_mensual.to_csv(ruta_mensual, index=False, encoding="utf-8")

    periodos_unicos = int(df_mensual["anio_mes"].nunique())
    duracion = time.time() - t0

    meta_diario = guardar_con_metadatos(
        ruta_archivo=ruta_diaria,
        fuente="Open-Meteo Historical Weather API (ERA5-Land)",
        url_origen=ARCHIVE_URL,
        registros=len(df_diario),
        periodos=int(df_diario["fecha"].nunique()),
        licencia="CC BY 4.0 (Open-Meteo / Copernicus ERA5)",
        notas=f"Serie diaria de 4 municipios citrícolas de Colima ({fecha_inicio} a {fecha_fin}).",
    )
    meta_mensual = guardar_con_metadatos(
        ruta_archivo=ruta_mensual,
        fuente="Open-Meteo Historical Weather API (Agregado Mensual)",
        url_origen=ARCHIVE_URL,
        registros=len(df_mensual),
        periodos=periodos_unicos,
        licencia="CC BY 4.0 (Open-Meteo / Copernicus ERA5)",
        notas=f"Serie histórica mensual con {periodos_unicos} periodos (>=36 requeridos en E0) para los 4 municipios.",
    )

    registrar_bitacora(
        fuente="open_meteo_archive",
        operacion="descarga_historica_60m",
        estado="EXITO",
        duracion_seg=duracion,
        registros=len(df_diario),
        archivo_salida=meta_mensual["ruta_relativa"],
        sha256=meta_mensual["sha256"],
        detalle=f"Descargados {len(df_diario)} registros diarios y {len(df_mensual)} mensuales ({periodos_unicos} meses).",
    )
    return {"meta_diario": meta_diario, "meta_mensual": meta_mensual}


def capturar_clima_diario_actual(extractor: ExtractorEtico | None = None) -> dict[str, Any]:
    """Ejecuta la captura diaria programada (últimos 7 días + pronóstico de 7 días) y guarda snapshot particionado por fecha."""
    ext = extractor or ExtractorEtico(pausa=1.5)
    BRONCE_OM_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    hoy_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    filas: list[dict[str, Any]] = []

    for m in MUNICIPIOS_COLIMA:
        params = {
            "latitude": m["lat"],
            "longitude": m["lon"],
            "daily": ",".join(VARIABLES_DIARIAS),
            "past_days": 7,
            "forecast_days": 7,
            "timezone": "America/Mexico_City",
        }
        resp = ext.get(FORECAST_URL, params=params, es_api_rest=True)
        payload = resp.json()
        daily = payload.get("daily", {})
        fechas = daily.get("time", [])
        for idx, f_str in enumerate(fechas):
            t_max = daily.get("temperature_2m_max", [None])[idx]
            t_min = daily.get("temperature_2m_min", [None])[idx]
            t_mean = daily.get("temperature_2m_mean", [None])[idx]
            precip = daily.get("precipitation_sum", [None])[idx]
            et0 = daily.get("et0_fao_evapotranspiration", [None])[idx]
            viento = daily.get("wind_speed_10m_max", [None])[idx]
            rad = daily.get("shortwave_radiation_sum", [None])[idx]
            filas.append(
                {
                    "fecha_captura_utc": hoy_utc,
                    "fecha_observacion": f_str,
                    "tipo_registro": "observado_reciente" if f_str <= hoy_utc else "pronostico_meteorologico",
                    "id_municipio": m["id_municipio"],
                    "municipio": m["municipio"],
                    "zona": m["zona"],
                    "temp_max_c": t_max,
                    "temp_min_c": t_min,
                    "temp_media_c": t_mean,
                    "precipitacion_mm": precip,
                    "evapotranspiracion_et0_mm": et0,
                    "viento_max_kmh": viento,
                    "radiacion_solar_mj_m2": rad,
                }
            )

    ruta_snapshot = BRONCE_OM_DIR / f"captura_diaria_{hoy_utc}.csv"
    with ruta_snapshot.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0].keys()))
        writer.writeheader()
        writer.writerows(filas)

    # También actualiza el archivo consolidado latest para acceso directo del pipeline
    ruta_latest = BRONCE_OM_DIR / "captura_diaria_latest.csv"
    ruta_latest.write_text(ruta_snapshot.read_text(encoding="utf-8"), encoding="utf-8")

    duracion = time.time() - t0
    meta = guardar_con_metadatos(
        ruta_archivo=ruta_snapshot,
        fuente="Open-Meteo Forecast & Recent Days API",
        url_origen=FORECAST_URL,
        registros=len(filas),
        periodos=14,
        licencia="CC BY 4.0 (Open-Meteo)",
        notas=f"Captura diaria automática ejecutada el {hoy_utc} para 4 municipios citrícolas de Colima.",
    )
    guardar_con_metadatos(
        ruta_archivo=ruta_latest,
        fuente="Open-Meteo Forecast & Recent Days API (Latest)",
        url_origen=FORECAST_URL,
        registros=len(filas),
        periodos=14,
        licencia="CC BY 4.0 (Open-Meteo)",
        notas=f"Espejo latest actualizado el {hoy_utc}.",
    )
    registrar_bitacora(
        fuente="open_meteo_forecast",
        operacion="captura_diaria_programada",
        estado="EXITO",
        duracion_seg=duracion,
        registros=len(filas),
        archivo_salida=meta["ruta_relativa"],
        sha256=meta["sha256"],
        detalle=f"Snapshot diario {hoy_utc} guardado con {len(filas)} registros (4 municipios x 14 días).",
    )
    return meta
