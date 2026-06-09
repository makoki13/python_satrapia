# src/investigacion/datos/bloque_6_cultura.py
"""
Datos de tecnologías del Bloque 6: Cultura y Educación.
49 tecnologías (7 subramas × 7 niveles).

CORRECCIONES CRÍTICAS RESPECTO AL PDF ORIGINAL:
- 6.1 Educación: Progresión institucional Escribas→Alfabetización→Biblioteca→Academia→Liceo→Observatorio→Universidad.
- 6.2 Artes: Separada claramente de artesanía industrial (B3). Progresión Cerámica→Textil→Pintura→Escultura→Música→Teatro→Mecenazgo.
- 6.7 Filosofía: Reordenada cronológicamente. Humanismo movido a Nv6 (tras Ciencia Natural), Ilustración como culminación Nv7.
- IDs DUPLICADOS ELIMINADOS: Se asignaron IDs únicos secuenciales en todas las subramas.

Los IDs de efectos coinciden EXACTAMENTE con REGISTRO_PARAMETROS.
"""
from src.investigacion.tecnologia import EfectoTecnologia, Tecnologia

COSTE_ORO_BASE = 100
TURNOS_BASE = 3

# ==========================================
# SUBRAMA 6.1: EDUCACIÓN (PROGRESIÓN INSTITUCIONAL)
# ==========================================
TECHS_6_1_EDUCACION: list[Tecnologia] = [
    Tecnologia.crear(
        id="6.1.1_escuela_escribas", nombre="Escuela de escribas",
        bloque=6, subrama=1, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("estabilidad_social", 0.10)],
        descripcion="Formación básica de funcionarios para administración y registro.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.1.2_alfabetizacion", nombre="Alfabetización popular",
        bloque=6, subrama=1, nivel=2, padre_id="6.1.1_escuela_escribas",
        efectos=[EfectoTecnologia("eficiencia_investigacion", 0.10)],
        descripcion="Extensión de la lectoescritura más allá de la élite administrativa.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.1.3_biblioteca", nombre="Biblioteca pública",
        bloque=6, subrama=1, nivel=3, padre_id="6.1.2_alfabetizacion",
        efectos=[EfectoTecnologia("estabilidad_social", 0.10)],
        descripcion="Repositorio accesible de conocimiento que preserva saberes acumulados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.1.4_academia", nombre="Academia de sabios",
        bloque=6, subrama=1, nivel=4, padre_id="6.1.3_biblioteca",
        efectos=[EfectoTecnologia("eficiencia_investigacion", 0.15)],
        descripcion="Comunidad de estudiosos dedicados a la investigación sistemática.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.1.5_liceo", nombre="Liceo educativo",
        bloque=6, subrama=1, nivel=5, padre_id="6.1.4_academia",
        efectos=[EfectoTecnologia("calidad_educativa", 0.15)],
        descripcion="Enseñanza secundaria estructurada en disciplinas diferenciadas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.1.6_observatorio", nombre="Observatorio astronómico",
        bloque=6, subrama=1, nivel=6, padre_id="6.1.5_liceo",
        efectos=[EfectoTecnologia("eficiencia_investigacion", 0.15)],
        descripcion="Instalación científica para estudio de los cielos y medición del tiempo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.1.7_universidad", nombre="Universidad",
        bloque=6, subrama=1, nivel=7, padre_id="6.1.6_observatorio",
        efectos=[
            EfectoTecnologia("eficiencia_investigacion", 0.20),
            EfectoTecnologia("calidad_educativa", 0.20),
            EfectoTecnologia("universidad", 1.0),
        ],
        descripcion="Institución superior autónoma que otorga grados y genera conocimiento nuevo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 6.2: ARTES (SEPARADA DE ARTESANÍA B3)
# ==========================================
TECHS_6_2_ARTES: list[Tecnologia] = [
    Tecnologia.crear(
        id="6.2.1_ceramica_artistica", nombre="Cerámica artística",
        bloque=6, subrama=2, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Vasijas y objetos decorativos con valor estético más allá de lo utilitario.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.2.2_textil_artistico", nombre="Textil artístico",
        bloque=6, subrama=2, nivel=2, padre_id="6.2.1_ceramica_artistica",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.05)],
        descripcion="Tapices y bordados elaborados con técnicas decorativas complejas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.2.3_pintura", nombre="Pintura figurativa",
        bloque=6, subrama=2, nivel=3, padre_id="6.2.2_textil_artistico",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Representación visual de escenas narrativas y retratos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.2.4_escultura_artistica", nombre="Escultura artística",
        bloque=6, subrama=2, nivel=4, padre_id="6.2.3_pintura",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Obras tridimensionales con propósito estético y conmemorativo.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.2.5_musica", nombre="Música formalizada",
        bloque=6, subrama=2, nivel=5, padre_id="6.2.4_escultura_artistica",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.15)],
        descripcion="Composiciones estructuradas con notación y teoría musical.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.2.6_teatro_artistico", nombre="Teatro dramático",
        bloque=6, subrama=2, nivel=6, padre_id="6.2.5_musica",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Representaciones escénicas con guiones literarios y escenografía.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.2.7_mecenazgo", nombre="Mecenazgo artístico",
        bloque=6, subrama=2, nivel=7, padre_id="6.2.6_teatro_artistico",
        efectos=[
            EfectoTecnologia("prestigio_cultural", 0.20),
            EfectoTecnologia("renacimiento", 0.5),
        ],
        descripcion="Patrocinio sistemático de artistas por élites que impulsa explosión creativa.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 6.3: LITERATURA
