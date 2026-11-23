"""Entidades generales del sistema y clase Cliente con encapsulación."""

from abc import ABC, abstractmethod
import re

from src.exceptions import DatoInvalidoError


class EntidadBase(ABC):
    """Clase abstracta base para entidades identificables de Software FJ."""

    def __init__(self, id_entidad: str):
        if not isinstance(id_entidad, str) or not id_entidad.strip():
            raise DatoInvalidoError("El identificador de la entidad es obligatorio.")
        self._id = id_entidad.strip().upper()

    @property
    def id(self) -> str:
        """Retorna el identificador único de la entidad."""
        return self._id

    @abstractmethod
    def resumen(self) -> str:
        """Representación resumida obligatoria para cada entidad concreta."""


class Cliente(EntidadBase):
    """Representa un cliente con atributos encapsulados y validaciones estrictas."""

    _REGEX_CORREO = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

    def __init__(self, id_cliente: str, nombre: str, correo: str, telefono: str, activo: bool = True):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.__activo = bool(activo)

    @property
    def nombre(self) -> str:
        return self.__nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise DatoInvalidoError("El nombre del cliente debe tener al menos 3 caracteres.")
        self.__nombre = valor.strip()

    @property
    def correo(self) -> str:
        return self.__correo

    @correo.setter
    def correo(self, valor: str) -> None:
        if not isinstance(valor, str) or not self._REGEX_CORREO.match(valor.strip()):
            raise DatoInvalidoError(f"Correo electrónico inválido: '{valor}'.")
        self.__correo = valor.strip().lower()

    @property
    def telefono(self) -> str:
        return self.__telefono

    @telefono.setter
    def telefono(self, valor: str) -> None:
        limpio = valor.strip() if isinstance(valor, str) else ""
        digitos = re.sub(r"\D", "", limpio)
        if len(digitos) < 7:
            raise DatoInvalidoError("El teléfono del cliente debe tener al menos 7 dígitos.")
        self.__telefono = limpio

    @property
    def activo(self) -> bool:
        return self.__activo

    def desactivar(self) -> None:
        self.__activo = False

    def activar(self) -> None:
        self.__activo = True

    def resumen(self) -> str:
        estado = "Activo" if self.__activo else "Inactivo"
        return f"Cliente [{self.id}] {self.__nombre} <{self.__correo}> - {estado}"