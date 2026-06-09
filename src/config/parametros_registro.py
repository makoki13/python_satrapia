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
        # PLACEHOLDERS PARA BLOQUES 2-7
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
