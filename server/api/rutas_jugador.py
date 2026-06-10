# server/api/rutas_jugador.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from server.estado import game_controller
from src.core.coordenada import Coordenada
from src.usuarios.jugador import Rol
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
    rol: str  # "Emperador" | "Sátrapa" | "Jefe Nómada"
    nombre_faccion: str | None = None
    posicion_inicial: dict | None = None

    @field_validator("rol")
    @classmethod
    def validar_rol(cls, v: str) -> str:
        roles_validos = {"Emperador", "Sátrapa", "Jefe Nómada"}
        if v not in roles_validos:
            raise ValueError(f"Rol inválido '{v}'. Debe ser uno de: {roles_validos}")
        return v

    @field_validator("nombre_faccion")
    @classmethod
    def validar_nombre_faccion(cls, v: str | None, info) -> str | None:
        rol = info.data.get("rol")
        if rol in ("Emperador", "Sátrapa", "Jefe Nómada") and not v:
            raise ValueError(f"nombre_faccion es obligatorio para rol '{rol}'")
        return v

    @field_validator("posicion_inicial")
    @classmethod
    def validar_posicion_jefe(cls, v: dict | None, info) -> dict | None:
        rol = info.data.get("rol")
        if rol == "Jefe Nómada" and not v:
            raise ValueError("posicion_inicial es obligatoria para rol 'Jefe Nómada'")
        if v and ("x" not in v or "y" not in v):
            raise ValueError("posicion_inicial debe tener 'x' e 'y'")
        return v


class RespuestaJugador(BaseModel):
    exito: bool
    mensaje: str
    jugador_nombre: str
    partida_id: str
    rol: str
    faccion_nombre: str
    faccion_tipo: str  # "Imperio" | "Reino" | "Tribu"
    capital_nombre: str | None = None
    posicion_inicial: dict | None = None


# ==========================================
# LÓGICA DE CREACIÓN DE FACCIONES
# ==========================================
# server/api/rutas_jugador.py (actualizar _crear_faccion_y_capital)

def _crear_faccion_y_capital(
    partida,
    jugador,
    rol_str: str,
    nombre_faccion: str,
    posicion_inicial: dict | None,
) -> dict:
    """
    Crea la entidad política según el rol y la vincula al jugador.
    Coordenadas ajustadas al grid de prueba (0-5 x 0-5).
    """
    from src.economia.edificios.granja import Granja  # noqa: F401
    from src.territorio.ciudad import Ciudad
    from src.territorio.punto import Punto
    from src.territorio.reino import Reino

    rol_enum = Rol(rol_str)
    jugador.asignar_rol(rol_enum)

    if rol_str == "Emperador":
        reino = Reino(nombre=nombre_faccion, es_imperial=True)
        partida.reinos.append(reino)

        # ✅ Capital imperial en (3, 3) - centro del grid de prueba
        coord = Coordenada(3, 3)
        capital = Ciudad(
            nombre=f"Capital de {nombre_faccion}",
            ubicacion=coord,
            reino_propietario=reino,
        )
        capital.almacen.nombre = f"Almacén {capital.nombre}"
        reino.fundar_ciudad(capital)
        partida.ciudades.append(capital)

        partida.mapa.puntos[coord] = Punto(
            coordenada=coord, estructura=capital, propietario=reino
        )

        jugador.asignar_faccion(reino)

        return {
            "faccion_nombre": nombre_faccion,
            "faccion_tipo": "Imperio",
            "capital_nombre": capital.nombre,
            "posicion_inicial": None,
        }

    elif rol_str == "Sátrapa":
        reino = Reino(nombre=nombre_faccion, es_imperial=False)
        partida.reinos.append(reino)

        # ✅ Capital vasalla en (1, 1) - dentro del grid de prueba
        coord = Coordenada(1, 1)
        capital = Ciudad(
            nombre=f"Capital de {nombre_faccion}",
            ubicacion=coord,
            reino_propietario=reino,
        )
        capital.almacen.nombre = f"Almacén {capital.nombre}"
        reino.fundar_ciudad(capital)
        partida.ciudades.append(capital)

        partida.mapa.puntos[coord] = Punto(
            coordenada=coord, estructura=capital, propietario=reino
        )

        jugador.asignar_faccion(reino)

        return {
            "faccion_nombre": nombre_faccion,
            "faccion_tipo": "Reino",
            "capital_nombre": capital.nombre,
            "posicion_inicial": None,
        }

    elif rol_str == "Jefe Nómada":
        assert posicion_inicial is not None, "posicion_inicial es obligatorio para Jefe Nómada"
        coord = Coordenada(posicion_inicial["x"], posicion_inicial["y"])

        try:
            from src.territorio.tribu import Tribu
            tribu = Tribu(nombre=nombre_faccion, ubicacion_actual=coord)
        except ImportError:
            tribu = type("Tribu", (), {
                "nombre": nombre_faccion,
                "ubicacion_actual": coord,
            })()

        partida.mapa.puntos[coord] = Punto(coordenada=coord, propietario=tribu)
        jugador.asignar_faccion(tribu)

        return {
            "faccion_nombre": nombre_faccion,
            "faccion_tipo": "Tribu",
            "capital_nombre": None,
            "posicion_inicial": {"x": coord.x, "y": coord.y},
        }

    raise ValueError(f"Rol no soportado: {rol_str}")

