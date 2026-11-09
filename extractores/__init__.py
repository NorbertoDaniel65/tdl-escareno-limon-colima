"""Paquete de extractores éticos del Observatorio Agroclimático y de Precios del Limón en Colima (TDL)."""
from .base import ExtractorEtico, UA, registrar_bitacora, guardar_con_metadatos

__all__ = ["ExtractorEtico", "UA", "registrar_bitacora", "guardar_con_metadatos"]
