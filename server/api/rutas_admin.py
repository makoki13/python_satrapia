# server/api/rutas_admin.py

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.estado import game_controller
from src.usuarios.usuario import Usuario

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
            _password_hash=request.password
        )
        return {
            "exito": True,
            "mensaje": f"Usuario {usuario.username} creado",
            "usuario_id": usuario.id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

@router.post("/partidas/crear", response_model=dict)
async def crear_partida(request: CrearPartidaRequest):
    """Crea una nueva partida."""
    # Creamos un usuario admin temporal para crear la partida
    usuario_admin = Usuario(username="admin", email="admin@satrapia.com", _password_hash="AdminPass123!")

    partida = game_controller.crear_partida(
        nombre=request.nombre,
        creador=usuario_admin,
        modo_desarrollo=request.modo_desarrollo
    )

    return {
        "exito": True,
        "mensaje": f"Partida '{partida.nombre}' creada",
        "partida_id": partida.id,
        "dimensiones": f"{partida.mapa.limite_x}x{partida.mapa.limite_y}"
    }

@router.get("/partidas", response_model=list[RespuestaPartida])
async def listar_partidas():
    """Lista todas las partidas activas en el servidor."""
    partidas = []
    for partida in game_controller.partidas_activas.values():
        partidas.append(RespuestaPartida(
            id=partida.id,
            nombre=partida.nombre,
            estado=partida.estado.name,
            jugadores=len(partida.jugadores),
            dimensiones_mapa=f"{partida.mapa.limite_x}x{partida.mapa.limite_y}"
        ))
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

# server/api/rutas_admin.py (añadir al final)

# server/api/rutas_admin.py (actualizar listar_jugadores_partida)

@router.get("/partidas/{partida_id}/jugadores")
async def listar_jugadores_partida(partida_id: str):
    if partida_id not in game_controller.partidas_activas:
        raise HTTPException(status_code=404, detail="Partida no encontrada")

    partida = game_controller.partidas_activas[partida_id]
    jugadores = []
    for jugador in partida.jugadores:
        faccion_nombre = getattr(jugador.faccion, "nombre", "Sin asignar") if jugador.faccion else "Sin asignar"
        jugadores.append({
            "nombre_personaje": jugador.nombre_partida,
            "username": jugador.usuario.username,
            "rol": jugador.rol.value,
            "estado": jugador.estado.value,
            "faccion": faccion_nombre,
        })
    return {"partida_id": partida_id, "jugadores": jugadores}
