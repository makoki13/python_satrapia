# test_disparadores_rapido.py
"""
Prueba rápida de Disparadores Automáticos de Transporte.
Valida: Llenado 100% → Creación de transporte → Vaciado de silo.
No requiere FastAPI ni WebSocket. Ejecución pura en memoria.
"""
from src.config.game_config import GameConfig
from src.core.coordenada import Coordenada
from src.core.server_tick import ServerTick
from src.economia.almacen import Almacen
from src.economia.silo import Silo, TipoRecurso
from src.gestion.partida import Partida
from src.logistica.gestor_transportes import GestorTransportes
from src.territorio.ciudad import Ciudad
from src.territorio.reino import Reino


def crear_partida_minima() -> tuple[Partida, GameConfig]:
    """Crea una partida con 2 ciudades: productora y capital."""
    config = GameConfig()

    # ✅ CORREGIDO: Partida solo requiere nombre y creador_id
    # El id se genera automáticamente (UUID)
    # El mapa se crea internamente en __post_init__
    from src.gestion.partida import ConfiguracionMapa

    partida = Partida(
        nombre="Test Disparadores",
        creador_id="test-runner",
        configuracion_mapa=ConfiguracionMapa.modo_desarrollo(),
    )

    # Crear reino y ciudades
    reino = Reino(nombre="Testlandia")

    # Capital PRIMERO (se convierte en reino.capital automáticamente)
    capital = Ciudad(
        nombre="Capital Real",
        ubicacion=Coordenada(5, 5),
        reino_propietario=reino,
    )
    capital.almacen = Almacen(nombre="Almacén Capital")
    capital.almacen.agregar_silo(
        Silo(nombre="Silo Oro Capital", tipo_recurso=TipoRecurso.ORO, capacidad_base=500)
    )

    # Ciudad productora DESPUÉS
    ciudad_mina = Ciudad(
        nombre="Mina de Oro",
        ubicacion=Coordenada(0, 0),
        reino_propietario=reino,
    )
    silo_oro = Silo(nombre="Silo Oro Mina", tipo_recurso=TipoRecurso.ORO, capacidad_base=100)
    ciudad_mina.almacen = Almacen(nombre="Almacén Mina")
    ciudad_mina.almacen.agregar_silo(silo_oro)

    # Configurar reino usando API pública (orden importa)
    reino.fundar_ciudad(capital)       # Índice 0 → capital
    reino.fundar_ciudad(ciudad_mina)   # Índice 1

    # Asignar entidades a la partida
    partida.reinos = [reino]
    partida.ciudades = [ciudad_mina, capital]
    partida.gestor_transportes = GestorTransportes()

        # ==========================================
    # CONFIGURACIÓN DEL MAPA PARA GPS (CRÍTICO)
    # ==========================================

    # 1. Registrar las ciudades como puntos en el mapa
    partida.mapa.puntos[capital.ubicacion] = capital
    partida.mapa.puntos[ciudad_mina.ubicacion] = ciudad_mina

    # 2. Crear puntos "tierra" transitables entre (0,0) y (5,5)
    # El GPS necesita nodos intermedios para saltar de uno a otro.
    # Rellenamos el rectángulo entre ambas coordenadas.
    from src.territorio.punto import Punto

    # 1. Registrar las ciudades como puntos en el mapa
    # Las ciudades deben ser puntos transitables para que el GPS las use como nodos
    partida.mapa.puntos[capital.ubicacion] = Punto(
        coordenada=capital.ubicacion,
        estructura=capital,
        propietario=reino,
    )
    partida.mapa.puntos[ciudad_mina.ubicacion] = Punto(
        coordenada=ciudad_mina.ubicacion,
        estructura=ciudad_mina,
        propietario=reino,
    )

    # 2. Rellenar el rectángulo entre (0,0) y (5,5) con llanuras transitables
    # El GPS A* necesita nodos adyacentes conectados para trazar ruta
    for x in range(0, 6):
        for y in range(0, 6):
            coord = Coordenada(x, y)
            if coord not in partida.mapa.puntos:
                partida.mapa.puntos[coord] = Punto(coordenada=coord)
                # LLANURA por defecto → transitable=True, coste_movimiento bajo

    return partida, config


