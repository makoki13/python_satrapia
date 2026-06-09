# src/territorio/reino.py
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:
    from src.economia.edificios.laboratorio import Laboratorio


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

    # Colecciones territoriales
    puntos_controlados: set[Any] = field(default_factory=set)
    ciudades: list[Any] = field(default_factory=list)

    # ==========================================
    # INVESTIGACIÓN (Única por Reino, vinculada a capital)
    # ==========================================
    laboratorio: Laboratorio | None = None
    investigaciones_completadas: set[str] = field(default_factory=set)

    # ==========================================
    # MÉTODOS DE GESTIÓN TERRITORIAL
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
        Si es la PRIMERA ciudad, establece capital y crea Laboratorio automáticamente.
        Devuelve True si tuvo éxito, False si alcanzó el límite.
        """
        if not self.puede_fundar_ciudad():
            print(f"⚠️ El reino de {self.nombre} ha alcanzado su límite de {self.get_limite_ciudades()} ciudades.")
            return False

        es_primera = len(self.ciudades) == 0
        self.ciudades.append(ciudad)

        # Creación automática de Laboratorio en la primera ciudad (capital)
        if es_primera and self.laboratorio is None:
            from src.economia.edificios.laboratorio import Laboratorio

            # Extracción segura del nombre de la ciudad
            nombre_ciudad: str
            if hasattr(ciudad, 'nombre') and isinstance(ciudad.nombre, str):
                nombre_ciudad = ciudad.nombre
            else:
                nombre_ciudad = str(ciudad)

            self.laboratorio = Laboratorio(nombre=f"Laboratorio Real de {nombre_ciudad}")
            print(f"🔬 Laboratorio creado automáticamente en capital: {nombre_ciudad}")

        return True

    # ==========================================
    # MÉTODOS DE INVESTIGACIÓN
    # ==========================================
    @property
    def capital(self) -> Any | None:
        """La primera ciudad fundada es la capital del reino."""
        return self.ciudades[0] if self.ciudades else None

    def tiene_laboratorio(self) -> bool:
        return self.laboratorio is not None

    def get_progreso_investigacion(self, total_tecnologias: int = 343) -> float:
        """Porcentaje de tecnologías completadas (0.0 a 100.0)."""
        if total_tecnologias <= 0:
            return 0.0
        return (len(self.investigaciones_completadas) / total_tecnologias) * 100.0

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        tipo = "Imperial" if self.es_imperial else "Vasallo/Satrapía"
        lab_status = "🔬 Activo" if self.laboratorio and self.laboratorio.esta_investigando else "⏸️ Sin lab"
        return (f"Reino de {self.nombre} ({tipo}) | "
                f"Territorios: {len(self.puntos_controlados)} | "
                f"Ciudades: {len(self.ciudades)}/{self.get_limite_ciudades()} | "
                f"{lab_status}")

# ==========================================
# BLOQUE DE PRUEBAS ACTUALIZADO
# ==========================================
if __name__ == "__main__":
    print("--- 🚀 Iniciando pruebas de Reino + Laboratorio ---\n")

    # 1. Creamos dos reinos distintos
    reino_emperador = Reino("Dominio Imperial de Aurelia", es_imperial=True)
    reino_satrapa = Reino("Satrapía de las Dunas")

    print(f"✅ {reino_emperador}")
    print(f"✅ {reino_satrapa}")

    # 2. Probamos la creación automática de Laboratorio en la capital
    print("\n--- 🔬 Prueba: Laboratorio en Capital ---")

    # Fundar primera ciudad en Satrapía → debe crear laboratorio
    resultado = reino_satrapa.fundar_ciudad("Oasis de Kharim")
    print(f"Fundar 'Oasis de Kharim': {'✅ Éxito' if resultado else '❌ Fallo'}")
    print(f"¿Tiene laboratorio? {reino_satrapa.tiene_laboratorio()}")
    print(f"Capital: {reino_satrapa.capital}")
    assert reino_satrapa.tiene_laboratorio(), "Debería tener laboratorio tras fundar capital"
    assert reino_satrapa.capital == "Oasis de Kharim", "Capital debería ser la primera ciudad"

    # Fundar segunda ciudad → NO debe crear otro laboratorio
    resultado2 = reino_satrapa.fundar_ciudad("Puerto de Sal")
    print(f"\nFundar 'Puerto de Sal': {'✅ Éxito' if resultado2 else '❌ Fallo'}")

    # Aserción de tipo para Pylance: garantiza que laboratorio no es None
    assert reino_satrapa.laboratorio is not None

    assert reino_satrapa.laboratorio.nombre == "Laboratorio Real de Oasis de Kharim", \
        "El laboratorio no debería cambiar al fundar segunda ciudad"
    print("✅ Laboratorio permanece vinculado a la capital original")

    # 3. Probamos el límite de ciudades (con laboratorio ya creado)
    print("\n--- 🏘️ Prueba: Expansión Urbana con Laboratorio ---")

    for i in range(2, 6):
        ciudad_mock = f"Aldea_{i}"

        # Intento en el reino Imperial (Límite 3) - Sin laboratorio aún
        if i <= 4:
            print(f"\nIntentando fundar {ciudad_mock} en Aurelia:")
            res_imp = reino_emperador.fundar_ciudad(ciudad_mock)
            if i == 2:  # Primera ciudad imperial → crea laboratorio
                assert reino_emperador.tiene_laboratorio()
                print(f"   🔬 Laboratorio imperial creado en {ciudad_mock}")

        # Intento en la Satrapía (Límite 5) - Ya tiene laboratorio
        print(f"Intentando fundar {ciudad_mock} en las Dunas:")
        reino_satrapa.fundar_ciudad(ciudad_mock)

    # Verificar límites respetados
    print(f"\n📊 Aurelia: {len(reino_emperador.ciudades)}/{reino_emperador.get_limite_ciudades()} ciudades")
    print(f"📊 Las Dunas: {len(reino_satrapa.ciudades)}/{reino_satrapa.get_limite_ciudades()} ciudades")

    # 4. Probamos estado de investigaciones
    print("\n--- 📜 Prueba: Estado de Investigaciones ---")
    print(f"Progreso Aurelia: {reino_emperador.get_progreso_investigacion():.1f}%")
    print(f"Progreso Las Dunas: {reino_satrapa.get_progreso_investigacion():.1f}%")

    # Simular investigación completada
    reino_satrapa.investigaciones_completadas.add("1.1.1_regadio_inundacion")
    reino_satrapa.investigaciones_completadas.add("2.1.1_talado")
    print(f"Tras completar 2 techs: {reino_satrapa.get_progreso_investigacion():.2f}%")
    assert len(reino_satrapa.investigaciones_completadas) == 2

    # 5. Probamos la asignación de puntos (Simulando un objeto Punto)
    print("\n--- 🗺️ Prueba: Control Territorial ---")

    class PuntoMock:
        def __init__(self):
            self.propietario: Any = None

    punto1 = PuntoMock()
    punto2 = PuntoMock()

    reino_satrapa.agregar_punto(punto1)
    reino_satrapa.agregar_punto(punto2)

    nombre_dueno = getattr(punto1.propietario, 'nombre', 'Desconocido')
    print(f"Punto 1 ahora pertenece a: {nombre_dueno}")
    print(f"Total de puntos controlados por las Dunas: {len(reino_satrapa.puntos_controlados)}")

    # 6. Resumen final
    print("\n--- 📋 Resumen Final ---")
    print(f"👑 {reino_emperador}")
    print(f"👑 {reino_satrapa}")

    print("\n--- ✅ Todas las pruebas pasaron correctamente ---")
