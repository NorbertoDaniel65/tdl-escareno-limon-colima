"""
Tablero Interactivo del Observatorio CITRO-DATA LAB COLIMA (E1 + E2).
Diseño original con identidad costera-terracota de Colima (#304C53, #BC6C50, #DDAD9C, #5A2F25, #AFE0E7),
logotipo propio diseñado con Gemini y navegación superior limpia (sin barra lateral izquierda).
Autor: Norberto Daniel Escareño Montaño (23460323)
"""

from __future__ import annotations

import base64
import json
from pathlib import Path
from textwrap import dedent

import altair as alt
import pandas as pd
import pydeck as pdk
import streamlit as st
from scipy import stats

ROOT_DIR = Path(__file__).resolve().parents[1]
ORO_DIR = ROOT_DIR / "data" / "oro"
PLATA_DIR = ROOT_DIR / "data" / "plata"
CUARENTENA_DIR = ROOT_DIR / "data" / "cuarentena"
FIGURAS_E1_DIR = ROOT_DIR / "docs" / "E1" / "figuras"
FIGURAS_E2_DIR = ROOT_DIR / "docs" / "E2" / "figuras"
LOGO_PATH = ROOT_DIR / "tablero" / "assets" / "logo_citrodata.png"
REPO_URL = "https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima"

st.set_page_config(
    page_title="CITRO-DATA LAB COLIMA · Observatorio",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else "🍋",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------------------------------------------------------------
# Paleta oficial proporcionada por el usuario (Colima Costero & Tierra)
# ---------------------------------------------------------------------------
PETROL = "#304C53"      # Ancla principal (encabezados, contraste profundo, pestaña activa)
TERRACOTA = "#BC6C50"   # Acento cálido principal (destacados comerciales, picos, CTAs)
ARENA = "#DDAD9C"       # Acento cálido suave (fondos sutiles, barras secundarias)
CACAO = "#5A2F25"       # Tierra profunda (énfasis fuerte, alertas / cuarentena)
BRISA = "#AFE0E7"       # Aqua Pacífico (clima, agua, acentos frescos sobre oscuro)

# Neutros armónicos derivados para máxima legibilidad
LIENZO = "#FAF7F5"      # Fondo general alabastro arena
BLANCO = "#FFFFFF"      # Tarjetas limpias
SUP_SUAVE = "#F3ECE8"   # Superficie secundaria cálida
SUP_AGUA = "#EAF6F8"    # Superficie secundaria aqua
BORDE = "#E6DCD6"       # Borde fino cálido
TEXTO = "#24353A"       # Texto principal alto contraste
TEXTO_SUAVE = "#5A6D72" # Texto secundario legible

CATEGORIAS = {
    "Zona_Huerta_Citricola": ("Huertas citrícolas", PETROL, [48, 76, 83]),
    "Infraestructura_Empaque_Bodega": ("Empaque / Bodega", TERRACOTA, [188, 108, 80]),
    "Mercado_Abasto": ("Mercado de abasto", CACAO, [90, 47, 37]),
    "Comercio_Fruticola_Mayorista": ("Comercio frutícola", "#5FA8B5", [95, 168, 181]),
}
MESES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
    7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic",
}
NUCLEO = ["Tecomán", "Armería", "Manzanillo", "Colima"]


@st.cache_data(show_spinner=False)
def cargar_logo_b64() -> str:
    if not LOGO_PATH.exists():
        return ""
    return "data:image/png;base64," + base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")


def html(contenido: str) -> None:
    st.markdown(dedent(contenido).strip(), unsafe_allow_html=True)


def pill(texto: str, estilo: str = "agua") -> str:
    mapa = {
        "agua": f"background:{SUP_AGUA};color:{PETROL};border:1px solid {BRISA};",
        "terracota": f"background:#F9ECE7;color:{CACAO};border:1px solid {ARENA};",
        "cacao": f"background:{CACAO};color:{BLANCO};border:1px solid {CACAO};",
        "petrol": f"background:{PETROL};color:{BLANCO};border:1px solid {PETROL};",
        "neutro": f"background:{SUP_SUAVE};color:{TEXTO_SUAVE};border:1px solid {BORDE};",
    }
    return f'<span class="cd-pill" style="{mapa.get(estilo, mapa["neutro"])}">{texto}</span>'


def titulo_vista(etiqueta: str, titulo: str, descripcion: str, derecha: str = "") -> None:
    html(
        f"""
        <div class="cd-view-head">
          <div>
            <div class="cd-kicker">{etiqueta}</div>
            <h2 class="cd-title">{titulo}</h2>
            <p class="cd-desc">{descripcion}</p>
          </div>
          <div>{derecha}</div>
        </div>
        """
    )


def metric_box(etiqueta: str, valor: str, sub: str, borde: str = PETROL) -> str:
    return (
        f'<div class="cd-metric" style="--ac:{borde}">'
        f'<div class="cd-kicker">{etiqueta}</div>'
        f'<div class="cd-mval num">{valor}</div>'
        f'<div class="cd-msub">{sub}</div></div>'
    )


def estilo_altair(chart: alt.Chart) -> alt.Chart:
    return (
        chart.configure_view(strokeWidth=0, fill=BLANCO)
        .configure_axis(
            labelColor=TEXTO_SUAVE,
            titleColor=TEXTO_SUAVE,
            gridColor="#EFE8E3",
            domainColor=BORDE,
            tickColor=BORDE,
            labelFont="Inter, sans-serif",
            titleFont="Inter, sans-serif",
            labelFontSize=11.5,
            titleFontSize=12,
        )
        .configure_title(
            font="Plus Jakarta Sans, Inter, sans-serif",
            fontSize=15,
            fontWeight=700,
            color=PETROL,
            anchor="start",
            offset=12,
        )
        .configure_legend(
            labelColor=TEXTO,
            titleColor=TEXTO_SUAVE,
            labelFont="Inter, sans-serif",
            labelFontSize=11.5,
        )
    )