# ==========================================
# ENDPOINTS DE JUGADOR
# ==========================================
@router.post("/unirse", response_model=RespuestaJugador)
async def unirse_a_partida(request: UnirsePartidaRequest):
    """Un usuario se une a una partida y se le asigna facción según su rol."""
    # 1. Crear usuario
    try:
        usuario = Usuario(
            username=request.username,
            email=request.email,
            _password_hash=request.password,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from None

    # 2. Unir jugador a la partida
    exito, mensaje, jugador = game_controller.unir_jugador(
        partida_id=request.partida_id,
        usuario=usuario,
        nombre_personaje=request.nombre_personaje,
    )

    if not exito or jugador is None:
        raise HTTPException(status_code=400, detail=mensaje)

    # 3. Obtener referencia a la partida
    partida = game_controller.partidas_activas.get(request.partida_id)
    if not partida:
        raise HTTPException(
            status_code=404, detail="Partida no encontrada tras unir jugador"
        )

    # 4. Crear facción y capital según rol
    assert request.nombre_faccion is not None, "nombre_faccion es obligatorio"
    try:
        datos_faccion = _crear_faccion_y_capital(
            partida=partida,
            jugador=jugador,
            rol_str=request.rol,
            nombre_faccion=request.nombre_faccion,
            posicion_inicial=request.posicion_inicial,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creando facción: {e}"
        ) from None

    return RespuestaJugador(
        exito=True,
        mensaje=(
            f"{mensaje}. Facción {datos_faccion['faccion_tipo']} "
            f"'{datos_faccion['faccion_nombre']}' asignada."
        ),
        jugador_nombre=jugador.nombre_partida,
        partida_id=request.partida_id,
        rol=request.rol,
        faccion_nombre=datos_faccion["faccion_nombre"],
        faccion_tipo=datos_faccion["faccion_tipo"],
        capital_nombre=datos_faccion.get("capital_nombre"),
        posicion_inicial=datos_faccion.get("posicion_inicial"),
    )


@router.get("/partidas/disponibles")
async def partidas_disponibles():
    """Lista partidas en estado LOBBY (esperando jugadores)."""
    from src.gestion.partida import EstadoPartida

    disponibles = []
    for partida in game_controller.partidas_activas.values():
        if partida.estado == EstadoPartida.LOBBY:
            disponibles.append(
                {
                    "id": partida.id,
                    "nombre": partida.nombre,
                    "jugadores": len(partida.jugadores),
                    "dimensiones": f"{partida.mapa.limite_x}x{partida.mapa.limite_y}",
                }
            )

    return {"partidas": disponibles}
