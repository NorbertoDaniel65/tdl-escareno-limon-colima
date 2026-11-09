"""Pruebas unitarias para el módulo ExtractorEtico (extractores/base.py)."""
from __future__ import annotations

import urllib.robotparser
import pytest

from extractores.base import UA, ExtractorEtico


def test_user_agent_institucional_valido() -> None:
    ext = ExtractorEtico(pausa=1.5)
    assert "TDL-Observatorio" in ext.user_agent
    assert "23460323@colima.tecnm.mx" in ext.user_agent
    assert ext.sesion.headers["User-Agent"] == UA


def test_pausa_minima_etica_obligatoria() -> None:
    with pytest.raises(ValueError, match="pausa entre peticiones"):
        ExtractorEtico(pausa=0.5)


def test_bloqueo_estricto_cuando_robots_disallow() -> None:
    ext = ExtractorEtico(pausa=1.0)
    rp = urllib.robotparser.RobotFileParser()
    rp.parse(["User-agent: *", "Disallow: /privado/"])
    ext.robots["https://ejemplo.mx"] = rp

    with pytest.raises(PermissionError, match="robots.txt no permite"):
        ext.get("https://ejemplo.mx/privado/datos.csv", es_api_rest=False)
