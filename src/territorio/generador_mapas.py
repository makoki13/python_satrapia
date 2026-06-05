# src/territorio/generador_mapas.py
import random

from src.core.coordenada import Coordenada
from src.territorio.mapa import Mapa
from src.territorio.punto import Punto
from src.territorio.terreno import TipoTerreno
from src.territorio.zona_disponible import TipoFaccion, ZonaDisponible


class GeneradorMapas:
    """
    Genera la geografía del mundo de Satrapia.
    Crea un continente central con biomas y define las zonas disponibles
    para que los jugadores funden sus facciones.
    """

    def __init__(self, mapa: Mapa):
        self.mapa = mapa
        self.zonas_disponibles: list[ZonaDisponible] = []

        # Parámetros de generación
        self.centro_x = mapa.limite_x // 2
        self.centro_y = mapa.limite_y // 2
        self.radio_maximo = min(mapa.limite_x, mapa.limite_y) // 2

    def generar_mundo(self) -> None:
        """
        Orquesta la generación completa del mapa.
        1. Pinta el terreno (biomas).
        2. Define las zonas disponibles para jugadores.
        """
        print(f"🌍 Generando mundo de {self.mapa.limite_x}x{self.mapa.limite_y} km...")
        self._pintar_biomas()
        self._definir_zonas_candidatas()
        print(f"✅ Mundo generado. {len(self.zonas_disponibles)} zonas disponibles para facciones.")

    def _pintar_biomas(self) -> None:
        """
        Asigna el tipo de terreno a cada punto del mapa.
        Usa la distancia al centro para crear un continente con costas naturales.
        """
        for x in range(self.mapa.limite_x):
            for y in range(self.mapa.limite_y):
                # Calcular distancia al centro (aproximación euclídea simple)
                dx = x - self.centro_x
                dy = y - self.centro_y
                distancia = (dx**2 + dy**2)**0.5

                # Normalizar distancia (0 = centro, 1 = borde del círculo máximo)
                dist_normalizada = distancia / self.radio_maximo

                # Añadir un poco de ruido aleatorio para que las costas no sean perfectas
                ruido = random.uniform(-0.1, 0.1)
                dist_final = dist_normalizada + ruido

                # Asignar terreno según la distancia
                terreno = self._elegir_terreno(dist_final)

                # Crear el punto y añadirlo al mapa
                punto = Punto(
                    coordenada=Coordenada(x, y),
                    terreno=terreno
                )
                self.mapa.puntos[punto.coordenada] = punto

    def _elegir_terreno(self, distancia_normalizada: float) -> TipoTerreno:
        """
        Decide qué terreno poner según qué tan lejos esté del centro.
        distancia_normalizada: 0.0 (centro) a 1.0+ (fuera del continente).
        """
        # Más allá del continente: Océano
        if distancia_normalizada > 0.95:
            return TipoTerreno.MAR

        # Bordes del continente: Costa/Mar poco profundo
        if distancia_normalizada > 0.85:
            # Aleatoriedad para crear golfos y penínsulas
            return TipoTerreno.MAR if random.random() < 0.7 else TipoTerreno.LLANURA

        # Fronteras lejanas: Montañas y Desiertos (barreras naturales)
        if distancia_normalizada > 0.65:
            return random.choice([TipoTerreno.MONTAÑA, TipoTerreno.DESIERTO, TipoTerreno.ESTEPA])

        # Zonas intermedias: Bosques y Colinas
        if distancia_normalizada > 0.30:
            return random.choice([TipoTerreno.BOSQUE, TipoTerreno.COLINA, TipoTerreno.LLANURA])

        # Centro del continente: Llanuras fértiles (el corazón del imperio)
        return random.choice([TipoTerreno.LLANURA, TipoTerreno.LLANURA, TipoTerreno.COLINA])

    def _definir_zonas_candidatas(self) -> None:
        """
        Crea los 'pools' de zonas disponibles distribuidas simétricamente.
        - 4 zonas cardinales (Imperios)
        - 4 zonas diagonales (Satrapías)
        - 4 zonas fronterizas (Tribus nómadas)
        """
        # Factores de distancia desde el centro (0 = centro, 1 = borde)
        dist_imperio = 0.40   # Zonas fértiles pero no en el centro exacto
        dist_satrapia = 0.60  # Zonas intermedias
        dist_tribu = 0.80     # Zonas fronterizas (estepas)

        # Ángulos para distribución simétrica
        angulos_cardinales = [0, 90, 180, 270]      # N, E, S, O
        angulos_diagonales = [45, 135, 225, 315]    # NE, NO, SE, SO

        # 1. Zonas para Imperios (Cardinales)
        for angulo in angulos_cardinales:
            coord = self._coordenada_desde_angulo(angulo, dist_imperio)
            self.zonas_disponibles.append(
                ZonaDisponible(coord, radio=40, tipo_faccion=TipoFaccion.IMPERIO)
            )

        # 2. Zonas para Satrapías (Diagonales)
        for angulo in angulos_diagonales:
            coord = self._coordenada_desde_angulo(angulo, dist_satrapia)
            self.zonas_disponibles.append(
                ZonaDisponible(coord, radio=30, tipo_faccion=TipoFaccion.SATRAPIA)
            )

        # 3. Zonas para Tribus (Fronteras, usando ángulos intermedios)
        angulos_frontera = [22, 112, 202, 292]  # Desplazados para no solapar
        for angulo in angulos_frontera:
            coord = self._coordenada_desde_angulo(angulo, dist_tribu)
            self.zonas_disponibles.append(
                ZonaDisponible(coord, radio=50, tipo_faccion=TipoFaccion.TRIBU)
            )

    def _coordenada_desde_angulo(self, angulo_grados: float, factor_distancia: float) -> Coordenada:
        """
        Calcula una coordenada en el mapa dado un ángulo y una distancia relativa al centro.
        """
        import math
        angulo_rad = math.radians(angulo_grados)
        radio_px = self.radio_maximo * factor_distancia

        x = int(self.centro_x + radio_px * math.cos(angulo_rad))
        y = int(self.centro_y + radio_px * math.sin(angulo_rad))

        # Asegurar que está dentro de los límites
        x = max(0, min(x, self.mapa.limite_x - 1))
        y = max(0, min(y, self.mapa.limite_y - 1))

        return Coordenada(x, y)

    def asignar_zona_a_jugador(self, rol_jugador) -> ZonaDisponible | None:
        """
        Busca una zona disponible adecuada para el rol del jugador.
        La marca como ocupada y la devuelve.
        """
        from src.usuarios.jugador import Rol

        # Mapear rol a tipo de facción requerida
        if rol_jugador == Rol.EMPERADOR:
            tipo_buscado = TipoFaccion.IMPERIO
        elif rol_jugador == Rol.SATRAPA:
            tipo_buscado = TipoFaccion.SATRAPIA
        elif rol_jugador == Rol.JEFE:
            tipo_buscado = TipoFaccion.TRIBU
        else:
            return None

        # Buscar la primera zona libre de ese tipo
        for zona in self.zonas_disponibles:
            if zona.tipo_faccion == tipo_buscado and not zona.ocupada:
                zona.ocupada = True
                print(f"📍 Asignada zona {zona.tipo_faccion.value} en {zona.coordenada_central}")
                return zona

        print(f"⚠️ No quedan zonas disponibles para {tipo_buscado.value}")
        return None


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🌍 Probando Generador de Mapas ---\n")

    # Usamos modo desarrollo para que sea rápido (200x200 = 40,000 puntos)
    mapa_test = Mapa(nombre="Mundo de Prueba", modo_desarrollo=True)

    generador = GeneradorMapas(mapa_test)
    generador.generar_mundo()

    # Estadísticas del mapa generado
    print("\n📊 Estadísticas del mapa:")
    print(f"   Total de puntos: {len(mapa_test.puntos)}")
    print(f"   Zonas candidatas creadas: {len(generador.zonas_disponibles)}")

    # Contar biomas
    biomas = {}
    for punto in mapa_test.puntos.values():
        nombre = punto.terreno.nombre_legible
        biomas[nombre] = biomas.get(nombre, 0) + 1

    print("\n🌳 Distribución de biomas:")
    for bioma, cantidad in sorted(biomas.items(), key=lambda x: x[1], reverse=True):
        porcentaje = (cantidad / len(mapa_test.puntos)) * 100
        print(f"   {bioma:20}: {cantidad:6} ({porcentaje:5.1f}%)")

    print("\n📍 Zonas disponibles:")
    for zona in generador.zonas_disponibles:
        print(f"   {zona}")

    print("\n--- Fin de las pruebas ---")
