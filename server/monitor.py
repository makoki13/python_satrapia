# server/monitor.py
"""
Monitor en tiempo real del estado de una partida Satrapia.
Uso: python server/monitor.py <partida_id>
Refresco automático cada 1 segundo.
"""
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

BASE_URL = "http://localhost:8000"


def limpiar_consola():
    """Limpia la consola de forma multiplataforma."""
    os.system("cls" if os.name == "nt" else "clear")


def formatear_almacen(stock: dict) -> list[str]:
    """Formatea un resumen de almacén en líneas indentadas."""
    lineas = []
    for recurso, datos in stock.items():
        cap = datos["capacidad"]
        cap_str = "∞" if cap == -1 else str(cap)
        lineas.append(f"            - {recurso}: {datos['stock']} / {cap_str}")
    return lineas


def renderizar(datos: dict) -> str:
    """Convierte el JSON de estado en texto formateado para consola."""
    lineas = [
        "=" * 75,
        f"🏛️  SATRAPIA MONITOR | {datos['partida_nombre']} | Turno: {datos['turno_actual']} | Estado: {datos['estado']}",
        "=" * 75,
    ]

    # ==========================================
    # JUGADORES Y CIUDADES
    # ==========================================
    for jugador in datos["jugadores"]:
        lineas.append(f"\n👤 Jugador: {jugador['nombre_personaje']} ({jugador['username']})")
        lineas.append(f"   Rol: {jugador['rol']} | Facción: {jugador['faccion']}")

        if not jugador["ciudades"]:
            lineas.append("   📭 Sin ciudades")
            continue

        for ciudad in jugador["ciudades"]:
            # Población y Oro visibles a nivel de ciudad
            lineas.append(f"\n   🏙️ {ciudad['nombre']}:")
            lineas.append(f"      👥 Población: {ciudad.get('poblacion', 0)}")
            lineas.append(f"      💰 Oro: {ciudad.get('oro', 0)}")

            edificios = ciudad.get("edificios", {})

            # Palacio (detalle ampliado)
            palacio = edificios.get("palacio")
            if palacio:
                pob = palacio["poblacion"]
                oro = palacio["oro"]
                lineas.append("      🏛️ Palacio:")
                lineas.append(f"         - Habitantes: {pob['actual']} / {pob['maxima']}")
                lineas.append(
                    f"         - Tesorería: {oro['actual']} "
                    f"(impuestos previstos: {oro['impuestos_previstos']})"
                )

            # Almacén central
            almacen = edificios.get("almacen")
            if almacen:
                lineas.append("      🏪 Almacén:")
                lineas.extend(formatear_almacen(almacen))

            # Granjas
            granjas = edificios.get("granjas", [])
            if granjas:
                lineas.append("      🌾 Granjas:")
                for granja in granjas:
                    lineas.append(f"         - {granja['nombre']}:")
                    if "almacen" in granja:
                        lineas.extend(formatear_almacen(granja["almacen"]))

    # ==========================================
    # TRANSPORTES ACTIVOS
    # ==========================================
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


def main():
    if len(sys.argv) < 2:
        print("Uso: python server/monitor.py <partida_id>")
        print("Ejemplo: python server/monitor.py ff786998-bd41-41ad-8cd9-10110a37f990")
        sys.exit(1)

    partida_id = sys.argv[1]
    cliente = httpx.Client(base_url=BASE_URL, timeout=5.0)

    try:
        while True:
            limpiar_consola()
            try:
                resp = cliente.get(f"/admin/partidas/{partida_id}/estado_detallado")
                if resp.is_success:
                    print(renderizar(resp.json()))
                else:
                    print(f"❌ Error [{resp.status_code}]: {resp.text}")
            except httpx.ConnectError:
                print("❌ No se pudo conectar al servidor.")
                print("   Asegúrate de que esté corriendo:")
                print("   uvicorn server.main:app --host 0.0.0.0 --port 8000")

            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\n👋 Monitor detenido.")


if __name__ == "__main__":
    main()
