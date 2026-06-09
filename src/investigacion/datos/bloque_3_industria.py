# src/investigacion/datos/bloque_3_industria.py
"""
Datos de tecnologías del Bloque 3: Industria.
49 tecnologías (7 subramas × 7 niveles).

CORRECCIONES APLICADAS RESPECTO AL PDF ORIGINAL:
- 3.1 Carpintería: "Talla" subida a Nv3, "Ensamblaje" a Nv5, "Ebanistería" a Nv7.
- 3.3 Herrería: "Fundición" reordenada a Nv5 (tras Forja/Laminado), "Acero" a Nv7.
- 3.5 Maquinaria: Progresión lógica Rueda→Engranajes→Poleas→Molino→Prensa→Telar→Hidráulica.
- 3.7 Seguridad Industrial: Renombrada para diferenciar de 2.5.7/2.7.5. "Gremios" contribuye al lógico compartido.

Los IDs de efectos coinciden EXACTAMENTE con REGISTRO_PARAMETROS.
"""
from src.investigacion.tecnologia import EfectoTecnologia, Tecnologia

COSTE_ORO_BASE = 100
TURNOS_BASE = 3

# ==========================================
# SUBRAMA 3.1: CARPINTERÍA (REORDENADA)
# Progresión: Aserradero → Herramientas → Talla → Ensamblaje → Torneado → Barnices → Ebanistería
# ==========================================
TECHS_3_1_CARPINTERIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="3.1.1_aserradero", nombre="Aserradero",
        bloque=3, subrama=1, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_madera_procesada", 0.10)],
        descripcion="Sierra mecánica básica para cortar troncos en tablones uniformes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.1.2_herramientas_carpintero", nombre="Herramientas de carpintero",
        bloque=3, subrama=1, nivel=2, padre_id="3.1.1_aserradero",
        efectos=[EfectoTecnologia("eficiencia_transformacion", 0.10)],
        descripcion="Garlopas, formones y sierras de precisión para trabajo fino.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.1.3_talla", nombre="Talla ornamental",
        bloque=3, subrama=1, nivel=3, padre_id="3.1.2_herramientas_carpintero",
        efectos=[EfectoTecnologia("prod_madera_procesada", 0.10)],
        descripcion="Decoración escultórica en madera para muebles y estructuras.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.1.4_torneado", nombre="Torneado",
        bloque=3, subrama=1, nivel=4, padre_id="3.1.3_talla",
        efectos=[EfectoTecnologia("calidad_producto", 0.05)],
        descripcion="Uso del torno para crear piezas cilíndricas simétricas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.1.5_ensamblaje", nombre="Ensamblaje avanzado",
        bloque=3, subrama=1, nivel=5, padre_id="3.1.4_torneado",
        efectos=[EfectoTecnologia("prod_madera_procesada", 0.10)],
        descripcion="Juntas complejas sin clavos que aumentan durabilidad y calidad.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.1.6_barnices", nombre="Barnices y lacas",
        bloque=3, subrama=1, nivel=6, padre_id="3.1.5_ensamblaje",
        efectos=[EfectoTecnologia("calidad_producto", 0.05)],
        descripcion="Acabados protectores que embellecen y preservan la madera.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.1.7_ebanisteria", nombre="Ebanistería fina",
        bloque=3, subrama=1, nivel=7, padre_id="3.1.6_barnices",
        efectos=[EfectoTecnologia("prod_madera_procesada", 0.15)],
        descripcion="Maestría en maderas nobles para mobiliario de lujo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 3.2: CANTERÍA
