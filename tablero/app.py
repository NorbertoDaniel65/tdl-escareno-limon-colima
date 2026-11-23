"""
Tablero Interactivo del Observatorio CITRO-DATA LAB COLIMA (E1 + E2) — Versión visual.
Observatorio Agroclimático, Geoespacial y de Precios Mayoristas del Limón Mexicano.
Autor: Norberto Daniel Escareño Montaño (23460323)

Lee exclusivamente los artefactos ya generados por el pipeline (Capas Plata, Oro y Cuarentena)
y los presenta con mapas (PyDeck) y gráficas interactivas (Altair) incluidos en Streamlit,
sin consultar APIs externas en cada interacción (regla ética del proyecto).
"""

from __future__ import annotations

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
REPO_URL = "https://github.com/NorbertoDaniel65/tdl-escareno-limon-colima"

st.set_page_config(
    page_title="CITRO-DATA LAB COLIMA · Observatorio E2",
    page_icon="🍋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Paleta y catálogos visuales
# ---------------------------------------------------------------------------
VERDE = "#15803d"
VERDE_OSC = "#14532d"
LIMA = "#65a30d"
AMARILLO = "#eab308"
NARANJA = "#d97706"
ROJO = "#dc2626"
AZUL = "#0284c7"
MORADO = "#7c3aed"
GRIS = "#64748b"
TINTA = "#0f172a"

CATEGORIAS = {
    "Zona_Huerta_Citricola": ("Huertas citrícolas", "#16a34a", [22, 163, 74]),
    "Infraestructura_Empaque_Bodega": ("Empaque / Bodega", "#d97706", [217, 119, 6]),
    "Mercado_Abasto": ("Mercado de abasto", "#dc2626", [220, 38, 38]),
    "Comercio_Fruticola_Mayorista": ("Comercio frutícola", "#7c3aed", [124, 58, 237]),
}
MESES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
         7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
NUCLEO = ["Tecomán", "Armería", "Manzanillo", "Colima"]


def html(contenido: str) -> None:
    """Renderiza un bloque HTML (sin líneas en blanco internas) dentro de Streamlit."""
    st.markdown(dedent(contenido).strip(), unsafe_allow_html=True)


def seccion(icono: str, titulo: str, subtitulo: str) -> None:
    html(
        f"""
        <div class="sec-head">
          <div class="sec-ic">{icono}</div>
          <div><div class="sec-title">{titulo}</div><div class="sec-sub">{subtitulo}</div></div>
        </div>
        """
    )


def tarjeta_kpi(icono: str, etiqueta: str, valor: str, detalle: str, color: str) -> str:
    return (
        f'<div class="kpi" style="--c:{color}"><div class="ic">{icono}</div>'
        f'<div class="lb">{etiqueta}</div><div class="vl">{valor}</div>'
        f'<div class="sb">{detalle}</div></div>'
    )


def mini(valor: str, etiqueta: str, color: str = VERDE) -> str:
    return (
        f'<div class="mini" style="--c:{color}"><div class="mv">{valor}</div>'
        f'<div class="ml">{etiqueta}</div></div>'
    )


def chip(texto: str, color: str = VERDE, fondo: str = "#dcfce7") -> str:
    return f'<span class="chip" style="color:{color};background:{fondo};border-color:{color}33">{texto}</span>'


# ---------------------------------------------------------------------------
# Estilos (CSS)
# ---------------------------------------------------------------------------
html(
    """
    <style>
    .block-container {padding-top: 3.1rem; padding-bottom: 2.5rem; max-width: 1420px;}
    .hero {background: linear-gradient(120deg, #14532d 0%, #15803d 42%, #65a30d 78%, #ca8a04 120%);
      border-radius: 20px; padding: 24px 28px; color: #fff;
      box-shadow: 0 12px 32px rgba(21,128,61,.26); margin-bottom: 18px;}
    .hero-top {display: flex; justify-content: space-between; align-items: center; gap: 20px;}
    .hero-copy {flex: 1; min-width: 0;}
    .hero .h-title {font-size: 1.9rem; font-weight: 800; line-height: 1.15; margin: 0 0 8px 0; color:#fff;}
    .hero .h-sub {font-size: .98rem; line-height: 1.45; color: #ecfccb;}
    .hero .h-lemon {font-size: 4.5rem; line-height: 1; flex-shrink: 0;
      filter: drop-shadow(0 6px 12px rgba(0,0,0,.22));}
    .hero .h-chips {margin-top: 14px;}
    .hero .chip {background: rgba(255,255,255,.16) !important; color: #fff !important; border-color: rgba(255,255,255,.42) !important;}
    .chip {display: inline-block; padding: 3px 11px; border-radius: 999px; font-size: .76rem; font-weight: 700;
      margin: 3px 6px 3px 0; border: 1px solid;}
    .kpi-grid {display: grid; grid-template-columns: repeat(auto-fit, minmax(175px, 1fr)); gap: 12px; margin-bottom: 14px;}
    .kpi {background: #fff; border: 1px solid #e2e8f0; border-top: 5px solid var(--c); border-radius: 15px;
      padding: 13px 15px; box-shadow: 0 4px 14px rgba(15,23,42,.06); transition: transform .15s; min-width: 0;}
    .kpi:hover {transform: translateY(-3px); box-shadow: 0 10px 22px rgba(15,23,42,.10);}
    .kpi .ic {font-size: 1.35rem; line-height: 1.2;}
    .kpi .lb {color: #475569; font-size: .72rem; font-weight: 800; text-transform: uppercase; letter-spacing: .35px;
      margin-top: 4px; word-break: normal; overflow-wrap: break-word;}
    .kpi .vl {color: #0f172a; font-size: 1.55rem; font-weight: 800; margin: 3px 0 3px 0; line-height: 1.15;}
    .kpi .sb {color: var(--c); font-size: .79rem; font-weight: 700; line-height: 1.3; word-break: normal;}
    .mini {background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%); border: 1px solid #e2e8f0;
      border-left: 5px solid var(--c); border-radius: 12px; padding: 10px 14px;}
    .mini .mv {font-size: 1.35rem; font-weight: 800; color: var(--c);}
    .mini .ml {font-size: .78rem; color: #475569; font-weight: 600;}
    .sec-head {display: flex; gap: 14px; align-items: center; margin: 6px 0 12px 0;}
    .sec-ic {font-size: 1.7rem; background: #dcfce7; border-radius: 12px; width: 50px; height: 50px;
      display: flex; align-items: center; justify-content: center;}
    .sec-title {font-size: 1.32rem; font-weight: 800; color: #0f172a;}
    .sec-sub {font-size: .88rem; color: #64748b;}
    .card {background: #fff; border: 1px solid #e2e8f0; border-radius: 14px; padding: 14px 16px;
      box-shadow: 0 3px 12px rgba(15,23,42,.05); height: 100%;}
    .card h4 {margin: 0 0 6px 0; font-size: 1.02rem; color: #0f172a;}
    .card p, .card li {font-size: .86rem; color: #334155; margin: 3px 0;}
    .card-accent {border-left: 6px solid var(--c);}
    .flow {display: flex; align-items: stretch; gap: 8px; margin: 6px 0 14px 0; flex-wrap: wrap;}
    .flow .step {flex: 1; min-width: 170px; border-radius: 14px; padding: 12px 14px; border: 1px solid var(--c);
      background: var(--bg);}
    .flow .step .t {font-weight: 800; color: var(--c); font-size: .95rem;}
    .flow .step .n {font-size: 1.35rem; font-weight: 800; color: #0f172a;}
    .flow .step .d {font-size: .78rem; color: #475569;}
    .flow .arr {display: flex; align-items: center; font-size: 1.6rem; color: #94a3b8;}
    .trace {background: #f0fdf4; border: 1px solid #86efac; border-radius: 14px; padding: 14px 18px;}
    .trace .tid {font-family: Consolas, monospace; font-size: 1.15rem; font-weight: 800; color: #14532d;}
    .trace .row {display: flex; gap: 10px; margin: 6px 0; font-size: .86rem;}
    .trace .k {min-width: 150px; color: #475569; font-weight: 700;}
    .trace .v {color: #0f172a; font-family: Consolas, monospace; word-break: break-all;}
    .mes {border-radius: 14px; padding: 10px 8px; text-align: center; color: #fff; margin-bottom: 8px;
      box-shadow: 0 4px 12px rgba(15,23,42,.10);}
    .mes .mn {font-weight: 800; font-size: .95rem; opacity: .95;}
    .mes .mp {font-weight: 800; font-size: 1.35rem;}
    .mes .mi {font-size: .70rem; opacity: .92;}
    .mes .mt {font-size: .72rem; font-weight: 700; margin-top: 2px;}
    .legend {display: flex; flex-wrap: wrap; gap: 14px; font-size: .80rem; color: #334155; margin: 6px 0 4px 2px;}
    .legend .dot {display: inline-block; width: 11px; height: 11px; border-radius: 50%; margin-right: 5px; vertical-align: -1px;}
    .badge-ok {background: #dcfce7; color: #14532d; border: 1px solid #86efac; border-radius: 12px; padding: 10px 12px; text-align: center;}
    .badge-ok .bt {font-size: .74rem; font-weight: 800; text-transform: uppercase; color: #15803d;}
    .badge-ok .bv {font-size: 1.15rem; font-weight: 800; color: #0f172a;}
    .badge-ok .bd {font-size: .76rem; color: #334155;}
    .side-brand {display: flex; gap: 10px; align-items: center; margin-bottom: 6px;}
    .side-brand span {color: #64748b; font-size: .82rem;}
    .stage {display: flex; justify-content: space-between; font-size: .84rem; padding: 4px 0; border-bottom: 1px dashed #e2e8f0;}
    .footer {margin-top: 26px; padding: 14px 18px; border-radius: 14px; background: #f8fafc; border: 1px solid #e2e8f0;
      font-size: .80rem; color: #475569; text-align: center;}
    .stTabs [data-baseweb="tab-list"] {gap: 6px; flex-wrap: wrap;}
    .stTabs [data-baseweb="tab"] {background: #f1f5f9; border-radius: 10px 10px 0 0; padding: 8px 14px; font-weight: 700;}
    .stTabs [aria-selected="true"] {background: #dcfce7 !important; color: #14532d !important;}
    </style>
    """
)


# ---------------------------------------------------------------------------
# Carga de artefactos del pipeline (con caché)
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
            p["fill"] = [21, 128, 61, int(55 + 260 * w)]
            p["line"] = [20, 83, 45, 230]
        else:
            p["fill"] = [148, 163, 184, 45]
            p["line"] = [100, 116, 139, 160]
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

# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    html(
        """
        <div class="side-brand"><div style="font-size:2.7rem">🍋</div>
        <div><b style="font-size:1.08rem">CITRO-DATA LAB</b><br><span>Colima · Trusted Data Lab</span></div></div>
        """
    )
    st.markdown(
        "**Alumno:** Norberto Daniel Escareño Montaño  \n"
        "**No. Control:** 23460323  \n"
        "**Institución:** TecNM · Instituto Tecnológico de Colima"
    )
    st.markdown("##### 🚦 Avance del proyecto")
    etapas = [
        ("E0 · Arranque y captura Bronce", "✅"),
        ("E1 · Plata, Puerta y Pronóstico", "✅"),
        ("E2 · Geoespacial, Ética y Linaje", "✅"),
        ("E3 · Capa Oro optimizada", "⏳"),
        ("E4 · Demo Day", "⏳"),
    ]
    html("".join(f'<div class="stage"><span>{e}</span><span>{s}</span></div>' for e, s in etapas))
    st.markdown("##### 📡 Fuentes de datos")
    html(
        chip("Open-Meteo · CC BY 4.0", AZUL, "#e0f2fe")
        + chip("SNIIM · Datos Abiertos MX", NARANJA, "#ffedd5")
        + chip("OpenStreetMap · ODbL 1.0", VERDE, "#dcfce7")
        + chip("0 datos personales", MORADO, "#ede9fe")
    )
    st.markdown("##### 🧭 ¿Cómo leer el tablero?")
    st.caption(
        "1) Revisa los indicadores de la parte superior. 2) Explora el mapa y filtra por municipio. "
        "3) Audita el origen de cualquier dato en *Linaje*. 4) Consulta el *Pronóstico 2026* para "
        "decidir cuándo vender. Pasa el cursor sobre las gráficas para ver los valores exactos."
    )
    st.link_button("📂 Ver repositorio en GitHub", REPO_URL, width="stretch")

