# src/investigacion/datos/bloque_2_extraccion.py
"""
Datos de tecnologías del Bloque 2: Extracción.
49 tecnologías (7 subramas × 7 niveles).

CORRECCIONES APLICADAS RESPECTO AL PDF ORIGINAL:
- 2.1 Forestal: Reordenada. "Sostenibilidad" movida a Nv7, "Cable" a Nv6, "Tala Selectiva" a Nv5.
- 2.2 Minera: Reordenada. "Canteras" a Nv3, "Pozos" a Nv4, "Hundimiento" a Nv5, "Lixiviación" a Nv6.
- 2.6.1: Renombrada a "Gestión Forestal Científica" para evitar colisión con 2.1.7.
- 2.5.7: Renombrada a "Legislación Seguridad" para diferenciarla de otras legislaciones.

Los IDs de efectos coinciden EXACTAMENTE con REGISTRO_PARAMETROS.
"""
from src.investigacion.tecnologia import EfectoTecnologia, Tecnologia

# ==========================================
# CONSTANTES DE COSTE BASE
# ==========================================
COSTE_ORO_BASE = 100
TURNOS_BASE = 3

# ==========================================
# SUBRAMA 2.1: TÉCNICAS FORESTALES (REORDENADA)
# Progresión lógica: Talado → Podado → Arrastre → Saca → Tala Selectiva → Cable → Sostenibilidad
# NOTA: Los IDs mantienen la numeración original del PDF pero se asignan al nivel corregido.
# ==========================================
TECHS_2_1_FORESTAL: list[Tecnologia] = [
    Tecnologia.crear(
        id="2.1.1_talado",
        nombre="Talado básico",
        bloque=2, subrama=1, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.10)],
        descripcion="Tala manual de árboles con hachas y sierras de mano.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.1.2_podado",
        nombre="Podado controlado",
        bloque=2, subrama=1, nivel=2, padre_id="2.1.1_talado",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.05)],
        descripcion="Eliminación selectiva de ramas para mejorar calidad de la madera.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.1.3_arrastre",
        nombre="Arrastre de troncos",
        bloque=2, subrama=1, nivel=3, padre_id="2.1.2_podado",
        efectos=[EfectoTecnologia("velocidad_extraccion", 0.10)],
        descripcion="Uso de animales de tiro para mover troncos desde el bosque.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.1.4_saca",
        nombre="Saca organizada",
        bloque=2, subrama=1, nivel=4, padre_id="2.1.3_arrastre",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.10)],
        descripcion="Extracción planificada por zonas para optimizar rendimiento.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Tala Selectiva era 2.1.7 en PDF, ahora es Nv5 por lógica histórica
    Tecnologia.crear(
        id="2.1.7_tala_selectiva",
        nombre="Tala selectiva",
        bloque=2, subrama=1, nivel=5, padre_id="2.1.4_saca",
        efectos=[
            EfectoTecnologia("prod_madera_serreria", 0.10),
            EfectoTecnologia("sostenibilidad_forestal", 0.5),  # Contribución parcial al desbloqueo lógico
        ],
        descripcion="Extraer solo árboles maduros preservando el bosque joven.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Cable era 2.1.6 en PDF, ahora es Nv6
    Tecnologia.crear(
        id="2.1.6_cable",
        nombre="Transporte por cable",
        bloque=2, subrama=1, nivel=6, padre_id="2.1.7_tala_selectiva",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.15)],
        descripcion="Sistemas de cables y poleas para extraer madera de terrenos escarpados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Sostenibilidad era 2.1.5 en PDF, ahora es Nv7 (culminación técnica+ética)
    Tecnologia.crear(
        id="2.1.5_sostenibilidad_practica",
        nombre="Explotación sostenible",
        bloque=2, subrama=1, nivel=7, padre_id="2.1.6_cable",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.10)],
        descripcion="Equilibrio entre extracción y regeneración natural del bosque.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 2.2: TÉCNICAS MINERAS (REORDENADA)