# Progresión: Corte → Herramientas → Pulido → Arcos → Escultura → Bóvedas → Arquitectura Monumental
# ==========================================
TECHS_3_2_CANTERIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="3.2.1_corte_piedra", nombre="Corte de piedra",
        bloque=3, subrama=2, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_piedra_tallada", 0.10)],
        descripcion="Técnicas básicas de extracción y corte de bloques regulares.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.2.2_herramientas_cantero", nombre="Herramientas de cantero",
        bloque=3, subrama=2, nivel=2, padre_id="3.2.1_corte_piedra",
        efectos=[EfectoTecnologia("eficiencia_transformacion", 0.10)],
        descripcion="Cinceles, mazas y punteros de acero templado.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.2.3_pulido", nombre="Pulido de piedra",
        bloque=3, subrama=2, nivel=3, padre_id="3.2.2_herramientas_cantero",
        efectos=[EfectoTecnologia("prod_piedra_tallada", 0.10)],
        descripcion="Acabado liso mediante abrasivos naturales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.2.4_arcos", nombre="Construcción de arcos",
        bloque=3, subrama=2, nivel=4, padre_id="3.2.3_pulido",
        efectos=[EfectoTecnologia("calidad_producto", 0.05)],
        descripcion="Dovelas y cimbras para vanos estables sin dinteles.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.2.5_escultura", nombre="Escultura en piedra",
        bloque=3, subrama=2, nivel=5, padre_id="3.2.4_arcos",
        efectos=[EfectoTecnologia("prod_piedra_tallada", 0.15)],
        descripcion="Representaciones figurativas y relieves decorativos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.2.6_bovedas", nombre="Bóvedas y cúpulas",
        bloque=3, subrama=2, nivel=6, padre_id="3.2.5_escultura",
        efectos=[EfectoTecnologia("calidad_producto", 0.10)],
        descripcion="Cubiertas curvas que permiten grandes espacios interiores.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.2.7_arquitectura_monumental", nombre="Arquitectura monumental",
        bloque=3, subrama=2, nivel=7, padre_id="3.2.6_bovedas",
        efectos=[EfectoTecnologia("prod_piedra_tallada", 0.20)],
        descripcion="Edificios colosales que proyectan poder y permanencia.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 3.3: HERRERÍA (REORDENADA)
# Progresión: Forja básica → Yunque → Laminado → Temple → Fundición → Aleaciones → Acero
# ==========================================
TECHS_3_3_HERRERIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="3.3.1_forja_basica", nombre="Forja básica",
        bloque=3, subrama=3, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_hierro_forjado", 0.10)],
        descripcion="Calentamiento y martillado manual del hierro.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.3.2_yunque_mejorado", nombre="Yunque mejorado",
        bloque=3, subrama=3, nivel=2, padre_id="3.3.1_forja_basica",
        efectos=[EfectoTecnologia("eficiencia_transformacion", 0.10)],
        descripcion="Yunque de acero con cuerno y mesa para formas complejas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.3.3_laminado", nombre="Laminado",
        bloque=3, subrama=3, nivel=3, padre_id="3.3.2_yunque_mejorado",
        efectos=[EfectoTecnologia("prod_hierro_forjado", 0.10)],
        descripcion="Rodillos para obtener láminas y barras uniformes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.3.4_temple", nombre="Temple y revenido",
        bloque=3, subrama=3, nivel=4, padre_id="3.3.3_laminado",
        efectos=[EfectoTecnologia("calidad_producto", 0.10)],
        descripcion="Tratamientos térmicos que endurecen el metal sin fragilizarlo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.3.5_fundicion", nombre="Fundición de hierro",
        bloque=3, subrama=3, nivel=5, padre_id="3.3.4_temple",
        efectos=[EfectoTecnologia("prod_hierro_forjado", 0.15)],
        descripcion="Altos hornos que licuan el hierro para moldes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.3.6_aleaciones", nombre="Aleaciones ferrosas",
        bloque=3, subrama=3, nivel=6, padre_id="3.3.5_fundicion",
        efectos=[EfectoTecnologia("calidad_producto", 0.10)],
        descripcion="Mezcla controlada de metales para propiedades específicas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.3.7_acero", nombre="Producción de acero",
        bloque=3, subrama=3, nivel=7, padre_id="3.3.6_aleaciones",
        efectos=[
            EfectoTecnologia("prod_hierro_forjado", 0.20),
            EfectoTecnologia("herreria_avanzada", 1.0),
        ],
        descripcion="Descarbonización controlada para obtener el metal definitivo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 3.4: ORFEBRERÍA