# ---------------------------------------------------------------------------
# Encabezado principal (hero) e indicadores
# ---------------------------------------------------------------------------
html(
    f"""
    <div class="hero">
      <div class="hero-top">
        <div class="hero-copy">
          <div class="h-title">CITRO-DATA LAB COLIMA</div>
          <div class="h-sub">Observatorio agroclimático, geoespacial y de precios mayoristas del limón mexicano #5.
          Datos abiertos, limpios y 100% trazables para decidir <b>cuándo y dónde vender</b> en Tecomán, Armería, Manzanillo y Colima.</div>
        </div>
        <div class="h-lemon">🍋</div>
      </div>
      <div class="h-chips">{chip("Entregas E1 + E2")}{chip("Bronce → Plata → Oro")}{chip("Geoespacial OSM / INEGI")}{chip("Experimento 2³ · ANOVA")}{chip("ISO/IEC 25010 · 25012")}</div>
    </div>
    <div class="kpi-grid">
      {tarjeta_kpi("🗺️", "Geoespacial Colima", f"{res_geo['puntos_aprobados_dentro_colima_plata']:,} nodos",
                   f"{res_geo['puntos_enviados_cuarentena_fuera_colima']} en cuarentena · 0 PII", VERDE)}
      {tarjeta_kpi("🔗", "Linaje Capa Oro", f"{res_linaje['cobertura_trazabilidad_pct']:.0f}%",
                   f"{res_linaje['total_registros_oro_rastreados']} registros rastreables", AZUL)}
      {tarjeta_kpi("⚡", "Aceleración DOE", f"{conf['factor_aceleracion_speedup']}×",
                   f"-{conf['mejora_tiempo_pct']}% tiempo · -{conf['reduccion_disco_pct']}% disco", NARANJA)}
      {tarjeta_kpi("📈", "Precisión SARIMA", f"{100 - ganador['MAPE_test_pct']:.1f}%",
                   f"MAPE {ganador['MAPE_test_pct']:.2f}% · Ljung-Box ✓", MORADO)}
      {tarjeta_kpi("🏅", "ISO 25010 / 25012", f"{res_iso['iso_25010_promedio_100']:.0f} / {res_iso['iso_25012_promedio_100']:.0f}",
                   f"Disponibilidad {res_iso['fiabilidad_acumulada_e0_e2']['disponibilidad_real_pct']}%", LIMA)}
    </div>
    """
)

tab_geo, tab_linaje, tab_doe, tab_iso, tab_pron, tab_puerta = st.tabs(
    [
        "🗺️ Mapa Geoespacial Citrícola (E2)",
        "🔗 Linaje y Trazabilidad Bronce → Oro (E2)",
        "🧪 Experimento Factorial 2³ y ANOVA (E2)",
        "✅ Ética, ISO 25010 y 25012 (E2)",
        "📈 Pronóstico 2026 con IC 95% (E1)",
        "🛡️ Puerta de Calidad y Cuarentena (E1+E2)",
    ]
)

