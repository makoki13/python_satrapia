# src/investigacion/datos/bloque_7_ciencia.py
"""
Datos de tecnologías del Bloque 7: Ciencia y Tecnología Avanzada.
49 tecnologías (7 subramas × 7 niveles).

CORRECCIONES CRÍTICAS RESPECTO AL PDF ORIGINAL:
- 7.1 Método Científico: Progresión epistemológica pura, separada de Filosofía (B6).
- 7.2 Matemáticas: Reordenada. Estadística movida tras Cálculo (requiere base analítica).
- 7.4 Medicina vs 7.5 Biología: Anatomía/Cirugía en Medicina (aplicada); Taxonomía/Fisiología en Biología (teórica).
- 7.7 Publicaciones: Renombrada desde "Difusión" para enfatizar publicaciones periódicas como motor científico.
- IDs DUPLICADOS ELIMINADOS: Se asignaron IDs únicos secuenciales en todas las subramas.

Los IDs de efectos coinciden EXACTAMENTE con REGISTRO_PARAMETROS.
"""
from src.investigacion.tecnologia import EfectoTecnologia, Tecnologia

COSTE_ORO_BASE = 100
TURNOS_BASE = 3

# ==========================================
# SUBRAMA 7.1: MÉTODO CIENTÍFICO (PROGRESIÓN EPISTEMOLÓGICA)
# Separada de B6.7 (Filosofía) por enfoque en procedimiento verificable
# ==========================================
TECHS_7_1_METODO_CIENTIFICO: list[Tecnologia] = [
    Tecnologia.crear(
        id="7.1.1_empirismo", nombre="Empirismo sistemático",
        bloque=7, subrama=1, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("velocidad_cientifica", 0.10)],
        descripcion="Observación directa y registro meticuloso como base del conocimiento.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.1.2_experimentacion", nombre="Experimentación controlada",
        bloque=7, subrama=1, nivel=2, padre_id="7.1.1_empirismo",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.10)],
        descripcion="Manipulación deliberada de variables para aislar causas y efectos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.1.3_hipotesis", nombre="Formulación de hipótesis",
        bloque=7, subrama=1, nivel=3, padre_id="7.1.2_experimentacion",
        efectos=[EfectoTecnologia("velocidad_cientifica", 0.10)],
        descripcion="Propuestas explicativas falsables que guían la investigación.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.1.4_verificacion", nombre="Verificación empírica",
        bloque=7, subrama=1, nivel=4, padre_id="7.1.3_hipotesis",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.10)],
        descripcion="Confirmación o refutación de hipótesis mediante evidencia reproducible.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.1.5_replicabilidad", nombre="Replicabilidad experimental",
        bloque=7, subrama=1, nivel=5, padre_id="7.1.4_verificacion",
        efectos=[EfectoTecnologia("velocidad_cientifica", 0.15)],
        descripcion="Protocolos detallados que permiten a otros reproducir resultados independientemente.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.1.6_revision_pares", nombre="Revisión por pares",
        bloque=7, subrama=1, nivel=6, padre_id="7.1.5_replicabilidad",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.15)],
        descripcion="Evaluación crítica por expertos anónimos antes de aceptar hallazgos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.1.7_metodo_cientifico", nombre="Método Científico Formal",
        bloque=7, subrama=1, nivel=7, padre_id="7.1.6_revision_pares",
        efectos=[
            EfectoTecnologia("velocidad_cientifica", 0.25),
            EfectoTecnologia("metodo_cientifico", 1.0),
            EfectoTecnologia("revolucion_cientifica", 0.5),
        ],
        descripcion="Marco metodológico universal que define la ciencia moderna.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 7.2: MATEMÁTICAS (REORDENADA)