# Progresión: Fundición oro → Aleaciones → Filigrana → Engaste → Acuñación → Esmaltes → Amonedación
# ==========================================
TECHS_3_4_ORFEBRERIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="3.4.1_fundicion_oro", nombre="Fundición de oro",
        bloque=3, subrama=4, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_oro_refinado", 0.10)],
        descripcion="Crisoles y hornos especializados para purificar oro.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.4.2_granulado", nombre="Granulado",
        bloque=3, subrama=4, nivel=2, padre_id="3.4.1_fundicion_oro",
        efectos=[EfectoTecnologia("calidad_producto", 0.05)],
        descripcion="Microesferas de oro soldadas para decoración minuciosa.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.4.3_aleaciones", nombre="Aleaciones preciosas",
        bloque=3, subrama=4, nivel=3, padre_id="3.4.2_granulado",
        efectos=[EfectoTecnologia("prod_oro_refinado", 0.15)],
        descripcion="Electrum y otras mezclas para dureza y color.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.4.4_engaste", nombre="Engaste de gemas",
        bloque=3, subrama=4, nivel=4, padre_id="3.4.3_aleaciones",
        efectos=[EfectoTecnologia("calidad_producto", 0.10)],
        descripcion="Montura segura de piedras preciosas en joyería.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.4.5_filigrana", nombre="Filigrana",
        bloque=3, subrama=4, nivel=5, padre_id="3.4.4_engaste",
        efectos=[EfectoTecnologia("prod_oro_refinado", 0.15)],
        descripcion="Hilos de oro entrelazados para piezas de extrema delicadeza.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.4.6_esmaltes", nombre="Esmaltado",
        bloque=3, subrama=4, nivel=6, padre_id="3.4.5_filigrana",
        efectos=[EfectoTecnologia("calidad_producto", 0.10)],
        descripcion="Vidrios fundidos sobre metal para color permanente.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.4.7_amonedacion", nombre="Amonedación sistemática",
        bloque=3, subrama=4, nivel=7, padre_id="3.4.6_esmaltes",
        efectos=[EfectoTecnologia("prod_oro_refinado", 0.20)],
        descripcion="Producción masiva de monedas con peso y ley garantizados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 3.5: MAQUINARIA (REORDENADA)
# Progresión: Rueda → Engranajes → Poleas → Molino viento → Prensa → Telar mecánico → Hidráulica
# ==========================================
TECHS_3_5_MAQUINARIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="3.5.1_rueda", nombre="Rueda industrial",
        bloque=3, subrama=5, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.05)],
        descripcion="Rueda reforzada para transporte de cargas pesadas en taller.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.5.2_engranajes", nombre="Engranajes",
        bloque=3, subrama=5, nivel=2, padre_id="3.5.1_rueda",
        efectos=[EfectoTecnologia("eficiencia_transformacion", 0.15)],
        descripcion="Transmisión de movimiento rotatorio entre ejes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.5.3_poleas", nombre="Sistemas de poleas",
        bloque=3, subrama=5, nivel=3, padre_id="3.5.2_engranajes",
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.10)],
        descripcion="Ventaja mecánica para elevar y mover materiales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.5.4_molino_viento", nombre="Molino de viento",
        bloque=3, subrama=5, nivel=4, padre_id="3.5.3_poleas",
        efectos=[EfectoTecnologia("eficiencia_transformacion", 0.15)],
        descripcion="Energía eólica convertida en fuerza motriz constante.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.5.5_prensa", nombre="Prensa mecánica",
        bloque=3, subrama=5, nivel=5, padre_id="3.5.4_molino_viento",
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.15)],
        descripcion="Compresión uniforme para aceites, vinos y metales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.5.6_telar_mecanico", nombre="Telar mecánico",
        bloque=3, subrama=5, nivel=6, padre_id="3.5.5_prensa",
        efectos=[EfectoTecnologia("eficiencia_transformacion", 0.15)],
        descripcion="Tejido automatizado que multiplica la producción textil.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.5.7_hidraulica", nombre="Maquinaria hidráulica",
        bloque=3, subrama=5, nivel=7, padre_id="3.5.6_telar_mecanico",
        efectos=[
            EfectoTecnologia("eficiencia_transformacion", 0.20),
            EfectoTecnologia("maquinaria_hidraulica", 1.0),
        ],
        descripcion="Fuerza del agua canalizada para mover máquinas complejas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 3.6: INVESTIGACIÓN INDUSTRIAL
