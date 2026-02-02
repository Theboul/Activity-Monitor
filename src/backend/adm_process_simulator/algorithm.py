from enum import Enum

class Algorithm(Enum):
    """Algoritmos de planificación disponibles"""
    FIFO = "FIFO (First Come First Served)"
    SJF = "SJF (Shortest Job First)"
    ROUND_ROBIN = "Round Robin"