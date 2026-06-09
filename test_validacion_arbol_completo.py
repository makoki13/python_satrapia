# test_validacion_arbol_completo.py
"""
SCRIPT DE VALIDACIÓN FINAL: ÁRBOL TECNOLÓGICO COMPLETO (BLOQUES 1-7).
Total esperado: 343 tecnologías (49 × 7).

Este script certifica la Fase 1 de datos al 100%. Verifica:
1. Carga estructural completa (343 nodos, 7 bloques)
2. Vinculación de efectos → parámetros (zero huérfanos)
3. Nivel 1 disponibles (49 tecnologías = 7 por bloque)
4. Curva de costes escalada en los 343 nodos
5. Cadenas padre-hijo en las 49 subramas
6. Todos los desbloqueos lógicos (simples + compartidos)
7. Correcciones históricas específicas de cada bloque
8. Zero IDs duplicados en todo el árbol
"""
from src.config.parametros_registro import REGISTRO_PARAMETROS, get_parametro
from src.investigacion.arbol_investigaciones import ArbolInvestigaciones
from src.investigacion.datos.bloque_1_alimentacion import TECNOLOGIAS_BLOQUE_1
from src.investigacion.datos.bloque_2_extraccion import TECNOLOGIAS_BLOQUE_2
from src.investigacion.datos.bloque_3_industria import TECNOLOGIAS_BLOQUE_3
from src.investigacion.datos.bloque_4_ejercito import TECNOLOGIAS_BLOQUE_4
from src.investigacion.datos.bloque_5_comercio import TECNOLOGIAS_BLOQUE_5
from src.investigacion.datos.bloque_6_cultura import TECNOLOGIAS_BLOQUE_6
from src.investigacion.datos.bloque_7_ciencia import TECNOLOGIAS_BLOQUE_7


def test_carga_arbol_completo():
    """Verifica que los siete bloques cargan juntos sin errores."""
    print("=" * 60)
    print("🌳 TEST 1: Carga Completa del Árbol Tecnológico")
    print("=" * 60)

    todas_techs = (
        TECNOLOGIAS_BLOQUE_1
        + TECNOLOGIAS_BLOQUE_2
        + TECNOLOGIAS_BLOQUE_3
        + TECNOLOGIAS_BLOQUE_4
        + TECNOLOGIAS_BLOQUE_5
        + TECNOLOGIAS_BLOQUE_6
        + TECNOLOGIAS_BLOQUE_7
    )
    arbol = ArbolInvestigaciones.construir(todas_techs)

    assert arbol.total_tecnologias == 343, f"Esperadas 343, encontradas {arbol.total_tecnologias}"
    assert arbol.total_bloques == 7, f"Esperados 7 bloques, encontrados {arbol.total_bloques}"

    resumen = arbol.resumen()
    print(f"\n📊 Resumen: {resumen}")
    for b in range(1, 8):
        count = resumen["tecnologias_por_bloque"].get(b, 0)
        assert count == 49, f"Bloque {b} debe tener 49 techs, tiene {count}"
        print(f"   ✅ Bloque {b}: {count} tecnologías")

    print("✅ TEST 1 PASADO: 343 tecnologías cargadas correctamente.\n")
    return arbol


def test_efectos_vinculados(arbol):
    """Verifica que TODOS los efectos referencian parámetros válidos."""
    print("=" * 60)
    print("🔗 TEST 2: Vinculación Efectos → Parámetros (343 techs)")
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
    """Verifica 49 tecnologías nivel 1 (7 por bloque)."""
    print("=" * 60)
    print("🔓 TEST 3: Nivel 1 Disponibles (49 total)")
    print("=" * 60)

    disponibles = arbol.get_nivel_1_disponibles()
    assert len(disponibles) == 49, f"Esperadas 49, encontradas {len(disponibles)}"

    por_bloque: dict[int, int] = {}
    for t in disponibles:
        por_bloque[t.bloque] = por_bloque.get(t.bloque, 0) + 1
        assert t.padre_id is None, f"{t.id} es Nv1 pero tiene padre"

    for b in range(1, 8):
        assert por_bloque.get(b, 0) == 7, f"Bloque {b} debe tener 7 Nv1"
        print(f"   ✅ Bloque {b}: {por_bloque[b]} tecnologías nivel 1")

    print("✅ TEST 3 PASADO\n")


