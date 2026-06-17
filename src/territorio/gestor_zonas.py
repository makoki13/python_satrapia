# src/territorio/gestor_zonas.py
"""
Gestor de zonas disponibles para el establecimiento de facciones.

Se encarga de generar, distribuir y asignar las zonas donde los jugadores
pueden fundar sus capitales al unirse a una partida. La distribución es
automática y se escala proporcionalmente al tamaño del mapa.

Distribución por defecto:
    - 1 IMPERIO en el centro (zona privilegiada)
    - 4 SATRAPÍAS en las diagonales (zonas intermedias)
    - 4 TRIBUS en las esquinas (zonas fronterizas)
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.core.coordenada import Coordenada
from src.territorio.faccion import TipoFaccion
from src.territorio.zona_disponible import ZonaDisponible

if TYPE_CHECKING:
    from src.territorio.mapa import Mapa


class GestorZonas:
    """
    Gestiona las zonas disponibles para facciones en un mapa.

    Las posiciones y radios se calculan como fracciones del tamaño del mapa,
    lo que garantiza una distribución equilibrada tanto en modo desarrollo
    (200x200) como en producción (1000x1000).
    """

    # ==========================================
    # FACTORES DE ESCALA (posiciones relativas al mapa)
    # ==========================================
    _POS_IMPERIO: tuple[float, float] = (0.50, 0.50)  # Centro exacto
    _POS_SATRAPIAS: list[tuple[float, float]] = [
        (0.25, 0.25), (0.25, 0.75),
        (0.75, 0.25), (0.75, 0.75),
    ]
    _POS_TRIBUS: list[tuple[float, float]] = [
        (0.12, 0.12), (0.12, 0.88),
        (0.88, 0.12), (0.88, 0.88),
    ]

    # Factores de escala para radios (relativos a min(ancho, alto))
    _RADIO_IMPERIO: float = 0.25
    _RADIO_SATRAPIA: float = 0.15
    _RADIO_TRIBU: float = 0.10

    # ==========================================
    # CONSTRUCTOR
    # ==========================================
    def __init__(self, mapa: Mapa):
        """
        Inicializa el gestor generando las zonas para el mapa dado.

        Args:
            mapa: Mapa sobre el que se distribuirán las zonas.

        Raises:
            ValueError: Si la generación produce zonas solapadas.
        """
        self.mapa = mapa
        self.zonas: list[ZonaDisponible] = self._generar_zonas()

        if self._hay_solapamientos():
            raise ValueError(
                "Se detectaron zonas solapadas durante la generación. "
                "Revisa los factores de escala."
            )

    # ==========================================
    # GENERACIÓN INTERNA
    # ==========================================
    def _generar_zonas(self) -> list[ZonaDisponible]:
        """Genera las zonas escaladas al tamaño del mapa."""
        ancho, alto = self.mapa.dimensiones
        escala = min(ancho, alto)
        zonas: list[ZonaDisponible] = []

        # 1. IMPERIO (1 en el centro)
        cx = int(ancho * self._POS_IMPERIO[0])
        cy = int(alto * self._POS_IMPERIO[1])
        radio = int(escala * self._RADIO_IMPERIO)
        zonas.append(ZonaDisponible(
            Coordenada(cx, cy),
            radio=radio,
            tipo_faccion=TipoFaccion.IMPERIO,
        ))

        # 2. SATRAPÍAS (4 en diagonales)
        radio_sat = int(escala * self._RADIO_SATRAPIA)
        for px, py in self._POS_SATRAPIAS:
            zonas.append(ZonaDisponible(
                Coordenada(int(ancho * px), int(alto * py)),
                radio=radio_sat,
                tipo_faccion=TipoFaccion.SATRAPIA,
            ))

        # 3. TRIBUS (4 en esquinas)
        radio_trib = int(escala * self._RADIO_TRIBU)
        for px, py in self._POS_TRIBUS:
            zonas.append(ZonaDisponible(
                Coordenada(int(ancho * px), int(alto * py)),
                radio=radio_trib,
                tipo_faccion=TipoFaccion.TRIBU,
            ))

        return zonas

    def _hay_solapamientos(self) -> bool:
        """
        Verifica si hay solapamientos entre las zonas.

        Dos zonas se solapan si la distancia Manhattan entre sus centros
        es menor que la suma de sus radios.
        """
        for i, z1 in enumerate(self.zonas):
            for z2 in self.zonas[i + 1:]:
                dist = z1.distancia_al_centro(z2.coordenada_central)
                if dist < (z1.radio + z2.radio):
                    return True
        return False

    # ==========================================
    # ASIGNACIÓN DE ZONAS
    # ==========================================
    def asignar_zona(self, tipo_faccion: TipoFaccion) -> ZonaDisponible | None:
        """
        Asigna la primera zona libre del tipo solicitado.

        Args:
            tipo_faccion: Tipo de facción que ocupará la zona.

        Returns:
            La zona asignada (ya marcada como ocupada), o None si no hay libres.
        """
        for zona in self.zonas:
            if zona.tipo_faccion == tipo_faccion and not zona.ocupada:
                zona.ocupar()
                return zona
        return None

    def liberar_zona(self, zona: ZonaDisponible) -> bool:
        """
        Libera una zona ocupada.

        Args:
            zona: Zona a liberar.

        Returns:
            True si se liberó, False si ya estaba libre o no pertenece al gestor.
        """
        if zona not in self.zonas:
            return False
        return zona.liberar()

    def liberar_todas(self) -> int:
        """
        Libera todas las zonas ocupadas. Útil al reiniciar una partida.

        Returns:
            Número de zonas que han sido liberadas.
        """
        liberadas = 0
        for zona in self.zonas:
            if zona.ocupada:
                zona.liberar()
                liberadas += 1
        return liberadas

    # ==========================================
    # CONSULTAS
    # ==========================================
    def zonas_disponibles(
        self, tipo_faccion: TipoFaccion | None = None
    ) -> list[ZonaDisponible]:
        """
        Devuelve las zonas no ocupadas, opcionalmente filtradas por tipo.

        Args:
            tipo_faccion: Si se proporciona, filtra por tipo. Si None, devuelve todas.
        """
        resultado = [z for z in self.zonas if not z.ocupada]
        if tipo_faccion is not None:
            resultado = [z for z in resultado if z.tipo_faccion == tipo_faccion]
        return resultado

    def zonas_ocupadas(self) -> list[ZonaDisponible]:
        """Devuelve todas las zonas actualmente ocupadas."""
        return [z for z in self.zonas if z.ocupada]

    def obtener_zona_en(self, coordenada: Coordenada) -> ZonaDisponible | None:
        """
        Busca la zona que contiene una coordenada específica.

        Args:
            coordenada: Coordenada a buscar.

        Returns:
            La zona que contiene la coordenada, o None si ninguna la contiene.
        """
        for zona in self.zonas:
            if zona.contiene(coordenada):
                return zona
        return None

    # ==========================================
    # PROPIEDADES
    # ==========================================
    @property
    def total_zonas(self) -> int:
        """Número total de zonas gestionadas."""
        return len(self.zonas)

    @property
    def total_disponibles(self) -> int:
        """Número de zonas actualmente libres."""
        return len(self.zonas_disponibles())

    @property
    def total_ocupadas(self) -> int:
        """Número de zonas actualmente ocupadas."""
        return len(self.zonas_ocupadas())

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        return (
            f"GestorZonas[{self.mapa.nombre}]: "
            f"{self.total_disponibles}/{self.total_zonas} disponibles"
        )

    def resumen(self) -> str:
        """Devuelve un resumen multilínea del estado de todas las zonas."""
        lineas = [f"📍 Zonas del mapa '{self.mapa.nombre}':"]
        for zona in self.zonas:
            lineas.append(f"   • {zona}")
        return "\n".join(lineas)


# ==========================================
# BLOQUE DE PRUEBAS
# ==========================================
if __name__ == "__main__":
    print("--- 🗺️ Probando GestorZonas ---\n")

    from src.territorio.mapa import Mapa

    # 1. Probar con mapa de desarrollo (200x200)
    print("--- Mapa de DESARROLLO (200x200) ---")
    mapa_dev = Mapa("Mapa Dev", modo_desarrollo=True)
    gestor_dev = GestorZonas(mapa_dev)

    print(gestor_dev.resumen())
    print(f"\n   Total: {gestor_dev.total_zonas} zonas "
          f"({gestor_dev.total_disponibles} disponibles)")

    assert gestor_dev.total_zonas == 9, "Debe haber 9 zonas (1+4+4)"
    assert gestor_dev.total_disponibles == 9, "Todas deben estar libres al inicio"

    # 2. Asignar zonas por tipo
    print("\n--- Asignando zonas ---")
    z_imp = gestor_dev.asignar_zona(TipoFaccion.IMPERIO)
    assert z_imp is not None, "Debe haber un IMPERIO libre"
    print(f"   ✅ Asignado IMPERIO: {z_imp}")

    z_sat1 = gestor_dev.asignar_zona(TipoFaccion.SATRAPIA)
    z_sat2 = gestor_dev.asignar_zona(TipoFaccion.SATRAPIA)
    assert z_sat1 is not None and z_sat2 is not None
    print("   ✅ Asignadas 2 SATRAPÍAS")

    z_trib = gestor_dev.asignar_zona(TipoFaccion.TRIBU)
    assert z_trib is not None
    print(f"   ✅ Asignada 1 TRIBU: {z_trib}")

    assert gestor_dev.total_ocupadas == 4, "Debe haber 4 zonas ocupadas"
    assert gestor_dev.total_disponibles == 5, "Debe haber 5 zonas disponibles"

    # 3. Probar agotamiento
    print("\n--- Probando agotamiento de IMPERIOS ---")
    z_imp2 = gestor_dev.asignar_zona(TipoFaccion.IMPERIO)
    assert z_imp2 is None, "No debe haber más IMPERIOS libres"
    print("   ✅ Correctamente None al no haber más IMPERIOS")

    # 4. Probar obtener_zona_en
    print("\n--- Probando obtener_zona_en() ---")
    zona_en_centro = gestor_dev.obtener_zona_en(Coordenada(100, 100))
    assert zona_en_centro is not None
    assert zona_en_centro.tipo_faccion == TipoFaccion.IMPERIO
    print(f"   ✅ Centro del mapa → {zona_en_centro.tipo_faccion.value}")

    zona_fuera = gestor_dev.obtener_zona_en(Coordenada(100, 0))
    print(f"   ✅ Coordenada (100, 0) → {zona_fuera}")

    # 5. Probar liberación
    print("\n--- Probando liberación ---")
    assert gestor_dev.liberar_zona(z_imp) is True
    assert z_imp.ocupada is False
    print(f"   ✅ Zona liberada: {z_imp}")

    assert gestor_dev.total_ocupadas == 3

    # 6. Probar liberar_todas
    print("\n--- Probando liberar_todas() ---")
    liberadas = gestor_dev.liberar_todas()
    assert liberadas == 3, f"Deberían liberarse 3, se liberaron {liberadas}"
    assert gestor_dev.total_ocupadas == 0
    assert gestor_dev.total_disponibles == 9
    print(f"   ✅ Liberadas {liberadas} zonas. Total disponibles: {gestor_dev.total_disponibles}")

    # 7. Probar con mapa de producción (1000x1000)
    print("\n--- Mapa de PRODUCCIÓN (1000x1000) ---")
    mapa_prod = Mapa("Mapa Producción", modo_desarrollo=False)
    gestor_prod = GestorZonas(mapa_prod)

    print(gestor_prod.resumen())

    z_imp_prod = gestor_prod.asignar_zona(TipoFaccion.IMPERIO)
    assert z_imp_prod is not None
    assert z_imp_prod.coordenada_central == Coordenada(500, 500), \
        "Centro debe estar en (500, 500)"
    assert z_imp_prod.radio == 250, "Radio debe ser 250 (1000 * 0.25)"
    print(f"   ✅ Escalado correcto en producción: {z_imp_prod}")

    print("\n✅ Todas las pruebas de GestorZonas pasaron correctamente.")
    print("\n--- Fin de las pruebas ---")
