# src/config/game_config.py
"""
Singleton de configuración global del juego.
Se actualizará dinámicamente conforme se completen investigaciones.
"""

from dataclasses import field


class GameConfig:
    """Configuración global parametrizable y evolutiva."""

    # Costes base de reclutamiento por tipo de tropa
    # Clave = nombre del TipoRecurso, Valor = dict de {recurso: cantidad_por_unidad}
    _costes_reclutamiento_base: dict[str, dict[str, int]] = field(default_factory=lambda: {
        "INFANTERIA": {"COMIDA": 2, "HIERRO": 1},
        "CABALLERIA": {"COMIDA": 5, "HIERRO": 3, "ORO": 2},
        "ARQUEROS": {"COMIDA": 2, "MADERA": 3},
        "LANCEROS": {"COMIDA": 3, "HIERRO": 2, "MADERA": 1},
        "MAQUINAS_ASALTO": {"MADERA": 10, "HIERRO": 8, "ORO": 5},
        "OFICIALES": {"COMIDA": 5, "ORO": 10},
    })


    _instance: "GameConfig | None" = None

    def __new__(cls) -> "GameConfig":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        # Límites base de edificios productivos por ciudad
        self._limites_base: dict[str, int] = {
            "granja": 3,
            "serreria": 3,
            "cantera": 3,
            "mina_hierro": 3,
            "mina_oro": 3,
        }
        # Bonos acumulativos por investigaciones completadas
        self._bonos_investigacion: dict[str, int] = {}
        self._initialized = True

    def get_max_edificios_productivos(self, tipo: str) -> int:
        """Devuelve el límite actual, modificado por investigaciones."""
        base = self._limites_base.get(tipo, 3)
        bonus = self._bonos_investigacion.get(f"max_{tipo}", 0)
        return base + bonus

    def aplicar_bono_investigacion(self, clave: str, valor: int) -> None:
        """
        Aplica un bono desde el sistema de investigaciones.
        Ejemplo: aplicar_bono_investigacion("max_granja", 1) → límite sube a 4
        """
        actual = self._bonos_investigacion.get(clave, 0)
        self._bonos_investigacion[clave] = actual + valor
        print(f"🔬 [CONFIG] Bono aplicado: {clave} = {actual + valor}")

    def reset(self) -> None:
        """Reinicia la configuración a valores base (útil para pruebas)."""
        self._bonos_investigacion.clear()
        print("🔄 [CONFIG] Configuración reiniciada a valores base.")

    # Añadir a src/config/game_config.py dentro de la clase GameConfig

    def get_bonus_silo(self, tipo_recurso_nombre: str) -> int:
        """Devuelve el bonus de capacidad para un tipo de silo."""
        return self._bonos_investigacion.get(f"silo_{tipo_recurso_nombre}", 0)

    def get_bonus_produccion(self, tipo_recurso_nombre: str) -> int:
        """Devuelve el bonus de producción para un tipo de edificio."""
        return self._bonos_investigacion.get(f"prod_{tipo_recurso_nombre}", 0)

    def get_coste_reclutamiento(self, tipo_tropa_nombre: str) -> dict[str, int] | None:
        """
        Devuelve el coste de reclutamiento de un tipo de tropa.
        Formato: {"COMIDA": 2, "HIERRO": 1} por unidad.
        None si el tipo no existe.
        """
        return self._costes_reclutamiento_base.get(tipo_tropa_nombre)


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- ⚙️ Probando GameConfig Singleton ---\n")

    # 1. Obtener instancia (siempre será la misma)
    config1 = GameConfig()
    config2 = GameConfig()
    print(f"✅ ¿Misma instancia? {config1 is config2}")

    # 2. Consultar límites base
    print("\n📊 Límites base:")
    for tipo in ["granja", "serreria", "cantera", "mina_hierro", "mina_oro"]:
        print(f"   {tipo}: {config1.get_max_edificios_productivos(tipo)}")

    # 3. Aplicar bono de investigación
    print("\n🔬 Aplicando investigación 'Arquitectura Avanzada'...")
    config1.aplicar_bono_investigacion("max_granja", 1)
    config1.aplicar_bono_investigacion("max_serreria", 2)

    # 4. Verificar nuevos límites
    print("\n📊 Límites tras investigación:")
    for tipo in ["granja", "serreria", "cantera"]:
        print(f"   {tipo}: {config1.get_max_edificios_productivos(tipo)}")

    # 5. Resetear
    config1.reset()
    print("\n📊 Límites tras reset:")
    print(f"   granja: {config1.get_max_edificios_productivos('granja')}")

    print("\n--- Fin de las pruebas ---")
