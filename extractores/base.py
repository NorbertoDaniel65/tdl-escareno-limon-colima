"""Extractor ético base: respeta robots.txt, se identifica, aplica pausa mínima y registra metadatos en Capa Bronce."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.robotparser
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests

UA = "TDL-Observatorio-Limon-Colima/1.0 (proyecto academico TecNM Colima; contacto: 23460323@colima.tecnm.mx)"

ROOT_DIR = Path(__file__).resolve().parent.parent
BITACORA_PATH = ROOT_DIR / "calidad" / "bitacora_capturas.jsonl"
ROBOTS_DIR = ROOT_DIR / "data" / "bronce" / "robots_txt"


class ExtractorEtico:
    """Extractor ético oficial del Kit de Arranque Trusted Data Lab con soporte de trazabilidad en Capa Bronce."""

    def __init__(self, pausa: float = 1.5, user_agent: str = UA) -> None:
        if pausa < 1.0:
            raise ValueError("Por regla ética del proyecto TDL, la pausa entre peticiones al mismo dominio debe ser >= 1.0 s")
        self.pausa = float(pausa)  # segundos mínimos entre peticiones al mismo dominio
        self.user_agent = user_agent
        self.robots: dict[str, urllib.robotparser.RobotFileParser] = {}
        self.ultimo: dict[str, float] = {}
        self.sesion = requests.Session()
        self.sesion.headers["User-Agent"] = self.user_agent

    def _reglas(self, url: str) -> urllib.robotparser.RobotFileParser:
        p = urlparse(url)
        base = f"{p.scheme}://{p.netloc}"
        if base not in self.robots:
            robots_url = base + "/robots.txt"
            rp = urllib.robotparser.RobotFileParser(robots_url)
            try:
                r = self.sesion.get(robots_url, timeout=15)
                if r.status_code == 200:
                    rp.parse(r.text.splitlines())
                    self._archivar_robots(p.netloc, robots_url, r.status_code, r.text)
                elif r.status_code in (401, 403):
                    rp.disallow_all = True
                    self._archivar_robots(p.netloc, robots_url, r.status_code, "")
                else:
                    rp.allow_all = True
                    self._archivar_robots(p.netloc, robots_url, r.status_code, r.text[:500])
            except requests.RequestException:
                # Si el dominio no expone robots.txt accesible pero el endpoint responde, se documenta como sin restricción explícita
                rp.allow_all = True
            self.robots[base] = rp
        return self.robots[base]

    def _archivar_robots(self, netloc: str, robots_url: str, status_code: int, contenido: str) -> None:
        ROBOTS_DIR.mkdir(parents=True, exist_ok=True)
        safe_name = netloc.replace(":", "_").replace("/", "_")
        txt_path = ROBOTS_DIR / f"{safe_name}_robots.txt"
        meta_path = ROBOTS_DIR / f"{safe_name}_robots.meta.json"
        txt_path.write_text(contenido or f"# HTTP {status_code} (sin archivo robots.txt público en {robots_url})\n", encoding="utf-8")
        meta = {
            "dominio": netloc,
            "robots_url": robots_url,
            "http_status": status_code,
            "verificado_utc": datetime.now(timezone.utc).isoformat(),
            "user_agent": self.user_agent,
        }
        meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")

    def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        intentos: int = 3,
        es_api_rest: bool = False,
    ) -> requests.Response:
        reglas = self._reglas(url)
        if not es_api_rest and not reglas.can_fetch(self.user_agent, url):
            raise PermissionError(f"robots.txt no permite {url}")
        dominio = urlparse(url).netloc
        delay_robots = reglas.crawl_delay(self.user_agent) or reglas.crawl_delay("*") or 0
        pausa = max(self.pausa, float(delay_robots))
        espera = pausa - (time.time() - self.ultimo.get(dominio, 0.0))
        if espera > 0:
            time.sleep(espera)
        for i in range(intentos):
            r = self.sesion.get(url, params=params, timeout=25)
            self.ultimo[dominio] = time.time()
            if r.status_code == 429 or r.status_code >= 500:
                time.sleep(pausa * (2**i))  # espera exponencial ante saturación
                continue
            r.raise_for_status()
            return r
        raise RuntimeError(f"Sin respuesta valida de {url} tras {intentos} intentos")


def calcular_sha256(ruta: Path) -> str:
    h = hashlib.sha256()
    with ruta.open("rb") as f:
        for bloque in iter(lambda: f.read(65536), b""):
            h.update(bloque)
    return h.hexdigest()


def guardar_con_metadatos(
    ruta_archivo: Path,
    fuente: str,
    url_origen: str,
    registros: int,
    periodos: int | None = None,
    licencia: str = "Datos Abiertos / Uso Académico",
    notas: str = "",
) -> dict[str, Any]:
    """Genera el archivo .meta.json junto al dataset en la capa bronce con su hash SHA-256 y linaje de captura."""
    sha = calcular_sha256(ruta_archivo)
    meta = {
        "archivo": ruta_archivo.name,
        "ruta_relativa": str(ruta_archivo.relative_to(ROOT_DIR)).replace("\\", "/"),
        "fuente": fuente,
        "url_origen": url_origen,
        "capturado_en_utc": datetime.now(timezone.utc).isoformat(),
        "user_agent": UA,
        "formato": ruta_archivo.suffix.lstrip("."),
        "tamano_bytes": ruta_archivo.stat().st_size,
        "sha256": sha,
        "registros": registros,
        "periodos_temporales": periodos if periodos is not None else registros,
        "datos_personales_incluidos": False,
        "licencia": licencia,
        "notas": notas,
    }
    meta_path = ruta_archivo.with_name(ruta_archivo.name + ".meta.json")
    meta_path.write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    return meta


def registrar_bitacora(
    fuente: str,
    operacion: str,
    estado: str,
    duracion_seg: float,
    registros: int,
    archivo_salida: str,
    sha256: str = "",
    detalle: str = "",
) -> dict[str, Any]:
    """Agrega un evento estructurado a calidad/bitacora_capturas.jsonl para el cálculo de MTBF/MTTR y disponibilidad en E1."""
    BITACORA_PATH.parent.mkdir(parents=True, exist_ok=True)
    evento = {
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "fuente": fuente,
        "operacion": operacion,
        "estado": estado,  # "EXITO" | "FALLO"
        "duracion_seg": round(duracion_seg, 3),
        "registros_capturados": registros,
        "archivo_bronce": archivo_salida,
        "sha256": sha256,
        "detalle": detalle,
    }
    with BITACORA_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(evento, ensure_ascii=False) + "\n")
    return evento
