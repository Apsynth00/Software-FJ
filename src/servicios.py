"""Jerarquía de servicios de Software FJ con polimorfismo y variantes de cálculo."""

from abc import ABC, abstractmethod
from functools import singledispatchmethod

from src.exceptions import (
    CalculoInconsistenteError,
    DatoInvalidoError,
    ServicioNoDisponibleError,
)


class Servicio(ABC):
    """Clase abstracta base para los servicios ofrecidos por Software FJ."""

    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True):
        if not isinstance(codigo, str) or not codigo.strip():
            raise DatoInvalidoError("El código del servicio no puede estar vacío.")
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise DatoInvalidoError("El nombre del servicio debe tener al menos 3 caracteres.")
        if isinstance(tarifa_base, bool) or not isinstance(tarifa_base, (int, float)) or tarifa_base <= 0:
            raise DatoInvalidoError("La tarifa base debe ser un número mayor que cero.")

        self.codigo = codigo.strip().upper()
        self.nombre = nombre.strip()
        self._tarifa_base = float(tarifa_base)
        self._disponible = bool(disponible)

    @property
    def tarifa_base(self) -> float:
        return self._tarifa_base

    @property
    def disponible(self) -> bool:
        return self._disponible

    def marcar_disponible(self, estado: bool) -> None:
        self._disponible = bool(estado)

    @abstractmethod
    def validar_parametros(self, duracion: int, **kwargs) -> None:
        """Valida duración y parámetros específicos de cada tipo de servicio."""

    @abstractmethod
    def calcular_costo(
        self,
        duracion: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        **kwargs,
    ) -> float:
        """Calcula el costo total aplicando validaciones, impuestos y descuentos."""

    @abstractmethod
    def describir(self) -> str:
        """Describe las características principales del servicio."""

    def _validar_tarifa_y_ajustes(self, subtotal: float, impuesto: float, descuento: float) -> float:
        """Valida que los ajustes financieros sean consistentes y calcula el total."""
        try:
            if isinstance(impuesto, bool) or not isinstance(impuesto, (int, float)):
                raise TypeError("El impuesto debe ser numérico.")
            if isinstance(descuento, bool) or not isinstance(descuento, (int, float)):
                raise TypeError("El descuento debe ser numérico.")
            if impuesto < 0 or impuesto > 1:
                raise ValueError("El impuesto debe estar entre 0.0 y 1.0.")
            if descuento < 0 or descuento >= 1:
                raise ValueError("El descuento debe estar entre 0.0 y menor que 1.0.")
            if subtotal < 0:
                raise ValueError("El subtotal no puede ser negativo.")

            total = (subtotal * (1.0 - float(descuento))) * (1.0 + float(impuesto))
            if total <= 0:
                raise ValueError("El total calculado debe ser mayor que cero.")
            return round(total, 2)
        except (TypeError, ValueError) as exc:
            # Encadenamiento explícito de excepciones
            raise CalculoInconsistenteError(f"Error al calcular el costo de '{self.nombre}': {exc}") from exc

    @singledispatchmethod
    def calcular_variante(self, parametro) -> float:
        """Sobrecarga polimórfica: acepta duración (int) o descuento porcentual (float)."""
        raise DatoInvalidoError(f"Tipo no soportado para cálculo rápido: {type(parametro).__name__}")

    @calcular_variante.register
    def _(self, duracion: int) -> float:
        return self.calcular_costo(duracion=duracion)

    @calcular_variante.register
    def _(self, porcentaje_descuento: float) -> float:
        return self.calcular_costo(duracion=1, descuento=porcentaje_descuento)


