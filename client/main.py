# client/main.py
"""
Punto de entrada del cliente Satrapia (PySide6).

Flujo de ejecución:
    1. Inicializa QApplication y configuración global.
    2. Muestra SplashScreen:
       - Detecta el servidor automáticamente.
       - Lista partidas disponibles (en LOBBY).
       - Usuario selecciona partida y se une.
       - El SERVIDOR crea la facción, asigna zona y funda capital.
    3. Al recibir señal partida_lista, cierra el splash y abre MainWindow.
    4. MainWindow muestra el estado del juego (placeholder visual por ahora).

Uso:
    python client/main.py
"""
from __future__ import annotations

import sys
from pathlib import Path

# ==========================================
# CONFIGURACIÓN DE PATH
# ==========================================
# Añadir la raíz del proyecto al sys.path para poder importar:
#   - src/      (core del juego, compartido con el servidor)
#   - server/   (por si se necesita algún helper)
#   - client/   (módulos del propio cliente)
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

# ==========================================
# IMPORTS DE PYSIDE6
# ==========================================
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QGroupBox,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

# ==========================================
# IMPORTS DEL CLIENTE
# ==========================================
from client.core.game_state import game_state  # noqa: E402
from client.ui.splash_screen import SplashScreen  # noqa: E402


class MainWindow(QMainWindow):
    """
    Ventana principal del juego.

    Por ahora es un placeholder que muestra los datos del jugador
    obtenidos tras la unión exitosa a la partida.

    En futuras fases contendrá:
        - MapWidget (renderizado del mapa)
        - Panel lateral (ciudad, edificios, recursos)
        - Barra superior (turno, acciones)
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Satrapia - {game_state.username or 'Jugador'}")
        self.setMinimumSize(1200, 800)

        # ── Widget central ─────────────────────────────────────────────
        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # ── Cabecera: Estado de conexión ───────────────────────────────
        self.label_estado = QLabel("🟢 Conectado y en juego")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #27ae60;"
        )
        layout.addWidget(self.label_estado)

        # ── Grupo: Datos del Jugador ───────────────────────────────────
        grupo_jugador = QGroupBox("👤 Jugador")
        grupo_jugador.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #3498db;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2c3e50;
            }
        """)
        layout_jugador = QVBoxLayout(grupo_jugador)

        # Labels con datos del jugador (leídos de game_state)
        self._crear_label_jugador(layout_jugador, "Username", game_state.username)
        self._crear_label_jugador(layout_jugador, "Personaje", self._personaje_display())
        self._crear_label_jugador(layout_jugador, "Rol", game_state.rol)

        layout.addWidget(grupo_jugador)

        # ── Grupo: Facción y Capital ───────────────────────────────────
        grupo_faccion = QGroupBox("🏛️ Facción")
        grupo_faccion.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #9b59b6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2c3e50;
            }
        """)
        layout_faccion = QVBoxLayout(grupo_faccion)

        self._crear_label_jugador(layout_faccion, "Tipo", self._tipo_faccion_display())
        self._crear_label_jugador(layout_faccion, "Nombre", game_state.faccion_nombre)
        self._crear_label_jugador(layout_faccion, "Capital", game_state.capital_nombre)
        self._crear_label_jugador(layout_faccion, "Posición", self._posicion_display())

        layout.addWidget(grupo_faccion)

        # ── Grupo: Información de la Partida ───────────────────────────
        grupo_partida = QGroupBox("🎲 Partida")
        grupo_partida.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 16px;
                border: 2px solid #e67e22;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2c3e50;
            }
        """)
        layout_partida = QVBoxLayout(grupo_partida)

        self._crear_label_jugador(
            layout_partida, "ID Partida",
            game_state.partida_id[:8] + "..." if game_state.partida_id else None,
        )
        self._crear_label_jugador(
            layout_partida, "Dimensiones Mapa",
            self._dimensiones_display(),
        )
        self._crear_label_jugador(layout_partida, "Turno Actual", str(game_state.turno_actual))

        layout.addWidget(grupo_partida)

        # ── Mensaje final ──────────────────────────────────────────────
        self.label_info = QLabel(
            "🚧 Vista placeholder. En la siguiente fase añadiremos:\n"
            "• Renderizado del mapa (MapWidget)\n"
            "• Panel de ciudad y edificios\n"
            "• Acciones del jugador"
        )
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_info.setStyleSheet(
            "font-size: 14px; color: #7f8c8d; padding: 15px; "
            "background-color: #ecf0f1; border-radius: 6px;"
        )
        layout.addWidget(self.label_info)

        self.setCentralWidget(central)

        # ── Suscribirse a señales ──────────────────────────────────────
        game_state.turno_avanzado.connect(self._on_turno_avanzado)
        game_state.error_ocurrido.connect(self._on_error)

    # ==========================================
    # HELPERS DE CONSTRUCCIÓN DE UI
    # ==========================================
    def _crear_label_jugador(
        self, layout: QVBoxLayout, etiqueta: str, valor: str | None
    ) -> None:
        """Crea una fila de label con etiqueta: valor."""
        row = QWidget()
        row_layout = QVBoxLayout(row)
        row_layout.setContentsMargins(0, 2, 0, 2)
        row_layout.setSpacing(0)

        label = QLabel(f"<b>{etiqueta}:</b> {valor or 'N/A'}")
        label.setStyleSheet("font-size: 15px; color: #2c3e50;")
        row_layout.addWidget(label)

        layout.addWidget(row)

    def _personaje_display(self) -> str | None:
        """Nombre del personaje en el juego."""
        jugador = game_state.jugador
        if jugador is None:
            return None
        return jugador["jugador_nombre"]

    def _tipo_faccion_display(self) -> str | None:
        """Tipo de facción con emoji."""
        jugador = game_state.jugador
        if jugador is None:
            return None
        tipo = jugador["faccion_tipo"]
        emojis = {
            "Imperio": "👑",
            "Reino": "🏰",
            "Tribu": "🏕️",
        }
        emoji = emojis.get(tipo, "")
        return f"{emoji} {tipo}" if tipo else None

    def _posicion_display(self) -> str | None:
        """Coordenada formateada."""
        pos = game_state.posicion_inicial
        if pos is None:
            return None
        return f"({pos['x']}, {pos['y']})"

    def _dimensiones_display(self) -> str | None:
        """Dimensiones del mapa formateadas."""
        dims = game_state.mapa_dimensiones
        if dims:
            return f"{dims[0]}x{dims[1]} km"
        return None

    # ==========================================
    # HANDLERS DE SEÑALES
    # ==========================================
    def _on_turno_avanzado(self, turno: int) -> None:
        """Actualiza el display del turno cuando avanza."""
        print(f"🔄 Turno actualizado a: {turno}")

    def _on_error(self, mensaje: str) -> None:
        """Muestra errores en la ventana principal."""
        print(f"⚠️ Error en MainWindow: {mensaje}")


