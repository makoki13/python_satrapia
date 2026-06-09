# src/investigacion/datos/bloque_1_alimentacion.py
"""
Datos de tecnologías del Bloque 1: Alimentación.
49 tecnologías (7 subramas × 7 niveles).

Nota: Los niveles han sido reordenados respecto al PDF original
para garantizar una progresión histórica y causal lógica.
Los IDs de efectos coinciden con REGISTRO_PARAMETROS.
"""
from src.investigacion.tecnologia import EfectoTecnologia, Tecnologia

# ==========================================
# CONSTANTES DE COSTE BASE
# ==========================================
COSTE_ORO_BASE = 100
TURNOS_BASE = 3

# ==========================================
# SUBRAMA 1.1: SIEMBRA
# Progresión: Inundación → Semillas → Ciclos → Canales → Recolección → Herramientas → Rotación
# ==========================================
TECHS_1_1_SIEMBRA: list[Tecnologia] = [
    Tecnologia.crear(
        id="1.1.1_regadio_inundacion",
        nombre="Regadío por inundación",
        bloque=1, subrama=1, nivel=1, padre_id=None,
        efectos=[
            EfectoTecnologia("prod_comida_granja", 0.10),
            EfectoTecnologia("velocidad_cosecha", 0.05),
        ],
        descripcion="Inundación controlada de campos para humedecer la tierra antes de la siembra.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.1.2_seleccion_semillas",
        nombre="Selección de semillas",
        bloque=1, subrama=1, nivel=2, padre_id="1.1.1_regadio_inundacion",
        efectos=[
            EfectoTecnologia("prod_comida_granja", 0.10),
        ],
        descripcion="Escoger las semillas más resistentes y productivas de cada cosecha.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.1.3_ciclos",
        nombre="Ciclos agrícolas",
        bloque=1, subrama=1, nivel=3, padre_id="1.1.2_seleccion_semillas",
        efectos=[
            EfectoTecnologia("prod_comida_granja", 0.05),
        ],
        descripcion="Comprensión de las estaciones y momentos óptimos para sembrar y recoger.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.1.4_regadio_canales",
        nombre="Regadío por canales",
        bloque=1, subrama=1, nivel=4, padre_id="1.1.3_ciclos",
        efectos=[
            EfectoTecnologia("prod_comida_granja", 0.15),
            EfectoTecnologia("velocidad_cosecha", 0.10),
        ],
        descripcion="Red de canales artificiales que permiten riego constante y predecible.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.1.5_recoleccion",
        nombre="Recolección organizada",
        bloque=1, subrama=1, nivel=5, padre_id="1.1.4_regadio_canales",
        efectos=[
            EfectoTecnologia("prod_comida_granja", 0.05),
            EfectoTecnologia("velocidad_cosecha", 0.10),
        ],
        descripcion="Coordinación de trabajadores para cosechar en el momento justo sin pérdidas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.1.6_herramientas_cosecha",
        nombre="Herramientas de cosecha",
        bloque=1, subrama=1, nivel=6, padre_id="1.1.5_recoleccion",
        efectos=[
            EfectoTecnologia("prod_comida_granja", 0.10),
            EfectoTecnologia("velocidad_cosecha", 0.20),
        ],
        descripcion="Hoces, guadañas y rastrillos metálicos que multiplican la eficiencia.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.1.7_rotacion_cultivos",
        nombre="Rotación de cultivos",
        bloque=1, subrama=1, nivel=7, padre_id="1.1.6_herramientas_cosecha",
        efectos=[
            EfectoTecnologia("prod_comida_granja", 0.15),
            EfectoTecnologia("velocidad_cosecha", 0.20),
        ],
        descripcion="Alternar cultivos en un mismo campo para mantener la fertilidad del suelo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 1.2: PESCA
# Progresión: Aparejos → Costa → Conservación → Naves → Aguas profundas → Bancos → Balleneros
# ==========================================
TECHS_1_2_PESCA: list[Tecnologia] = [
    Tecnologia.crear(
        id="1.2.1_aparejos",
        nombre="Aparejos de pesca",
        bloque=1, subrama=2, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_comida_pesca", 0.10)],
        descripcion="Redes, anzuelos y nasas básicas para capturar peces costeros.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.2.2_navegacion_costa",
        nombre="Navegación de costa",
        bloque=1, subrama=2, nivel=2, padre_id="1.2.1_aparejos",
        efectos=[EfectoTecnologia("prod_comida_pesca", 0.10)],
        descripcion="Embarcaciones pequeñas que siguen la línea de costa sin perder tierra de vista.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.2.3_conservacion_pescado",
        nombre="Conservación de pescado",
        bloque=1, subrama=2, nivel=3, padre_id="1.2.2_navegacion_costa",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.05)],
        descripcion="Salado y secado de pescado para almacenarlo durante meses.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.2.4_naves",
        nombre="Naves pesqueras",
        bloque=1, subrama=2, nivel=4, padre_id="1.2.3_conservacion_pescado",
        efectos=[EfectoTecnologia("prod_comida_pesca", 0.15)],
        descripcion="Barcos mayores con bodega propia para faenas más largas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.2.5_navegacion_aguas_profundas",
        nombre="Navegación en aguas profundas",
        bloque=1, subrama=2, nivel=5, padre_id="1.2.4_naves",
        efectos=[
            EfectoTecnologia("prod_comida_pesca", 0.20),
            EfectoTecnologia("pesca_aguas_profundas", 1.0),  # Desbloqueo lógico
        ],
        descripcion="Capacidad de navegar mar adentro usando estrellas y corrientes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.2.6_seguimiento_bancos",
        nombre="Seguimiento de bancos",
        bloque=1, subrama=2, nivel=6, padre_id="1.2.5_navegacion_aguas_profundas",
        efectos=[EfectoTecnologia("prod_comida_pesca", 0.15)],
        descripcion="Conocimiento de migraciones estacionales y señales naturales de cardúmenes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.2.7_balleneros",
        nombre="Balleneros",
        bloque=1, subrama=2, nivel=7, padre_id="1.2.6_seguimiento_bancos",
        efectos=[EfectoTecnologia("prod_comida_pesca", 0.20)],
        descripcion="Caza organizada de grandes cetáceos para carne, grasa y hueso.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 1.3: PLAGAS
# Progresión: Medicinas → Trampas → Entomología → Redes → Injertos → Raticidas → Prevención
# ==========================================
TECHS_1_3_PLAGAS: list[Tecnologia] = [
    Tecnologia.crear(
        id="1.3.1_medicinas",
        nombre="Medicinas vegetales",
        bloque=1, subrama=3, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.10)],
        descripcion="Uso de extractos de plantas para tratar cultivos enfermos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.3.2_trampas",
        nombre="Trampas para plagas",
        bloque=1, subrama=3, nivel=2, padre_id="1.3.1_medicinas",
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.10)],
        descripcion="Trampas físicas y cebos para reducir poblaciones de insectos dañinos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.3.3_entomologia",
        nombre="Entomología básica",
        bloque=1, subrama=3, nivel=3, padre_id="1.3.2_trampas",
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.15)],
        descripcion="Estudio de ciclos vitales de insectos para atacar en fases vulnerables.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.3.4_redes",
        nombre="Redes protectoras",
        bloque=1, subrama=3, nivel=4, padre_id="1.3.3_entomologia",
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.10)],
        descripcion="Mallas y coberturas que impiden físicamente el acceso de plagas voladoras.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.3.5_injertos",
        nombre="Injertos resistentes",
        bloque=1, subrama=3, nivel=5, padre_id="1.3.4_redes",
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.15)],
        descripcion="Unir variedades productivas con patrones resistentes a enfermedades.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.3.6_raticidas",
        nombre="Raticidas y venenos",
        bloque=1, subrama=3, nivel=6, padre_id="1.3.5_injertos",
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.15)],
        descripcion="Sustancias tóxicas específicas para controlar roedores en graneros y campos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.3.7_prevencion",
        nombre="Prevención integrada",
        bloque=1, subrama=3, nivel=7, padre_id="1.3.6_raticidas",
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.25)],
        descripcion="Sistema holístico que combina todas las técnicas para minimizar pérdidas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 1.4: GANADERÍA
