"""Ejecución secuencial del sistema Software FJ para probar casos válidos y errores."""

from src.entidades import Cliente
from src.exceptions import ErrorSoftwareFJ, logger_fj
from src.gestor import SistemaSoftwareFJ
from src.servicios import AlquilerEquipo, AsesoriaEspecializada, ReservaSala


def main() -> None:
    sistema = SistemaSoftwareFJ()

    print("--- 1. Registro de clientes (incluyendo errores) ---")
    for args_cliente in [
        ("C01", "Laura Gómez", "laura@empresa.com", "3001234567"),
        ("C02", "Carlos Ruiz", "carlos@empresa.com", "3109876543"),
        ("C03", "A", "correo-malo", "12"),  # Error: nombre y correo/teléfono inválidos
    ]:
        try:
            cliente = Cliente(*args_cliente)
            print(sistema.agregar_cliente(cliente))
        except ErrorSoftwareFJ as err:
            logger_fj.error("Error al crear cliente %s: %s", args_cliente, err)
            print("Error controlado:", err)

    print("\n--- 2. Registro de servicios especializados ---")
    servicios_demo = [
        ReservaSala("S01", "Sala Ejecutiva Norte", 80000, capacidad=12),
        AlquilerEquipo("E01", "Laptop Pro i7", 45000, unidades_disponibles=4),
        AsesoriaEspecializada("A01", "Arquitectura Cloud", 150000, especialidad="Cloud & DevOps"),
    ]
    for srv in servicios_demo:
        print(sistema.agregar_servicio(srv))

    print("\n--- 3. Demostración de variantes de cálculo y polimorfismo ---")
    for srv in sistema.servicios:
        print(srv.describir(), "| Costo 2 und/hr/sesión:", srv.calcular_variante(2))

    print("\n--- 4. Secuencia de reservas (casos exitosos y de error) ---")
    pruebas_reservas = [
        ("R01", "C01", "S01", 2, True, 0.19, 0.10, {"asistentes": 8}),       # Válida con descuento
        ("R02", "C02", "E01", 3, True, 0.19, 0.0, {"unidades": 2}),        # Válida (quedan 2 laptops)
        ("R03", "C01", "A01", 1, False, 0.19, 0.0, {}),                    # Válida (queda PENDIENTE)
        ("R04", "C01", "S01", 2, True, 0.19, 0.0, {"asistentes": 25}),      # Error: supera capacidad
        ("R05", "C02", "E01", 2, True, 0.19, 0.0, {"unidades": 5}),        # Error: supera stock restante
        ("R06", "C01", "E01", 1, True, 1.5, 0.0, {"unidades": 1}),         # Error: cálculo inconsistente
        ("R07", "C99", "S01", 1, True, 0.19, 0.0, {"asistentes": 2}),       # Error: cliente inexistente
    ]

    for id_res, id_cli, cod_srv, dur, conf, imp, desc, extras in pruebas_reservas:
        print(
            sistema.crear_y_procesar_reserva(
                id_reserva=id_res,
                id_cliente=id_cli,
                codigo_servicio=cod_srv,
                duracion=dur,
                confirmar_inmediato=conf,
                impuesto=imp,
                descuento=desc,
                **extras,
            )
        )

    print("\n--- 5. Estado final de reservas en memoria ---")
    for res in sistema.reservas:
        print(res.resumen())

    print("\nRevisa el archivo 'logs/software_fj.log' para ver el historial de eventos y errores.")


if __name__ == "__main__":
    main()