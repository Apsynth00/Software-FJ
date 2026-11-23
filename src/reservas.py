"""Gestión del ciclo de vida de una reserva en Software FJ."""

from src.entidades import Cliente, EntidadBase
from src.exceptions import DatoInvalidoError, ReservaInvalidaError, ServicioNoDisponibleError
from src.servicios import AlquilerEquipo, Servicio


class Reserva(EntidadBase):
    """Integra cliente, servicio, duración y estado con control de transiciones."""

    ESTADOS_VALIDOS = ("PENDIENTE", "CONFIRMADA", "CANCELADA")

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        duracion: int,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        **detalle_servicio,
    ):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("Debe asignarse un objeto Cliente válido.")
        if not cliente.activo:
            raise ReservaInvalidaError(f"El cliente '{cliente.nombre}' está inactivo y no puede reservar.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("Debe asignarse un objeto Servicio válido.")
        if not servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible.")

        servicio.validar_parametros(duracion, **detalle_servicio)
        monto_total = servicio.calcular_costo(
            duracion=duracion,
            impuesto=impuesto,
            descuento=descuento,
            **detalle_servicio,
        )

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self._detalle_servicio = detalle_servicio
        self._monto_total = monto_total
        self._estado = "PENDIENTE"

    @property
    def estado(self) -> str:
        return self._estado

    @property
    def monto_total(self) -> float:
        return self._monto_total

    def confirmar(self) -> str:
        """Confirma una reserva pendiente y descuenta inventario si aplica."""
        if self._estado == "CONFIRMADA":
            raise ReservaInvalidaError(f"La reserva {self.id} ya se encuentra confirmada.")
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError(f"No se puede confirmar la reserva {self.id} porque está cancelada.")
        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' dejó de estar disponible.")

        if isinstance(self.servicio, AlquilerEquipo):
            unidades = self._detalle_servicio.get("unidades", 1)
            self.servicio.validar_parametros(self.duracion, unidades=unidades)
            self.servicio.unidades_disponibles -= unidades

        self._estado = "CONFIRMADA"
        return f"Reserva {self.id} CONFIRMADA para {self.cliente.nombre} (Total: ${self._monto_total:,.2f})."

    def cancelar(self, motivo: str = "Cancelación solicitada") -> str:
        """Cancela una reserva activa y restituye unidades si había alquiler de equipo."""
        if self._estado == "CANCELADA":
            raise ReservaInvalidaError(f"La reserva {self.id} ya estaba cancelada.")

        if self._estado == "CONFIRMADA" and isinstance(self.servicio, AlquilerEquipo):
            unidades = self._detalle_servicio.get("unidades", 1)
            self.servicio.unidades_disponibles += unidades

        self._estado = "CANCELADA"
        return f"Reserva {self.id} CANCELADA ({motivo})."

    def resumen(self) -> str:
        return (
            f"Reserva [{self.id}] | Estado: {self._estado} | Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | Duración: {self.duracion} | Total: ${self._monto_total:,.2f}"
        )