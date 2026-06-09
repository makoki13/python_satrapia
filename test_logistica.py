# test_logistica.py
"""
Script de prueba del sistema logístico completo:
1. Genera un mapa con biomas
2. Calcula rutas entre varios puntos (incluyendo rutas imposibles)
3. Crea transportes de diferentes tipos
4. Simula ticks del servidor hasta que llegan
5. Verifica transferencias y destrucción
"""

from src.core.coordenada import Coordenada
from src.economia.silo import TipoRecurso
from src.logistica.gestor_transportes import GestorTransportes
from src.logistica.gps import GPS
from src.logistica.transporte import TipoTransporte
from src.territorio.generador_mapas import GeneradorMapas
from src.territorio.mapa import Mapa


def encontrar_punto_transitable(mapa: Mapa, centro: Coordenada, radio: int = 30) -> Coordenada | None:
    """Busca un punto transitable cercano al centro dado."""
    for dx in range(-radio, radio + 1):
        for dy in range(-radio, radio + 1):
            coord = Coordenada(centro.x + dx, centro.y + dy)
            punto = mapa.puntos.get(coord)
            if punto and punto.es_transitable():
                return coord
    return None


def test_gps_rutas(mapa: Mapa):
    """Prueba el cálculo de rutas en diferentes escenarios."""
    print("=" * 60)
    print("🗺️  PRUEBA 1: GPS - Cálculo de Rutas")
    print("=" * 60)

    centro = Coordenada(mapa.limite_x // 2, mapa.limite_y // 2)

    # Buscar puntos transitables en diferentes zonas del mapa
    origen = encontrar_punto_transitable(mapa, centro)
    destino_cerca = encontrar_punto_transitable(mapa, centro, radio=15)
    destino_lejos = encontrar_punto_transitable(mapa, Coordenada(centro.x + 60, centro.y + 60), radio=20)
    destino_mar = Coordenada(0, 0)  # Esquina del mapa, probablemente mar

    assert origen is not None, "No se encontró punto transitable de origen"
    assert destino_cerca is not None, "No se encontró punto transitable cercano"
    assert destino_lejos is not None, "No se encontró punto transitable lejano"

    # test_logistica.py (correcciones en test_gps_rutas)

    # Test 1: Ruta corta
    ruta_corta = GPS.calcular_ruta(mapa, origen, destino_cerca)
    print(f"\n✅ Ruta corta ({origen} → {destino_cerca}):")
    print(f"   Waypoints: {len(ruta_corta) if ruta_corta is not None else 'SIN RUTA'}")
    assert ruta_corta is not None, "Debería existir ruta corta"
    assert ruta_corta[0] == origen, "Primer waypoint debe ser origen"
    assert ruta_corta[-1] == destino_cerca, "Último waypoint debe ser destino"

    # Test 2: Ruta larga
    ruta_larga = GPS.calcular_ruta(mapa, origen, destino_lejos)
    print(f"\n✅ Ruta larga ({origen} → {destino_lejos}):")
    print(f"   Waypoints: {len(ruta_larga) if ruta_larga is not None else 'SIN RUTA'}")
    assert ruta_larga is not None, "Debería existir ruta larga"
    assert len(ruta_larga) > len(ruta_corta), "Ruta larga debe tener más waypoints"

    # Test 3: Ruta al mismo punto
    ruta_mismo = GPS.calcular_ruta(mapa, origen, origen)
    print(f"\n✅ Ruta al mismo punto: {len(ruta_mismo) if ruta_mismo is not None else 'SIN RUTA'} waypoint(s)")
    assert ruta_mismo is not None, "Debería existir ruta al mismo punto"
    assert ruta_mismo == [origen], "Ruta al mismo punto debe ser solo el origen"

    # Test 4: Ruta imposible (hacia el mar)
    ruta_imposible = GPS.calcular_ruta(mapa, origen, destino_mar)
    print(f"\n{'✅' if ruta_imposible is None else '⚠️'} Ruta imposible ({origen} → {destino_mar}):")
    print(f"   Resultado: {'Sin ruta (correcto)' if ruta_imposible is None else f'{len(ruta_imposible)} waypoints'}")

    print("\n✅ Todas las pruebas de GPS pasaron.\n")
    return origen, destino_cerca, destino_lejos


def test_gestor_transportes(mapa: Mapa, origen: Coordenada, destino: Coordenada):
    """Prueba la creación, movimiento y llegada de transportes."""
    print("=" * 60)
    print("🚚 PRUEBA 2: GestorTransportes - Ciclo de Vida Completo")
    print("=" * 60)

    gestor = GestorTransportes()

    # Crear transporte de recursos
    exito, msg, t_recursos = gestor.crear_transporte(
        mapa=mapa,
        origen=origen,
        destino=destino,
        tipo=TipoTransporte.RECURSOS,
        tipo_recurso=TipoRecurso.COMIDA,
        cantidad=100,
        velocidad=2,
        propietario_id="reino_test",
    )
    print(f"\n{msg}")
    assert exito and t_recursos is not None, "Debería crearse transporte de recursos"
    print(f"   📦 {t_recursos}")

    # Crear transporte militar (más lento)
    exito2, msg2, t_ejercito = gestor.crear_transporte(
        mapa=mapa,
        origen=origen,
        destino=destino,
        tipo=TipoTransporte.EJERCITO,
        velocidad=1,
        propietario_id="reino_test",
        metadata={"ejercito_id": "legion_1"},
    )
    print(f"{msg2}")
    assert exito2 and t_ejercito is not None, "Debería crearse transporte militar"
    print(f"   ⚔️ {t_ejercito}")

    # Intentar crear transporte a destino imposible
    exito3, msg3, _ = gestor.crear_transporte(
        mapa=mapa,
        origen=origen,
        destino=Coordenada(0, 0),
        tipo=TipoTransporte.RECURSOS,
    )
    print(f"{msg3}")
    assert not exito3, "No debería crearse transporte sin ruta viable"

    print(f"\n📊 Transportes activos: {gestor.total_activos}")
    assert gestor.total_activos == 2, "Debería haber exactamente 2 transportes"

    # Simular ticks hasta que todos lleguen
    print("\n--- Simulación de Ticks ---")
    max_ticks = 200
    eventos_totales = []

    for tick in range(1, max_ticks + 1):
        eventos = gestor.avanzar_todos(mapa)

        for evento in eventos:
            print(f"   Tick {tick}: {evento.mensaje}")
            print(f"      Tipo: {evento.transporte.tipo.value} | "
                  f"Carga: {evento.transporte.tipo_recurso}×{evento.transporte.cantidad}")
            eventos_totales.append(evento)
            # Simular transferencia y eliminación
            gestor.eliminar(evento.transporte.id)

        if gestor.total_activos == 0:
            print(f"\n✅ Todos los transportes llegaron en {tick} ticks.")
            break

        if tick % 10 == 0:
            print(f"   Tick {tick}: {gestor.total_activos} transportes activos")

    assert gestor.total_activos == 0, "Todos los transportes deberían haber llegado"
    assert len(eventos_totales) == 2, "Debería haber 2 eventos de llegada"

    # Verificar consultas
    print(f"\n📊 Resumen final: {gestor.resumen()}")
    print("\n✅ Todas las pruebas de GestorTransportes pasaron.\n")


def main():
    print("\n🧪 === SUITE DE PRUEBAS LOGÍSTICAS ===\n")

    # Generar mapa de prueba (modo desarrollo = 200x200)
    print("🌍 Generando mapa de prueba (200x200)...")
    mapa = Mapa(nombre="Mapa Logística Test", modo_desarrollo=True)
    generador = GeneradorMapas(mapa)
    generador.generar_mundo()
    print(f"   ✅ Mapa generado: {len(mapa.puntos)} puntos\n")

    # Ejecutar pruebas
    origen, destino_cerca, destino_lejos = test_gps_rutas(mapa)
    test_gestor_transportes(mapa, origen, destino_lejos)

    print("=" * 60)
    print("🎉 TODAS LAS PRUEBAS LOGÍSTICAS PASARON CORRECTAMENTE")
    print("=" * 60)


if __name__ == "__main__":
    main()