# ==========================================
# FUNCIÓN PRINCIPAL
# ==========================================
def main():
    """Punto de entrada de la aplicación."""
    print("🎮 Iniciando cliente Satrapia...")
    print(f"   📂 Directorio raíz: {ROOT_DIR}")

    # 1. Crear la aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName("Satrapia")
    app.setOrganizationName("Satrapia Games")
    app.setApplicationVersion("0.1.0")

    # 2. Crear las dos ventanas
    splash = SplashScreen()
    main_window = MainWindow()

    # 3. Conectar señal: cuando la partida esté lista → abrir MainWindow
    def on_partida_lista():
        """Transición: Splash → MainWindow."""
        splash.close()
        main_window.show()
        print("✅ Partida lista. Ventana principal abierta.")
        print(f"   👤 Jugador: {game_state.username}")
        print(f"   🏛️ Facción: {game_state.faccion_nombre}")
        print(f"   🏙️ Capital: {game_state.capital_nombre}")
        print(f"   📍 Posición: {game_state.posicion_inicial}")

    splash.partida_lista.connect(on_partida_lista)

    # 4. Mostrar splash primero (MainWindow queda oculta hasta señal)
    splash.show()

    print(f"✅ Estado global inicializado: {type(game_state).__name__}")
    print("🖥️  Splash screen mostrada (esperando servidor)")
    print("-" * 60)

    # 5. Ejecutar el loop de eventos de Qt
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
