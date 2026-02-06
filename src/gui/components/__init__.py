# Paquete de componentes de la GUI

from .cpu_card import CPUCard
from .ram_card import RAMCard
from .storage_card import StorageCard
from .gantt_chart import GanttChart
from .memory_vector import MemoryVector
from .memory_stats_panel import MemoryStatsPanel
from .partition_block import PartitionBlock

__all__ = [
    'CPUCard',
    'RAMCard',
    'StorageCard',
    'GanttChart',
    'MemoryVector',
    'MemoryStatsPanel',
    'PartitionBlock'
]
