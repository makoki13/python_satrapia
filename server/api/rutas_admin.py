# server/api/rutas_admin.py
import logging
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.estado import game_controller
from src.core.coordenada import Coordenada
from src.usuarios.usuario import Usuario

logger = logging.getLogger(__name__)

router = APIRouter()


# ==========================================
# MODELOS DE DATOS (Pydantic)
# ==========================================
class CrearPartidaRequest(BaseModel):
    nombre: str
    modo_desarrollo: bool = False


class CrearUsuarioRequest(BaseModel):
    username: str
    email: str
    password: str


class RespuestaPartida(BaseModel):
    id: str
    nombre: str
    estado: str
    jugadores: int
    dimensiones_mapa: str


class ConstruirEdificioRequest(BaseModel):
    partida_id: str
    ciudad_nombre: str
    tipo: str
    coordenada: dict
    capacidad_silo: int = 100


class AvanzarTurnoRequest(BaseModel):
    turnos: int = 1


# ==========================================
# ENDPOINTS DE ADMINISTRACIÓN
# ==========================================
@router.post("/usuarios/crear", response_model=dict)
async def crear_usuario_admin(request: CrearUsuarioRequest):
    """Crea un nuevo usuario en el sistema (solo admin)."""
    try:
        usuario = Usuario(
            username=request.username,
            email=request.email,
            _password_hash=request.password,
        )
        return {
            "exito": True,
            "mensaje": f"Usuario {usuario.username} creado",
            "usuario_id": usuario.id,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None


@router.post("/partidas/crear", response_model=dict)
async def crear_partida(request: CrearPartidaRequest):
    """Crea una nueva partida."""
    usuario_admin = Usuario(
        username="admin",
        email="admin@satrapia.com",
        _password_hash="AdminPass123!",
    )
    partida = game_controller.crear_partida(
        nombre=request.nombre,
        creador=usuario_admin,
        modo_desarrollo=request.modo_desarrollo,
    )
    return {
        "exito": True,
        "mensaje": f"Partida '{partida.nombre}' creada",
        "partida_id": partida.id,
        "dimensiones": f"{partida.mapa.limite_x}x{partida.mapa.limite_y}",
    }


@router.get("/partidas", response_model=list[RespuestaPartida])
async def listar_partidas():
    """Lista todas las partidas activas en el servidor."""
    partidas = []
    for partida in game_controller.partidas_activas.values():
        partidas.append(
            RespuestaPartida(
                id=partida.id,
                nombre=partida.nombre,
                estado=partida.estado.name,
                jugadores=len(partida.jugadores),
                dimensiones_mapa=f"{partida.mapa.limite_x}x{partida.mapa.limite_y}",
            )
        )
    return partidas


@router.post("/partidas/{partida_id}/iniciar")
async def iniciar_partida_admin(partida_id: str):
    """Fuerza el inicio de una partida (solo admin)."""
    exito, mensaje = game_controller.iniciar_partida(partida_id)
    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)
    return {"exito": True, "mensaje": mensaje}


@router.delete("/partidas/{partida_id}")
async def eliminar_partida(partida_id: str):
    """Elimina una partida del servidor (solo admin)."""
    if partida_id in game_controller.partidas_activas:
        del game_controller.partidas_activas[partida_id]
        return {"exito": True, "mensaje": "Partida eliminada"}
    raise HTTPException(status_code=404, detail="Partida no encontrada")


@router.get("/partidas/{partida_id}/jugadores")
async def listar_jugadores_partida(partida_id: str):
    """Lista los jugadores conectados a una partida específica."""
    if partida_id not in game_controller.partidas_activas:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    partida = game_controller.partidas_activas[partida_id]
    jugadores = []
    for jugador in partida.jugadores:
        faccion_nombre = (
            getattr(jugador.faccion, "nombre", "Sin asignar")
            if jugador.faccion
            else "Sin asignar"
        )
        jugadores.append({
            "nombre_personaje": jugador.nombre_partida,
            "username": jugador.usuario.username,
            "rol": jugador.rol.value,
            "estado": jugador.estado.value,
            "faccion": faccion_nombre,
        })
    return {"partida_id": partida_id, "jugadores": jugadores}