# Progresión lógica: Búsqueda → Cielo abierto → Canteras → Pozos → Hundimiento → Lixiviación → Submarina
# ==========================================
TECHS_2_2_MINERA: list[Tecnologia] = [
    Tecnologia.crear(
        id="2.2.1_busqueda_vetas",
        nombre="Búsqueda de vetas",
        bloque=2, subrama=2, nivel=1, padre_id=None,
        efectos=[
            EfectoTecnologia("prod_hierro_mina", 0.10),
            EfectoTecnologia("prod_oro_mina", 0.05),
        ],
        descripcion="Identificación superficial de yacimientos minerales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.2.2_cielo_abierto",
        nombre="Minería a cielo abierto",
        bloque=2, subrama=2, nivel=2, padre_id="2.2.1_busqueda_vetas",
        efectos=[EfectoTecnologia("prod_piedra_cantera", 0.10)],
        descripcion="Excavación superficial para extraer piedra y minerales cercanos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Canteras era 2.2.6 en PDF, ahora es Nv3 (más antigua que pozos profundos)
    Tecnologia.crear(
        id="2.2.6_canteras",
        nombre="Canteras organizadas",
        bloque=2, subrama=2, nivel=3, padre_id="2.2.2_cielo_abierto",
        efectos=[EfectoTecnologia("prod_piedra_cantera", 0.15)],
        descripcion="Extracción sistemática de bloques de piedra para construcción.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Por pozos era 2.2.4 en PDF, ahora es Nv4
    Tecnologia.crear(
        id="2.2.4_pozos",
        nombre="Minería por pozos",
        bloque=2, subrama=2, nivel=4, padre_id="2.2.6_canteras",
        efectos=[EfectoTecnologia("prod_hierro_mina", 0.10)],
        descripcion="Pozos verticales para alcanzar vetas profundas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Hundimiento era 2.2.3 en PDF, ahora es Nv5 (técnica avanzada de túneles)
    Tecnologia.crear(
        id="2.2.3_hundimiento",
        nombre="Minería por hundimiento",
        bloque=2, subrama=2, nivel=5, padre_id="2.2.4_pozos",
        efectos=[EfectoTecnologia("prod_hierro_mina", 0.15)],
        descripcion="Provocar colapso controlado de vetas para extraer mineral masivamente.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Lixiviación era 2.2.5 en PDF, ahora es Nv6 (proceso químico moderno)
    Tecnologia.crear(
        id="2.2.5_lixiviacion",
        nombre="Lixiviación química",
        bloque=2, subrama=2, nivel=6, padre_id="2.2.3_hundimiento",
        efectos=[EfectoTecnologia("prod_oro_mina", 0.20)],
        descripcion="Disolución química de metales preciosos de baja ley.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.2.7_submarina",
        nombre="Minería submarina",
        bloque=2, subrama=2, nivel=7, padre_id="2.2.5_lixiviacion",
        efectos=[
            EfectoTecnologia("prod_oro_mina", 0.15),
            EfectoTecnologia("mineria_submarina", 1.0),  # Desbloqueo lógico
        ],
        descripcion="Extracción de nódulos polimetálicos del fondo marino.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 2.3: HERRAMIENTAS Y CONOCIMIENTO
# ==========================================
TECHS_2_3_HERRAMIENTAS: list[Tecnologia] = [
    Tecnologia.crear(
        id="2.3.1_picos_palas",
        nombre="Picos y palas metálicas",
        bloque=2, subrama=3, nivel=1, padre_id=None,
        efectos=[
            EfectoTecnologia("prod_hierro_mina", 0.10),
            EfectoTecnologia("velocidad_extraccion", 0.10),
        ],
        descripcion="Herramientas básicas de hierro para excavación manual.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.3.2_perforadoras",
        nombre="Perforadoras mecánicas",
        bloque=2, subrama=3, nivel=2, padre_id="2.3.1_picos_palas",
        efectos=[EfectoTecnologia("prod_piedra_cantera", 0.10)],
        descripcion="Máquinas de percusión para romper roca dura.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.3.3_brocas",
        nombre="Brocas reforzadas",
        bloque=2, subrama=3, nivel=3, padre_id="2.3.2_perforadoras",
        efectos=[EfectoTecnologia("prod_hierro_mina", 0.10)],
        descripcion="Puntas de perforación templadas para mayor durabilidad.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.3.4_jumbos_perforacion",
        nombre="Jumbos de perforación",
        bloque=2, subrama=3, nivel=4, padre_id="2.3.3_brocas",
        efectos=[EfectoTecnologia("velocidad_extraccion", 0.20)],
        descripcion="Plataformas móviles multi-brazo para túneles rápidos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.3.5_gruas",
        nombre="Grúas de extracción",
        bloque=2, subrama=3, nivel=5, padre_id="2.3.4_jumbos_perforacion",
        efectos=[EfectoTecnologia("velocidad_extraccion", 0.15)],
        descripcion="Sistemas de elevación para sacar mineral de pozos profundos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.3.6_geologia",
        nombre="Geología aplicada",
        bloque=2, subrama=3, nivel=6, padre_id="2.3.5_gruas",
        efectos=[EfectoTecnologia("calidad_mineral", 0.10)],
        descripcion="Comprensión de formaciones rocosas para localizar vetas ricas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.3.7_maestria",
        nombre="Maestría extractiva",
        bloque=2, subrama=3, nivel=7, padre_id="2.3.6_geologia",
        efectos=[EfectoTecnologia("velocidad_extraccion", 0.15)],
        descripcion="Conocimiento acumulado que optimiza todos los procesos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 2.4: TRANSPORTE Y ALMACENAMIENTO
# ==========================================
TECHS_2_4_TRANSPORTE: list[Tecnologia] = [
    Tecnologia.crear(
        id="2.4.1_carromatos",
        nombre="Carromatos de carga",
        bloque=2, subrama=4, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("capacidad_almacen_recursos", 0.10)],
        descripcion="Vehículos tirados por animales para transporte terrestre.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.4.2_caravanas",
        nombre="Caravanas organizadas",
        bloque=2, subrama=4, nivel=2, padre_id="2.4.1_carromatos",
        efectos=[EfectoTecnologia("capacidad_almacen_recursos", 0.10)],
        descripcion="Rutas comerciales regulares con protección y logística.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.4.3_montacargas",
        nombre="Montacargas",
        bloque=2, subrama=4, nivel=3, padre_id="2.4.2_caravanas",
        efectos=[EfectoTecnologia("velocidad_extraccion", 0.15)],
        descripcion="Mecanismos para elevar y mover cargas pesadas verticalmente.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.4.4_gestion_inventarios",
        nombre="Gestión de inventarios",
        bloque=2, subrama=4, nivel=4, padre_id="2.4.3_montacargas",
        efectos=[EfectoTecnologia("capacidad_almacen_recursos", 0.15)],
        descripcion="Registro sistemático de entradas y salidas de recursos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.4.5_estanterias",
        nombre="Estanterías industriales",
        bloque=2, subrama=4, nivel=5, padre_id="2.4.4_gestion_inventarios",
        efectos=[EfectoTecnologia("capacidad_almacen_recursos", 0.15)],
        descripcion="Almacenamiento vertical organizado para maximizar espacio.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.4.6_recipientes",
        nombre="Recipientes estandarizados",
        bloque=2, subrama=4, nivel=6, padre_id="2.4.5_estanterias",
        efectos=[EfectoTecnologia("capacidad_almacen_recursos", 0.10)],
        descripcion="Contenedores uniformes que facilitan carga y descarga.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.4.7_normativa",
        nombre="Normativa de transporte",
        bloque=2, subrama=4, nivel=7, padre_id="2.4.6_recipientes",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.10)],
        descripcion="Regulaciones que reducen pérdidas y accidentes en rutas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 2.5: SEGURIDAD
# ==========================================
TECHS_2_5_SEGURIDAD: list[Tecnologia] = [
    Tecnologia.crear(
        id="2.5.1_calzado",
        nombre="Calzado de seguridad",
        bloque=2, subrama=5, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.10)],
        descripcion="Botas reforzadas que protegen contra caídas de material.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.5.2_uniformes",
        nombre="Uniformes protectores",
        bloque=2, subrama=5, nivel=2, padre_id="2.5.1_calzado",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.10)],
        descripcion="Ropa resistente a cortes, polvo y humedad.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.5.3_inspeccion",
        nombre="Inspección regular",
        bloque=2, subrama=5, nivel=3, padre_id="2.5.2_uniformes",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.15)],
        descripcion="Revisiones periódicas de túneles y equipos preventivos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.5.4_balizas",
        nombre="Balizas y señalización",
        bloque=2, subrama=5, nivel=4, padre_id="2.5.3_inspeccion",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.10)],
        descripcion="Marcado de zonas peligrosas y rutas de evacuación.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.5.5_rescate",
        nombre="Equipos de rescate",
        bloque=2, subrama=5, nivel=5, padre_id="2.5.4_balizas",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.15)],
        descripcion="Brigadas especializadas y equipo para emergencias mineras.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.5.6_antiincendios",
        nombre="Sistemas antiincendios",
        bloque=2, subrama=5, nivel=6, padre_id="2.5.5_rescate",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.15)],
        descripcion="Detección y supresión de fuegos en instalaciones extractivas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.5.7_legislacion_seguridad",
        nombre="Legislación de seguridad",
        bloque=2, subrama=5, nivel=7, padre_id="2.5.6_antiincendios",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.15)],
        descripcion="Marco legal obligatorio que estandariza todas las medidas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 2.6: INVESTIGACIÓN FORESTAL
