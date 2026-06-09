# test_validacion_bloque1_2.py
"""
Script de validación conjunta: Bloque 1 (Alimentación) + Bloque 2 (Extracción).
Total esperado: 98 tecnologías.

Verifica:
1. Carga sin errores estructurales (98 nodos, 2 bloques)
2. Todos los efectos apuntan a parámetros existentes
3. Nivel 1 disponibles (14 tecnologías = 7 por bloque)
4. Costes escalados correctamente
5. Cadenas padre-hijo coherentes en todas las subramas
6. Parámetros lógicos compartidos (sostenibilidad_forestal)
7. Correcciones específicas del Bloque 2 (reordenación histórica)
"""
from src.config.parametros_registro import REGISTRO_PARAMETROS, get_parametro
from src.investigacion.arbol_investigaciones import ArbolInvestigaciones
from src.investigacion.datos.bloque_1_alimentacion import TECNOLOGIAS_BLOQUE_1
from src.investigacion.datos.bloque_2_extraccion import TECNOLOGIAS_BLOQUE_2


def test_carga_arbol_completo():
    """Verifica que ambos bloques cargan juntos sin errores."""
    print("=" * 60)
    print("🌳 TEST 1: Carga Conjunta Bloques 1+2")
    print("=" * 60)

    todas_techs = TECNOLOGIAS_BLOQUE_1 + TECNOLOGIAS_BLOQUE_2
    arbol = ArbolInvestigaciones.construir(todas_techs)

    assert arbol.total_tecnologias == 98, f"Esperadas 98, encontradas {arbol.total_tecnologias}"
    assert arbol.total_bloques == 2, f"Esperados 2 bloques, encontrados {arbol.total_bloques}"

    resumen = arbol.resumen()
    print(f"\n📊 Resumen: {resumen}")
    assert resumen["tecnologias_por_bloque"].get(1, 0) == 49
    assert resumen["tecnologias_por_bloque"].get(2, 0) == 49

    print("✅ TEST 1 PASADO: 98 tecnologías cargadas correctamente.\n")
    return arbol


def test_efectos_vinculados(arbol):
    """Verifica que TODOS los efectos de ambos bloques referencian parámetros válidos."""
    print("=" * 60)
    print("🔗 TEST 2: Vinculación Efectos → Parámetros (98 techs)")
    print("=" * 60)

    ids_validos = set(REGISTRO_PARAMETROS.keys())
    errores: list[str] = []

    for tech in arbol:
        for efecto in tech.efectos:
            if efecto.id_parametro not in ids_validos:
                errores.append(f"   ❌ {tech.id} → '{efecto.id_parametro}' NO existe")

    if errores:
        raise AssertionError("\n".join(errores))

    total_efectos = sum(len(t.efectos) for t in arbol)
    params_usados = {e.id_parametro for t in arbol for e in t.efectos}
    print(f"\n📊 Efectos verificados: {total_efectos}")
    print(f"📊 Parámetros usados: {len(params_usados)}/{len(ids_validos)}")
    print("✅ TEST 2 PASADO\n")


def test_nivel_1_disponibles(arbol):
    """Verifica 14 tecnologías nivel 1 (7 por bloque)."""
    print("=" * 60)
    print("🔓 TEST 3: Nivel 1 Disponibles (14 total)")
    print("=" * 60)

    disponibles = arbol.get_nivel_1_disponibles()
    assert len(disponibles) == 14, f"Esperadas 14, encontradas {len(disponibles)}"

    por_bloque: dict[int, int] = {}
    for t in disponibles:
        por_bloque[t.bloque] = por_bloque.get(t.bloque, 0) + 1
        assert t.padre_id is None, f"{t.id} es Nv1 pero tiene padre"

    assert por_bloque.get(1, 0) == 7, "Bloque 1 debe tener 7 Nv1"
    assert por_bloque.get(2, 0) == 7, "Bloque 2 debe tener 7 Nv1"

    print(f"   ✅ Bloque 1: {por_bloque[1]} tecnologías nivel 1")
    print(f"   ✅ Bloque 2: {por_bloque[2]} tecnologías nivel 1")
    print("✅ TEST 3 PASADO\n")


