# Objetivos de Calidad Medibles del Observatorio (Arranque E0 → Plan SQA E1)

**Observatorio:** Agroclima y Precios del Limón Mexicano en Colima (`tdl-escareno-limon-colima`)  
**Responsable (PSP / Quality Lead):** Norberto Daniel Escareño Montaño (`23460323`)

De acuerdo con los lineamientos del Proyecto Integrador **Trusted Data Lab** (Sección 6 · E0 y Sección 6 · E3 *Sello TDL*), se establecen **tres objetivos de calidad cuantitativos, medibles y auditables** desde el arranque en la Capa Bronce:

---

## 1. Objetivo O1 · Disponibilidad y Fiabilidad Operativa de la Máquina de Captura
- **Métrica:** Disponibilidad real del sistema de ingesta programada:
  $$A = \frac{\text{MTBF}}{\text{MTBF} + \text{MTTR}} \times 100\%$$
  y Tasa de Éxito de Ejecución Diaria ($\text{Corridas Exitosas} / \text{Corridas Programadas}$).
- **Umbral Mínimo Comprometido:** **$A \ge 95.0\%$** y tasa de éxito $\ge 95.0\%$ en ventanas móviles de 7 y 14 días.
- **Instrumento de Medición:** Bitácora estructurada [`calidad/bitacora_capturas.jsonl`](bitacora_capturas.jsonl) alimentada en cada corrida de `.github/workflows/captura-bronce.yml` y auditada por `pipeline/verificar_e0.py`.

---

## 2. Objetivo O2 · Completitud, Horizonte Histórico e Integridad Criptográfica en Capa Bronce
- **Métrica:**
  1. **Horizonte histórico mínimo:** $\ge 36$ periodos mensuales continuos por serie base (**actualmente 60 meses: 2021-01 a 2025-12**, superando en $66.7\%$ el mínimo requerido).
  2. **Completitud de celdas críticas:** $\ge 98.0\%$ de valores no nulos en variables climáticas (`temp_max_c`, `temp_min_c`, `precipitacion_mm`, `evapotranspiracion_et0_mm`) y de precios (`precio_frecuente_mxn_kg`).
  3. **Integridad de archivo:** $100\%$ de coincidencia entre el hash **SHA-256** calculado sobre cada archivo CSV en `data/bronce/` y su ficha técnica `.meta.json`.
- **Umbral Mínimo Comprometido:** **$100\%$ de integridad SHA-256** y **$\ge 98.0\%$ de completitud** en Capa Bronce (y $\ge 95.0\%$ en Capa Oro para el Sello TDL bajo ISO/IEC 25012).
- **Instrumento de Medición:** Ejecución automática de `python -m pipeline.verificar_e0` y pruebas unitarias en `tests/test_fuentes_bronce.py`.

---

## 3. Objetivo O3 · Cumplimiento Ético, Cero Datos Personales (LFPDPPP) y Calidad del Código
- **Métrica:**
  1. **Exposición de Datos Personales (PII) y Secretos:** $0$ columnas o registros con datos personales identificables en `data/bronce/` y $0$ credenciales expuestas en el historial de Git.
  2. **Respeto a `robots.txt` y Tasa de Peticiones:** Pausa mínima obligatoria $\ge 1.5\text{ s}$ entre peticiones al mismo dominio (`ExtractorEtico`), con evidencia archivada en `data/bronce/robots_txt/`.
  3. **Cobertura de Pruebas y Trazabilidad PSP:** Cobertura de pruebas automáticas $\ge 80\%$ (umbral Sello TDL: $\ge 60\%$) y el $100\%$ de los defectos detectados registrados con su tiempo de corrección y fase PSP en [`calidad/defectos-norberto.csv`](defectos-norberto.csv).
- **Umbral Mínimo Comprometido:** **$0$ datos personales**, **$0$ secretos expuestos** y **$\ge 80\%$ de cobertura en `pytest`**.
- **Instrumento de Medición:** Suite `tests/` ejecutada en cada corrida de GitHub Actions y auditoría de esquemas en `pipeline/verificar_e0.py`.
