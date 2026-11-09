# Reporte de Verificación Técnica de la Entrega E0 (`docs/E0/verificacion.md`)

Este documento resume la comprobación reproducible de todos los entregables de **E0** para **CITRO-DATA LAB COLIMA**.

## 1. Comandos de Verificación Reproducible (Sin depender de configuración externa)

Cualquier docente o auditor puede clonar el repositorio y ejecutar en menos de 10 segundos:

```powershell
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Ejecutar el verificador integral de la rúbrica E0
python -m pipeline.verificar_e0

# 3. Ejecutar la suite completa de pruebas unitarias (pytest)
pytest -v

# 4. Ejecutar manualmente la máquina de captura diaria en Capa Bronce
python -m extractores.ejecutar_captura --modo diario
```

## 2. Resumen de Inventario Verificado en Capa Bronce (`data/bronce/`)

| Archivo en Capa Bronce | Fuente | Registros | Periodos | Hash SHA-256 Verificado |
|---|---|---:|---:|---|
| `open_meteo/agroclima_colima_diario_historico.csv` | Open-Meteo Archive API (ERA5-Land) | 7,304 | 1,826 días | `a8e5f5c699898e47fbb50c3fc6af023519244d3e1f1a9879e0a64189ad0488cc` |
| `open_meteo/agroclima_colima_mensual_60m.csv` | Open-Meteo Archive API (Mensual) | 240 | **60 meses** | `6aad451dfcd2d2f033352a9a6182fac3800a818bc3b92fb2baa73cc7bd2ae240` |
| `sniim_limon/precios_limon_sniim_historico_60m.csv` | SNIIM - Secretaría de Economía | 240 | **60 meses** | `7dde14cf7f818a89294b73c91a15647315794c91ef7021c29fb276edd598adc2` |
| `open_meteo/captura_diaria_2026-11-09.csv` | Open-Meteo Forecast API (Diaria) | 56 | 14 días | `61ecb7e0dbd0182a359cb23884d5d0ed415c00d77fb1f71966684cda47d02a5e` |
| `sniim_limon/monitoreo_sniim_2026-11-09.csv` | SNIIM Portal Frutas y Hortalizas | 16 | 4 meses | `183b267f3a826005554f55a4840f9bbebea9a709baa175f1508bf43825ae51c6` |

## 3. Cumplimiento de Reglas del Juego (Sección 3 del Documento Oficial)
- **Serie histórica $\ge 36$ periodos:** Cumplido con **60 periodos mensuales** (2021-01 a 2025-12) en ambas fuentes.
- **Al menos 3 grupos para comparar en E3:** Cumplido con **4 municipios citrícolas de Colima** (`Tecomán`, `Armería`, `Manzanillo`, `Colima`) y **4 mercados mayoristas nacionales** (`Colima`, `Guadalajara`, `CDMX`, `Monterrey`).
- **Scraping y extracción con ética:** `ExtractorEtico` (`extractores/base.py`) verifica y archiva `robots.txt`, usa `User-Agent` identificable con correo institucional (`23460323@colima.tecnm.mx`) y respeta pausa mínima $\ge 1.5\text{ s}$ entre peticiones al mismo dominio.
- **Cero datos personales (LFPDPPP):** Verificado automáticamente por `pipeline/verificar_e0.py` y `tests/test_fuentes_bronce.py`.