# NOTA: 2.6.1 renombrada para evitar colisión con 2.1.5/2.1.7
# ==========================================
TECHS_2_6_INV_FORESTAL: list[Tecnologia] = [
    Tecnologia.crear(
        id="2.6.1_gestion_forestal_cientifica",
        nombre="Gestión forestal científica",
        bloque=2, subrama=6, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("sostenibilidad_forestal", 0.5)],  # Contribución parcial al desbloqueo lógico
        descripcion="Aplicación de método científico a la silvicultura.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.6.2_dendrometria",
        nombre="Dendrometría",
        bloque=2, subrama=6, nivel=2, padre_id="2.6.1_gestion_forestal_cientifica",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.10)],
        descripcion="Medición precisa de dimensiones y volumen arbóreo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.6.3_epidometria",
        nombre="Epidometría",
        bloque=2, subrama=6, nivel=3, padre_id="2.6.2_dendrometria",
        efectos=[EfectoTecnologia("calidad_mineral", 0.05)],  # Bonus menor por conocimiento ecológico
        descripcion="Estudio de crecimiento y salud de masas forestales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.6.4_inventario_forestal",
        nombre="Inventario forestal",
        bloque=2, subrama=6, nivel=4, padre_id="2.6.3_epidometria",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.10)],
        descripcion="Censo completo de especies y volúmenes disponibles.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.6.5_sig",
        nombre="Sistemas de información geográfica",
        bloque=2, subrama=6, nivel=5, padre_id="2.6.4_inventario_forestal",
        efectos=[EfectoTecnologia("velocidad_extraccion", 0.10)],
        descripcion="Cartografía digital para planificación extractiva.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.6.6_regeneracion",
        nombre="Regeneración asistida",
        bloque=2, subrama=6, nivel=6, padre_id="2.6.5_sig",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.10)],
        descripcion="Reforestación activa tras ciclos de tala.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.6.7_bancos_semillas",
        nombre="Bancos de semillas",
        bloque=2, subrama=6, nivel=7, padre_id="2.6.6_regeneracion",
        efectos=[EfectoTecnologia("prod_madera_serreria", 0.10)],
        descripcion="Preservación de diversidad genética forestal.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 2.7: INVESTIGACIÓN MINERA