# Progresión: Ovino → Bovino → Porcino → Caballería → Aves → Conejos → Aparejos
# ==========================================
TECHS_1_4_GANADERIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="1.4.1_ovino",
        nombre="Cría ovina",
        bloque=1, subrama=4, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_comida_ganaderia", 0.10)],
        descripcion="Domesticación de ovejas para lana, leche y carne.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.4.2_bovino",
        nombre="Cría bovina",
        bloque=1, subrama=4, nivel=2, padre_id="1.4.1_ovino",
        efectos=[EfectoTecnologia("prod_comida_ganaderia", 0.15)],
        descripcion="Bueyes y vacas como fuente de carne, leche y fuerza de tiro.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.4.3_porcino",
        nombre="Cría porcina",
        bloque=1, subrama=4, nivel=3, padre_id="1.4.2_bovino",
        efectos=[EfectoTecnologia("prod_comida_ganaderia", 0.10)],
        descripcion="Cerdos como fuente eficiente de proteína cárnica.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.4.4_caballeria",
        nombre="Cría caballar",
        bloque=1, subrama=4, nivel=4, padre_id="1.4.3_porcino",
        efectos=[
            EfectoTecnologia("ganaderia_caballar", 1.0),  # Desbloqueo lógico
        ],
        descripcion="Caballada para transporte rápido, guerra y mensajería.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.4.5_aves",
        nombre="Avicultura",
        bloque=1, subrama=4, nivel=5, padre_id="1.4.4_caballeria",
        efectos=[EfectoTecnologia("prod_comida_ganaderia", 0.10)],
        descripcion="Gallinas, patos y gansos para huevos y carne de ciclo corto.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.4.6_conejos",
        nombre="Cunicultura",
        bloque=1, subrama=4, nivel=6, padre_id="1.4.5_aves",
        efectos=[EfectoTecnologia("prod_comida_ganaderia", 0.10)],
        descripcion="Cría de conejos en espacios reducidos para complemento proteico.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.4.7_aparejos_ganaderos",
        nombre="Aparejos ganaderos",
        bloque=1, subrama=4, nivel=7, padre_id="1.4.6_conejos",
        efectos=[EfectoTecnologia("prod_comida_ganaderia", 0.15)],
        descripcion="Yugos, arneses y herrajes que optimizan el uso del ganado.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 1.5: ALMACENAMIENTO
