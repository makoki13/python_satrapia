# server/test.py
"""
Script unificado: Test E2E + Monitor en tiempo real.
Ejecuta el guion completo de pruebas y lanza automáticamente el monitor.
Uso: python server/test.py [--solo-monitor <partida_id>]
"""

import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import json

import httpx

# ==========================================
# CONFIGURACIÓN DEL CLIENTE
# ==========================================
BASE_URL = "http://localhost:8000"

cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)


def imprimir_respuesta(etiqueta: str, response: httpx.Response) -> dict[str, Any]:
    """Formatea y muestra la respuesta del servidor en consola."""
    datos: dict[str, Any] = response.json() if response.content else {}
    estado = "✅" if response.is_success else "❌"
    print(f"{estado} {etiqueta} [{response.status_code}]")
    print(f"   → {json.dumps(datos, ensure_ascii=False, indent=2)}")
    print()
    return datos


# ==========================================
# OPERACIONES DEL GUION E2E
# ==========================================
def crear_usuario(username: str, email: str, password: str) -> dict[str, Any]:
    response = cliente.post(
        "/admin/usuarios/crear",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )
    return imprimir_respuesta(f"Crear usuario '{username}'", response)


def crear_partida(nombre: str, modo_desarrollo: bool = True) -> dict[str, Any]:
    response = cliente.post(
        "/admin/partidas/crear",
        json={
            "nombre": nombre,
            "modo_desarrollo": modo_desarrollo,
        },
    )
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


def iniciar_partida(partida_id: str) -> dict[str, Any]:
    response = cliente.post(f"/admin/partidas/{partida_id}/iniciar")
    return imprimir_respuesta("Iniciar partida", response)


def construir_granja(
    partida_id: str,
    ciudad_nombre: str,
    coordenada: dict[str, int],
    capacidad_silo: int = 100,
) -> dict[str, Any]:
    response = cliente.post(
        "/admin/edificios/construir",
        json={
            "partida_id": partida_id,
            "ciudad_nombre": ciudad_nombre,
            "tipo": "granja",
            "coordenada": coordenada,
            "capacidad_silo": capacidad_silo,
        },
    )
    return imprimir_respuesta(
        f"Construir granja en ({coordenada['x']}, {coordenada['y']})",
        response,
    )

# server/test.py (añadir función tras construir_granja)

def construir_serreria(
    partida_id: str, ciudad_nombre: str,
    coordenada: dict[str, int], capacidad_silo: int = 100,
) -> dict[str, Any]:
    response = cliente.post("/admin/edificios/construir", json={
        "partida_id": partida_id, "ciudad_nombre": ciudad_nombre,
        "tipo": "serreria", "coordenada": coordenada,
        "capacidad_silo": capacidad_silo,
    })
    return imprimir_respuesta(
        f"Construir serrería en ({coordenada['x']}, {coordenada['y']})", response,
    )


def avanzar_turnos(partida_id: str, turnos: int = 1) -> dict[str, Any]:
    response = cliente.post(
        f"/admin/partidas/{partida_id}/avanzar_turno",
        json={
            "turnos": turnos,
        },
    )
    return imprimir_respuesta(f"Avanzar {turnos} turno(s)", response)


# ==========================================
# MONITOR EN TIEMPO REAL
# ==========================================
def limpiar_consola():
    os.system("cls" if os.name == "nt" else "clear")


def formatear_almacen(stock: dict) -> list[str]:
    lineas = []
    for recurso, datos in stock.items():
        cap = datos["capacidad"]
        cap_str = "∞" if cap == -1 else str(cap)
        lineas.append(f"            - {recurso}: {datos['stock']} / {cap_str}")
    return lineas


def renderizar_monitor(datos: dict) -> str:  # noqa: C901
    """Convierte el JSON de estado en texto formateado para consola."""
    lineas = [
        "=" * 75,
        f"🏛️  SATRAPIA MONITOR | {datos['partida_nombre']} | Turno: {datos['turno_actual']} | Estado: {datos['estado']}",
        "=" * 75,
    ]

    for jugador in datos["jugadores"]:
        lineas.append(
            f"\n👤 Jugador: {jugador['nombre_personaje']} ({jugador['username']})"
        )
        lineas.append(f"   Rol: {jugador['rol']} | Facción: {jugador['faccion']}")

        if not jugador["ciudades"]:
            lineas.append("   📭 Sin ciudades")
            continue

        for ciudad in jugador["ciudades"]:
            lineas.append(f"\n   🏙️ {ciudad['nombre']}:")
            lineas.append(f"      👥 Población: {ciudad.get('poblacion', 0)}")
            lineas.append(f"      💰 Oro: {ciudad.get('oro', 0)}")

            edificios = ciudad.get("edificios", {})

            palacio = edificios.get("palacio")
            if palacio:
                pob = palacio["poblacion"]
                oro = palacio["oro"]
                lineas.append("      🏛️ Palacio:")
                lineas.append(
                    f"         - Habitantes: {pob['actual']} / {pob['maxima']}"
                )
                lineas.append(
                    f"         - Tesorería: {oro['actual']} "
                    f"(impuestos previstos: {oro['impuestos_previstos']})"
                )

            almacen = edificios.get("almacen")
            if almacen:
                lineas.append("      🏪 Almacén:")
                lineas.extend(formatear_almacen(almacen))

            granjas = edificios.get("granjas", [])
            if granjas:
                lineas.append("      🌾 Granjas:")
                for granja in granjas:
                    lineas.append(f"         - {granja['nombre']}:")
                    if "almacen" in granja:
                        lineas.extend(formatear_almacen(granja["almacen"]))

    transportes = datos.get("transportes_activos", [])
    lineas.append(f"\n{'─' * 75}")
    lineas.append(f"🚛 TRANSPORTES ACTIVOS: {len(transportes)}")
    lineas.append(f"{'─' * 75}")

    if transportes:
        lineas.append(
            f"   {'ID':<10} {'Tipo':<12} {'Recurso':<10} {'Cant.':<7} "
            f"{'Movs.':<6} {'Progreso':<9} {'Posición Actual':<16} {'Origen → Destino'}"
        )
        lineas.append(
            f"   {'─'*8:<10} {'─'*10:<12} {'─'*8:<10} {'─'*5:<7} "
            f"{'─'*4:<6} {'─'*7:<9} {'─'*14:<16} {'─'*30}"
        )
        for t in transportes:
            recurso = t["recurso"] or "-"
            movs = t["movimientos_pendientes"]
            movs_str = str(movs) if movs >= 0 else "?"
            progreso = f"{t['progreso_pct']:.1f}%"
            lineas.append(
                f"   {t['id']:<10} {t['tipo']:<12} {recurso:<10} {t['cantidad']:<7} "
                f"{movs_str:<6} {progreso:<9} {t['posicion_actual']:<16} "
                f"{t['origen']} → {t['destino']}"
            )
    else:
        lineas.append("   📭 No hay transportes en tránsito")

    lineas.append("\n" + "=" * 75)
    lineas.append("⏱️  Refrescando cada 1s | Ctrl+C para salir")
    return "\n".join(lineas)