# NOTA: Estadística movida tras Cálculo (requiere base analítica)
# ==========================================
TECHS_7_2_MATEMATICAS: list[Tecnologia] = [
    Tecnologia.crear(
        id="7.2.1_aritmetica_avanzada", nombre="Aritmética avanzada",
        bloque=7, subrama=2, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("precision_medicion", 0.10)],
        descripcion="Sistemas numéricos posicionales y algoritmos de cálculo eficientes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.2.2_algebra", nombre="Álgebra simbólica",
        bloque=7, subrama=2, nivel=2, padre_id="7.2.1_aritmetica_avanzada",
        efectos=[EfectoTecnologia("innovacion_tecnologica", 0.10)],
        descripcion="Manipulación de incógnitas y ecuaciones mediante notación abstracta.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.2.3_geometria_analitica", nombre="Geometría analítica",
        bloque=7, subrama=2, nivel=3, padre_id="7.2.2_algebra",
        efectos=[EfectoTecnologia("precision_medicion", 0.10)],
        descripcion="Unificación de álgebra y geometría mediante coordenadas cartesianas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.2.4_calculo", nombre="Cálculo infinitesimal",
        bloque=7, subrama=2, nivel=4, padre_id="7.2.3_geometria_analitica",
        efectos=[EfectoTecnologia("innovacion_tecnologica", 0.15)],
        descripcion="Herramientas para modelar cambio continuo y áreas bajo curvas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    # REORDENADO: Movido tras Cálculo (requiere base analítica)
    Tecnologia.crear(
        id="7.2.5_probabilidad", nombre="Teoría de la probabilidad",
        bloque=7, subrama=2, nivel=5, padre_id="7.2.4_calculo",
        efectos=[EfectoTecnologia("precision_medicion", 0.15)],
        descripcion="Marco matemático para cuantificar incertidumbre y azar.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.2.6_estadistica", nombre="Estadística inferencial",
        bloque=7, subrama=2, nivel=6, padre_id="7.2.5_probabilidad",
        efectos=[EfectoTecnologia("innovacion_tecnologica", 0.15)],
        descripcion="Extracción de conclusiones generales a partir de muestras de datos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.2.7_matematica_aplicada", nombre="Matemática aplicada",
        bloque=7, subrama=2, nivel=7, padre_id="7.2.6_estadistica",
        efectos=[EfectoTecnologia("precision_medicion", 0.20)],
        descripcion="Modelado matemático de fenómenos físicos, biológicos y sociales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 7.3: ASTRONOMÍA Y FÍSICA CELESTE
# ==========================================
TECHS_7_3_ASTRONOMIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="7.3.1_observacion_sistematica", nombre="Observación astronómica sistemática",
        bloque=7, subrama=3, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("precision_medicion", 0.05)],
        descripcion="Registros nocturnos regulares con instrumentos básicos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.3.2_telescopio", nombre="Telescopio óptico",
        bloque=7, subrama=3, nivel=2, padre_id="7.3.1_observacion_sistematica",
        efectos=[EfectoTecnologia("precision_medicion", 0.10)],
        descripcion="Instrumento que amplifica la visión celestial revelando detalles invisibles.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.3.3_mecanica_celeste", nombre="Mecánica celeste",
        bloque=7, subrama=3, nivel=3, padre_id="7.3.2_telescopio",
        efectos=[EfectoTecnologia("precision_medicion", 0.10)],
        descripcion="Leyes matemáticas que describen órbitas y movimientos planetarios.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.3.4_cartografia_celeste", nombre="Cartografía celeste precisa",
        bloque=7, subrama=3, nivel=4, padre_id="7.3.3_mecanica_celeste",
        efectos=[EfectoTecnologia("precision_medicion", 0.10)],
        descripcion="Mapas estelares detallados para navegación y referencia temporal.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.3.5_espectroscopia", nombre="Espectroscopia estelar",
        bloque=7, subrama=3, nivel=5, padre_id="7.3.4_cartografia_celeste",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.10)],
        descripcion="Análisis de luz para determinar composición química de cuerpos celestes.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.3.6_gravitacion_universal", nombre="Gravitación universal",
        bloque=7, subrama=3, nivel=6, padre_id="7.3.5_espectroscopia",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.15)],
        descripcion="Teoría unificada que explica atracción entre todos los cuerpos masivos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.3.7_cosmologia", nombre="Cosmología científica",
        bloque=7, subrama=3, nivel=7, padre_id="7.3.6_gravitacion_universal",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.20)],
        descripcion="Estudio del origen, estructura y evolución del universo como sistema físico.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 7.4: MEDICINA (PRÁCTICA CLÍNICA Y SALUD PÚBLICA)
