# src/investigacion/arbol_investigaciones.py
from __future__ import annotations

from collections.abc import Iterator
from dataclasses import dataclass, field

from src.investigacion.tecnologia import Tecnologia


@dataclass(frozen=True)
class ArbolInvestigaciones:
    """
    Contenedor inmutable del árbol completo de investigaciones.

    Se construye una vez al arrancar el servidor. Durante la partida es solo lectura.
    El estado de investigación por partida vive externamente (set[str] en Partida).

    Responsabilidades:
    - Almacenar y indexar las 343 tecnologías
    - Validar integridad estructural al construirse
    - Resolver prerequisitos y disponibilidad
    - Servir datos a Laboratorio y UI
    """

    # ==========================================
    # ÍNDICES INTERNOS (Construidos en construir())
    # ==========================================
    _por_id: dict[str, Tecnologia] = field(default_factory=dict, repr=False)
    _por_bloque_subrama: dict[tuple[int, int], list[Tecnologia]] = field(
        default_factory=dict, repr=False
    )
    _errores_validacion: tuple[str, ...] = field(default=(), repr=False)

    # ==========================================
    # CONSTRUCCIÓN Y VALIDACIÓN
    # ==========================================
    @classmethod
    def construir(cls, tecnologias: list[Tecnologia]) -> ArbolInvestigaciones:
        """
        Factory method principal. Construye el árbol y valida su integridad.
        Lanza ValueError si hay errores estructurales críticos.
        """
        arbol = cls()

        # Construir índice por ID
        object.__setattr__(arbol, '_por_id', {t.id: t for t in tecnologias})

        # Agrupar por (bloque, subrama) y ordenar por nivel
        agrupado: dict[tuple[int, int], list[Tecnologia]] = {}
        for t in tecnologias:
            clave = (t.bloque, t.subrama)
            if clave not in agrupado:
                agrupado[clave] = []
            agrupado[clave].append(t)

        # Ordenar cada subrama por nivel
        for clave in agrupado:
            agrupado[clave].sort(key=lambda x: x.nivel)

        object.__setattr__(arbol, '_por_bloque_subrama', agrupado)

        # Validar integridad
        errores = arbol._validar_integridad()
        if errores:
            object.__setattr__(arbol, '_errores_validacion', tuple(errores))
            raise ValueError(
                f"❌ Árbol de investigaciones con {len(errores)} error(es):\n"
                + "\n".join(f"   • {e}" for e in errores)
            )

        print(f"✅ Árbol de investigaciones cargado: {len(tecnologias)} tecnologías validadas.")
        return arbol

    def _validar_integridad(self) -> list[str]:
        """Verifica la estructura completa del árbol."""
        errores: list[str] = []

        for tech in self._por_id.values():
            # 1. Verificar que niveles >1 tienen padre existente y válido
            if tech.nivel > 1:
                if tech.padre_id is None:
                    errores.append(f"{tech.id}: Nivel {tech.nivel} sin padre_id")
                elif tech.padre_id not in self._por_id:
                    errores.append(f"{tech.id}: Padre '{tech.padre_id}' no existe")
                else:
                    # Acceso directo [] es seguro aquí porque ya verificamos
                    # que padre_id no es None y que existe en el diccionario
                    padre = self._por_id[tech.padre_id]
                    # Verificar que padre está en misma subrama y nivel anterior
                    if (padre.bloque, padre.subrama) != (tech.bloque, tech.subrama):
                        errores.append(
                            f"{tech.id}: Padre '{tech.padre_id}' está en otra subrama"
                        )
                    if padre.nivel >= tech.nivel:
                        errores.append(
                            f"{tech.id}: Padre '{tech.padre_id}' tiene nivel >= hijo"
                        )

            # 2. Verificar que nivel 1 no tiene padre
            if tech.nivel == 1 and tech.padre_id is not None:
                errores.append(f"{tech.id}: Nivel 1 no debería tener padre_id")

        # 3. Verificar que todas las subramas tienen niveles consecutivos sin huecos
        for (bloque, subrama), techs in self._por_bloque_subrama.items():
            niveles = [t.nivel for t in techs]
            esperados = list(range(1, len(niveles) + 1))
            if niveles != esperados:
                errores.append(
                    f"Bloque {bloque}.{subrama}: Niveles {niveles} "
                    f"no son consecutivos (esperado {esperados})"
                )

        return errores

    # ==========================================
    # CONSULTAS POR ID
    # ==========================================
    def get(self, id_tech: str) -> Tecnologia | None:
        """Devuelve una tecnología por su ID, o None si no existe."""
        return self._por_id.get(id_tech)

    def obtener(self, id_tech: str) -> Tecnologia:
        """Devuelve una tecnología por su ID. Lanza KeyError si no existe."""
        if id_tech not in self._por_id:
            raise KeyError(f"Tecnología '{id_tech}' no encontrada en el árbol.")
        return self._por_id[id_tech]

    def existe(self, id_tech: str) -> bool:
        return id_tech in self._por_id

    # ==========================================
    # CONSULTAS ESTRUCTURALES
    # ==========================================
    def get_subrama(self, bloque: int, subrama: int) -> list[Tecnologia]:
        """Devuelve todas las tecnologías de una subrama, ordenadas por nivel."""
        return self._por_bloque_subrama.get((bloque, subrama), [])

    def get_nivel_1_disponibles(self) -> list[Tecnologia]:
        """Devuelve todas las tecnologías de nivel 1 (siempre disponibles)."""
        return [t for t in self._por_id.values() if t.es_nivel_1]

    def get_hijos(self, id_tech: str) -> list[Tecnologia]:
        """Devuelve las tecnologías que tienen esta como padre directo."""
        return [t for t in self._por_id.values() if t.padre_id == id_tech]

    # ==========================================
    # RESOLUCIÓN DE DISPONIBILIDAD
    # ==========================================
    def puede_investigar(
        self, id_tech: str, investigaciones_completadas: set[str]
    ) -> tuple[bool, str]:
        """
        Verifica si una tecnología puede ser investigada dado el estado actual.

        Returns:
            (puede, razon)
        """
        tech = self._por_id.get(id_tech)
        if tech is None:
            return False, f"❌ Tecnología '{id_tech}' no existe."

        if id_tech in investigaciones_completadas:
            return False, f"ℹ️ '{tech.nombre}' ya fue investigada."

        # Nivel 1 siempre disponible (si no está completada)
        if tech.es_nivel_1:
            return True, "✅ Disponible (nivel 1)."

        # Verificar prerequisito directo
        if tech.padre_id is not None and tech.padre_id not in investigaciones_completadas:
            padre = self._por_id.get(tech.padre_id)
            nombre_padre = padre.nombre if padre else tech.padre_id
            return False, f"🔒 Requiere investigar primero: '{nombre_padre}'."

        return True, "✅ Prerequisito cumplido."

    def obtener_siguientes_disponibles(
        self, investigaciones_completadas: set[str]
    ) -> list[Tecnologia]:
        """
        Devuelve todas las tecnologías que el jugador PUEDE investigar ahora.
        Útil para mostrar opciones en el Laboratorio / UI.
        """
        disponibles: list[Tecnologia] = []
        for tech in self._por_id.values():
            if tech.id in investigaciones_completadas:
                continue
            puede, _ = self.puede_investigar(tech.id, investigaciones_completadas)
            if puede:
                disponibles.append(tech)
        return disponibles

    # ==========================================
    # ESTADÍSTICAS Y DEBUG
    # ==========================================
    @property
    def total_tecnologias(self) -> int:
        return len(self._por_id)

    @property
    def total_bloques(self) -> int:
        bloques = {b for b, _ in self._por_bloque_subrama}
        return len(bloques)

    def resumen(self) -> dict:
        """Resumen estadístico del árbol para debug / admin."""
        por_bloque: dict[int, int] = {}
        for tech in self._por_id.values():
            por_bloque[tech.bloque] = por_bloque.get(tech.bloque, 0) + 1

        return {
            "total_tecnologias": self.total_tecnologias,
            "total_bloques": self.total_bloques,
            "tecnologias_por_bloque": por_bloque,
            "subramas": len(self._por_bloque_subrama),
            "errores_validacion": len(self._errores_validacion),
        }

    # ==========================================
    # ITERACIÓN
    # ==========================================
    def __iter__(self) -> Iterator[Tecnologia]:
        """Itera sobre todas las tecnologías en orden de ID."""
        return iter(sorted(self._por_id.values(), key=lambda t: t.id))

    def __len__(self) -> int:
        return len(self._por_id)

    def __contains__(self, id_tech: str) -> bool:
        return id_tech in self._por_id

    # ==========================================
    # REPRESENTACIÓN
    # ==========================================
    def __str__(self) -> str:
        return (f"🌳 ArbolInvestigaciones: {self.total_tecnologias} tecnologías, "
                f"{self.total_bloques} bloques, {len(self._por_bloque_subrama)} subramas")