# Progresión: Salazones → Salmuera → Curtidos → Neveros → Confitado → Esterilización → Conservación avanzada
# ==========================================
TECHS_1_5_ALMACENAMIENTO: list[Tecnologia] = [
    Tecnologia.crear(
        id="1.5.1_salazones",
        nombre="Salazones",
        bloque=1, subrama=5, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.10)],
        descripcion="Uso masivo de sal para preservar carnes y pescados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.5.2_salmuera",
        nombre="Salmuera",
        bloque=1, subrama=5, nivel=2, padre_id="1.5.1_salazones",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.10)],
        descripcion="Sumergir alimentos en soluciones concentradas de salmuera.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.5.3_curtidos",
        nombre="Curtidos alimentarios",
        bloque=1, subrama=5, nivel=3, padre_id="1.5.2_salmuera",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.05)],
        descripcion="Tratamiento de pieles para recipientes herméticos de almacenamiento.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.5.4_neveros",
        nombre="Neveros",
        bloque=1, subrama=5, nivel=4, padre_id="1.5.3_curtidos",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.15)],
        descripcion="Pozos aislados con nieve/hielo compactado para conservación fría.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.5.5_confitado_aceite",
        nombre="Confitado en aceite",
        bloque=1, subrama=5, nivel=5, padre_id="1.5.4_neveros",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.10)],
        descripcion="Sumergir alimentos cocinados en aceite/grasa para aislarlos del aire.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.5.6_esterilizacion",
        nombre="Esterilización térmica",
        bloque=1, subrama=5, nivel=6, padre_id="1.5.5_confitado_aceite",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.15)],
        descripcion="Calentar recipientes sellados para eliminar microorganismos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.5.7_conservacion_avanzada",
        nombre="Conservación avanzada",
        bloque=1, subrama=5, nivel=7, padre_id="1.5.6_esterilizacion",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.20)],
        descripcion="Combinación sistemática de todas las técnicas de preservación.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 1.6: AGRICULTURA (Diversificación)
