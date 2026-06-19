# client/core/api_client.py
"""
Cliente HTTP para comunicarse con el backend Satrapia.

Usa httpx async para no bloquear la UI de Qt.
Todas las llamadas actualizan el GameState automáticamente.

Uso:
    from client.core.api_client import api_client

    # Verificar conexión
    conectado = await api_client.verificar_conexion()

    # Listar partidas disponibles
    partidas = await api_client.listar_partidas_disponibles()

    # Unirse como Emperador
    jugador = await api_client.unirse_partida(
        partida_id="abc-123",
        username="ciro",
        email="ciro@test.com",
        password="TestPass123!",
        nombre_personaje="Ciro el Grande",
        rol="Emperador",
        nombre_faccion="Imperio Aqueménida"
    )
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from client.core.game_state import game_state

logger = logging.getLogger(__name__)


class ApiClient:
    """
    Cliente HTTP para el backend Satrapia.

    Todas las llamadas son async y manejan errores gracefully,
    actualizando el GameState y emitiendo señales de error si falla.
    """

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.timeout = 10.0

    # ==========================================
    # CONEXIÓN
    # ==========================================
    async def verificar_conexion(self) -> bool:
        """
        Verifica si el servidor está activo.

        Returns:
            True si el servidor responde, False en caso contrario.
        """
        game_state.set_conexion("conectando")

        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=2.0) as client:
                resp = await client.get("/health")
                if resp.is_success:
                    game_state.set_conexion("conectado")
                    logger.info("✅ Conexión establecida con %s", self.base_url)
                    return True
                else:
                    game_state.set_conexion("desconectado")
                    game_state.reportar_error(f"Servidor respondió {resp.status_code}")
                    return False
        except (httpx.ConnectError, httpx.ReadTimeout, httpx.RequestError) as e:
            game_state.set_conexion("desconectado")
            game_state.reportar_error(f"No se pudo conectar: {e}")
            logger.warning("❌ Error de conexión: %s", e)
            return False

    # ==========================================
    # PARTIDAS
    # ==========================================
    async def crear_partida(self, nombre: str, modo_desarrollo: bool = False) -> dict[str, Any] | None:
        """
        Crea una nueva partida (solo admin).

        Returns:
            Diccionario con datos de la partida o None si falla.
        """
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                resp = await client.post("/admin/partidas/crear", json={
                    "nombre": nombre,
                    "modo_desarrollo": modo_desarrollo,
                })

                if resp.is_success:
                    datos = resp.json()
                    logger.info("✅ Partida creada: %s", datos["partida_id"])
                    return datos
                else:
                    error_msg = f"Error creando partida: {resp.text}"
                    game_state.reportar_error(error_msg)
                    logger.error(error_msg)
                    return None
        except Exception as e:
            error_msg = f"Excepción creando partida: {e}"
            game_state.reportar_error(error_msg)
            logger.exception(error_msg)
            return None

    async def listar_partidas(self) -> list[dict[str, Any]]:
        """Lista todas las partidas activas (cualquier estado)."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                resp = await client.get("/admin/partidas")
                if resp.is_success:
                    return resp.json()
                return []
        except Exception as e:
            logger.warning("Error listando partidas: %s", e)
            return []

    async def listar_partidas_disponibles(self) -> list[dict[str, Any]]:
        """
        Lista partidas en estado LOBBY (disponibles para unirse).

        Returns:
            Lista de partidas con formato:
            [
                {
                    "id": "abc-123",
                    "nombre": "Mundo de Pruebas",
                    "jugadores": 0,
                    "dimensiones": "200x200"
                },
                ...
            ]
        """
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                resp = await client.get("/jugador/partidas/disponibles")
                if resp.is_success:
                    datos = resp.json()
                    return datos.get("partidas", [])
                logger.warning("Error listando partidas disponibles: %s", resp.text)
                return []
        except Exception as e:
            logger.warning("Excepción listando partidas disponibles: %s", e)
            return []

    async def unirse_partida(
        self,
        partida_id: str,
        username: str,
        email: str,
        password: str,
        nombre_personaje: str,
        rol: str,
        nombre_faccion: str,
        posicion_inicial: dict[str, int] | None = None,
    ) -> dict[str, Any] | None:
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                payload: dict[str, str | dict[str, int]] = {
                    "partida_id": partida_id,
                    "username": username,
                    "email": email,
                    "password": password,
                    "nombre_personaje": nombre_personaje,
                    "rol": rol,
                    "nombre_faccion": nombre_faccion,
                }
                if posicion_inicial is not None:
                    payload["posicion_inicial"] = posicion_inicial

                resp = await client.post("/jugador/unirse", json=payload)

                if resp.is_success:
                    datos = resp.json()

                    # ✅ Obtener dimensiones reales desde la lista de partidas
                    dimensiones_mapa = "200x200"  # Default
                    partidas_resp = await client.get("/admin/partidas")
                    if partidas_resp.is_success:
                        for p in partidas_resp.json():
                            if p["id"] == partida_id:
                                dimensiones_mapa = p.get("dimensiones_mapa", "200x200")
                                break

                    game_state.set_partida({
                        "id": partida_id,
                        "dimensiones_mapa": dimensiones_mapa,
                    })
                    game_state.set_jugador(datos)

                    # ✅ Guardar también username (no viene en la respuesta del servidor)
                    game_state.username = username

                    logger.info("✅ Jugador unido: %s (%s)", datos["jugador_nombre"], datos["rol"])
                    return datos
                else:
                    error_msg = f"Error uniéndose: {resp.text}"
                    game_state.reportar_error(error_msg)
                    logger.error(error_msg)
                    return None
        except Exception as e:
            error_msg = f"Excepción uniéndose: {e}"
            game_state.reportar_error(error_msg)
            logger.exception(error_msg)
            return None

    async def iniciar_partida(self, partida_id: str) -> bool:
        """Inicia una partida (LOBBY → EN_CURSO)."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                resp = await client.post(f"/admin/partidas/{partida_id}/iniciar")
                if resp.is_success:
                    logger.info("✅ Partida iniciada: %s", partida_id)
                    return True
                else:
                    game_state.reportar_error(f"Error iniciando: {resp.text}")
                    return False
        except Exception as e:
            game_state.reportar_error(f"Excepción iniciando: {e}")
            return False

    async def avanzar_turno(self, partida_id: str, turnos: int = 1) -> dict[str, Any] | None:
        """Avanza uno o más turnos."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
                resp = await client.post(
                    f"/admin/partidas/{partida_id}/avanzar_turno",
                    json={"turnos": turnos},
                )
                if resp.is_success:
                    datos = resp.json()
                    turno_actual = datos.get("resumen", {}).get("turno_actual", 0)
                    game_state.set_turno(turno_actual)
                    logger.info("✅ Turno avanzado: %d", turno_actual)
                    return datos
                else:
                    game_state.reportar_error(f"Error avanzando turno: {resp.text}")
                    return None
        except Exception as e:
            game_state.reportar_error(f"Excepción avanzando turno: {e}")
            return None

    # ==========================================
    # CONSTRUCCIÓN
    # ==========================================
    async def construir_edificio(
        self,
        partida_id: str,
        ciudad_nombre: str,
        tipo: str,
        coordenada: dict[str, int],
        capacidad_silo: int = 100,
    ) -> dict[str, Any] | None:
        """Construye un edificio (granja, serrería, etc.)."""
        try:
            async with httpx.AsyncClient(base_url=self.base_url, timeout=self.timeout) as client:
                resp = await client.post("/admin/edificios/construir", json={
                    "partida_id": partida_id,
                    "ciudad_nombre": ciudad_nombre,
                    "tipo": tipo,
                    "coordenada": coordenada,
                    "capacidad_silo": capacidad_silo,
                })
                if resp.is_success:
                    datos = resp.json()
                    logger.info("✅ Edificio construido: %s en %s", tipo, coordenada)
                    return datos
                else:
                    game_state.reportar_error(f"Error construyendo: {resp.text}")
                    return None
        except Exception as e:
            game_state.reportar_error(f"Excepción construyendo: {e}")
            return None


# ==========================================
# INSTANCIA GLOBAL
# ==========================================
api_client = ApiClient(base_url=game_state.servidor_url)