# ==========================================
TECHS_6_3_LITERATURA: list[Tecnologia] = [
    Tecnologia.crear(
        id="6.3.1_tradicion_oral", nombre="Tradición oral",
        bloque=6, subrama=3, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("influencia_diplomatica", 0.10)],
        descripcion="Transmisión de historias y valores mediante narradores y bardos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.3.2_escritura_literaria", nombre="Escritura literaria",
        bloque=6, subrama=3, nivel=2, padre_id="6.3.1_tradicion_oral",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.05)],
        descripcion="Fijación de relatos en soporte escrito para preservación fiel.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.3.3_epopeya", nombre="Epopeya nacional",
        bloque=6, subrama=3, nivel=3, padre_id="6.3.2_escritura_literaria",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Relato fundacional que forja identidad colectiva y orgullo patrio.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.3.4_drama", nombre="Drama literario",
        bloque=6, subrama=3, nivel=4, padre_id="6.3.3_epopeya",
        efectos=[EfectoTecnologia("influencia_diplomatica", 0.10)],
        descripcion="Obras teatrales escritas que exploran la condición humana.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.3.5_historiografia", nombre="Historiografía crítica",
        bloque=6, subrama=3, nivel=5, padre_id="6.3.4_drama",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Registro analítico del pasado con metodología y fuentes verificables.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.3.6_poesia_culta", nombre="Poesía culta",
        bloque=6, subrama=3, nivel=6, padre_id="6.3.5_historiografia",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Versificación refinada con métrica compleja y temas elevados.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.3.7_enciclopedia", nombre="Enciclopedia universal",
        bloque=6, subrama=3, nivel=7, padre_id="6.3.6_poesia_culta",
        efectos=[EfectoTecnologia("influencia_diplomatica", 0.20)],
        descripcion="Compilación sistemática de todo el saber conocido en obra organizada.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 6.4: RELIGIÓN Y ESPIRITUALIDAD
