"""Punto de entrada CLI para ejecutar la máquina de captura en Capa Bronce (local y en GitHub Actions)."""
from __future__ import annotations

import argparse
import json

from .base import ExtractorEtico
from .open_meteo import capturar_clima_diario_actual, descargar_historico_agroclima
from .sniim_limon import generar_serie_historica_sniim, verificar_portal_sniim_etico


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Máquina de captura en Capa Bronce - Observatorio Agroclimático y de Precios del Limón en Colima (TDL)"
    )
    parser.add_argument(
        "--modo",
        choices=["completo", "diario", "historico"],
        default="diario",
        help="'completo' descarga históricos de 60 meses + captura diaria; 'diario' corre la captura programada para GitHub Actions.",
    )
    args = parser.parse_args()

    extractor = ExtractorEtico(pausa=1.5)
    resumen = {}

    if args.modo in ("completo", "historico"):
        resumen["open_meteo_historico"] = descargar_historico_agroclima(extractor=extractor)
        resumen["sniim_historico"] = generar_serie_historica_sniim()

    if args.modo in ("completo", "diario"):
        # Asegura que la serie base exista antes de correr el monitoreo incremental
        from .sniim_limon import BRONCE_SNIIM_DIR
        if not (BRONCE_SNIIM_DIR / "precios_limon_sniim_historico_60m.csv").exists():
            generar_serie_historica_sniim()
        resumen["open_meteo_diario"] = capturar_clima_diario_actual(extractor=extractor)
        resumen["sniim_monitoreo"] = verificar_portal_sniim_etico(extractor=extractor)

    print(json.dumps(resumen, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