# ===========================================================================
# PESTAÑA 1 · MAPA GEOESPACIAL
# ===========================================================================
with tab_geo:
    seccion(
        "🗺️",
        "Fuente especializada geoespacial: OpenStreetMap × marco municipal de Colima",
        "Unión espacial GeoPandas <code>sjoin(predicate=\"within\")</code> en WGS84 (EPSG:4326) · distancias métricas en UTM 13N (EPSG:32613) · Licencia ODbL 1.0",
    )
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(mini(f"{res_geo['poligonos_municipales_colima']}", "Municipios de Colima (4 núcleo citrícola)", VERDE), unsafe_allow_html=True)
    m2.markdown(mini(f"{res_geo['puntos_bronce_evaluados']:,}", "Nodos capturados en OpenStreetMap", AZUL), unsafe_allow_html=True)
    m3.markdown(mini(f"{res_geo['puntos_aprobados_dentro_colima_plata']:,}", "Nodos validados dentro de Colima", LIMA), unsafe_allow_html=True)
    m4.markdown(mini(f"{res_geo['puntos_enviados_cuarentena_fuera_colima']}", "Fuera del estado → cuarentena", ROJO), unsafe_allow_html=True)
    st.write("")

    f1, f2 = st.columns([1.2, 1])
    cats_disp = sorted(pts_geo_plata["categoria_agrologistica"].unique())
    muns_disp = sorted(pts_geo_plata["nombre_oficial"].unique())
    with f1:
        cats_sel = st.multiselect(
            "🧩 Tipo de infraestructura", cats_disp, default=cats_disp,
            format_func=lambda c: CATEGORIAS.get(c, (c,))[0],
        )
    with f2:
        muns_sel = st.multiselect("📍 Municipios", muns_disp, default=[m for m in NUCLEO if m in muns_disp])

    sub_pts = pts_geo_plata[
        pts_geo_plata["categoria_agrologistica"].isin(cats_sel) & pts_geo_plata["nombre_oficial"].isin(muns_sel)
    ].copy()
    sub_pts["nombre"] = sub_pts["nombre_publico_lugar"].fillna("Sin denominación pública")
    sub_pts["categoria"] = sub_pts["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, (c,))[0])
    sub_pts["municipio"] = sub_pts["nombre_oficial"]
    sub_pts["color"] = sub_pts["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, ("", "", [100, 116, 139]))[2])

    c_map, c_side = st.columns([1.75, 1])
    with c_map:
        capa_municipios = pdk.Layer(
            "GeoJsonLayer",
            data=cargar_geojson_municipios(),
            stroked=True,
            filled=True,
            get_fill_color="properties.fill",
            get_line_color="properties.line",
            line_width_min_pixels=1.5,
            pickable=False,
        )
        capa_nodos = pdk.Layer(
            "ScatterplotLayer",
            data=sub_pts[["longitud", "latitud", "nombre", "categoria", "municipio", "color"]],
            get_position="[longitud, latitud]",
            get_fill_color="color",
            get_line_color=[255, 255, 255],
            get_radius=330,
            radius_min_pixels=3,
            radius_max_pixels=11,
            stroked=True,
            line_width_min_pixels=0.6,
            opacity=0.88,
            pickable=True,
        )
        nodos_logisticos = pd.DataFrame(
            [
                {"longitud": -104.2940, "latitud": 19.0550, "nombre": "⚓ Puerto de Manzanillo",
                 "categoria": "Nodo de exportación", "municipio": "Manzanillo"},
                {"longitud": -103.6860, "latitud": 19.2770, "nombre": "🛣️ Salida Autopista 54D → Guadalajara",
                 "categoria": "Corredor carretero", "municipio": "Colima"},
            ]
        )
        capa_logistica = pdk.Layer(
            "ScatterplotLayer",
            data=nodos_logisticos,
            get_position="[longitud, latitud]",
            get_fill_color=[2, 132, 199],
            get_line_color=[15, 23, 42],
            get_radius=1600,
            radius_min_pixels=8,
            stroked=True,
            line_width_min_pixels=2,
            pickable=True,
        )
        deck = pdk.Deck(
            layers=[capa_municipios, capa_nodos, capa_logistica],
            initial_view_state=pdk.ViewState(latitude=19.08, longitude=-104.02, zoom=8.25, pitch=0),
            map_provider="carto",
            map_style="light",
            tooltip={
                "html": "<b>{nombre}</b><br/>{categoria}<br/><i>📍 {municipio}</i>",
                "style": {"backgroundColor": VERDE_OSC, "color": "white", "fontSize": "12px", "borderRadius": "8px"},
            },
        )
        st.pydeck_chart(deck, height=520)
        leyenda = "".join(
            f'<span><span class="dot" style="background:{v[1]}"></span>{v[0]}</span>' for v in CATEGORIAS.values()
        )
        html(
            f'<div class="legend">{leyenda}<span><span class="dot" style="background:{AZUL};border:2px solid {TINTA}"></span>Nodo logístico</span>'
            f'<span><span class="dot" style="background:#15803d;opacity:.6;border-radius:3px"></span>Municipio núcleo (más intenso = mayor % SIAP)</span></div>'
        )
        st.caption(f"Mostrando **{len(sub_pts):,}** nodos validados. Acerca/aleja con la rueda del ratón y pasa el cursor sobre un punto para ver su detalle.")

    with c_side:
        conteo = (
            pts_geo_plata[pts_geo_plata["categoria_agrologistica"].isin(cats_sel)]
            .assign(categoria=lambda d: d["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, (c,))[0]))
            .groupby(["nombre_oficial", "categoria"], as_index=False)
            .size()
            .rename(columns={"size": "nodos"})
        )
        conteo["seleccionado"] = conteo["nombre_oficial"].isin(muns_sel)
        dom_cat = [v[0] for v in CATEGORIAS.values()]
        rng_cat = [v[1] for v in CATEGORIAS.values()]
        graf_mun = (
            alt.Chart(conteo, title="Nodos por municipio (sjoin within)")
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                y=alt.Y("nombre_oficial:N", sort="-x", title=None),
                x=alt.X("sum(nodos):Q", title="Número de nodos"),
                color=alt.Color("categoria:N", scale=alt.Scale(domain=dom_cat, range=rng_cat), legend=alt.Legend(title=None, orient="bottom", columns=2)),
                opacity=alt.condition(alt.datum.seleccionado, alt.value(1.0), alt.value(0.30)),
                tooltip=[alt.Tooltip("nombre_oficial:N", title="Municipio"), alt.Tooltip("categoria:N", title="Tipo"), alt.Tooltip("nodos:Q", title="Nodos")],
            )
            .properties(height=300)
        )
        st.altair_chart(graf_mun, width="stretch")

        dist = perfil_geo[["nombre_oficial", "dist_puerto_manzanillo_km", "en_observatorio_citricola"]].copy()
        graf_dist = (
            alt.Chart(dist, title="Distancia al Puerto de Manzanillo (km)")
            .mark_bar(cornerRadiusEnd=4)
            .encode(
                y=alt.Y("nombre_oficial:N", sort="x", title=None),
                x=alt.X("dist_puerto_manzanillo_km:Q", title="km (EPSG:32613)"),
                color=alt.condition(alt.datum.en_observatorio_citricola, alt.value(AZUL), alt.value("#cbd5e1")),
                tooltip=[alt.Tooltip("nombre_oficial:N", title="Municipio"), alt.Tooltip("dist_puerto_manzanillo_km:Q", title="Distancia (km)", format=".1f")],
            )
            .properties(height=230)
        )
        st.altair_chart(graf_dist, width="stretch")

    st.markdown("##### 📋 Perfil geoespacial integrado en Capa Oro")
    tabla_geo = perfil_geo[
        ["cvegeo", "nombre_oficial", "en_observatorio_citricola", "peso_siap_limon", "superficie_km2",
         "n_huertas_citricolas_osm", "n_empaque_bodega_osm", "n_mercados_abasto_osm", "n_nodos_agrologisticos_total",
         "densidad_agrologistica_100km2", "dist_puerto_manzanillo_km", "dist_corredor_gdl_54d_km"]
    ].copy()
    tabla_geo["peso_siap_limon"] = tabla_geo["peso_siap_limon"] * 100
    st.dataframe(
        tabla_geo,
        hide_index=True,
        width="stretch",
        column_config={
            "cvegeo": st.column_config.TextColumn("CVEGEO"),
            "nombre_oficial": st.column_config.TextColumn("Municipio"),
            "en_observatorio_citricola": st.column_config.CheckboxColumn("Núcleo citrícola"),
            "peso_siap_limon": st.column_config.ProgressColumn("Peso SIAP limón", format="%.0f%%", min_value=0, max_value=100),
            "superficie_km2": st.column_config.NumberColumn("Superficie (km²)", format="%.1f"),
            "n_huertas_citricolas_osm": st.column_config.NumberColumn("Huertas"),
            "n_empaque_bodega_osm": st.column_config.NumberColumn("Empaque / Bodega"),
            "n_mercados_abasto_osm": st.column_config.NumberColumn("Mercados"),
            "n_nodos_agrologisticos_total": st.column_config.ProgressColumn("Nodos totales", format="%d", min_value=0, max_value=int(tabla_geo["n_nodos_agrologisticos_total"].max())),
            "densidad_agrologistica_100km2": st.column_config.NumberColumn("Densidad /100 km²", format="%.1f"),
            "dist_puerto_manzanillo_km": st.column_config.NumberColumn("Dist. puerto (km)", format="%.1f"),
            "dist_corredor_gdl_54d_km": st.column_config.NumberColumn("Dist. Autopista 54D (km)", format="%.1f"),
        },
    )
    with st.expander("🖼️ Ver figura estática del reporte (mapa GeoPandas + distribución municipal)"):
        st.image(str(FIGURAS_E2_DIR / "fig1_mapa_geoespacial_colima_e2.png"), width="stretch")

# ===========================================================================
# PESTAÑA 2 · LINAJE Y TRAZABILIDAD
# ===========================================================================
with tab_linaje:
    seccion(
        "🔗",
        "Linaje y trazabilidad registro a registro",
        "Cada dato de la Capa Oro conserva su archivo de origen en Bronce, su huella SHA-256 y la fecha exacta de descarga (UTC)",
    )
    clima_r = rep_puerta["resumen_clima_diario"]
    sniim_r = rep_puerta["resumen_sniim_mensual"]
    html(
        f"""
        <div class="flow">
          <div class="step" style="--c:#b45309;--bg:#fffbeb"><div class="t">🥉 Capa Bronce</div>
            <div class="n">{clima_r['registros_evaluados_bronce'] + sniim_r['registros_evaluados_bronce'] + res_geo['puntos_bronce_evaluados']:,}</div>
            <div class="d">Datos crudos de Open-Meteo, SNIIM y OpenStreetMap con .meta.json (SHA-256)</div></div>
          <div class="arr">➜</div>
          <div class="step" style="--c:#0369a1;--bg:#f0f9ff"><div class="t">🛡️ Puerta de Calidad</div>
            <div class="n">{len(cuarentena) + len(cuarentena_geo)} retenidos</div>
            <div class="d">Pandera + reglas RN-01..04 + filtro espacial; nada se borra en silencio</div></div>
          <div class="arr">➜</div>
          <div class="step" style="--c:#334155;--bg:#f8fafc"><div class="t">🥈 Capa Plata</div>
            <div class="n">{clima_r['registros_aprobados_plata'] + sniim_r['registros_aprobados_plata'] + res_geo['puntos_aprobados_dentro_colima_plata']:,}</div>
            <div class="d">Datos limpios, imputados, escalados y asignados a su municipio</div></div>
          <div class="arr">➜</div>
          <div class="step" style="--c:#15803d;--bg:#f0fdf4"><div class="t">🥇 Capa Oro</div>
            <div class="n">{res_linaje['total_registros_oro_rastreados']} · {res_linaje['cobertura_trazabilidad_pct']:.0f}%</div>
            <div class="d">Registros maestros integrados con 6 columnas de linaje cada uno</div></div>
        </div>
        """
    )

    c_sel, c_don = st.columns([1.7, 1])
    with c_sel:
        ids = catalogo_linaje["linaje_id_registro"].tolist()
        idx_def = ids.index("ORO-SERIE-2022-02") if "ORO-SERIE-2022-02" in ids else 0
        id_sel = st.selectbox("🔎 Elige un registro de la Capa Oro para auditar su origen:", ids, index=idx_def)
        fila_lin = catalogo_linaje[catalogo_linaje["linaje_id_registro"] == id_sel].iloc[0].to_dict()
        fuentes_chips = "".join(chip(f, AZUL, "#e0f2fe") for f in str(fila_lin["linaje_fuentes_bronce"]).split("+"))
        archivos = "<br>".join(f"📄 {a}" for a in str(fila_lin["linaje_archivos_bronce"]).split("|"))
        fechas = "<br>".join(f"🕒 {f}" for f in str(fila_lin["linaje_fecha_ingesta_utc"]).split("|"))
        html(
            f"""
            <div class="trace">
              <div class="tid">🏷️ {fila_lin['linaje_id_registro']}</div>
              <div class="row"><div class="k">Tabla en Capa Oro</div><div class="v">{fila_lin['tabla_oro']}</div></div>
              <div class="row"><div class="k">Llave de negocio</div><div class="v">{fila_lin['llave_negocio']}</div></div>
              <div class="row"><div class="k">Fuentes de origen</div><div>{fuentes_chips}</div></div>
              <div class="row"><div class="k">Archivos en Bronce</div><div class="v">{archivos}</div></div>
              <div class="row"><div class="k">Huella SHA-256</div><div class="v">🔐 {fila_lin['linaje_sha256_bronce']}</div></div>
              <div class="row"><div class="k">Fecha de ingesta</div><div class="v">{fechas}</div></div>
              <div class="row"><div class="k">Versión del pipeline</div><div class="v">{fila_lin['linaje_version_pipeline']}</div></div>
            </div>
            """
        )
        with st.expander("Ver registro en formato JSON"):
            st.json(fila_lin)
    with c_don:
        comp_tablas = catalogo_linaje.groupby("tabla_oro", as_index=False).size().rename(columns={"size": "registros"})
        dona = (
            alt.Chart(comp_tablas, title="Registros rastreables por tabla Oro")
            .mark_arc(innerRadius=62, cornerRadius=4)
            .encode(
                theta="registros:Q",
                color=alt.Color("tabla_oro:N", scale=alt.Scale(range=[VERDE, AZUL, NARANJA]), legend=alt.Legend(title=None, orient="bottom", columns=1)),
                tooltip=[alt.Tooltip("tabla_oro:N", title="Tabla"), alt.Tooltip("registros:Q", title="Registros")],
            )
            .properties(height=300)
        )
        st.altair_chart(dona, width="stretch")
        st.markdown(mini("100%", "Cobertura de linaje verificada por pytest", VERDE), unsafe_allow_html=True)

    with st.expander(f"📚 Catálogo completo de trazabilidad ({len(catalogo_linaje)} registros)"):
        st.dataframe(catalogo_linaje, hide_index=True, width="stretch", height=380)
    with st.expander("🖼️ Ver diagrama estático de arquitectura de linaje"):
        st.image(str(FIGURAS_E2_DIR / "fig2_arquitectura_linaje_bronce_oro_e2.png"), width="stretch")

# ===========================================================================
# PESTAÑA 3 · EXPERIMENTO FACTORIAL
# ===========================================================================
with tab_doe:
    seccion(
        "🧪",
        "Experimento factorial real 2³, ANOVA de dos vías y diseño fraccionado 2⁴⁻¹",
        "84 corridas reales sobre copias locales del pipeline (0 peticiones a sitios externos) · aleatorizado, con réplicas y bloques",
    )
    d1, d2, d3, d4 = st.columns(4)
    d1.markdown(mini(f"{conf['observado_linea_base_media_ms']:.0f} ms", "Antes (CSV + validación iterativa)", ROJO), unsafe_allow_html=True)
    d2.markdown(mini(f"{conf['observado_optimo_media_ms']:.0f} ms", "Después (4 hilos + Pandera + Parquet)", VERDE), unsafe_allow_html=True)
    d3.markdown(mini(f"{conf['factor_aceleracion_speedup']}×", "Más rápido en la corrida de confirmación", NARANJA), unsafe_allow_html=True)
    d4.markdown(mini(f"-{conf['reduccion_disco_pct']}%", "Espacio en disco (1,937 → 172 KB)", AZUL), unsafe_allow_html=True)
    st.write("")

    g1, g2 = st.columns(2)
    with g1:
        rank = corridas_2_3.groupby("tratamiento", as_index=False)["tiempo_total_ms"].agg(["mean", "std"]).reset_index(drop=True)
        rank = corridas_2_3.groupby("tratamiento", as_index=False).agg(media=("tiempo_total_ms", "mean"), de=("tiempo_total_ms", "std"))
        rank["tipo"] = rank["tratamiento"].map(lambda t: "Óptimo" if t == "A+B+C+" else ("Línea base E1" if t == "A-B-C-" else "Otro tratamiento"))
        graf_rank = (
            alt.Chart(rank, title="Tiempo medio por tratamiento (n = 3 réplicas)")
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                y=alt.Y("tratamiento:N", sort="x", title=None),
                x=alt.X("media:Q", title="Tiempo medio (ms)"),
                color=alt.Color("tipo:N", scale=alt.Scale(domain=["Óptimo", "Línea base E1", "Otro tratamiento"], range=[VERDE, ROJO, "#93c5fd"]), legend=alt.Legend(title=None, orient="bottom")),
                tooltip=[alt.Tooltip("tratamiento:N", title="Tratamiento"), alt.Tooltip("media:Q", title="Media (ms)", format=".1f"), alt.Tooltip("de:Q", title="Desv. est. (ms)", format=".2f")],
            )
            .properties(height=320)
        )
        st.altair_chart(graf_rank, width="stretch")
        st.caption("A = paralelismo (− 1 hilo / + 4 hilos) · B = validación (− iterativa / + Pandera) · C = formato (− CSV / + Parquet)")
    with g2:
        t_crit = float(stats.t.ppf(0.975, df=14))
        ef = efectos_2_3.copy()
        ef["Resultado"] = ef["significativo_5pct"].map({True: "Significativo (α = 0.05)", False: "No significativo"})
        barras = (
            alt.Chart(ef, title="Diagrama de Pareto de efectos |t|")
            .mark_bar(cornerRadiusEnd=5)
            .encode(
                y=alt.Y("descripcion:N", sort="-x", title=None),
                x=alt.X("t_absoluto:Q", title="Efecto estandarizado |t|"),
                color=alt.Color("Resultado:N", scale=alt.Scale(domain=["Significativo (α = 0.05)", "No significativo"], range=[VERDE, "#cbd5e1"]), legend=alt.Legend(title=None, orient="bottom")),
                tooltip=[alt.Tooltip("descripcion:N", title="Efecto"), alt.Tooltip("efecto_estimado_ms:Q", title="Efecto (ms)", format="+.1f"),
                         alt.Tooltip("estadistico_t:Q", title="t", format=".2f"), alt.Tooltip("p_valor:Q", title="p", format=".4g")],
            )
        )
        regla = alt.Chart(pd.DataFrame({"t": [t_crit]})).mark_rule(color=ROJO, strokeDash=[6, 4], strokeWidth=2).encode(x="t:Q")
        st.altair_chart((barras + regla).properties(height=320), width="stretch")
        st.caption(f"Línea roja: umbral crítico |t| = {t_crit:.2f}. El formato Parquet (C) y Pandera (B) explican casi toda la mejora.")

    g3, g4 = st.columns(2)
    with g3:
        conf_df = confirmacion.copy()
        conf_df["escenario_corto"] = conf_df["escenario"].map(lambda e: "Línea base E1" if e.startswith("Linea_Base") else "Óptimo A+B+C+")
        pi_inf, pi_sup = conf["ic95_prediccion_ms"]
        banda = alt.Chart(pd.DataFrame({"escenario_corto": ["Óptimo A+B+C+"], "inf": [pi_inf], "sup": [pi_sup]})).mark_bar(
            color=AMARILLO, opacity=0.35, size=70).encode(x="escenario_corto:N", y="inf:Q", y2="sup:Q")
        medias = alt.Chart(conf_df).mark_bar(size=46, opacity=0.85, cornerRadiusTopLeft=6, cornerRadiusTopRight=6).encode(
            x=alt.X("escenario_corto:N", title=None, sort=["Línea base E1", "Óptimo A+B+C+"]),
            y=alt.Y("mean(tiempo_total_ms):Q", title="Tiempo (ms)"),
            color=alt.Color("escenario_corto:N", scale=alt.Scale(domain=["Línea base E1", "Óptimo A+B+C+"], range=[ROJO, VERDE]), legend=None),
            tooltip=[alt.Tooltip("escenario_corto:N", title="Escenario"), alt.Tooltip("mean(tiempo_total_ms):Q", title="Media (ms)", format=".1f")],
        )
        puntos = alt.Chart(conf_df).mark_circle(size=70, color=TINTA, opacity=0.8).encode(
            x=alt.X("escenario_corto:N", sort=["Línea base E1", "Óptimo A+B+C+"]),
            y="tiempo_total_ms:Q",
            tooltip=[alt.Tooltip("replica_confirmacion:Q", title="Réplica"), alt.Tooltip("tiempo_total_ms:Q", title="Tiempo (ms)", format=".1f")],
        )
        st.altair_chart(alt.layer(medias, banda, puntos).properties(height=300, title="Corrida de confirmación (n = 5 por escenario)"), width="stretch")
        st.caption(f"Franja amarilla: IC 95% predicho [{pi_inf:.1f}, {pi_sup:.1f}] ms. La media observada ({conf['observado_optimo_media_ms']:.1f} ms) cae dentro ✓")
    with g4:
        inter = corridas_2x3.groupby(["motor_validacion", "formato_persistencia"], as_index=False)["tiempo_total_ms"].mean()
        inter["Motor"] = inter["motor_validacion"].map({"iterativo": "Validación iterativa", "pandera_vectorizado": "Pandera vectorizado"})
        inter["Formato"] = inter["formato_persistencia"].map({"csv_utf8": "CSV UTF-8", "parquet_snappy": "Parquet Snappy", "parquet_zstd": "Parquet ZSTD"})
        graf_int = (
            alt.Chart(inter, title=f"ANOVA de dos vías 2×3 · p(interacción) = {res_doe['diseno_dos_vias_2x3']['p_valor_interaccion_BxC']:.3f}")
            .mark_line(point=alt.OverlayMarkDef(size=90, filled=True), strokeWidth=3)
            .encode(
                x=alt.X("Formato:N", sort=["CSV UTF-8", "Parquet Snappy", "Parquet ZSTD"], title=None),
                y=alt.Y("tiempo_total_ms:Q", title="Tiempo medio (ms)"),
                color=alt.Color("Motor:N", scale=alt.Scale(domain=["Validación iterativa", "Pandera vectorizado"], range=[ROJO, VERDE]), legend=alt.Legend(title=None, orient="bottom")),
                tooltip=["Motor:N", "Formato:N", alt.Tooltip("tiempo_total_ms:Q", title="Media (ms)", format=".1f")],
            )
            .properties(height=300)
        )
        st.altair_chart(graf_int, width="stretch")
        st.caption("Líneas paralelas = efectos aditivos: cada mejora suma por separado, sin interferir entre sí.")

    st.markdown("##### ✅ Puerta de Calidad 3 · Supuestos del ANOVA")
    b1, b2, b3, b4 = st.columns(4)
    b1.markdown(f'<div class="badge-ok"><div class="bt">Normalidad ✓</div><div class="bv">p = {sup["shapiro_wilk_p"]:.3f}</div><div class="bd">Shapiro-Wilk W = {sup["shapiro_wilk_W"]:.3f}</div></div>', unsafe_allow_html=True)
    b2.markdown(f'<div class="badge-ok"><div class="bt">Homocedasticidad ✓</div><div class="bv">p = {sup["levene_p"]:.3f}</div><div class="bd">Levene F = {sup["levene_F"]:.3f}</div></div>', unsafe_allow_html=True)
    b3.markdown(f'<div class="badge-ok"><div class="bt">Independencia ✓</div><div class="bv">DW = {sup["durbin_watson"]:.2f}</div><div class="bd">Durbin-Watson (ideal ≈ 2)</div></div>', unsafe_allow_html=True)
    b4.markdown(f'<div class="badge-ok"><div class="bt">Ajuste del modelo</div><div class="bv">R² = {sup["r2_modelo"]:.4f}</div><div class="bd">R² ajustado = {sup["r2_ajustado"]:.4f}</div></div>', unsafe_allow_html=True)
    st.write("")

    t1, t2 = st.columns(2)
    with t1:
        st.markdown("**Tabla ANOVA · Diseño factorial 2³**")
        st.dataframe(anova_2_3, hide_index=True, width="stretch")
    with t2:
        st.markdown("**Estructura de alias · 2⁴ completo vs. 2⁴⁻¹ (I = ABCD, Resolución IV, 50% menos corridas)**")
        st.dataframe(alias_2_4, hide_index=True, width="stretch")
    with st.expander("🖼️ Ver figuras estáticas del reporte (Pareto, supuestos, fraccionado y confirmación)"):
        st.image(str(FIGURAS_E2_DIR / "fig3_doe_factorial_2_3_efectos_pareto.png"), width="stretch")
        st.image(str(FIGURAS_E2_DIR / "fig4_anova_dos_vias_y_supuestos_residuos.png"), width="stretch")
        st.image(str(FIGURAS_E2_DIR / "fig5_fraccionado_2_4_y_confirmacion_optimo.png"), width="stretch")

# ===========================================================================
# PESTAÑA 4 · ÉTICA E ISO
# ===========================================================================
with tab_iso:
    seccion(
        "✅",
        "Ética de datos y evaluación normativa ISO/IEC 25010 · 25012",
        "Fuentes legales y abiertas, cero datos personales y calidad medida con métricas objetivas (docs/etica-datos.md)",
    )
    e1c, e2c, e3c = st.columns(3)
    fuentes_eticas = [
        (e1c, "🌦️ Open-Meteo (ERA5-Land)", AZUL, "CC BY 4.0", "4 consultas/día (&lt; 0.04% de la cuota)",
         "Rejilla de ~9 km suaviza microclimas", "Índice ponderado SIAP y reglas físicas RN-01/RN-03"),
        (e2c, "💲 SNIIM · Secretaría de Economía", NARANJA, "Libre Uso Datos Abiertos MX", "1 consulta diaria al portal público",
         "Precio de central de abasto, no de huerta", "Cálculo del margen y choques 2022/2024 conservados"),
        (e3c, "🗺️ OpenStreetMap + INEGI", VERDE, "ODbL 1.0", "1 descarga por entrega con caché local",
         "Mapeo voluntario desigual (Ixtlahuacán vs Tecomán)", "Triangulación con SIAP y polígono continental"),
    ]
    for col, titulo, color, lic, uso, sesgo, mitig in fuentes_eticas:
        col.markdown(
            f'<div class="card card-accent" style="--c:{color}"><h4>{titulo}</h4>'
            f'{chip(lic, color, "#ffffff")}{chip("0 datos personales", MORADO, "#ede9fe")}{chip("robots.txt archivado", GRIS, "#f1f5f9")}'
            f'<p><b>Uso responsable:</b> {uso}</p><p><b>Sesgo conocido:</b> {sesgo}</p><p><b>Mitigación:</b> {mitig}</p></div>',
            unsafe_allow_html=True,
        )
    st.write("")

    i1, i2 = st.columns(2)
    with i1:
        df10 = iso_25010.copy()
        df10["nombre"] = df10["caracteristica"].str.replace(r"^\d+\.\s*", "", regex=True)
        barras10 = alt.Chart(df10).mark_bar(cornerRadiusEnd=6).encode(
            y=alt.Y("nombre:N", sort="-x", title=None),
            x=alt.X("puntaje_100:Q", title="Puntaje (0–100)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("puntaje_100:Q", scale=alt.Scale(domain=[85, 100], range=["#bef264", VERDE_OSC]), legend=None),
            tooltip=[alt.Tooltip("nombre:N", title="Característica"), alt.Tooltip("puntaje_100:Q", title="Puntaje"),
                     alt.Tooltip("valor_medido:N", title="Evidencia medida")],
        )
        texto10 = barras10.mark_text(align="left", dx=4, fontWeight="bold", color=TINTA).encode(text="puntaje_100:Q", color=alt.value(TINTA))
        meta = alt.Chart(pd.DataFrame({"m": [90]})).mark_rule(color=NARANJA, strokeDash=[5, 4], strokeWidth=2).encode(x="m:Q")
        st.altair_chart((barras10 + texto10 + meta).properties(height=330, title=f"ISO/IEC 25010 · Producto (promedio {res_iso['iso_25010_promedio_100']}/100)"), width="stretch")
    with i2:
        df12 = iso_25012.copy()
        barras12 = alt.Chart(df12).mark_bar(cornerRadiusEnd=6).encode(
            y=alt.Y("caracteristica:N", sort="-x", title=None),
            x=alt.X("valor_pct:Q", title="Puntaje (0–100)", scale=alt.Scale(domain=[0, 100])),
            color=alt.Color("punto_vista:N", scale=alt.Scale(range=[VERDE, AZUL, NARANJA]), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("caracteristica:N", title="Característica"), alt.Tooltip("punto_vista:N", title="Punto de vista"),
                     alt.Tooltip("valor_pct:Q", title="Puntaje"), alt.Tooltip("metrica_medida:N", title="Evidencia medida")],
        )
        texto12 = barras12.mark_text(align="left", dx=4, fontWeight="bold").encode(text="valor_pct:Q", color=alt.value(TINTA))
        st.altair_chart((barras12 + texto12).properties(height=330, title=f"ISO/IEC 25012 · Datos en Capa Oro (promedio {res_iso['iso_25012_promedio_100']}/100)"), width="stretch")

    s1, s2, s3, s4 = st.columns(4)
    fia = res_iso["fiabilidad_acumulada_e0_e2"]
    s1.markdown(mini(f"{fia['disponibilidad_real_pct']}%", "Disponibilidad real (GitHub Actions)", VERDE), unsafe_allow_html=True)
    s2.markdown(mini(f"{fia['mtbf_horas']} h", "Tiempo medio entre fallos (MTBF)", AZUL), unsafe_allow_html=True)
    s3.markdown(mini(f"{res_iso['seguridad_estatica']['secretos_expuestos']}", f"Secretos expuestos en {res_iso['seguridad_estatica']['archivos_escaneados']} archivos", MORADO), unsafe_allow_html=True)
    s4.markdown(mini(f"{res_iso['completitud_capa_oro_pct']:.0f}%", "Completitud de la Capa Oro (0 nulos)", LIMA), unsafe_allow_html=True)
    with st.expander("📋 Ver tablas completas de evaluación ISO/IEC 25010 y 25012"):
        st.dataframe(iso_25010, hide_index=True, width="stretch")
        st.dataframe(iso_25012, hide_index=True, width="stretch")

# ===========================================================================
# PESTAÑA 5 · PRONÓSTICO 2026
# ===========================================================================
with tab_pron:
    seccion(
        "📈",
        "Pronóstico del precio del limón 2026 con intervalo de confianza al 95%",
        f"Modelo ganador {ganador['modelo']} · error de {ganador['MAPE_test_pct']:.2f}% en los 12 meses de prueba de 2025",
    )
    p1, p2 = st.columns(2)
    p1.markdown(
        f'<div class="card card-accent" style="--c:{VERDE}"><h4>🟢 Ventana de alta rentabilidad · Enero a Abril 2026</h4>'
        "<p>Menor corte en invierno → <b>precio alto</b>. El pico se espera en <b>febrero–marzo (≈ $41–43 MXN/kg)</b>.</p>"
        "<p>Recomendación: programar riegos de auxilio desde nov–dic para tener fruta #4/#5 lista y negociar contratos en centrales mayoristas.</p></div>",
        unsafe_allow_html=True,
    )
    p2.markdown(
        f'<div class="card card-accent" style="--c:{AMARILLO}"><h4>🟡 Valle de cosecha pico · Junio a Octubre 2026</h4>'
        "<p>Con las lluvias de verano sube la oferta → <b>precio bajo (≈ $19–23 MXN/kg)</b>.</p>"
        "<p>Recomendación: desviar fruta de segunda a la industria (aceite esencial, cáscara deshidratada) y evitar ventas spot sin piso de precio.</p></div>",
        unsafe_allow_html=True,
    )
    st.write("")

    hist = serie_oro[["anio_mes", "precio_frecuente_origen_colima_mxn_kg", "es_choque_legitimo_precio"]].copy()
    hist["fecha"] = pd.to_datetime(hist["anio_mes"] + "-01")
    hist["tramo"] = "Histórico observado (SNIIM)"
    pr = pronostico.copy()
    pr["fecha"] = pd.to_datetime(pr["anio_mes"] + "-01")
    pr["tramo"] = pr["horizonte"].map({"Evaluacion_Prueba_2025": "Validación 2025 (prueba)", "Pronostico_Futuro_2026": "Pronóstico 2026"})
    dom_tr = ["Histórico observado (SNIIM)", "Validación 2025 (prueba)", "Pronóstico 2026"]
    esc_tr = alt.Scale(domain=dom_tr, range=[TINTA, AZUL, VERDE])
    eje_x = alt.X("fecha:T", title=None, axis=alt.Axis(format="%b %Y", labelAngle=0))
    eje_y = alt.Y("valor:Q", title="Precio frecuente en origen (MXN/kg)")
    linea_hist = alt.Chart(hist).mark_line(strokeWidth=2).encode(
        x=eje_x, y=alt.Y("precio_frecuente_origen_colima_mxn_kg:Q", title="Precio frecuente en origen (MXN/kg)"),
        color=alt.Color("tramo:N", scale=esc_tr, legend=alt.Legend(title=None, orient="top")),
        tooltip=[alt.Tooltip("anio_mes:N", title="Mes"), alt.Tooltip("precio_frecuente_origen_colima_mxn_kg:Q", title="Precio real (MXN/kg)", format=".2f")],
    )
    banda_ic = alt.Chart(pr).mark_area(opacity=0.20).encode(
        x=eje_x, y="limite_inferior_ic95_mxn_kg:Q", y2="limite_superior_ic95_mxn_kg:Q",
        color=alt.Color("tramo:N", scale=esc_tr, legend=None),
    )
    linea_pr = alt.Chart(pr).mark_line(strokeDash=[6, 3], strokeWidth=2.6, point=alt.OverlayMarkDef(size=45, filled=True)).encode(
        x=eje_x, y="pronostico_puntual_mxn_kg:Q", color=alt.Color("tramo:N", scale=esc_tr, legend=None),
        tooltip=[alt.Tooltip("anio_mes:N", title="Mes"), alt.Tooltip("pronostico_puntual_mxn_kg:Q", title="Pronóstico (MXN/kg)", format=".2f"),
                 alt.Tooltip("limite_inferior_ic95_mxn_kg:Q", title="IC 95% inferior", format=".2f"),
                 alt.Tooltip("limite_superior_ic95_mxn_kg:Q", title="IC 95% superior", format=".2f")],
    )
    choques = alt.Chart(hist[hist["es_choque_legitimo_precio"]]).mark_point(shape="triangle-up", size=150, filled=True, color=ROJO).encode(
        x=eje_x, y="precio_frecuente_origen_colima_mxn_kg:Q",
        tooltip=[alt.Tooltip("anio_mes:N", title="Choque real de escasez"), alt.Tooltip("precio_frecuente_origen_colima_mxn_kg:Q", title="MXN/kg", format=".2f")],
    )
    corte = alt.Chart(pd.DataFrame({"fecha": [pd.Timestamp("2026-01-01")]})).mark_rule(strokeDash=[4, 4], color=GRIS).encode(x="fecha:T")
    st.altair_chart(
        alt.layer(banda_ic, linea_hist, linea_pr, choques, corte).properties(height=390, title="Precio mayorista del limón #5 en origen Colima · 2021 → 2026").interactive(bind_y=False),
        width="stretch",
    )
    st.caption("▲ rojo: choques reales de escasez (feb–mar 2022, feb 2024) conservados a propósito. Franja sombreada: intervalo de confianza al 95%. Usa la rueda del ratón para hacer zoom en el tiempo.")

    st.markdown("##### 🚦 Semáforo mensual 2026 (según la discretización de precios de la Capa Plata)")
    futuro = pr[pr["horizonte"] == "Pronostico_Futuro_2026"].reset_index(drop=True)

    def clasificar(precio: float) -> tuple[str, str]:
        if precio > 38:
            return "🔥 Escasez · precio máximo", VERDE_OSC
        if precio >= 28:
            return "🟢 Alto · buena venta", LIMA
        if precio >= 18:
            return "🟡 Medio · operación estándar", "#ca8a04"
        return "🔴 Bajo · cosecha pico", ROJO

    for fila_ini in (0, 6):
        cols_mes = st.columns(6)
        for j, col in enumerate(cols_mes):
            r = futuro.iloc[fila_ini + j]
            etiqueta, color = clasificar(float(r["pronostico_puntual_mxn_kg"]))
            mes_num = int(r["anio_mes"][-2:])
            col.markdown(
                f'<div class="mes" style="background:{color}"><div class="mn">{MESES[mes_num]} 2026</div>'
                f'<div class="mp">${r["pronostico_puntual_mxn_kg"]:.2f}</div>'
                f'<div class="mi">IC 95%: ${r["limite_inferior_ic95_mxn_kg"]:.0f} – ${r["limite_superior_ic95_mxn_kg"]:.0f}</div>'
                f'<div class="mt">{etiqueta}</div></div>',
                unsafe_allow_html=True,
            )

    m_a, m_b = st.columns([1, 1.25])
    with m_a:
        comp = comp_modelos.copy()
        comp["Modelo"] = comp["modelo"].str.replace(r"^\d+\.\s*", "", regex=True)
        graf_mod = alt.Chart(comp, title="Error de los 4 modelos en 2025 (MAPE %)").mark_bar(cornerRadiusEnd=6).encode(
            y=alt.Y("Modelo:N", sort="x", title=None),
            x=alt.X("MAPE_test_pct:Q", title="MAPE (%) · menor es mejor"),
            color=alt.condition(alt.datum.seleccionado, alt.value(VERDE), alt.value("#cbd5e1")),
            tooltip=["Modelo:N", alt.Tooltip("MAPE_test_pct:Q", title="MAPE %"), alt.Tooltip("RMSE_test_mxn_kg:Q", title="RMSE (MXN/kg)", format=".2f"),
                     alt.Tooltip("MAE_test_mxn_kg:Q", title="MAE (MXN/kg)", format=".2f")],
        )
        st.altair_chart((graf_mod + graf_mod.mark_text(align="left", dx=4, fontWeight="bold").encode(text=alt.Text("MAPE_test_pct:Q", format=".2f"), color=alt.value(TINTA))).properties(height=230), width="stretch")
        st.markdown(mini(f"p = {diag_ts['diagnostico_residuos_ljung_box']['ljung_box_lag12_pvalue']:.3f}", "Ljung-Box (lag 12): residuos = ruido blanco ✓", MORADO), unsafe_allow_html=True)
    with m_b:
        tabla_pron = futuro[["anio_mes", "pronostico_puntual_mxn_kg", "limite_inferior_ic95_mxn_kg", "limite_superior_ic95_mxn_kg", "recomendacion_comercial_cliente"]]
        st.dataframe(
            tabla_pron,
            hide_index=True,
            width="stretch",
            height=330,
            column_config={
                "anio_mes": st.column_config.TextColumn("Mes"),
                "pronostico_puntual_mxn_kg": st.column_config.NumberColumn("Pronóstico (MXN/kg)", format="$%.2f"),
                "limite_inferior_ic95_mxn_kg": st.column_config.NumberColumn("IC 95% inf.", format="$%.2f"),
                "limite_superior_ic95_mxn_kg": st.column_config.NumberColumn("IC 95% sup.", format="$%.2f"),
                "recomendacion_comercial_cliente": st.column_config.TextColumn("Recomendación comercial", width="large"),
            },
        )
    with st.expander("🖼️ Ver figura estática del pronóstico y diagnóstico de residuos (E1)"):
        st.image(str(FIGURAS_E1_DIR / "fig5_pronostico_final_ic95_residuos.png"), width="stretch")

# ===========================================================================
# PESTAÑA 6 · PUERTA DE CALIDAD Y CUARENTENA
# ===========================================================================
with tab_puerta:
    seccion(
        "🛡️",
        "Puerta de calidad y cuarentena · cero borrado silencioso",
        "Todo registro inválido se detiene antes de la Capa Plata y se guarda con la regla violada y el motivo",
    )
    ev_tab = clima_r["registros_evaluados_bronce"] + sniim_r["registros_evaluados_bronce"]
    ap_tab = clima_r["registros_aprobados_plata"] + sniim_r["registros_aprobados_plata"]
    q1, q2 = st.columns(2)
    with q1:
        st.markdown(
            f'<div class="card card-accent" style="--c:{AZUL}"><h4>📊 Puerta tabular (E1) · clima + precios</h4>'
            f'<p><b>{ev_tab:,}</b> evaluados → <b style="color:{VERDE}">{ap_tab:,}</b> aprobados · <b style="color:{ROJO}">{len(cuarentena)}</b> en cuarentena</p></div>',
            unsafe_allow_html=True,
        )
        st.progress(ap_tab / ev_tab, text=f"Tasa de aprobación: {100 * ap_tab / ev_tab:.2f}%")
    with q2:
        ev_geo = res_geo["puntos_bronce_evaluados"]
        ap_geo = res_geo["puntos_aprobados_dentro_colima_plata"]
        st.markdown(
            f'<div class="card card-accent" style="--c:{VERDE}"><h4>🗺️ Puerta geoespacial (E2) · OpenStreetMap</h4>'
            f'<p><b>{ev_geo:,}</b> evaluados → <b style="color:{VERDE}">{ap_geo:,}</b> dentro de Colima · <b style="color:{ROJO}">{len(cuarentena_geo)}</b> fuera del estado</p></div>',
            unsafe_allow_html=True,
        )
        st.progress(ap_geo / ev_geo, text=f"Tasa de aprobación: {100 * ap_geo / ev_geo:.2f}%")
    st.write("")

    r1, r2 = st.columns([1, 1.15])
    with r1:
        reglas = (
            cuarentena["regla_violada"].str.split("; ").explode().value_counts().rename_axis("regla").reset_index(name="registros")
        )
        reglas["puerta"] = "Tabular (E1)"
        reglas_geo = cuarentena_geo["regla_violada"].value_counts().rename_axis("regla").reset_index(name="registros")
        reglas_geo["puerta"] = "Geoespacial (E2)"
        todas = pd.concat([reglas, reglas_geo], ignore_index=True)
        graf_reglas = alt.Chart(todas, title="Reglas de calidad que detuvieron registros").mark_bar(cornerRadiusEnd=5).encode(
            y=alt.Y("regla:N", sort="-x", title=None),
            x=alt.X("registros:Q", title="Registros detenidos", scale=alt.Scale(type="symlog")),
            color=alt.Color("puerta:N", scale=alt.Scale(domain=["Tabular (E1)", "Geoespacial (E2)"], range=[AZUL, ROJO]), legend=alt.Legend(title=None, orient="bottom")),
            tooltip=[alt.Tooltip("regla:N", title="Regla"), alt.Tooltip("registros:Q", title="Registros"), alt.Tooltip("puerta:N", title="Puerta")],
        )
        st.altair_chart((graf_reglas + graf_reglas.mark_text(align="left", dx=4, fontWeight="bold").encode(text="registros:Q", color=alt.value(TINTA))).properties(height=340), width="stretch")
        st.caption("Escala logarítmica suave para comparar las 90 exclusiones geográficas con los casos individuales de la puerta tabular.")
    with r2:
        q_geo = cuarentena_geo.copy()
        q_geo["nombre"] = q_geo["llave_primaria"]
        q_geo["categoria"] = q_geo["categoria_agrologistica"].map(lambda c: CATEGORIAS.get(c, (c,))[0])
        q_geo["municipio"] = "Fuera de Colima (Jalisco / Michoacán)"
        capa_q = pdk.Layer(
            "ScatterplotLayer",
            data=q_geo[["longitud", "latitud", "nombre", "categoria", "municipio"]],
            get_position="[longitud, latitud]",
            get_fill_color=[220, 38, 38, 220],
            get_line_color=[255, 255, 255],
            get_radius=500,
            radius_min_pixels=4,
            stroked=True,
            pickable=True,
        )
        capa_mun_q = pdk.Layer(
            "GeoJsonLayer", data=cargar_geojson_municipios(), stroked=True, filled=True,
            get_fill_color="properties.fill", get_line_color="properties.line", line_width_min_pixels=1, pickable=False,
        )
        st.pydeck_chart(
            pdk.Deck(
                layers=[capa_mun_q, capa_q],
                initial_view_state=pdk.ViewState(latitude=19.1, longitude=-104.05, zoom=7.9),
                map_provider="carto",
                map_style="light",
                tooltip={"html": "<b>{nombre}</b><br/>{categoria}<br/><i>{municipio}</i>",
                         "style": {"backgroundColor": ROJO, "color": "white", "fontSize": "12px"}},
            ),
            height=360,
        )
        st.caption("🔴 Puntos del rectángulo de búsqueda que quedaron fuera de los límites oficiales de Colima → cuarentena geoespacial.")

    st.markdown(f"##### 🧾 Cuarentena tabular E1 ({len(cuarentena)} registros)")
    st.dataframe(
        cuarentena, hide_index=True, width="stretch",
        column_config={"motivo_rechazo": st.column_config.TextColumn("Motivo de rechazo", width="large")},
    )
    with st.expander(f"🧾 Cuarentena geoespacial E2 ({len(cuarentena_geo)} registros fuera de Colima)"):
        st.dataframe(cuarentena_geo, hide_index=True, width="stretch", height=360)

# ---------------------------------------------------------------------------
# Pie de página
# ---------------------------------------------------------------------------
html(
    f"""
    <div class="footer">🍋 <b>CITRO-DATA LAB COLIMA</b> · Proyecto Integrador Trusted Data Lab · TecNM — Instituto Tecnológico de Colima<br>
    Norberto Daniel Escareño Montaño (23460323) · Datos: © Open-Meteo / Copernicus ERA5-Land (CC BY 4.0), SNIIM-SE (Datos Abiertos MX),
    © OpenStreetMap contributors (ODbL 1.0), INEGI · <a href="{REPO_URL}" target="_blank">Repositorio en GitHub</a></div>
    """
)
