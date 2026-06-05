# src/gestion/controlador_partida.py

from src.core.coordenada import Coordenada
from src.gestion.partida import ConfiguracionMapa, EstadoPartida, Partida
from src.usuarios.jugador import EstadoJugador, Jugador, Rol
from src.usuarios.usuario import Usuario


class ControladorPartida:
    """
    El 'Árbitro' y 'Orquestador' del juego.
    Mantiene el estado de todas las partidas en memoria y procesa las intenciones
    (órdenes) de los jugadores, asegurando que se cumplan las reglas del Core.
    """

    def __init__(self):
        # Diccionario que almacena todas las partidas vivas en el servidor.
        # Clave: ID de la partida (str), Valor: Objeto Partida
        self.partidas_activas: dict[str, Partida] = {}

    # ==========================================
    # 1. GESTIÓN DEL CICLO DE VIDA
    # ==========================================
    def crear_partida(self, nombre: str, creador: Usuario, modo_desarrollo: bool = False) -> Partida:
        """Crea una nueva partida, la registra en el servidor y devuelve el objeto."""
        config = ConfiguracionMapa.modo_desarrollo() if modo_desarrollo else ConfiguracionMapa.modo_produccion()

        partida = Partida(
            nombre=nombre,
            creador_id=creador.id,
            configuracion_mapa=config
        )

        self.partidas_activas[partida.id] = partida
        print(f"🎲 [SERVIDOR] Partida '{nombre}' creada con ID {partida.id[:8]}...")
        return partida

    def unir_jugador(self, partida_id: str, usuario: Usuario, nombre_personaje: str) -> tuple[bool, str, Jugador | None]:
        """Intenta añadir un usuario a una partida existente."""
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, "❌ Partida no encontrada.", None

        if partida.estado != EstadoPartida.LOBBY:
            return False, "❌ La partida ya ha comenzado o está cerrada.", None

        jugador = Jugador(usuario=usuario, partida=partida, nombre_partida=nombre_personaje)
        exito = partida.añadir_jugador(jugador)

        if exito:
            return True, f"✅ {nombre_personaje} se ha unido a la sala.", jugador
        return False, "❌ No se pudo unir a la partida (¿quizás ya estás dentro?).", None

    def iniciar_partida(self, partida_id: str) -> tuple[bool, str]:
        """
        Transiciona la partida a EN_CURSO.
        Aquí es donde el servidor asigna los roles y genera el mundo.
        """
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, "❌ Partida no encontrada."

        exito = partida.iniciar_partida()
        if not exito:
            return False, "❌ No se pudo iniciar (faltan jugadores o no está en lobby)."

        # 🌍 MAGIA DEL MOTOR: Asignación de roles y generación de mundo
        self._distribuir_roles_iniciales(partida)
        # self._generar_mapa(partida) # <-- Futuro: Aquí generaremos los Puntos y Reinos

        for jugador in partida.jugadores:
            jugador.activar()

        return True, f"🎮 ¡La partida '{partida.nombre}' ha comenzado! Turno 1."

    # ==========================================
    # 2. PROCESAMIENTO DE ÓRDENES (El Tick del Jugador)
    # ==========================================
    def procesar_orden(self, partida_id: str, jugador: Jugador, tipo_orden: str, **kwargs) -> tuple[bool, str]:
        """
        Recibe una intención del cliente (vía WebSocket/API) y la valida.
        Devuelve (Éxito, Mensaje).
        """
        partida = self.partidas_activas.get(partida_id)
        if not partida or partida.estado != EstadoPartida.EN_CURSO:
            return False, "❌ No se pueden dar órdenes en este momento."

        if jugador.estado != EstadoJugador.ACTIVO:
            return False, "❌ No puedes dar órdenes (estás eliminado o desconectado)."

        # Enrutador de órdenes (Match/Case)
        if tipo_orden == "mover_faccion":
            destino: Coordenada | None = kwargs.get('destino')
            if not destino:
                return False, "❌ Falta la coordenada de destino."
            return self._validar_y_mover(partida, jugador, destino)

        elif tipo_orden == "recaudar_impuestos":
            return self._recaudar_impuestos(partida, jugador)

        return False, "❌ Orden desconocida o no implementada."

    # ==========================================
    # 3. EL RELOJ DEL SERVIDOR (El Tick Global)
    # ==========================================
    def avanzar_turno(self, partida_id: str) -> tuple[bool, dict]:
        """
        El servidor llama a esto cada 1 minuto (o cuando todos han enviado órdenes).
        Resuelve todo y genera el resumen para enviar a los clientes.
        """
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, {}

        partida.turno_actual += 1

        # Aquí el motor calcularía:
        # 1. Movimientos de tropas y nómadas
        # 2. Resolución de combates
        # 3. Crecimiento de ciudades y economía

        resumen_turno = {
            "turno": partida.turno_actual,
            "eventos": [
                "El sol sale sobre el imperio.",
                "Las tribus nómadas levantan sus campamentos."
            ],
            "jugadores_activos": len([j for j in partida.jugadores if j.estado == EstadoJugador.ACTIVO])
        }

        print(f"⏳ [SERVIDOR] Turno {partida.turno_actual} resuelto para '{partida.nombre}'.")
        return True, resumen_turno

    # ==========================================
    # MÉTODOS PRIVADOS (Lógica Interna)
    # ==========================================
    def _distribuir_roles_iniciales(self, partida: Partida) -> None:
        """Lógica temporal para asignar roles al empezar."""
        if not partida.jugadores:
            return

        for i, jugador in enumerate(partida.jugadores):
            if i == 0:
                jugador.asignar_rol(Rol.EMPERADOR)
            elif i == 1:
                jugador.asignar_rol(Rol.JEFE)
            else:
                jugador.asignar_rol(Rol.SATRAPA)

    def _validar_y_mover(self, partida: Partida, jugador: Jugador, destino: Coordenada) -> tuple[bool, str]:
        """Valida si una facción puede moverse a un lugar."""
        if not partida.mapa.es_coordenada_valida(destino):
            return False, "❌ Destino fuera de los límites del mundo conocido."

        # Futuro: Aquí consultaríamos el diccionario de 'Puntos' del mapa
        # para ver si hay montañas, si es territorio enemigo, etc.

        print(f"👣 [MOTOR] {jugador.nombre_partida} se mueve hacia {destino}.")
        return True, f"✅ Orden de movimiento a {destino} registrada para el final del turno."

    def _recaudar_impuestos(self, partida: Partida, jugador: Jugador) -> tuple[bool, str]:
        """Ejemplo de orden económica."""

        # Garantía para Pylance: "Te aseguro que el rol existe en este punto"
        assert jugador.rol is not None, "Bug crítico: Se intentó recaudar impuestos sin rol asignado."

        if jugador.rol == Rol.SIN_ASIGNAR:
            return False, "❌ No tienes un rol asignado aún."

        if jugador.rol == Rol.JEFE:
            return False, "❌ Los nómadas no recaudan impuestos, ¡saquean!"

        return True, "✅ Impuestos recaudados. Tus arcas se llenan."


