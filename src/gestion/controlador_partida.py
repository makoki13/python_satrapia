# src/gestion/controlador_partida.py

from src.core.coordenada import Coordenada
from src.gestion.partida import ConfiguracionMapa, EstadoPartida, Partida
from src.territorio.generador_mapas import GeneradorMapas
from src.territorio.reino import Reino
from src.territorio.tribu import Tribu
from src.territorio.zona_disponible import TipoFaccion
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

        # Diccionario paralelo para guardar los generadores de mapas por partida
        # Clave: ID de la partida (str), Valor: Objeto GeneradorMapas
        self.generadores_mapas: dict[str, GeneradorMapas] = {}

    # ==========================================
    # 1. GESTIÓN DEL CICLO DE VIDA
    # ==========================================
    def crear_partida(self, nombre: str, creador: Usuario, modo_desarrollo: bool = False) -> Partida:
        """Crea una nueva partida, genera el mundo y la registra en el servidor."""
        config = ConfiguracionMapa.modo_desarrollo() if modo_desarrollo else ConfiguracionMapa.modo_produccion()

        partida = Partida(
            nombre=nombre,
            creador_id=creador.id,
            configuracion_mapa=config
        )

        # 🌍 GENERACIÓN DEL MUNDO (Nuevo)
        generador = GeneradorMapas(partida.mapa)
        generador.generar_mundo()
        self.generadores_mapas[partida.id] = generador

        self.partidas_activas[partida.id] = partida
        print(f"🎲 [SERVIDOR] Partida '{nombre}' creada con ID {partida.id[:8]}...")
        print(f"🗺️ [SERVIDOR] Mundo generado con {len(generador.zonas_disponibles)} zonas disponibles.")
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

    # src/gestion/controlador_partida.py (actualizar iniciar_partida)

    def iniciar_partida(self, partida_id: str) -> tuple[bool, str]:
        """Transiciona la partida a EN_CURSO."""
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, "❌ Partida no encontrada."

        if partida.estado != EstadoPartida.LOBBY:
            return False, f"❌ La partida no está en lobby (estado actual: {partida.estado.name})."

        # ✅ En modo desarrollo, permitir 1 jugador mínimo
        minimo_jugadores = 1 if partida.configuracion_mapa.modo_desarrollo else 2
        if len(partida.jugadores) < minimo_jugadores:
            return False, f"❌ Faltan jugadores. Hay {len(partida.jugadores)}/{minimo_jugadores}."

        exito = partida.iniciar_partida()
        if not exito:
            return False, "❌ No se pudo iniciar la partida (error interno)."

        # Solo distribuir roles automáticamente si NO fueron asignados por API
        jugadores_sin_rol = [j for j in partida.jugadores if j.rol == Rol.SIN_ASIGNAR]
        if jugadores_sin_rol:
            self._distribuir_roles_y_facciones(partida)

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
    # src/gestion/controlador_partida.py (reemplazar método avanzar_turno existente)

    async def avanzar_turno(self, partida_id: str) -> tuple[bool, dict]:
        """
        Ejecuta un tick completo del ServerTick para la partida.
        Solo funciona si la partida está EN_CURSO.
        """
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, {"error": "Partida no encontrada"}

        if partida.estado != EstadoPartida.EN_CURSO:
            return False, {"error": f"La partida no está en curso (estado: {partida.estado.name})"}

        from src.config.game_config import GameConfig
        from src.core.server_tick import ServerTick
        from src.investigacion.arbol_investigaciones import ArbolInvestigaciones

        config = GameConfig()
        arbol = ArbolInvestigaciones.construir([])

        tick = ServerTick(partida=partida, config=config, arbol=arbol)

        # ✅ Simplemente await directo; FastAPI maneja el loop
        resumen = await tick.ejecutar()

        print(f"⏳ [SERVIDOR] Turno {resumen['turno']} resuelto para '{partida.nombre}'.")
        return True, resumen

    # ==========================================
    # MÉTODOS PRIVADOS (Lógica Interna)
    # ==========================================
    def _distribuir_roles_y_facciones(self, partida: Partida) -> None:
        """
        Asigna roles a los jugadores, les asigna zonas del mapa y crea sus facciones.
        """
        if not partida.jugadores:
            return

        generador = self.generadores_mapas.get(partida.id)
        if not generador:
            print("❌ Error: No se encontró el generador de mapas para esta partida.")
            return

        # Lógica temporal: asignar roles en orden
        roles_disponibles = [Rol.EMPERADOR, Rol.JEFE, Rol.SATRAPA, Rol.SATRAPA, Rol.SATRAPA]

        for i, jugador in enumerate(partida.jugadores):
            if i < len(roles_disponibles):
                rol = roles_disponibles[i]
                jugador.asignar_rol(rol)

                # 🏰 CREACIÓN DE FACCIÓN (Nuevo)
                self._crear_faccion_para_jugador(partida, jugador, generador)
            else:
                # Si hay más jugadores que roles definidos, los dejamos sin asignar
                pass

    def _crear_faccion_para_jugador(self, partida: Partida, jugador: Jugador, generador: GeneradorMapas) -> None:
        """
        Crea el Reino o Tribu del jugador y lo vincula con su zona del mapa.
        """
        # Pedir al generador una zona adecuada para el rol del jugador
        zona = generador.asignar_zona_a_jugador(jugador.rol)

        if not zona:
            print(f"⚠️ No se pudo asignar zona a {jugador.nombre_partida}")
            return

        # Crear la facción según el tipo
        if zona.tipo_faccion == TipoFaccion.TRIBU:
            # Crear Tribu nómada
            tribu = Tribu(
                nombre=f"Tribu de {jugador.nombre_partida}",
                ubicacion_actual=zona.coordenada_central
            )
            jugador.asignar_faccion(tribu)
            print(f"🏕️ Creada {tribu} para {jugador.nombre_partida}")

        else:
            # Crear Reino (Imperio o Satrapía)
            es_imperial = (zona.tipo_faccion == TipoFaccion.IMPERIO)
            reino = Reino(
                nombre=f"Reino de {jugador.nombre_partida}",
                es_imperial=es_imperial
            )
            jugador.asignar_faccion(reino)

            # Asignar los puntos del mapa alrededor de la zona al reino
            self._asignar_territorio_inicial(partida, reino, zona)
            print(f"🏰 Creado {reino} para {jugador.nombre_partida} con {len(reino.puntos_controlados)} puntos")

    def _asignar_territorio_inicial(self, partida: Partida, reino: Reino, zona) -> None:
        """
        Asigna los puntos del mapa dentro del radio de la zona al reino.
        """
        centro = zona.coordenada_central
        radio = zona.radio

        for x in range(centro.x - radio, centro.x + radio + 1):
            for y in range(centro.y - radio, centro.y + radio + 1):
                # Calcular distancia al centro
                dx = x - centro.x
                dy = y - centro.y
                distancia = (dx**2 + dy**2)**0.5

                # Solo asignar puntos dentro del radio
                if distancia <= radio:
                    punto = partida.mapa.puntos.get(Coordenada(x, y))
                    if punto and punto.es_tierra() and not punto.tiene_propietario():
                        reino.agregar_punto(punto)

    def _validar_y_mover(self, partida: Partida, jugador: Jugador, destino: Coordenada) -> tuple[bool, str]:
        """Valida si una facción puede moverse a un lugar."""
        # Verificar que el jugador tiene facción asignada
        if jugador.faccion is None:
            return False, "❌ No tienes una facción asignada aún."

        if not partida.mapa.es_coordenada_valida(destino):
            return False, "❌ Destino fuera de los límites del mundo conocido."

        # Futuro: Aquí consultaríamos el diccionario de 'Puntos' del mapa
        # para ver si hay montañas, si es territorio enemigo, etc.

        print(f"👣 [MOTOR] {jugador.nombre_partida} se mueve hacia {destino}.")
        return True, f"✅ Orden de movimiento a {destino} registrada para el final del turno."

    def _recaudar_impuestos(self, partida: Partida, jugador: Jugador) -> tuple[bool, str]:
        """Ejemplo de orden económica."""
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
    u1 = Usuario(username="admin_god", email="admin@satrapia.com", _password_hash="Pass1234567!")
    u2 = Usuario(username="jugador_1", email="j1@satrapia.com", _password_hash="Pass1234567!")
    u3 = Usuario(username="jugador_2", email="j2@satrapia.com", _password_hash="Pass1234567!")

    # 3. Crear Partida (ahora genera el mundo automáticamente)
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

    # 5. Iniciar Partida (ahora asigna roles, zonas y crea facciones)
    print("\n=== Iniciando Partida ===")
    exito, msg_inicio = servidor.iniciar_partida(partida.id)
    print(msg_inicio)
    print(f"Roles asignados: {j1.rol.value}, {j2.rol.value}, {j3.rol.value}")

    # Mostrar las facciones creadas
    print("\nFacciones creadas:")
    print(f"   {j1.nombre_partida}: {j1.faccion}")
    print(f"   {j2.nombre_partida}: {j2.faccion}")
    print(f"   {j3.nombre_partida}: {j3.faccion}")

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
    import asyncio
    _, resumen = asyncio.run(servidor.avanzar_turno(partida.id))
    print(f"Resumen emitido a los clientes: {resumen}")

    print("\n--- Fin de las pruebas ---")
