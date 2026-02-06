"""
Algoritmos de asignación de memoria
Define los algoritmos disponibles y tipos de particionamiento
"""
from enum import Enum


class MemoryAlgorithm(Enum):
    """Algoritmos de asignación de memoria disponibles"""
    FIRST_FIT = "First Fit"
    BEST_FIT = "Best Fit"


class PartitionType(Enum):
    """Tipos de particionamiento de memoria"""
    FIXED = "Particiones Fijas"
    VARIABLE = "Particiones Variables"