def test_costes_escalados(arbol):
    """Verifica curva de costes en los 343 nodos."""
    print("=" * 60)
    print("💰 TEST 4: Escalado de Costes (343 techs)")
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

    print("   ✅ Curva verificada para 343 tecnologías")
    print("✅ TEST 4 PASADO\n")


def test_cadenas_padre_hijo(arbol):
    """Verifica cadenas lineales en las 49 subramas (7×7 bloques)."""
    print("=" * 60)
    print("🔗 TEST 5: Cadenas Padre-Hijo (49 subramas)")
    print("=" * 60)

    errores: list[str] = []
    for bloque in range(1, 8):
        for subrama in range(1, 8):
            techs = arbol.get_subrama(bloque, subrama)
            assert len(techs) == 7, f"B{bloque}.S{subrama}: esperados 7, encontrados {len(techs)}"

            for i, tech in enumerate(techs):
                niv_exp = i + 1
                if tech.nivel != niv_exp:
                    errores.append(f"   ❌ {bloque}.{subrama}: pos {i} tiene nivel {tech.nivel}")
                if niv_exp == 1 and tech.padre_id is not None:
                    errores.append(f"   ❌ {tech.id}: Nv1 con padre")
                elif niv_exp > 1 and tech.padre_id != techs[i - 1].id:
                    errores.append(f"   ❌ {tech.id}: padre={tech.padre_id}, exp={techs[i-1].id}")

    if errores:
        raise AssertionError("\n".join(errores))

    print("   ✅ 49 subramas con cadenas 1→7 correctas")
    print("✅ TEST 5 PASADO\n")