# Progresión: Forraje → Frutas → Legumbres → Hongos → Cereales → Floricultura → Tubérculos
# ==========================================
TECHS_1_6_AGRICULTURA: list[Tecnologia] = [
    Tecnologia.crear(
        id="1.6.1_forraje",
        nombre="Cultivo de forraje",
        bloque=1, subrama=6, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prod_comida_ganaderia", 0.05)],
        descripcion="Plantas dedicadas exclusivamente a alimentar ganado.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.6.2_frutas",
        nombre="Fruticultura",
        bloque=1, subrama=6, nivel=2, padre_id="1.6.1_forraje",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.05)],
        descripcion="Huertos organizados de árboles frutales perennes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.6.3_legumbres",
        nombre="Leguminosas",
        bloque=1, subrama=6, nivel=3, padre_id="1.6.2_frutas",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.05)],
        descripcion="Lentejas, garbanzos y habas que fijan nitrógeno en el suelo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.6.4_hongos",
        nombre="Micocultura",
        bloque=1, subrama=6, nivel=4, padre_id="1.6.3_legumbres",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.05)],
        descripcion="Cultivo controlado de setas comestibles en ambientes húmedos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.6.5_cereales",
        nombre="Cerealicultura avanzada",
        bloque=1, subrama=6, nivel=5, padre_id="1.6.4_hongos",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.10)],
        descripcion="Variedades mejoradas de trigo, cebada y centeno de alto rendimiento.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.6.6_floricultura",
        nombre="Floricultura",
        bloque=1, subrama=6, nivel=6, padre_id="1.6.5_cereales",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.05)],
        descripcion="Cultivo de flores para miel, especias y comercio de lujo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.6.7_tuberculos",
        nombre="Tubérculos",
        bloque=1, subrama=6, nivel=7, padre_id="1.6.6_floricultura",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.10)],
        descripcion="Patatas, nabos y remolachas como reserva calórica resistente.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 1.7: COCINA
# Progresión: Hervido → Freidoras → Hornos → Cerámica → Ahumados → Estofados → Recetas
# ==========================================
TECHS_1_7_COCINA: list[Tecnologia] = [
    Tecnologia.crear(
        id="1.7.1_hervido",
        nombre="Hervido",
        bloque=1, subrama=7, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_perdida_plagas", 0.05)],
        descripcion="Cocción en agua que elimina patógenos y ablanda alimentos duros.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.7.2_freidoras",
        nombre="Fritura",
        bloque=1, subrama=7, nivel=2, padre_id="1.7.1_hervido",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.05)],
        descripcion="Cocción rápida en grasas calientes que también conserva.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.7.3_hornos",
        nombre="Hornos de pan",
        bloque=1, subrama=7, nivel=3, padre_id="1.7.2_freidoras",
        efectos=[
            EfectoTecnologia("cocina_hornos", 1.0),  # Desbloqueo lógico
            EfectoTecnologia("prod_comida_granja", 0.05),
        ],
        descripcion="Estructuras cerradas de cocción indirecta para pan y asados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.7.4_ceramica",
        nombre="Cerámica culinaria",
        bloque=1, subrama=7, nivel=4, padre_id="1.7.3_hornos",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.05)],
        descripcion="Ollas, cazuelas y ánforas que resisten fuego directo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.7.5_ahumados",
        nombre="Ahumados",
        bloque=1, subrama=7, nivel=5, padre_id="1.7.4_ceramica",
        efectos=[EfectoTecnologia("capacidad_silo_comida", 0.05)],
        descripcion="Exposición al humo que aporta sabor y propiedades conservantes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.7.6_estofados",
        nombre="Estofados y guisos",
        bloque=1, subrama=7, nivel=6, padre_id="1.7.5_ahumados",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.05)],
        descripcion="Cocción lenta combinada que aprovecha cortes menos nobles.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="1.7.7_recetas",
        nombre="Recetario sistematizado",
        bloque=1, subrama=7, nivel=7, padre_id="1.7.6_estofados",
        efectos=[EfectoTecnologia("prod_comida_granja", 0.10)],
        descripcion="Registro escrito de preparaciones que estandariza la calidad nutricional.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# EXPORTACIÓN UNIFICADA DEL BLOQUE 1
# ==========================================
TECNOLOGIAS_BLOQUE_1: list[Tecnologia] = (
    TECHS_1_1_SIEMBRA
    + TECHS_1_2_PESCA
    + TECHS_1_3_PLAGAS
    + TECHS_1_4_GANADERIA
    + TECHS_1_5_ALMACENAMIENTO
    + TECHS_1_6_AGRICULTURA
    + TECHS_1_7_COCINA
)