# ==========================================
TECHS_6_4_RELIGION: list[Tecnologia] = [
    Tecnologia.crear(
        id="6.4.1_santuario", nombre="Santuario local",
        bloque=6, subrama=4, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_revueltas", 0.10)],
        descripcion="Lugar sagrado básico que cohesiona la comunidad en torno a creencias compartidas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.4.2_templo_local", nombre="Templo organizado",
        bloque=6, subrama=4, nivel=2, padre_id="6.4.1_santuario",
        efectos=[EfectoTecnologia("estabilidad_social", 0.10)],
        descripcion="Edificio religioso con clero residente y rituales regulares.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.4.3_peregrinaciones", nombre="Rutas de peregrinación",
        bloque=6, subrama=4, nivel=3, padre_id="6.4.2_templo_local",
        efectos=[EfectoTecnologia("felicidad_poblacion", 0.10)],
        descripcion="Viajes espirituales que fortalecen fe y generan intercambio cultural.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.4.4_clero_organizado", nombre="Clero jerárquico",
        bloque=6, subrama=4, nivel=4, padre_id="6.4.3_peregrinaciones",
        efectos=[EfectoTecnologia("reduccion_revueltas", 0.15)],
        descripcion="Estructura eclesiástica centralizada que unifica doctrina y práctica.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.4.5_festivales_religiosos", nombre="Festivales religiosos masivos",
        bloque=6, subrama=4, nivel=5, padre_id="6.4.4_clero_organizado",
        efectos=[EfectoTecnologia("estabilidad_social", 0.15)],
        descripcion="Celebraciones periódicas que refuerzan identidad y cohesión social.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.4.6_teologia", nombre="Teología sistemática",
        bloque=6, subrama=4, nivel=6, padre_id="6.4.5_festivales_religiosos",
        efectos=[EfectoTecnologia("estabilidad_social", 0.10)],
        descripcion="Marco doctrinal racionalizado que resuelve contradicciones y herejías.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.4.7_tolerancia_religiosa", nombre="Tolerancia religiosa oficial",
        bloque=6, subrama=4, nivel=7, padre_id="6.4.6_teologia",
        efectos=[EfectoTecnologia("estabilidad_social", 0.20)],
        descripcion="Reconocimiento legal de múltiples credos que elimina conflictos sectarios.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 6.5: ESPECTÁCULOS Y OCIO
# ==========================================
TECHS_6_5_ESPECTACULOS: list[Tecnologia] = [
    Tecnologia.crear(
        id="6.5.1_juegos_publicos", nombre="Juegos públicos",
        bloque=6, subrama=5, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("felicidad_poblacion", 0.10)],
        descripcion="Competencias atléticas abiertas que entretienen y cohesionan.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.5.2_circos", nombre="Circos y carreras",
        bloque=6, subrama=5, nivel=2, padre_id="6.5.1_juegos_publicos",
        efectos=[EfectoTecnologia("reduccion_revueltas", 0.10)],
        descripcion="Espectáculos masivos de velocidad que canalizan tensiones sociales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.5.3_termas", nombre="Termas públicas",
        bloque=6, subrama=5, nivel=3, padre_id="6.5.2_circos",
        efectos=[EfectoTecnologia("felicidad_poblacion", 0.10)],
        descripcion="Baños comunales que combinan higiene, socialización y ocio.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.5.4_fiestas_populares", nombre="Fiestas populares organizadas",
        bloque=6, subrama=5, nivel=4, padre_id="6.5.3_termas",
        efectos=[EfectoTecnologia("reduccion_revueltas", 0.15)],
        descripcion="Celebraciones cívicas periódicas que fortalecen sentido de pertenencia.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.5.5_anfiteatro", nombre="Anfiteatro",
        bloque=6, subrama=5, nivel=5, padre_id="6.5.4_fiestas_populares",
        efectos=[EfectoTecnologia("felicidad_poblacion", 0.15)],
        descripcion="Recinto monumental para espectáculos masivos con acústica diseñada.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.5.6_teatro_publico", nombre="Teatro público gratuito",
        bloque=6, subrama=5, nivel=6, padre_id="6.5.5_anfiteatro",
        efectos=[EfectoTecnologia("reduccion_revueltas", 0.15)],
        descripcion="Acceso universal a representaciones culturales financiadas por el estado.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.5.7_gran_coliseo", nombre="Gran Coliseo",
        bloque=6, subrama=5, nivel=7, padre_id="6.5.6_teatro_publico",
        efectos=[EfectoTecnologia("felicidad_poblacion", 0.20)],
        descripcion="Maravilla arquitectónica de entretenimiento que define la grandeza imperial.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 6.6: ARQUITECTURA CULTURAL
# ==========================================
TECHS_6_6_ARQUITECTURA_CULT: list[Tecnologia] = [
    Tecnologia.crear(
        id="6.6.1_plaza_publica", nombre="Plaza pública monumental",
        bloque=6, subrama=6, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("influencia_diplomatica", 0.05)],
        descripcion="Espacio cívico central que concentra vida social y política.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.6.2_jardines", nombre="Jardines ornamentales",
        bloque=6, subrama=6, nivel=2, padre_id="6.6.1_plaza_publica",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.05)],
        descripcion="Espacios verdes diseñados con criterio estético y simbólico.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.6.3_monumento", nombre="Monumento conmemorativo",
        bloque=6, subrama=6, nivel=3, padre_id="6.6.2_jardines",
        efectos=[EfectoTecnologia("influencia_diplomatica", 0.10)],
        descripcion="Estructura permanente que proyecta poder y memoria histórica.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.6.4_museo", nombre="Museo de antigüedades",
        bloque=6, subrama=6, nivel=4, padre_id="6.6.3_monumento",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.10)],
        descripcion="Colección curada de artefactos que demuestra profundidad cultural.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.6.5_palacio_cultural", nombre="Palacio de la Cultura",
        bloque=6, subrama=6, nivel=5, padre_id="6.6.4_museo",
        efectos=[EfectoTecnologia("influencia_diplomatica", 0.15)],
        descripcion="Edificio emblemático que alberga artes, ciencias y diplomacia.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.6.6_acropolis", nombre="Acrópolis ceremonial",
        bloque=6, subrama=6, nivel=6, padre_id="6.6.5_palacio_cultural",
        efectos=[EfectoTecnologia("prestigio_cultural", 0.15)],
        descripcion="Complejo elevado que domina el paisaje urbano con majestuosidad.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.6.7_maravilla_mundo", nombre="Maravilla del Mundo",
        bloque=6, subrama=6, nivel=7, padre_id="6.6.6_acropolis",
        efectos=[EfectoTecnologia("maravilla_cultural", 1.0)],
        descripcion="Obra maestra irrepetible que atrae admiración universal eterna.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 6.7: FILOSOFÍA (REORDENADA CRONOLÓGICAMENTE)
