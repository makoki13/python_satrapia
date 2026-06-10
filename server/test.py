# server/test.py
import sys
from pathlib import Path
from typing import Any  # Añadir este import al inicio del fichero

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json

import httpx

# ==========================================
# CONFIGURACIÓN DEL CLIENTE
# ==========================================
BASE_URL = "http://localhost:8000"
WS_URL = "ws://localhost:8000/ws"

cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)


def imprimir_respuesta(etiqueta: str, response: httpx.Response) -> dict:
    """Formatea y muestra la respuesta del servidor en consola."""
    datos = response.json() if response.content else {}
    estado = "✅" if response.is_success else "❌"
    print(f"{estado} {etiqueta} [{response.status_code}]")
    print(f"   → {json.dumps(datos, ensure_ascii=False, indent=2)}")
    print()
    return datos


# ==========================================
# OPERACIONES DEL GUION
# ==========================================
def crear_usuario(username: str, email: str, password: str) -> dict:
    """Crea un nuevo usuario mediante POST /admin/usuarios/crear."""
    response = cliente.post("/admin/usuarios/crear", json={
        "username": username,
        "email": email,
        "password": password,
    })
    return imprimir_respuesta(f"Crear usuario '{username}'", response)


def crear_partida(nombre: str, modo_desarrollo: bool = True) -> dict:
    """Crea una nueva partida mediante POST /admin/partidas/crear."""
    response = cliente.post("/admin/partidas/crear", json={
        "nombre": nombre,
        "modo_desarrollo": modo_desarrollo,
    })
    return imprimir_respuesta(f"Crear partida '{nombre}'", response)


# server/test.py (actualizar función crear_jugador)

def crear_jugador(
    partida_id: str,
    username: str,
    email: str,
    password: str,
    nombre_personaje: str,
    rol: str,
    nombre_faccion: str,
    posicion_inicial: dict | None = None,
) -> dict:
    """Crea un jugador con rol y facción asignada."""
    body: dict[str, Any] = {  # ✅ Tipado explícito para aceptar valores mixtos
        "partida_id": partida_id,
        "username": username,
        "email": email,
        "password": password,
        "nombre_personaje": nombre_personaje,
        "rol": rol,
        "nombre_faccion": nombre_faccion,
    }
    if posicion_inicial:
        body["posicion_inicial"] = posicion_inicial  # ✅ Ahora es válido

    response = cliente.post("/jugador/unirse", json=body)
    return imprimir_respuesta(f"Crear jugador '{nombre_personaje}' ({rol})", response)


# ==========================================
# EJECUCIÓN DEL GUION
# ==========================================
# server/test.py (reemplazar bloque __main__)

# server/test.py (actualizar bloque __main__)

if __name__ == "__main__":
    print("=" * 60)
    print("🎮 SATRAPIA - Test E2E: Asignación de Facciones")
    print("=" * 60)
    print()

    # ✅ Tipar explícitamente para que Pylance sepa que son dict[str, Any]
    usuario: dict = crear_usuario(
        username="Admin",
        email="admin@satrapia.com",
        password="TestPass123!",
    )

    partida: dict = crear_partida(
        nombre="Mundo de Prueba",
        modo_desarrollo=True,
    )

    emperador: dict = crear_jugador(
        partida_id=partida["partida_id"],  # ✅ Ahora Pylance sabe que es str
        username="Ciro",
        email="ciro@satrapia.com",
        password="TestPass123!",
        nombre_personaje="Ciro el Grande",
        rol="Emperador",
        nombre_faccion="Imperio Aqueménida",
    )

    satrapa: dict = crear_jugador(
        partida_id=partida["partida_id"],
        username="Dario",
        email="dario@satrapia.com",
        password="TestPass123!",
        nombre_personaje="Darío I",
        rol="Sátrapa",
        nombre_faccion="Satrapía de Bactriana",
    )

    jefe: dict = crear_jugador(
        partida_id=partida["partida_id"],
        username="Atila",
        email="atila@satrapia.com",
        password="TestPass123!",
        nombre_personaje="Atila el Huno",
        rol="Jefe Nómada",
        nombre_faccion="Hijos del Viento",
        posicion_inicial={"x": 80, "y": 80},
    )

    print("\n📋 Verificando estado del servidor...")
    from server.backoffice import mostrar_backoffice
    mostrar_backoffice()

    print("\n✅ Si ves 3 jugadores con sus facciones arriba, todo funciona.")
