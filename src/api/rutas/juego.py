# src/api/rutas/juego.py
from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect

from src.core.server_tick import ServerTick

if TYPE_CHECKING:
    from src.config.game_config import GameConfig
    from src.gestion.partida import Partida
    from src.investigacion.arbol_investigaciones import ArbolInvestigaciones

router = APIRouter(prefix="/api/v1", tags=["Juego"])

# ==========================================
# DEPENDENCIAS (Inyectar desde app principal)
# ==========================================
def _get_partida(partida_id: str) -> Partida:
    """Obtiene la partida activa. Lanza 404 si no existe."""
    # TODO: Reemplazar con tu gestor de partidas real
    from src.api.dependencias import obtener_partida_activa
    partida = obtener_partida_activa(partida_id)
    if partida is None:
        raise HTTPException(status_code=404, detail=f"Partida '{partida_id}' no encontrada")
    return partida


def _get_reino(partida: Partida, reino_nombre: str):
    """Obtiene un reino por nombre dentro de la partida."""
    for reino in partida.reinos:
        if reino.nombre == reino_nombre:
            return reino
    raise HTTPException(status_code=404, detail=f"Reino '{reino_nombre}' no encontrado en la partida")


def _get_ciudad(partida: Partida, ciudad_nombre: str):
    """Obtiene una ciudad por nombre dentro de la partida."""
    for ciudad in partida.ciudades:
        if ciudad.nombre == ciudad_nombre:
            return ciudad
    raise HTTPException(status_code=404, detail=f"Ciudad '{ciudad_nombre}' no encontrada en la partida")


# ==========================================
# 1. ESTADO DEL REINO (Dashboard Principal)
# ==========================================
@router.get("/partidas/{partida_id}/reinos/{reino_nombre}/estado")
async def get_estado_reino(partida_id: str, reino_nombre: str):
    """
    Resumen completo del reino para el dashboard del jugador.
    Incluye: recursos, laboratorio, ciudades y progreso tecnológico.
    """
    partida = _get_partida(partida_id)
    reino = _get_reino(partida, reino_nombre)

    # Obtener recursos de la capital (almacén principal)
    capital = reino.capital
    recursos_capital = {}
    if capital and hasattr(capital, 'almacen'):
        for tipo_recurso, silo in capital.almacen.silos.items():
            recursos_capital[tipo_recurso.value] = {
                "stock": silo.stock_actual,
                "capacidad": silo.get_capacidad_maxima(),
            }

    # Estado del laboratorio
    lab_estado = None
    if reino.tiene_laboratorio() and reino.laboratorio is not None:
        from src.api.dependencias import ARBOL_GLOBAL
        if ARBOL_GLOBAL is None:
            raise HTTPException(
                status_code=503,
                detail="Árbol de investigaciones no inicializado."
            )

        # ✅ Variable local con tipo explícito → Pylance acepta sin dudas
        lab_estado = reino.laboratorio.resumen(ARBOL_GLOBAL)

    return {
        "reino": reino.nombre,
        "capital": capital.nombre if capital else None,
        "oro": capital.palacio.get_oro() if capital and capital.palacio else 0,
        "poblacion": capital.palacio.get_poblacion() if capital and capital.palacio else 0,
        "recursos": recursos_capital,
        "laboratorio": lab_estado,
        "tecnologias_completadas": len(reino.investigaciones_completadas),
        "progreso_porcentaje": round(reino.get_progreso_investigacion(), 2),
        "turno_actual": partida.turno_actual,
    }


# ==========================================
# 2. GESTIÓN DEL LABORATORIO
# ==========================================
@router.post("/partidas/{partida_id}/reinos/{reino_nombre}/laboratorio/investigar")
async def iniciar_investigacion(
    partida_id: str,
    reino_nombre: str,
    body: dict,  # {"tech_id": "1.1.1_regadio_inundacion"}
):
    """Añade una tecnología a la cola de investigación del laboratorio."""
    partida = _get_partida(partida_id)
    reino = _get_reino(partida, reino_nombre)

    if not reino.tiene_laboratorio() or reino.laboratorio is None:
        raise HTTPException(status_code=400, detail="El reino no tiene laboratorio.")

    tech_id = body.get("tech_id")
    if not tech_id:
        raise HTTPException(status_code=422, detail="Se requiere 'tech_id' en el cuerpo.")

    from src.api.dependencias import ARBOL_GLOBAL, CONFIG_GLOBAL

    # Necesitamos el palacio de la capital para pagar
    capital = reino.capital
    if not capital or not capital.palacio:
        raise HTTPException(status_code=400, detail="La capital no tiene palacio para financiar investigación.")

    if ARBOL_GLOBAL is None or CONFIG_GLOBAL is None:
        raise HTTPException(status_code=503, detail="Servidor no completamente inicializado.")

    exito, mensaje = reino.laboratorio.agregar_investigacion(
        tech_id=tech_id,
        arbol=ARBOL_GLOBAL,
        palacio=capital.palacio,
        config=CONFIG_GLOBAL,
        investigaciones_completadas=reino.investigaciones_completadas,
    )

    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)

    return {"exito": True, "mensaje": mensaje}


