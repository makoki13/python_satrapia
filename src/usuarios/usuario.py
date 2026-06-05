# src/usuarios/usuario.py
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar

import bcrypt


@dataclass
class Usuario:
    """
    Representa a una persona física registrada en la plataforma Satrapia.
    Gestiona credenciales seguras y cumple con los principios básicos del GDPR.
    """

    # ==========================================
    # CONSTANTES DE VALIDACIÓN (ClassVar le dice a dataclass que las ignore en el __init__)
    # ==========================================
    MIN_USERNAME_LENGTH: ClassVar[int] = 3
    MAX_USERNAME_LENGTH: ClassVar[int] = 30
    MIN_PASSWORD_LENGTH: ClassVar[int] = 10

    # ==========================================
    # 1. ATRIBUTOS OBLIGATORIOS (Sin valores por defecto, van al principio)
    # ==========================================
    username: str
    email: str
    _password_hash: str = field(repr=False)  # Obligatorio, pero oculto en los prints

        # ==========================================
    # 2. ATRIBUTOS OPCIONALES (Con valor por defecto, van después)
    # ==========================================
    fecha_ultimo_login: datetime | None = None  # <-- Sintaxis moderna
    activo: bool = True

    # ==========================================
    # 3. ATRIBUTOS INTERNOS (init=False: No se piden al crear el objeto)
    # ==========================================
    id: str = field(default_factory=lambda: str(uuid.uuid4()), init=False)
    fecha_registro: datetime = field(default_factory=datetime.now, init=False)
    fecha_consentimiento_gdpr: datetime = field(default_factory=datetime.now, init=False)

    # ==========================================
    # VALIDACIONES AL CREAR
    # ==========================================
    def __post_init__(self):
        self._validar_username()
        self._validar_email()
        # Si nos pasan una contraseña en texto plano en lugar de un hash bcrypt, la hasheamos
        if not isinstance(self._password_hash, str) or not self._password_hash.startswith('$2b$'):
            self.set_password(self._password_hash)

    def _validar_username(self) -> None:
        if not (self.MIN_USERNAME_LENGTH <= len(self.username) <= self.MAX_USERNAME_LENGTH):
            raise ValueError(f"El username debe tener entre {self.MIN_USERNAME_LENGTH} y {self.MAX_USERNAME_LENGTH} caracteres.")
        if not re.match(r'^[a-zA-Z0-9_-]+$', self.username):
            raise ValueError("El username solo puede contener letras, números, guiones y guiones bajos.")

    def _validar_email(self) -> None:
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(patron, self.email):
            raise ValueError("El formato del email no es válido.")

    # ==========================================
    # GESTIÓN DE CONTRASEÑAS
    # ==========================================
    def set_password(self, password_plano: str) -> None:
        """Hashea y almacena una nueva contraseña."""
        if len(password_plano) < self.MIN_PASSWORD_LENGTH:
            raise ValueError(f"La contraseña debe tener al menos {self.MIN_PASSWORD_LENGTH} caracteres.")

        password_bytes = password_plano.encode('utf-8')
        salt = bcrypt.gensalt(rounds=12)
        self._password_hash = bcrypt.hashpw(password_bytes, salt).decode('utf-8')

    def verificar_password(self, password_plano: str) -> bool:
        """Comprueba si una contraseña introducida coincide con el hash almacenado."""
        if not self.activo:
            return False
        password_bytes = password_plano.encode('utf-8')
        hash_bytes = self._password_hash.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hash_bytes)

    # ==========================================
    # ACCIONES DE CICLO DE VIDA
    # ==========================================
    def registrar_login(self) -> None:
        """Actualiza la marca de tiempo del último acceso."""
        self.fecha_ultimo_login = datetime.now()

    def anonimizar(self) -> None:
        """
        Ejecuta el DERECHO AL OLVIDO (GDPR).
        Desvincula los datos personales pero mantiene el registro histórico.
        """
        self.username = f"usuario_eliminado_{self.id[:8]}"
        self.email = f"{self.id[:8]}@deleted.satrapia"
        self._password_hash = ""  # Imposibilita cualquier login futuro
        self.activo = False

    def __str__(self) -> str:
        estado = "✅ Activo" if self.activo else "❌ Eliminado"
        return f"Usuario: {self.username} ({self.email}) | {estado}"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Usuario ---\n")

    # 1. Crear usuario válido
    try:
        usuario1 = Usuario(
            username="satrapa_99",
            email="jugador@satrapia.com",
            _password_hash="MiContraseñaSegura123!"
        )
        print(f"✅ {usuario1}")
        print(f"   ID interno: {usuario1.id}")
        print(f"   ¿Se guardó la contraseña en plano? -> NO. Hash: {usuario1._password_hash[:20]}...")
    except Exception as e:
        print(f"❌ Error al crear usuario: {e}")

    # 2. Verificar contraseña
    print("\n--- Probando Login ---")
    login_correcto = usuario1.verificar_password("MiContraseñaSegura123!")
    login_fallido = usuario1.verificar_password("contraseñaIncorrecta")
    print(f"   Login con password correcta: {login_correcto} (Esperado: True)")
    print(f"   Login con password errónea: {login_fallido} (Esperado: False)")

    # 3. Validación de seguridad
    print("\n--- Probando validaciones ---")
    try:
        usuario2 = Usuario(
            username="corto",
            email="test@test.com",
            _password_hash="123"
        )
    except ValueError as e:
        print(f"   ✅ Bloqueado correctamente: {e}")

    # 4. Derecho al olvido (GDPR)
    print("\n--- Ejecutando Derecho al Olvido ---")
    print(f"   Antes: {usuario1}")
    usuario1.anonimizar()
    print(f"   Después: {usuario1}")
    print(f"   ¿Puede hacer login tras anonimizar? -> {usuario1.verificar_password('MiContraseñaSegura123!')}")

    print("\n--- Fin de las pruebas ---")
