# test_validacion_bloque1.py
"""
Script de validación del piloto Bloque 1 (Alimentación).

Verifica:
1. Carga sin errores estructurales en ArbolInvestigaciones
2. Todos los efectos apuntan a parámetros existentes en REGISTRO_PARAMETROS
3. Las 7 tecnologías de nivel 1 aparecen en get_nivel_1_disponibles()
4. Los costes escalan correctamente por nivel
5. La cadena padre-hijo es coherente en cada subrama
6. Los parámetros lógicos se desbloquean correctamente
"""
from src.config.parametros_registro import REGISTRO_PARAMETROS, get_parametro
from src.investigacion.arbol_investigaciones import ArbolInvestigaciones
from src.investigacion.datos.bloque_1_alimentacion import TECNOLOGIAS_BLOQUE_1


def test_carga_arbol():
    """Verifica que el árbol se construye sin errores estructurales."""
    print("=" * 60)
    print("🌳 TEST 1: Carga del Árbol de Investigaciones")
    print("=" * 60)

    arbol = ArbolInvestigaciones.construir(TECNOLOGIAS_BLOQUE_1)

    assert arbol.total_tecnologias == 49, f"Esperadas 49 tecnologías, encontradas {arbol.total_tecnologias}"
    assert arbol.total_bloques == 1, f"Esperado 1 bloque, encontrados {arbol.total_bloques}"

    resumen = arbol.resumen()
    print(f"\n📊 Resumen: {resumen}")
    print("✅ TEST 1 PASADO: Árbol cargado correctamente con 49 tecnologías.\n")
    return arbol


def test_efectos_vinculados_a_parametros(arbol):
    """Verifica que TODOS los efectos referencian parámetros existentes."""
    print("=" * 60)
    print("🔗 TEST 2: Vinculación Efectos → Parámetros")
    print("=" * 60)

    ids_parametros_validos = set(REGISTRO_PARAMETROS.keys())
    errores: list[str] = []

    for tech in arbol:
        for efecto in tech.efectos:
            if efecto.id_parametro not in ids_parametros_validos:
                errores.append(
                    f"   ❌ {tech.id} → efecto '{efecto.id_parametro}' NO existe en REGISTRO_PARAMETROS"
                )

    if errores:
        print("\n".join(errores))
        raise AssertionError(f"{len(errores)} efecto(s) sin parámetro válido")

    # Contar efectos totales
    total_efectos = sum(len(t.efectos) for t in arbol)
    print(f"\n📊 Total de efectos verificados: {total_efectos}")
    print(f"📊 Parámetros del registro usados: "
          f"{len({e.id_parametro for t in arbol for e in t.efectos})}/{len(ids_parametros_validos)}")
    print("✅ TEST 2 PASADO: Todos los efectos apuntan a parámetros válidos.\n")


def test_nivel_1_disponibles(arbol):
    """Verifica que exactamente 7 tecnologías de nivel 1 están disponibles."""
    print("=" * 60)
    print("🔓 TEST 3: Tecnologías Nivel 1 Disponibles")
    print("=" * 60)

    disponibles = arbol.get_nivel_1_disponibles()

    assert len(disponibles) == 7, f"Esperadas 7 techs nivel 1, encontradas {len(disponibles)}"

    # Verificar que todas son de subramas distintas
    subramas = {(t.bloque, t.subrama) for t in disponibles}
    assert len(subramas) == 7, f"Esperadas 7 subramas distintas, encontradas {len(subramas)}"

    # Verificar que ninguna tiene padre
    for t in disponibles:
        assert t.padre_id is None, f"{t.id} es nivel 1 pero tiene padre_id={t.padre_id}"

    print("\n📋 Tecnologías nivel 1:")
    for _, t in sorted([(t.subrama, t) for t in disponibles]):
        print(f"   ✅ {t.id}: {t.nombre}")

    print("\n✅ TEST 3 PASADO: 7 tecnologías nivel 1 correctas.\n")


def test_costes_escalados(arbol):
    """Verifica que los costes siguen la curva de escalado por nivel."""
    print("=" * 60)
    print("💰 TEST 4: Escalado de Costes por Nivel")
    print("=" * 60)

    # Multiplicadores esperados (definidos en Tecnologia.crear)
    mult_oro = {1: 1, 2: 3, 3: 8, 4: 15, 5: 25, 6: 40, 7: 60}
    mult_turnos = {1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 10, 7: 15}
    base_oro = 100
    base_turnos = 3

    errores: list[str] = []

    for tech in arbol:
        oro_esperado = base_oro * mult_oro[tech.nivel]
        turnos_esperados = base_turnos * mult_turnos[tech.nivel]

        if tech.coste_oro != oro_esperado:
            errores.append(
                f"   ❌ {tech.id}: oro={tech.coste_oro}, esperado={oro_esperado}"
            )
        if tech.turnos_requeridos != turnos_esperados:
            errores.append(
                f"   ❌ {tech.id}: turnos={tech.turnos_requeridos}, esperado={turnos_esperados}"
            )

    if errores:
        print("\n".join(errores))
        raise AssertionError(f"{len(errores)} error(es) de escalado de costes")

    # Mostrar tabla resumen
    print("\n📊 Curva de costes verificada:")
    for nivel in range(1, 8):
        oro = base_oro * mult_oro[nivel]
        turnos = base_turnos * mult_turnos[nivel]
        print(f"   Nivel {nivel}: 💰{oro:>5} oro | ⏳{turnos:>2} turnos")

    print("\n✅ TEST 4 PASADO: Todos los costes escalan correctamente.\n")