@router.post("/partidas/{partida_id}/avanzar_turno", response_model=dict)
async def avanzar_turno_admin(partida_id: str, request: AvanzarTurnoRequest):
    """Avanza uno o más turnos manualmente (solo admin/testing)."""
    if partida_id not in game_controller.partidas_activas:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    resumen_acumulado: dict[str, Any] = {"turnos_avanzados": 0, "eventos": []}

    for _ in range(request.turnos):
        exito, resumen = await game_controller.avanzar_turno(partida_id)
        if not exito:
            break
        resumen_acumulado["turnos_avanzados"] += 1
        resumen_acumulado["eventos"].extend(resumen.get("eventos", []))
        resumen_acumulado["turno_actual"] = resumen.get("turno")

    return {
        "exito": True,
        "mensaje": f"Avanzados {resumen_acumulado['turnos_avanzados']} turno(s)",
        "resumen": resumen_acumulado,
    }


# ==========================================
# ENDPOINTS DE CONSTRUCCIÓN
# ==========================================
@router.post("/edificios/construir", response_model=dict)
async def construir_edificio(request: ConstruirEdificioRequest):  # noqa: C901
    """Construye un edificio productivo en una posición del mapa."""
    if request.partida_id not in game_controller.partidas_activas:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    partida = game_controller.partidas_activas[request.partida_id]

    ciudad = next(
        (c for c in partida.ciudades if c.nombre == request.ciudad_nombre),
        None,
    )
    if not ciudad:
        raise HTTPException(
            status_code=404,
            detail=f"Ciudad '{request.ciudad_nombre}' no encontrada",
        )

    coord = Coordenada(request.coordenada["x"], request.coordenada["y"])

    if request.tipo == "granja":
        from src.economia.edificios.granja import Granja
        from src.territorio.punto import Punto

        granja = Granja.crear(
            nombre=f"Granja de {request.ciudad_nombre}",
            coordenada=coord,
            capacidad_silo=request.capacidad_silo,
        )
        ciudad.granjas.append(granja)

        # ✅ Registrar CORREDOR de puntos alrededor de la ruta granja → capital
        # A* usa 8 direcciones; necesitamos puntos adyacentes para que no falle
        dest_x, dest_y = ciudad.ubicacion.x, ciudad.ubicacion.y

        # Calcular bounding box de la ruta + margen de 1 celda
        min_x = max(0, min(coord.x, dest_x) - 1)
        max_x = min(partida.mapa.limite_x - 1, max(coord.x, dest_x) + 1)
        min_y = max(0, min(coord.y, dest_y) - 1)
        max_y = min(partida.mapa.limite_y - 1, max(coord.y, dest_y) + 1)

        for rx in range(min_x, max_x + 1):
            for ry in range(min_y, max_y + 1):
                c = Coordenada(rx, ry)
                if c not in partida.mapa.puntos:
                    partida.mapa.puntos[c] = Punto(
                        coordenada=c,
                        propietario=ciudad.reino_propietario,
                    )

        # Asegurar que el punto de destino existe con estructura
        if ciudad.ubicacion not in partida.mapa.puntos:
            partida.mapa.puntos[ciudad.ubicacion] = Punto(
                coordenada=ciudad.ubicacion,
                estructura=ciudad,
                propietario=ciudad.reino_propietario,
            )

        # 🔍 DEBUG TEMPORAL: Verificar puntos clave de la ruta
        puntos_clave = []
        check_x, check_y = coord.x, coord.y
        while (check_x, check_y) != (dest_x, dest_y):
            c = Coordenada(check_x, check_y)
            existe = c in partida.mapa.puntos
            transitable = partida.mapa.puntos[c].es_transitable() if existe else False
            puntos_clave.append(f"{c}: ex={existe}, tr={transitable}")
            if check_x < dest_x:
                check_x += 1
            elif check_x > dest_x:
                check_x -= 1
            elif check_y < dest_y:
                check_y += 1
            elif check_y > dest_y:
                check_y -= 1

        logger.info(
            "🗺️ Ruta granja→capital (%d puntos clave): %s",
            len(puntos_clave), puntos_clave,
        )
        logger.info(
            "🗺️ Corredor registrado: (%d,%d) a (%d,%d) = %d puntos",
            min_x, min_y, max_x, max_y,
            (max_x - min_x + 1) * (max_y - min_y + 1),
        )

        return {
            "exito": True,
            "mensaje": f"Granja creada en ({coord.x}, {coord.y})",
            "edificio": "granja",
            "coordenada": {"x": coord.x, "y": coord.y},
            "silo_capacidad": request.capacidad_silo,
            "ciudad": request.ciudad_nombre,
        }

    raise HTTPException(
        status_code=400,
        detail=f"Tipo de edificio '{request.tipo}' no soportado",
    )


