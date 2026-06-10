# server/test.py
"""
Script de pruebas E2E contra servidor real (server/main.py).
Ejecutar tras: uvicorn server.main:app --host 0.0.0.0 --port 8000 --reload
"""
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json

import httpx

# ==========================================
# CONFIGURACIÓN DEL CLIENTE
# ==========================================
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)


def imprimir_respuesta(etiqueta: str, response: httpx.Response) -> dict[str, Any]:
    """Formatea y muestra la respuesta del servidor en consola."""
    datos: dict[str, Any] = response.json() if response.content else {}
    estado = "✅" if response.is_success else "❌"
    print(f"{estado} {etiqueta} [{response.status_code}]")
    print(f"   → {json.dumps(datos, ensure_ascii=False, indent=2)}")
    print()
    return datos

def iniciar_partida(partida_id: str) -> dict[str, Any]:
    """Inicia una partida (cambia estado LOBBY → EN_CURSO)."""
    response = cliente.post(f"/admin/partidas/{partida_id}/iniciar")
    return imprimir_respuesta("Iniciar partida", response)

# ==========================================
# OPERACIONES DEL GUION
# ==========================================
def crear_usuario(username: str, email: str, password: str) -> dict[str, Any]:
    """Crea un nuevo usuario mediante POST /admin/usuarios/crear."""
    response = cliente.post("/admin/usuarios/crear", json={
        "username": username,
        "email": email,
        "password": password,
    })
    return imprimir_respuesta(f"Crear usuario '{username}'", response)


def crear_partida(nombre: str, modo_desarrollo: bool = True) -> dict[str, Any]:
    """Crea una nueva partida mediante POST /admin/partidas/crear."""
    response = cliente.post("/admin/partidas/crear", json={
        "nombre": nombre,
        "modo_desarrollo": modo_desarrollo,
    })
    return imprimir_respuesta(f"Crear partida '{nombre}'", response)


def crear_jugador(
    partida_id: str,
    username: str,
    email: str,
    password: str,
    nombre_personaje: str,
    rol: str,
    nombre_faccion: str,
    posicion_inicial: dict[str, int] | None = None,
) -> dict[str, Any]:
    """Crea un jugador con rol y facción asignada."""
    body: dict[str, Any] = {
        "partida_id": partida_id,
        "username": username,
        "email": email,
        "password": password,
        "nombre_personaje": nombre_personaje,
        "rol": rol,
        "nombre_faccion": nombre_faccion,
    }
    if posicion_inicial:
        body["posicion_inicial"] = posicion_inicial

    response = cliente.post("/jugador/unirse", json=body)
    return imprimir_respuesta(f"Crear jugador '{nombre_personaje}' ({rol})", response)


def construir_granja(
    partida_id: str,
    ciudad_nombre: str,
    coordenada: dict[str, int],
    capacidad_silo: int = 100,
) -> dict[str, Any]:
    """Construye una granja en una posición del mapa vinculada a una ciudad."""
    response = cliente.post("/admin/edificios/construir", json={
        "partida_id": partida_id,
        "ciudad_nombre": ciudad_nombre,
        "tipo": "granja",
        "coordenada": coordenada,
        "capacidad_silo": capacidad_silo,
    })
    return imprimir_respuesta(
        f"Construir granja en ({coordenada['x']}, {coordenada['y']})",
        response,
    )


def avanzar_turnos(partida_id: str, turnos: int = 1) -> dict[str, Any]:
    """Avanza uno o más turnos para activar producción y disparadores."""
    response = cliente.post(f"/admin/partidas/{partida_id}/avanzar_turno", json={
        "turnos": turnos,
    })
    return imprimir_respuesta(f"Avanzar {turnos} turno(s)", response)


# ==========================================
# EJECUCIÓN DEL GUION
# ==========================================
if __name__ == "__main__":
    print("=" * 60)
    print("🎮 SATRAPIA - Test E2E: Producción + Transporte")
    print("=" * 60)
    print()

    # Paso 1: Crear usuario y partida base
    usuario: dict[str, Any] = crear_usuario(
        username="Admin",
        email="admin@satrapia.com",
        password="TestPass123!",
    )

    partida: dict[str, Any] = crear_partida(
        nombre="Mundo Económico",
        modo_desarrollo=True,
    )

    # Paso 2: Emperador → Capital en (3,3)
    emperador: dict[str, Any] = crear_jugador(
        partida_id=partida["partida_id"],
        username="Ciro",
        email="ciro@satrapia.com",
        password="TestPass123!",
        nombre_personaje="Ciro el Grande",
        rol="Emperador",
        nombre_faccion="Imperio Aqueménida",
    )

    inicio: dict[str, Any] = iniciar_partida(partida["partida_id"])

    # Paso 3: Construir granja en (4,3) - adyacente a capital (3,3)
    # Silo de 50 para que se llene en 5 turnos (producción base = 10/turno)
    granja: dict[str, Any] = construir_granja(
        partida_id=partida["partida_id"],
        ciudad_nombre="Capital de Imperio Aqueménida",
        coordenada={"x": 4, "y": 3},
        capacidad_silo=50,
    )

    # Paso 4: Avanzar turnos hasta que el silo se llene y se dispare transporte
    # Producción 10/turno, silo=50 → lleno en turno 5 → transporte en turno 5-6
    turno: dict[str, Any] = avanzar_turnos(
        partida_id=partida["partida_id"],
        turnos=7,
    )

    # Paso 5: Verificar estado final
    print("\n📋 Estado tras producción y transporte...")
    from server.backoffice import mostrar_backoffice
    mostrar_backoffice()

    print("\n✅ Si ves eventos de 'transporte_automatico_creado' arriba,")
    print("   el ciclo económico completo funciona correctamente.")