# Separada de Biología (7.5): aquí todo es aplicación clínica
# ==========================================
TECHS_7_4_MEDICINA: list[Tecnologia] = [
    Tecnologia.crear(
        id="7.4.1_anatomia", nombre="Anatomía descriptiva",
        bloque=7, subrama=4, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("eficiencia_medica", 0.10)],
        descripcion="Disección sistemática para mapear estructuras del cuerpo humano.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.4.2_cirugia", nombre="Cirugía reglada",
        bloque=7, subrama=4, nivel=2, padre_id="7.4.1_anatomia",
        efectos=[EfectoTecnologia("reduccion_mortalidad", 0.10)],
        descripcion="Procedimientos quirúrgicos estandarizados con protocolos de seguridad.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.4.3_farmacologia", nombre="Farmacología experimental",
        bloque=7, subrama=4, nivel=3, padre_id="7.4.2_cirugia",
        efectos=[EfectoTecnologia("eficiencia_medica", 0.10)],
        descripcion="Estudio sistemático de sustancias activas y sus dosis terapéuticas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.4.4_vacunacion", nombre="Vacunación preventiva",
        bloque=7, subrama=4, nivel=4, padre_id="7.4.3_farmacologia",
        efectos=[EfectoTecnologia("reduccion_mortalidad", 0.15)],
        descripcion="Inmunización artificial que previene enfermedades infecciosas masivas.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.4.5_higiene_publica", nombre="Higiene pública",
        bloque=7, subrama=4, nivel=5, padre_id="7.4.4_vacunacion",
        efectos=[EfectoTecnologia("eficiencia_medica", 0.15)],
        descripcion="Normas sanitarias colectivas que reducen propagación de enfermedades.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.4.6_saneamiento", nombre="Saneamiento urbano",
        bloque=7, subrama=4, nivel=6, padre_id="7.4.5_higiene_publica",
        efectos=[EfectoTecnologia("reduccion_mortalidad", 0.15)],
        descripcion="Infraestructura de agua potable y alcantarillado que elimina focos epidémicos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.4.7_hospital_moderno", nombre="Hospital moderno",
        bloque=7, subrama=4, nivel=7, padre_id="7.4.6_saneamiento",
        efectos=[EfectoTecnologia("eficiencia_medica", 0.25)],
        descripcion="Institución médica especializada con personal formado y equipamiento científico.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 7.5: BIOLOGÍA (ESTUDIO TEÓRICO DE ORGANISMOS)
# Separada de Medicina (7.4): aquí todo es conocimiento teórico
# ==========================================
TECHS_7_5_BIOLOGIA: list[Tecnologia] = [
    Tecnologia.crear(
        id="7.5.1_taxonomia", nombre="Taxonomía sistemática",
        bloque=7, subrama=5, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("reduccion_mortalidad", 0.05)],
        descripcion="Clasificación jerárquica de seres vivos basada en características observables.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.5.2_fisiologia", nombre="Fisiología comparada",
        bloque=7, subrama=5, nivel=2, padre_id="7.5.1_taxonomia",
        efectos=[EfectoTecnologia("eficiencia_medica", 0.10)],
        descripcion="Estudio de funciones vitales en diferentes organismos para entender principios universales.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.5.3_genetica", nombre="Genética mendeliana",
        bloque=7, subrama=5, nivel=3, padre_id="7.5.2_fisiologia",
        efectos=[EfectoTecnologia("innovacion_tecnologica", 0.15)],
        descripcion="Leyes de herencia que explican transmisión de caracteres entre generaciones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.5.4_epidemiologia", nombre="Epidemiología estadística",
        bloque=7, subrama=5, nivel=4, padre_id="7.5.3_genetica",
        efectos=[EfectoTecnologia("eficiencia_medica", 0.15)],
        descripcion="Análisis cuantitativo de patrones de enfermedad en poblaciones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.5.5_microbiologia", nombre="Microbiología",
        bloque=7, subrama=5, nivel=5, padre_id="7.5.4_epidemiologia",
        efectos=[EfectoTecnologia("innovacion_tecnologica", 0.15)],
        descripcion="Descubrimiento y estudio de microorganismos como agentes biológicos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.5.6_bioquimica", nombre="Bioquímica",
        bloque=7, subrama=5, nivel=6, padre_id="7.5.5_microbiologia",
        efectos=[EfectoTecnologia("reduccion_mortalidad", 0.15)],
        descripcion="Comprensión de procesos vitales a nivel molecular y químico.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.5.7_teoria_evolucion", nombre="Teoría de la Evolución",
        bloque=7, subrama=5, nivel=7, padre_id="7.5.6_bioquimica",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.20)],
        descripcion="Marco unificador que explica diversidad biológica mediante selección natural.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 7.6: INSTITUCIONES CIENTÍFICAS