def test_cadenas_padre_hijo(arbol):
    """Verifica que cada subrama forma una cadena lineal perfecta 1→2→3→...→7."""
    print("=" * 60)
    print("🔗 TEST 5: Cadenas Padre-Hijo por Subrama")
    print("=" * 60)

    errores: list[str] = []

    for subrama_num in range(1, 8):
        techs = arbol.get_subrama(1, subrama_num)
        assert len(techs) == 7, f"Subrama 1.{subrama_num}: esperados 7 niveles, encontrados {len(techs)}"

        # Verificar cadena
        for i, tech in enumerate(techs):
            nivel_esperado = i + 1
            if tech.nivel != nivel_esperado:
                errores.append(f"   ❌ 1.{subrama_num}: posición {i} tiene nivel {tech.nivel}, esperado {nivel_esperado}")

            if nivel_esperado == 1:
                if tech.padre_id is not None:
                    errores.append(f"   ❌ {tech.id}: nivel 1 con padre_id={tech.padre_id}")
            else:
                padre_esperado = techs[i - 1].id
                if tech.padre_id != padre_esperado:
                    errores.append(f"   ❌ {tech.id}: padre={tech.padre_id}, esperado={padre_esperado}")

        print(f"   ✅ Subrama 1.{subrama_num}: cadena 1→7 correcta ({techs[0].nombre} → ... → {techs[-1].nombre})")

    if errores:
        print("\n".join(errores))
        raise AssertionError(f"{len(errores)} error(es) en cadenas padre-hijo")

    print("\n✅ TEST 5 PASADO: Todas las cadenas padre-hijo son correctas.\n")


def test_parametros_logicos(arbol):
    """Verifica que los desbloqueos lógicos funcionan correctamente."""
    print("=" * 60)
    print("🔒 TEST 6: Parámetros Lógicos (Desbloqueos)")
    print("=" * 60)

    # Pares (tech_id, parametro_id) que deben ser lógicos
    desbloqueos = [
        ("1.2.5_navegacion_aguas_profundas", "pesca_aguas_profundas"),
        ("1.4.4_caballeria", "ganaderia_caballar"),
        ("1.7.3_hornos", "cocina_hornos"),
    ]

    for tech_id, param_id in desbloqueos:
        tech = arbol.obtener(tech_id)
        param = get_parametro(param_id)

        assert param.es_logico, f"{param_id} debería ser lógico pero es {param.tipo}"

        # Antes de investigar: bloqueado
        assert not param.esta_desbloqueado(set()), f"{param_id} debería estar bloqueado inicialmente"

        # Después de investigar: desbloqueado
        assert param.esta_desbloqueado({tech_id}), f"{param_id} debería desbloquearse con {tech_id}"

        # Verificar que la tech tiene el efecto correcto
        contribucion = tech.get_contribucion(param_id)
        assert contribucion == 1.0, f"{tech_id} debería contribuir 1.0 a {param_id}, contribuye {contribucion}"

        print(f"   ✅ {tech.nombre} → desbloquea {param.nombre}")

    print("\n✅ TEST 6 PASADO: Todos los desbloqueos lógicos funcionan correctamente.\n")


def test_prerequisitos(arbol):
    """Verifica que puede_investigar() respeta la cadena de prerequisitos."""
    print("=" * 60)
    print("🔐 TEST 7: Resolución de Prerequisitos")
    print("=" * 60)

    completadas: set[str] = set()

    # Nivel 1 siempre disponible
    puede, razon = arbol.puede_investigar("1.1.1_regadio_inundacion", completadas)
    assert puede, f"Nivel 1 debería estar disponible: {razon}"
    print(f"   ✅ 1.1.1 (Nv1) disponible sin prerequisitos: {razon}")

    # Nivel 2 bloqueado sin nivel 1
    puede, razon = arbol.puede_investigar("1.1.2_seleccion_semillas", completadas)
    assert not puede, "Nivel 2 debería estar bloqueado sin nivel 1"
    print(f"   ✅ 1.1.2 (Nv2) bloqueado sin padre: {razon}")

    # Completar nivel 1 y verificar nivel 2
    completadas.add("1.1.1_regadio_inundacion")
    puede, razon = arbol.puede_investigar("1.1.2_seleccion_semillas", completadas)
    assert puede, f"Nivel 2 debería estar disponible tras completar nivel 1: {razon}"
    print(f"   ✅ 1.1.2 (Nv2) disponible tras completar 1.1.1: {razon}")

    # Nivel 3 sigue bloqueado
    puede, razon = arbol.puede_investigar("1.1.3_ciclos", completadas)
    assert not puede, "Nivel 3 debería estar bloqueado sin nivel 2"
    print(f"   ✅ 1.1.3 (Nv3) bloqueado sin padre directo: {razon}")

    # Ya investigada
    puede, razon = arbol.puede_investigar("1.1.1_regadio_inundacion", completadas)
    assert not puede, "Tecnología ya completada no debería poder investigarse de nuevo"
    print(f"   ✅ 1.1.1 ya completada: {razon}")

    print("\n✅ TEST 7 PASADO: Prerequisitos resueltos correctamente.\n")


def main():
    print("\n🧪 === VALIDACIÓN PILOTO BLOQUE 1: ALIMENTACIÓN ===\n")

    arbol = test_carga_arbol()
    test_efectos_vinculados_a_parametros(arbol)
    test_nivel_1_disponibles(arbol)
    test_costes_escalados(arbol)
    test_cadenas_padre_hijo(arbol)
    test_parametros_logicos(arbol)
    test_prerequisitos(arbol)

    print("=" * 60)
    print("🎉 TODOS LOS TESTS DEL BLOQUE 1 PASARON CORRECTAMENTE")
    print("=" * 60)
    print("\n✅ El pipeline está validado. Se puede escalar a Bloques 2-7.")
    print("   Siguiente paso: Generar datos de los 6 bloques restantes.\n")


if __name__ == "__main__":
    main()
