# src/territorio/reino.py
from dataclasses import dataclass, field
from typing import Any, ClassVar


@dataclass
class Reino:
    """
    Representa una facción política que controla un subconjunto de puntos del mapa.
    Puede ser el dominio personal de un Emperador o la satrapía de un Sátrapa.
    """

    # ==========================================
    # CONSTANTES GLOBALES DEL JUEGO
    # ==========================================
    MAX_CIUDADES_SATRAPIA: ClassVar[int] = 5
    MAX_CIUDADES_IMPERIAL: ClassVar[int] = 3

    # ==========================================
    # ATRIBUTOS DE INSTANCIA
    # ==========================================
    nombre: str
    gobernante: Any = None  # Futuro: Objeto Emperador o Sátrapa
    es_imperial: bool = False  # True si es el reino personal del Emperador

    # Colecciones (Se inicializan vacías para cada reino nuevo)
    puntos_controlados: set[Any] = field(default_factory=set)
    ciudades: list[Any] = field(default_factory=list)

    # ==========================================
    # MÉTODOS DE GESTIÓN
    # ==========================================
    def get_limite_ciudades(self) -> int:
        """Devuelve el máximo de ciudades permitidas según el tipo de reino."""
        return self.MAX_CIUDADES_IMPERIAL if self.es_imperial else self.MAX_CIUDADES_SATRAPIA

    def puede_fundar_ciudad(self) -> bool:
        """Verifica si el reino tiene espacio para una nueva ciudad."""
        return len(self.ciudades) < self.get_limite_ciudades()

    def agregar_punto(self, punto: Any) -> None:
        """
        Añade un Punto al reino y actualiza automáticamente el propietario del Punto.
        Mantiene la coherencia bidireccional entre el Mapa y el Reino.
        """
        self.puntos_controlados.add(punto)
        punto.propietario = self

    def fundar_ciudad(self, ciudad: Any) -> bool:
        """
        Intenta añadir una ciudad al reino.
        Devuelve True si tuvo éxito, False si alcanzó el límite.
        """
        if not self.puede_fundar_ciudad():
            print(f"⚠️ El reino de {self.nombre} ha alcanzado su límite de {self.get_limite_ciudades()} ciudades.")
            return False

        self.ciudades.append(ciudad)
        return True

    def __str__(self) -> str:
        tipo = "Imperial" if self.es_imperial else "Vasallo/Satrapía"
        return (f"Reino de {self.nombre} ({tipo}) | "
                f"Territorios: {len(self.puntos_controlados)} | "
                f"Ciudades: {len(self.ciudades)}/{self.get_limite_ciudades()}")


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Reino ---\n")

    # 1. Creamos dos reinos distintos
    reino_emperador = Reino("Dominio Imperial de Aurelia", es_imperial=True)
    reino_satrapa = Reino("Satrapía de las Dunas")

    print(f"✅ {reino_emperador}")
    print(f"✅ {reino_satrapa}")

    # 2. Probamos el límite de ciudades
    print("\n--- Probando expansión urbana ---")

    # Simulamos la creación de ciudades (usamos strings por ahora)
    for i in range(1, 6):
        ciudad_mock = f"Ciudad_{i}"

        # Intento en el reino Imperial (Límite 3)
        if i <= 4: # Intentamos 4 veces
            print(f"\nIntentando fundar {ciudad_mock} en Aurelia:")
            reino_emperador.fundar_ciudad(ciudad_mock)

        # Intento en la Satrapía (Límite 5)
        print(f"Intentando fundar {ciudad_mock} en las Dunas:")
        reino_satrapa.fundar_ciudad(ciudad_mock)

    # 3. Probamos la asignación de puntos (Simulando un objeto Punto)
    print("\n--- Probando control territorial ---")

    class PuntoMock:
        def __init__(self):
            # LE DECIMOS A VS CODE: "Esto empieza siendo None, pero luego será 'Any' (cualquier cosa)"
            self.propietario: Any = None

    punto1 = PuntoMock()
    punto2 = PuntoMock()

    reino_satrapa.agregar_punto(punto1)
    reino_satrapa.agregar_punto(punto2)

    # getattr es la forma segura de pedir un atributo sin que VS Code se enfade si hay un None
    nombre_dueno = getattr(punto1.propietario, 'nombre', 'Desconocido')
    print(f"Punto 1 ahora pertenece a: {nombre_dueno}")
    print(f"Total de puntos controlados por las Dunas: {len(reino_satrapa.puntos_controlados)}")

    print("\n--- Fin de las pruebas ---")
