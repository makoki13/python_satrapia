# src/territorio/punto.py

# Para poder utilizar tipos aun no definidos o autoreferencias y referencias circulares
from __future__ import annotations

# Permite el decorador @dataclass que genera __init__, __eq__ etc
# 'field' permite que una variable sea un conjunto de atributos
# cada instancia es propia del objeto, no son compartidas
# 'field' se usa en @dataclass
from dataclasses import dataclass, field

from src.core.coordenada import Coordenada
from src.territorio.entidad import EntidadPolitica  # ← Import del Protocol
from src.territorio.terreno import TipoTerreno


@dataclass(eq=False)  # ← Desactivamos __eq__ automático del dataclass
class Punto:
    """
    Representa una casilla del mapa (1 km²).
    Contiene información sobre el terreno, propietario y posibles estructuras.

    IDENTIDAD: Dos puntos son iguales si y solo si ocupan la misma coordenada.
    Los demás atributos (terreno, propietario, estructura) son propiedades
    mutables de esa ubicación, no parte de su identidad.

    NOTA: La elevación se gestiona en Coordenada.z, no aquí.
    """

    # ==========================================
    # ATRIBUTOS OBLIGATORIOS
    # ==========================================
    coordenada: Coordenada  # Incluye x, y, z (elevación)

    # ==========================================
    # ATRIBUTOS CON VALOR POR DEFECTO
    # ==========================================
    # Por defecto, toda casilla nueva es una llanura (terreno neutro)
    terreno: TipoTerreno = TipoTerreno.LLANURA

    """
    # Propietario (Reino, Tribu o None). Usamos Any por flexibilidad.
    propietario: Any = None

    # Aquí guardaremos referencias a ciudades, ejércitos, etc. (futuro)
    estructura: Any = None
    """

    propietario: EntidadPolitica | None = None
    estructura: object | None = None  # o un Protocol más específico

    unidades: list = field(default_factory=list)

    # ==========================================
    # IDENTIDAD (Hash + Eq consistentes)
    # ==========================================
    def __eq__(self, other: object) -> bool:
        """
        Dos puntos son iguales si ocupan la misma coordenada.
        El resto de atributos son estado mutable de esa ubicación.
        """
        if not isinstance(other, Punto):
            return NotImplemented
        return self.coordenada == other.coordenada

    def __hash__(self) -> int:
        """
        Identidad basada exclusivamente en la coordenada.
        Garantiza que __eq__ y __hash__ son consistentes:
        dos puntos iguales SIEMPRE tienen el mismo hash.
        """
        return hash(self.coordenada)

    # ==========================================
    # PROPIEDADES DERIVADAS (Del terreno)
    # Todas como @property para una API consistente:
    # punto.es_tierra en lugar de punto.es_tierra()
    # ==========================================
    @property
    def es_transitable(self) -> bool:
        """Indica si una unidad terrestre puede pasar por aquí."""
        return self.terreno.transitable

    @property
    def es_tierra(self) -> bool:
        """Indica si es una casilla de tierra (no agua)."""
        return self.terreno.es_tierra

    @property
    def es_agua(self) -> bool:
        """Indica si es una casilla de agua."""
        return self.terreno.es_agua

    @property
    def es_construible(self) -> bool:
        """Indica si se puede construir una ciudad o edificio aquí."""
        return self.terreno.construible and self.estructura is None

    @property
    def coste_movimiento(self) -> float:
        """
        Devuelve el coste de movimiento para atravesar este punto.
        Devuelve math.inf si el terreno es intransitable (ej: MAR).
        """
        return self.terreno.coste_movimiento

    # ==========================================
    # MÉTODOS
    # ==========================================
    @property
    def tiene_propietario(self) -> bool:
        """Devuelve True si el punto pertenece a algún Reino o Tribu."""
        return self.propietario is not None

    def __str__(self) -> str:
        if isinstance(self.propietario, EntidadPolitica):
            # ✅ Seguro: sabemos que tiene .nombre
            return f"Punto{self.coordenada} [{self.terreno}] - {self.propietario.nombre}"
        return f"Punto{self.coordenada} [{self.terreno}] - Tierra de nadie"


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 📍 Probando Puntos del Mapa ---\n")

    # 1. Punto por defecto (llanura)
    p1 = Punto(Coordenada(50, 50))
    print(f"✅ {p1}")
    print(f"   Transitable: {p1.es_transitable} | Construible: {p1.es_construible}")

    # 2. Punto de montaña
    p2 = Punto(Coordenada(51, 50), terreno=TipoTerreno.MONTAÑA)
    print(f"\n✅ {p2}")
    print(f"   Transitable: {p2.es_transitable} | Construible: {p2.es_construible}")
    print(f"   Coste de movimiento: {p2.coste_movimiento} (vs llanura: {p1.coste_movimiento})")

    # 3. Punto de mar
    p3 = Punto(Coordenada(52, 50), terreno=TipoTerreno.MAR)
    print(f"\n✅ {p3}")
    print(f"   ¿Es agua? {p3.es_agua} | ¿Transitable por tierra? {p3.es_transitable}")

    # 4. Verificar consistencia hash/eq
    print("\n--- 🔍 Verificando consistencia hash/eq ---")
    pa = Punto(Coordenada(10, 10), terreno=TipoTerreno.LLANURA)
    pb = Punto(Coordenada(10, 10), terreno=TipoTerreno.BOSQUE)
    pc = Punto(Coordenada(10, 11), terreno=TipoTerreno.LLANURA)

    print(f"\n   pa = {pa}")
    print(f"   pb = {pb}  (misma coordenada, distinto terreno)")
    print(f"   pc = {pc}  (distinta coordenada, mismo terreno)")

    print(f"\n   pa == pb: {pa == pb}  (esperado: True, misma coordenada)")
    print(f"   pa == pc: {pa == pc}  (esperado: False, distinta coordenada)")
    print(f"   hash(pa) == hash(pb): {hash(pa) == hash(pb)}  (esperado: True)")
    print(f"   hash(pa) == hash(pc): {hash(pa) == hash(pc)}  (esperado: False)")

    # 5. Verificar comportamiento en set
    conjunto = {pa, pb, pc}
    print(f"\n   set({{pa, pb, pc}}) tiene {len(conjunto)} elementos (esperado: 2)")
    print(f"   pa in conjunto: {pa in conjunto}  (esperado: True)")
    print(f"   pb in conjunto: {pb in conjunto}  (esperado: True, misma coord que pa)")
    print(f"   pc in conjunto: {pc in conjunto}  (esperado: True)")

    # Verificación final
    assert pa == pb, "pa y pb deben ser iguales (misma coordenada)"
    assert pa != pc, "pa y pc deben ser distintos (distinta coordenada)"
    assert hash(pa) == hash(pb), "hash debe coincidir para puntos iguales"
    assert len(conjunto) == 2, "set debe deduplicar por coordenada"
    print("\n   ✅ Todas las verificaciones de identidad pasaron correctamente.")

    print("\n--- Fin de las pruebas ---")
