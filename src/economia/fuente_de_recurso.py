# src/economia/fuente_de_recurso.py
from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass
class FuenteDeRecurso:
    """
    Representa un yacimiento o fuente de recursos en el mapa.

    Puede ser FINITA (minas: oro, hierro, piedra) o INAGOTABLE (granjas, bosques).
    Para fuentes finitas, el stock disminuye con cada extracción hasta agotarse.
    Para fuentes inagotables, stock_actual siempre == valor_inicial (nunca se consume).
    """

    # ==========================================
    # IDENTIDAD Y CONFIGURACIÓN
    # ==========================================
    nombre: str
    nivel: int                    # 1-5, determina riqueza del yacimiento
    valor_inicial: int            # Stock máximo (calculado según nivel + params)
    es_inagotable: bool = False   # True = granja/bosque; False = mina

    # ==========================================
    # ESTADO DINÁMICO
    # ==========================================
    stock_actual: int = -1        # Se inicializa en __post_init__ si es -1

    # ==========================================
    # VALIDACIONES E INICIALIZACIÓN
    # ==========================================
    def __post_init__(self):
        if not 1 <= self.nivel <= 5:
            raise ValueError(f"El nivel debe estar entre 1 y 5. Recibido: {self.nivel}")
        if self.valor_inicial < 0:
            raise ValueError(f"El valor inicial no puede ser negativo. Recibido: {self.valor_inicial}")

        # Si no se proporcionó stock_actual, se iguala al valor inicial
        if self.stock_actual == -1:
            self.stock_actual = self.valor_inicial

        if self.stock_actual > self.valor_inicial:
            raise ValueError(
                f"El stock actual ({self.stock_actual}) no puede superar "
                f"el valor inicial ({self.valor_inicial})."
            )

    # ==========================================
    # EXTRACCIÓN DE RECURSOS
    # ==========================================
    def extraer(self, cantidad_solicitada: int) -> tuple[bool, int, str]:
        """
        Extrae recursos de la fuente.

        - Si es INAGOTABLE: siempre devuelve la cantidad solicitada completa.
        - Si es FINITA: devuelve lo disponible hasta agotar el stock.

        Returns:
            (éxito, cantidad_real_extraída, mensaje)
        """
        if cantidad_solicitada <= 0:
            return False, 0, "❌ La cantidad a extraer debe ser positiva."

        # Fuentes inagotables: producción perpetua
        if self.es_inagotable:
            return True, cantidad_solicitada, (
                f"✅ Extraídas {cantidad_solicitada} unidades de {self.nombre} (fuente inagotable)."
            )

        # Fuentes finitas: consumo real del yacimiento
        if self.stock_actual <= 0:
            return False, 0, f"⛔ {self.nombre} está AGOTADA. No quedan recursos."

        real = min(cantidad_solicitada, self.stock_actual)
        self.stock_actual -= real

        if real < cantidad_solicitada:
            return True, real, (
                f"⚠️ {self.nombre}: solo se extrajeron {real}/{cantidad_solicitada}. "
                f"Quedan {self.stock_actual} unidades en el yacimiento."
            )

        if self.stock_actual == 0:
            return True, real, (
                f"⛔ {self.nombre} se ha AGOTADO tras esta extracción. "
                f"Se obtuvieron {real} unidades finales."
            )

        return True, real, f"✅ Extraídas {real} unidades de {self.nombre}. Restan {self.stock_actual}."

    # ==========================================
    # CONSULTAS DE ESTADO
    # ==========================================
    def esta_agotada(self) -> bool:
        """Solo aplica a fuentes finitas. Las inagotables nunca se agotan."""
        if self.es_inagotable:
            return False
        return self.stock_actual <= 0

    def porcentaje_restante(self) -> float:
        """Devuelve el % de recurso restante (0.0 a 100.0)."""
        if self.es_inagotable or self.valor_inicial == 0:
            return 100.0
        return (self.stock_actual / self.valor_inicial) * 100.0

    # ==========================================
    # FACTORY METHOD (Creación con nivel aleatorio)
    # ==========================================
    @classmethod
    def crear_con_nivel_aleatorio(
        cls,
        nombre: str,
        es_inagotable: bool = False,
        tabla_valores: dict[int, int] | None = None
    ) -> FuenteDeRecurso:
        """
        Crea una fuente con nivel aleatorio (1-5).

        Args:
            nombre: Nombre descriptivo ("Mina de Oro Norte")
            es_inagotable: True para granjas/bosques, False para minas
            tabla_valores: Dict {nivel: valor_inicial}. Si None, usa valores por defecto.

        Returns:
            Instancia de FuenteDeRecurso configurada
        """
        nivel = random.randint(1, 5)

        # Tabla por defecto (parametrizable en el futuro vía GameConfig)
        if tabla_valores is None:
            tabla_valores = {1: 100, 2: 250, 3: 500, 4: 1000, 5: 2000}

        valor_inicial = tabla_valores.get(nivel, 100)

        return cls(
            nombre=nombre,
            nivel=nivel,
            valor_inicial=valor_inicial,
            es_inagotable=es_inagotable
        )

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        if self.es_inagotable:
            return f"♻️ {self.nombre} (Nv.{self.nivel}) [INAGOTABLE]"

        pct = self.porcentaje_restante()
        estado = "AGOTADA" if self.esta_agotada() else f"{pct:.0f}%"
        return f"⛏️ {self.nombre} (Nv.{self.nivel}) [{self.stock_actual}/{self.valor_inicial}] {estado}"
