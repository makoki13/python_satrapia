# src/logistica/transporte.py
from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

from src.core.coordenada import Coordenada
from src.economia.silo import TipoRecurso

if TYPE_CHECKING:
    from src.territorio.mapa import Mapa


class TipoTransporte(Enum):
    """Clasificación del transporte según su propósito."""
    RECURSOS = "recursos"       # Envío automático de silo lleno → ciudad
    COMERCIO = "comercio"       # Intercambio pactado entre ciudades
    EJERCITO = "ejercito"       # Despliegue militar
    TRIBU = "tribu"             # Migración nómada


@dataclass
class Transporte:
    """
    Entidad móvil que transporta recursos o tropas entre dos puntos del mapa.

    Ciclo de vida:
    1. Se crea con origen, destino, ruta y carga.
    2. Cada tick avanza N waypoints según velocidad.
    3. Al llegar al último waypoint (destino): transfiere carga y se destruye.
    """

    origen: Coordenada
    destino: Coordenada
    ruta: list[Coordenada]              # Waypoints calculados por GPS

    # ==========================================
    # IDENTIDAD
    # ==========================================
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    tipo: TipoTransporte = TipoTransporte.RECURSOS

    # ==========================================
    # RUTA Y POSICIÓN
    # ==========================================

    indice_actual: int = 0              # Posición actual en la ruta

    # ==========================================
    # CARGA
    # ==========================================
    tipo_recurso: TipoRecurso | None = None  # None para tribus
    cantidad: int = 0

    # ==========================================
    # VELOCIDAD
    # ==========================================
    velocidad: int = 1                  # Waypoints por tick

    # ==========================================
    # METADATOS
    # ==========================================
    propietario_id: str | None = None   # ID del Reino/Tribu dueña
    metadata: dict[str, Any] = field(default_factory=dict)  # Datos extra (ej: ejército_id)

    # ==========================================
    # VALIDACIONES
    # ==========================================
    def __post_init__(self):
        if not self.ruta:
            raise ValueError("La ruta no puede estar vacía.")
        if self.velocidad <= 0:
            raise ValueError(f"Velocidad debe ser > 0. Recibido: {self.velocidad}")
        if self.origen != self.ruta[0]:
            raise ValueError("El primer waypoint debe coincidir con el origen.")
        if self.destino != self.ruta[-1]:
            raise ValueError("El último waypoint debe coincidir con el destino.")

    # ==========================================
    # CICLO DE VIDA (Llamado por Server Tick)
    # ==========================================
    def avanzar(self, mapa: Mapa) -> tuple[bool, str]:
        """
        Avanza el transporte a lo largo de la ruta.

        Returns:
            (ha_llegado, mensaje)
            - ha_llegado=True: alcanzó el destino, listo para transferencia
            - ha_llegado=False: sigue en ruta o ruta bloqueada
        """
        if self.ha_llegado():
            return True, f"✅ Transporte {self.id} ya está en destino."

        # Avanzar N waypoints según velocidad
        pasos = min(self.velocidad, len(self.ruta) - 1 - self.indice_actual)

        for _ in range(pasos):
            siguiente_idx = self.indice_actual + 1
            siguiente_coord = self.ruta[siguiente_idx]

            # Verificar viabilidad del siguiente punto
            punto = mapa.puntos.get(siguiente_coord)
            if not punto or not punto.es_transitable:
                return False, (
                    f"⛔ Transporte {self.id}: ruta bloqueada en {siguiente_coord}. "
                    f"Terreno intransitable."
                )

            self.indice_actual = siguiente_idx

        if self.ha_llegado():
            return True, f"🏁 Transporte {self.id} ha llegado a {self.destino}."

        restante = len(self.ruta) - 1 - self.indice_actual
        return False, f"🚚 Transporte {self.id}: {restante} waypoints restantes."

    def ha_llegado(self) -> bool:
        """Verifica si el transporte alcanzó el destino."""
        return self.indice_actual >= len(self.ruta) - 1

    @property
    def posicion_actual(self) -> Coordenada:
        """Coordenada actual del transporte en el mapa."""
        return self.ruta[self.indice_actual]

    @property
    def waypoints_restantes(self) -> int:
        """Número de waypoints que faltan para llegar."""
        return max(0, len(self.ruta) - 1 - self.indice_actual)

    @property
    def progreso_porcentaje(self) -> float:
        """Progreso del viaje como porcentaje (0.0 a 100.0)."""
        total = len(self.ruta) - 1
        if total == 0:
            return 100.0
        return (self.indice_actual / total) * 100.0

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        recurso = self.tipo_recurso.value if self.tipo_recurso else "N/A"
        return (
            f"🚚 [{self.tipo.value}] {self.id} | "
            f"{self.posicion_actual} → {self.destino} | "
            f"{recurso}×{self.cantidad} | "
            f"{self.progreso_porcentaje:.0f}%"
        )
