# test_validacion_bloques_1_2_3_4.py
"""
Script de validación conjunta: Bloques 1 + 2 + 3 + 4.
Total esperado: 196 tecnologías.

Verifica:
1. Carga sin errores estructurales (196 nodos, 4 bloques)
2. Todos los efectos apuntan a parámetros existentes
3. Nivel 1 disponibles (28 tecnologías = 7 por bloque)
4. Costes escalados correctamente en los 196 nodos
5. Cadenas padre-hijo coherentes en las 28 subramas
6. Parámetros lógicos (simples, compartidos y nuevos del B4)
7. Correcciones históricas y de IDs específicos del Bloque 4
"""
from src.config.parametros_registro import REGISTRO_PARAMETROS, get_parametro
from src.investigacion.arbol_investigaciones import ArbolInvestigaciones
from src.investigacion.datos.bloque_1_alimentacion import TECNOLOGIAS_BLOQUE_1
from src.investigacion.datos.bloque_2_extraccion import TECNOLOGIAS_BLOQUE_2
from src.investigacion.datos.bloque_3_industria import TECNOLOGIAS_BLOQUE_3
from src.investigacion.datos.bloque_4_ejercito import TECNOLOGIAS_BLOQUE_4


def test_carga_arbol_completo():
    """Verifica que los cuatro bloques cargan juntos sin errores."""
    print("=" * 60)
    print("🌳 TEST 1: Carga Conjunta Bloques 1+2+3+4")
    print("=" * 60)

    todas_techs = (
        TECNOLOGIAS_BLOQUE_1
        + TECNOLOGIAS_BLOQUE_2
        + TECNOLOGIAS_BLOQUE_3
        + TECNOLOGIAS_BLOQUE_4
    )
    arbol = ArbolInvestigaciones.construir(todas_techs)

    assert arbol.total_tecnologias == 196, f"Esperadas 196, encontradas {arbol.total_tecnologias}"
    assert arbol.total_bloques == 4, f"Esperados 4 bloques, encontrados {arbol.total_bloques}"

    resumen = arbol.resumen()
    print(f"\n📊 Resumen: {resumen}")
    for b in range(1, 5):
        count = resumen["tecnologias_por_bloque"].get(b, 0)
        assert count == 49, f"Bloque {b} debe tener 49 techs, tiene {count}"
        print(f"   ✅ Bloque {b}: {count} tecnologías")

    print("✅ TEST 1 PASADO: 196 tecnologías cargadas correctamente.\n")
    return arbol


def test_efectos_vinculados(arbol):
    """Verifica que TODOS los efectos de los 4 bloques referencian parámetros válidos."""
    print("=" * 60)
    print("🔗 TEST 2: Vinculación Efectos → Parámetros (196 techs)")
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
    """Verifica 28 tecnologías nivel 1 (7 por bloque)."""
    print("=" * 60)
    print("🔓 TEST 3: Nivel 1 Disponibles (28 total)")
    print("=" * 60)

    disponibles = arbol.get_nivel_1_disponibles()
    assert len(disponibles) == 28, f"Esperadas 28, encontradas {len(disponibles)}"

    por_bloque: dict[int, int] = {}
    for t in disponibles:
        por_bloque[t.bloque] = por_bloque.get(t.bloque, 0) + 1
        assert t.padre_id is None, f"{t.id} es Nv1 pero tiene padre"

    for b in [1, 2, 3, 4]:
        assert por_bloque.get(b, 0) == 7, f"Bloque {b} debe tener 7 Nv1"
        print(f"   ✅ Bloque {b}: {por_bloque[b]} tecnologías nivel 1")

    print("✅ TEST 3 PASADO\n")


def test_costes_escalados(arbol):
    """Verifica curva de costes en los 196 nodos."""
    print("=" * 60)
    print("💰 TEST 4: Escalado de Costes (196 techs)")
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

    print("   ✅ Curva verificada para 196 tecnologías")
    print("✅ TEST 4 PASADO\n")


def test_cadenas_padre_hijo(arbol):
    """Verifica cadenas lineales en las 28 subramas (7×4 bloques)."""
    print("=" * 60)
    print("🔗 TEST 5: Cadenas Padre-Hijo (28 subramas)")
    print("=" * 60)

    errores: list[str] = []
    for bloque in [1, 2, 3, 4]:
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

    print("   ✅ 28 subramas con cadenas 1→7 correctas")
    print("✅ TEST 5 PASADO\n")


