# test_validacion_bloques_1_2_3.py
"""
Script de validación conjunta: Bloques 1 + 2 + 3.
Total esperado: 147 tecnologías.

Verifica:
1. Carga sin errores estructurales (147 nodos, 3 bloques)
2. Todos los efectos apuntan a parámetros existentes
3. Nivel 1 disponibles (21 tecnologías = 7 por bloque)
4. Costes escalados correctamente en los 147 nodos
5. Cadenas padre-hijo coherentes en las 21 subramas
6. Parámetros lógicos (simples, compartidos y nuevos del B3)
7. Correcciones históricas específicas del Bloque 3
"""
from src.config.parametros_registro import REGISTRO_PARAMETROS, get_parametro
from src.investigacion.arbol_investigaciones import ArbolInvestigaciones
from src.investigacion.datos.bloque_1_alimentacion import TECNOLOGIAS_BLOQUE_1
from src.investigacion.datos.bloque_2_extraccion import TECNOLOGIAS_BLOQUE_2
from src.investigacion.datos.bloque_3_industria import TECNOLOGIAS_BLOQUE_3


def test_carga_arbol_completo():
    """Verifica que los tres bloques cargan juntos sin errores."""
    print("=" * 60)
    print("🌳 TEST 1: Carga Conjunta Bloques 1+2+3")
    print("=" * 60)

    todas_techs = TECNOLOGIAS_BLOQUE_1 + TECNOLOGIAS_BLOQUE_2 + TECNOLOGIAS_BLOQUE_3
    arbol = ArbolInvestigaciones.construir(todas_techs)

    assert arbol.total_tecnologias == 147, f"Esperadas 147, encontradas {arbol.total_tecnologias}"
    assert arbol.total_bloques == 3, f"Esperados 3 bloques, encontrados {arbol.total_bloques}"

    resumen = arbol.resumen()
    print(f"\n📊 Resumen: {resumen}")
    assert resumen["tecnologias_por_bloque"].get(1, 0) == 49, "Bloque 1 debe tener 49 techs"
    assert resumen["tecnologias_por_bloque"].get(2, 0) == 49, "Bloque 2 debe tener 49 techs"
    assert resumen["tecnologias_por_bloque"].get(3, 0) == 49, "Bloque 3 debe tener 49 techs"

    print("✅ TEST 1 PASADO: 147 tecnologías cargadas correctamente.\n")
    return arbol


def test_efectos_vinculados(arbol):
    """Verifica que TODOS los efectos de los 3 bloques referencian parámetros válidos."""
    print("=" * 60)
    print("🔗 TEST 2: Vinculación Efectos → Parámetros (147 techs)")
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
    """Verifica 21 tecnologías nivel 1 (7 por bloque)."""
    print("=" * 60)
    print("🔓 TEST 3: Nivel 1 Disponibles (21 total)")
    print("=" * 60)

    disponibles = arbol.get_nivel_1_disponibles()
    assert len(disponibles) == 21, f"Esperadas 21, encontradas {len(disponibles)}"

    por_bloque: dict[int, int] = {}
    for t in disponibles:
        por_bloque[t.bloque] = por_bloque.get(t.bloque, 0) + 1
        assert t.padre_id is None, f"{t.id} es Nv1 pero tiene padre"

    for b in [1, 2, 3]:
        assert por_bloque.get(b, 0) == 7, f"Bloque {b} debe tener 7 Nv1"
        print(f"   ✅ Bloque {b}: {por_bloque[b]} tecnologías nivel 1")

    print("✅ TEST 3 PASADO\n")


def test_costes_escalados(arbol):
    """Verifica curva de costes en los 147 nodos."""
    print("=" * 60)
    print("💰 TEST 4: Escalado de Costes (147 techs)")
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

    print("   ✅ Curva verificada para 147 tecnologías")
    print("✅ TEST 4 PASADO\n")


def test_cadenas_padre_hijo(arbol):
    """Verifica cadenas lineales en las 21 subramas (7×3 bloques)."""
    print("=" * 60)
    print("🔗 TEST 5: Cadenas Padre-Hijo (21 subramas)")
    print("=" * 60)

    errores: list[str] = []
    for bloque in [1, 2, 3]:
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

    print("   ✅ 21 subramas con cadenas 1→7 correctas")
    print("✅ TEST 5 PASADO\n")


