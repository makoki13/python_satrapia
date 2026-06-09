# src/investigacion/datos/bloque_4_ejercito.py
"""
Datos de tecnologías del Bloque 4: Ejército.
49 tecnologías (7 subramas × 7 niveles).

CORRECCIONES CRÍTICAS RESPECTO AL PDF ORIGINAL:
- 4.2 Caballería: "Carro de guerra" movido a Nv3 (posterior a jinetes ligeros).
- 4.3 Asedio: "Torre de asedio" reordenada a Nv3 (tras Ariete, antes de Catapulta).
- 4.6 Tácticas: "Formaciones" subida a Nv1. "Emboscada" movida a Nv3 tras Flanqueo.
- 4.7 Ingeniería Militar: Renombrada desde "Fortificaciones". Progresión defensiva lógica.
- IDs DUPLICADOS ELIMINADOS: El PDF tenía 4.6.1 repetido 3 veces. Se asignaron IDs únicos.

Los IDs de efectos coinciden EXACTAMENTE con REGISTRO_PARAMETROS.
"""
from src.investigacion.tecnologia import EfectoTecnologia, Tecnologia

COSTE_ORO_BASE = 100
TURNOS_BASE = 3

# ==========================================
# SUBRAMA 4.1: INFANTERÍA
# Progresión: Lanceros → Armas → Escudos → Armadura → Hoplitas → Pica → Legión
# ==========================================
TECHS_4_1_INFANTERIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="4.1.1_lanceros", nombre="Lanceros",
        bloque=4, subrama=1, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("fuerza_infanteria", 0.10)],
        descripcion="Unidades básicas armadas con lanzas largas para formación cerrada.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.1.2_armas_hierro", nombre="Armas de hierro",
        bloque=4, subrama=1, nivel=2, padre_id="4.1.1_lanceros",
        efectos=[EfectoTecnologia("fuerza_infanteria", 0.05)],
        descripcion="Espadas y hachas de hierro que superan al bronce.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.1.3_escudos", nombre="Escudos reforzados",
        bloque=4, subrama=1, nivel=3, padre_id="4.1.2_armas_hierro",
        efectos=[EfectoTecnologia("fuerza_infanteria", 0.10)],
        descripcion="Protección corporal que permite mantener la línea de batalla.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.1.4_armadura", nombre="Armadura corporal",
        bloque=4, subrama=1, nivel=4, padre_id="4.1.3_escudos",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.05)],
        descripcion="Cotas de malla y placas que reducen bajas por proyectiles.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.1.5_hoplitas", nombre="Hoplitas",
        bloque=4, subrama=1, nivel=5, padre_id="4.1.4_armadura",
        efectos=[EfectoTecnologia("fuerza_infanteria", 0.15)],
        descripcion="Infantería pesada con equipo completo y disciplina de falange.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.1.6_pica", nombre="Pica larga",
        bloque=4, subrama=1, nivel=6, padre_id="4.1.5_hoplitas",
        efectos=[EfectoTecnologia("fuerza_infanteria", 0.10)],
        descripcion="Lanzas de 4-6 metros que detienen cargas de caballería.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.1.7_legion", nombre="Legión organizada",
        bloque=4, subrama=1, nivel=7, padre_id="4.1.6_pica",
        efectos=[EfectoTecnologia("fuerza_infanteria", 0.20)],
        descripcion="Unidad táctica autónoma con mando profesional y rotación de líneas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 4.2: CABALLERÍA (REORDENADA)
