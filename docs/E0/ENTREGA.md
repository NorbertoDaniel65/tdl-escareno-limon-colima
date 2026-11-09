# Entrega E0 · CITRO-DATA LAB COLIMA (Observatorio Agroclimático y de Precios del Limón Mexicano)

Equipo: Norberto Daniel Escareño Montaño (`23460323`, `@NorbertoDaniel65`) · Etiqueta: `e0` · Tablero: En construcción para E1/E4 (Streamlit)

## Resumen en tres líneas
1. **CITRO-DATA LAB COLIMA** observa la relación entre el estrés agroclimático en los **4 municipios citrícolas de Colima** (*Tecomán, Armería, Manzanillo y Colima*) y el precio mayorista del **limón mexicano con semilla #5** en **4 mercados nacionales** (*Colima, Guadalajara, CDMX y Monterrey*), validado mediante entrevista de campo con un actor real del sector.
2. La **Capa Bronce** cuenta ya con **60 periodos mensuales continuos (`2021-01` a `2025-12`, superando los 36 requeridos)** tanto en agroclima (`Open-Meteo Archive API`, 7,304 registros diarios / 240 mensuales) como en precios mayoristas (`SNIIM - Secretaría de Economía`, 240 registros mensuales), además de captura diaria automatizada con **GitHub Actions** y fichas `.meta.json` con hash **SHA-256**.
3. El **Sistema de Calidad inicial (PSP)** está abierto y operando con registros reales en `calidad/tiempo-norberto.csv`, `calidad/defectos-norberto.csv`, bitácora estructurada `calidad/bitacora_capturas.jsonl`, 3 objetivos medibles en `calidad/objetivos.md` y verificación automática aprobada con `pytest` y `python -m pipeline.verificar_e0`.

## Ingeniería de Datos
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| **Plan de recopilación** (estructura, formato, frecuencia, análisis de `robots.txt` y términos de uso) | [`docs/E0/propuesta.md` (§4)](propuesta.md#4-plan-de-recopilacion-de-datos-y-analisis-etico-legal-robotstxt-y-terminos-de-uso), [`docs/fuentes/README.md`](../fuentes/README.md), [`docs/fuentes/open_meteo.md`](../fuentes/open_meteo.md), [`docs/fuentes/sniim_agro.md`](../fuentes/sniim_agro.md) y archivos en [`data/bronce/robots_txt/`](../../data/bronce/robots_txt/) | Incluye análisis legal de CC BY 4.0 (Open-Meteo) y Libre Uso MX (SNIIM), más archivo automático de `robots.txt`. |
| **Captura y serie histórica** (dos fuentes funcionando, una programada con GitHub Actions; serie $\ge 36$ periodos en capa bronce) | Extractores: [`extractores/base.py`](../../extractores/base.py), [`extractores/open_meteo.py`](../../extractores/open_meteo.py), [`extractores/sniim_limon.py`](../../extractores/sniim_limon.py)<br>Workflow: [`.github/workflows/captura-bronce.yml`](../../.github/workflows/captura-bronce.yml)<br>Series 60 meses: [`agroclima_colima_mensual_60m.csv`](../../data/bronce/open_meteo/agroclima_colima_mensual_60m.csv) y [`precios_limon_sniim_historico_60m.csv`](../../data/bronce/sniim_limon/precios_limon_sniim_historico_60m.csv) | **60 periodos mensuales** descargados en ambas fuentes ($\ge 36$ requeridos) + **7,304 registros diarios** y capturas diarias con hash SHA-256 verificado. |
| **Estructura del repositorio y verificabilidad** | [`README.md`](../../README.md), [`pipeline/verificar_e0.py`](../../pipeline/verificar_e0.py) y [`docs/E0/verificacion.md`](verificacion.md) | 100% reproducible con `python -m pipeline.verificar_e0` y `pytest`. |

## Análisis Estadístico
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| **Pregunta y cliente** (pregunta concreta con evidencia de entrevista de $\ge 15\text{ min}$; cliente identificado con motivo para pagar) | [`docs/E0/propuesta.md` (§1 y §2)](propuesta.md#1-ficha-del-observatorio) | Entrevista de campo de 22 min con comercializador/productor citrícola en Tecomán-Colima (5 preguntas, respuestas y 3 aprendizajes operativos). |
| **Preguntas analíticas** (tres preguntas medibles: variable a pronosticar en E1, factores del experimento en E2 y grupos a comparar en E3) | [`docs/E0/propuesta.md` (§3.1, §3.2 y §3.3)](propuesta.md#3-las-tres-preguntas-analiticas-del-proyecto-e1-e2-y-e3) | **E1:** Pronóstico de `precio_frecuente_mxn_kg` (SES, Holt, Holt-Winters, SARIMA).<br>**E2:** Diseño factorial $2^3$ y ANOVA de 2 vías sobre rendimiento del pipeline.<br>**E3:** PCA y MANOVA ($\Lambda$ de Wilks y Pillai) comparando 4 municipios y 4 mercados en $\ge 7$ variables. |
| **Serie histórica identificada ($\ge 36$ periodos)** | [`docs/E0/propuesta.md` (§5)](propuesta.md#5-evidencia-de-serie-historica-en-capa-bronce-36-periodos-cumplidos) y [`data/bronce/`](../../data/bronce/) | 60 meses continuos (`2021-01` a `2025-12`) sin valores faltantes en ambas fuentes. |

## Calidad en los Sistemas de Información *(Sección PSP y Aseguramiento del Proyecto)*
| Criterio de la rúbrica | Evidencia (enlace) | Nota del equipo |
|---|---|---|
| **Registros individuales de defectos y tiempo (PSP)** | [`calidad/tiempo-norberto.csv`](../../calidad/tiempo-norberto.csv) y [`calidad/defectos-norberto.csv`](../../calidad/defectos-norberto.csv) | Formato oficial exacto del Kit de Arranque (pág. 32), con 6 sesiones de tiempo y 4 defectos reales documentados y corregidos. |
| **Bitácora de captura activa** | [`calidad/bitacora_capturas.jsonl`](../../calidad/bitacora_capturas.jsonl) | Registro automático en JSON Lines con marcas de tiempo UTC, duración en segundos, conteo de filas y hash SHA-256 por corrida. |
| **Tres objetivos de calidad medibles** | [`calidad/objetivos.md`](../../calidad/objetivos.md) y [`calidad/README.md`](../../calidad/README.md) | **O1:** Disponibilidad $\ge 95\%$; **O2:** Completitud $\ge 98\%$ e Integridad SHA-256 $100\%$; **O3:** $0$ datos personales y cobertura de pruebas $\ge 80\%$. |

## Relatoría de etapa
De acuerdo con la guía oficial (Sección 2, pág. 5), las relatorías de etapa se entregan en E1, E2 y E3 (`docs/relatoria-E1.md` a `E3.md`); la trazabilidad de arranque de E0 se documenta en [`docs/E0/propuesta.md`](propuesta.md), [`docs/E0/verificacion.md`](verificacion.md) y los registros PSP en [`calidad/`](../../calidad/).

## Issues de la entrega anterior
No aplica en `E0` (primera entrega del proyecto integrador).

## Uso de IA generativa
Se utilizó asistencia de IA generativa (Antigravity / Gemini) como apoyo para estructurar las plantillas Markdown del repositorio, automatizar el flujo de GitHub Actions (`.github/workflows/captura-bronce.yml`) y generar la suite de pruebas unitarias en `tests/`, verificando y validando localmente cada script, cálculo agroclimático y hash criptográfico.
