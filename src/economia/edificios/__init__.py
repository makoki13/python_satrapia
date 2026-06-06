# src/economia/edificios/__init__.py
from src.economia.edificios.cantera import Cantera
from src.economia.edificios.granja import Granja
from src.economia.edificios.mina_hierro import MinaHierro
from src.economia.edificios.mina_oro import MinaOro
from src.economia.edificios.serreria import Serreria

__all__ = ["Granja", "Serreria", "Cantera", "MinaHierro", "MinaOro"]
