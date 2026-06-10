# server/backoffice.py
"""
Backoffice en modo texto para inspeccionar el estado del servidor Satrapia.
Uso: python server/backoffice.py
Requiere: uvicorn server.main:app corriendo en localhost:8000
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

BASE_URL = "http://localhost:8000"
cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)


def obtener_partidas() -> list[dict]:
    """Obtiene la lista de partidas activas."""
    resp = cliente.get("/admin/partidas")
    if not resp.is_success:
        print(f"❌ Error obteniendo partidas [{resp.status_code}]")
        return []
    return resp.json()


def obtener_jugadores(partida_id: str) -> list[dict]:
    """Obtiene los jugadores de una partida específica."""
    resp = cliente.get(f"/admin/partidas/{partida_id}/jugadores")
    if not resp.is_success:
        return []
    return resp.json().get("jugadores", [])


def mostrar_backoffice():
    """Renderiza el estado completo del servidor en consola."""
    print()
    print("=" * 65)
    print("🖥️  BACKOFFICE SATRAPIA")
    print("=" * 65)

    partidas = obtener_partidas()

    if not partidas:
        print("\n📭 No hay partidas activas en el servidor.")
        print("=" * 65)
        return

    for p in partidas:
        print(f"\n🎲 Partida: {p['nombre']}")
        print(f"   ID:         {p['id']}")
        print(f"   Estado:     {p['estado']}")
        print(f"   Mapa:       {p['dimensiones_mapa']}")
        print(f"   Jugadores:  {p['jugadores']}")

        jugadores = obtener_jugadores(p["id"])

        # server/backoffice.py (actualizar bloque de tabla)

        if jugadores:
            print(f"   ┌{'─'*20}┬{'─'*15}┬{'─'*12}┬{'─'*10}┬{'─'*18}┐")
            print(f"   │ {'Personaje':<18} │ {'Usuario':<13} │ {'Rol':<10} │ {'Estado':<8} │ {'Facción':<16} │")
            print(f"   ├{'─'*20}┼{'─'*15}┼{'─'*12}┼{'─'*10}┼{'─'*18}┤")
            for j in jugadores:
                print(
                    f"   │ {j['nombre_personaje']:<18} "
                    f"│ {j['username']:<13} "
                    f"│ {j['rol']:<10} "
                    f"│ {j['estado']:<8} "
                    f"│ {j['faccion']:<16} │"
                )
            print(f"   └{'─'*20}┴{'─'*15}┴{'─'*12}┴{'─'*10}┴{'─'*18}┘")
        else:
            print("   👤 Sin jugadores conectados")

    print("\n" + "=" * 65)
    print()


if __name__ == "__main__":
    try:
        mostrar_backoffice()
    except httpx.ConnectError:
        print("\n❌ No se pudo conectar al servidor.")
        print("   Asegúrate de que esté corriendo:")
        print("   uvicorn server.main:app --host 0.0.0.0 --port 8000\n")
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}\n")