def test_costes_escalados(arbol):
    """Verifica curva de costes en los 98 nodos."""
    print("=" * 60)
    print("💰 TEST 4: Escalado de Costes (98 techs)")
    print("=" * 60)

    mult_oro = {1: 1, 2: 3, 3: 8, 4: 15, 5: 25, 6: 40, 7: 60}
    mult_turnos = {1: 1, 2: 2, 3: 3, 4: 5, 5: 7, 6: 10, 7: 15}
    base_oro, base_turnos = 100, 3
    errores: list[str] = []

    for tech in arbol:
        oro_exp = base_oro * mult_oro[tech.nivel]
        turnos_exp = base_turnos * mult_turnos[tech.nivel]
        if tech.coste_oro != oro_exp:
            errores.append(f"   ❌ {tech.id}: oro={tech.coste_oro}, exp={oro_exp}")
        if tech.turnos_requeridos != turnos_exp:
            errores.append(f"   ❌ {tech.id}: turnos={tech.turnos_requeridos}, exp={turnos_exp}")

    if errores:
        raise AssertionError("\n".join(errores))

    print("   ✅ Curva verificada para 98 tecnologías")
    print("✅ TEST 4 PASADO\n")


def test_cadenas_padre_hijo(arbol):
    """Verifica cadenas lineales en las 14 subramas (7 B1 + 7 B2)."""
    print("=" * 60)
    print("🔗 TEST 5: Cadenas Padre-Hijo (14 subramas)")
    print("=" * 60)

    errores: list[str] = []
    for bloque in [1, 2]:
        for subrama in range(1, 8):
            techs = arbol.get_subrama(bloque, subrama)
            assert len(techs) == 7, f"B{bloque}.S{subrama}: esperados 7, encontrados {len(techs)}"

            for i, tech in enumerate(techs):
                niv_exp = i + 1
                if tech.nivel != niv_exp:
                    errores.append(f"   ❌ {bloque}.{subrama}: pos {i} tiene nivel {tech.nivel}")
                if niv_exp == 1:
                    if tech.padre_id is not None:
                        errores.append(f"   ❌ {tech.id}: Nv1 con padre")
                else:
                    padre_exp = techs[i - 1].id
                    if tech.padre_id != padre_exp:
                        errores.append(f"   ❌ {tech.id}: padre={tech.padre_id}, exp={padre_exp}")

    if errores:
        raise AssertionError("\n".join(errores))

    print("   ✅ 14 subramas con cadenas 1→7 correctas")
    print("✅ TEST 5 PASADO\n")


def test_parametros_logicos(arbol):
    """Verifica desbloqueos lógicos de ambos bloques."""
    print("=" * 60)
    print("🔒 TEST 6: Parámetros Lógicos")
    print("=" * 60)

    # Desbloqueos simples (Bloque 1)
    simples = [
        ("1.2.5_navegacion_aguas_profundas", "pesca_aguas_profundas"),
        ("1.4.4_caballeria", "ganaderia_caballar"),
        ("1.7.3_hornos", "cocina_hornos"),
    ]
    for tech_id, param_id in simples:
        param = get_parametro(param_id)
        assert param.es_logico
        assert not param.esta_desbloqueado(set())
        assert param.esta_desbloqueado({tech_id})
        print(f"   ✅ {tech_id} → {param.nombre}")

    # Desbloqueo COMPARTIDO (Bloque 2): requiere AMBOS aportes
    param_sost = get_parametro("sostenibilidad_forestal")
    assert param_sost.es_logico
    assert not param_sost.esta_desbloqueado(set())
    assert not param_sost.esta_desbloqueado({"2.1.7_tala_selectiva"})  # Solo práctica ≠ suficiente
    assert not param_sost.esta_desbloqueado({"2.6.1_gestion_forestal_cientifica"})  # Solo teoría ≠ suficiente
    assert param_sost.esta_desbloqueado({
        "2.1.7_tala_selectiva",
        "2.6.1_gestion_forestal_cientifica"
    })
    print("   ✅ sostenibilidad_forestal requiere 2.1.7 + 2.6.1 (compartido)")

    # Minería submarina (Bloque 2)
    param_sub = get_parametro("mineria_submarina")
    assert param_sub.es_logico
    assert param_sub.esta_desbloqueado({"2.2.7_submarina"})
    print("   ✅ 2.2.7_submarina → mineria_submarina")

    print("✅ TEST 6 PASADO\n")