# ==========================================
# BLOQUE DE PRUEBAS (Simulando el Servidor)
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas del ControladorPartida ---\n")

    # 1. Instanciar el Motor (Esto lo hará FastAPI al arrancar)
    servidor = ControladorPartida()

    # 2. Crear Usuarios (Simulando peticiones de registro)
    u1 = Usuario("admin_god", "admin@satrapia.com", "Pass1234567!")
    u2 = Usuario("jugador_1", "j1@satrapia.com", "Pass1234567!")
    u3 = Usuario("jugador_2", "j2@satrapia.com", "Pass1234567!")

    # 3. Crear Partida
    print("=== Creando Partida ===")
    partida = servidor.crear_partida("La Caída de Roma", u1, modo_desarrollo=True)

        # 4. Unir Jugadores
    print("\n=== Uniendo Jugadores ===")

    # Jugador 1
    exito1, msg1, j1 = servidor.unir_jugador(partida.id, u1, "César Augusto")
    print(msg1)
    assert j1 is not None, "Error crítico en prueba: j1 no debería ser None"

    # Jugador 2
    exito2, msg2, j2 = servidor.unir_jugador(partida.id, u2, "Atila el Huno")
    print(msg2)
    assert j2 is not None, "Error crítico en prueba: j2 no debería ser None"

    # Jugador 3
    exito3, msg3, j3 = servidor.unir_jugador(partida.id, u3, "Sátrapa de Oriente")
    print(msg3)
    assert j3 is not None, "Error crítico en prueba: j3 no debería ser None"

    # 5. Iniciar Partida
    print("\n=== Iniciando Partida ===")
    exito, msg_inicio = servidor.iniciar_partida(partida.id)
    print(msg_inicio)
    print(f"Roles asignados: {j1.rol.value}, {j2.rol.value}, {j3.rol.value}")

    # 6. Procesar Órdenes (Simulando WebSockets recibiendo datos)
    print("\n=== Procesando Órdenes (Turno 1) ===")
    _, msg_mov = servidor.procesar_orden(
        partida.id, j2, "mover_faccion", destino=Coordenada(50, 50)
    )
    print(f"{j2.nombre_partida}: {msg_mov}")

    _, msg_imp = servidor.procesar_orden(partida.id, j2, "recaudar_impuestos")
    print(f"{j2.nombre_partida}: {msg_imp}") # Debería fallar por ser Jefe

    _, msg_imp2 = servidor.procesar_orden(partida.id, j1, "recaudar_impuestos")
    print(f"{j1.nombre_partida}: {msg_imp2}") # Debería funcionar

    # 7. El Reloj del Servidor avanza el turno
    print("\n=== Avanzando Turno (Tick del Servidor) ===")
    _, resumen = servidor.avanzar_turno(partida.id)
    print(f"Resumen emitido a los clientes: {resumen}")

    print("\n--- Fin de las pruebas ---")