# Progresión: Jinetes ligeros → Montura → Carro guerra → Catafractos → Estribo → Caballería pesada
# NOTA: Carro de guerra movido a Nv3 (es posterior a jinetes básicos)
# ==========================================
TECHS_4_2_CABALLERIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="4.2.1_jinetes_ligeros", nombre="Jinetes ligeros",
        bloque=4, subrama=2, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("fuerza_caballeria", 0.10)],
        descripcion="Exploradores y hostigadores montados para reconocimiento.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.2.2_montura_mejorada", nombre="Montura mejorada",
        bloque=4, subrama=2, nivel=2, padre_id="4.2.1_jinetes_ligeros",
        efectos=[EfectoTecnologia("velocidad_marcha", 0.05)],
        descripcion="Sillas y riendas que permiten mayor control y resistencia.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Era 4.2.1 en PDF, ahora Nv3 por complejidad tecnológica
    Tecnologia.crear(
        id="4.2.3_carro_guerra", nombre="Carro de guerra",
        bloque=4, subrama=2, nivel=3, padre_id="4.2.2_montura_mejorada",
        efectos=[EfectoTecnologia("fuerza_caballeria", 0.10)],
        descripcion="Plataforma móvil de combate para arqueros y lanceros.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.2.4_carga_coordinada", nombre="Carga coordinada",
        bloque=4, subrama=2, nivel=4, padre_id="4.2.3_carro_guerra",
        efectos=[EfectoTecnologia("fuerza_caballeria", 0.10)],
        descripcion="Maniobras de choque en formación para romper líneas enemigas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.2.5_catafractos", nombre="Catafractos",
        bloque=4, subrama=2, nivel=5, padre_id="4.2.4_carga_coordinada",
        efectos=[EfectoTecnologia("fuerza_caballeria", 0.15)],
        descripcion="Caballería completamente blindada (jinete y caballo).",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.2.6_estribo", nombre="Estribo metálico",
        bloque=4, subrama=2, nivel=6, padre_id="4.2.5_catafractos",
        efectos=[EfectoTecnologia("fuerza_caballeria", 0.10)],
        descripcion="Soporte para el jinete que permite golpes más potentes sin caer.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.2.7_caballeria_pesada", nombre="Caballería pesada",
        bloque=4, subrama=2, nivel=7, padre_id="4.2.6_estribo",
        efectos=[
            EfectoTecnologia("fuerza_caballeria", 0.20),
            EfectoTecnologia("caballeria_pesada", 1.0),
        ],
        descripcion="Fuerza de choque definitiva con armadura completa y lanza de justa.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 4.3: ASEDIO (REORDENADA)
# Progresión: Escalas → Ariete → Torre → Catapulta → Fuego griego → Trebuchet → Trabuquete
# NOTA: Torre movida a Nv3 (más compleja que ariete, menos que catapulta)
# ==========================================
TECHS_4_3_ASEDIO: list[Tecnologia] = [
    Tecnologia.crear(
        id="4.3.1_escalas", nombre="Escalas de asalto",
        bloque=4, subrama=3, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("fuerza_asedio", 0.05)],
        descripcion="Asalto directo a murallas mediante escaleras portátiles.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.3.2_ariete", nombre="Ariete",
        bloque=4, subrama=3, nivel=2, padre_id="4.3.1_escalas",
        efectos=[EfectoTecnologia("fuerza_asedio", 0.10)],
        descripcion="Viga reforzada para derribar puertas y portones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Era 4.3.3 en PDF pero con posición incorrecta relativa a catapulta
    Tecnologia.crear(
        id="4.3.3_torre_asedio", nombre="Torre de asedio",
        bloque=4, subrama=3, nivel=3, padre_id="4.3.2_ariete",
        efectos=[EfectoTecnologia("fuerza_asedio", 0.10)],
        descripcion="Estructura móvil que permite asaltar murallas a nivel superior.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.3.4_minado", nombre="Minado de murallas",
        bloque=4, subrama=3, nivel=4, padre_id="4.3.3_torre_asedio",
        efectos=[EfectoTecnologia("fuerza_asedio", 0.10)],
        descripcion="Túneles bajo cimientos para provocar colapsos estructurales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.3.5_catapulta", nombre="Catapulta de torsión",
        bloque=4, subrama=3, nivel=5, padre_id="4.3.4_minado",
        efectos=[EfectoTecnologia("fuerza_asedio", 0.15)],
        descripcion="Artillería que lanza proyectiles pesados contra fortificaciones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.3.6_fuego_griego", nombre="Fuego griego",
        bloque=4, subrama=3, nivel=6, padre_id="4.3.5_catapulta",
        efectos=[EfectoTecnologia("fuerza_asedio", 0.10)],
        descripcion="Mezcla incendiaria imparable que arde incluso sobre agua.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.3.7_trabuquete", nombre="Trabuquete de contrapeso",
        bloque=4, subrama=3, nivel=7, padre_id="4.3.6_fuego_griego",
        efectos=[
            EfectoTecnologia("fuerza_asedio", 0.20),
            EfectoTecnologia("maquinas_asedio_avanzadas", 1.0),
        ],
        descripcion="Máquina de asedio definitiva capaz de destruir cualquier muralla.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 4.4: LOGÍSTICA MILITAR
# ==========================================
TECHS_4_4_LOGISTICA_MIL: list[Tecnologia] = [
    Tecnologia.crear(
        id="4.4.1_suministros", nombre="Cadena de suministros",
        bloque=4, subrama=4, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("moral_tropa", 0.10)],
        descripcion="Organización básica de provisiones para campañas cortas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.4.2_caminos_militares", nombre="Caminos militares",
        bloque=4, subrama=4, nivel=2, padre_id="4.4.1_suministros",
        efectos=[EfectoTecnologia("velocidad_marcha", 0.15)],
        descripcion="Vías pavimentadas para movimiento rápido de legiones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.4.3_campamentos", nombre="Campamentos fortificados",
        bloque=4, subrama=4, nivel=3, padre_id="4.4.2_caminos_militares",
        efectos=[EfectoTecnologia("moral_tropa", 0.10)],
        descripcion="Bases temporales seguras con empalizadas y fosos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.4.4_logistica_caravanas", nombre="Logística de caravanas",
        bloque=4, subrama=4, nivel=4, padre_id="4.4.3_campamentos",
        efectos=[EfectoTecnologia("velocidad_marcha", 0.15)],
        descripcion="Carros de intendencia organizados para campañas largas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.4.5_hospitales", nombre="Hospitales de campaña",
        bloque=4, subrama=4, nivel=5, padre_id="4.4.4_logistica_caravanas",
        efectos=[EfectoTecnologia("moral_tropa", 0.15)],
        descripcion="Atención médica que recupera heridos y mantiene la moral.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.4.6_cuartel_general", nombre="Cuartel General",
        bloque=4, subrama=4, nivel=6, padre_id="4.4.5_hospitales",
        efectos=[EfectoTecnologia("capacidad_reclutamiento", 0.20)],
        descripcion="Centro de mando permanente para coordinación estratégica.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.4.7_academia_militar", nombre="Academia Militar",
        bloque=4, subrama=4, nivel=7, padre_id="4.4.6_cuartel_general",
        efectos=[EfectoTecnologia("capacidad_reclutamiento", 0.20)],
        descripcion="Formación profesional de oficiales y tropas de élite.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 4.5: EXPLORACIÓN Y RECONOCIMIENTO
# ==========================================
TECHS_4_5_EXPLORACION: list[Tecnologia] = [
    Tecnologia.crear(
        id="4.5.1_exploradores", nombre="Exploradores",
        bloque=4, subrama=5, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("velocidad_marcha", 0.10)],
        descripcion="Unidades ligeras para reconocimiento del terreno enemigo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.5.2_vanguardia", nombre="Vanguardia organizada",
        bloque=4, subrama=5, nivel=2, padre_id="4.5.1_exploradores",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.10)],
        descripcion="Avanzadilla que detecta emboscadas antes del grueso del ejército.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.5.3_cartografia_militar", nombre="Cartografía militar",
        bloque=4, subrama=5, nivel=3, padre_id="4.5.2_vanguardia",
        efectos=[EfectoTecnologia("velocidad_marcha", 0.10)],
        descripcion="Mapas detallados de rutas, vados y posiciones defensivas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.5.4_emboscada_defensiva", nombre="Contraemboscada",
        bloque=4, subrama=5, nivel=4, padre_id="4.5.3_cartografia_militar",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.15)],
        descripcion="Técnicas para detectar y neutralizar trampas enemigas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.5.5_telegrafo_optico", nombre="Telégrafo óptico",
        bloque=4, subrama=5, nivel=5, padre_id="4.5.4_emboscada_defensiva",
        efectos=[EfectoTecnologia("velocidad_marcha", 0.15)],
        descripcion="Comunicación visual rápida entre puestos de vigilancia.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.5.6_red_inteligencia", nombre="Red de inteligencia",
        bloque=4, subrama=5, nivel=6, padre_id="4.5.5_telegrafo_optico",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.10)],
        descripcion="Informantes infiltrados que revelan movimientos enemigos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.5.7_conocimiento_terreno", nombre="Dominio del terreno",
        bloque=4, subrama=5, nivel=7, padre_id="4.5.6_red_inteligencia",
        efectos=[EfectoTecnologia("velocidad_marcha", 0.15)],
        descripcion="Explotación sistemática de ventajas geográficas en campaña.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 4.6: TÁCTICAS (REORDENADA + IDs CORREGIDOS)
