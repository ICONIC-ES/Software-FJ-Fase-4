"""
Proyecto Fase 4 - Programación (213023)
Sistema Integral de Gestión de Clientes, Servicios y Reservas
Empresa: Software FJ

El sistema utiliza objetos y listas en memoria. No utiliza bases de datos.
Los archivos se usan únicamente para registrar eventos y errores (software_fj.log).
"""

from abc import ABC, abstractmethod
from datetime import datetime
import logging


# --------------------------- CONFIGURACIÓN DE LOGS ---------------------------

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    encoding="utf-8"
)


# -------------------------- EXCEPCIONES PERSONALIZADAS -----------------------

class ErrorSistema(Exception):
    """Excepción base para los errores controlados del sistema."""


class DatoInvalidoError(ErrorSistema):
    """Se presenta cuando un dato no cumple las validaciones."""


class ServicioNoDisponibleError(ErrorSistema):
    """Se presenta cuando un servicio no está disponible."""


class ReservaNoPermitidaError(ErrorSistema):
    """Se presenta cuando una reserva no puede procesarse."""


# ------------------------------- ENTIDADES -----------------------------------

class Entidad(ABC):
    """Clase abstracta que representa una entidad general del sistema."""

    def __init__(self, identificador):
        if not identificador:
            raise DatoInvalidoError("El identificador es obligatorio.")
        self._identificador = str(identificador)

    @property
    def identificador(self):
        return self._identificador

    @abstractmethod
    def describir(self):
        """Cada entidad debe proporcionar su descripción."""


class Cliente(Entidad):
    """Representa un cliente y protege sus datos mediante propiedades."""

    def __init__(self, identificador, nombre, correo, telefono):
        super().__init__(identificador)
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise DatoInvalidoError("El nombre debe tener al menos dos caracteres.")
        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):
        if not isinstance(valor, str) or "@" not in valor or "." not in valor:
            raise DatoInvalidoError("El correo electrónico no es válido.")
        self._correo = valor.strip().lower()

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        texto = str(valor).strip()
        if not texto.isdigit() or len(texto) < 7:
            raise DatoInvalidoError("El teléfono debe contener al menos 7 dígitos.")
        self._telefono = texto

    def describir(self):
        return f"Cliente {self.nombre} | Correo: {self.correo}"


# -------------------------------- SERVICIOS ----------------------------------

class Servicio(Entidad, ABC):
    """Clase abstracta para los servicios ofrecidos por Software FJ."""

    def __init__(self, identificador, nombre, tarifa_hora, disponible=True):
        super().__init__(identificador)
        if not isinstance(nombre, str) or not nombre.strip():
            raise DatoInvalidoError("El nombre del servicio es obligatorio.")
        if not isinstance(tarifa_hora, (int, float)) or tarifa_hora <= 0:
            raise DatoInvalidoError("La tarifa por hora debe ser mayor que cero.")
        self.nombre = nombre.strip()
        self.tarifa_hora = float(tarifa_hora)
        self.disponible = bool(disponible)

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    @abstractmethod
    def describir(self):
        pass

    def calcular_costo(self, duracion, impuesto=0.0, descuento=0.0):
        """
        Simula sobrecarga mediante parámetros opcionales:
        - calcular_costo(duracion)
        - calcular_costo(duracion, impuesto)
        - calcular_costo(duracion, impuesto, descuento)
        """
        self.validar_parametros(duracion)
        if not 0 <= impuesto <= 1:
            raise DatoInvalidoError("El impuesto debe estar entre 0 y 1.")
        if not 0 <= descuento <= 1:
            raise DatoInvalidoError("El descuento debe estar entre 0 y 1.")

        subtotal = self.tarifa_hora * duracion
        total_con_descuento = subtotal * (1 - descuento)
        return round(total_con_descuento * (1 + impuesto), 2)


class ReservaSala(Servicio):
    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0 or duracion > 12:
            raise DatoInvalidoError("La sala debe reservarse entre 0 y 12 horas.")
        if not self.disponible:
            raise ServicioNoDisponibleError("La sala no está disponible.")

    def describir(self):
        return f"Reserva de sala: {self.nombre}"