# ==========================================
TECHS_2_7_INV_MINERA: list[Tecnologia] = [
    Tecnologia.crear(
        id="2.7.1_catas",
        nombre="Catas exploratorias",
        bloque=2, subrama=7, nivel=1, padre_id=None,
        efectos=[
            EfectoTecnologia("prod_oro_mina", 0.10),
            EfectoTecnologia("calidad_mineral", 0.10),
        ],
        descripcion="Perforaciones de prueba para evaluar riqueza del yacimiento.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.7.2_cartografia",
        nombre="Cartografía minera",
        bloque=2, subrama=7, nivel=2, padre_id="2.7.1_catas",
        efectos=[EfectoTecnologia("prod_hierro_mina", 0.10)],
        descripcion="Mapas detallados de galerías y vetas subterráneas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.7.3_mineralogia",
        nombre="Mineralogía avanzada",
        bloque=2, subrama=7, nivel=3, padre_id="2.7.2_cartografia",
        efectos=[
            EfectoTecnologia("prod_piedra_cantera", 0.10),
            EfectoTecnologia("prod_oro_mina", 0.10),
            EfectoTecnologia("calidad_mineral", 0.15),
        ],
        descripcion="Identificación y clasificación precisa de minerales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.7.4_sismologia",
        nombre="Sismología aplicada",
        bloque=2, subrama=7, nivel=4, padre_id="2.7.3_mineralogia",
        efectos=[EfectoTecnologia("calidad_mineral", 0.10)],
        descripcion="Detección de estructuras profundas mediante ondas sísmicas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.7.5_legislacion_minera",
        nombre="Legislación minera",
        bloque=2, subrama=7, nivel=5, padre_id="2.7.4_sismologia",
        efectos=[EfectoTecnologia("reduccion_accidentes", 0.05)],
        descripcion="Marco regulatorio para concesiones y explotación responsable.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.7.6_perforacion_profunda",
        nombre="Perforación profunda",
        bloque=2, subrama=7, nivel=6, padre_id="2.7.5_legislacion_minera",
        efectos=[EfectoTecnologia("prod_piedra_cantera", 0.15)],
        descripcion="Tecnología para alcanzar yacimientos a gran profundidad.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="2.7.7_calculo_reservas",
        nombre="Cálculo de reservas",
        bloque=2, subrama=7, nivel=7, padre_id="2.7.6_perforacion_profunda",
        efectos=[
            EfectoTecnologia("prod_hierro_mina", 0.15),
            EfectoTecnologia("prod_oro_mina", 0.20),
            EfectoTecnologia("calidad_mineral", 0.15),
        ],
        descripcion="Estimación precisa de vida útil y rentabilidad del yacimiento.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# EXPORTACIÓN UNIFICADA DEL BLOQUE 2
# ==========================================
TECNOLOGIAS_BLOQUE_2: list[Tecnologia] = (
    TECHS_2_1_FORESTAL
    + TECHS_2_2_MINERA
    + TECHS_2_3_HERRAMIENTAS
    + TECHS_2_4_TRANSPORTE
    + TECHS_2_5_SEGURIDAD
    + TECHS_2_6_INV_FORESTAL
    + TECHS_2_7_INV_MINERA
)
