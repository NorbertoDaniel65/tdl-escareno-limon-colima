# Fuente 1 · Open-Meteo Archive & Forecast API (`open_meteo.md`)

## 1. Ficha Técnica de la Fuente
- **Proveedor:** Open-Meteo.com (basado en reanálisis climático global **Copernicus ERA5 / ERA5-Land** del ECMWF y modelos NOAA GFS / DWD ICON).
- **Endpoints utilizados:**
  - Histórico (60 meses): `https://archive-api.open-meteo.com/v1/archive`
  - Captura diaria activa: `https://api.open-meteo.com/v1/forecast`
- **Formato de origen y destino:** Respuesta nativa en `JSON` columnar codificado en UTF-8; persistido en Capa Bronce como archivos `CSV` con ficha criptográfica `.meta.json` (SHA-256).
- **Cobertura geográfica (4 grupos comparables en Colima):**
  1. **Tecomán** (`06009`, `18.9136, -103.8753`) — Valle Citrícola Sur.
  2. **Armería** (`06001`, `18.9378, -103.9644`) — Corredor Costero.
  3. **Manzanillo** (`06007`, `19.0522, -104.3158`) — Costa Portuaria.
  4. **Colima** (`06002`, `19.2433, -103.7247`) — Valle Central.

## 2. Estructura y Diccionario de Variables en Capa Bronce
- `agroclima_colima_diario_historico.csv` (**7,304 registros**, 1,826 días del `2021-01-01` al `2025-12-31`).
- `agroclima_colima_mensual_60m.csv` (**240 registros**, **60 periodos mensuales** exactos por cada uno de los 4 municipios).
- `captura_diaria_<YYYY-MM-DD>.csv` (**56 registros** por corrida: 7 días observados recientes + 7 días de pronóstico para los 4 municipios).

| Variable | Tipo | Unidad | Descripción Agroclimática |
|---|---|---|---|
| `temp_max_c` / `temp_min_c` / `temp_media_c` | `float` | `°C` | Temperaturas extremas y media diaria a 2 metros sobre el suelo. |
| `precipitacion_mm` | `float` | `mm` | Precipitación pluvial diaria acumulada. |
| `evapotranspiracion_et0_mm` | `float` | `mm` | Evapotranspiración de referencia calculada con el estándar FAO Penman-Monteith ($ET_0$). |
| `balance_hidrico_mm` | `float` | `mm` | Diferencia $P - ET_0$ que mide el estrés o superávit hídrico del cultivo de limón. |
| `grados_dia_citricos_gdd` | `float` | `°C·día` | Grados-Día de Desarrollo acumulados sobre la temperatura base fisiológica de los cítricos ($T_{\text{base}} = 13^\circ\text{C}$). |
| `viento_max_kmh` | `float` | `km/h` | Ráfaga/velocidad máxima diaria de viento a 10 m (asociada a caída de flor/fruto joven y cicatrización de cáscara). |
| `radiacion_solar_mj_m2` | `float` | `MJ/m²` | Radiación solar de onda corta acumulada diaria (fotosíntesis y floración). |

## 3. Análisis de `robots.txt` y Términos de Uso
- **Licencia de los datos:** **Creative Commons Attribution 4.0 International (CC BY 4.0)** para uso académico y no comercial, conforme a `https://open-meteo.com/en/terms`.
- **Límites de tasa oficiales:** Hasta $10,000$ llamadas/día, $5,000$/hora y $600$/minuto por IP en el tier gratuito no comercial. Nuestro observatorio realiza únicamente **4 llamadas por corrida diaria** con pausa de $1.5\text{ s}$ entre ellas ($< 0.04\%$ de la cuota diaria).
- **Hallazgo técnico sobre `robots.txt` (documentado como Defecto #1 en PSP):** Los subdominios `api.open-meteo.com` y `archive-api.open-meteo.com` entregan `User-agent: * / Disallow: /` en su `robots.txt` (archivado en `data/bronce/robots_txt/`) con el propósito estándar en la industria de **impedir que motores de búsqueda web (Googlebot, Bingbot) indexen respuestas JSON dinámicas**, mientras que su documentación oficial autoriza e invita al consumo programático vía API REST. Por ello, `ExtractorEtico` archiva el `robots.txt` para trazabilidad y habilita el parámetro explícito `es_api_rest=True` para APIs REST documentadas, manteniendo intactos el `User-Agent` académico, la pausa mínima de $1.5\text{ s}$ y el backoff exponencial.
