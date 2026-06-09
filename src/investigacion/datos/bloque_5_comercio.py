# src/investigacion/datos/bloque_5_comercio.py
"""
Datos de tecnologías del Bloque 5: Comercio.
49 tecnologías (7 subramas × 7 niveles).

CORRECCIONES CRÍTICAS RESPECTO AL PDF ORIGINAL:
- 5.2 Rutas Terrestres: "Posadas" movida a Nv3 (requiere caminos previos).
- 5.3 Rutas Marítimas: Progresión lógica Puerto→Muelle→Faro→Dársena→Astillero→Franco→Arsenal.
- 5.6 Finanzas: "Letra de cambio" reordenada tras "Contabilidad doble".
- IDs DUPLICADOS ELIMINADOS: Se asignaron IDs únicos secuenciales en todas las subramas.

Los IDs de efectos coinciden EXACTAMENTE con REGISTRO_PARAMETROS.
"""
from src.investigacion.tecnologia import EfectoTecnologia, Tecnologia

COSTE_ORO_BASE = 100
TURNOS_BASE = 3

# ==========================================
# SUBRAMA 5.1: MERCADOS
# ==========================================
TECHS_5_1_MERCADOS: list[Tecnologia] = [
    Tecnologia.crear(
        id="5.1.1_trueque", nombre="Trueque organizado",
        bloque=5, subrama=1, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("eficiencia_comercial", 0.10)],
        descripcion="Intercambio directo de bienes con valores de referencia acordados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.1.2_pesas_medidas", nombre="Pesas y medidas estandarizadas",
        bloque=5, subrama=1, nivel=2, padre_id="5.1.1_trueque",
        efectos=[EfectoTecnologia("velocidad_transaccion", 0.15)],
        descripcion="Unidades comunes que eliminan disputas en transacciones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.1.3_mercado_local", nombre="Mercado local permanente",
        bloque=5, subrama=1, nivel=3, padre_id="5.1.2_pesas_medidas",
        efectos=[EfectoTecnologia("eficiencia_comercial", 0.10)],
        descripcion="Espacio fijo de intercambio que concentra oferta y demanda.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.1.4_moneda_local", nombre="Moneda local acuñada",
        bloque=5, subrama=1, nivel=4, padre_id="5.1.3_mercado_local",
        efectos=[EfectoTecnologia("velocidad_transaccion", 0.15)],
        descripcion="Medio de pago oficial que acelera el comercio interno.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.1.5_feria_regional", nombre="Feria regional periódica",
        bloque=5, subrama=1, nivel=5, padre_id="5.1.4_moneda_local",
        efectos=[EfectoTecnologia("eficiencia_comercial", 0.15)],
        descripcion="Eventos comerciales masivos que atraen mercaderes externos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.1.6_contratos", nombre="Contratos mercantiles escritos",
        bloque=5, subrama=1, nivel=6, padre_id="5.1.5_feria_regional",
        efectos=[EfectoTecnologia("velocidad_transaccion", 0.10)],
        descripcion="Acuerdos formales que reducen riesgo y litigios comerciales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.1.7_bolsa_mercantil", nombre="Bolsa mercantil",
        bloque=5, subrama=1, nivel=7, padre_id="5.1.6_contratos",
        efectos=[
            EfectoTecnologia("eficiencia_comercial", 0.20),
            EfectoTecnologia("gremio_mercaderes", 0.5),
        ],
        descripcion="Mercado centralizado de materias primas con precios públicos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 5.2: RUTAS TERRESTRES (REORDENADA)
# NOTA: Posadas movida a Nv3 (requiere caminos empedrados previos)
# ==========================================
TECHS_5_2_RUTAS_TERRESTRES: list[Tecnologia] = [
    Tecnologia.crear(
        id="5.2.1_senderos", nombre="Senderos comerciales",
        bloque=5, subrama=2, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("capacidad_caravanas", 0.10)],
        descripcion="Rutas básicas trazadas entre asentamientos vecinos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.2.2_caminos_empedrados", nombre="Caminos empedrados",
        bloque=5, subrama=2, nivel=2, padre_id="5.2.1_senderos",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.10)],
        descripcion="Vías pavimentadas que permiten tránsito en toda estación.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Movido a Nv3 (infraestructura requiere vía previa)
    Tecnologia.crear(
        id="5.2.3_posadas", nombre="Red de posadas",
        bloque=5, subrama=2, nivel=3, padre_id="5.2.2_caminos_empedrados",
        efectos=[EfectoTecnologia("capacidad_caravanas", 0.10)],
        descripcion="Alojamiento seguro para mercaderes y bestias de carga.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.2.4_escorts", nombre="Escorts armados",
        bloque=5, subrama=2, nivel=4, padre_id="5.2.3_posadas",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.10)],
        descripcion="Protección contratada contra bandidos en rutas peligrosas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.2.5_caravasar", nombre="Caravasar fortificado",
        bloque=5, subrama=2, nivel=5, padre_id="5.2.4_escorts",
        efectos=[EfectoTecnologia("capacidad_caravanas", 0.15)],
        descripcion="Complejo amurallado con almacenes, establos y mercado interior.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.2.6_correos", nombre="Servicio de correos postal",
        bloque=5, subrama=2, nivel=6, padre_id="5.2.5_caravasar",
        efectos=[EfectoTecnologia("velocidad_transaccion", 0.10)],
        descripcion="Red de mensajería rápida para órdenes comerciales y noticias.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.2.7_ruta_seda", nombre="Gran Ruta Comercial",
        bloque=5, subrama=2, nivel=7, padre_id="5.2.6_correos",
        efectos=[EfectoTecnologia("capacidad_caravanas", 0.20)],
        descripcion="Corredor transcontinental que conecta civilizaciones distantes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 5.3: RUTAS MARÍTIMAS (PROGRESIÓN PORTUARIA)
