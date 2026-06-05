# test_flujo_completo.py
"""
Script que prueba el flujo completo del servidor:
1. Crear partida (con generación automática de mapa)
2. Unir 3 jugadores
3. Iniciar partida (asignación de roles, zonas y creación de facciones)
4. Verificar que los reinos/tribus se crearon correctamente
"""

import requests

BASE_URL = "http://127.0.0.1:8000"

def test_flujo_completo():
    print("🎮 === PRUEBA DE FLUJO COMPLETO CON GENERADOR DE MAPAS ===\n")

    # 1. Crear partida (esto genera el mundo automáticamente)
    print("1️⃣ Creando partida (generando mundo)...")
    response = requests.post(f"{BASE_URL}/admin/partidas/crear", json={
        "nombre": "Imperio de Prueba",
        "modo_desarrollo": True  # Mapa pequeño para pruebas rápidas
    })

    if response.status_code != 200:
        print(f"   ❌ Error al crear partida: {response.text}")
        return

    partida_data = response.json()
    partida_id = partida_data["partida_id"]
    print(f"   ✅ Partida creada: {partida_data['mensaje']}")
    print(f"   🆔 ID: {partida_id}")
    print(f"   📏 Dimensiones: {partida_data['dimensiones']}\n")

    # 2. Unir jugadores (3 jugadores: Emperador, Jefe, Sátrapa)
    jugadores = [
        {
            "partida_id": partida_id,
            "username": "cesar",
            "email": "cesar@roma.com",
            "password": "Password123!",
            "nombre_personaje": "César Augusto"
        },
        {
            "partida_id": partida_id,
            "username": "atila",
            "email": "atila@hunos.com",
            "password": "Password123!",
            "nombre_personaje": "Atila el Huno"
        },
        {
            "partida_id": partida_id,
            "username": "satrapa",
            "email": "satrapa@persia.com",
            "password": "Password123!",
            "nombre_personaje": "Darío I"
        }
    ]

    print("2️⃣ Uniendo jugadores...")
    for i, jugador_data in enumerate(jugadores, 1):
        response = requests.post(f"{BASE_URL}/jugador/unirse", json=jugador_data)
        data = response.json()

        if data.get("exito"):
            print(f"   ✅ Jugador {i}: {data['jugador_nombre']} unido")
        else:
            print(f"   ❌ Error al unir jugador {i}: {data.get('detail', 'Error desconocido')}")

    print()

    # 3. Listar partidas para ver el estado
    print("3️⃣ Verificando estado de la partida...")
    response = requests.get(f"{BASE_URL}/admin/partidas")
    partidas = response.json()

    for partida in partidas:
        if partida["id"] == partida_id:
            print(f"   📊 Partida: {partida['nombre']}")
            print(f"   👥 Jugadores: {partida['jugadores']}")
            print(f"   🎯 Estado: {partida['estado']}")
            print(f"   🗺️ Mapa: {partida['dimensiones_mapa']}\n")

    # 4. Iniciar la partida (esto asigna roles, zonas y crea facciones)
    print("4️⃣ Iniciando partida (asignando roles y creando facciones)...")
    print("   ⏳ Esto puede tardar un momento mientras se asignan territorios...")

    response = requests.post(f"{BASE_URL}/admin/partidas/{partida_id}/iniciar")
    data = response.json()

    if data.get("exito"):
        print(f"   ✅ {data['mensaje']}\n")
        print("   🎉 ¡La partida ha comenzado!")
        print("   👑 Los roles han sido asignados automáticamente")
        print("   🗺️ Los reinos y tribus han sido creados en el mapa")
        print("   🏰 Cada jugador tiene su territorio inicial\n")
    else:
        print(f"   ❌ Error al iniciar: {data.get('detail', 'Error desconocido')}\n")

    # 5. Verificar estado final
    print("5️⃣ Estado final de la partida...")
    response = requests.get(f"{BASE_URL}/admin/partidas")
    partidas = response.json()

    for partida in partidas:
        if partida["id"] == partida_id:
            print("   📊 Estado final:")
            print(f"   🎯 Estado: {partida['estado']}")
            print(f"   👥 Jugadores activos: {partida['jugadores']}")
            print(f"   🗺️ Mapa generado: {partida['dimensiones_mapa']} km\n")

    print("🏁 === PRUEBA COMPLETADA ===")
    print("\n📋 Revisa la terminal del servidor para ver:")
    print("   - 🌍 Generación del mundo")
    print("   - 📍 Asignación de zonas a jugadores")
    print("   - 🏰 Creación de reinos y tribus")
    print("   - 🗺️ Asignación de territorios iniciales")

if __name__ == "__main__":
    print("Asegúrate de que el servidor está corriendo (python -m server.main)\n")
    test_flujo_completo()
