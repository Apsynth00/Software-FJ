"""Gestor central en memoria (listas internas) con registro obligatorio en logs."""

from src.entidades import Cliente
from src.exceptions import (
    DatoInvalidoError,
    ErrorSoftwareFJ,
    ReservaInvalidaError,
    logger_fj,
)
from src.reservas import Reserva
from src.servicios import Servicio


class SistemaSoftwareFJ:
    """Administra clientes, servicios y reservas en listas en memoria."""

    def __init__(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        logger_fj.info("Sistema Software FJ inicializado correctamente.")

    def agregar_cliente(self, cliente: Cliente) -> str:
        if any(c.id == cliente.id for c in self.clientes):
            raise DatoInvalidoError(f"Ya existe un cliente con ID '{cliente.id}'.")
        self.clientes.append(cliente)
        msg = f"Cliente agregado: {cliente.resumen()}"
        logger_fj.info(msg)
        return msg

    def agregar_servicio(self, servicio: Servicio) -> str:
        if any(s.codigo == servicio.codigo for s in self.servicios):
            raise DatoInvalidoError(f"Ya existe un servicio con código '{servicio.codigo}'.")
        self.servicios.append(servicio)
        msg = f"Servicio agregado: {servicio.describir()}"
        logger_fj.info(msg)
        return msg

    def buscar_cliente(self, id_cliente: str) -> Cliente:
        clave = id_cliente.strip().upper() if isinstance(id_cliente, str) else ""
        for cliente in self.clientes:
            if cliente.id == clave:
                return cliente
        raise DatoInvalidoError(f"Cliente con ID '{id_cliente}' no encontrado.")

    def buscar_servicio(self, codigo_servicio: str) -> Servicio:
        clave = codigo_servicio.strip().upper() if isinstance(codigo_servicio, str) else ""
        for servicio in self.servicios:
            if servicio.codigo == clave:
                return servicio
        raise DatoInvalidoError(f"Servicio con código '{codigo_servicio}' no encontrado.")

    def crear_y_procesar_reserva(
        self,
        id_reserva: str,
        id_cliente: str,
        codigo_servicio: str,
        duracion: int,
        confirmar_inmediato: bool = True,
        impuesto: float = 0.19,
        descuento: float = 0.0,
        **detalle_servicio,
    ) -> str:
        """Crea y procesa una reserva usando try / except / else / finally y log de errores."""
        resultado = ""
        exito = False
        try:
            if any(r.id == id_reserva.strip().upper() for r in self.reservas if isinstance(id_reserva, str)):
                raise ReservaInvalidaError(f"La reserva '{id_reserva}' ya está registrada.")

            cliente = self.buscar_cliente(id_cliente)
            servicio = self.buscar_servicio(codigo_servicio)
            reserva = Reserva(
                id_reserva=id_reserva,
                cliente=cliente,
                servicio=servicio,
                duracion=duracion,
                impuesto=impuesto,
                descuento=descuento,
                **detalle_servicio,
            )
            self.reservas.append(reserva)
            if confirmar_inmediato:
                resultado = reserva.confirmar()
            else:
                resultado = f"Reserva {reserva.id} creada en estado PENDIENTE."
        except ErrorSoftwareFJ as err:
            logger_fj.error("Error controlado [%s] en reserva '%s': %s", err.codigo, id_reserva, err)
            resultado = f"[Error {err.codigo}] {err}"
        except Exception as err:
            try:
                raise ErrorSoftwareFJ(f"Fallo inesperado en reserva '{id_reserva}': {err}") from err
            except ErrorSoftwareFJ as encadenada:
                logger_fj.critical("Excepción encadenada: %s", encadenada)
                resultado = f"[Error crítico] {encadenada}"
        else:
            exito = True
            logger_fj.info("Operación exitosa en reserva '%s': %s", id_reserva, resultado)
        finally:
            estado_traza = "OK" if exito else "FALLO"
            logger_fj.info("Fin de procesamiento de reserva '%s' -> Estado: %s", id_reserva, estado_traza)

        return resultado