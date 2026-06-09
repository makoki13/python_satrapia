# src/core/server_tick.py
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from src.logistica.transporte import TipoTransporte

if TYPE_CHECKING:
    from src.config.game_config import GameConfig
    from src.gestion.partida import Partida
    from src.investigacion.arbol_investigaciones import ArbolInvestigaciones

logger = logging.getLogger(__name__)


class ServerTick:
    """
    Motor de simulación del juego.

    Ejecuta un ciclo completo de actualización para toda la partida:
    1. Economía: Producción de edificios + Recaudación de impuestos
    2. Logística: Movimiento de transportes + Transferencias en destino
    3. Investigación: Avance del laboratorio del reino + Aplicación de efectos

    Es stateless respecto a la lógica de negocio; solo orquesta llamadas.
    """

    def __init__(
        self,
        partida: Partida,
        config: GameConfig,
        arbol: ArbolInvestigaciones,
    ):
        self.partida = partida
        self.config = config
        self.arbol = arbol

    async def ejecutar(self) -> dict:  # noqa: C901
        """
        Ejecuta un tick completo del servidor.

        Returns:
            Resumen del tick con eventos generados (para broadcast WS).
        """
        eventos: list[dict] = []

        logger.debug(f"⏱️ Iniciando tick {self.partida.turno_actual + 1}")

        # ==========================================
        # FASE 1: ECONOMÍA (Por ciudad)
        # ==========================================
        for ciudad in self.partida.ciudades:
            # 1a. Producción de edificios productivos
            for edificio in ciudad.obtener_edificios_productivos():
                exito, cantidad, msg = edificio.producir(ciudad.almacen, self.config)
                if not exito and "agotada" in msg.lower():
                    eventos.append({
                        "tipo": "alerta_fuente_agotada",
                        "ciudad": ciudad.nombre,
                        "mensaje": msg,
                    })
                elif exito and cantidad > 0:
                    logger.debug(f"   🏭 {msg}")

            # 1b. Recaudación de impuestos en el Palacio
            if ciudad.palacio:
                exito_imp, oro, msg_imp = ciudad.palacio.recaudar_impuestos(self.config)
                if exito_imp and oro > 0:
                    logger.debug(f"   💰 {msg_imp}")
                    eventos.append({
                        "tipo": "impuestos_recaudados",
                        "ciudad": ciudad.nombre,
                        "oro": oro,
                        "poblacion": ciudad.palacio.get_poblacion(),
                    })

        # ==========================================
        # FASE 2: LOGÍSTICA (Global)
        # ==========================================
        if hasattr(self.partida, 'gestor_transportes'):
            llegadas = self.partida.gestor_transportes.avanzar_todos(self.partida.mapa)

            for evento_llegada in llegadas:
                t = evento_llegada.transport

                # Procesar transferencia según tipo de transporte
                if t.tipo == TipoTransporte.RECURSOS and t.tipo_recurso:
                    ciudad_destino = self.partida.obtener_ciudad_en(t.destino)
                    if ciudad_destino:
                        exito_transf, real, msg_transf = ciudad_destino.almacen.agregar_recurso(
                            t.tipo_recurso, t.cantidad, self.config
                        )
                        logger.info(f"📦 Transferencia en {ciudad_destino.nombre}: {msg_transf}")
                        eventos.append({
                            "tipo": "transporte_recursos_llegado",
                            "ciudad": ciudad_destino.nombre,
                            "recurso": t.tipo_recurso.value,
                            "cantidad": real,
                        })
                    else:
                        logger.warning(f"⚠️ Transporte {t.id} llegó a {t.destino} pero no hay ciudad.")

                elif t.tipo == TipoTransporte.EJERCITO:
                    # Futuro: desplegar ejército en destino
                    logger.info(f"⚔️ Ejército llegado a {t.destino} (despliegue pendiente)")
                    eventos.append({
                        "tipo": "ejercito_desplegado",
                        "destino": str(t.destino),
                        "metadata": t.metadata,
                    })

                elif t.tipo == TipoTransporte.TRIBU:
                    # Futuro: actualizar posición del campamento nómada
                    logger.info(f"🏕️ Tribu migró a {t.destino}")
                    eventos.append({
                        "tipo": "tribu_migrada",
                        "destino": str(t.destino),
                        "propietario": t.propietario_id,
                    })

                elif t.tipo == TipoTransporte.COMERCIO:
                    # Futuro: procesar intercambio comercial pactado
                    logger.info(f"🤝 Comercio completado en {t.destino}")

                # Eliminar transporte tras procesamiento
                self.partida.gestor_transportes.eliminar(t.id)

        # ==========================================
        # FASE 3: INVESTIGACIÓN (Por reino)
        # ==========================================
        for reino in self.partida.reinos:
            if reino.tiene_laboratorio() and reino.laboratorio.esta_investigando:
                completada, tech_id = reino.laboratorio.avanzar_tick()

                if completada and tech_id:
                    # Registrar como completada
                    reino.investigaciones_completadas.add(tech_id)

                    # Obtener tecnología y aplicar efectos
                    tech = self.arbol.obtener(tech_id)
                    efectos_aplicados: list[dict] = []

                    for efecto in tech.efectos:
                        try:
                            param = self.config.get_parametro(efecto.id_parametro)
                            nuevo_valor = param.calcular_valor(reino.investigaciones_completadas)
                            efectos_aplicados.append({
                                "parametro": efecto.id_parametro,
                                "nombre": param.nombre,
                                "nuevo_valor": round(nuevo_valor, 2),
                            })
                            logger.info(
                                f"📈 [{reino.nombre}] {param.nombre}: {nuevo_valor:.2f}"
                            )
                        except KeyError:
                            logger.error(
                                f"❌ Parámetro '{efecto.id_parametro}' no encontrado "
                                f"al completar '{tech_id}'"
                            )

                    eventos.append({
                        "tipo": "investigacion_completada",
                        "reino": reino.nombre,
                        "tech_id": tech_id,
                        "tech_nombre": tech.nombre,
                        "total_completadas": len(reino.investigaciones_completadas),
                        "efectos": efectos_aplicados,
                    })

        # ==========================================
        # FINALIZACIÓN DEL TICK
        # ==========================================
        self.partida.turno_actual += 1

        resumen = {
            "turno": self.partida.turno_actual,
            "eventos": eventos,
            "total_eventos": len(eventos),
        }

        logger.info(
            f"✅ Tick {self.partida.turno_actual} completado | "
            f"{len(eventos)} evento(s) generado(s)"
        )

        return resumen