# Progresión: Puerto fluvial → Muelle → Faro → Dársena → Astillero → Puerto franco → Arsenal
# ==========================================
TECHS_5_3_RUTAS_MARITIMAS: list[Tecnologia] = [
    Tecnologia.crear(
        id="5.3.1_puerto_fluvial", nombre="Puerto fluvial",
        bloque=5, subrama=3, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("volumen_maritimo", 0.10)],
        descripcion="Embarcadero básico en río navegable para comercio interior.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.3.2_muelle", nombre="Muelle de piedra",
        bloque=5, subrama=3, nivel=2, padre_id="5.3.1_puerto_fluvial",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.10)],
        descripcion="Estructura permanente que permite atracar barcos mayores.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.3.3_faro", nombre="Faro costero",
        bloque=5, subrama=3, nivel=3, padre_id="5.3.2_muelle",
        efectos=[EfectoTecnologia("volumen_maritimo", 0.10)],
        descripcion="Señalización nocturna que reduce naufragios y permite navegación segura.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.3.4_darsena", nombre="Dársena protegida",
        bloque=5, subrama=3, nivel=4, padre_id="5.3.3_faro",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.10)],
        descripcion="Bacín artificial cerrado que protege barcos de tormentas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.3.5_astillero_comercial", nombre="Astillero comercial",
        bloque=5, subrama=3, nivel=5, padre_id="5.3.4_darsena",
        efectos=[EfectoTecnologia("volumen_maritimo", 0.15)],
        descripcion="Instalación especializada en construcción y reparación de mercantes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.3.6_puerto_franco", nombre="Puerto franco",
        bloque=5, subrama=3, nivel=6, padre_id="5.3.5_astillero_comercial",
        efectos=[EfectoTecnologia("volumen_maritimo", 0.10)],
        descripcion="Zona portuaria exenta de aranceles que atrae comercio internacional.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.3.7_arsenal_naval_mercante", nombre="Arsenal naval mercante",
        bloque=5, subrama=3, nivel=7, padre_id="5.3.6_puerto_franco",
        efectos=[EfectoTecnologia("volumen_maritimo", 0.20)],
        descripcion="Complejo portuario industrial capaz de mantener flotas comerciales enteras.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 5.4: ADUANAS Y REGULACIÓN
