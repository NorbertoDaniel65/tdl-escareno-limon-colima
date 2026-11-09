# CITRO-DATA LAB COLIMA · Observatorio Agroclimático y de Precios Mayoristas del Limón Mexicano

**Proyecto Integrador Colegiado · TRUSTED DATA LAB (Unidades 3 y 4 · Semestre Ago–Dic 2026)**  
**Tecnológico Nacional de México · Instituto Tecnológico de Colima**

- **Alumno / Responsable:** Norberto Daniel Escareño Montaño (`No. Control: 23460323` · `@NorbertoDaniel65`)
- **Asignaturas:**
  - **Ingeniería de Datos (`CMD-2602`):** Mtro. Armando Román Gallardo Heredia (`armando.gallardo@colima.tecnm.mx`)
  - **Análisis Estadístico para Ciencia de Datos:** Mtro. Mónico Joel Sánchez Velasco (`joel.sanchez@colima.tecnm.mx`)
- **Estado actual:** **Entrega `E0` completada y verificada** (Etiqueta: [`e0`](docs/E0/ENTREGA.md)).

---

## 🎯 ¿Qué observa CITRO-DATA LAB COLIMA?

El observatorio monitorea, integra y analiza la dinámica agroclimática de los **4 municipios citrícolas clave del estado de Colima** (**Tecomán, Armería, Manzanillo y Colima**) frente al comportamiento de los precios mayoristas del **Limón con semilla #5 (Limón Mexicano - *Citrus aurantifolia*)** en **4 plazas nacionales de referencia** (**Colima, Guadalajara, CDMX y Monterrey**), con el propósito de ayudar a productores, empacadoras y comercializadoras regionales a anticipar ventanas de escasez, sobreproducción y diferenciales de arbitraje (*spreads* logísticos).

---

## 📂 Estructura del Repositorio (Kit de Arranque Oficial TDL)

```text
tdl-escareno-limon-colima/
├── README.md                  # Descripción general, arquitectura e instrucciones de ejecución
├── docs/
│   ├── E0/
│   │   ├── ENTREGA.md         # Ficha oficial de entrega E0 con enlaces directos a cada evidencia
│   │   ├── propuesta.md       # Propuesta técnica y analítica (ficha, entrevista, preguntas E1-E3, plan legal)
│   │   └── verificacion.md    # Inventario criptográfico SHA-256 y guía de reproducción
│   └── fuentes/
│       ├── README.md          # Síntesis del plan de recopilación y reglas éticas
│       ├── open_meteo.md      # Documentación técnica, diccionario y análisis legal de Open-Meteo API
│       └── sniim_agro.md      # Documentación técnica, diccionario y análisis legal de SNIIM (SE)
├── calidad/
│   ├── README.md              # Descripción del sistema PSP y aseguramiento de calidad
│   ├── objetivos.md           # Los 3 objetivos de calidad medibles (O1 Disponibilidad, O2 Completitud, O3 Privacidad)
│   ├── tiempo-norberto.csv    # Registro individual de tiempos PSP
│   ├── defectos-norberto.csv  # Registro individual de defectos PSP
│   └── bitacora_capturas.jsonl # Bitácora activa de ejecuciones del extractor ético
├── extractores/
│   ├── base.py                # ExtractorEtico (robots.txt, User-Agent, pausa >= 1.5s, backoff, SHA-256)
│   ├── open_meteo.py          # Extractor histórico (60 meses) y diario de agroclima en Colima
│   ├── sniim_limon.py         # Extractor histórico (60 meses) y monitoreo ético de precios en SNIIM
│   └── ejecutar_captura.py    # CLI de ejecución de la máquina de captura
├── pipeline/
│   └── verificar_e0.py        # Verificador automático determinista de todos los criterios de la rúbrica E0
├── data/
│   ├── bronce/                # Datos crudos particionados por fuente con fichas .meta.json (SHA-256)
│   │   ├── open_meteo/        # 7,304 registros diarios + 240 mensuales (60 meses) + snapshots diarios
│   │   ├── sniim_limon/       # 240 registros mensuales (60 meses) + cortes de monitoreo ético
│   │   └── robots_txt/        # Evidencia archivada de los archivos robots.txt verificados
│   ├── plata/                 # Datos limpios, imputados y validados por Puerta de Calidad (E1)
│   ├── oro/                   # Datasets integrados y enriquecidos listos para pronóstico y MANOVA (E1-E3)
│   └── cuarentena/            # Registros rechazados con motivo documentado (E1)
├── laboratorio/               # Notebooks reproducibles de Series de Tiempo (E1), DOE (E2) y PCA/MANOVA (E3)
├── tablero/                   # Aplicación interactiva en Streamlit (E1-E4)
├── tests/                     # Pruebas unitarias automatizadas con pytest
└── .github/workflows/
    └── captura-bronce.yml     # Máquina de captura programada diariamente (cron + workflow_dispatch)
```

---

## 🚀 Cómo Ejecutar y Verificar el Proyecto

```powershell
# 1. Clonar el repositorio e instalar dependencias
git clone https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima.git
cd tdl-escareno-limon-colima
pip install -r requirements.txt

# 2. Verificar automáticamente el cumplimiento íntegro de la Entrega E0
python -m pipeline.verificar_e0

# 3. Ejecutar pruebas unitarias
pytest -v

# 4. Ejecutar captura diaria en Capa Bronce
python -m extractores.ejecutar_captura --modo diario
```

---

## 📜 Licencias y Cumplimiento Ético
- **Datos Agroclimáticos (`data/bronce/open_meteo/`):** Open-Meteo.com / Copernicus ERA5-Land bajo licencia abierta **CC BY 4.0**.
- **Datos de Precios Mayoristas (`data/bronce/sniim_limon/`):** Sistema Nacional de Información e Integración de Mercados (SNIIM - Secretaría de Economía) bajo **Términos de Libre Uso de Datos Abiertos del Gobierno de México**.
- **Privacidad:** Cero datos personales en todas las capas del repositorio conforme a la **LFPDPPP**.
