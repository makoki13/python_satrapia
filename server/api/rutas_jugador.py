# server/api/rutas_jugador.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from server.estado import game_controller
from src.usuarios.usuario import Usuario

router = APIRouter()

# ==========================================
# MODELOS DE DATOS
# ==========================================
class UnirsePartidaRequest(BaseModel):
    partida_id: str
    username: str
    email: str
    password: str
    nombre_personaje: str

# ==========================================
# ENDPOINTS DE JUGADOR
# ==========================================
@router.post("/unirse")
async def unirse_a_partida(request: UnirsePartidaRequest):
    """Un usuario se une a una partida existente."""
    try:
        usuario = Usuario(
            username=request.username,
            email=request.email,
            _password_hash=request.password
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    exito, mensaje, jugador = game_controller.unir_jugador(
        partida_id=request.partida_id,
        usuario=usuario,
        nombre_personaje=request.nombre_personaje
    )

    # 👇 AÑADIMOS "or jugador is None" PARA QUE PYLANCE SEPA QUE A PARTIR DE AQUÍ NO ES NULL
    if not exito or jugador is None:
        raise HTTPException(status_code=400, detail=mensaje)

    return {
        "exito": True,
        "mensaje": mensaje,
        "jugador_nombre": jugador.nombre_partida,  # ✅ Pylance ahora está feliz
        "partida_id": request.partida_id
    }

@router.get("/partidas/disponibles")
async def partidas_disponibles():
    """Lista partidas en estado LOBBY (esperando jugadores)."""
    from src.gestion.partida import EstadoPartida

    disponibles = []
    for partida in game_controller.partidas_activas.values():
        if partida.estado == EstadoPartida.LOBBY:
            disponibles.append({
                "id": partida.id,
                "nombre": partida.nombre,
                "jugadores": len(partida.jugadores),
                "dimensiones": f"{partida.mapa.limite_x}x{partida.mapa.limite_y}"
            })

    return {"partidas": disponibles}
