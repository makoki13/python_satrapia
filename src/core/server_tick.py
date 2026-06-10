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
    3. Disparadores: Transporte automático desde ciudades y edificios productivos
    4. Investigación: Avance del laboratorio del reino + Aplicación de efectos

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

    def _procesar_disparadores_automaticos(self) -> list[dict]:  # noqa: C901
        """
        Fase 2a: Disparadores Automáticos de Transporte.
        Crea transportes SOLO cuando el silo alcanza el 100% de capacidad.
        Envía todo el stock disponible (vaciado completo por desbordamiento).

        Procesa tanto almacenes de ciudades como almacenes locales de edificios
        productivos (granjas, minas, etc.).
        """
        eventos: list[dict] = []

        if self.partida.gestor_transportes is None:
            return eventos

        # ==========================================
        # DISPARADORES DESDE CIUDADES
        # ==========================================
        for ciudad in self.partida.ciudades:
            if not hasattr(ciudad, "almacen") or not ciudad.almacen:
                continue

            # Contar transportes activos salientes de esta ciudad
            transportes_salientes = sum(
                1
                for t in self.partida.gestor_transportes._por_id.values()
                if t.origen == ciudad.ubicacion
            )

            if transportes_salientes >= self.config.auto_transport_max_active_per_city:
                continue

            for tipo_recurso, silo in ciudad.almacen.silos_items:
                capacidad = silo.get_capacidad_maxima(self.config)

                # Umbral 100%: solo actuar cuando está completamente lleno
                if silo.stock_actual < capacidad:
                    continue

                cantidad_a_enviar = silo.stock_actual

                if cantidad_a_enviar < self.config.auto_transport_min_amount:
                    continue

                # Determinar destino (Capital del Reino)
                reino = ciudad.reino_propietario
                destino_ciudad = None
                if reino and reino.capital and reino.capital != ciudad:
                    destino_ciudad = reino.capital

                if not destino_ciudad:
                    continue

                try:
                    exito, msg_creacion, transporte = (
                        self.partida.gestor_transportes.crear_transporte(
                            mapa=self.partida.mapa,
                            origen=ciudad.ubicacion,
                            destino=destino_ciudad.ubicacion,
                            tipo=TipoTransporte.RECURSOS,
                            tipo_recurso=tipo_recurso,
                            cantidad=cantidad_a_enviar,
                            propietario_id=reino.nombre,
                        )
                    )

                    if not exito or transporte is None:
                        logger.warning(
                            "No se pudo crear transporte automático desde %s: %s",
                            ciudad.nombre,
                            msg_creacion,
                        )
                        continue

                    # Retirar TODO el stock inmediatamente
                    exito_retiro, _, msg_retiro = ciudad.almacen.retirar_recurso(
                        tipo_recurso, cantidad_a_enviar
                    )

                    if exito_retiro:
                        eventos.append({
                            "tipo": "transporte_automatico_creado",
                            "origen": ciudad.nombre,
                            "destino": destino_ciudad.nombre,
                            "recurso": tipo_recurso.value,
                            "cantidad": cantidad_a_enviar,
                            "transporte_id": transporte.id,
                        })
                    else:
                        logger.error(
                            "Inconsistencia logística en %s: %s",
                            ciudad.nombre,
                            msg_retiro,
                        )
                        self.partida.gestor_transportes.eliminar(transporte.id)

                except Exception as e:
                    logger.warning(
                        "Error inesperado en transporte automático desde %s: %s",
                        ciudad.nombre,
                        e,
                    )

        # ==========================================
        # DISPARADORES DESDE EDIFICIOS PRODUCTIVOS
        # ==========================================
        for ciudad in self.partida.ciudades:
            for edificio in ciudad.obtener_edificios_productivos():
                if edificio.almacen is None or edificio.coordenada is None:
                    continue

                # Contar transportes activos salientes de este edificio
                transportes_salientes = sum(
                    1
                    for t in self.partida.gestor_transportes._por_id.values()
                    if t.origen == edificio.coordenada
                )

                if transportes_salientes >= self.config.auto_transport_max_active_per_city:
                    continue

                for tipo_recurso, silo in edificio.almacen.silos_items:
                    capacidad = silo.get_capacidad_maxima(self.config)

                    if silo.stock_actual < capacidad:
                        continue

                    cantidad_a_enviar = silo.stock_actual

                    if cantidad_a_enviar < self.config.auto_transport_min_amount:
                        continue

                    # Destino siempre es la ciudad propietaria
                    destino_ciudad = ciudad

                    try:
                        exito, msg_creacion, transporte = (
                            self.partida.gestor_transportes.crear_transporte(
                                mapa=self.partida.mapa,
                                origen=edificio.coordenada,
                                destino=destino_ciudad.ubicacion,
                                tipo=TipoTransporte.RECURSOS,
                                tipo_recurso=tipo_recurso,
                                cantidad=cantidad_a_enviar,
                                propietario_id=ciudad.reino_propietario.nombre,
                            )
                        )

                        if not exito or transporte is None:
                            logger.warning(
                                "No se pudo crear transporte automático desde %s: %s",
                                edificio.nombre,
                                msg_creacion,
                            )
                            continue

                        # Retirar stock del almacén del edificio
                        exito_retiro, _, msg_retiro = edificio.almacen.retirar_recurso(
                            tipo_recurso, cantidad_a_enviar
                        )

                        if exito_retiro:
                            eventos.append({
                                "tipo": "transporte_automatico_creado",
                                "origen": f"{edificio.nombre} ({edificio.coordenada})",
                                "destino": destino_ciudad.nombre,
                                "recurso": tipo_recurso.value,
                                "cantidad": cantidad_a_enviar,
                                "transporte_id": transporte.id,
                            })
                        else:
                            logger.error(
                                "Inconsistencia logística en %s: %s",
                                edificio.nombre,
                                msg_retiro,
                            )
                            self.partida.gestor_transportes.eliminar(transporte.id)

                    except Exception as e:
                        logger.warning(
                            "Error inesperado en transporte automático desde %s: %s",
                            edificio.nombre,
                            e,
                        )

        return eventos

    async def ejecutar(self) -> dict:  # noqa: C901
        """
        Ejecuta un tick completo del servidor.

        Returns:
            Resumen del tick con eventos generados (para broadcast WS).
        """
        eventos: list[dict] = []

        logger.debug("⏱️ Iniciando tick %d", self.partida.turno_actual + 1)

        # ==========================================
        # FASE 1: ECONOMÍA (Por ciudad)
        # ==========================================
        for ciudad in self.partida.ciudades:
            # 1a. Producción de edificios productivos
            for edificio in ciudad.obtener_edificios_productivos():
                # ✅ Usar almacén local del edificio si existe;
                #    si no, fallback al almacén de la ciudad
                almacen_destino = (
                    edificio.almacen
                    if edificio.almacen is not None
                    else ciudad.almacen
                )

                exito, cantidad, msg = edificio.producir(almacen_destino, self.config)
                if not exito and "agotada" in msg.lower():
                    eventos.append({
                        "tipo": "alerta_fuente_agotada",
                        "ciudad": ciudad.nombre,
                        "mensaje": msg,
                    })
                elif exito and cantidad > 0:
                    logger.debug("   🏭 %s", msg)

            # 1b. Recaudación de impuestos en el Palacio
            if ciudad.palacio:
                exito_imp, oro, msg_imp = ciudad.palacio.recaudar_impuestos(self.config)
                if exito_imp and oro > 0:
                    logger.debug("   💰 %s", msg_imp)
                    eventos.append({
                        "tipo": "impuestos_recaudados",
                        "ciudad": ciudad.nombre,
                        "oro": oro,
                        "poblacion": ciudad.palacio.get_poblacion(),
                    })

        # ==========================================
        # FASE 2: LOGÍSTICA (Global)
        # ==========================================
        if self.partida.gestor_transportes is not None:
            llegadas = self.partida.gestor_transportes.avanzar_todos(self.partida.mapa)

            for evento_llegada in llegadas:
                t = evento_llegada.transporte

                # Procesar transferencia según tipo de transporte
                if t.tipo == TipoTransporte.RECURSOS and t.tipo_recurso:
                    ciudad_destino = self.partida.obtener_ciudad_en(t.destino)
                    if ciudad_destino:
                        exito_transf, real, msg_transf = (
                            ciudad_destino.almacen.agregar_recurso(
                                t.tipo_recurso, t.cantidad, self.config
                            )
                        )
                        logger.info(
                            "📦 Transferencia en %s: %s",
                            ciudad_destino.nombre,
                            msg_transf,
                        )
                        eventos.append({
                            "tipo": "transporte_recursos_llegado",
                            "ciudad": ciudad_destino.nombre,
                            "recurso": t.tipo_recurso.value,
                            "cantidad": real,
                        })
                    else:
                        logger.warning(
                            "⚠️ Transporte %s llegó a %s pero no hay ciudad.",
                            t.id,
                            t.destino,
                        )

                elif t.tipo == TipoTransporte.EJERCITO:
                    logger.info("⚔️ Ejército llegado a %s (despliegue pendiente)", t.destino)
                    eventos.append({
                        "tipo": "ejercito_desplegado",
                        "destino": str(t.destino),
                        "metadata": t.metadata,
                    })

                elif t.tipo == TipoTransporte.TRIBU:
                    logger.info("🏕️ Tribu migró a %s", t.destino)
                    eventos.append({
                        "tipo": "tribu_migrada",
                        "destino": str(t.destino),
                        "propietario": t.propietario_id,
                    })

                elif t.tipo == TipoTransporte.COMERCIO:
                    logger.info("🤝 Comercio completado en %s", t.destino)

                # Eliminar transporte tras procesamiento
                self.partida.gestor_transportes.eliminar(t.id)

        # --- FASE 2a: DISPARADORES AUTOMÁTICOS ---
        eventos_auto = self._procesar_disparadores_automaticos()
        eventos.extend(eventos_auto)

        # ==========================================
        # FASE 3: INVESTIGACIÓN (Por reino)
        # ==========================================
        for reino in self.partida.reinos:
            if reino.laboratorio is not None and reino.laboratorio.esta_investigando:
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
                            nuevo_valor = param.calcular_valor(
                                reino.investigaciones_completadas
                            )
                            efectos_aplicados.append({
                                "parametro": efecto.id_parametro,
                                "nombre": param.nombre,
                                "nuevo_valor": round(nuevo_valor, 2),
                            })
                            logger.info(
                                "📈 [%s] %s: %.2f",
                                reino.nombre,
                                param.nombre,
                                nuevo_valor,
                            )
                        except KeyError:
                            logger.error(
                                "❌ Parámetro '%s' no encontrado al completar '%s'",
                                efecto.id_parametro,
                                tech_id,
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
            "✅ Tick %d completado | %d evento(s) generado(s)",
            self.partida.turno_actual,
            len(eventos),
        )

        return resumen
