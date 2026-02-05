"""
Paquete de administracion de memoria para el Activity Monitor.

Expone utilidades para simular estrategias de asignacion dinamica de memoria
mediante bloques libres/ocupados, similar al simulador de procesos.
"""

from .allocation_strategy import AllocationStrategy
from .memory_block import MemoryBlock
from .memory_manager import MemoryManager
from .memory_monitor import MemoryMonitor

__all__ = [
    "AllocationStrategy",
    "MemoryBlock",
    "MemoryManager",
    "MemoryMonitor",
]