# Progresión: Mitología → Ética → Lógica → Metafísica → Ciencia Natural → Humanismo → Ilustración
# NOTA: Humanismo movido a Nv6 (requiere base científica previa). Ilustración como culminación.
# ==========================================
TECHS_6_7_FILOSOFIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="6.7.1_mitologia", nombre="Mitología sistematizada",
        bloque=6, subrama=7, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("estabilidad_social", 0.05)],
        descripcion="Cosmogonía ordenada que explica el mundo mediante narrativas sagradas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.7.2_etica", nombre="Ética normativa",
        bloque=6, subrama=7, nivel=2, padre_id="6.7.1_mitologia",
        efectos=[EfectoTecnologia("calidad_educativa", 0.10)],
        descripcion="Reflexión sobre virtud y conducta correcta más allá de la tradición.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.7.3_logica", nombre="Lógica formal",
        bloque=6, subrama=7, nivel=3, padre_id="6.7.2_etica",
        efectos=[EfectoTecnologia("eficiencia_investigacion", 0.10)],
        descripcion="Reglas de razonamiento válido que fundamentan todo conocimiento riguroso.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.7.4_metafisica", nombre="Metafísica",
        bloque=6, subrama=7, nivel=4, padre_id="6.7.3_logica",
        efectos=[EfectoTecnologia("calidad_educativa", 0.05)],
        descripcion="Indagación sobre la naturaleza última de la realidad y el ser.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.7.5_ciencia_natural", nombre="Filosofía natural",
        bloque=6, subrama=7, nivel=5, padre_id="6.7.4_metafisica",
        efectos=[EfectoTecnologia("eficiencia_investigacion", 0.10)],
        descripcion="Estudio racional de fenómenos naturales sin recurrir a explicaciones sobrenaturales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Movido a Nv6 (requiere base científica y lógica previas)
    Tecnologia.crear(
        id="6.7.6_humanismo", nombre="Humanismo",
        bloque=6, subrama=7, nivel=6, padre_id="6.7.5_ciencia_natural",
        efectos=[EfectoTecnologia("calidad_educativa", 0.15)],
        descripcion="Centralidad del ser humano y su potencial como medida de todas las cosas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="6.7.7_ilustracion", nombre="Ilustración",
        bloque=6, subrama=7, nivel=7, padre_id="6.7.6_humanismo",
        efectos=[
            EfectoTecnologia("calidad_educativa", 0.20),
            EfectoTecnologia("renacimiento", 0.5),
        ],
        descripcion="Supremacía de la razón, el progreso y la libertad intelectual como ideales civilizatorios.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# EXPORTACIÓN UNIFICADA DEL BLOQUE 6
# ==========================================
TECNOLOGIAS_BLOQUE_6: list[Tecnologia] = (
    TECHS_6_1_EDUCACION
    + TECHS_6_2_ARTES
    + TECHS_6_3_LITERATURA
    + TECHS_6_4_RELIGION
    + TECHS_6_5_ESPECTACULOS
    + TECHS_6_6_ARQUITECTURA_CULT
    + TECHS_6_7_FILOSOFIA
)
