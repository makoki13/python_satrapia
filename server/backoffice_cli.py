# server/backoffice_cli.py
"""
Backoffice interactivo en modo texto para Satrapia.
Detecta el estado del servidor y muestra un menú contextual.

Uso: python server/backoffice_cli.py
"""

from __future__ import annotations

import os
import sys
import time
from enum import Enum, auto
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx

BASE_URL = "http://localhost:8000"
REFRESH_INTERVAL = 3  # Segundos entre detecciones automáticas de estado

_primera_deteccion = True


# ==========================================
# ESTADOS DEL SISTEMA
# ==========================================
class EstadoSistema(Enum):
    """Estado detectado del servidor + partidas."""

    SIN_SERVIDOR = auto()  # No hay servidor corriendo
    SERVIDOR_SIN_PARTIDAS = auto()  # Servidor OK pero 0 partidas
    SERVIDOR_CON_PARTIDAS = auto()  # Servidor OK y hay partidas


# ==========================================
# DETECCIÓN DE ESTADO
# ==========================================
def detectar_estado() -> tuple[EstadoSistema, list[dict[str, Any]]]:
    """
    Consulta el servidor y devuelve (estado, lista_de_partidas).
    Si el servidor no responde → SIN_SERVIDOR.
    Si responde pero no hay partidas → SERVIDOR_SIN_PARTIDAS.
    Si responde y hay partidas → SERVIDOR_CON_PARTIDAS.
    """
    global _primera_deteccion

    if _primera_deteccion:
        print("\n🔍 Detectando estado del servidor...\n")
        time.sleep(0.5)
        _primera_deteccion = False

    cliente = httpx.Client(base_url=BASE_URL, timeout=2.0)

    # 1. Ping al servidor
    try:
        resp = cliente.get("/health")
        if not resp.is_success:
            return EstadoSistema.SIN_SERVIDOR, []
    except (httpx.ConnectError, httpx.ReadTimeout, httpx.RequestError):
        return EstadoSistema.SIN_SERVIDOR, []

    # 2. Consultar partidas activas
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
    """Muestra la cabecera con el estado actual del sistema."""
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
    """Solicita una opción al usuario hasta que sea válida."""
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
    """Pausa para que el usuario lea el resultado antes de redibujar."""
    try:
        input("\n   ⏎ Pulsa ENTER para continuar...")
    except (EOFError, KeyboardInterrupt):
        pass


# ==========================================
# HANDLERS (PLACEHOLDER - TODO)
# ==========================================
def handler_arrancar_servidor():
    print("\n   🚀 TODO: Arrancar servidor (uvicorn)...")
    pausa()


def handler_parar_servidor():
    print("\n   🛑 TODO: Parar servidor...")
    pausa()


def handler_reiniciar_servidor():
    print("\n   🔄 TODO: Reiniciar servidor...")
    pausa()


def handler_nueva_partida():
    print("\n   🎲 TODO: Crear nueva partida...")
    pausa()


def handler_listar_partidas(partidas: list[dict[str, Any]]):
    print("\n   📋 TODO: Listar partidas con detalle...")
    if partidas:
        print(f"   (Detectadas {len(partidas)} partidas)")
    pausa()


# ==========================================
# MENÚS CONTEXTUALES
# ==========================================
def menu_sin_servidor() -> str | None:
    """Menú cuando no se detecta servidor."""
    print("\n  1.- Arrancar servidor")
    print("  2.- Salir")

    opcion = esperar_opcion(["1", "2"])

    if opcion == "1":
        handler_arrancar_servidor()
    elif opcion == "2":
        return "salir"

    return None


def menu_servidor_sin_partidas() -> str | None:
    """Menú cuando hay servidor pero no hay partidas."""
    print("\n  1.- Parar servidor")
    print("  2.- Reiniciar servidor")
    print("  3.- Nueva partida")
    print("  4.- Salir")

    opcion = esperar_opcion(["1", "2", "3", "4"])

    if opcion == "1":
        handler_parar_servidor()
    elif opcion == "2":
        handler_reiniciar_servidor()
    elif opcion == "3":
        handler_nueva_partida()
    elif opcion == "4":
        return "salir"

    return None


def menu_servidor_con_partidas(partidas: list[dict[str, Any]]) -> str | None:
    """Menú cuando hay servidor y partidas activas."""
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
