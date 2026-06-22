# client/main.py
"""
Punto de entrada del cliente Satrapia (PySide6).

Usa qasync para integrar el event loop de Qt con asyncio.
MainWindow se suscribe a señales de GameState para refrescarse automáticamente
cuando los datos del jugador y partida estén disponibles.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

import qasync  # noqa: E402
from PySide6.QtCore import Qt  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication,
    QGroupBox,
    QLabel,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from client.core.game_state import game_state  # noqa: E402
from client.ui.splash_screen import SplashScreen  # noqa: E402


class MainWindow(QMainWindow):
    """
    Ventana principal del juego.

    Se suscribe a las señales de GameState para refrescar sus labels
    cuando los datos del jugador/partida lleguen del servidor.
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

        # ── Cabecera ───────────────────────────────────────────────────
        self.label_estado = QLabel("🟢 Conectado y en juego")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setStyleSheet(
            "font-size: 28px; font-weight: bold; color: #27ae60;"
        )
        layout.addWidget(self.label_estado)

        # ── Grupo Jugador ──────────────────────────────────────────────
        grupo_jugador = QGroupBox("👤 Jugador")
        grupo_jugador.setStyleSheet(self._grupo_style("#3498db"))
        layout_jugador = QVBoxLayout(grupo_jugador)

        # Guardar referencias a los labels para poder refrescarlos
        self.label_username = self._crear_label("Username", None)
        self.label_personaje = self._crear_label("Personaje", None)
        self.label_rol = self._crear_label("Rol", None)

        layout_jugador.addWidget(self.label_username)
        layout_jugador.addWidget(self.label_personaje)
        layout_jugador.addWidget(self.label_rol)
        layout.addWidget(grupo_jugador)

        # ── Grupo Facción ──────────────────────────────────────────────
        grupo_faccion = QGroupBox("🏛️ Facción")
        grupo_faccion.setStyleSheet(self._grupo_style("#9b59b6"))
        layout_faccion = QVBoxLayout(grupo_faccion)

        self.label_tipo_faccion = self._crear_label("Tipo", None)
        self.label_nombre_faccion = self._crear_label("Nombre", None)
        self.label_capital = self._crear_label("Capital", None)
        self.label_posicion = self._crear_label("Posición", None)

        layout_faccion.addWidget(self.label_tipo_faccion)
        layout_faccion.addWidget(self.label_nombre_faccion)
        layout_faccion.addWidget(self.label_capital)
        layout_faccion.addWidget(self.label_posicion)
        layout.addWidget(grupo_faccion)

        # ── Grupo Partida ──────────────────────────────────────────────
        grupo_partida = QGroupBox("🎲 Partida")
        grupo_partida.setStyleSheet(self._grupo_style("#e67e22"))
        layout_partida = QVBoxLayout(grupo_partida)

        self.label_id_partida = self._crear_label("ID Partida", None)
        self.label_dimensiones = self._crear_label("Dimensiones Mapa", None)
        self.label_turno = self._crear_label("Turno Actual", "0")

        layout_partida.addWidget(self.label_id_partida)
        layout_partida.addWidget(self.label_dimensiones)
        layout_partida.addWidget(self.label_turno)
        layout.addWidget(grupo_partida)

        # ── Mensaje roadmap ────────────────────────────────────────────
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

        # ── Suscribirse a señales (REFRESCO AUTOMÁTICO) ────────────────
        game_state.jugador_asignado.connect(self._on_jugador_asignado)
        game_state.partida_actualizada.connect(self._on_partida_actualizada)
        game_state.turno_avanzado.connect(self._on_turno_avanzado)
        game_state.error_ocurrido.connect(self._on_error)

    # ==========================================
    # HELPERS DE UI
    # ==========================================
    def _grupo_style(self, color: str) -> str:
        """Estilo reutilizable para QGroupBox."""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 16px;
                border: 2px solid {color};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #2c3e50;
            }}
        """

    def _crear_label(self, etiqueta: str, valor: str | None) -> QLabel:
        """Crea un label con formato 'Etiqueta: valor'."""
        label = QLabel(f"<b>{etiqueta}:</b> {valor or 'N/A'}")
        label.setStyleSheet("font-size: 15px; color: #2c3e50; padding: 2px 0;")
        # Guardamos el nombre de la etiqueta para poder refrescar
        label.setProperty("etiqueta", etiqueta)
        return label

    def _actualizar_label(self, label: QLabel, valor: str | None) -> None:
        """Refresca el texto de un label."""
        etiqueta = label.property("etiqueta")
        label.setText(f"<b>{etiqueta}:</b> {valor or 'N/A'}")

    # ==========================================
    # HANDLERS DE SEÑALES (REFRESCO AUTOMÁTICO)
    # ==========================================
    def _on_jugador_asignado(self, datos: dict) -> None:
        """Se ejecuta cuando el jugador se une exitosamente a la partida."""

        """Se ejecuta cuando el jugador se une exitosamente a la partida."""
        print("🔍 DEBUG MainWindow: _on_jugador_asignado llamado")
        print(f"🔍 DEBUG MainWindow: game_state.username = '{game_state.username}'")  # ← NUEVO
        print(f"🔍 DEBUG MainWindow: datos recibidos = {datos}")  # ← NUEVO

        # ... resto del código

        print("🔄 MainWindow: refrescando datos de jugador")

        # Actualizar título de la ventana
        self.setWindowTitle(f"Satrapia - {game_state.username or 'Jugador'}")

        # Refrescar grupo Jugador
        self._actualizar_label(self.label_username, game_state.username)
        self._actualizar_label(self.label_personaje, datos.get("jugador_nombre"))
        self._actualizar_label(self.label_rol, game_state.rol)

        # Refrescar grupo Facción
        tipo = datos.get("faccion_tipo")
        emojis = {"Imperio": "👑", "Reino": "🏰", "Tribu": "🏕️"}
        tipo_display = f"{emojis.get(tipo, '')} {tipo}" if tipo else None

        self._actualizar_label(self.label_tipo_faccion, tipo_display)
        self._actualizar_label(self.label_nombre_faccion, game_state.faccion_nombre)
        self._actualizar_label(self.label_capital, game_state.capital_nombre)

        pos = game_state.posicion_inicial
        pos_display = f"({pos['x']}, {pos['y']})" if pos else None
        self._actualizar_label(self.label_posicion, pos_display)

    def _on_partida_actualizada(self, datos: dict) -> None:
        """Se ejecuta cuando los datos de la partida se actualizan."""
        print("🔄 MainWindow: refrescando datos de partida")

        partida_id = game_state.partida_id
        id_display = partida_id[:8] + "..." if partida_id else None
        self._actualizar_label(self.label_id_partida, id_display)

        dims = game_state.mapa_dimensiones
        dims_display = f"{dims[0]}x{dims[1]} km" if dims else None
        self._actualizar_label(self.label_dimensiones, dims_display)

    def _on_turno_avanzado(self, turno: int) -> None:
        """Actualiza el display del turno."""
        self._actualizar_label(self.label_turno, str(turno))
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

    app = QApplication(sys.argv)
    app.setApplicationName("Satrapia")
    app.setOrganizationName("Satrapia Games")
    app.setApplicationVersion("0.1.0")

    # Configurar qasync
    loop = qasync.QEventLoop(app)
    import asyncio
    asyncio.set_event_loop(loop)

    # Crear ventanas
    splash = SplashScreen()
    main_window = MainWindow()

    # Conectar señal: Splash → MainWindow
    def on_partida_lista():
        splash.close()
        main_window.show()
        print("✅ Partida lista. Ventana principal abierta.")
        print(f"   👤 Jugador: {game_state.username}")
        print(f"   🏛️ Facción: {game_state.faccion_nombre}")
        print(f"   🏙️ Capital: {game_state.capital_nombre}")
        print(f"   📍 Posición: {game_state.posicion_inicial}")

    splash.partida_lista.connect(on_partida_lista)

    splash.show()

    print("✅ Estado global inicializado: {type(game_state).__name__}")
    print("✅ Event loop: qasync (Qt + asyncio integrados)")
    print("🖥️  Splash screen mostrada (esperando servidor)")
    print("-" * 60)

    with loop:
        loop.run_forever()


if __name__ == "__main__":
    main()