@router.delete("/partidas/{partida_id}/reinos/{reino_nombre}/laboratorio/cancelar/{posicion}")
async def cancelar_investigacion(
    partida_id: str,
    reino_nombre: str,
    posicion: int,
):
    """Cancela una investigación de la cola y reembolsa el oro."""
    partida = _get_partida(partida_id)
    reino = _get_reino(partida, reino_nombre)

    if not reino.tiene_laboratorio() or reino.laboratorio is None:
        raise HTTPException(status_code=400, detail="El reino no tiene laboratorio.")

    capital = reino.capital
    if not capital or not capital.palacio:
        raise HTTPException(status_code=400, detail="La capital no tiene palacio para procesar reembolso.")

    from src.api.dependencias import ARBOL_GLOBAL, CONFIG_GLOBAL

    if ARBOL_GLOBAL is None or CONFIG_GLOBAL is None:
        raise HTTPException(status_code=503, detail="Servidor no completamente inicializado.")

    exito, mensaje = reino.laboratorio.cancelar_investigacion(
        posicion=posicion,
        palacio=capital.palacio,
        arbol=ARBOL_GLOBAL,
        config=CONFIG_GLOBAL,
    )

    if not exito:
        raise HTTPException(status_code=400, detail=mensaje)

    return {"exito": True, "mensaje": mensaje}


# ==========================================
# 3. CONSTRUCCIÓN DE EDIFICIOS
# ==========================================
@router.post("/partidas/{partida_id}/ciudades/{ciudad_nombre}/construir")
async def construir_edificio(
    partida_id: str,
    ciudad_nombre: str,
    body: dict,
):
    """Construye un nuevo edificio productivo en la ciudad."""
    partida = _get_partida(partida_id)
    ciudad = _get_ciudad(partida, ciudad_nombre)

    tipo = body.get("tipo")
    if not tipo:
        raise HTTPException(status_code=422, detail="Se requiere 'tipo' de edificio.")

    from src.api.dependencias import CONFIG_GLOBAL

    if CONFIG_GLOBAL is None:
        raise HTTPException(status_code=503, detail="Servidor no completamente inicializado.")

    # ✅ Variable local tipada → Pylance acepta sin dudas
    config: GameConfig = CONFIG_GLOBAL

    puede, mensaje = ciudad.puede_construir(tipo, config)
    if not puede:
        raise HTTPException(status_code=400, detail=mensaje)

    return {
        "exito": True,
        "mensaje": f"✅ Edificio '{tipo}' construido en {ciudad.nombre}.",
        "total_edificios": ciudad.total_edificios_productivos(),
    }


# ==========================================
# 4. TRANSPORTE LOGÍSTICO
# ==========================================
@router.get("/partidas/{partida_id}/transportes")
async def get_transportes_activos(partida_id: str):
    """Lista todos los transportes activos en la partida."""
    partida = _get_partida(partida_id)

    if partida.gestor_transportes is None:
        return {"transportes": [], "total": 0}

    transportes = []
    for t in partida.gestor_transportes._por_id.values():
        transportes.append({
            "id": t.id,
            "tipo": t.tipo.value,
            "origen": str(t.origen),
            "destino": str(t.destino),
            "posicion_actual": str(t.posicion_actual),
            "progreso_porcentaje": round(t.progreso_porcentaje, 1),
            "waypoints_restantes": t.waypoints_restantes,
            "recurso": t.tipo_recurso.value if t.tipo_recurso else None,
            "cantidad": t.cantidad,
            "propietario": t.propietario_id,
        })

    return {
        "transportes": transportes,
        "total": len(transportes),
    }


# ==========================================
# 5. WEBSOCKET: EVENTOS EN TIEMPO REAL
# ==========================================
@router.websocket("/ws/partidas/{partida_id}")
async def websocket_partida(websocket: WebSocket, partida_id: str):
    """
    Conexión WebSocket para recibir eventos del ServerTick en tiempo real.

    Eventos emitidos:
    - tick_completado: Resumen de producción, impuestos, llegadas e investigaciones
    - transporte_llegado: Notificación individual de llegada
    - investigacion_completada: Tech completada con efectos aplicados
    - alerta_fuente_agotada: Fuente de recurso agotada
    """
    await websocket.accept()

    try:
        while True:
            # El cliente puede enviar comandos o simplemente escuchar
            data = await websocket.receive_text()

            # Si el cliente envía "avanzar_turno", ejecutar el tick
            if data == "avanzar_turno":
                partida = _get_partida(partida_id)
                from src.api.dependencias import ARBOL_GLOBAL, CONFIG_GLOBAL

                # ✅ Validar ANTES de instanciar
                if CONFIG_GLOBAL is None or ARBOL_GLOBAL is None:
                    await websocket.send_json({
                        "tipo": "error",
                        "mensaje": "Servidor no completamente inicializado."
                    })
                    continue

                # ✅ Asignar a variables locales tipadas
                config: GameConfig = CONFIG_GLOBAL
                arbol: ArbolInvestigaciones = ARBOL_GLOBAL

                # ✅ Ahora los tipos coinciden con __init__ de ServerTick
                tick = ServerTick(partida, config, arbol)
                resumen = await tick.ejecutar()

                await websocket.send_json({
                    "tipo": "tick_completado",
                    **resumen,
                })

            elif data == "ping":
                await websocket.send_text("pong")

    except WebSocketDisconnect:
        pass  # Cliente desconectado limpiamente
    except Exception as e:
        await websocket.send_json({"tipo": "error", "mensaje": str(e)})
