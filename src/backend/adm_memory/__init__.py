"""
Módulo de administración de memoria
Simula asignación de procesos con particiones fijas y variables
"""
from .MemoryProcess import MemoryProcess
from .Partition import Partition
from .algorithm import MemoryAlgorithm, PartitionType
from .memory_monitor import MemoryMonitor
from .fixed_partition_manager import FixedPartitionManager
from .variable_partition_manager import VariablePartitionManager

__all__ = [
    'MemoryProcess',
    'Partition',
    'MemoryAlgorithm',
    'PartitionType',
    'MemoryMonitor',
    'FixedPartitionManager',
    'VariablePartitionManager'
]
