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

    def _procesar_disparadores_automaticos(self) -> list[dict]:  # noqa: C901
        """
        Fase 1c: Disparadores Automáticos de Transporte.
        Crea transportes SOLO cuando el silo alcanza el 100% de capacidad.
        Envía todo el stock disponible (vaciado completo por desbordamiento).
        """
        eventos = []

        if self.partida.gestor_transportes is None:
            return eventos

        for ciudad in self.partida.ciudades:
            if not hasattr(ciudad, 'almacen') or not ciudad.almacen:
                continue

            # Contar transportes activos salientes de esta ciudad
            transportes_salientes = sum(
                1 for t in self.partida.gestor_transportes._por_id.values()
                if t.origen == ciudad.ubicacion
            )

            if transportes_salientes >= self.config.auto_transport_max_active_per_city:
                continue

                        # ✅ CORREGIDO: Usar API pública en lugar de atributo privado
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
                    # ✅ CORREGIDO: Firma real de crear_transporte
                    # - mapa va primero
                    # - tipo explícito como TipoTransporte.RECURSOS
                    # - devuelve tupla (exito, mensaje, transporte)
                    exito, msg_creacion, transporte = self.partida.gestor_transportes.crear_transporte(
                        mapa=self.partida.mapa,
                        origen=ciudad.ubicacion,
                        destino=destino_ciudad.ubicacion,
                        tipo=TipoTransporte.RECURSOS,
                        tipo_recurso=tipo_recurso,
                        cantidad=cantidad_a_enviar,
                        propietario_id=reino.nombre,
                    )

                    if not exito or transporte is None:
                        logger.warning(f"No se pudo crear transporte automático desde {ciudad.nombre}: {msg_creacion}")
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
                            "transporte_id": transporte.id
                        })
                    else:
                        # Error crítico: transporte creado pero recurso no retirado
                        logger.error(f"Inconsistencia logística en {ciudad.nombre}: {msg_retiro}")
                        self.partida.gestor_transportes.eliminar(transporte.id)

                except Exception as e:
                    logger.warning(f"Error inesperado en transporte automático desde {ciudad.nombre}: {e}")

        return eventos

    async def ejecutar(self) -> dict:  # noqa: C901
        """
        Ejecuta un tick completo del servidor.

        Returns:
            Resumen del tick con eventos generados (para broadcast WS).
        """
        eventos: list[dict] = []
        todos_eventos = []

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
        if self.partida.gestor_transportes is not None:
            llegadas = self.partida.gestor_transportes.avanzar_todos(self.partida.mapa)

            for evento_llegada in llegadas:
                t = evento_llegada.transporte

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

        # --- FASE 2a: DISPARADORES AUTOMÁTICOS (NUEVO) ---
        eventos_auto = self._procesar_disparadores_automaticos()
        todos_eventos.extend(eventos_auto)

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