# ==========================================
TECHS_5_4_ADUANAS: list[Tecnologia] = [
    Tecnologia.crear(
        id="5.4.1_peaje", nombre="Peaje de camino",
        bloque=5, subrama=4, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("ingresos_aduanas", 0.10)],
        descripcion="Impuesto por uso de vías comerciales principales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.4.2_inspectores", nombre="Inspectores de mercancías",
        bloque=5, subrama=4, nivel=2, padre_id="5.4.1_peaje",
        efectos=[EfectoTecnologia("ingresos_aduanas", 0.05)],
        descripcion="Funcionarios que verifican calidad y cantidad de bienes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.4.3_aranceles", nombre="Aranceles sistemáticos",
        bloque=5, subrama=4, nivel=3, padre_id="5.4.2_inspectores",
        efectos=[EfectoTecnologia("ingresos_aduanas", 0.15)],
        descripcion="Tarifas reguladas por tipo de bien y origen.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.4.4_cuarentena", nombre="Cuarentena sanitaria",
        bloque=5, subrama=4, nivel=4, padre_id="5.4.3_aranceles",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.05)],
        descripcion="Control de plagas que evita pérdidas catastróficas en cargamentos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.4.5_zona_libre", nombre="Zona de libre comercio",
        bloque=5, subrama=4, nivel=5, padre_id="5.4.4_cuarentena",
        efectos=[EfectoTecnologia("ingresos_aduanas", 0.10)],
        descripcion="Área designada donde se suspenden aranceles para reexportación.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.4.6_normas_origen", nombre="Certificación de origen",
        bloque=5, subrama=4, nivel=6, padre_id="5.4.5_zona_libre",
        efectos=[EfectoTecnologia("ingresos_aduanas", 0.10)],
        descripcion="Documentación que verifica procedencia para aplicar tarifas correctas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.4.7_tratado_comercial", nombre="Tratado comercial bilateral",
        bloque=5, subrama=4, nivel=7, padre_id="5.4.6_normas_origen",
        efectos=[EfectoTecnologia("ingresos_aduanas", 0.20)],
        descripcion="Acuerdo formal que reduce barreras entre dos reinos aliados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 5.5: LOGÍSTICA COMERCIAL
# ==========================================
TECHS_5_5_LOGISTICA_COM: list[Tecnologia] = [
    Tecnologia.crear(
        id="5.5.1_emballaje", nombre="Embalaje estandarizado",
        bloque=5, subrama=5, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.05)],
        descripcion="Contenedores uniformes que optimizan espacio en transporte.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.5.2_almacenes_transito", nombre="Almacenes de tránsito",
        bloque=5, subrama=5, nivel=2, padre_id="5.5.1_emballaje",
        efectos=[EfectoTecnologia("capacidad_caravanas", 0.10)],
        descripcion="Depósitos intermedios para consolidar y redistribuir cargas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.5.3_logistica_integrada", nombre="Logística integrada",
        bloque=5, subrama=5, nivel=3, padre_id="5.5.2_almacenes_transito",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.15)],
        descripcion="Coordinación multimodal terrestre-marítima sin rupturas de carga.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.5.4_seguros_maritimos", nombre="Seguros marítimos",
        bloque=5, subrama=5, nivel=4, padre_id="5.5.3_logistica_integrada",
        efectos=[EfectoTecnologia("volumen_maritimo", 0.10)],
        descripcion="Cobertura contra naufragio que incentiva comercio de alto riesgo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.5.5_red_comercial", nombre="Red comercial coordinada",
        bloque=5, subrama=5, nivel=5, padre_id="5.5.4_seguros_maritimos",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.15)],
        descripcion="Sistema de nodos interconectados con información compartida.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.5.6_flota_mercante", nombre="Flota mercante estatal",
        bloque=5, subrama=5, nivel=6, padre_id="5.5.5_red_comercial",
        efectos=[EfectoTecnologia("volumen_maritimo", 0.10)],
        descripcion="Barcos de propiedad pública para garantizar suministro estratégico.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.5.7_hub_logistico", nombre="Hub logístico central",
        bloque=5, subrama=5, nivel=7, padre_id="5.5.6_flota_mercante",
        efectos=[EfectoTecnologia("capacidad_caravanas", 0.15)],
        descripcion="Centro neurálgico que orquesta todo el flujo comercial del reino.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 5.6: FINANZAS (REORDENADA)