class AlquilerEquipo(Servicio):
    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0 or duracion > 72:
            raise DatoInvalidoError("El alquiler debe ser mayor a 0 y máximo 72 horas.")
        if not self.disponible:
            raise ServicioNoDisponibleError("El equipo no está disponible.")

    def describir(self):
        return f"Alquiler de equipo: {self.nombre}"


class AsesoriaEspecializada(Servicio):
    def validar_parametros(self, duracion):
        if not isinstance(duracion, (int, float)) or duracion <= 0 or duracion > 8:
            raise DatoInvalidoError("La asesoría debe durar entre 0 y 8 horas.")
        if not self.disponible:
            raise ServicioNoDisponibleError("La asesoría no está disponible.")

    def describir(self):
        return f"Asesoría especializada: {self.nombre}"


# -------------------------------- RESERVAS -----------------------------------

class Reserva(Entidad):
    """Relaciona un cliente con un servicio y controla su estado."""

    ESTADOS_VALIDOS = ("Pendiente", "Confirmada", "Cancelada")

    def __init__(self, identificador, cliente, servicio, duracion):
        super().__init__(identificador)
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("La reserva requiere un cliente válido.")
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("La reserva requiere un servicio válido.")
        servicio.validar_parametros(duracion)
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        logging.info("Reserva %s creada para %s.", self.identificador, cliente.nombre)

    def confirmar(self):
        if self.estado != "Pendiente":
            raise ReservaNoPermitidaError("Solo se pueden confirmar reservas pendientes.")
        self.estado = "Confirmada"
        logging.info("Reserva %s confirmada.", self.identificador)

    def cancelar(self):
        if self.estado == "Cancelada":
            raise ReservaNoPermitidaError("La reserva ya se encuentra cancelada.")
        self.estado = "Cancelada"
        logging.info("Reserva %s cancelada.", self.identificador)

    def procesar(self, impuesto=0.19, descuento=0.0):
        try:
            if self.estado == "Cancelada":
                raise ReservaNoPermitidaError("No se puede procesar una reserva cancelada.")
            total = self.servicio.calcular_costo(
                self.duracion, impuesto=impuesto, descuento=descuento
            )
        except (DatoInvalidoError, ServicioNoDisponibleError) as error:
            logging.exception("Error al procesar reserva %s.", self.identificador)
            raise ReservaNoPermitidaError(
                f"No fue posible procesar la reserva: {error}"
            ) from error  # Encadenamiento de excepciones
        else:
            logging.info("Reserva %s procesada. Total: $%.2f", self.identificador, total)
            return total
        finally:
            logging.info("Finalizó el intento de procesamiento de reserva %s.",
                         self.identificador)

    def describir(self):
        return (f"Reserva {self.identificador} | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Estado: {self.estado}")


# ----------------------------- GESTOR DEL SISTEMA ----------------------------

