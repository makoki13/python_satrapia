# src/gestion/controlador_partida.py
from __future__ import annotations

from src.core.coordenada import Coordenada
from src.gestion.partida import ConfiguracionMapa, EstadoPartida, Partida
from src.territorio.ciudad import Ciudad
from src.territorio.faccion import TipoFaccion
from src.territorio.punto import Punto
from src.territorio.reino import Reino
from src.territorio.tribu import Tribu
from src.usuarios.jugador import EstadoJugador, Jugador, Rol
from src.usuarios.usuario import Usuario

# ==========================================
# MAPEO ROL → TIPO FACCIÓN
# ==========================================
_ROL_A_TIPO_FACCION: dict[Rol, TipoFaccion] = {
    Rol.EMPERADOR: TipoFaccion.IMPERIO,
    Rol.SATRAPA: TipoFaccion.SATRAPIA,
    Rol.JEFE: TipoFaccion.TRIBU,
}


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
    def crear_partida(
        self, nombre: str, creador: Usuario, modo_desarrollo: bool = False
    ) -> Partida:
        """Crea una nueva partida y la registra en el servidor."""
        config = (
            ConfiguracionMapa.modo_desarrollo()
            if modo_desarrollo
            else ConfiguracionMapa.modo_produccion()
        )

        partida = Partida(
            nombre=nombre,
            creador_id=creador.id,
            configuracion_mapa=config,
        )

        # ✅ El GestorZonas ya se inicializa automáticamente en Partida.__post_init__
        self.partidas_activas[partida.id] = partida

        print(f"🎲 [SERVIDOR] Partida '{nombre}' creada con ID {partida.id[:8]}...")
        print(f"🗺️ [SERVIDOR] {partida.gestor_zonas}")
        return partida

    def unir_jugador(
        self, partida_id: str, usuario: Usuario, nombre_personaje: str
    ) -> tuple[bool, str, Jugador | None]:
        """Intenta añadir un usuario a una partida existente."""
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, "❌ Partida no encontrada.", None

        if partida.estado != EstadoPartida.LOBBY:
            return False, "❌ La partida ya ha comenzado o está cerrada.", None

        jugador = Jugador(
            usuario=usuario, partida=partida, nombre_partida=nombre_personaje
        )
        exito = partida.añadir_jugador(jugador)

        if exito:
            return True, f"✅ {nombre_personaje} se ha unido a la sala.", jugador
        return (
            False,
            "❌ No se pudo unir a la partida (¿quizás ya estás dentro?).",
            None,
        )

    def iniciar_partida(self, partida_id: str) -> tuple[bool, str]:
        """Transiciona la partida a EN_CURSO."""
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, "❌ Partida no encontrada."

        if partida.estado != EstadoPartida.LOBBY:
            return False, (
                f"❌ La partida no está en lobby (estado actual: {partida.estado.name})."
            )

        # ✅ Determinar modo usando max_x (no modo_desarrollo, que no existe)
        es_desarrollo = partida.configuracion_mapa.max_x < 500
        minimo_jugadores = 1 if es_desarrollo else 2

        if len(partida.jugadores) < minimo_jugadores:
            return False, (
                f"❌ Faltan jugadores. Hay {len(partida.jugadores)}/{minimo_jugadores}."
            )

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
    def procesar_orden(
        self, partida_id: str, jugador: Jugador, tipo_orden: str, **kwargs
    ) -> tuple[bool, str]:
        """
        Recibe una intención del cliente (vía WebSocket/API) y la valida.
        Devuelve (Éxito, Mensaje).
        """
        partida = self.partidas_activas.get(partida_id)
        if not partida or partida.estado != EstadoPartida.EN_CURSO:
            return False, "❌ No se pueden dar órdenes en este momento."

        if jugador.estado != EstadoJugador.ACTIVO:
            return False, "❌ No puedes dar órdenes (estás eliminado o desconectado)."

        if tipo_orden == "mover_faccion":
            destino: Coordenada | None = kwargs.get("destino")
            if not destino:
                return False, "❌ Falta la coordenada de destino."
            return self._validar_y_mover(partida, jugador, destino)

        elif tipo_orden == "recaudar_impuestos":
            return self._recaudar_impuestos(partida, jugador)

        return False, "❌ Orden desconocida o no implementada."

    # ==========================================
    # 3. EL RELOJ DEL SERVIDOR (El Tick Global)
    # ==========================================
    async def avanzar_turno(self, partida_id: str) -> tuple[bool, dict]:
        """
        Ejecuta un tick completo del ServerTick para la partida.
        Solo funciona si la partida está EN_CURSO.
        """
        partida = self.partidas_activas.get(partida_id)
        if not partida:
            return False, {"error": "Partida no encontrada"}

        if partida.estado != EstadoPartida.EN_CURSO:
            return False, {
                "error": f"La partida no está en curso (estado: {partida.estado.name})"
            }

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
        Usa el GestorZonas de la partida (unificado con rutas_jugador.py).
        """
        if not partida.jugadores:
            return

        # Lógica temporal: asignar roles en orden
        roles_disponibles = [
            Rol.EMPERADOR,
            Rol.JEFE,
            Rol.SATRAPA,
            Rol.SATRAPA,
            Rol.SATRAPA,
        ]

        for i, jugador in enumerate(partida.jugadores):
            if i < len(roles_disponibles):
                rol = roles_disponibles[i]
                jugador.asignar_rol(rol)

                # 🏰 CREACIÓN DE FACCIÓN usando GestorZonas unificado
                self._crear_faccion_para_jugador(partida, jugador)
            # Si hay más jugadores que roles, los dejamos sin asignar

    def _crear_faccion_para_jugador(self, partida: Partida, jugador: Jugador) -> None:
        """
        Crea el Reino o Tribu del jugador usando el GestorZonas de la partida.
        Unifica el camino con rutas_jugador.py (una sola fuente de verdad).
        """
        tipo_faccion = _ROL_A_TIPO_FACCION.get(jugador.rol)
        if tipo_faccion is None:
            print(f"⚠️ Rol {jugador.rol} no tiene tipo de facción mapeado")
            return

        # ✅ Pedir zona al GestorZonas de la partida (igual que rutas_jugador.py)
        zona = partida.gestor_zonas.asignar_zona(tipo_faccion)
        if zona is None:
            print(f"⚠️ No hay zonas {tipo_faccion.value} libres para {jugador.nombre_partida}")
            return

        coord_centro = zona.coordenada_central

        if tipo_faccion == TipoFaccion.TRIBU:
            # Crear Tribu nómada
            tribu = Tribu(
                nombre=f"Tribu de {jugador.nombre_partida}",
                ubicacion_actual=coord_centro,
            )
            jugador.asignar_faccion(tribu)

            # Registrar punto en el mapa
            punto = Punto(coordenada=coord_centro, propietario=tribu)
            partida.mapa.registrar_punto(punto, sobrescribir=True)

            print(f"🏕️ Creada {tribu} para {jugador.nombre_partida} en {coord_centro}")

        else:
            # Crear Reino (Imperio o Satrapía)
            es_imperial = tipo_faccion == TipoFaccion.IMPERIO
            reino = Reino(
                nombre=f"Reino de {jugador.nombre_partida}",
                es_imperial=es_imperial,
            )
            jugador.asignar_faccion(reino)
            partida.reinos.append(reino)

            # Crear capital en el centro de la zona
            capital = Ciudad(
                nombre=f"Capital de {reino.nombre}",
                ubicacion=coord_centro,
                reino_propietario=reino,
            )
            capital.tiene_castillo = True
            if es_imperial:
                from src.economia.edificios.palacio import Palacio
                capital.palacio = Palacio(nombre=f"Palacio Imperial de {reino.nombre}")
                capital.tiene_palacio = True

            reino.fundar_ciudad(capital)
            partida.ciudades.append(capital)

            # Registrar punto en el mapa
            punto = Punto(
                coordenada=coord_centro, estructura=capital, propietario=reino
            )
            partida.mapa.registrar_punto(punto, sobrescribir=True)

            # Asignar territorio circundante
            self._asignar_territorio_inicial(partida, reino, zona)
            print(
                f"🏰 Creado {reino} para {jugador.nombre_partida} "
                f"en {coord_centro} con {len(reino.puntos_controlados)} puntos"
            )

    def _asignar_territorio_inicial(self, partida: Partida, reino: Reino, zona) -> None:
        """
        Asigna los puntos del mapa dentro del radio de la zona al reino.
        Usa la misma métrica (Manhattan) que ZonaDisponible.contiene().
        """

        # ✅ Bounding box para iterar solo puntos potencialmente dentro
        min_coord, max_coord = zona.bounding_box

        for x in range(min_coord.x, max_coord.x + 1):
            for y in range(min_coord.y, max_coord.y + 1):
                coord = Coordenada(x, y)

                # ✅ Usar el mismo criterio que ZonaDisponible.contiene (Manhattan)
                if not zona.contiene(coord):
                    continue

                # ✅ Usar método seguro obtener_punto (no acceso directo al dict)
                punto = partida.mapa.obtener_punto(coord)
                if punto is None:
                    continue

                # ✅ Propiedades sin paréntesis (refactorizadas en punto.py)
                if punto.es_tierra and not punto.tiene_propietario:
                    reino.agregar_punto(punto)

    def _validar_y_mover(
        self, partida: Partida, jugador: Jugador, destino: Coordenada
    ) -> tuple[bool, str]:
        """Valida si una facción puede moverse a un lugar."""
        if jugador.faccion is None:
            return False, "❌ No tienes una facción asignada aún."

        if not partida.mapa.es_coordenada_valida(destino):
            return False, "❌ Destino fuera de los límites del mundo conocido."

        print(f"👣 [MOTOR] {jugador.nombre_partida} se mueve hacia {destino}.")
        return True, f"✅ Orden de movimiento a {destino} registrada para el final del turno."

    def _recaudar_impuestos(
        self, partida: Partida, jugador: Jugador
    ) -> tuple[bool, str]:
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

    servidor = ControladorPartida()

    u1 = Usuario(
        username="admin_god",
        email="admin@satrapia.com",
        _password_hash="Pass1234567!",
    )
    u2 = Usuario(
        username="jugador_1",
        email="j1@satrapia.com",
        _password_hash="Pass1234567!",
    )
    u3 = Usuario(
        username="jugador_2",
        email="j2@satrapia.com",
        _password_hash="Pass1234567!",
    )

    print("=== Creando Partida ===")
    partida = servidor.crear_partida("La Caída de Roma", u1, modo_desarrollo=True)

    print("\n=== Uniendo Jugadores ===")
    _, msg1, j1 = servidor.unir_jugador(partida.id, u1, "César Augusto")
    print(msg1)
    assert j1 is not None

    _, msg2, j2 = servidor.unir_jugador(partida.id, u2, "Atila el Huno")
    print(msg2)
    assert j2 is not None

    _, msg3, j3 = servidor.unir_jugador(partida.id, u3, "Sátrapa de Oriente")
    print(msg3)
    assert j3 is not None

    print("\n=== Iniciando Partida ===")
    exito, msg_inicio = servidor.iniciar_partida(partida.id)
    print(msg_inicio)
    print(f"Roles asignados: {j1.rol.value}, {j2.rol.value}, {j3.rol.value}")

    print("\nFacciones creadas:")
    print(f"   {j1.nombre_partida}: {j1.faccion}")
    print(f"   {j2.nombre_partida}: {j2.faccion}")
    print(f"   {j3.nombre_partida}: {j3.faccion}")

    print("\nEstado del GestorZonas:")
    print(partida.gestor_zonas.resumen())

    print("\n=== Procesando Órdenes (Turno 1) ===")
    _, msg_mov = servidor.procesar_orden(
        partida.id, j2, "mover_faccion", destino=Coordenada(50, 50)
    )
    print(f"{j2.nombre_partida}: {msg_mov}")

    _, msg_imp = servidor.procesar_orden(partida.id, j2, "recaudar_impuestos")
    print(f"{j2.nombre_partida}: {msg_imp}")  # Debería fallar por ser Jefe

    _, msg_imp2 = servidor.procesar_orden(partida.id, j1, "recaudar_impuestos")
    print(f"{j1.nombre_partida}: {msg_imp2}")  # Debería funcionar

    print("\n=== Avanzando Turno (Tick del Servidor) ===")
    import asyncio
    _, resumen = asyncio.run(servidor.avanzar_turno(partida.id))
    print(f"Resumen emitido a los clientes: {resumen}")

    print("\n--- Fin de las pruebas ---")
