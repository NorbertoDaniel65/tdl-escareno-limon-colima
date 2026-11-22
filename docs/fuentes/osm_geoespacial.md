# Fuente Especializada 3 (E2) — Geoespacial: OpenStreetMap (Nominatim & Overpass API) + Catálogo Municipal INEGI

* **Módulo Extractor:** `extractores/geoespacial_osm.py`
* **Módulo de Unión Espacial e Integración Oro:** `pipeline/geoespacial_e2.py`
* **Archivos en Capa Bronce:**
  * `data/bronce/geoespacial/municipios_colima_osm.geojson` (`10` polígonos administrativos de Colima, `EPSG:4326`, con `.meta.json` SHA-256)
  * `data/bronce/geoespacial/infraestructura_agrologistica_colima_osm.geojson` y `.csv` (`1,164` elementos agrologísticos en el bounding box de Colima, `EPSG:4326`, `0` PII)
* **Archivos en Capa Plata y Cuarentena:**
  * `data/plata/infraestructura_agrologistica_colima_plata.geojson` (`1,074` nodos estrictamente dentro de Colima asignados a municipio vía `gpd.sjoin(..., predicate="within")`)
  * `data/cuarentena/cuarentena_geoespacial_e2.csv` (`90` puntos del bounding box pertenecientes a Jalisco/Michoacán rechazados con regla `RN-GEO-01_FUERA_POLIGONO_COLIMA`)
* **Archivo Integrado en Capa Oro:**
  * `data/oro/perfil_geoespacial_municipios_oro.geojson` y `.csv` (`10` municipios enriquecidos con métricas de densidad en `EPSG:32613`, distancias al Puerto de Manzanillo y Autopista 54D, clima histórico de 5 años y 6 columnas de linaje por registro)

## Licenciamiento, `robots.txt` y Privacidad (LFPDPPP)

* **Licencia:** **Open Database License (ODbL 1.0)** — *© OpenStreetMap Contributors* + Catálogo Geoestadístico Municipal INEGI.
* **Evidencia `robots.txt`:** `data/bronce/robots_txt/nominatim.openstreetmap.org_robots.txt` y `data/bronce/robots_txt/overpass-api.de_robots.txt`.
* **Privacidad:** Lista blanca estricta de columnas en `extractores/geoespacial_osm.py` + sanitizador por expresión regular que elimina cualquier rastro de teléfonos o correos electrónicos antes de escribir en Capa Bronce (`datos_personales_incluidos: false`).