class ReservaSala(Servicio):
    """Servicio de reserva de salas (reuniones, capacitación, auditorio)."""

    def __init__(self, codigo: str, nombre: str, tarifa_hora: float, capacidad: int, disponible: bool = True):
        super().__init__(codigo, nombre, tarifa_hora, disponible)
        if isinstance(capacidad, bool) or not isinstance(capacidad, int) or capacidad <= 0:
            raise DatoInvalidoError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad

    def validar_parametros(self, duracion: int, asistentes: int = 1, **kwargs) -> None:
        if isinstance(duracion, bool) or not isinstance(duracion, int) or duracion <= 0:
            raise DatoInvalidoError("La duración en horas de la sala debe ser un entero positivo.")
        if isinstance(asistentes, bool) or not isinstance(asistentes, int) or asistentes <= 0:
            raise DatoInvalidoError("El número de asistentes debe ser mayor que cero.")
        if asistentes > self.capacidad:
            raise DatoInvalidoError(
                f"Los asistentes ({asistentes}) superan la capacidad de la sala '{self.nombre}' ({self.capacidad})."
            )

    def calcular_costo(
        self,
        duracion: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        asistentes: int = 1,
        **kwargs,
    ) -> float:
        self.validar_parametros(duracion, asistentes=asistentes)
        subtotal = self._tarifa_base * duracion
        return self._validar_tarifa_y_ajustes(subtotal, impuesto, descuento)

    def describir(self) -> str:
        return f"[Sala] {self.nombre} | Capacidad: {self.capacidad} pers. | ${self._tarifa_base:,.2f}/hora"


class AlquilerEquipo(Servicio):
    """Servicio de alquiler de equipos tecnológicos (portátiles, proyectores, kits)."""

    def __init__(self, codigo: str, nombre: str, tarifa_dia: float, unidades_disponibles: int, disponible: bool = True):
        super().__init__(codigo, nombre, tarifa_dia, disponible)
        if isinstance(unidades_disponibles, bool) or not isinstance(unidades_disponibles, int) or unidades_disponibles < 0:
            raise DatoInvalidoError("Las unidades disponibles deben ser un entero no negativo.")
        self.unidades_disponibles = unidades_disponibles

    def validar_parametros(self, duracion: int, unidades: int = 1, **kwargs) -> None:
        if isinstance(duracion, bool) or not isinstance(duracion, int) or duracion <= 0:
            raise DatoInvalidoError("La duración en días del alquiler debe ser un entero positivo.")
        if isinstance(unidades, bool) or not isinstance(unidades, int) or unidades <= 0:
            raise DatoInvalidoError("Las unidades a alquilar deben ser un entero positivo.")
        if unidades > self.unidades_disponibles:
            raise ServicioNoDisponibleError(
                f"Solo hay {self.unidades_disponibles} unidad(es) de '{self.nombre}' (solicitadas: {unidades})."
            )

    def calcular_costo(
        self,
        duracion: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        unidades: int = 1,
        **kwargs,
    ) -> float:
        self.validar_parametros(duracion, unidades=unidades)
        subtotal = self._tarifa_base * duracion * unidades
        return self._validar_tarifa_y_ajustes(subtotal, impuesto, descuento)

    def describir(self) -> str:
        return (
            f"[Equipo] {self.nombre} | Stock: {self.unidades_disponibles} und. | "
            f"${self._tarifa_base:,.2f}/día por unidad"
        )


class AsesoriaEspecializada(Servicio):
    """Servicio de consultoría o asesoría técnica especializada."""

    def __init__(self, codigo: str, nombre: str, tarifa_sesion: float, especialidad: str, disponible: bool = True):
        super().__init__(codigo, nombre, tarifa_sesion, disponible)
        if not isinstance(especialidad, str) or len(especialidad.strip()) < 3:
            raise DatoInvalidoError("La especialidad de la asesoría es obligatoria.")
        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion: int, **kwargs) -> None:
        if isinstance(duracion, bool) or not isinstance(duracion, int) or duracion <= 0:
            raise DatoInvalidoError("La cantidad de sesiones debe ser un entero positivo.")

    def calcular_costo(
        self,
        duracion: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        **kwargs,
    ) -> float:
        self.validar_parametros(duracion)
        subtotal = self._tarifa_base * duracion
        return self._validar_tarifa_y_ajustes(subtotal, impuesto, descuento)

    def describir(self) -> str:
        return f"[Asesoría] {self.nombre} ({self.especialidad}) | ${self._tarifa_base:,.2f}/sesión"