# ==========================================
TECHS_3_6_INV_INDUSTRIAL: list[Tecnologia] = [
    Tecnologia.crear(
        id="3.6.1_aprendizaje", nombre="Sistema de aprendizaje",
        bloque=3, subrama=6, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("calidad_producto", 0.10)],
        descripcion="Transmisión estructurada de oficios de maestro a aprendiz.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.6.2_estandares_calidad", nombre="Estándares de calidad",
        bloque=3, subrama=6, nivel=2, padre_id="3.6.1_aprendizaje",
        efectos=[
            EfectoTecnologia("prod_madera_procesada", 0.10),
            EfectoTecnologia("calidad_producto", 0.15),
        ],
        descripcion="Medidas y pesos normalizados para productos consistentes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.6.3_geometria_aplicada", nombre="Geometría aplicada",
        bloque=3, subrama=6, nivel=3, padre_id="3.6.2_estandares_calidad",
        efectos=[EfectoTecnologia("prod_piedra_tallada", 0.10)],
        descripcion="Cálculo de proporciones y ángulos para construcción precisa.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.6.4_metalurgia_avanzada", nombre="Metalurgia avanzada",
        bloque=3, subrama=6, nivel=4, padre_id="3.6.3_geometria_aplicada",
        efectos=[
            EfectoTecnologia("prod_hierro_forjado", 0.15),
            EfectoTecnologia("prod_oro_refinado", 0.10),
        ],
        descripcion="Comprensión científica de propiedades metálicas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.6.5_division_trabajo", nombre="División del trabajo",
        bloque=3, subrama=6, nivel=5, padre_id="3.6.4_metalurgia_avanzada",
        efectos=[EfectoTecnologia("prod_madera_procesada", 0.10)],
        descripcion="Especialización por tareas para mayor productividad.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.6.6_maestros_artesanos", nombre="Maestros artesanos",
        bloque=3, subrama=6, nivel=6, padre_id="3.6.5_division_trabajo",
        efectos=[EfectoTecnologia("calidad_producto", 0.15)],
        descripcion="Reconocimiento formal de excelencia en el oficio.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.6.7_cartas_gremiales", nombre="Cartas gremiales",
        bloque=3, subrama=6, nivel=7, padre_id="3.6.6_maestros_artesanos",
        efectos=[EfectoTecnologia("gremios_artesanos", 0.5)],
        descripcion="Documentos legales que regulan y protegen los oficios.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 3.7: SEGURIDAD INDUSTRIAL
# ==========================================
TECHS_3_7_SEGURIDAD_IND: list[Tecnologia] = [
    Tecnologia.crear(
        id="3.7.1_ventilacion", nombre="Ventilación de talleres",
        bloque=3, subrama=7, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.05)],
        descripcion="Extracción de humos y polvo para proteger al trabajador.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.7.2_proteccion_personal", nombre="Protección personal",
        bloque=3, subrama=7, nivel=2, padre_id="3.7.1_ventilacion",
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.05)],
        descripcion="Guantes, delantales y gafas para trabajos peligrosos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.7.3_control_calidad", nombre="Control de calidad",
        bloque=3, subrama=7, nivel=3, padre_id="3.7.2_proteccion_personal",
        efectos=[
            EfectoTecnologia("reduccion_desperdicio", 0.15),
            EfectoTecnologia("calidad_producto", 0.10),
        ],
        descripcion="Inspección sistemática que detecta defectos antes del envío.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.7.4_prevencion_incendios", nombre="Prevención de incendios",
        bloque=3, subrama=7, nivel=4, padre_id="3.7.3_control_calidad",
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.10)],
        descripcion="Normas de almacenamiento seguro de combustibles.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.7.5_reciclaje_industrial", nombre="Reciclaje industrial",
        bloque=3, subrama=7, nivel=5, padre_id="3.7.4_prevencion_incendios",
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.20)],
        descripcion="Reaprovechamiento de recortes y virutas como materia prima.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.7.6_normativa_residuos", nombre="Normativa de residuos",
        bloque=3, subrama=7, nivel=6, padre_id="3.7.5_reciclaje_industrial",
        efectos=[EfectoTecnologia("reduccion_desperdicio", 0.15)],
        descripcion="Gestión regulada de desechos tóxicos y vertidos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="3.7.7_legislacion_gremial", nombre="Legislación gremial",
        bloque=3, subrama=7, nivel=7, padre_id="3.7.6_normativa_residuos",
        efectos=[EfectoTecnologia("gremios_artesanos", 0.5)],
        descripcion="Marco legal que regula relaciones laborales y estándares.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# EXPORTACIÓN UNIFICADA DEL BLOQUE 3
# ==========================================
TECNOLOGIAS_BLOQUE_3: list[Tecnologia] = (
    TECHS_3_1_CARPINTERIA
    + TECHS_3_2_CANTERIA
    + TECHS_3_3_HERRERIA
    + TECHS_3_4_ORFEBRERIA
    + TECHS_3_5_MAQUINARIA
    + TECHS_3_6_INV_INDUSTRIAL
    + TECHS_3_7_SEGURIDAD_IND
)
