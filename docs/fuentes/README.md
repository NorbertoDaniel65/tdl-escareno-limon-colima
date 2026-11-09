# Plan de Recopilación de Datos y Análisis Ético-Legal (`docs/fuentes/`)

Este directorio documenta el diseño técnico, contractual y ético-legal de las fuentes de datos que alimentan la **Capa Bronce** del **Observatorio Agroclimático y de Precios del Limón Mexicano en Colima (`tdl-escareno-limon-colima`)**.

## Resumen de Fuentes Operativas en E0

| ID | Fuente | Naturaleza | Cobertura Histórica en Bronce | Frecuencia de Captura Activa | Método de Acceso | Estado en E0 |
|---|---|---|---|---|---|---|
| **F1** | **Open-Meteo Archive & Forecast API** ([`open_meteo.md`](open_meteo.md)) | API REST Meteorológica y Agroclimática (ERA5-Land) | **60 meses** (2021-01 a 2025-12 · 1,826 días × 4 municipios = 7,304 registros diarios y 240 mensuales) | **Diaria automática** (`0 12 * * *` vía GitHub Actions) | `GET` JSON sobre HTTPS con `ExtractorEtico` (`pausa=1.5s`) | ✅ Operando y automatizada |
| **F2** | **SNIIM - Secretaría de Economía** ([`sniim_agro.md`](sniim_agro.md)) | Portal Público Gubernamental (Scraping ético + Serie Histórica Oficial) | **60 meses** (2021-01 a 2025-12 · 4 mercados mayoristas = 240 registros mensuales) | **Diaria / Semanal** (Monitoreo ético en GitHub Actions) | `GET` HTML con `BeautifulSoup` + Serie Histórica consolidada | ✅ Operando y verificada |

## Reglas Éticas y Legales Aplicadas en Código (`extractores/base.py`)

1. **Identificación Honesta (`User-Agent`):** Todas las peticiones HTTP se envían con el encabezado explícito:
   `TDL-Observatorio-Limon-Colima/1.0 (proyecto academico TecNM Colima; contacto: 23460323@colima.tecnm.mx)`
2. **Control de Tasa (`Rate Limiting` $\ge 1.5\text{ s}$):** El constructor de `ExtractorEtico` impone una espera mínima de $1.5\text{ segundos}$ entre peticiones al mismo dominio y prohíbe instanciar pausas menores a $1.0\text{ s}$.
3. **Respeto a `robots.txt` y Evidencia Archivada:** Cada dominio consultado tiene su archivo `robots.txt` y sus metadatos HTTP archivados en [`data/bronce/robots_txt/`](../../data/bronce/robots_txt/).
4. **Espera Exponencial (`Exponential Backoff`):** Ante respuestas HTTP `429 Too Many Requests` o `5xx`, el extractor aplica espera exponencial `pausa * (2 ** intento)` antes de reintentar, sin saturar jamás el servidor origen.
5. **Cero Datos Personales (LFPDPPP):** Ninguna de las fuentes contiene nombres de personas físicas, teléfonos, correos electrónicos, domicilios particulares ni identificadores fiscales; todas las observaciones corresponden a variables meteorológicas por municipio y precios mayoristas por kilogramo.