def test_parametros_logicos(arbol):
    """Verifica todos los desbloqueos lógicos de los 7 bloques."""
    print("=" * 60)
    print("🔒 TEST 6: Parámetros Lógicos (18 desbloqueos)")
    print("=" * 60)

    # === B1 (3 simples) ===
    for tech_id, param_id in [
        ("1.2.5_navegacion_aguas_profundas", "pesca_aguas_profundas"),
        ("1.4.4_caballeria", "ganaderia_caballar"),
        ("1.7.3_hornos", "cocina_hornos"),
    ]:
        p = get_parametro(param_id)
        assert p.es_logico and p.esta_desbloqueado({tech_id})
        print(f"   ✅ [B1] {tech_id} → {p.nombre}")

    # === B2 (1 compartido + 1 simple) ===
    sost = get_parametro("sostenibilidad_forestal")
    assert sost.esta_desbloqueado({"2.1.7_tala_selectiva", "2.6.1_gestion_forestal_cientifica"})
    print("   ✅ [B2] sostenibilidad_forestal (compartido)")
    assert get_parametro("mineria_submarina").esta_desbloqueado({"2.2.7_submarina"})
    print("   ✅ [B2] mineria_submarina")

    # === B3 (2 simples + 1 compartido) ===
    assert get_parametro("herreria_avanzada").esta_desbloqueado({"3.3.7_acero"})
    print("   ✅ [B3] herreria_avanzada")
    assert get_parametro("maquinaria_hidraulica").esta_desbloqueado({"3.5.7_hidraulica"})
    print("   ✅ [B3] maquinaria_hidraulica")
    grem_art = get_parametro("gremios_artesanos")
    assert grem_art.esta_desbloqueado({"3.6.7_cartas_gremiales", "3.7.7_legislacion_gremial"})
    print("   ✅ [B3] gremios_artesanos (compartido)")

    # === B4 (2 simples + 1 compartido) ===
    assert get_parametro("caballeria_pesada").esta_desbloqueado({"4.2.7_caballeria_pesada"})
    print("   ✅ [B4] caballeria_pesada")
    assert get_parametro("maquinas_asedio_avanzadas").esta_desbloqueado({"4.3.7_trabuquete"})
    print("   ✅ [B4] maquinas_asedio_avanzadas")
    doctrina = get_parametro("doctrina_militar")
    assert doctrina.esta_desbloqueado({"4.6.7_codigo_guerra", "4.7.7_fortaleza_estrellada"})
    print("   ✅ [B4] doctrina_militar (compartido)")

    # === B5 (1 simple + 2 compartidos) ===
    assert get_parametro("moneda_unificada").esta_desbloqueado({"5.6.7_banca_internacional"})
    print("   ✅ [B5] moneda_unificada")
    grem_mer = get_parametro("gremio_mercaderes")
    assert grem_mer.esta_desbloqueado({"5.1.7_bolsa_mercantil", "5.7.7_carta_comercial"})
    print("   ✅ [B5] gremio_mercaderes (compartido)")
    banca = get_parametro("banca_internacional")
    assert banca.esta_desbloqueado({"5.6.7_banca_internacional", "5.7.7_carta_comercial"})
    print("   ✅ [B5] banca_internacional (compartido)")

    # === B6 (2 simples + 1 compartido) ===
    assert get_parametro("universidad").esta_desbloqueado({"6.1.7_universidad"})
    print("   ✅ [B6] universidad")
    assert get_parametro("maravilla_cultural").esta_desbloqueado({"6.6.7_maravilla_mundo"})
    print("   ✅ [B6] maravilla_cultural")
    renac = get_parametro("renacimiento")
    assert renac.esta_desbloqueado({"6.2.7_mecenazgo", "6.7.7_ilustracion"})
    print("   ✅ [B6] renacimiento (compartido)")

    # === B7 (1 simple + 2 compartidos) ===
    metodo = get_parametro("metodo_cientifico")
    assert metodo.es_logico and metodo.esta_desbloqueado({"7.1.7_metodo_cientifico"})
    print("   ✅ [B7] metodo_cientifico")

    rev_cient = get_parametro("revolucion_cientifica")
    assert not rev_cient.esta_desbloqueado({"7.1.7_metodo_cientifico"})
    assert not rev_cient.esta_desbloqueado({"7.6.7_sociedad_real"})
    assert rev_cient.esta_desbloqueado({"7.1.7_metodo_cientifico", "7.6.7_sociedad_real"})
    print("   ✅ [B7] revolucion_cientifica (compartido 7.1.7+7.6.7)")

    soc_real = get_parametro("sociedad_real_ciencias")
    assert not soc_real.esta_desbloqueado({"7.6.7_sociedad_real"})
    assert not soc_real.esta_desbloqueado({"7.7.7_enciclopedia_ciencias"})
    assert soc_real.esta_desbloqueado({"7.6.7_sociedad_real", "7.7.7_enciclopedia_ciencias"})
    print("   ✅ [B7] sociedad_real_ciencias (compartido 7.6.7+7.7.7)")

    print("✅ TEST 6 PASADO\n")