class SistemaSoftwareFJ:
    """Administra las listas internas de clientes, servicios y reservas."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente):
        if not isinstance(cliente, Cliente):
            raise DatoInvalidoError("El objeto recibido no es un cliente.")
        if any(c.identificador == cliente.identificador for c in self.clientes):
            raise DatoInvalidoError("Ya existe un cliente con ese identificador.")
        self.clientes.append(cliente)
        logging.info("Cliente registrado: %s.", cliente.nombre)
        return cliente

    def registrar_servicio(self, servicio):
        if not isinstance(servicio, Servicio):
            raise DatoInvalidoError("El objeto recibido no es un servicio.")
        if any(s.identificador == servicio.identificador for s in self.servicios):
            raise DatoInvalidoError("Ya existe un servicio con ese identificador.")
        self.servicios.append(servicio)
        logging.info("Servicio registrado: %s.", servicio.nombre)
        return servicio

    def crear_reserva(self, identificador, cliente, servicio, duracion):
        reserva = Reserva(identificador, cliente, servicio, duracion)
        if any(r.identificador == reserva.identificador for r in self.reservas):
            raise DatoInvalidoError("Ya existe una reserva con ese identificador.")
        self.reservas.append(reserva)
        return reserva


# --------------------------- PRUEBAS DE 10 OPERACIONES -----------------------

def ejecutar_pruebas():
    sistema = SistemaSoftwareFJ()
    print("\nSISTEMA INTEGRAL SOFTWARE FJ - PRUEBAS DE FUNCIONAMIENTO")
    print("-" * 62)

    # 1. Registro correcto de cliente.
    try:
        cliente1 = sistema.registrar_cliente(
            Cliente("C001", "Laura Pérez", "laura@email.com", "3001234567")
        )
        print("1. Cliente registrado:", cliente1.describir())
    except ErrorSistema as error:
        print("1. Error:", error)

    # 2. Registro de cliente con correo inválido.
    try:
        Cliente("C002", "Carlos Ruiz", "correo-invalido", "3007654321")
    except ErrorSistema as error:
        logging.exception("Prueba 2: registro inválido de cliente.")
        print("2. Validación de cliente inválido:", error)

    # 3. Registro de segundo cliente.
    try:
        cliente2 = sistema.registrar_cliente(
            Cliente("C003", "Andrés Gómez", "andres@email.com", "3015556677")
        )
        print("3. Segundo cliente registrado:", cliente2.nombre)
    except ErrorSistema as error:
        print("3. Error:", error)

    # 4. Creación correcta de una sala.
    try:
        sala = sistema.registrar_servicio(
            ReservaSala("S001", "Sala de reuniones", 50000)
        )
        print("4. Servicio creado:", sala.describir())
    except ErrorSistema as error:
        print("4. Error:", error)

    # 5. Creación de alquiler de equipo.
    try:
        equipo = sistema.registrar_servicio(
            AlquilerEquipo("S002", "Computador portátil", 20000)
        )
        print("5. Servicio creado:", equipo.describir())
    except ErrorSistema as error:
        print("5. Error:", error)

    # 6. Creación de asesoría especializada.
    try:
        asesoria = sistema.registrar_servicio(
            AsesoriaEspecializada("S003", "Asesoría en programación", 80000)
        )
        print("6. Servicio creado:", asesoria.describir())
    except ErrorSistema as error:
        print("6. Error:", error)

    # 7. Intento de crear servicio con tarifa inválida.
    try:
        ReservaSala("S004", "Sala inválida", -1000)
    except ErrorSistema as error:
        logging.exception("Prueba 7: creación incorrecta de servicio.")
        print("7. Servicio inválido controlado:", error)

    # 8. Reserva exitosa y cálculo con impuesto y descuento.
    try:
        reserva1 = sistema.crear_reserva("R001", cliente1, sala, 2)
        reserva1.confirmar()
        total = reserva1.procesar(impuesto=0.19, descuento=0.10)
        print(f"8. Reserva exitosa: {reserva1.describir()} | Total: ${total:,.2f}")
    except ErrorSistema as error:
        print("8. Error:", error)

    # 9. Intento de reserva con duración inválida.
    try:
        sistema.crear_reserva("R002", cliente2, equipo, 100)
    except ErrorSistema as error:
        logging.exception("Prueba 9: intento de reserva inválido.")
        print("9. Reserva fallida controlada:", error)

    # 10. Reserva de servicio no disponible.
    try:
        servicio_no_disponible = AsesoriaEspecializada(
            "S005", "Asesoría temporalmente suspendida", 60000, disponible=False
        )
        sistema.registrar_servicio(servicio_no_disponible)
        sistema.crear_reserva("R003", cliente2, servicio_no_disponible, 1)
    except ErrorSistema as error:
        logging.exception("Prueba 10: reserva de servicio no disponible.")
        print("10. Servicio no disponible controlado:", error)

    # Ejemplo adicional de try/except/else/finally.
    print("-" * 62)
    try:
        print("Resumen: clientes =", len(sistema.clientes),
              "| servicios =", len(sistema.servicios),
              "| reservas =", len(sistema.reservas))
    except Exception as error:
        logging.exception("Error al mostrar el resumen.")
        print("No se pudo mostrar el resumen:", error)
    else:
        print("Resumen generado correctamente.")
    finally:
        print("Las pruebas finalizaron. Revise el archivo software_fj.log.")


if __name__ == "__main__":
    ejecutar_pruebas()
