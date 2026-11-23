"""Excepciones personalizadas y configuración de registro de eventos/errores."""

import logging
from pathlib import Path


def configurar_logger(ruta_log: str = "logs/software_fj.log") -> logging.Logger:
    """Configura un logger que guarda eventos y errores en archivo sin base de datos."""
    archivo = Path(ruta_log)
    archivo.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    # Evita duplicar manejadores si se reimporta el módulo
    if not logger.handlers:
        manejador_archivo = logging.FileHandler(archivo, encoding="utf-8")
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        manejador_archivo.setFormatter(formato)
        logger.addHandler(manejador_archivo)

    return logger


logger_fj = configurar_logger()


class ErrorSoftwareFJ(Exception):
    """Excepción base para errores controlados de Software FJ."""

    def __init__(self, mensaje: str, codigo: str = "ERR_GENERAL"):
        super().__init__(mensaje)
        self.codigo = codigo


class DatoInvalidoError(ErrorSoftwareFJ):
    """Error por datos faltantes, formato incorrecto o valores fuera de rango."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_DATO_INVALIDO")


class ServicioNoDisponibleError(ErrorSoftwareFJ):
    """Error cuando el servicio está inactivo o no puede atenderse."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_SERVICIO_NO_DISPONIBLE")


class ReservaInvalidaError(ErrorSoftwareFJ):
    """Error por estados incompatibles, duplicidad o reglas de reserva."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_RESERVA_INVALIDA")


class CalculoInconsistenteError(ErrorSoftwareFJ):
    """Error cuando el cálculo de tarifas, descuentos o impuestos es inválido."""

    def __init__(self, mensaje: str):
        super().__init__(mensaje, codigo="ERR_CALCULO_INCONSISTENTE")