def test_correcciones_bloque2(arbol):
    """Verifica que las reordenaciones históricas del Bloque 2 se aplicaron correctamente."""
    print("=" * 60)
    print("🔧 TEST 7: Correcciones Históricas Bloque 2")
    print("=" * 60)

    # 2.1 Forestal: Tala Selectiva debe ser Nv5, Cable Nv6, Sostenibilidad Nv7
    forestal = arbol.get_subrama(2, 1)
    nombres_forestal = [t.nombre for t in forestal]
    assert forestal[4].id == "2.1.7_tala_selectiva", f"Nv5 debería ser tala_selectiva, es {forestal[4].id}"
    assert forestal[5].id == "2.1.6_cable", f"Nv6 debería ser cable, es {forestal[5].id}"
    assert forestal[6].id == "2.1.5_sostenibilidad_practica", f"Nv7 debería ser sostenibilidad, es {forestal[6].id}"
    print(f"   ✅ 2.1 Forestal reordenada: {' → '.join(nombres_forestal)}")

    # 2.2 Minera: Canteras Nv3, Pozos Nv4, Hundimiento Nv5, Lixiviación Nv6
    minera = arbol.get_subrama(2, 2)
    nombres_minera = [t.nombre for t in minera]
    assert minera[2].id == "2.2.6_canteras", f"Nv3 debería ser canteras, es {minera[2].id}"
    assert minera[3].id == "2.2.4_pozos", f"Nv4 debería ser pozos, es {minera[3].id}"
    assert minera[4].id == "2.2.3_hundimiento", f"Nv5 debería ser hundimiento, es {minera[4].id}"
    assert minera[5].id == "2.2.5_lixiviacion", f"Nv6 debería ser lixiviacion, es {minera[5].id}"
    print(f"   ✅ 2.2 Minera reordenada: {' → '.join(nombres_minera)}")

    # 2.6.1 renombrada
    inv_forestal = arbol.get_subrama(2, 6)
    assert inv_forestal[0].id == "2.6.1_gestion_forestal_cientifica"
    print(f"   ✅ 2.6.1 renombrada: {inv_forestal[0].nombre}")

    print("✅ TEST 7 PASADO\n")


def main():
    print("\n🧪 === VALIDACIÓN CONJUNTA: BLOQUES 1+2 ===\n")

    arbol = test_carga_arbol_completo()
    test_efectos_vinculados(arbol)
    test_nivel_1_disponibles(arbol)
    test_costes_escalados(arbol)
    test_cadenas_padre_hijo(arbol)
    test_parametros_logicos(arbol)
    test_correcciones_bloque2(arbol)

    print("=" * 60)
    print("🎉 TODOS LOS TESTS DE BLOQUES 1+2 PASARON")
    print("=" * 60)
    print("\n✅ 98 tecnologías validadas. Pipeline listo para Bloques 3-7.")
    print("   Siguiente: Generar Bloque 3 (Industria) o Bloque 4 (Ejército).\n")


if __name__ == "__main__":
    main()