# Progresión: Formaciones → Flanqueo → Retirada ordenada → Disciplina → Terreno → Oficiales → Código
# NOTA: PDF tenía 4.6.1 repetido 3 veces. IDs ahora son únicos y secuenciales.
# ==========================================
TECHS_4_6_TACTICAS: list[Tecnologia] = [
    # REORDENADO: Subido a Nv1 como base táctica fundamental
    Tecnologia.crear(
        id="4.6.1_formaciones", nombre="Formaciones de combate",
        bloque=4, subrama=6, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("fuerza_infanteria", 0.10)],
        descripcion="Disposiciones ordenadas que multiplican la efectividad colectiva.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.6.2_flanqueo", nombre="Maniobra de flanqueo",
        bloque=4, subrama=6, nivel=2, padre_id="4.6.1_formaciones",
        efectos=[EfectoTecnologia("fuerza_caballeria", 0.10)],
        descripcion="Ataque lateral que rompe la cohesión de la línea enemiga.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Movido a Nv3 (requiere disciplina previa para ejecutarse sin desbandada)
    Tecnologia.crear(
        id="4.6.3_retirada_ordenada", nombre="Retirada ordenada",
        bloque=4, subrama=6, nivel=3, padre_id="4.6.2_flanqueo",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.15)],
        descripcion="Repliegue disciplinado que evita la aniquilación tras derrota.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.6.4_disciplina", nombre="Disciplina férrea",
        bloque=4, subrama=6, nivel=4, padre_id="4.6.3_retirada_ordenada",
        efectos=[
            EfectoTecnologia("fuerza_infanteria", 0.10),
            EfectoTecnologia("moral_tropa", 0.15),
        ],
        descripcion="Obediencia absoluta que mantiene la formación bajo presión extrema.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.6.5_terreno_favorable", nombre="Elección de terreno",
        bloque=4, subrama=6, nivel=5, padre_id="4.6.4_disciplina",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.15)],
        descripcion="Forzar batalla en posiciones que favorecen a tus unidades.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.6.6_oficiales", nombre="Cuerpo de oficiales",
        bloque=4, subrama=6, nivel=6, padre_id="4.6.5_terreno_favorable",
        efectos=[EfectoTecnologia("moral_tropa", 0.15)],
        descripcion="Mando intermedio profesional que coordina unidades independientes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.6.7_codigo_guerra", nombre="Código de guerra",
        bloque=4, subrama=6, nivel=7, padre_id="4.6.6_oficiales",
        efectos=[EfectoTecnologia("doctrina_militar", 0.5)],
        descripcion="Doctrina escrita unificada para todo el ejército del reino.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 4.7: INGENIERÍA MILITAR (RENOMBRADA)
