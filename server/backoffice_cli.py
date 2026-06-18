# server/backoffice_cli.py
"""
Backoffice interactivo en modo texto para Satrapia.
Detecta el estado del servidor y muestra un menú contextual.

Uso: python server/backoffice_cli.py
"""

from __future__ import annotations

import os
import signal
import socket
import subprocess
import sys
import time
from enum import Enum, auto
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

BASE_URL = "http://localhost:8000"
SERVER_LOG_FILE = Path(__file__).parent.parent / "satrapia_server.log"
SERVER_PORT = 8000

_server_process: subprocess.Popen | None = None
_primera_deteccion = True


# ==========================================
# ESTADOS DEL SISTEMA
# ==========================================
class EstadoSistema(Enum):
    SIN_SERVIDOR = auto()
    SERVIDOR_SIN_PARTIDAS = auto()
    SERVIDOR_CON_PARTIDAS = auto()


# ==========================================
# UTILIDADES DE SISTEMA
# ==========================================
def _is_port_in_use(port: int) -> bool:
    """Verifica si un puerto TCP está ocupado en localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except OSError:
            return True


def _kill_process_tree(pid: int) -> None:
    """
    Mata un proceso y TODOS sus hijos (cross-platform).
    Necesario porque `uvicorn --reload` crea procesos hijos (watchfiles).
    """
    if os.name == "nt":
        # Windows: taskkill /T (árbol) /F (forzado) /PID
        subprocess.run(
            ["taskkill", "/T", "/F", "/PID", str(pid)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    else:
        # Unix: matar hijos primero, luego el padre
        try:
            result = subprocess.run(
                ["pgrep", "-P", str(pid)],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                for child_pid in result.stdout.strip().split():
                    try:
                        os.kill(int(child_pid), signal.SIGTERM)
                    except (ProcessLookupError, ValueError):
                        pass
            os.kill(pid, signal.SIGTERM)
        except (ProcessLookupError, PermissionError, FileNotFoundError):
            # FileNotFoundError si pgrep no existe; PermissionError si sin permisos
            pass


def _find_pids_on_port(port: int) -> list[int]:  # noqa: C901
    """Busca los PIDs que están escuchando en un puerto (cross-platform)."""
    pids: list[int] = []
    if os.name == "nt":
        try:
            result = subprocess.run(
                ["netstat", "-ano"],
                capture_output=True,
                text=True,
            )
            for line in result.stdout.splitlines():
                if f":{port}" in line and "LISTENING" in line:
                    parts = line.split()
                    if parts:
                        try:
                            pids.append(int(parts[-1]))
                        except ValueError:
                            pass
        except Exception:
            pass
    else:
        try:
            result = subprocess.run(
                ["lsof", "-ti", f":{port}"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip():
                for pid_str in result.stdout.strip().split():
                    try:
                        pids.append(int(pid_str))
                    except ValueError:
                        pass
        except Exception:
            pass
    return list(set(pids))


def _esperar_puerto_libre(port: int, timeout: float = 5.0) -> bool:
    """Espera hasta que el puerto quede libre o expire el timeout."""
    inicio = time.time()
    while time.time() - inicio < timeout:
        if not _is_port_in_use(port):
            return True
        time.sleep(0.3)
    return False


# ==========================================
# DETECCIÓN DE ESTADO
# ==========================================
def detectar_estado() -> tuple[EstadoSistema, list[dict[str, Any]]]:
    global _primera_deteccion

    if _primera_deteccion:
        print("\n🔍 Detectando estado del servidor...\n")
        time.sleep(0.5)
        _primera_deteccion = False

    cliente = httpx.Client(base_url=BASE_URL, timeout=2.0)

    try:
        resp = cliente.get("/health")
        if not resp.is_success:
            return EstadoSistema.SIN_SERVIDOR, []
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.RequestError):
        return EstadoSistema.SIN_SERVIDOR, []

    try:
        resp = cliente.get("/admin/partidas")
        if resp.is_success:
            partidas = resp.json()
            if partidas:
                return EstadoSistema.SERVIDOR_CON_PARTIDAS, partidas
            return EstadoSistema.SERVIDOR_SIN_PARTIDAS, []
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.RequestError):
        return EstadoSistema.SIN_SERVIDOR, []

    return EstadoSistema.SERVIDOR_SIN_PARTIDAS, []


# ==========================================
# UTILIDADES DE CONSOLA
# ==========================================
def limpiar_consola():
    os.system("cls" if os.name == "nt" else "clear")


def imprimir_cabecera(estado: EstadoSistema, partidas: list[dict[str, Any]]):
    print("=" * 60)
    print("🏛️  SATRAPIA - BACKOFFICE DE ADMINISTRACIÓN")
    print("=" * 60)

    if estado == EstadoSistema.SIN_SERVIDOR:
        print("🔴 Estado: Servidor NO DETECTADO")
    elif estado == EstadoSistema.SERVIDOR_SIN_PARTIDAS:
        print("🟡 Estado: Servidor ACTIVO | 0 partidas")
    else:
        print(f"🟢 Estado: Servidor ACTIVO | {len(partidas)} partida(s)")
    print("-" * 60)


def esperar_opcion(opciones_validas: list[str]) -> str:
    while True:
        try:
            opcion = input("\n👉 Selecciona una opción: ").strip().lower()
            if opcion in opciones_validas:
                return opcion
            print(f"   ⚠️  Opción no válida. Usa: {', '.join(opciones_validas)}")
        except (EOFError, KeyboardInterrupt):
            print()
            return "salir"


def pausa():
    try:
        input("\n   ⏎ Pulsa ENTER para continuar...")
    except (EOFError, KeyboardInterrupt):
        pass


# ==========================================
# HANDLERS
# ==========================================
def handler_arrancar_servidor():
    global _server_process

    if _server_process and _server_process.poll() is None:
        print("\n   ⚠️  El servidor ya está en ejecución en esta sesión.")
        pausa()
        return

    if _is_port_in_use(SERVER_PORT):
        print(f"\n   ⚠️  El puerto {SERVER_PORT} ya está en uso.")
        print("   ¿Hay otro servidor corriendo? Usa 'Parar servidor' primero.")
        pausa()
        return

    print("\n   🚀 Arrancando servidor Satrapia...")
    try:
        python_exec = sys.executable
        cmd = [
            python_exec, "-m", "uvicorn",
            "server.main:app",
            "--host", "0.0.0.0",
            "--port", str(SERVER_PORT),
            "--reload",
        ]

        log_file = open(SERVER_LOG_FILE, "a", encoding="utf-8")

        # ✅ Forzar UTF-8 en el proceso hijo (crítico en Windows)
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        env["PYTHONUTF8"] = "1"  # Python 3.7+ UTF-8 mode

        creationflags = 0
        if os.name == "nt":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        _server_process = subprocess.Popen(
            cmd,
            stdout=log_file,
            stderr=subprocess.STDOUT,
            creationflags=creationflags,
            env=env,  # ← Pasar entorno con UTF-8 forzado
        )

        print(f"   ✅ Proceso lanzado (PID: {_server_process.pid})")
        print(f"   📝 Logs en: {SERVER_LOG_FILE.name}")
        print("   ⏳ Esperando inicialización (3s)...")
        time.sleep(3)

        if _server_process.poll() is not None:
            print("   ❌ El servidor se cerró inesperadamente. Revisa el log.")
        else:
            print(f"   🟢 Servidor listo en http://localhost:{SERVER_PORT}")

    except Exception as e:
        print(f"   ❌ Error al arrancar: {e}")
    pausa()

def handler_parar_servidor(silencioso: bool = False):  # noqa: C901
    """
    Detiene el servidor. Cubre 3 casos:
      1) Servidor arrancado desde este CLI → usamos _server_process
      2) Servidor externo (otro terminal) → buscamos PID por puerto
      3) No hay servidor → mensaje informativo

    Args:
        silencioso: Si True, omite la pausa final (para uso en reinicio).
    """
    global _server_process

    # ── CASO 1: Servidor propio (tenemos referencia al proceso) ──────────
    if _server_process is not None and _server_process.poll() is None:
        pid = _server_process.pid
        print(f"\n   🛑 Deteniendo servidor propio (PID: {pid})...")

        _kill_process_tree(pid)

        try:
            _server_process.wait(timeout=5)
            print("   ✅ Servidor detenido correctamente.")
        except subprocess.TimeoutExpired:
            print("   ⚠️  Timeout. Forzando kill()...")
            try:
                _server_process.kill()
                _server_process.wait(timeout=3)
                print("   ✅ Servidor forzado a cerrar.")
            except Exception as e:
                print(f"   ❌ No se pudo forzar el cierre: {e}")

        _server_process = None

        if _esperar_puerto_libre(SERVER_PORT):
            print(f"   🟢 Puerto {SERVER_PORT} liberado.")
        else:
            print(f"   ⚠️  El puerto {SERVER_PORT} sigue ocupado tras 5s.")

        if not silencioso:
            pausa()
        return

    # ── CASO 2: Servidor externo (detectado por puerto) ──────────────────
    if _is_port_in_use(SERVER_PORT):
        print(f"\n   🔍 Servidor detectado en puerto {SERVER_PORT} (no arrancado desde este CLI).")
        pids = _find_pids_on_port(SERVER_PORT)

        if not pids:
            print("   ❌ No se pudo identificar el PID. Ciérralo manualmente.")
            if not silencioso:
                pausa()
            return

        print(f"   🎯 PIDs encontrados: {pids}")
        for pid in pids:
            print(f"   🛑 Matando proceso {pid}...")
            _kill_process_tree(pid)

        if _esperar_puerto_libre(SERVER_PORT):
            print(f"   🟢 Puerto {SERVER_PORT} liberado.")
        else:
            print(f"   ⚠️  El puerto {SERVER_PORT} sigue ocupado.")

        if not silencioso:
            pausa()
        return

    # ── CASO 3: No hay servidor ──────────────────────────────────────────
    print("\n   ℹ️  No hay servidor activo que detener.")
    if not silencioso:
        pausa()

def handler_reiniciar_servidor():
    """Reinicia el servidor: para (si existe) + espera + arranca de nuevo."""
    print("\n   🔄 Reiniciando servidor Satrapia...")
    print("-" * 60)

    # 1. Parar sin pausa final (modo silencioso)
    if _server_process is not None or _is_port_in_use(SERVER_PORT):
        handler_parar_servidor(silencioso=True)
        # Pequeña pausa adicional para asegurar liberación completa de sockets
        time.sleep(1)
    else:
        print("   ℹ️  No había servidor previo que detener.")

    print("-" * 60)

    # 2. Arrancar de nuevo (ya tiene su propia pausa al final)
    handler_arrancar_servidor()


def handler_nueva_partida():  # noqa: C901
    """Crea una nueva partida mediante la API."""
    print("\n" + "=" * 60)
    print("🎲 CREAR NUEVA PARTIDA")
    print("=" * 60)

    # 1. Solicitar nombre de la partida
    while True:
        try:
            nombre = input("\n   📝 Nombre de la partida: ").strip()
            if nombre:
                break
            print("   ⚠️  El nombre no puede estar vacío.")
        except (EOFError, KeyboardInterrupt):
            print()
            return

    # 2. Preguntar modo (desarrollo vs producción)
    print("\n   📏 Modo de mapa:")
    print("      1.- Desarrollo (200x200 km) - Rápido para pruebas")
    print("      2.- Producción (1000x1000 km) - Tamaño completo")
    modo_opcion = esperar_opcion(["1", "2"])
    modo_desarrollo = (modo_opcion == "1")

    modo_str = "Desarrollo" if modo_desarrollo else "Producción"
    print(f"\n   🗺️  Modo seleccionado: {modo_str}")

    # 3. Confirmar
    print(f"\n   ¿Crear partida '{nombre}' en modo {modo_str}?")
    print("      s.- Sí, crear")
    print("      n.- Cancelar")
    confirmar = esperar_opcion(["s", "n"])

    if confirmar == "n":
        print("   ❌ Creación cancelada.")
        pausa()
        return

    # 4. Llamar a la API
    print("\n   ⏳ Creando partida...")
    cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)

    try:
        resp = cliente.post("/admin/partidas/crear", json={
            "nombre": nombre,
            "modo_desarrollo": modo_desarrollo,
        })

        if resp.is_success:
            datos = resp.json()
            partida_id = datos["partida_id"]
            print("\n   ✅ Partida creada exitosamente")
            print(f"      📋 ID: {partida_id}")
            print(f"      📛 Nombre: {nombre}")
            print(f"      🗺️  Dimensiones: {datos['dimensiones']}")

            # 5. Ofrecer crear emperador automáticamente
            print("\n   👑 ¿Crear un Emperador automáticamente?")
            print("      s.- Sí (Ciro el Grande - Imperio Aqueménida)")
            print("      n.- No, lo haré después")
            crear_emp = esperar_opcion(["s", "n"])

            coord_imperial = None
            coord_satrapa = None

            if crear_emp == "s":
                coord_imperial = _crear_emperador_automatico(partida_id, nombre)

                # Lógica específica para modo PRODUCCIÓN (requiere 2 jugadores)
                if not modo_desarrollo:
                    print("\n   ⚠️  El modo PRODUCCIÓN requiere mínimo 2 jugadores para iniciar.")
                    print("      ¿Crear un Sátrapa automáticamente?")
                    print("      s.- Sí (Darío I - Reino de Media)")
                    print("      n.- No, la partida quedará en LOBBY")
                    crear_sat = esperar_opcion(["s", "n"])
                    if crear_sat == "s":
                        coord_satrapa = _crear_satrapa_automatico(partida_id)
                    else:
                        print("   ℹ️  Partida creada en LOBBY. Añade jugadores manualmente antes de iniciar.")
                        pausa()
                        return

                # Ofrecer iniciar la partida
                print("\n   🎮 ¿Iniciar la partida ahora?")
                print("      s.- Sí, comenzar el juego")
                print("      n.- No, la iniciaré después")
                iniciar = esperar_opcion(["s", "n"])

                if iniciar == "s":
                    _iniciar_partida(
                        partida_id,
                        coord_imperial=coord_imperial,
                        coord_satrapa=coord_satrapa,
                    )

        else:
            print(f"\n   ❌ Error al crear partida [{resp.status_code}]:")
            print(f"      {resp.text}")

    except httpx.ConnectError:
        print("\n   ❌ No se pudo conectar al servidor.")
        print("      Asegúrate de que esté arrancado.")
    except Exception as e:
        print(f"\n   ❌ Error inesperado: {e}")

    pausa()


def _crear_emperador_automatico(partida_id: str, nombre_partida: str) -> dict | None:
    """
    Crea un emperador por defecto para la partida recién creada.

    Returns:
        Diccionario con posicion_inicial {"x": int, "y": int} o None si falla.
    """
    print("\n   ⏳ Creando Emperador...")
    cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)

    try:
        resp = cliente.post("/jugador/unirse", json={
            "partida_id": partida_id,
            "username": "Ciro",
            "email": "ciro@satrapia.com",
            "password": "TestPass123!",
            "nombre_personaje": "Ciro el Grande",
            "rol": "Emperador",
            "nombre_faccion": "Imperio Aqueménida",
        })

        if resp.is_success:
            datos = resp.json()
            print("   ✅ Emperador creado:")
            print(f"      👤 Personaje: {datos['jugador_nombre']}")
            print(f"      🏛️  Facción: {datos['faccion_nombre']}")
            print(f"      🏙️  Capital: {datos['capital_nombre']}")

            posicion = datos.get("posicion_inicial")
            if posicion:
                print(f"      📍 Posición: ({posicion['x']}, {posicion['y']})")
            return posicion
        else:
            print(f"   ❌ Error al crear emperador [{resp.status_code}]:")
            print(f"      {resp.text}")
            return None

    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return None

def _crear_satrapa_automatico(partida_id: str) -> dict | None:
    """
    Crea un sátrapa por defecto para cumplir el requisito de 2 jugadores en producción.

    Returns:
        Diccionario con posicion_inicial {"x": int, "y": int} o None si falla.
    """
    print("\n   ⏳ Creando Sátrapa...")
    cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)
    try:
        resp = cliente.post("/jugador/unirse", json={
            "partida_id": partida_id,
            "username": "Dario",
            "email": "dario@satrapia.com",
            "password": "TestPass123!",
            "nombre_personaje": "Darío I",
            "rol": "Sátrapa",
            "nombre_faccion": "Reino de Media",
        })
        if resp.is_success:
            datos = resp.json()
            print("   ✅ Sátrapa creado:")
            print(f"      👤 Personaje: {datos['jugador_nombre']}")
            print(f"      🏛️  Facción: {datos['faccion_nombre']}")
            print(f"      🏙️  Capital: {datos['capital_nombre']}")

            posicion = datos.get("posicion_inicial")
            if posicion:
                print(f"      📍 Posición: ({posicion['x']}, {posicion['y']})")
            return posicion
        else:
            print(f"   ❌ Error al crear sátrapa [{resp.status_code}]: {resp.text}")
            return None
    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")
        return None


def _iniciar_partida(
    partida_id: str,
    coord_imperial: dict | None = None,
    coord_satrapa: dict | None = None,
):
    """
    Inicia la partida (transición LOBBY → EN_CURSO).

    Args:
        partida_id: ID de la partida a iniciar.
        coord_imperial: Coordenadas de la capital imperial {"x": int, "y": int}.
        coord_satrapa: Coordenadas de la capital del sátrapa (opcional).
    """
    print("\n   ⏳ Iniciando partida...")
    cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)

    try:
        resp = cliente.post(f"/admin/partidas/{partida_id}/iniciar")

        if resp.is_success:
            datos = resp.json()
            print(f"   ✅ {datos['mensaje']}")

            # Ofrecer construir edificios iniciales
            print("\n   🏗️  ¿Construir edificios de producción iniciales?")
            print("      s.- Sí (🌾 Granja + 🪵 Serrería para cada capital)")
            print("      n.- No, los construiré manualmente")
            construir = esperar_opcion(["s", "n"])

            if construir == "s":
                # Validar que tenemos coordenadas
                if coord_imperial is None:
                    print("\n   ⚠️  No se pudo obtener la posición de la capital imperial.")
                    print("      No se construirán edificios automáticamente.")
                else:
                    print("\n   🏗️  Construyendo edificios iniciales...")

                    ciudad_imperial = "Capital de Imperio Aqueménida"
                    c1, t1 = _construir_edificios_para_ciudad(
                        partida_id, ciudad_imperial, coord_imperial
                    )

                    if coord_satrapa is not None:
                        ciudad_satrapa = "Capital de Reino de Media"
                        c2, t2 = _construir_edificios_para_ciudad(
                            partida_id, ciudad_satrapa, coord_satrapa
                        )
                        total_construidos = c1 + c2
                        total_esperados = t1 + t2
                    else:
                        total_construidos = c1
                        total_esperados = t1

                    if total_construidos == total_esperados:
                        print(f"\n   ✅ {total_construidos}/{total_esperados} edificios construidos correctamente.")
                        print("   🚛 Los transportes automáticos comenzarán en el turno 5.")
                    else:
                        print(f"\n   ⚠️  Solo se construyeron {total_construidos}/{total_esperados} edificios.")

            print("\n   🎮 La partida está lista.")
            print("      Monitor en tiempo real:")
            print(f"      python server/test.py --solo-monitor {partida_id}")
        else:
            print(f"   ❌ Error al iniciar [{resp.status_code}]:")
            print(f"      {resp.text}")

    except Exception as e:
        print(f"   ❌ Error inesperado: {e}")

def _construir_edificios_para_ciudad(
    partida_id: str,
    ciudad_nombre: str,
    coord_base: dict[str, int],
):
    """
    Construye una granja y una serrería en posiciones relativas a coord_base.
    Las coordenadas se calculan para no colisionar con la capital ni entre sí.
    """
    x, y = coord_base["x"], coord_base["y"]

    edificios = [
        {
            "tipo": "granja",
            "coordenada": {"x": x + 3, "y": y},      # 3 pasos al este
            "capacidad": 50,
            "emoji": "🌾",
            "nombre": "Granja",
        },
        {
            "tipo": "serreria",
            "coordenada": {"x": x, "y": y + 3},      # 3 pasos al sur
            "capacidad": 50,
            "emoji": "🪵",
            "nombre": "Serrería",
        },
    ]

    cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)
    construidos = 0

    for edificio in edificios:
        coord = edificio["coordenada"]
        try:
            resp = cliente.post("/admin/edificios/construir", json={
                "partida_id": partida_id,
                "ciudad_nombre": ciudad_nombre,
                "tipo": edificio["tipo"],
                "coordenada": coord,
                "capacidad_silo": edificio["capacidad"],
            })

            if resp.is_success:
                print(f"   {edificio['emoji']} {edificio['nombre']} de {ciudad_nombre} en ({coord['x']}, {coord['y']})")
                construidos += 1
            else:
                print(f"   ❌ Error al construir {edificio['tipo']} para {ciudad_nombre}: {resp.text}")

        except Exception as e:
            print(f"   ❌ Error de conexión al construir {edificio['tipo']}: {e}")

    return construidos, len(edificios)


def handler_listar_partidas(partidas: list[dict[str, Any]]):
    """Muestra tabla de partidas activas y permite actuar sobre ellas."""
    print("\n" + "=" * 80)
    print("📋 PARTIDAS ACTIVAS")
    print("=" * 80)

    if not partidas:
        print("\n   📭 No hay partidas activas en el servidor.")
        pausa()
        return

    # Tabla formateada
    print(f"\n   {'#':<3} {'ID':<11} {'Nombre':<25} {'Estado':<12} {'Jug.':<5} {'Mapa'}")
    print(f"   {'─'*2:<3} {'─'*8:<11} {'─'*23:<25} {'─'*10:<12} {'─'*4:<5} {'─'*10}")

    for i, p in enumerate(partidas, start=1):
        id_corto = p['id'][:8] + "..."
        nombre = p['nombre'][:23] + ".." if len(p['nombre']) > 23 else p['nombre']
        estado = p['estado']
        jugadores = str(p['jugadores'])
        mapa = p['dimensiones_mapa']

        # Icono según estado
        icono = {"LOBBY": "🟡", "EN_CURSO": "🟢", "FINALIZADA": "🏁", "CANCELADA": "❌"}.get(estado, "⚪")

        print(f"   {i:<3} {id_corto:<11} {nombre:<25} {icono} {estado:<9} {jugadores:<5} {mapa}")

    # Submenú de acciones
    print("\n" + "-" * 80)
    print("   Introduce el número de la partida para actuar sobre ella (0 para volver):")
    seleccion = esperar_opcion([str(i) for i in range(0, len(partidas) + 1)])

    if seleccion == "0":
        return

    idx = int(seleccion) - 1
    partida = partidas[idx]

    # Submenú de acciones específicas
    _menu_acciones_partida(partida)


def _menu_acciones_partida(partida: dict[str, Any]):
    """Submenú con acciones disponibles sobre una partida concreta."""
    limpiar_consola()
    print("=" * 60)
    print(f"🎯 PARTIDA: {partida['nombre']}")
    print("=" * 60)
    print(f"   ID:       {partida['id']}")
    print(f"   Estado:   {partida['estado']}")
    print(f"   Jugadores: {partida['jugadores']}")
    print(f"   Mapa:     {partida['dimensiones_mapa']}")

    print("\n   Acciones disponibles:")
    print("      1.- 📊 Monitorizar en tiempo real")
    print("      2.- 🗑️  Eliminar partida")

    # Avanzar turnos solo si está en curso
    puede_avanzar = partida['estado'] == "EN_CURSO"
    if puede_avanzar:
        print("      3.- ⏩ Avanzar turnos")
        print("      0.- Volver")
        opciones = ["0", "1", "2", "3"]
    else:
        print("      3.- ⏩ Avanzar turnos (⚠️  Solo disponible en EN_CURSO)")
        print("      0.- Volver")
        opciones = ["0", "1", "2"]

    accion = esperar_opcion(opciones)

    if accion == "1":
        _monitorizar_partida(partida)
    elif accion == "2":
        _eliminar_partida(partida)
    elif accion == "3" and puede_avanzar:
        _avanzar_turnos(partida)
    # "0" vuelve al menú principal sin hacer nada


def _monitorizar_partida(partida: dict[str, Any]):
    """Muestra el comando para lanzar el monitor en otra terminal."""
    print(f"\n   📊 Monitor de '{partida['nombre']}'")
    print("   ─" * 50)
    print("\n   Para lanzar el monitor en OTRA terminal, ejecuta:")
    print(f"\n      python server/test.py --solo-monitor {partida['id']}")
    print("\n   El monitor se refrescará cada segundo.")
    print("   Pulsa Ctrl+C en esa terminal para detenerlo.")
    pausa()


def _eliminar_partida(partida: dict[str, Any]):
    """Elimina una partida del servidor con confirmación."""
    print(f"\n   🗑️  Eliminar '{partida['nombre']}'")
    print("   ⚠️  Esta acción no se puede deshacer.")
    print(f"      ID: {partida['id']}")
    print(f"      Estado: {partida['estado']}")
    print(f"      Jugadores conectados: {partida['jugadores']}")

    print("\n   ¿Confirmas la eliminación?")
    print("      s.- Sí, eliminar definitivamente")
    print("      n.- Cancelar")
    confirmar = esperar_opcion(["s", "n"])

    if confirmar != "s":
        print("   ❌ Eliminación cancelada.")
        pausa()
        return

    cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)
    try:
        resp = cliente.delete(f"/admin/partidas/{partida['id']}")
        if resp.is_success:
            print(f"   ✅ Partida '{partida['nombre']}' eliminada.")
        else:
            print(f"   ❌ Error [{resp.status_code}]: {resp.text}")
    except Exception as e:
        print(f"   ❌ Error de conexión: {e}")

    pausa()


def _avanzar_turnos(partida: dict[str, Any]):  # noqa: C901
    """Avanza uno o más turnos en una partida en curso."""
    print(f"\n   ⏩ Avanzar turnos en '{partida['nombre']}'")
    print("   Introduce el número de turnos a avanzar (1-100):")

    while True:
        try:
            entrada = input("\n   👉 Turnos [por defecto 1]: ").strip()
            if not entrada:
                turnos = 1
                break
            turnos = int(entrada)
            if 1 <= turnos <= 100:
                break
            print("   ⚠️  Debe estar entre 1 y 100.")
        except ValueError:
            print("   ⚠️  Introduce un número válido.")
        except (EOFError, KeyboardInterrupt):
            print()
            return

    print(f"\n   ⏳ Avanzando {turnos} turno(s)...")
    cliente = httpx.Client(base_url=BASE_URL, timeout=30.0)

    try:
        resp = cliente.post(
            f"/admin/partidas/{partida['id']}/avanzar_turno",
            json={"turnos": turnos},
        )
        if resp.is_success:
            datos = resp.json()
            resumen = datos.get("resumen", {})
            print(f"\n   ✅ {datos['mensaje']}")
            print(f"      Turno actual: {resumen.get('turno_actual', '?')}")

            eventos = resumen.get("eventos", [])
            if eventos:
                print(f"\n      📜 Eventos generados ({len(eventos)}):")
                # Contar por tipo para no saturar la salida
                contador: dict[str, int] = {}
                for ev in eventos:
                    tipo = ev.get("tipo", "desconocido")
                    contador[tipo] = contador.get(tipo, 0) + 1
                for tipo, count in contador.items():
                    print(f"         • {tipo}: ×{count}")
            else:
                print("      (Sin eventos)")
        else:
            print(f"\n   ❌ Error [{resp.status_code}]: {resp.text}")
    except Exception as e:
        print(f"\n   ❌ Error de conexión: {e}")

    pausa()

def handler_setup_rapido():  # noqa: C901
    """Crea una partida de pruebas completa en un solo paso."""
    print("\n" + "=" * 60)
    print("⚡ SETUP RÁPIDO - MUNDO DE PRUEBAS")
    print("=" * 60)
    print("\n   Se creará automáticamente:")
    print("      🎲 Partida 'Mundo de Pruebas' (200x200)")
    print("      👑 Ciro el Grande (Emperador)")
    print("      🌾 Granja + 🪵 Serrería para la capital imperial")
    print("\n   ¿Proceder?")
    print("      s.- Sí, crear todo")
    print("      n.- Cancelar")
    confirmar = esperar_opcion(["s", "n"])

    if confirmar == "n":
        print("   ❌ Cancelado.")
        pausa()
        return

    cliente = httpx.Client(base_url=BASE_URL, timeout=10.0)

    # 1. Crear partida
    print("\n   🎲 Creando partida...")
    try:
        resp = cliente.post("/admin/partidas/crear", json={
            "nombre": "Mundo de Pruebas",
            "modo_desarrollo": True,
        })
        if not resp.is_success:
            print(f"   ❌ Error al crear partida: {resp.text}")
            pausa()
            return
        partida_id = resp.json()["partida_id"]
        print(f"   ✅ Partida creada (ID: {partida_id[:8]}...)")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        pausa()
        return

    # 2. Crear emperador
    print("   👑 Creando emperador...")
    try:
        resp = cliente.post("/jugador/unirse", json={
            "partida_id": partida_id,
            "username": "Ciro",
            "email": "ciro@satrapia.com",
            "password": "TestPass123!",
            "nombre_personaje": "Ciro el Grande",
            "rol": "Emperador",
            "nombre_faccion": "Imperio Aqueménida",
        })
        if not resp.is_success:
            print(f"   ❌ Error al crear emperador: {resp.text}")
            pausa()
            return

        datos = resp.json()
        coord_imperial = datos.get("posicion_inicial")
        print("   ✅ Emperador creado")
        if coord_imperial:
            print(f"      📍 Capital en ({coord_imperial['x']}, {coord_imperial['y']})")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        pausa()
        return

    # 3. Iniciar partida
    print("   🎮 Iniciando partida...")
    try:
        resp = cliente.post(f"/admin/partidas/{partida_id}/iniciar")
        if not resp.is_success:
            print(f"   ❌ Error al iniciar: {resp.text}")
            pausa()
            return
        print("   ✅ Partida iniciada")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        pausa()
        return

    # 4. Construir edificios SOLO para capital imperial (setup rápido = 1 jugador)
    if coord_imperial is None:
        print("   ⚠️  No se pudo obtener la posición de la capital. No se construirán edificios.")
        pausa()
        return

    print("   🏗️  Construyendo edificios...")
    ciudad_imperial = "Capital de Imperio Aqueménida"
    c, t = _construir_edificios_para_ciudad(partida_id, ciudad_imperial, coord_imperial)

    if c == t:
        print(f"\n   🎉 Setup completo. {c}/{t} edificios construidos.")
        print(f"      Monitor: python server/test.py --solo-monitor {partida_id}")
    else:
        print(f"\n   ⚠️  Solo se construyeron {c}/{t} edificios.")

    pausa()


# ==========================================
# MENÚS CONTEXTUALES
# ==========================================
def menu_sin_servidor() -> str | None:
    print("\n  1.- Arrancar servidor")
    print("  2.- Salir")
    opcion = esperar_opcion(["1", "2"])
    if opcion == "1":
        handler_arrancar_servidor()
    elif opcion == "2":
        return "salir"
    return None


def menu_servidor_sin_partidas() -> str | None:
    print("\n  1.- Parar servidor")
    print("  2.- Reiniciar servidor")
    print("  3.- Nueva partida (asistida)")
    print("  4.- ⚡ Setup rápido (mundo de pruebas)")  # ✅ NUEVO
    print("  5.- Salir")
    opcion = esperar_opcion(["1", "2", "3", "4", "5"])
    if opcion == "1":
        handler_parar_servidor()
    elif opcion == "2":
        handler_reiniciar_servidor()
    elif opcion == "3":
        handler_nueva_partida()
    elif opcion == "4":
        handler_setup_rapido()
    elif opcion == "5":
        return "salir"
    return None


def menu_servidor_con_partidas(partidas: list[dict[str, Any]]) -> str | None:
    print("\n  1.- Parar servidor")
    print("  2.- Reiniciar servidor")
    print("  3.- Nueva partida")
    print("  4.- Listar partidas")
    print("  5.- Salir")
    opcion = esperar_opcion(["1", "2", "3", "4", "5"])
    if opcion == "1":
        handler_parar_servidor()
    elif opcion == "2":
        handler_reiniciar_servidor()
    elif opcion == "3":
        handler_nueva_partida()
    elif opcion == "4":
        handler_listar_partidas(partidas)
    elif opcion == "5":
        return "salir"
    return None


# ==========================================
# BUCLE PRINCIPAL
# ==========================================
def main():
    while True:
        limpiar_consola()
        estado, partidas = detectar_estado()
        imprimir_cabecera(estado, partidas)

        try:
            if estado == EstadoSistema.SIN_SERVIDOR:
                resultado = menu_sin_servidor()
            elif estado == EstadoSistema.SERVIDOR_SIN_PARTIDAS:
                resultado = menu_servidor_sin_partidas()
            else:
                resultado = menu_servidor_con_partidas(partidas)

            if resultado == "salir":
                print("\n👋 Hasta luego.\n")
                break

        except KeyboardInterrupt:
            print("\n\n👋 Interrumpido. Hasta luego.\n")
            break


if __name__ == "__main__":
    main()