# ==========================================
# ENDPOINTS DE MONITORIZACIÓN
# ==========================================
@router.get("/partidas/{partida_id}/estado_detallado")
async def obtener_estado_detallado(partida_id: str):  # noqa: C901
    """Devuelve el estado completo de una partida para el monitor."""
    if partida_id not in game_controller.partidas_activas:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    from src.config.game_config import GameConfig
    config = GameConfig()
    partida = game_controller.partidas_activas[partida_id]

    # Obtener transportes activos con movimientos pendientes
    transportes_activos = []
    if partida.gestor_transportes is not None:
        for transporte in partida.gestor_transportes._por_id.values():
            transportes_activos.append({
                "id": transporte.id,
                "tipo": transporte.tipo.value,
                "origen": str(transporte.origen),
                "destino": str(transporte.destino),
                "recurso": transporte.tipo_recurso.value if transporte.tipo_recurso else None,
                "cantidad": transporte.cantidad,
                "movimientos_pendientes": transporte.waypoints_restantes,
                "progreso_pct": round(transporte.progreso_porcentaje, 1),
                "posicion_actual": str(transporte.posicion_actual),
                "propietario": transporte.propietario_id,
            })

    jugadores_data = []
    for jugador in partida.jugadores:
        ciudades_jugador = []
        faccion = jugador.faccion

        ciudades_faccion = [
            c for c in partida.ciudades
            if c.reino_propietario and hasattr(faccion, "nombre")
            and c.reino_propietario.nombre == faccion.nombre
        ]

        for ciudad in ciudades_faccion:
            ciudad_data: dict[str, Any] = {
                "nombre": ciudad.nombre,
                "poblacion": 0,
                "oro": 0,
                "edificios": {},
            }

            if ciudad.palacio:
                resumen_palacio = ciudad.palacio.resumen(config)
                ciudad_data["poblacion"] = resumen_palacio["poblacion"]["actual"]
                ciudad_data["oro"] = resumen_palacio["oro"]["actual"]
                ciudad_data["edificios"]["palacio"] = resumen_palacio

            if ciudad.almacen:
                ciudad_data["edificios"]["almacen"] = ciudad.almacen.resumen_stock(config)

            if ciudad.granjas:
                granjas_data = []
                for granja in ciudad.granjas:
                    granja_info: dict[str, Any] = {"nombre": granja.nombre}
                    if granja.almacen:
                        granja_info["almacen"] = granja.almacen.resumen_stock(config)
                    granjas_data.append(granja_info)
                ciudad_data["edificios"]["granjas"] = granjas_data

            ciudades_jugador.append(ciudad_data)

        jugadores_data.append({
            "nombre_personaje": jugador.nombre_partida,
            "username": jugador.usuario.username,
            "rol": jugador.rol.value,
            "faccion": getattr(faccion, "nombre", "Sin asignar"),
            "ciudades": ciudades_jugador,
        })

    return {
        "partida_nombre": partida.nombre,
        "turno_actual": partida.turno_actual,
        "estado": partida.estado.name,
        "jugadores": jugadores_data,
        "transportes_activos": transportes_activos,
    }