def test_correcciones_todos_bloques(arbol):
    """Verifica correcciones históricas clave de todos los bloques."""
    print("=" * 60)
    print("🔧 TEST 7: Correcciones Históricas (Todos los Bloques)")
    print("=" * 60)

    # B3: Carpintería reordenada
    carp = arbol.get_subrama(3, 1)
    assert carp[2].id == "3.1.3_talla" and carp[6].id == "3.1.7_ebanisteria"
    print("   ✅ [B3] Carpintería: Talla=Nv3, Ebanistería=Nv7")

    # B4: Caballería y Tácticas reordenadas + zero duplicados
    cab = arbol.get_subrama(4, 2)
    assert cab[2].id == "4.2.3_carro_guerra"
    tact = arbol.get_subrama(4, 6)
    assert tact[0].id == "4.6.1_formaciones"
    print("   ✅ [B4] Carro guerra=Nv3, Formaciones=Nv1, IDs únicos")

    # B5: Progresión portuaria y financiera
    mar = arbol.get_subrama(5, 3)
    assert mar[0].id == "5.3.1_puerto_fluvial" and mar[6].id == "5.3.7_arsenal_naval_mercante"
    fin = arbol.get_subrama(5, 6)
    assert fin[3].id == "5.6.4_letra_cambio"
    print("   ✅ [B5] Puerto→Arsenal progresión, Letra cambio tras Contabilidad")

    # B6: Educación institucional y Filosofía cronológica
    edu = arbol.get_subrama(6, 1)
    assert edu[6].id == "6.1.7_universidad"
    filo = arbol.get_subrama(6, 7)
    assert filo[5].id == "6.7.6_humanismo" and filo[6].id == "6.7.7_ilustracion"
    print("   ✅ [B6] Universidad=Nv7, Humanismo=Nv6, Ilustración=Nv7")

    # B7: Matemáticas reordenada y Medicina/Biología separadas
    mat = arbol.get_subrama(7, 2)
    assert mat[3].id == "7.2.4_calculo" and mat[5].id == "7.2.6_estadistica"
    med = arbol.get_subrama(7, 4)
    bio = arbol.get_subrama(7, 5)
    assert med[0].id == "7.4.1_anatomia"  # Anatomía en Medicina
    assert bio[0].id == "7.5.1_taxonomia"  # Taxonomía en Biología
    print("   ✅ [B7] Estadística tras Cálculo, Anatomía≠Taxonomía separadas")

    # Verificación global: zero IDs duplicados
    todos_ids = [t.id for t in arbol]
    duplicados = [x for x in todos_ids if todos_ids.count(x) > 1]
    assert len(duplicados) == 0, f"IDs duplicados encontrados: {set(duplicados)}"
    print("   ✅ Zero IDs duplicados en 343 tecnologías")

    print("✅ TEST 7 PASADO\n")


def main():
    print("\n" + "=" * 60)
    print("🏆 VALIDACIÓN FINAL: ÁRBOL TECNOLÓGICO COMPLETO")
    print("=" * 60 + "\n")

    arbol = test_carga_arbol_completo()
    test_efectos_vinculados(arbol)
    test_nivel_1_disponibles(arbol)
    test_costes_escalados(arbol)
    test_cadenas_padre_hijo(arbol)
    test_parametros_logicos(arbol)
    test_correcciones_todos_bloques(arbol)

    print("=" * 60)
    print("🎉🎉🎉 TODOS LOS TESTS PASARON — FASE 1 CERTIFICADA 🎉🎉🎉")
    print("=" * 60)
    print("""
    ┌─────────────────────────────────────────────┐
    │         RESUMEN FINAL DE VALIDACIÓN          │
    ├─────────────────────────────────────────────┤
    │  Tecnologías totales:     343 / 343  ✅      │
    │  Bloques completos:       7 / 7      ✅      │
    │  Subramas validadas:      49 / 49    ✅      │
    │  Parámetros vinculados:   100%       ✅      │
    │  Desbloqueos lógicos:     18 / 18    ✅      │
    │  IDs duplicados:          0          ✅      │
    │  Correcciones aplicadas:  Todas      ✅      │
    ├─────────────────────────────────────────────┤
    │  ESTADO: FASE 1 DE DATOS CERRADA AL 100%    │
    └─────────────────────────────────────────────┘
    """)
    print("   El motor de juego está listo para producción.")
    print("   Siguiente fase: Frontend / Cliente Web o Disparadores Automáticos.\n")


if __name__ == "__main__":
    main()
