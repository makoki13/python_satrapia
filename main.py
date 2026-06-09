# En tu main.py de FastAPI
from src.api.dependencias import inicializar_dependencias
from src.api.rutas.juego import router as juego_router

app = FastAPI(title="Motor de Juego - Fase 1")

@app.on_event("startup")
async def startup():
    from src.config.game_config import GameConfig
    from src.investigacion.arbol_investigaciones import ArbolInvestigaciones
    from src.investigacion.datos.bloque_1_alimentacion import TECNOLOGIAS_BLOQUE_1
    from src.investigacion.datos.bloque_2_extraccion import TECNOLOGIAS_BLOQUE_2
    from src.investigacion.datos.bloque_3_industria import TECNOLOGIAS_BLOQUE_3

    config = GameConfig()
    todas_techs = TECNOLOGIAS_BLOQUE_1 + TECNOLOGIAS_BLOQUE_2 + TECNOLOGIAS_BLOQUE_3
    arbol = ArbolInvestigaciones.construir(todas_techs)

    inicializar_dependencias(config, arbol)

app.include_router(juego_router)