def test_parametros_logicos(arbol):
    """Verifica todos los desbloqueos lógicos de los 4 bloques."""
    print("=" * 60)
    print("🔒 TEST 6: Parámetros Lógicos (9 desbloqueos)")
    print("=" * 60)

    # === Desbloqueos simples B1 ===
    for tech_id, param_id in [
        ("1.2.5_navegacion_aguas_profundas", "pesca_aguas_profundas"),
        ("1.4.4_caballeria", "ganaderia_caballar"),
        ("1.7.3_hornos", "cocina_hornos"),
    ]:
        p = get_parametro(param_id)
        assert p.es_logico and p.esta_desbloqueado({tech_id})
        print(f"   ✅ [B1] {tech_id} → {p.nombre}")

    # === Desbloqueos B2 ===
    sost = get_parametro("sostenibilidad_forestal")
    assert sost.esta_desbloqueado({"2.1.7_tala_selectiva", "2.6.1_gestion_forestal_cientifica"})
    print("   ✅ [B2] sostenibilidad_forestal (compartido)")

    sub = get_parametro("mineria_submarina")
    assert sub.esta_desbloqueado({"2.2.7_submarina"})
    print("   ✅ [B2] mineria_submarina")

    # === Desbloqueos B3 ===
    acero = get_parametro("herreria_avanzada")
    assert acero.esta_desbloqueado({"3.3.7_acero"})
    print("   ✅ [B3] herreria_avanzada")

    hidr = get_parametro("maquinaria_hidraulica")
    assert hidr.esta_desbloqueado({"3.5.7_hidraulica"})
    print("   ✅ [B3] maquinaria_hidraulica")

    grem = get_parametro("gremios_artesanos")
    assert grem.esta_desbloqueado({"3.6.7_cartas_gremiales", "3.7.7_legislacion_gremial"})
    print("   ✅ [B3] gremios_artesanos (compartido)")

    # === Desbloqueos B4 ===
    cab_pes = get_parametro("caballeria_pesada")
    assert cab_pes.esta_desbloqueado({"4.2.7_caballeria_pesada"})
    print("   ✅ [B4] caballeria_pesada")

    asedio = get_parametro("maquinas_asedio_avanzadas")
    assert asedio.esta_desbloqueado({"4.3.7_trabuquete"})
    print("   ✅ [B4] maquinas_asedio_avanzadas")

    doctrina = get_parametro("doctrina_militar")
    assert not doctrina.esta_desbloqueado({"4.6.7_codigo_guerra"})
    assert not doctrina.esta_desbloqueado({"4.7.7_fortaleza_estrellada"})
    assert doctrina.esta_desbloqueado({"4.6.7_codigo_guerra", "4.7.7_fortaleza_estrellada"})
    print("   ✅ [B4] doctrina_militar (compartido)")

    print("✅ TEST 6 PASADO\n")


def test_correcciones_bloque4(arbol):
    """Verifica correcciones históricas y resolución de IDs duplicados en B4."""
    print("=" * 60)
    print("🔧 TEST 7: Correcciones Bloque 4 (Ejército)")
    print("=" * 60)

    # 4.2 Caballería: Carro de guerra debe ser Nv3
    cab = arbol.get_subrama(4, 2)
    assert cab[2].id == "4.2.3_carro_guerra", f"Nv3 debería ser carro_guerra, es {cab[2].id}"
    print("   ✅ 4.2 Carro de guerra movido a Nv3")

    # 4.3 Asedio: Torre debe ser Nv3
    ased = arbol.get_subrama(4, 3)
    assert ased[2].id == "4.3.3_torre_asedio", f"Nv3 debería ser torre_asedio, es {ased[2].id}"
    print("   ✅ 4.3 Torre de asedio movida a Nv3")

    # 4.6 Tácticas: Formaciones debe ser Nv1, Retirada Nv3
    tact = arbol.get_subrama(4, 6)
    assert tact[0].id == "4.6.1_formaciones", f"Nv1 debería ser formaciones, es {tact[0].id}"
    assert tact[2].id == "4.6.3_retirada_ordenada", f"Nv3 debería ser retirada, es {tact[2].id}"
    print("   ✅ 4.6 Tácticas reordenada: Formaciones=Nv1, Retirada=Nv3")

    # Verificar que NO hay IDs duplicados en todo el árbol
    todos_ids = [t.id for t in arbol]
    duplicados = [x for x in todos_ids if todos_ids.count(x) > 1]
    assert len(duplicados) == 0, f"IDs duplicados encontrados: {set(duplicados)}"
    print("   ✅ Zero IDs duplicados en 196 tecnologías")

    # 4.7 Ingeniería Militar: Verificar nombre corregido
    ing = arbol.get_subrama(4, 7)
    assert "fortaleza" in ing[6].nombre.lower(), f"4.7.7 debería ser fortaleza estrellada, es {ing[6].nombre}"
    print(f"   ✅ 4.7 renombrada a Ingeniería Militar: {ing[6].nombre}")

    print("✅ TEST 7 PASADO\n")


def main():
    print("\n🧪 === VALIDACIÓN CONJUNTA: BLOQUES 1+2+3+4 ===\n")

    arbol = test_carga_arbol_completo()
    test_efectos_vinculados(arbol)
    test_nivel_1_disponibles(arbol)
    test_costes_escalados(arbol)
    test_cadenas_padre_hijo(arbol)
    test_parametros_logicos(arbol)
    test_correcciones_bloque4(arbol)

    print("=" * 60)
    print("🎉 TODOS LOS TESTS DE BLOQUES 1+2+3+4 PASARON")
    print("=" * 60)
    print("\n✅ 196 tecnologías validadas. Pipeline listo para Bloques 5-7.")
    print("   Siguiente: Generar Bloque 5 (Comercio) o Bloque 6 (Cultura).\n")


if __name__ == "__main__":
    main()