# ==========================================
TECHS_7_6_INSTITUCIONES: list[Tecnologia] = [
    Tecnologia.crear(
        id="7.6.1_correspondencia", nombre="Correspondencia científica",
        bloque=7, subrama=6, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("colaboracion_cientifica", 0.10)],
        descripcion="Red epistolar informal entre investigadores de diferentes regiones.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.6.2_congresos", nombre="Congresos científicos",
        bloque=7, subrama=6, nivel=2, padre_id="7.6.1_correspondencia",
        efectos=[EfectoTecnologia("colaboracion_cientifica", 0.15)],
        descripcion="Reuniones periódicas para presentar hallazgos y debatir en persona.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.6.3_laboratorio_nacional", nombre="Laboratorio Nacional",
        bloque=7, subrama=6, nivel=3, padre_id="7.6.2_congresos",
        efectos=[EfectoTecnologia("velocidad_cientifica", 0.15)],
        descripcion="Instalación estatal equipada para investigación experimental a gran escala.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.6.4_red_investigadores", nombre="Red formal de investigadores",
        bloque=7, subrama=6, nivel=4, padre_id="7.6.3_laboratorio_nacional",
        efectos=[
            EfectoTecnologia("produccion_conocimiento", 0.15),
            EfectoTecnologia("colaboracion_cientifica", 0.15),
        ],
        descripcion="Asociación estructurada con membresía, cuotas y objetivos compartidos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.6.5_academia_ciencias", nombre="Academia de Ciencias",
        bloque=7, subrama=6, nivel=5, padre_id="7.6.4_red_investigadores",
        efectos=[EfectoTecnologia("velocidad_cientifica", 0.20)],
        descripcion="Institución oficial que valida, premia y dirige la investigación nacional.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.6.6_fondos_investigacion", nombre="Fondos públicos de investigación",
        bloque=7, subrama=6, nivel=6, padre_id="7.6.5_academia_ciencias",
        efectos=[EfectoTecnologia("innovacion_tecnologica", 0.20)],
        descripcion="Financiación estatal competitiva para proyectos científicos prioritarios.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.6.7_sociedad_real", nombre="Sociedad Real de Ciencias",
        bloque=7, subrama=6, nivel=7, padre_id="7.6.6_fondos_investigacion",
        efectos=[
            EfectoTecnologia("revolucion_cientifica", 0.5),
            EfectoTecnologia("sociedad_real_ciencias", 0.5),
        ],
        descripcion="Institución suprema que consagra la ciencia como pilar del estado moderno.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# SUBRAMA 7.7: PUBLICACIONES CIENTÍFICAS
# Renombrada desde "Difusión" para enfatizar publicaciones periódicas
# ==========================================
TECHS_7_7_PUBLICACIONES: list[Tecnologia] = [
    Tecnologia.crear(
        id="7.7.1_traduccion_cientifica", nombre="Traducción científica",
        bloque=7, subrama=7, nivel=1, padre_id=None,
        efectos=[EfectoTecnologia("colaboracion_cientifica", 0.10)],
        descripcion="Vertido de obras clave a lenguas vernáculas para ampliar acceso.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.7.2_catalogos", nombre="Catálogos bibliográficos",
        bloque=7, subrama=7, nivel=2, padre_id="7.7.1_traduccion_cientifica",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.05)],
        descripcion="Inventarios sistemáticos de obras disponibles para evitar duplicación.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.7.3_revista_cientifica", nombre="Revista científica periódica",
        bloque=7, subrama=7, nivel=3, padre_id="7.7.2_catalogos",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.15)],
        descripcion="Publicación regular con revisión editorial que acelera difusión de hallazgos.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.7.4_monografias", nombre="Monografías especializadas",
        bloque=7, subrama=7, nivel=4, padre_id="7.7.3_revista_cientifica",
        efectos=[EfectoTecnologia("produccion_conocimiento", 0.10)],
        descripcion="Tratamientos exhaustivos de temas específicos con rigor académico.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.7.5_biblioteca_universal", nombre="Biblioteca Universal de Ciencias",
        bloque=7, subrama=7, nivel=5, padre_id="7.7.4_monografias",
        efectos=[EfectoTecnologia("colaboracion_cientifica", 0.20)],
        descripcion="Colección centralizada que aspira a contener todo el saber científico publicado.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.7.6_indice_abstracts", nombre="Índice de resúmenes",
        bloque=7, subrama=7, nivel=6, padre_id="7.7.5_biblioteca_universal",
        efectos=[EfectoTecnologia("colaboracion_cientifica", 0.15)],
        descripcion="Base de datos de resúmenes que permite búsqueda eficiente de literatura.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
    Tecnologia.crear(
        id="7.7.7_enciclopedia_ciencias", nombre="Enciclopedia de las Ciencias",
        bloque=7, subrama=7, nivel=7, padre_id="7.7.6_indice_abstracts",
        efectos=[
            EfectoTecnologia("produccion_conocimiento", 0.20),
            EfectoTecnologia("sociedad_real_ciencias", 0.5),
        ],
        descripcion="Obra magna que sintetiza y organiza todo el conocimiento científico de la era.",
        coste_oro_base=COSTE_ORO_BASE, turnos_base=TURNOS_BASE,
    ),
]

# ==========================================
# EXPORTACIÓN UNIFICADA DEL BLOQUE 7
# ==========================================
TECNOLOGIAS_BLOQUE_7: list[Tecnologia] = (
    TECHS_7_1_METODO_CIENTIFICO
    + TECHS_7_2_MATEMATICAS
    + TECHS_7_3_ASTRONOMIA
    + TECHS_7_4_MEDICINA
    + TECHS_7_5_BIOLOGIA
    + TECHS_7_6_INSTITUCIONES
    + TECHS_7_7_PUBLICACIONES
)