def test_parametros_logicos(arbol):
    """Verifica todos los desbloqueos lógicos de los 3 bloques."""
    print("=" * 60)
    print("🔒 TEST 6: Parámetros Lógicos (6 desbloqueos)")
    print("=" * 60)

    # === Desbloqueos simples (Bloque 1) ===
    simples_b1 = [
        ("1.2.5_navegacion_aguas_profundas", "pesca_aguas_profundas"),
        ("1.4.4_caballeria", "ganaderia_caballar"),
        ("1.7.3_hornos", "cocina_hornos"),
    ]
    for tech_id, param_id in simples_b1:
        param = get_parametro(param_id)
        assert param.es_logico
        assert not param.esta_desbloqueado(set())
        assert param.esta_desbloqueado({tech_id})
        print(f"   ✅ [B1] {tech_id} → {param.nombre}")

    # === Desbloqueo compartido B2: sostenibilidad_forestal ===
    param_sost = get_parametro("sostenibilidad_forestal")
    assert param_sost.es_logico
    assert not param_sost.esta_desbloqueado({"2.1.7_tala_selectiva"})
    assert not param_sost.esta_desbloqueado({"2.6.1_gestion_forestal_cientifica"})
    assert param_sost.esta_desbloqueado({
        "2.1.7_tala_selectiva", "2.6.1_gestion_forestal_cientifica"
    })
    print("   ✅ [B2] sostenibilidad_forestal requiere 2.1.7 + 2.6.1")

    # === Desbloqueo simple B2: minería submarina ===
    param_sub = get_parametro("mineria_submarina")
    assert param_sub.es_logico
    assert param_sub.esta_desbloqueado({"2.2.7_submarina"})
    print("   ✅ [B2] 2.2.7_submarina → mineria_submarina")

    # === Desbloqueos simples B3 ===
    param_acero = get_parametro("herreria_avanzada")
    assert param_acero.es_logico
    assert param_acero.esta_desbloqueado({"3.3.7_acero"})
    print("   ✅ [B3] 3.3.7_acero → herreria_avanzada")

    param_hidr = get_parametro("maquinaria_hidraulica")
    assert param_hidr.es_logico
    assert param_hidr.esta_desbloqueado({"3.5.7_hidraulica"})
    print("   ✅ [B3] 3.5.7_hidraulica → maquinaria_hidraulica")

    # === Desbloqueo COMPARTIDO B3: gremios_artesanos ===
    param_grem = get_parametro("gremios_artesanos")
    assert param_grem.es_logico
    assert not param_grem.esta_desbloqueado(set())
    assert not param_grem.esta_desbloqueado({"3.6.7_cartas_gremiales"})
    assert not param_grem.esta_desbloqueado({"3.7.7_legislacion_gremial"})
    assert param_grem.esta_desbloqueado({
        "3.6.7_cartas_gremiales", "3.7.7_legislacion_gremial"
    })
    print("   ✅ [B3] gremios_artesanos requiere 3.6.7 + 3.7.7 (compartido)")

    print("✅ TEST 6 PASADO\n")


def test_correcciones_bloque3(arbol):
    """Verifica que las reordenaciones históricas del Bloque 3 se aplicaron."""
    print("=" * 60)
    print("🔧 TEST 7: Correcciones Históricas Bloque 3")
    print("=" * 60)

    # 3.1 Carpintería: Talla=Nv3, Ensamblaje=Nv5, Ebanistería=Nv7
    carp = arbol.get_subrama(3, 1)
    assert carp[2].id == "3.1.3_talla", f"Nv3 debería ser talla, es {carp[2].id}"
    assert carp[4].id == "3.1.5_ensamblaje", f"Nv5 debería ser ensamblaje, es {carp[4].id}"
    assert carp[6].id == "3.1.7_ebanisteria", f"Nv7 debería ser ebanisteria, es {carp[6].id}"
    print(f"   ✅ 3.1 Carpintería reordenada: {' → '.join(t.nombre for t in carp)}")

    # 3.3 Herrería: Fundición=Nv5, Acero=Nv7
    herr = arbol.get_subrama(3, 3)
    assert herr[4].id == "3.3.5_fundicion", f"Nv5 debería ser fundicion, es {herr[4].id}"
    assert herr[6].id == "3.3.7_acero", f"Nv7 debería ser acero, es {herr[6].id}"
    print(f"   ✅ 3.3 Herrería reordenada: {' → '.join(t.nombre for t in herr)}")

    # 3.5 Maquinaria: Progresión Rueda→Engranajes→Poleas→Molino→Prensa→Telar→Hidráulica
    maq = arbol.get_subrama(3, 5)
    ids_esperados = [
        "3.5.1_rueda", "3.5.2_engranajes", "3.5.3_poleas",
        "3.5.4_molino_viento", "3.5.5_prensa", "3.5.6_telar_mecanico", "3.5.7_hidraulica"
    ]
    for i, id_exp in enumerate(ids_esperados):
        assert maq[i].id == id_exp, f"Nv{i+1} debería ser {id_exp}, es {maq[i].id}"
    print(f"   ✅ 3.5 Maquinaria reordenada: {' → '.join(t.nombre for t in maq)}")

    # 3.7 Seguridad Industrial: Verificar nombre corregido
    seg = arbol.get_subrama(3, 7)
    assert "seguridad" in seg[6].nombre.lower() or "gremial" in seg[6].nombre.lower(), \
        f"3.7.7 debería ser legislación gremial, es {seg[6].nombre}"
    print(f"   ✅ 3.7 Seguridad Industrial: {seg[6].nombre}")

    print("✅ TEST 7 PASADO\n")


def main():
    print("\n🧪 === VALIDACIÓN CONJUNTA: BLOQUES 1+2+3 ===\n")

    arbol = test_carga_arbol_completo()
    test_efectos_vinculados(arbol)
    test_nivel_1_disponibles(arbol)
    test_costes_escalados(arbol)
    test_cadenas_padre_hijo(arbol)
    test_parametros_logicos(arbol)
    test_correcciones_bloque3(arbol)

    print("=" * 60)
    print("🎉 TODOS LOS TESTS DE BLOQUES 1+2+3 PASARON")
    print("=" * 60)
    print("\n✅ 147 tecnologías validadas. Pipeline listo para Bloques 4-7.")
    print("   Siguiente: Generar Bloque 4 (Ejército) con corrección de IDs duplicados.\n")


if __name__ == "__main__":
    main()