# NOTA: Letra de cambio movida tras Contabilidad doble
# ==========================================
TECHS_5_6_FINANZAS: list[Tecnologia] = [
    Tecnologia.crear(
        id="5.6.1_registro_mercantil", nombre="Registro mercantil",
        bloque=5, subrama=6, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("ingresos_aduanas", 0.10)],
        descripcion="Censo oficial de comerciantes y sus actividades tributables.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.6.2_contabilidad_doble", nombre="Contabilidad por partida doble",
        bloque=5, subrama=6, nivel=2, padre_id="5.6.1_registro_mercantil",
        efectos=[EfectoTecnologia("eficiencia_comercial", 0.10)],
        descripcion="Sistema contable que detecta errores y fraudes automáticamente.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Requiere contabilidad avanzada para funcionar
    Tecnologia.crear(
        id="5.6.3_banca_deposito", nombre="Banca de depósito",
        bloque=5, subrama=6, nivel=3, padre_id="5.6.2_contabilidad_doble",
        efectos=[
            EfectoTecnologia("velocidad_transaccion", 0.15),
            EfectoTecnologia("prestamo_comercial", 0.15),
        ],
        descripcion="Instituciones que custodian fondos y facilitan pagos sin mover oro.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.6.4_letra_cambio", nombre="Letra de cambio",
        bloque=5, subrama=6, nivel=4, padre_id="5.6.3_banca_deposito",
        efectos=[EfectoTecnologia("eficiencia_comercial", 0.10)],
        descripcion="Documento que permite pagar en una ciudad distinta sin transportar oro.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.6.5_giro_bancario", nombre="Giro bancario",
        bloque=5, subrama=6, nivel=5, padre_id="5.6.4_letra_cambio",
        efectos=[
            EfectoTecnologia("velocidad_transaccion", 0.15),
            EfectoTecnologia("prestamo_comercial", 0.15),
        ],
        descripcion="Transferencia instantánea entre sucursales bancarias.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.6.6_credito_documentario", nombre="Crédito documentario",
        bloque=5, subrama=6, nivel=6, padre_id="5.6.5_giro_bancario",
        efectos=[EfectoTecnologia("prestamo_comercial", 0.20)],
        descripcion="Garantía bancaria que asegura pago al vendedor contra documentos de envío.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.6.7_banca_internacional", nombre="Banca internacional",
        bloque=5, subrama=6, nivel=7, padre_id="5.6.6_credito_documentario",
        efectos=[
            EfectoTecnologia("moneda_unificada", 1.0),
            EfectoTecnologia("banca_internacional", 0.5),
        ],
        descripcion="Red financiera transnacional que opera con moneda propia aceptada globalmente.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 5.7: DIPLOMACIA COMERCIAL
# ==========================================
TECHS_5_7_DIPLOMACIA_COM: list[Tecnologia] = [
    Tecnologia.crear(
        id="5.7.1_embajadores", nombre="Embajadores comerciales",
        bloque=5, subrama=7, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("velocidad_transaccion", 0.05)],
        descripcion="Representantes que negocian acceso a mercados extranjeros.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.7.2_consulados", nombre="Consulados mercantiles",
        bloque=5, subrama=7, nivel=2, padre_id="5.7.1_embajadores",
        efectos=[EfectoTecnologia("velocidad_transaccion", 0.05)],
        descripcion="Oficinas en puertos extranjeros que protegen intereses de mercaderes propios.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.7.3_acuerdos_bilaterales", nombre="Acuerdos bilaterales",
        bloque=5, subrama=7, nivel=3, padre_id="5.7.2_consulados",
        efectos=[EfectoTecnologia("velocidad_transaccion", 0.10)],
        descripcion="Pactos recíprocos que reducen fricciones comerciales entre dos reinos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.7.4_extraterritorialidad", nombre="Extraterritorialidad mercantil",
        bloque=5, subrama=7, nivel=4, padre_id="5.7.3_acuerdos_bilaterales",
        efectos=[EfectoTecnologia("reduccion_costes_ruta", 0.05)],
        descripcion="Mercaderes juzgados por leyes propias, no las del país anfitrión.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.7.5_diplomacia_economica", nombre="Diplomacia económica",
        bloque=5, subrama=7, nivel=5, padre_id="5.7.4_extraterritorialidad",
        efectos=[EfectoTecnologia("prestamo_comercial", 0.15)],
        descripcion="Uso de incentivos comerciales como herramienta de política exterior.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.7.6_union_aduanera", nombre="Unión aduanera",
        bloque=5, subrama=7, nivel=6, padre_id="5.7.5_diplomacia_economica",
        efectos=[EfectoTecnologia("prestamo_comercial", 0.15)],
        descripcion="Territorio compartido sin aranceles internos y tarifa externa común.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="5.7.7_carta_comercial", nombre="Carta comercial internacional",
        bloque=5, subrama=7, nivel=7, padre_id="5.7.6_union_aduanera",
        efectos=[
            EfectoTecnologia("gremio_mercaderes", 0.5),
            EfectoTecnologia("banca_internacional", 0.5),
        ],
        descripcion="Marco legal supranacional que regula y protege el comercio global.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# EXPORTACIÓN UNIFICADA DEL BLOQUE 5
# ==========================================
TECNOLOGIAS_BLOQUE_5: list[Tecnologia] = (
    TECHS_5_1_MERCADOS
    + TECHS_5_2_RUTAS_TERRESTRES
    + TECHS_5_3_RUTAS_MARITIMAS
    + TECHS_5_4_ADUANAS
    + TECHS_5_5_LOGISTICA_COM
    + TECHS_5_6_FINANZAS
    + TECHS_5_7_DIPLOMACIA_COM
)