# Antes: "Fortificaciones". Ahora incluye defensa + infraestructura militar.
# Progresión: Murallas → Foso → Barbacana → Castillo concéntrico → Baluarte → Ciudadela → Fortaleza estrellada
# ==========================================
TECHS_4_7_INGENIERIA_MIL: list[Tecnologia] = [
    Tecnologia.crear(
        id="4.7.1_murallas", nombre="Murallas de piedra",
        bloque=4, subrama=7, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("fuerza_asedio", 0.05)],  # Conocer murallas ayuda a asediarlas
        descripcion="Defensa básica permanente contra incursiones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.7.2_foso", nombre="Foso y empalizada",
        bloque=4, subrama=7, nivel=2, padre_id="4.7.1_murallas",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.05)],
        descripcion="Obstáculo perimetral que frena asaltos directos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.7.3_barbacana", nombre="Barbacana",
        bloque=4, subrama=7, nivel=3, padre_id="4.7.2_foso",
        efectos=[EfectoTecnologia("capacidad_reclutamiento", 0.10)],
        descripcion="Puerta fortificada avanzada que protege el acceso principal.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.7.4_castillo_concentrico", nombre="Castillo concéntrico",
        bloque=4, subrama=7, nivel=4, padre_id="4.7.3_barbacana",
        efectos=[EfectoTecnologia("reduccion_bajas", 0.15)],
        descripcion="Múltiples anillos defensivos que obligan a asaltos sucesivos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.7.5_baluarte", nombre="Baluarte artillero",
        bloque=4, subrama=7, nivel=5, padre_id="4.7.4_castillo_concentrico",
        efectos=[EfectoTecnologia("fuerza_asedio", 0.10)],
        descripcion="Torreón diseñado para albergar artillería defensiva.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.7.6_ciudadela", nombre="Ciudadela interior",
        bloque=4, subrama=7, nivel=6, padre_id="4.7.5_baluarte",
        efectos=[EfectoTecnologia("capacidad_reclutamiento", 0.15)],
        descripcion="Último reducto fortificado dentro de la ciudad para resistir cercos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="4.7.7_fortaleza_estrellada", nombre="Fortaleza estrellada",
        bloque=4, subrama=7, nivel=7, padre_id="4.7.6_ciudadela",
        efectos=[EfectoTecnologia("doctrina_militar", 0.5)],
        descripcion="Diseño geométrico que elimina ángulos muertos ante artillería.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# EXPORTACIÓN UNIFICADA DEL BLOQUE 4
# ==========================================
TECNOLOGIAS_BLOQUE_4: list[Tecnologia] = (
    TECHS_4_1_INFANTERIA
    + TECHS_4_2_CABALLERIA
    + TECHS_4_3_ASEDIO
    + TECHS_4_4_LOGISTICA_MIL
    + TECHS_4_5_EXPLORACION
    + TECHS_4_6_TACTICAS
    + TECHS_4_7_INGENIERIA_MIL
)