# ---------------------------------------------------------------------------
# Estilos CSS originales (Paleta Colima: #304C53, #BC6C50, #DDAD9C, #5A2F25, #AFE0E7)
# ---------------------------------------------------------------------------
html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@600;700;800&display=swap');

    /* Eliminar completamente la barra lateral izquierda */
    [data-testid="stSidebar"],
    [data-testid="stSidebarCollapsedControl"],
    section[data-testid="stSidebar"] {
      display: none !important;
      width: 0 !important;
    }

    html, body, [data-testid="stAppViewContainer"], .stApp {
      background-color: #FAF7F5 !important;
      color: #24353A !important;
      font-family: "Inter", system-ui, -apple-system, "Segoe UI", sans-serif !important;
    }
    header[data-testid="stHeader"] {
      background: rgba(250, 247, 245, 0.88) !important;
      backdrop-filter: blur(8px);
    }
    .block-container {
      padding-top: 2.8rem !important;
      padding-bottom: 3rem !important;
      padding-left: 2.2rem !important;
      padding-right: 2.2rem !important;
      max-width: 1360px !important;
    }
    h1, h2, h3, h4, .cd-display {
      font-family: "Plus Jakarta Sans", "Inter", sans-serif !important;
      letter-spacing: -0.02em;
    }
    .num { font-variant-numeric: tabular-nums lining-nums; }

    /* Barra de marca superior */
    .cd-navbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 16px;
      flex-wrap: wrap;
      padding: 4px 0 16px 0;
      border-bottom: 1px solid #E6DCD6;
      margin-bottom: 16px;
    }
    .cd-brand {
      display: flex;
      align-items: center;
      gap: 13px;
    }
    .cd-brand-logo {
      width: 44px;
      height: 44px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(48, 76, 83, 0.22);
      display: block;
    }
    .cd-brand-name {
      font-family: "Plus Jakarta Sans", sans-serif;
      font-weight: 800;
      font-size: 1.24rem;
      color: #304C53;
      line-height: 1.1;
    }
    .cd-brand-sub {
      font-size: 0.8rem;
      color: #5A6D72;
      font-weight: 500;
    }
    .cd-nav-meta {
      display: flex;
      align-items: center;
      gap: 9px;
      flex-wrap: wrap;
    }
    .cd-live {
      display: inline-flex;
      align-items: center;
      gap: 7px;
      background: #EAF6F8;
      color: #304C53;
      border: 1px solid #AFE0E7;
      padding: 6px 13px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
    }
    .cd-live-dot {
      width: 8px; height: 8px; border-radius: 50%; background: #BC6C50; display: inline-block;
    }
    .cd-author {
      background: #FFFFFF;
      color: #5A6D72;
      border: 1px solid #E6DCD6;
      padding: 6px 13px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 600;
    }
    .cd-link-btn {
      text-decoration: none !important;
      background: #304C53;
      color: #FFFFFF !important;
      padding: 6px 14px;
      border-radius: 999px;
      font-size: 0.78rem;
      font-weight: 700;
      transition: opacity 0.15s;
    }
    .cd-link-btn:hover { opacity: 0.9; }

    /* Navegación superior en pestañas (React Aria + BaseWeb compatible) */
    div[data-testid="stTabs"] [role="tablist"],
    div[data-testid="stTabs"] [data-baseweb="tab-list"] {
      background: #FFFFFF !important;
      border: 1px solid #E6DCD6 !important;
      border-radius: 14px !important;
      padding: 5px !important;
      gap: 5px !important;
      flex-wrap: wrap !important;
      box-shadow: 0 2px 10px rgba(48, 76, 83, 0.05) !important;
      margin-bottom: 20px !important;
      border-bottom: 1px solid #E6DCD6 !important;
    }
    div[data-testid="stTabs"] .react-aria-SelectionIndicator,
    div[data-testid="stTabs"] [data-baseweb="tab-highlight"],
    div[data-testid="stTabs"] [data-baseweb="tab-border"] {
      display: none !important;
      height: 0 !important;
    }
    div[data-testid="stTabs"] [data-testid="stTab"][role="tab"],
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
      background: transparent !important;
      color: #5A6D72 !important;
      border-radius: 10px !important;
      padding: 8px 16px !important;
      margin: 0 !important;
      font-family: "Plus Jakarta Sans", sans-serif !important;
      font-weight: 600 !important;
      font-size: 0.87rem !important;
      height: auto !important;
      min-height: 36px !important;
      border: none !important;
      cursor: pointer !important;
      transition: all 0.15s ease !important;
    }
    div[data-testid="stTabs"] [data-testid="stTab"] p,
    div[data-testid="stTabs"] button[data-baseweb="tab"] p {
      margin: 0 !important;
      font-weight: inherit !important;
      color: inherit !important;
    }
    div[data-testid="stTabs"] [data-testid="stTab"][role="tab"]:hover,
    div[data-testid="stTabs"] button[data-baseweb="tab"]:hover {
      background: #F3ECE8 !important;
      color: #304C53 !important;
    }
    div[data-testid="stTabs"] [data-testid="stTab"][role="tab"][aria-selected="true"],
    div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {
      background: #BC6C50 !important;
      color: #FFFFFF !important;
      font-weight: 700 !important;
      border-radius: 10px !important;
      padding: 8px 18px !important;
      box-shadow: 0 4px 12px -3px rgba(188, 108, 80, 0.45) !important;
    }

    /* Portada split original de CITRO-DATA (NO copia de KOVA) */
    .cd-home-split {
      display: grid;
      grid-template-columns: 1.2fr 1fr;
      gap: 18px;
      margin-bottom: 18px;
      align-items: stretch;
    }
    @media (max-width: 960px) {
      .cd-home-split { grid-template-columns: 1fr; }
    }
    .cd-hero-left {
      background: linear-gradient(135deg, #304C53 0%, #243C42 65%, #3B5B63 100%);
      color: #FFFFFF;
      border-radius: 22px;
      padding: 32px 34px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 14px 32px -14px rgba(48, 76, 83, 0.45);
      position: relative;
      overflow: hidden;
    }
    .cd-hero-bar {
      width: 56px; height: 5px; border-radius: 99px; background: #BC6C50; margin-bottom: 14px;
    }
    .cd-hero-kicker {
      font-size: 0.72rem; font-weight: 700; letter-spacing: 0.11em; text-transform: uppercase; color: #AFE0E7;
    }
    .cd-hero-h1 {
      font-family: "Plus Jakarta Sans", sans-serif;
      font-size: clamp(1.75rem, 3vw, 2.5rem);
      font-weight: 800;
      line-height: 1.12;
      color: #FFFFFF;
      margin: 10px 0 12px 0;
    }
    .cd-hero-h1 span { color: #AFE0E7; }
    .cd-hero-p {
      font-size: 0.96rem;
      line-height: 1.56;
      color: #E2EEF0;
      margin: 0 0 20px 0;
    }
    .cd-hero-highlights {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .cd-hero-chip {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(175, 224, 231, 0.28);
      border-radius: 14px;
      padding: 12px 14px;
    }
    .cd-hero-chip .lbl { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.08em; color: #AFE0E7; font-weight: 700; }
    .cd-hero-chip .val { font-family: "Plus Jakarta Sans", sans-serif; font-size: 1.25rem; font-weight: 800; color: #FFFFFF; margin-top: 2px; }
    .cd-hero-chip .sub { font-size: 0.76rem; color: #DDAD9C; font-weight: 600; }

    /* Panel derecho del resumen: 4 señales clave */
    .cd-hero-right {
      background: #FFFFFF;
      border: 1px solid #E6DCD6;
      border-radius: 22px;
      padding: 24px 26px;
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      box-shadow: 0 6px 22px -12px rgba(90, 47, 37, 0.14);
    }
    .cd-snap-header {
      display: flex;
      align-items: center;
      gap: 12px;
      padding-bottom: 14px;
      border-bottom: 1px solid #EFE8E3;
      margin-bottom: 14px;
    }
    .cd-snap-grid {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 12px;
    }
    .cd-snap-item {
      background: #FAF7F5;
      border: 1px solid #EFE8E3;
      border-left: 4px solid var(--c);
      border-radius: 14px;
      padding: 12px 14px;
    }
    .cd-snap-item .sk { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.08em; color: #5A6D72; font-weight: 700; }
    .cd-snap-item .sv { font-family: "Plus Jakarta Sans", sans-serif; font-size: 1.42rem; font-weight: 800; color: #304C53; margin: 2px 0; }
    .cd-snap-item .ss { font-size: 0.76rem; color: #5A6D72; }

    /* Tira de 3 pasos "Cómo usar" */
    .cd-steps {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 14px;
      margin-bottom: 20px;
    }
    @media (max-width: 860px) {
      .cd-steps { grid-template-columns: 1fr; }
    }
    .cd-step {
      background: #FFFFFF;
      border: 1px solid #E6DCD6;
      border-radius: 16px;
      padding: 16px 18px;
      display: flex;
      gap: 14px;
      align-items: flex-start;
    }
    .cd-step-num {
      width: 34px; height: 34px; border-radius: 10px;
      background: #EAF6F8; color: #304C53;
      font-family: "Plus Jakarta Sans", sans-serif;
      font-weight: 800; font-size: 0.9rem;
      display: flex; align-items: center; justify-content: center; flex-shrink: 0;
      border: 1px solid #AFE0E7;
    }
    .cd-step h4 { margin: 0 0 3px 0; font-size: 0.95rem; color: #304C53; font-weight: 700; }
    .cd-step p { margin: 0; font-size: 0.82rem; color: #5A6D72; line-height: 1.45; }

    /* Componentes reutilizables */
    .cd-view-head {
      display: flex; justify-content: space-between; align-items: flex-end; gap: 16px; flex-wrap: wrap;
      margin: 2px 0 18px 0;
    }
    .cd-kicker {
      font-size: 0.71rem; font-weight: 700; letter-spacing: 0.1em; text-transform: uppercase; color: #BC6C50;
    }
    .cd-title {
      font-family: "Plus Jakarta Sans", sans-serif;
      font-size: 1.75rem; font-weight: 800; color: #304C53; margin: 3px 0 4px 0; line-height: 1.12;
    }
    .cd-desc { font-size: 0.9rem; color: #5A6D72; margin: 0; max-width: 78ch; }
    .cd-pill {
      display: inline-flex; align-items: center; gap: 5px;
      padding: 5px 12px; border-radius: 999px; font-size: 0.75rem; font-weight: 700;
      white-space: nowrap; flex-shrink: 0; margin: 2px 4px 2px 0;
    }
    .cd-card {
      background: #FFFFFF;
      border: 1px solid #E6DCD6;
      border-radius: 18px;
      padding: 20px 22px;
      box-shadow: 0 4px 16px -10px rgba(48, 76, 83, 0.12);
      height: 100%;
    }
    .cd-metric-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(195px, 1fr));
      gap: 14px;
      margin-bottom: 18px;
    }
    .cd-metric {
      background: #FFFFFF;
      border: 1px solid #E6DCD6;
      border-top: 4px solid var(--ac);
      border-radius: 16px;
      padding: 15px 17px;
    }
    .cd-mval {
      font-family: "Plus Jakarta Sans", sans-serif;
      font-size: 1.65rem; font-weight: 800; color: #304C53; margin: 4px 0 2px 0; line-height: 1.12;
    }
    .cd-msub { font-size: 0.8rem; color: #5A6D72; }

    /* Semáforo mensual 2026 con tu paleta exacta */
    .cd-mes {
      border-radius: 15px;
      padding: 12px 10px;
      text-align: center;
      margin-bottom: 10px;
      background: var(--bg);
      color: var(--fg);
      border: 1px solid var(--bd);
    }
    .cd-mes .mn { font-size: 0.74rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; opacity: 0.85; }
    .cd-mes .mp { font-family: "Plus Jakarta Sans", sans-serif; font-size: 1.4rem; font-weight: 800; margin: 3px 0; }
    .cd-mes .mi { font-size: 0.72rem; opacity: 0.82; }
    .cd-mes .mt { font-size: 0.73rem; font-weight: 700; margin-top: 4px; }

    /* Ficha de linaje */
    .cd-trace-row {
      display: flex; gap: 12px; padding: 8px 0; border-bottom: 1px solid #EFE8E3; font-size: 0.85rem;
    }
    .cd-trace-row:last-child { border-bottom: none; }
    .cd-trace-k { min-width: 145px; color: #5A6D72; font-weight: 700; }
    .cd-trace-v { color: #24353A; font-family: Consolas, monospace; word-break: break-all; }

    /* Barra de progreso limpia */
    .cd-bar-track { height: 10px; background: #F3ECE8; border-radius: 999px; overflow: hidden; margin-top: 8px; }
    .cd-bar-fill { height: 100%; border-radius: 999px; }

    /* Leyenda mapa */
    .cd-legend {
      display: flex; flex-wrap: wrap; gap: 14px; font-size: 0.8rem; color: #5A6D72; margin: 8px 0 4px 2px;
    }
    .cd-legend .dot {
      display: inline-block; width: 10px; height: 10px; border-radius: 50%; margin-right: 6px; vertical-align: -1px;
    }

    [data-testid="stDataFrame"] {
      background: #FFFFFF;
      border: 1px solid #E6DCD6;
      border-radius: 14px;
      padding: 6px;
    }
    .cd-footer {
      margin-top: 30px;
      padding-top: 14px;
      border-top: 1px solid #E6DCD6;
      font-size: 0.79rem;
      color: #5A6D72;
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 10px;
    }
    .cd-footer a { color: #BC6C50; font-weight: 700; text-decoration: none; }
    .cd-footer a:hover { text-decoration: underline; }
    </style>
    """
)


# ---------------------------------------------------------------------------
# Carga de artefactos (caché)
# ---------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def cargar_csv(ruta: str) -> pd.DataFrame:
    return pd.read_csv(ROOT_DIR / ruta)


@st.cache_data(show_spinner=False)
def cargar_json(ruta: str) -> dict:
    return json.loads((ROOT_DIR / ruta).read_text(encoding="utf-8"))


@st.cache_data(show_spinner=False)
def cargar_geojson_municipios() -> dict:
    gj = json.loads((ORO_DIR / "perfil_geoespacial_municipios_oro.geojson").read_text(encoding="utf-8"))
    for feat in gj["features"]:
        p = feat["properties"]
        if bool(p.get("en_observatorio_citricola")):
            w = float(p.get("peso_siap_limon", 0.0))
            p["fill"] = [48, 76, 83, int(70 + 240 * w)]
            p["line"] = [48, 76, 83, 235]
        else:
            p["fill"] = [221, 173, 156, 48]
            p["line"] = [188, 108, 80, 120]
    return gj


serie_oro = cargar_csv("data/oro/serie_mensual_oro_60m.csv")
pronostico = cargar_csv("data/oro/pronostico_e1_limon.csv")
comp_modelos = cargar_csv("data/oro/comparativa_modelos_pronostico_e1.csv")
cuarentena = cargar_csv("data/cuarentena/cuarentena_registros.csv")
cuarentena_geo = cargar_csv("data/cuarentena/cuarentena_geoespacial_e2.csv")
perfil_geo = cargar_csv("data/oro/perfil_geoespacial_municipios_oro.csv")
pts_geo_plata = cargar_csv("data/plata/infraestructura_agrologistica_colima_plata.csv")
catalogo_linaje = cargar_csv("data/oro/catalogo_linaje_oro_bronce.csv")
anova_2_3 = cargar_csv("data/oro/anova_factorial_2_3_e2.csv")
efectos_2_3 = cargar_csv("data/oro/efectos_factorial_2_3_e2.csv")
corridas_2_3 = cargar_csv("data/oro/experimento_factorial_2_3_corridas_e2.csv")
corridas_2x3 = cargar_csv("data/oro/experimento_dos_factores_2x3_e2.csv")
confirmacion = cargar_csv("data/oro/corrida_confirmacion_optimo_e2.csv")
alias_2_4 = cargar_csv("data/oro/estructura_alias_2_4_fraccionado_e2.csv")
iso_25010 = cargar_csv("data/oro/evaluacion_iso_25010_e2.csv")
iso_25012 = cargar_csv("data/oro/evaluacion_iso_25012_e2.csv")

rep_puerta = cargar_json("data/cuarentena/reporte_puerta_calidad.json")
diag_ts = cargar_json("data/oro/diagnostico_series_tiempo_e1.json")
res_geo = cargar_json("data/oro/resumen_geoespacial_e2.json")
res_linaje = cargar_json("data/oro/linaje_datos_e2.json")
res_doe = cargar_json("data/oro/resumen_experimento_doe_e2.json")
res_iso = cargar_json("data/oro/resumen_evaluacion_iso_e2.json")

ganador = comp_modelos.iloc[0]
conf = res_doe["corrida_confirmacion"]
sup = res_doe["diseno_2_3"]["supuestos_residuos_escala_lineal"]
clima_r = rep_puerta["resumen_clima_diario"]
sniim_r = rep_puerta["resumen_sniim_mensual"]
ev_tab = clima_r["registros_evaluados_bronce"] + sniim_r["registros_evaluados_bronce"]
ap_tab = clima_r["registros_aprobados_plata"] + sniim_r["registros_aprobados_plata"]
ev_geo = res_geo["puntos_bronce_evaluados"]
ap_geo = res_geo["puntos_aprobados_dentro_colima_plata"]
total_cuarentena = len(cuarentena) + len(cuarentena_geo)
futuro_2026 = pronostico[pronostico["horizonte"] == "Pronostico_Futuro_2026"].reset_index(drop=True)
pico_2026 = futuro_2026.loc[futuro_2026["pronostico_puntual_mxn_kg"].idxmax()]
valle_2026 = futuro_2026.loc[futuro_2026["pronostico_puntual_mxn_kg"].idxmin()]
tecoman_geo = perfil_geo[perfil_geo["cvegeo"] == 6009].iloc[0]
logo_src = cargar_logo_b64()

# ---------------------------------------------------------------------------
# Barra superior original con logotipo diseñado con Gemini (sin barra lateral)
# ---------------------------------------------------------------------------
logo_img_tag = f'<img class="cd-brand-logo" src="{logo_src}" alt="Logo CITRO-DATA LAB COLIMA" />' if logo_src else ""
html(
    f"""
    <div class="cd-navbar">
      <div class="cd-brand">
        {logo_img_tag}
        <div>
          <div class="cd-brand-name">CITRO-DATA LAB COLIMA</div>
          <div class="cd-brand-sub">Observatorio agroclimático, geoespacial y de precios del limón mexicano</div>
        </div>
      </div>
      <div class="cd-nav-meta">
        <span class="cd-live"><span class="cd-live-dot"></span>Operando · {res_iso['fiabilidad_acumulada_e0_e2']['disponibilidad_real_pct']}% disponibilidad</span>
        <span class="cd-author">Norberto Escareño · 23460323</span>
        <a class="cd-link-btn" href="{REPO_URL}" target="_blank">GitHub (E2) ↗</a>
      </div>
    </div>
    """
)

# 6 pestañas claras en una sola línea horizontal
tab_resumen, tab_precios, tab_mapa, tab_linaje, tab_doe, tab_calidad = st.tabs(
    [
        "Resumen",
        "Precios 2026",
        "Mapa Colima",
        "Linaje",
        "Experimento 2³",
        "Calidad y Ética",
    ]
)

# ===========================================================================
# PESTAÑA 1 · RESUMEN (Orientada a negocio y fácil de entender al instante)
# ===========================================================================
with tab_resumen:
    logo_snap = f'<img src="{logo_src}" style="width:42px;height:42px;border-radius:11px;" alt="CITRO-DATA"/>' if logo_src else ""
    html(
        f"""
        <div class="cd-home-split">
          <div class="cd-hero-left">
            <div>
              <div class="cd-hero-bar"></div>
              <div class="cd-hero-kicker">Observatorio Citrícola · Valle de Tecomán, Armería, Manzanillo y Colima</div>
              <h1 class="cd-hero-h1">Decide <span>cuándo cortar</span> y hacia dónde enviar tu limón.</h1>
              <p class="cd-hero-p">
                Reunimos clima histórico de Colima, precios mayoristas oficiales de SNIIM e infraestructura real en mapa
                para que empacadoras y productores negocien con números verificados en lugar de rumores.
              </p>
            </div>
            <div class="cd-hero-highlights">
              <div class="cd-hero-chip">
                <div class="lbl">Mejor ventana 2026</div>
                <div class="val num">${pico_2026['pronostico_puntual_mxn_kg']:.2f} MXN/kg</div>
                <div class="sub">Pico en {MESES[int(pico_2026['anio_mes'][-2:])]} · Ene–Abr alto</div>
              </div>
              <div class="cd-hero-chip">
                <div class="lbl">Temporada baja 2026</div>
                <div class="val num">${valle_2026['pronostico_puntual_mxn_kg']:.2f} MXN/kg</div>
                <div class="sub">Valle en {MESES[int(valle_2026['anio_mes'][-2:])]} · desviar a industria</div>
              </div>
            </div>
          </div>

          <div class="cd-hero-right">
            <div class="cd-snap-header">
              {logo_snap}
              <div>
                <div class="cd-kicker">Estado del observatorio · E1 + E2</div>
                <div style="font-family:'Plus Jakarta Sans',sans-serif;font-weight:800;font-size:1.12rem;color:{PETROL};">
                  Indicadores clave listos para decidir
                </div>
              </div>
            </div>
            <div class="cd-snap-grid">
              <div class="cd-snap-item" style="--c:{TERRACOTA}">
                <div class="sk">Precisión SARIMA</div>
                <div class="sv num">{100 - ganador['MAPE_test_pct']:.1f}%</div>
                <div class="ss">Error MAPE {ganador['MAPE_test_pct']:.2f}% en 2025</div>
              </div>
              <div class="cd-snap-item" style="--c:{PETROL}">
                <div class="sk">Nodos en Colima</div>
                <div class="sv num">{ap_geo:,}</div>
                <div class="ss">0 PII · {len(cuarentena_geo)} en cuarentena</div>
              </div>
              <div class="cd-snap-item" style="--c:{BRISA}">
                <div class="sk">Linaje Capa Oro</div>
                <div class="sv num">{res_linaje['cobertura_trazabilidad_pct']:.0f}%</div>
                <div class="ss">{res_linaje['total_registros_oro_rastreados']} registros rastreables</div>
              </div>
              <div class="cd-snap-item" style="--c:{CACAO}">
                <div class="sk">Calidad & Velocidad</div>
                <div class="sv num">{conf['factor_aceleracion_speedup']}×</div>
                <div class="ss">ISO {res_iso['iso_25010_promedio_100']:.0f}/{res_iso['iso_25012_promedio_100']:.0f} · -{conf['reduccion_disco_pct']}% disco</div>
              </div>
            </div>
          </div>
        </div>

        <div class="cd-steps">
          <div class="cd-step">
            <div class="cd-step-num">01</div>
            <div>
              <h4>Consulta los precios 2026</h4>
              <p>Abre <b>Precios 2026</b> para ver el semáforo mensual y negociar mejor en báscula según la temporada.</p>
            </div>
          </div>
          <div class="cd-step">
            <div class="cd-step-num">02</div>
            <div>
              <h4>Evalúa rutas y zonas</h4>
              <p>Explora <b>Mapa Colima</b> para ubicar huertas, bodegas y distancias al Puerto de Manzanillo y Autopista 54D.</p>
            </div>
          </div>
          <div class="cd-step">
            <div class="cd-step-num">03</div>
            <div>
              <h4>Audita la confianza</h4>
              <p>Revisa <b>Linaje</b> y <b>Calidad y Ética</b> para confirmar el origen SHA-256 y los {total_cuarentena} datos apartados en cuarentena.</p>
            </div>
          </div>
        </div>
        """
    )

    c_prev1, c_prev2 = st.columns([1.35, 1])
    with c_prev1:
        f_prev = futuro_2026.copy()
        f_prev["mes_lbl"] = f_prev["anio_mes"].apply(lambda ym: MESES[int(ym[-2:])])
        f_prev["franja"] = f_prev["pronostico_puntual_mxn_kg"].apply(
            lambda p: "Alta rentabilidad (> $28)" if p >= 28 else "Cosecha / operación estándar"
        )
        graf_prev = alt.Chart(f_prev, title="Panorama mensual de precios proyectados 2026 (MXN/kg)").mark_bar(
            cornerRadiusTopLeft=6, cornerRadiusTopRight=6
        ).encode(
            x=alt.X("mes_lbl:N", sort=list(MESES.values()), title=None),
            y=alt.Y("pronostico_puntual_mxn_kg:Q", title="MXN / kg"),
            color=alt.Color(
                "franja:N",
                scale=alt.Scale(domain=["Alta rentabilidad (> $28)", "Cosecha / operación estándar"], range=[TERRACOTA, PETROL]),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=[
                alt.Tooltip("anio_mes:N", title="Mes"),
                alt.Tooltip("pronostico_puntual_mxn_kg:Q", title="Pronóstico (MXN/kg)", format="$.2f"),
                alt.Tooltip("limite_inferior_ic95_mxn_kg:Q", title="Mín. IC 95%", format="$.2f"),
                alt.Tooltip("limite_superior_ic95_mxn_kg:Q", title="Máx. IC 95%", format="$.2f"),
            ],
        ).properties(height=280)
        st.altair_chart(estilo_altair(graf_prev), width="stretch")

    with c_prev2:
        nucleo_df = perfil_geo[perfil_geo["en_observatorio_citricola"]].copy()
        filas_m = ""
        for _, r in nucleo_df.iterrows():
            pct = int(round(r["peso_siap_limon"] * 100))
            filas_m += (
                f'<div style="margin-bottom:13px;">'
                f'<div style="display:flex;justify-content:space-between;font-size:.86rem;font-weight:700;color:{PETROL};">'
                f'<span>{r["nombre_oficial"]} <span style="font-weight:500;color:{TEXTO_SUAVE};">· {int(r["n_nodos_agrologisticos_total"])} nodos</span></span>'
                f'<span class="num" style="color:{TERRACOTA};">{pct}% SIAP · {r["dist_puerto_manzanillo_km"]:.0f} km Pto</span></div>'
                f'<div class="cd-bar-track"><div class="cd-bar-fill" style="width:{pct}%;background:{PETROL};"></div></div></div>'
            )
        html(
            f"""
            <div class="cd-card">
              <div class="cd-kicker">Cuenca citrícola de Colima</div>
              <h3 style="margin:4px 0 14px 0;font-size:1.15rem;color:{PETROL};">4 municipios núcleo del observatorio</h3>
              {filas_m}
              <div style="margin-top:14px;padding-top:10px;border-top:1px solid #EFE8E3;font-size:.8rem;color:{TEXTO_SUAVE};">
                Tecomán concentra <b>55%</b> de la producción estatal y está a <b>{tecoman_geo['dist_puerto_manzanillo_km']:.1f} km</b> del Puerto de Manzanillo y <b>{tecoman_geo['dist_corredor_gdl_54d_km']:.1f} km</b> de la Autopista 54D hacia Guadalajara.
              </div>
            </div>
            """
        )

# ===========================================================================
# PESTAÑA 2 · PRECIOS 2026
# ===========================================================================
with tab_precios:
    titulo_vista(
        "PRONÓSTICO DE PRECIOS MAYORISTAS · MODELO SARIMA",
        "Precios proyectados del limón mexicano en 2026",
        f"Modelo ganador {ganador['modelo']} seleccionado por menor error en prueba 2025 (MAPE {ganador['MAPE_test_pct']:.2f}%) y residuos de ruido blanco.",
        pill(f"Ljung-Box p = {diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag12_pvalue']:.3f} ✓", "agua"),
    )

    c_v1, c_v2 = st.columns(2)
    with c_v1:
        html(
            f"""
            <div class="cd-card" style="border-left:5px solid {TERRACOTA};">
              {pill("Ventana de alta rentabilidad · Ene – Abr", "terracota")}
              <h3 style="margin:8px 0 6px 0;color:{PETROL};font-size:1.15rem;">Pico proyectado: $41.6 – $43.1 MXN/kg</h3>
              <p style="font-size:.86rem;color:{TEXTO_SUAVE};margin:0;">
                La menor oferta invernal impulsa los precios mayoristas. Prioriza riegos de auxilio desde noviembre–diciembre
                para asegurar calibre #4 y #5 y negociar mejores contratos en centrales de abasto.
              </p>
            </div>
            """
        )
    with c_v2:
        html(
            f"""
            <div class="cd-card" style="border-left:5px solid {PETROL};">
              {pill("Cosecha pico · Jun – Oct", "agua")}
              <h3 style="margin:8px 0 6px 0;color:{PETROL};font-size:1.15rem;">Banda esperada: $19.0 – $23.5 MXN/kg</h3>
              <p style="font-size:.86rem;color:{TEXTO_SUAVE};margin:0;">
                Con las lluvias de verano aumenta el volumen disponible. Conviene desviar fruta de segunda a la industria
                destiladora de aceite esencial en Tecomán y evitar ventas spot sin piso de precio.
              </p>
            </div>
            """
        )
    st.write("")

    hist = serie_oro[["anio_mes", "precio_frecuente_origen_colima_mxn_kg", "es_choque_legitimo_precio"]].copy()
    hist["fecha"] = pd.to_datetime(hist["anio_mes"] + "-01")
    hist["tramo"] = "Histórico observado (SNIIM)"
    pr = pronostico.copy()
    pr["fecha"] = pd.to_datetime(pr["anio_mes"] + "-01")
    pr["tramo"] = pr["horizonte"].map(
        {"Evaluacion_Prueba_2025": "Validación 2025 (prueba)", "Pronostico_Futuro_2026": "Pronóstico 2026"}
    )
    dom_tr = ["Histórico observado (SNIIM)", "Validación 2025 (prueba)", "Pronóstico 2026"]
    esc_tr = alt.Scale(domain=dom_tr, range=[PETROL, "#5FA8B5", TERRACOTA])
    eje_x = alt.X("fecha:T", title=None, axis=alt.Axis(format="%b %Y", labelAngle=0))

    linea_hist = alt.Chart(hist).mark_line(strokeWidth=2.3).encode(
        x=eje_x,
        y=alt.Y("precio_frecuente_origen_colima_mxn_kg:Q", title="Precio frecuente en origen (MXN/kg)"),
        color=alt.Color("tramo:N", scale=esc_tr, legend=alt.Legend(title=None, orient="top")),
        tooltip=[
            alt.Tooltip("anio_mes:N", title="Mes"),
            alt.Tooltip("precio_frecuente_origen_colima_mxn_kg:Q", title="Precio real (MXN/kg)", format=".2f"),
        ],
    )
    banda_ic = alt.Chart(pr).mark_area(opacity=0.22).encode(
        x=eje_x, y="limite_inferior_ic95_mxn_kg:Q", y2="limite_superior_ic95_mxn_kg:Q",
        color=alt.Color("tramo:N", scale=esc_tr, legend=None),
    )
    linea_pr = alt.Chart(pr).mark_line(
        strokeDash=[6, 4], strokeWidth=2.6, point=alt.OverlayMarkDef(size=52, filled=True)
    ).encode(
        x=eje_x, y="pronostico_puntual_mxn_kg:Q", color=alt.Color("tramo:N", scale=esc_tr, legend=None),
        tooltip=[
            alt.Tooltip("anio_mes:N", title="Mes"),
            alt.Tooltip("pronostico_puntual_mxn_kg:Q", title="Pronóstico (MXN/kg)", format=".2f"),
            alt.Tooltip("limite_inferior_ic95_mxn_kg:Q", title="IC 95% inf.", format=".2f"),
            alt.Tooltip("limite_superior_ic95_mxn_kg:Q", title="IC 95% sup.", format=".2f"),
        ],
    )
    choques = alt.Chart(hist[hist["es_choque_legitimo_precio"]]).mark_point(
        shape="triangle-up", size=145, filled=True, color=CACAO
    ).encode(
        x=eje_x, y="precio_frecuente_origen_colima_mxn_kg:Q",
        tooltip=[alt.Tooltip("anio_mes:N", title="Choque real de escasez"), alt.Tooltip("precio_frecuente_origen_colima_mxn_kg:Q", title="MXN/kg", format=".2f")],
    )
    corte = alt.Chart(pd.DataFrame({"fecha": [pd.Timestamp("2026-01-01")]})).mark_rule(strokeDash=[4, 4], color=ARENA).encode(x="fecha:T")
    st.altair_chart(
        estilo_altair(
            alt.layer(banda_ic, linea_hist, linea_pr, choques, corte)
            .properties(height=380, title="Trayectoria del precio mayorista en origen Colima · 2021 → 2026")
            .interactive(bind_y=False)
        ),
        width="stretch",
    )
    st.caption("▲ cacao: choques reales de escasez (feb–mar 2022, feb 2024) preservados. Usa la rueda del ratón para hacer zoom temporal.")

    st.markdown("##### Semáforo mensual 2026")

    def estilo_mes(precio: float) -> tuple[str, str, str, str]:
        if precio > 38:
            return "Escasez · pico máximo", TERRACOTA, BLANCO, TERRACOTA
        if precio >= 28:
            return "Alto · buena venta", PETROL, BLANCO, PETROL
        if precio >= 18:
            return "Medio · estándar", SUP_AGUA, PETROL, BRISA
        return "Bajo · cosecha pico", "#F9ECE7", CACAO, ARENA

    for fila_ini in (0, 6):
        cols_mes = st.columns(6)
        for j, col in enumerate(cols_mes):
            r = futuro_2026.iloc[fila_ini + j]
            etq, bg, fg, bd = estilo_mes(float(r["pronostico_puntual_mxn_kg"]))
            mes_num = int(r["anio_mes"][-2:])
            col.markdown(
                f'<div class="cd-mes" style="--bg:{bg};--fg:{fg};--bd:{bd}"><div class="mn">{MESES[mes_num]} 2026</div>'
                f'<div class="mp num">${r["pronostico_puntual_mxn_kg"]:.2f}</div>'
                f'<div class="mi num">IC 95%: ${r["limite_inferior_ic95_mxn_kg"]:.0f}–${r["limite_superior_ic95_mxn_kg"]:.0f}</div>'
                f'<div class="mt">{etq}</div></div>',
                unsafe_allow_html=True,
            )

    m_a, m_b = st.columns([1, 1.35])
    with m_a:
        comp = comp_modelos.copy()
        comp["Modelo"] = comp["modelo"].str.replace(r"^\d+\.\s*", "", regex=True)
        graf_mod = alt.Chart(comp, title="Error de los 4 modelos en prueba 2025 (MAPE %)").mark_bar(cornerRadiusEnd=6).encode(
            y=alt.Y("Modelo:N", sort="x", title=None),
            x=alt.X("MAPE_test_pct:Q", title="MAPE (%) · menor es mejor"),
            color=alt.condition(alt.datum.seleccionado, alt.value(TERRACOTA), alt.value(ARENA)),
            tooltip=["Modelo:N", alt.Tooltip("MAPE_test_pct:Q", title="MAPE %"), alt.Tooltip("RMSE_test_mxn_kg:Q", title="RMSE", format=".2f")],
        )
        txt_mod = graf_mod.mark_text(align="left", dx=5, fontWeight="bold", color=PETROL).encode(
            text=alt.Text("MAPE_test_pct:Q", format=".2f"), color=alt.value(PETROL)
        )
        st.altair_chart(estilo_altair((graf_mod + txt_mod).properties(height=250)), width="stretch")
    with m_b:
        tabla_pron = futuro_2026[
            ["anio_mes", "pronostico_puntual_mxn_kg", "limite_inferior_ic95_mxn_kg", "limite_superior_ic95_mxn_kg", "recomendacion_comercial_cliente"]
        ]
        st.dataframe(
            tabla_pron, hide_index=True, width="stretch", height=300,
            column_config={
                "anio_mes": st.column_config.TextColumn("Mes"),
                "pronostico_puntual_mxn_kg": st.column_config.NumberColumn("Pronóstico (MXN/kg)", format="$%.2f"),
                "limite_inferior_ic95_mxn_kg": st.column_config.NumberColumn("IC 95% inf.", format="$%.2f"),
                "limite_superior_ic95_mxn_kg": st.column_config.NumberColumn("IC 95% sup.", format="$%.2f"),
                "recomendacion_comercial_cliente": st.column_config.TextColumn("Recomendación comercial", width="large"),
            },
        )
    with st.expander("Ver figura estática del reporte E1 (pronóstico y diagnóstico de residuos)"):
        st.image(str(FIGURAS_E1_DIR / "fig5_pronostico_final_ic95_residuos.png"), width="stretch")

# ===========================================================================
# PESTAÑA 3 · MAPA COLIMA
# ===========================================================================
with tab_mapa:
    titulo_vista(
        "FUENTE ESPECIALIZADA · GEOPANDAS + OPENSTREETMAP + INEGI",
        "Mapa geoespacial y logística de Colima",
        "Unión espacial point-in-polygon en WGS84 (EPSG:4326) y distancias métricas al Puerto de Manzanillo y Autopista 54D en UTM Zona 13N.",
        pill("ODbL 1.0 · 0 PII", "agua"),
    )

    html(
        f"""
        <div class="cd-metric-grid">
          {metric_box("Municipios", f"{res_geo['poligonos_municipales_colima']}", "4 núcleo citrícola + 6 vecinos", PETROL)}
          {metric_box("Capturados OSM", f"{ev_geo:,}", "Bounding box estatal", BRISA)}
          {metric_box("Validados en Colima", f"{ap_geo:,}", "Aprobados por sjoin(within)", TERRACOTA)}
          {metric_box("Fuera del estado", f"{len(cuarentena_geo)}", "Apartados a cuarentena espacial", CACAO)}
        </div>
        """
    )

    f1, f2 = st.columns([1.2, 1])
    cats_disp = sorted(pts_geo_plata["categoria_agrologistica"].unique())
    muns_disp = sorted(pts_geo_plata["nombre_oficial"].unique())
    with f1:
        cats_sel = st.multiselect(
            "Tipo de infraestructura", cats_disp, default=cats_disp,
            format_func=lambda c: CATEGORIAS.get(c, (c,))[0],
        )
    with f2:
        muns_sel = st.multiselect("Municipios visibles", muns_disp, default=[m for m in NUCLEO if m in muns_disp])

    sub_pts = pts_geo_plata[
        pts_geo_plata["categoria_agrologistica"].isin(cats_sel) & pts_geo_plata["nombre_oficial"].isin(muns_sel)
    ].copy()
    sub_pts["nombre"] = sub_pts["nombre_publico_lugar"].fillna("Sin denominación pública")
    sub_pts["categoria"] = sub_pts["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, (c,))[0])
    sub_pts["municipio"] = sub_pts["nombre_oficial"]
    sub_pts["color"] = sub_pts["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, ("", "", [48, 76, 83]))[2])

    c_map, c_side = st.columns([1.45, 1])
    with c_map:
        capa_municipios = pdk.Layer(
            "GeoJsonLayer", data=cargar_geojson_municipios(), stroked=True, filled=True,
            get_fill_color="properties.fill", get_line_color="properties.line", line_width_min_pixels=1.4, pickable=False,
        )
        capa_nodos = pdk.Layer(
            "ScatterplotLayer",
            data=sub_pts[["longitud", "latitud", "nombre", "categoria", "municipio", "color"]],
            get_position="[longitud, latitud]", get_fill_color="color", get_line_color=[255, 255, 255],
            get_radius=330, radius_min_pixels=3, radius_max_pixels=11, stroked=True, line_width_min_pixels=0.6,
            opacity=0.90, pickable=True,
        )
        nodos_logisticos = pd.DataFrame(
            [
                {"longitud": -104.2940, "latitud": 19.0550, "nombre": "Puerto de Manzanillo",
                 "categoria": "Nodo de exportación marítima", "municipio": "Manzanillo"},
                {"longitud": -103.6860, "latitud": 19.2770, "nombre": "Salida Autopista 54D → Guadalajara",
                 "categoria": "Corredor carretero mayorista", "municipio": "Colima"},
            ]
        )
        capa_logistica = pdk.Layer(
            "ScatterplotLayer", data=nodos_logisticos, get_position="[longitud, latitud]",
            get_fill_color=[175, 224, 231], get_line_color=[48, 76, 83], get_radius=1600, radius_min_pixels=8,
            stroked=True, line_width_min_pixels=2.2, pickable=True,
        )
        st.pydeck_chart(
            pdk.Deck(
                layers=[capa_municipios, capa_nodos, capa_logistica],
                initial_view_state=pdk.ViewState(latitude=19.08, longitude=-104.02, zoom=8.25),
                map_provider="carto", map_style="light",
                tooltip={
                    "html": "<b>{nombre}</b><br/>{categoria}<br/><i>{municipio}</i>",
                    "style": {"backgroundColor": PETROL, "color": BLANCO, "fontSize": "12px", "borderRadius": "10px"},
                },
            ),
            height=520,
        )
        leyenda = "".join(f'<span><span class="dot" style="background:{v[1]}"></span>{v[0]}</span>' for v in CATEGORIAS.values())
        html(f'<div class="cd-legend">{leyenda}<span><span class="dot" style="background:{BRISA};border:2px solid {PETROL}"></span>Nodo logístico</span></div>')
        st.caption(f"Mostrando **{len(sub_pts):,}** nodos agrologísticos validados dentro de Colima.")

    with c_side:
        conteo = (
            pts_geo_plata[pts_geo_plata["categoria_agrologistica"].isin(cats_sel)]
            .assign(categoria=lambda d: d["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, (c,))[0]))
            .groupby(["nombre_oficial", "categoria"], as_index=False)
            .size().rename(columns={"size": "nodos"})
        )
        conteo["seleccionado"] = conteo["nombre_oficial"].isin(muns_sel)
        dom_cat = [v[0] for v in CATEGORIAS.values()]
        rng_cat = [v[1] for v in CATEGORIAS.values()]
        graf_mun = alt.Chart(conteo, title="Nodos por municipio").mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("nombre_oficial:N", sort="-x", title=None),
            x=alt.X("sum(nodos):Q", title="Nodos asignados"),
            color=alt.Color(
                "categoria:N",
                scale=alt.Scale(domain=dom_cat, range=rng_cat),
                legend=alt.Legend(title=None, orient="bottom", columns=2, labelLimit=180),
            ),
            opacity=alt.condition(alt.datum.seleccionado, alt.value(1.0), alt.value(0.28)),
            tooltip=[alt.Tooltip("nombre_oficial:N", title="Municipio"), alt.Tooltip("categoria:N", title="Tipo"), alt.Tooltip("nodos:Q", title="Nodos")],
        ).properties(height=285, padding={"right": 14})
        st.altair_chart(estilo_altair(graf_mun), width="stretch")

        dist = perfil_geo[["nombre_oficial", "dist_puerto_manzanillo_km", "en_observatorio_citricola"]].copy()
        graf_dist = alt.Chart(dist, title="Distancia a Manzanillo (km)").mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("nombre_oficial:N", sort="x", title=None),
            x=alt.X("dist_puerto_manzanillo_km:Q", title="km (EPSG:32613)"),
            color=alt.condition(alt.datum.en_observatorio_citricola, alt.value(TERRACOTA), alt.value(ARENA)),
            tooltip=[alt.Tooltip("nombre_oficial:N", title="Municipio"), alt.Tooltip("dist_puerto_manzanillo_km:Q", title="Distancia (km)", format=".1f")],
        ).properties(height=230, padding={"right": 14})
        st.altair_chart(estilo_altair(graf_dist), width="stretch")

    st.markdown("##### Perfil geoespacial integrado en Capa Oro")
    tabla_geo = perfil_geo[
        ["cvegeo", "nombre_oficial", "en_observatorio_citricola", "peso_siap_limon", "superficie_km2",
         "n_huertas_citricolas_osm", "n_empaque_bodega_osm", "n_mercados_abasto_osm", "n_nodos_agrologisticos_total",
         "densidad_agrologistica_100km2", "dist_puerto_manzanillo_km", "dist_corredor_gdl_54d_km"]
    ].copy()
    tabla_geo["peso_siap_limon"] = tabla_geo["peso_siap_limon"] * 100
    st.dataframe(
        tabla_geo, hide_index=True, width="stretch",
        column_config={
            "cvegeo": st.column_config.TextColumn("CVEGEO"),
            "nombre_oficial": st.column_config.TextColumn("Municipio"),
            "en_observatorio_citricola": st.column_config.CheckboxColumn("Núcleo"),
            "peso_siap_limon": st.column_config.ProgressColumn("Peso SIAP", format="%.0f%%", min_value=0, max_value=100),
            "superficie_km2": st.column_config.NumberColumn("Área (km²)", format="%.1f"),
            "n_huertas_citricolas_osm": st.column_config.NumberColumn("Huertas"),
            "n_empaque_bodega_osm": st.column_config.NumberColumn("Empaque/Bod."),
            "n_mercados_abasto_osm": st.column_config.NumberColumn("Mercados"),
            "n_nodos_agrologisticos_total": st.column_config.ProgressColumn("Nodos", format="%d", min_value=0, max_value=int(tabla_geo["n_nodos_agrologisticos_total"].max())),
            "densidad_agrologistica_100km2": st.column_config.NumberColumn("Densidad /100 km²", format="%.1f"),
            "dist_puerto_manzanillo_km": st.column_config.NumberColumn("Dist. Pto (km)", format="%.1f"),
            "dist_corredor_gdl_54d_km": st.column_config.NumberColumn("Dist. 54D (km)", format="%.1f"),
        },
    )
    with st.expander("Ver figura cartográfica estática del reporte E2"):
        st.image(str(FIGURAS_E2_DIR / "fig1_mapa_geoespacial_colima_e2.png"), width="stretch")

# ===========================================================================
# PESTAÑA 4 · LINAJE
# ===========================================================================
with tab_linaje:
    titulo_vista(
        "TRAZABILIDAD COMPLETA · BRONCE → PLATA → ORO",
        "Auditoría de linaje registro por registro",
        "Selecciona cualquier registro de la Capa Oro para comprobar de qué archivo de Capa Bronce salió, su huella SHA-256 y su fecha UTC.",
        pill(f"{res_linaje['total_registros_oro_rastreados']} registros · 100%", "petrol"),
    )

    c_sel, c_don = st.columns([1.7, 1])
    with c_sel:
        ids = catalogo_linaje["linaje_id_registro"].tolist()
        idx_def = ids.index("ORO-SERIE-2022-02") if "ORO-SERIE-2022-02" in ids else 0
        id_sel = st.selectbox("Identificador de registro en Capa Oro:", ids, index=idx_def)
        fila_lin = catalogo_linaje[catalogo_linaje["linaje_id_registro"] == id_sel].iloc[0].to_dict()
        fuentes_pills = "".join(pill(f, "agua") for f in str(fila_lin["linaje_fuentes_bronce"]).split("+"))
        archivos = "<br>".join(str(fila_lin["linaje_archivos_bronce"]).split("|"))
        fechas = "<br>".join(str(fila_lin["linaje_fecha_ingesta_utc"]).split("|"))
        html(
            f"""
            <div class="cd-card">
              <div class="cd-kicker">Ficha verificada de origen</div>
              <div style="font-family:Consolas,monospace;font-size:1.15rem;font-weight:800;color:{PETROL};margin:4px 0 10px 0;">
                {fila_lin['linaje_id_registro']}
              </div>
              <div class="cd-trace-row"><div class="cd-trace-k">Tabla en Capa Oro</div><div class="cd-trace-v">{fila_lin['tabla_oro']}</div></div>
              <div class="cd-trace-row"><div class="cd-trace-k">Llave de negocio</div><div class="cd-trace-v">{fila_lin['llave_negocio']}</div></div>
              <div class="cd-trace-row"><div class="cd-trace-k">Fuentes origen</div><div>{fuentes_pills}</div></div>
              <div class="cd-trace-row"><div class="cd-trace-k">Archivos en Bronce</div><div class="cd-trace-v">{archivos}</div></div>
              <div class="cd-trace-row"><div class="cd-trace-k">Huella SHA-256</div><div class="cd-trace-v">{fila_lin['linaje_sha256_bronce']}</div></div>
              <div class="cd-trace-row"><div class="cd-trace-k">Ingesta UTC</div><div class="cd-trace-v">{fechas}</div></div>
              <div class="cd-trace-row"><div class="cd-trace-k">Versión pipeline</div><div class="cd-trace-v">{fila_lin['linaje_version_pipeline']}</div></div>
            </div>
            """
        )
        with st.expander("Ver registro en formato JSON"):
            st.json(fila_lin)
    with c_don:
        comp_tablas = catalogo_linaje.groupby("tabla_oro", as_index=False).size().rename(columns={"size": "registros"})
        dona = alt.Chart(comp_tablas, title="Registros por tabla Oro").mark_arc(innerRadius=64, cornerRadius=5).encode(
            theta="registros:Q",
            color=alt.Color("tabla_oro:N", scale=alt.Scale(range=[PETROL, TERRACOTA, BRISA]), legend=alt.Legend(title=None, orient="bottom", columns=1, labelLimit=260)),
            tooltip=[alt.Tooltip("tabla_oro:N", title="Tabla Oro"), alt.Tooltip("registros:Q", title="Registros")],
        ).properties(height=300)
        st.altair_chart(estilo_altair(dona), width="stretch")

    with st.expander(f"Ver catálogo completo ({len(catalogo_linaje)} registros rastreables)"):
        st.dataframe(catalogo_linaje, hide_index=True, width="stretch", height=360)
    with st.expander("Ver diagrama estático de arquitectura de linaje"):
        st.image(str(FIGURAS_E2_DIR / "fig2_arquitectura_linaje_bronce_oro_e2.png"), width="stretch")

# ===========================================================================
# PESTAÑA 5 · EXPERIMENTO 2³
# ===========================================================================
with tab_doe:
    titulo_vista(
        "DISEÑO DE EXPERIMENTOS · ANÁLISIS ESTADÍSTICO UNIDAD 4",
        "Experimento factorial 2³, ANOVA 2×3 y fraccionado 2⁴⁻¹",
        "84 corridas reales en entorno local aislado (0 tráfico externo) con aleatorización, 3 réplicas, 3 bloques y corrida de confirmación.",
        pill(f"Óptimo {res_doe['diseno_2_3']['tratamiento_optimo']} confirmado", "terracota"),
    )

    html(
        f"""
        <div class="cd-metric-grid">
          {metric_box("Línea base E1", f"{conf['observado_linea_base_media_ms']:.1f} ms", "1 hilo · iterativo · CSV", CACAO)}
          {metric_box("Óptimo A+B+C+", f"{conf['observado_optimo_media_ms']:.1f} ms", "4 hilos · Pandera · Parquet", PETROL)}
          {metric_box("Aceleración real", f"{conf['factor_aceleracion_speedup']}×", f"-{conf['mejora_tiempo_pct']}% tiempo (n = 5)", TERRACOTA)}
          {metric_box("Ahorro en disco", f"-{conf['reduccion_disco_pct']}%", "1,936.8 KB → 171.7 KB", BRISA)}
        </div>
        """
    )

    g1, g2 = st.columns(2)
    with g1:
        rank = corridas_2_3.groupby("tratamiento", as_index=False).agg(media=("tiempo_total_ms", "mean"), de=("tiempo_total_ms", "std"))
        rank["tipo"] = rank["tratamiento"].map(
            lambda t: "Óptimo" if t == "A+B+C+" else ("Línea base E1" if t == "A-B-C-" else "Otro tratamiento")
        )
        graf_rank = alt.Chart(rank, title="Tiempo medio por tratamiento (n = 3 réplicas)").mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("tratamiento:N", sort="x", title=None),
            x=alt.X("media:Q", title="Tiempo medio (ms)"),
            color=alt.Color("tipo:N", scale=alt.Scale(domain=["Óptimo", "Línea base E1", "Otro tratamiento"], range=[PETROL, CACAO, ARENA]), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("tratamiento:N", title="Tratamiento"), alt.Tooltip("media:Q", title="Media (ms)", format=".1f"), alt.Tooltip("de:Q", title="DE (ms)", format=".2f")],
        ).properties(height=305)
        st.altair_chart(estilo_altair(graf_rank), width="stretch")
    with g2:
        t_crit = float(stats.t.ppf(0.975, df=14))
        ef = efectos_2_3.copy()
        ef["Resultado"] = ef["significativo_5pct"].map({True: "Significativo (α = 0.05)", False: "No significativo"})
        barras = alt.Chart(ef, title="Diagrama de Pareto de efectos |t|").mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("descripcion:N", sort="-x", title=None),
            x=alt.X("t_absoluto:Q", title="Efecto estandarizado |t|"),
            color=alt.Color("Resultado:N", scale=alt.Scale(domain=["Significativo (α = 0.05)", "No significativo"], range=[TERRACOTA, ARENA]), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("descripcion:N", title="Efecto"), alt.Tooltip("efecto_estimado_ms:Q", title="Efecto (ms)", format="+.1f"), alt.Tooltip("p_valor:Q", title="p", format=".4g")],
        )
        regla = alt.Chart(pd.DataFrame({"t": [t_crit]})).mark_rule(color=CACAO, strokeDash=[6, 4], strokeWidth=2).encode(x="t:Q")
        st.altair_chart(estilo_altair((barras + regla).properties(height=305)), width="stretch")

    g3, g4 = st.columns(2)
    with g3:
        conf_df = confirmacion.copy()
        conf_df["escenario_corto"] = conf_df["escenario"].map(
            lambda e: "Línea base E1" if e.startswith("Linea_Base") else "Óptimo A+B+C+"
        )
        pi_inf, pi_sup = conf["ic95_prediccion_ms"]
        banda = alt.Chart(pd.DataFrame({"escenario_corto": ["Óptimo A+B+C+"], "inf": [pi_inf], "sup": [pi_sup]})).mark_bar(
            color=BRISA, opacity=0.55, size=74
        ).encode(x="escenario_corto:N", y="inf:Q", y2="sup:Q")
        medias = alt.Chart(conf_df).mark_bar(size=48, opacity=0.92, cornerRadiusTopLeft=7, cornerRadiusTopRight=7).encode(
            x=alt.X("escenario_corto:N", title=None, sort=["Línea base E1", "Óptimo A+B+C+"]),
            y=alt.Y("mean(tiempo_total_ms):Q", title="Tiempo (ms)"),
            color=alt.Color("escenario_corto:N", scale=alt.Scale(domain=["Línea base E1", "Óptimo A+B+C+"], range=[CACAO, PETROL]), legend=None),
            tooltip=[alt.Tooltip("escenario_corto:N", title="Escenario"), alt.Tooltip("mean(tiempo_total_ms):Q", title="Media (ms)", format=".1f")],
        )
        puntos = alt.Chart(conf_df).mark_circle(size=65, color=TERRACOTA, opacity=0.95).encode(
            x=alt.X("escenario_corto:N", sort=["Línea base E1", "Óptimo A+B+C+"]), y="tiempo_total_ms:Q",
            tooltip=[alt.Tooltip("replica_confirmacion:Q", title="Réplica"), alt.Tooltip("tiempo_total_ms:Q", title="Tiempo (ms)", format=".1f")],
        )
        st.altair_chart(
            estilo_altair(alt.layer(medias, banda, puntos).properties(height=285, title="Corrida de confirmación (n = 5 · banda IC 95%)")),
            width="stretch",
        )
    with g4:
        inter = corridas_2x3.groupby(["motor_validacion", "formato_persistencia"], as_index=False)["tiempo_total_ms"].mean()
        inter["Motor"] = inter["motor_validacion"].map({"iterativo": "Validación iterativa", "pandera_vectorizado": "Pandera vectorizado"})
        inter["Formato"] = inter["formato_persistencia"].map({"csv_utf8": "CSV UTF-8", "parquet_snappy": "Parquet Snappy", "parquet_zstd": "Parquet ZSTD"})
        graf_int = alt.Chart(
            inter, title=f"ANOVA de dos vías 2×3 · p(interacción) = {res_doe['diseno_dos_vias_2x3']['p_valor_interaccion_BxC']:.3f}"
        ).mark_line(point=alt.OverlayMarkDef(size=85, filled=True), strokeWidth=2.8).encode(
            x=alt.X("Formato:N", sort=["CSV UTF-8", "Parquet Snappy", "Parquet ZSTD"], title=None),
            y=alt.Y("tiempo_total_ms:Q", title="Tiempo medio (ms)"),
            color=alt.Color("Motor:N", scale=alt.Scale(domain=["Validación iterativa", "Pandera vectorizado"], range=[TERRACOTA, PETROL]), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=["Motor:N", "Formato:N", alt.Tooltip("tiempo_total_ms:Q", title="Media (ms)", format=".1f")],
        ).properties(height=285)
        st.altair_chart(estilo_altair(graf_int), width="stretch")

    html(
        f"""
        <div class="cd-metric-grid">
          {metric_box("Puerta 3 · Normalidad", f"p = {sup['shapiro_wilk_p']:.3f}", f"Shapiro-Wilk W = {sup['shapiro_wilk_W']:.3f} ✓", BRISA)}
          {metric_box("Puerta 3 · Homocedasticidad", f"p = {sup['levene_p']:.3f}", f"Levene F = {sup['levene_F']:.3f} ✓", BRISA)}
          {metric_box("Puerta 3 · Independencia", f"DW = {sup['durbin_watson']:.2f}", "Durbin-Watson ≈ 2.0 ✓", BRISA)}
          {metric_box("Ajuste del modelo", f"R² = {sup['r2_modelo']:.4f}", f"R² ajustado = {sup['r2_ajustado']:.4f}", PETROL)}
        </div>
        """
    )

    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Tabla ANOVA · Diseño factorial 2³**")
        st.dataframe(anova_2_3, hide_index=True, width="stretch")
    with t2:
        st.markdown("**Estructura de alias · 2⁴ vs. 2⁴⁻¹ (I = ABCD, Resolución IV · 50% ahorro)**")
        st.dataframe(alias_2_4, hide_index=True, width="stretch")
    with st.expander("Ver figuras estáticas del reporte E2"):
        st.image(str(FIGURAS_E2_DIR / "fig3_doe_factorial_2_3_efectos_pareto.png"), width="stretch")
        st.image(str(FIGURAS_E2_DIR / "fig4_anova_dos_vias_y_supuestos_residuos.png"), width="stretch")
        st.image(str(FIGURAS_E2_DIR / "fig5_fraccionado_2_4_y_confirmacion_optimo.png"), width="stretch")

# ===========================================================================
# PESTAÑA 6 · CALIDAD, ÉTICA Y CUARENTENA
# ===========================================================================
with tab_calidad:
    titulo_vista(
        "CONFIANZA CERTIFICADA · ÉTICA, ISO 25010–25012 Y CUARENTENA",
        "Calidad del sistema, ética legal y puerta de datos",
        "Auditoría de licencias y privacidad (0 PII), calificaciones medidas bajo normas ISO y registro transparente de los 101 datos retenidos en cuarentena.",
        pill(f"ISO {res_iso['iso_25010_promedio_100']:.1f} / {res_iso['iso_25012_promedio_100']:.1f}", "petrol"),
    )

    # 1. Ética de las 3 fuentes
    e1c, e2c, e3c = st.columns(3)
    fuentes_eticas = [
        (e1c, "Open-Meteo (ERA5-Land)", "CC BY 4.0", "4 llamadas/día (< 0.04% de cuota)",
         "Rejilla satelital ~9 km suaviza microclimas.", "Índice ponderado SIAP y reglas RN-01/RN-03."),
        (e2c, "SNIIM · Economía", "Datos Abiertos MX", "1 consulta GET diaria respetuosa",
         "Precio mayorista en bodega, no en huerta.", "Cálculo de margen y choques preservados."),
        (e3c, "OpenStreetMap + INEGI", "ODbL 1.0", "Batch por entrega con caché local",
         "Cobertura VGI desigual entre municipios.", "Triangulación SIAP y polígono continental."),
    ]
    for col, titulo, lic, uso, sesgo, mitig in fuentes_eticas:
        col.markdown(
            f'<div class="cd-card"><div class="cd-kicker">Fuente legalmente auditada</div>'
            f'<h4 style="margin:4px 0 8px 0;font-size:1.08rem;color:{PETROL};">{titulo}</h4>'
            f'{pill(lic, "agua")}{pill("0 PII", "terracota")}{pill("robots.txt ✓", "neutro")}'
            f'<p style="font-size:.83rem;color:{TEXTO};margin:10px 0 4px 0;"><b>Uso:</b> {uso}</p>'
            f'<p style="font-size:.83rem;color:{TEXTO_SUAVE};margin:4px 0;"><b>Sesgo:</b> {sesgo}</p>'
            f'<p style="font-size:.83rem;color:{TEXTO_SUAVE};margin:4px 0 0 0;"><b>Mitigación:</b> {mitig}</p></div>',
            unsafe_allow_html=True,
        )
    st.write("")

    # 2. ISO/IEC 25010 y 25012
    i1, i2 = st.columns(2)
    with i1:
        df10 = iso_25010.copy()
        df10["nombre"] = df10["caracteristica"].str.replace(r"^\d+\.\s*", "", regex=True)
        barras10 = alt.Chart(df10).mark_bar(cornerRadiusEnd=6).encode(
            y=alt.Y("nombre:N", sort="-x", title=None),
            x=alt.X("puntaje_100:Q", title="Puntaje (0–100)", scale=alt.Scale(domain=[0, 106])),
            color=alt.Color("puntaje_100:Q", scale=alt.Scale(domain=[88, 100], range=[BRISA, PETROL]), legend=None),
            tooltip=[alt.Tooltip("nombre:N", title="Característica"), alt.Tooltip("puntaje_100:Q", title="Puntaje"), alt.Tooltip("valor_medido:N", title="Evidencia")],
        )
        texto10 = barras10.mark_text(align="left", dx=5, fontWeight="bold", color=PETROL).encode(text="puntaje_100:Q", color=alt.value(PETROL))
        meta = alt.Chart(pd.DataFrame({"m": [90]})).mark_rule(color=TERRACOTA, strokeDash=[5, 4], strokeWidth=2).encode(x="m:Q")
        st.altair_chart(estilo_altair((barras10 + texto10 + meta).properties(height=310, title=f"ISO/IEC 25010 · Producto ({res_iso['iso_25010_promedio_100']}/100)")), width="stretch")
    with i2:
        df12 = iso_25012.copy()
        barras12 = alt.Chart(df12).mark_bar(cornerRadiusEnd=6).encode(
            y=alt.Y("caracteristica:N", sort="-x", title=None),
            x=alt.X("valor_pct:Q", title="Puntaje (0–100)", scale=alt.Scale(domain=[0, 106])),
            color=alt.Color("punto_vista:N", scale=alt.Scale(range=[PETROL, TERRACOTA, "#5FA8B5"]), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("caracteristica:N", title="Característica"), alt.Tooltip("punto_vista:N", title="Enfoque"), alt.Tooltip("valor_pct:Q", title="Puntaje")],
        )
        texto12 = barras12.mark_text(align="left", dx=5, fontWeight="bold", color=PETROL).encode(text="valor_pct:Q", color=alt.value(PETROL))
        st.altair_chart(estilo_altair((barras12 + texto12).properties(height=310, title=f"ISO/IEC 25012 · Datos Oro ({res_iso['iso_25012_promedio_100']}/100)")), width="stretch")

    # 3. Puerta de Calidad y Cuarentena (Cero borrado silencioso)
    st.markdown("##### Puerta de calidad automática y cuarentena (cero borrado silencioso)")
    q1, q2 = st.columns(2)
    with q1:
        html(
            f"""
            <div class="cd-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="cd-kicker">Puerta tabular (E1) · Clima + Precios</div>
                {pill(f"{100 * ap_tab / ev_tab:.2f}% aprobados", "agua")}
              </div>
              <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.35rem;font-weight:800;color:{PETROL};margin-top:4px;" class="num">
                {ap_tab:,} válidos · {len(cuarentena)} en cuarentena
              </div>
              <div class="cd-bar-track"><div class="cd-bar-fill" style="width:{100 * ap_tab / ev_tab:.2f}%;background:{PETROL};"></div></div>
            </div>
            """
        )
    with q2:
        html(
            f"""
            <div class="cd-card">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <div class="cd-kicker">Puerta geoespacial (E2) · OpenStreetMap</div>
                {pill(f"{100 * ap_geo / ev_geo:.2f}% en Colima", "terracota")}
              </div>
              <div style="font-family:'Plus Jakarta Sans',sans-serif;font-size:1.35rem;font-weight:800;color:{PETROL};margin-top:4px;" class="num">
                {ap_geo:,} válidos · {len(cuarentena_geo)} fuera de estado
              </div>
              <div class="cd-bar-track"><div class="cd-bar-fill" style="width:{100 * ap_geo / ev_geo:.2f}%;background:{TERRACOTA};"></div></div>
            </div>
            """
        )
    st.write("")

    r1, r2 = st.columns([1, 1.15])
    with r1:
        reglas = cuarentena["regla_violada"].str.split("; ").explode().value_counts().rename_axis("regla").reset_index(name="registros")
        reglas["puerta"] = "Tabular (E1)"
        reglas_geo = cuarentena_geo["regla_violada"].value_counts().rename_axis("regla").reset_index(name="registros")
        reglas_geo["puerta"] = "Geoespacial (E2)"
        todas = pd.concat([reglas, reglas_geo], ignore_index=True)
        graf_reglas = alt.Chart(todas, title="Reglas que apartaron registros").mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("regla:N", sort="-x", title=None),
            x=alt.X("registros:Q", title="Registros detenidos", scale=alt.Scale(type="symlog")),
            color=alt.Color("puerta:N", scale=alt.Scale(domain=["Tabular (E1)", "Geoespacial (E2)"], range=[PETROL, CACAO]), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("regla:N", title="Regla"), alt.Tooltip("registros:Q", title="Registros"), alt.Tooltip("puerta:N", title="Puerta")],
        )
        txt_r = graf_reglas.mark_text(align="left", dx=5, fontWeight="bold", color=PETROL).encode(text="registros:Q", color=alt.value(PETROL))
        st.altair_chart(estilo_altair((graf_reglas + txt_r).properties(height=330)), width="stretch")
    with r2:
        q_geo = cuarentena_geo.copy()
        q_geo["nombre"] = q_geo["llave_primaria"]
        q_geo["categoria"] = q_geo["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, (c,))[0])
        q_geo["municipio"] = "Fuera de Colima (Jalisco / Michoacán)"
        capa_q = pdk.Layer(
            "ScatterplotLayer", data=q_geo[["longitud", "latitud", "nombre", "categoria", "municipio"]],
            get_position="[longitud, latitud]", get_fill_color=[90, 47, 37, 230], get_line_color=[255, 255, 255],
            get_radius=500, radius_min_pixels=4, stroked=True, pickable=True,
        )
        capa_mun_q = pdk.Layer(
            "GeoJsonLayer", data=cargar_geojson_municipios(), stroked=True, filled=True,
            get_fill_color="properties.fill", get_line_color="properties.line", line_width_min_pixels=1, pickable=False,
        )
        st.pydeck_chart(
            pdk.Deck(
                layers=[capa_mun_q, capa_q],
                initial_view_state=pdk.ViewState(latitude=19.1, longitude=-104.05, zoom=7.9),
                map_provider="carto", map_style="light",
                tooltip={"html": "<b>{nombre}</b><br/>{categoria}<br/><i>{municipio}</i>",
                         "style": {"backgroundColor": CACAO, "color": BLANCO, "fontSize": "12px", "borderRadius": "8px"}},
            ),
            height=340,
        )
        st.caption("Puntos en tierra cacao: 90 nodos fuera de los límites oficiales de Colima apartados a cuarentena.")

    with st.expander(f"Ver registros en cuarentena tabular ({len(cuarentena)}) y geoespacial ({len(cuarentena_geo)})"):
        st.dataframe(cuarentena, hide_index=True, width="stretch", column_config={"motivo_rechazo": st.column_config.TextColumn("Motivo", width="large")})
        st.dataframe(cuarentena_geo, hide_index=True, width="stretch", height=300)
    with st.expander("Ver tablas detalladas de evaluación ISO/IEC 25010 y 25012"):
        st.dataframe(iso_25010, hide_index=True, width="stretch")
        st.dataframe(iso_25012, hide_index=True, width="stretch")

# ---------------------------------------------------------------------------
# Pie de página
# ---------------------------------------------------------------------------
html(
    f"""
    <div class="cd-footer">
      <div><b>CITRO-DATA LAB COLIMA</b> · Proyecto Integrador Trusted Data Lab · TecNM — Instituto Tecnológico de Colima</div>
      <div>Open-Meteo (CC BY 4.0) · SNIIM-SE (Datos Abiertos MX) · OpenStreetMap (ODbL 1.0) · <a href="{REPO_URL}" target="_blank">GitHub ↗</a></div>
    </div>
    """
)
