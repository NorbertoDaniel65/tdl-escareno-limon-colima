# Fuente 2 · SNIIM - Secretaría de Economía (`sniim_agro.md`)

## 1. Ficha Técnica de la Fuente
- **Institución:** Secretaría de Economía del Gobierno de México — **Sistema Nacional de Información e Integración de Mercados (SNIIM)** y **SIAP (Servicio de Información Agroalimentaria y Pesquera)**.
- **URL de consulta:** `http://www.economia-sniim.gob.mx/nuevo/Consultas/MercadosNacionales/PreciosDeMercado/Agricolas/ConsultaFrutasYHortalizas.aspx`
- **Producto observado:** **Limón con semilla #5 (Limón Mexicano - *Citrus aurantifolia*)**, originario del estado de Colima.
- **Mercados mayoristas monitoreados (4 nodos comerciales):**
  1. `MKT-COL`: Colima — Empacadoras y Distribución Regional (Tecomán / Colima).
  2. `MKT-GDL`: Guadalajara — Mercado de Abastos (principal nodo receptor en el Occidente).
  3. `MKT-CDMX`: Ciudad de México — Central de Abasto de Iztapalapa (referencia nacional).
  4. `MKT-MTY`: Monterrey — Mercado de Abastos Estrella (referencia norte).

## 2. Estructura y Diccionario de Variables en Capa Bronce
- `precios_limon_sniim_historico_60m.csv` (**240 registros**, **60 periodos mensuales** continuos desde `2021-01` hasta `2025-12` para los 4 mercados mayoristas).
- `monitoreo_sniim_<YYYY-MM-DD>.csv` (**16 registros** del corte de verificación ética ejecutado sobre el portal del SNIIM).

| Variable | Tipo | Unidad | Descripción Comercial |
|---|---|---|---|
| `anio_mes` | `str` | `YYYY-MM` | Periodo mensual de observación (60 meses continuos). |
| `id_mercado` / `mercado_mayorista` | `str` | Categoría | Identificador y nombre oficial de la central de abasto o nodo regional. |
| `precio_min_mxn_kg` | `float` | `MXN/kg` | Precio mínimo mayorista registrado en el periodo por kilogramo. |
| `precio_frecuente_mxn_kg` | `float` | `MXN/kg` | **Variable objetivo central para E1:** Precio modal/frecuente mayorista en pesos por kilogramo. |
| `precio_max_mxn_kg` | `float` | `MXN/kg` | Precio máximo mayorista registrado en el periodo por kilogramo. |
| `diferencial_vs_origen_mxn_kg` | `float` | `MXN/kg` | Margen de intermediación y transporte respecto al precio base en Colima (`spread` comercial). |
| `volumen_comercializado_ton` | `int` | `Toneladas` | Volumen mensual estimado de flujo comercial hacia el nodo mayorista. |

## 3. Análisis de `robots.txt` y Términos de Uso
- **Análisis de `robots.txt`:** Al consultar `http://www.economia-sniim.gob.mx/robots.txt`, el servidor gubernamental responde con código HTTP `404 Not Found` (sin restricciones de exclusión de robots publicadas; evidencia archivada en [`data/bronce/robots_txt/www.economia-sniim.gob.mx_robots.txt`](../../data/bronce/robots_txt/www.economia-sniim.gob.mx_robots.txt) y su `.meta.json`).
- **Marco Legal y Licencia:** Los precios mayoristas publicados por el SNIIM son información estadística de interés público generada por la Secretaría de Economía bajo los **Términos de Libre Uso de Datos Abiertos del Gobierno de México (MX-LibreUso)**, que autorizan su extracción, almacenamiento, transformación, modelado estadístico y redistribución abierta siempre que se cite la fuente institucional (*Fuente: SNIIM - Secretaría de Economía*) y no se aparenten sellos oficiales gubernamentales.
- **Ética de Extracción:** El módulo `extractores/sniim_limon.py` realiza únicamente **1 petición HTTP GET por corrida diaria** con pausa mínima de $1.5\text{ s}$ y cabecera identificable `TDL-Observatorio-Limon-Colima/1.0`, evitando cualquier carga sobre los servidores del SNIIM.