def test_disparador_automatico():
    print("=" * 60)
    print("🚛 TEST RÁPIDO: Disparadores Automáticos")
    print("=" * 60)

    partida, config = crear_partida_minima()

    assert partida.gestor_transportes is not None, "El gestor de transportes debe estar inicializado"

    mina = partida.ciudades[0]
    capital = partida.ciudades[1]

    # PASO 1: Verificar estado inicial
    stock_inicial = mina.almacen.stock_total(TipoRecurso.ORO)
    transportes_iniciales = partida.gestor_transportes.total_activos
    print("\n📊 Estado inicial:")
    print(f"   Stock mina: {stock_inicial}/100")
    print(f"   Transportes activos: {transportes_iniciales}")
    assert stock_inicial == 0, "El silo debería empezar vacío"
    assert transportes_iniciales == 0, "No debería haber transportes"

    # PASO 2: Llenar silo al 100% artificialmente
    exito, cantidad, msg = mina.almacen.agregar_recurso(TipoRecurso.ORO, 100, config)
    assert exito, f"Fallo al llenar silo: {msg}"
    print(f"\n📦 Silo llenado: +{cantidad} oro → {mina.almacen.stock_total(TipoRecurso.ORO)}/100")

    # PASO 3: Ejecutar 1 tick (debe activar disparador)
    tick = ServerTick(partida, config, arbol=None)  # type: ignore[arg-type]

    # DEBUG: Verificar estado real antes del disparador
    silo = mina.almacen.obtener_silo(TipoRecurso.ORO)
    assert silo is not None
    cap_efectiva = silo.get_capacidad_maxima(config)
    print(f"\n🔍 DEBUG: stock={silo.stock_actual}, capacidad_base={silo.capacidad_base}, "
          f"capacidad_efectiva={cap_efectiva}, lleno={silo.esta_lleno(config)}")

    # DEBUG: Verificar si existe ruta
    from src.logistica.gps import GPS
    ruta = GPS.calcular_ruta(partida.mapa, mina.ubicacion, capital.ubicacion)
    print(f"🔍 DEBUG: Ruta (0,0)→(5,5): {'✅ Viable' if ruta else '❌ NO VIABLE'}")
    print(f"🔍 DEBUG: Mapa límites: {partida.mapa.limite_x}x{partida.mapa.limite_y}")


    resumen = tick._procesar_disparadores_automaticos()

    # PASO 4: Verificar resultados
    stock_final = mina.almacen.stock_total(TipoRecurso.ORO)
    transportes_finales = partida.gestor_transportes.total_activos

    print("\n⚙️ Tras ejecutar disparadores:")
    print(f"   Stock mina: {stock_final}/100")
    print(f"   Transportes activos: {transportes_finales}")
    print(f"   Eventos generados: {len(resumen)}")

    # Assertions críticas
    assert len(resumen) == 1, f"Debería generarse 1 evento, se generaron {len(resumen)}"
    assert resumen[0]["tipo"] == "transporte_automatico_creado"
    assert resumen[0]["cantidad"] == 100, f"Debería enviar 100, envió {resumen[0]['cantidad']}"
    assert resumen[0]["origen"] == "Mina de Oro"
    assert resumen[0]["destino"] == "Capital Real"

    assert stock_final == 0, f"El silo debería vaciarse a 0, tiene {stock_final}"
    assert transportes_finales == 1, f"Debería haber 1 transporte activo, hay {transportes_finales}"

    # Verificar que el transporte tiene la ruta correcta
    transporte = list(partida.gestor_transportes._por_id.values())[0]
    assert transporte.origen == Coordenada(0, 0)
    assert transporte.destino == Coordenada(5, 5)
    assert transporte.tipo_recurso == TipoRecurso.ORO
    assert transporte.cantidad == 100

    print("\n✅ TEST PASADO: Disparador automático funciona correctamente")
    print("   ✓ Umbral 100% respetado")
    print("   ✓ Transporte creado con ruta válida")
    print("   ✓ Silo vaciado completamente")
    print("   ✓ Evento emitido con datos correctos")
    print("=" * 60)


def test_no_disparo_si_no_lleno():
    """Verifica que NO se crea transporte si el silo no está al 100%."""
    print("\n🔒 TEST NEGATIVO: Sin disparo si < 100%")

    partida, config = crear_partida_minima()

    assert partida.gestor_transportes is not None

    mina = partida.ciudades[0]

    # Llenar solo al 80%
    mina.almacen.agregar_recurso(TipoRecurso.ORO, 80, config)

    tick = ServerTick(partida, config, arbol=None)  # type: ignore[arg-type]
    eventos = tick._procesar_disparadores_automaticos()

    assert len(eventos) == 0, f"No debería haber eventos con 80%, hubo {len(eventos)}"
    assert partida.gestor_transportes.total_activos == 0
    assert mina.almacen.stock_total(TipoRecurso.ORO) == 80

    print("   ✅ Correcto: No se dispara con 80% de capacidad")


if __name__ == "__main__":
    test_disparador_automatico()
    test_no_disparo_si_no_lleno()
    print("\n🎉 TODAS LAS PRUEBAS RÁPIDAS PASARON\n")
