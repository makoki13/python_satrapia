# src/config/parametros_registro.py
"""
Registro Central de Parámetros del Juego.

Contiene la definición inmutable de todos los ParametroJuego.
Las investigaciones referencian estos IDs para modificar sus valores.
"""
from src.config.parametro_juego import ContribucionParametro, ParametroJuego


def _crear_registro_parametros() -> dict[str, ParametroJuego]:
    """
    Fábrica interna del registro.
    Se llama una vez al importar el módulo para garantizar inmutabilidad.
    """
    params: list[ParametroJuego] = [
        # ==========================================
        # BLOQUE 1: ALIMENTACIÓN (Piloto)
        # ==========================================

        # --- Producción ---
        ParametroJuego.numerico(
            id="prod_comida_granja",
            nombre="Producción de Comida (Granja)",
            valor_maximo=50.0,          # 50 comida/turno al 100%
            porcentaje_inicial=0.30,    # Empiezas al 30% (15/turno)
            contribuciones=[
                ContribucionParametro("1.1.1_regadio_inundacion", 0.10),
                ContribucionParametro("1.1.2_seleccion_semillas", 0.10),
                ContribucionParametro("1.1.3_ciclos", 0.05),
                ContribucionParametro("1.1.4_regadio_canales", 0.15),
                ContribucionParametro("1.1.5_recoleccion", 0.05),
                ContribucionParametro("1.1.6_herramientas_cosecha", 0.10),
                ContribucionParametro("1.1.7_rotacion_cultivos", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_comida_pesca",
            nombre="Producción de Comida (Pesca)",
            valor_maximo=40.0,
            porcentaje_inicial=0.25,
            contribuciones=[
                ContribucionParametro("1.2.1_aparejos", 0.10),
                ContribucionParametro("1.2.2_navegacion_costa", 0.10),
                ContribucionParametro("1.2.4_naves", 0.15),
                ContribucionParametro("1.2.5_navegacion_aguas_profundas", 0.20),
                ContribucionParametro("1.2.6_seguimiento_bancos", 0.15),
                ContribucionParametro("1.2.7_balleneros", 0.20),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_comida_ganaderia",
            nombre="Producción de Comida (Ganadería)",
            valor_maximo=45.0,
            porcentaje_inicial=0.20,
            contribuciones=[
                ContribucionParametro("1.4.1_ovino", 0.10),
                ContribucionParametro("1.4.2_bovino", 0.15),
                ContribucionParametro("1.4.3_porcino", 0.10),
                ContribucionParametro("1.4.5_aves", 0.10),
                ContribucionParametro("1.4.6_conejos", 0.10),
                ContribucionParametro("1.4.7_aparejos_ganaderos", 0.15),
            ],
        ),

        # --- Velocidad / Eficiencia ---
        ParametroJuego.numerico(
            id="velocidad_cosecha",
            nombre="Velocidad de Cosecha",
            valor_maximo=2.0,           # Multiplicador x2.0
            porcentaje_inicial=0.50,    # Empiezas al 50% (x1.0)
            contribuciones=[
                ContribucionParametro("1.1.5_recoleccion", 0.10),
                ContribucionParametro("1.1.6_herramientas_cosecha", 0.20),
                ContribucionParametro("1.1.7_rotacion_cultivos", 0.20),
            ],
        ),

        # --- Capacidad de Almacenamiento ---
        ParametroJuego.numerico(
            id="capacidad_silo_comida",
            nombre="Capacidad Silo de Comida",
            valor_maximo=5000.0,        # 5000 unidades al 100%
            porcentaje_inicial=0.40,    # Empiezas con 2000
            contribuciones=[
                ContribucionParametro("1.5.1_salazones", 0.10),
                ContribucionParametro("1.5.2_salmuera", 0.10),
                ContribucionParametro("1.5.4_neveros", 0.15),
                ContribucionParametro("1.5.5_confitado_aceite", 0.10),
                ContribucionParametro("1.5.6_esterilizacion", 0.15),
                ContribucionParametro("1.5.7_conservacion_avanzada", 0.20),
            ],
        ),

        # --- Reducción de Pérdidas (Plagas) ---
        ParametroJuego.numerico(
            id="reduccion_perdida_plagas",
            nombre="Reducción de Pérdidas por Plagas",
            valor_maximo=0.90,          # Máximo 90% de reducción
            porcentaje_inicial=0.0,     # Sin protección inicial
            contribuciones=[
                ContribucionParametro("1.3.1_medicinas", 0.10),
                ContribucionParametro("1.3.2_trampas", 0.10),
                ContribucionParametro("1.3.3_entomologia", 0.15),
                ContribucionParametro("1.3.4_redes", 0.10),
                ContribucionParametro("1.3.5_injertos", 0.15),
                ContribucionParametro("1.3.6_raticidas", 0.15),
                ContribucionParametro("1.3.7_prevencion", 0.25),
            ],
        ),

        # --- Desbloqueos Lógicos ---
        ParametroJuego.logico(
            id="pesca_aguas_profundas",
            nombre="Pesca en Aguas Profundas",
            contribuciones=[
                ContribucionParametro("1.2.5_navegacion_aguas_profundas", 1.0),
            ],
        ),
        ParametroJuego.logico(
            id="ganaderia_caballar",
            nombre="Cría de Caballos",
            contribuciones=[
                ContribucionParametro("1.4.4_caballeria", 1.0),
            ],
        ),
        ParametroJuego.logico(
            id="cocina_hornos",
            nombre="Tecnología de Hornos",
            contribuciones=[
                ContribucionParametro("1.7.3_hornos", 1.0),
            ],
        ),

        # ==========================================
        # BLOQUE 2: EXTRACCIÓN
        # ==========================================

        # --- Producción de Recursos ---
        ParametroJuego.numerico(
            id="prod_madera_serreria",
            nombre="Producción de Madera (Serrería)",
            valor_maximo=40.0,
            porcentaje_inicial=0.30,
            contribuciones=[
                ContribucionParametro("2.1.1_talado", 0.10),
                ContribucionParametro("2.1.2_podado", 0.05),
                ContribucionParametro("2.1.4_saca", 0.10),
                ContribucionParametro("2.1.6_cable", 0.15),
                ContribucionParametro("2.1.7_tala_selectiva", 0.10),
                ContribucionParametro("2.6.2_dendrometria", 0.10),
                ContribucionParametro("2.6.4_inventario_forestal", 0.10),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_piedra_cantera",
            nombre="Producción de Piedra (Cantera)",
            valor_maximo=35.0,
            porcentaje_inicial=0.25,
            contribuciones=[
                ContribucionParametro("2.2.2_cielo_abierto", 0.10),
                ContribucionParametro("2.2.3_canteras", 0.15),
                ContribucionParametro("2.2.4_pozos", 0.10),
                ContribucionParametro("2.3.2_perforadoras", 0.10),
                ContribucionParametro("2.7.3_mineralogia", 0.10),
                ContribucionParametro("2.7.6_perforacion_profunda", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_hierro_mina",
            nombre="Producción de Hierro (Mina)",
            valor_maximo=30.0,
            porcentaje_inicial=0.20,
            contribuciones=[
                ContribucionParametro("2.2.1_busqueda_vetas", 0.10),
                ContribucionParametro("2.2.5_hundimiento", 0.15),
                ContribucionParametro("2.3.1_picos_palas", 0.10),
                ContribucionParametro("2.3.3_brocas", 0.10),
                ContribucionParametro("2.7.2_cartografia", 0.10),
                ContribucionParametro("2.7.7_calculo_reservas", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_oro_mina",
            nombre="Producción de Oro (Mina)",
            valor_maximo=25.0,
            porcentaje_inicial=0.15,
            contribuciones=[
                ContribucionParametro("2.2.1_busqueda_vetas", 0.05),
                ContribucionParametro("2.2.6_lixiviacion", 0.20),
                ContribucionParametro("2.7.1_catas", 0.10),
                ContribucionParametro("2.7.3_mineralogia", 0.10),
                ContribucionParametro("2.7.7_calculo_reservas", 0.20),
            ],
        ),

        # --- Eficiencia y Velocidad ---
        ParametroJuego.numerico(
            id="velocidad_extraccion",
            nombre="Velocidad de Extracción",
            valor_maximo=2.0,
            porcentaje_inicial=0.50,
            contribuciones=[
                ContribucionParametro("2.1.3_arrastre", 0.10),
                ContribucionParametro("2.3.1_picos_palas", 0.10),
                ContribucionParametro("2.3.4_jumbos_perforacion", 0.20),
                ContribucionParametro("2.3.5_gruas", 0.15),
                ContribucionParametro("2.4.3_montacargas", 0.15),
            ],
        ),

        # --- Capacidad Logística ---
        ParametroJuego.numerico(
            id="capacidad_almacen_recursos",
            nombre="Capacidad Almacén de Recursos",
            valor_maximo=5000.0,
            porcentaje_inicial=0.40,
            contribuciones=[
                ContribucionParametro("2.4.1_carromatos", 0.10),
                ContribucionParametro("2.4.2_caravanas", 0.10),
                ContribucionParametro("2.4.5_estanterias", 0.15),
                ContribucionParametro("2.4.6_recipientes", 0.10),
                ContribucionParametro("2.4.4_gestion_inventarios", 0.15),
            ],
        ),

        # --- Seguridad ---
        ParametroJuego.numerico(
            id="reduccion_accidentes",
            nombre="Reducción de Accidentes Mineros/Forestales",
            valor_maximo=0.90,
            porcentaje_inicial=0.0,
            contribuciones=[
                ContribucionParametro("2.5.1_calzado", 0.10),
                ContribucionParametro("2.5.2_uniformes", 0.10),
                ContribucionParametro("2.5.3_inspeccion", 0.15),
                ContribucionParametro("2.5.4_balizas", 0.10),
                ContribucionParametro("2.5.5_rescate", 0.15),
                ContribucionParametro("2.5.6_antiincendios", 0.15),
                ContribucionParametro("2.5.7_legislacion_seguridad", 0.15),
            ],
        ),

        # --- Calidad ---
        ParametroJuego.numerico(
            id="calidad_mineral",
            nombre="Calidad del Mineral Extraído",
            valor_maximo=1.5,
            porcentaje_inicial=0.50,
            contribuciones=[
                ContribucionParametro("2.7.1_catas", 0.10),
                ContribucionParametro("2.7.3_mineralogia", 0.15),
                ContribucionParametro("2.7.4_sismologia", 0.10),
                ContribucionParametro("2.7.7_calculo_reservas", 0.15),
            ],
        ),

        # --- Desbloqueos Lógicos ---
        ParametroJuego.logico(
            id="sostenibilidad_forestal",
            nombre="Tala Sostenible Certificada",
            contribuciones=[
                ContribucionParametro("2.1.7_tala_selectiva", 0.5),
                ContribucionParametro("2.6.1_gestion_forestal_cientifica", 0.5),
            ],
        ),
        ParametroJuego.logico(
            id="mineria_submarina",
            nombre="Minería Submarina",
            contribuciones=[
                ContribucionParametro("2.2.7_submarina", 1.0),
            ],
        ),

                # ==========================================
        # BLOQUE 3: INDUSTRIA
        # ==========================================

        # --- Producción de Productos Procesados ---
        ParametroJuego.numerico(
            id="prod_madera_procesada",
            nombre="Producción de Madera Procesada",
            valor_maximo=30.0,
            porcentaje_inicial=0.20,
            contribuciones=[
                ContribucionParametro("3.1.1_aserradero", 0.10),
                ContribucionParametro("3.1.3_talla", 0.10),
                ContribucionParametro("3.1.5_ensamblaje", 0.10),
                ContribucionParametro("3.1.7_ebanisteria", 0.15),
                ContribucionParametro("3.6.2_estandares_calidad", 0.10),
                ContribucionParametro("3.6.5_division_trabajo", 0.10),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_piedra_tallada",
            nombre="Producción de Piedra Tallada",
            valor_maximo=25.0,
            porcentaje_inicial=0.15,
            contribuciones=[
                ContribucionParametro("3.2.1_corte_piedra", 0.10),
                ContribucionParametro("3.2.3_pulido", 0.10),
                ContribucionParametro("3.2.5_escultura", 0.15),
                ContribucionParametro("3.2.7_arquitectura_monumental", 0.20),
                ContribucionParametro("3.6.3_geometria_aplicada", 0.10),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_hierro_forjado",
            nombre="Producción de Hierro Forjado",
            valor_maximo=25.0,
            porcentaje_inicial=0.15,
            contribuciones=[
                ContribucionParametro("3.3.1_forja_basica", 0.10),
                ContribucionParametro("3.3.3_laminado", 0.10),
                ContribucionParametro("3.3.5_fundicion", 0.15),
                ContribucionParametro("3.3.7_acero", 0.20),
                ContribucionParametro("3.6.4_metalurgia_avanzada", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="prod_oro_refinado",
            nombre="Producción de Oro Refinado",
            valor_maximo=20.0,
            porcentaje_inicial=0.10,
            contribuciones=[
                ContribucionParametro("3.4.1_fundicion_oro", 0.10),
                ContribucionParametro("3.4.3_aleaciones", 0.15),
                ContribucionParametro("3.4.5_filigrana", 0.15),
                ContribucionParametro("3.4.7_amonedacion", 0.20),
                ContribucionParametro("3.6.4_metalurgia_avanzada", 0.10),
            ],
        ),

        # --- Eficiencia y Calidad ---
        ParametroJuego.numerico(
            id="eficiencia_transformacion",
            nombre="Eficiencia de Transformación Industrial",
            valor_maximo=2.0,
            porcentaje_inicial=0.50,
            contribuciones=[
                ContribucionParametro("3.1.2_herramientas_carpintero", 0.10),
                ContribucionParametro("3.2.2_herramientas_cantero", 0.10),
                ContribucionParametro("3.3.2_yunque_mejorado", 0.10),
                ContribucionParametro("3.5.2_engranajes", 0.15),
                ContribucionParametro("3.5.4_molino_viento", 0.15),
                ContribucionParametro("3.5.6_telar_mecanico", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="reduccion_desperdicio",
            nombre="Reducción de Desperdicio Industrial",
            valor_maximo=0.80,
            porcentaje_inicial=0.0,
            contribuciones=[
                ContribucionParametro("3.5.1_rueda", 0.05),
                ContribucionParametro("3.5.3_poleas", 0.10),
                ContribucionParametro("3.5.5_prensa", 0.15),
                ContribucionParametro("3.7.3_control_calidad", 0.15),
                ContribucionParametro("3.7.5_reciclaje_industrial", 0.20),
                ContribucionParametro("3.7.6_normativa_residuos", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="calidad_producto",
            nombre="Calidad del Producto Final",
            valor_maximo=1.5,
            porcentaje_inicial=0.50,
            contribuciones=[
                ContribucionParametro("3.6.1_aprendizaje", 0.10),
                ContribucionParametro("3.6.2_estandares_calidad", 0.15),
                ContribucionParametro("3.6.6_maestros_artesanos", 0.15),
                ContribucionParametro("3.7.3_control_calidad", 0.10),
            ],
        ),

        # --- Desbloqueos Lógicos ---
        ParametroJuego.logico(
            id="herreria_avanzada",
            nombre="Herrería Avanzada (Acero)",
            contribuciones=[
                ContribucionParametro("3.3.7_acero", 1.0),
            ],
        ),
        ParametroJuego.logico(
            id="maquinaria_hidraulica",
            nombre="Maquinaria Hidráulica",
            contribuciones=[
                ContribucionParametro("3.5.7_hidraulica", 1.0),
            ],
        ),
        ParametroJuego.logico(
            id="gremios_artesanos",
            nombre="Gremios Artesanos Organizados",
            contribuciones=[
                ContribucionParametro("3.6.7_cartas_gremiales", 0.5),
                ContribucionParametro("3.7.7_legislacion_gremial", 0.5),
            ],
        ),

                # ==========================================
        # BLOQUE 4: EJÉRCITO
        # ==========================================

        # --- Fuerza por tipo de unidad ---
        ParametroJuego.numerico(
            id="fuerza_infanteria",
            nombre="Fuerza de Infantería",
            valor_maximo=30.0,
            porcentaje_inicial=0.20,
            contribuciones=[
                ContribucionParametro("4.1.1_lanceros", 0.10),
                ContribucionParametro("4.1.3_escudos", 0.10),
                ContribucionParametro("4.1.5_hoplitas", 0.15),
                ContribucionParametro("4.1.7_legion", 0.20),
                ContribucionParametro("4.6.1_formaciones", 0.10),
                ContribucionParametro("4.6.4_disciplina", 0.10),
            ],
        ),
        ParametroJuego.numerico(
            id="fuerza_caballeria",
            nombre="Fuerza de Caballería",
            valor_maximo=25.0,
            porcentaje_inicial=0.15,
            contribuciones=[
                ContribucionParametro("4.2.1_jinetes_ligeros", 0.10),
                ContribucionParametro("4.2.3_carro_guerra", 0.10),
                ContribucionParametro("4.2.5_catafractos", 0.15),
                ContribucionParametro("4.2.7_caballeria_pesada", 0.20),
                ContribucionParametro("4.6.2_flanqueo", 0.10),
            ],
        ),
        ParametroJuego.numerico(
            id="fuerza_asedio",
            nombre="Fuerza de Asedio",
            valor_maximo=20.0,
            porcentaje_inicial=0.10,
            contribuciones=[
                ContribucionParametro("4.3.1_escalas", 0.05),
                ContribucionParametro("4.3.2_ariete", 0.10),
                ContribucionParametro("4.3.3_torre_asedio", 0.10),
                ContribucionParametro("4.3.5_catapulta", 0.15),
                ContribucionParametro("4.3.7_trabuquete", 0.20),
                ContribucionParametro("4.7.5_baluarte", 0.10),
            ],
        ),

        # --- Eficiencia y Moral ---
        ParametroJuego.numerico(
            id="moral_tropa",
            nombre="Moral de Tropa",
            valor_maximo=1.5,
            porcentaje_inicial=0.50,
            contribuciones=[
                ContribucionParametro("4.4.1_suministros", 0.10),
                ContribucionParametro("4.4.3_campamentos", 0.10),
                ContribucionParametro("4.4.5_hospitales", 0.15),
                ContribucionParametro("4.6.4_disciplina", 0.15),
                ContribucionParametro("4.6.6_oficiales", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="velocidad_marcha",
            nombre="Velocidad de Marcha",
            valor_maximo=2.0,
            porcentaje_inicial=0.50,
            contribuciones=[
                ContribucionParametro("4.4.2_caminos_militares", 0.15),
                ContribucionParametro("4.4.4_logistica_caravanas", 0.15),
                ContribucionParametro("4.5.1_exploradores", 0.10),
                ContribucionParametro("4.5.3_cartografia_militar", 0.10),
                ContribucionParametro("4.5.5_telegrafo_optico", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="capacidad_reclutamiento",
            nombre="Capacidad de Reclutamiento por Turno",
            valor_maximo=50.0,
            porcentaje_inicial=0.30,
            contribuciones=[
                ContribucionParametro("4.4.6_cuartel_general", 0.20),
                ContribucionParametro("4.4.7_academia_militar", 0.20),
                ContribucionParametro("4.7.3_barbacana", 0.10),
                ContribucionParametro("4.7.6_ciudadela", 0.15),
            ],
        ),
        ParametroJuego.numerico(
            id="reduccion_bajas",
            nombre="Reducción de Bajas en Combate",
            valor_maximo=0.70,
            porcentaje_inicial=0.0,
            contribuciones=[
                ContribucionParametro("4.5.2_vanguardia", 0.10),
                ContribucionParametro("4.5.4_emboscada_defensiva", 0.15),
                ContribucionParametro("4.6.3_retirada_ordenada", 0.15),
                ContribucionParametro("4.6.5_terreno_favorable", 0.15),
                ContribucionParametro("4.7.4_castillo_concentrico", 0.15),
            ],
        ),

        # --- Desbloqueos Lógicos ---
        ParametroJuego.logico(
            id="caballeria_pesada",
            nombre="Caballería Pesada",
            contribuciones=[
                ContribucionParametro("4.2.7_caballeria_pesada", 1.0),
            ],
        ),
        ParametroJuego.logico(
            id="maquinas_asedio_avanzadas",
            nombre="Máquinas de Asedio Avanzadas",
            contribuciones=[
                ContribucionParametro("4.3.7_trabuquete", 1.0),
            ],
        ),
        ParametroJuego.logico(
            id="doctrina_militar",
            nombre="Doctrina Militar Unificada",
            contribuciones=[
                ContribucionParametro("4.6.7_codigo_guerra", 0.5),
                ContribucionParametro("4.7.7_fortaleza_estrellada", 0.5),
            ],
        ),

        # ==========================================
        # PLACEHOLDERS PARA BLOQUES 5-7
        # Se rellenarán tras validar el piloto
        # ==========================================
        # Ejemplo futuro:
        # ParametroJuego.numerico(
        #     id="prod_madera_serreria",
        #     nombre="Producción de Madera (Serrería)",
        #     valor_maximo=40.0,
        #     porcentaje_inicial=0.30,
        #     contribuciones=[],
        # ),
    ]

    # Validar unicidad de IDs
    ids = [p.id for p in params]
    duplicados = set([i for i in ids if ids.count(i) > 1])
    if duplicados:
        raise ValueError(f"❌ IDs de parámetro duplicados: {duplicados}")

    return {p.id: p for p in params}


# ==========================================
# REGISTRO GLOBAL (Inmutable tras carga)
# ==========================================
REGISTRO_PARAMETROS: dict[str, ParametroJuego] = _crear_registro_parametros()


def get_parametro(id_parametro: str) -> ParametroJuego:
    """Obtiene un parámetro por ID. Lanza KeyError si no existe."""
    if id_parametro not in REGISTRO_PARAMETROS:
        raise KeyError(
            f"Parámetro '{id_parametro}' no encontrado en el registro. "
            f"IDs disponibles: {sorted(REGISTRO_PARAMETROS.keys())}"
        )
    return REGISTRO_PARAMETROS[id_parametro]


def listar_ids_parametros() -> list[str]:
    """Devuelve todos los IDs de parámetros ordenados."""
    return sorted(REGISTRO_PARAMETROS.keys())