def lanzar_monitor(partida_id: str):
    """Bucle de monitorización en tiempo real."""
    print("\n🔄 Lanzando monitor en tiempo real...")
    print("   Esperando a que el servidor esté listo...\n")
    time.sleep(1)

    monitor_cliente = httpx.Client(base_url=BASE_URL, timeout=5.0)

    # server/test.py (actualizar dentro de lanzar_monitor)

    try:
        resp = monitor_cliente.get(
            f"/admin/partidas/{partida_id}/estado_detallado"
        )
        if resp.is_success:
            print(renderizar_monitor(resp.json()))
        elif resp.status_code == 404:
            # ✅ No es un error; simplemente no hay partida activa
            limpiar_consola()
            print("=" * 75)
            print("⏳ ESPERANDO PARTIDA ACTIVA...")
            print(f"   ID buscado: {partida_id}")
            print("   Ejecuta 'python server/test.py' para crear una.")
            print("=" * 75)
        else:
            print(f"❌ Error [{resp.status_code}]: {resp.text}")
    except httpx.ConnectError:
        print("❌ No se pudo conectar al servidor.")

    try:
        while True:
            limpiar_consola()
            try:
                resp = monitor_cliente.get(
                    f"/admin/partidas/{partida_id}/estado_detallado"
                )
                if resp.is_success:
                    print(renderizar_monitor(resp.json()))
                else:
                    # ✅ No es un error; simplemente no hay partida activa
                    limpiar_consola()
                    print("=" * 75)
                    print("⏳ ESPERANDO PARTIDA ACTIVA...")
                    print(f"   ID buscado: {partida_id}")
                    print("   Ejecuta 'python server/test.py' para crear una.")
                    print("=" * 75)
            except httpx.ConnectError:
                print("❌ No se pudo conectar al servidor.")
                print("   Asegúrate de que esté corriendo:")
                print("   uvicorn server.main:app --host 0.0.0.0 --port 8000")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n👋 Monitor detenido.")


# ==========================================
# EJECUCIÓN PRINCIPAL
# ==========================================
if __name__ == "__main__":
    # Modo alternativo: solo monitor con ID existente
    if len(sys.argv) >= 3 and sys.argv[1] == "--solo-monitor":
        lanzar_monitor(sys.argv[2])
        sys.exit(0)

    # Modo normal: test E2E + monitor automático
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
    partida_id: str = partida["partida_id"]

    # Paso 2: Emperador → Capital en (3,3)
    emperador: dict[str, Any] = crear_jugador(
        partida_id=partida_id,
        username="Ciro",
        email="ciro@satrapia.com",
        password="TestPass123!",
        nombre_personaje="Ciro el Grande",
        rol="Emperador",
        nombre_faccion="Imperio Aqueménida",
    )

    # Paso 3: Iniciar partida
    inicio: dict[str, Any] = iniciar_partida(partida_id)

    # Paso 4: Construir granja en (4,3) adyacente a capital
    granja: dict[str, Any] = construir_granja(
        partida_id=partida_id,
        ciudad_nombre="Capital de Imperio Aqueménida",
        coordenada={"x": 6, "y": 3},
        capacidad_silo=50,
    )

    serreria: dict[str, Any] = construir_serreria(
        partida_id=partida_id,
        ciudad_nombre="Capital de Imperio Aqueménida",
        coordenada={"x": 3, "y": 6},  # Diferente a granja (6,3) y capital (3,3)
        capacidad_silo=50,
    )

    # Paso 5: Avanzar turnos para activar producción y transporte
    turno: dict[str, Any] = avanzar_turnos(partida_id=partida_id, turnos=7)

    # Paso 6: Lanzar monitor automáticamente con el ID de la partida
    print("\n✅ Test E2E completado. Iniciando monitor...\n")
    lanzar_monitor(partida_id)
