# client/ui/splash_screen.py
"""
Pantalla de splash con selección de partida y formulario de unión.

Flujo correcto (alineado con arquitectura cliente-servidor):
    1. Verifica conexión al servidor.
    2. Lista partidas disponibles (en estado LOBBY).
    3. Usuario selecciona partida + rellena formulario.
    4. Cliente llama a POST /jugador/unirse.
    5. SERVIDOR crea facción, asigna zona, funda capital, registra punto.
    6. Cliente recibe respuesta → actualiza GameState → emite señal partida_lista.
"""
from __future__ import annotations

import asyncio

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from client.core.api_client import api_client
from client.core.game_state import game_state


class SplashScreen(QWidget):
    """
    Pantalla de conexión y selección de partida.

    Señales:
        partida_lista: Se emite cuando el jugador se ha unido exitosamente.
    """

    partida_lista = Signal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satrapia - Unirse a Partida")
        self.setFixedSize(600, 700)

        # ── Layout principal ───────────────────────────────────────────
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        # ── Título ─────────────────────────────────────────────────────
        self.label_titulo = QLabel("🏛️ SATRAPIA")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setStyleSheet("font-size: 42px; font-weight: bold; color: #2c3e50;")
        layout.addWidget(self.label_titulo)

        # ── Estado de conexión ─────────────────────────────────────────
        self.label_estado = QLabel("🔍 Detectando servidor...")
        self.label_estado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_estado.setStyleSheet("font-size: 16px; color: #7f8c8d;")
        layout.addWidget(self.label_estado)

        layout.addSpacing(10)

        # ── Grupo: Selección de Partida ────────────────────────────────
        grupo_partida = QGroupBox("📋 Seleccionar Partida")
        grupo_partida.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        layout_partida = QVBoxLayout(grupo_partida)

        self.combo_partidas = QComboBox()
        self.combo_partidas.setStyleSheet("""
            QComboBox {
                padding: 8px;
                font-size: 14px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)
        self.combo_partidas.setEnabled(False)
        layout_partida.addWidget(self.combo_partidas)

        self.label_partida_info = QLabel("")
        self.label_partida_info.setStyleSheet("font-size: 12px; color: #7f8c8d;")
        self.label_partida_info.setWordWrap(True)
        layout_partida.addWidget(self.label_partida_info)

        self.btn_refrescar = QPushButton("🔄 Refrescar Lista")
        self.btn_refrescar.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.btn_refrescar.clicked.connect(self._on_refrescar_partidas)
        self.btn_refrescar.setEnabled(False)
        layout_partida.addWidget(self.btn_refrescar)

        layout.addWidget(grupo_partida)

        # ── Grupo: Formulario de Jugador ───────────────────────────────
        grupo_jugador = QGroupBox("👤 Datos del Jugador")
        grupo_jugador.setStyleSheet(grupo_partida.styleSheet())
        form_layout = QFormLayout(grupo_jugador)

        # Campos del formulario
        self.input_username = QLineEdit()
        self.input_username.setPlaceholderText("ciro_grande")
        self.input_username.setStyleSheet("padding: 6px; border: 1px solid #bdc3c7; border-radius: 4px;")

        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("ciro@satrapia.com")
        self.input_email.setStyleSheet("padding: 6px; border: 1px solid #bdc3c7; border-radius: 4px;")

        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("TestPass123!")
        self.input_password.setEchoMode(QLineEdit.EchoMode.Password)
        self.input_password.setStyleSheet("padding: 6px; border: 1px solid #bdc3c7; border-radius: 4px;")

        self.input_nombre_personaje = QLineEdit()
        self.input_nombre_personaje.setPlaceholderText("Ciro el Grande")
        self.input_nombre_personaje.setStyleSheet("padding: 6px; border: 1px solid #bdc3c7; border-radius: 4px;")

        self.combo_rol = QComboBox()
        self.combo_rol.addItems(["Emperador", "Sátrapa", "Jefe Nómada"])
        self.combo_rol.setStyleSheet("""
            QComboBox {
                padding: 6px;
                border: 1px solid #bdc3c7;
                border-radius: 4px;
            }
        """)

        self.input_nombre_faccion = QLineEdit()
        self.input_nombre_faccion.setPlaceholderText("Imperio Aqueménida")
        self.input_nombre_faccion.setStyleSheet("padding: 6px; border: 1px solid #bdc3c7; border-radius: 4px;")

        # Añadir campos al formulario
        form_layout.addRow("Username:", self.input_username)
        form_layout.addRow("Email:", self.input_email)
        form_layout.addRow("Password:", self.input_password)
        form_layout.addRow("Personaje:", self.input_nombre_personaje)
        form_layout.addRow("Rol:", self.combo_rol)
        form_layout.addRow("Facción:", self.input_nombre_faccion)

        layout.addWidget(grupo_jugador)

        # ── Botón de Unirse ────────────────────────────────────────────
        self.btn_unirse = QPushButton("🚀 Unirse a la Partida")
        self.btn_unirse.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-size: 18px;
                padding: 15px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.btn_unirse.clicked.connect(self._on_unirse)
        self.btn_unirse.setEnabled(False)
        layout.addWidget(self.btn_unirse)

        # ── Label de información/errores ───────────────────────────────
        self.label_info = QLabel("")
        self.label_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_info.setStyleSheet("font-size: 13px; color: #34495e;")
        self.label_info.setWordWrap(True)
        layout.addWidget(self.label_info)

        # ── Suscribirse a señales ──────────────────────────────────────
        game_state.estado_conexion_cambiado.connect(self._on_estado_conexion)
        game_state.error_ocurrido.connect(self._on_error)

        # ── Iniciar verificación de conexión tras 500ms ────────────────
        QTimer.singleShot(500, self._verificar_conexion)

    # ==========================================
    # VERIFICACIÓN DE CONEXIÓN
    # ==========================================
    def _verificar_conexion(self):
        """Inicia la verificación async de conexión."""
        asyncio.create_task(self._verificar_conexion_async())

    async def _verificar_conexion_async(self):
        """Verifica conexión al servidor."""
        conectado = await api_client.verificar_conexion()
        if conectado:
            self.label_estado.setText("✅ Servidor detectado")
            self.label_estado.setStyleSheet("font-size: 16px; color: #27ae60;")
            self.btn_refrescar.setEnabled(True)
            self.label_info.setText("Cargando partidas disponibles...")
            await self._cargar_partidas_disponibles()
        else:
            self.label_estado.setText("❌ Servidor no detectado")
            self.label_estado.setStyleSheet("font-size: 16px; color: #c0392b;")
            self.label_info.setText(
                "No se pudo conectar al servidor.\n"
                "Asegúrate de que esté corriendo:\n\n"
                "python server/backoffice_cli.py → Opción 1"
            )

    # ==========================================
    # CARGA DE PARTIDAS
    # ==========================================
    def _on_refrescar_partidas(self):
        """Refresca la lista de partidas disponibles."""
        self.btn_refrescar.setEnabled(False)
        self.label_info.setText("🔄 Actualizando lista de partidas...")
        asyncio.create_task(self._cargar_partidas_disponibles())

    async def _cargar_partidas_disponibles(self):
        """Carga partidas en estado LOBBY desde el servidor."""
        partidas = await api_client.listar_partidas_disponibles()

        self.combo_partidas.clear()

        if not partidas:
            self.combo_partidas.addItem("❌ No hay partidas disponibles")
            self.combo_partidas.setEnabled(False)
            self.btn_unirse.setEnabled(False)
            self.label_partida_info.setText(
                "No hay partidas en estado LOBBY.\n"
                "Usa el backoffice para crear una partida primero."
            )
        else:
            for p in partidas:
                texto = f"{p['nombre']} ({p['dimensiones']}, {p['jugadores']} jugadores)"
                self.combo_partidas.addItem(texto, p['id'])
            self.combo_partidas.setEnabled(True)
            self.btn_unirse.setEnabled(True)
            self.label_partida_info.setText(f"✅ {len(partidas)} partida(s) disponible(s)")

        self.btn_refrescar.setEnabled(True)
        self.label_info.setText("")

    # ==========================================
    # UNIRSE A PARTIDA
    # ==========================================
    def _on_unirse(self):
        """Valida formulario y se une a la partida seleccionada."""
        # Validar campos obligatorios
        if not self.input_username.text().strip():
            self.label_info.setText("⚠️ El username es obligatorio")
            self.label_info.setStyleSheet("font-size: 13px; color: #c0392b;")
            return

        if not self.input_email.text().strip():
            self.label_info.setText("⚠️ El email es obligatorio")
            self.label_info.setStyleSheet("font-size: 13px; color: #c0392b;")
            return

        if not self.input_password.text().strip():
            self.label_info.setText("⚠️ La password es obligatoria")
            self.label_info.setStyleSheet("font-size: 13px; color: #c0392b;")
            return

        if not self.input_nombre_personaje.text().strip():
            self.label_info.setText("⚠️ El nombre del personaje es obligatorio")
            self.label_info.setStyleSheet("font-size: 13px; color: #c0392b;")
            return

        if not self.input_nombre_faccion.text().strip():
            self.label_info.setText("⚠️ El nombre de la facción es obligatorio")
            self.label_info.setStyleSheet("font-size: 13px; color: #c0392b;")
            return

        # Obtener partida seleccionada
        partida_id = self.combo_partidas.currentData()
        if not partida_id:
            self.label_info.setText("⚠️ Selecciona una partida")
            self.label_info.setStyleSheet("font-size: 13px; color: #c0392b;")
            return

        # Deshabilitar UI mientras se procesa
        self.btn_unirse.setEnabled(False)
        self.btn_unirse.setText("⏳ Uniéndose...")
        self.label_info.setText("Conectando con el servidor...")
        self.label_info.setStyleSheet("font-size: 13px; color: #34495e;")

        # Llamar async a unirse
        asyncio.create_task(self._unirse_async(partida_id))

    async def _unirse_async(self, partida_id: str):
        """Llama al endpoint /jugador/unirse."""
        jugador = await api_client.unirse_partida(
            partida_id=partida_id,
            username=self.input_username.text().strip(),
            email=self.input_email.text().strip(),
            password=self.input_password.text().strip(),
            nombre_personaje=self.input_nombre_personaje.text().strip(),
            rol=self.combo_rol.currentText(),
            nombre_faccion=self.input_nombre_faccion.text().strip(),
        )

        if jugador:
            # Éxito: servidor creó facción, capital, etc.
            self.label_info.setText(
                f"✅ ¡Bienvenido {jugador['jugador_nombre']}!\n"
                f"{jugador['faccion_tipo']}: {jugador['faccion_nombre']}\n"
                f"Capital: {jugador['capital_nombre'] or 'Nómada sin capital fija'}"
            )
            self.label_info.setStyleSheet("font-size: 13px; color: #27ae60;")

            # Emitir señal tras 1.5s para que el usuario lea el mensaje
            QTimer.singleShot(1500, self.partida_lista.emit)
        else:
            # Error: reactivar UI
            self.btn_unirse.setEnabled(True)
            self.btn_unirse.setText("🚀 Unirse a la Partida")

    # ==========================================
    # HANDLERS DE SEÑALES
    # ==========================================
    def _on_estado_conexion(self, estado: str):
        """Actualiza el label cuando cambia el estado."""
        if estado == "conectando":
            self.label_estado.setText("🟡 Conectando...")
            self.label_estado.setStyleSheet("font-size: 16px; color: #f39c12;")

    def _on_error(self, mensaje: str):
        """Muestra errores en el label de info."""
        self.label_info.setText(f"⚠️ {mensaje}")
        self.label_info.setStyleSheet("font-size: 13px; color: #c0392b;")
