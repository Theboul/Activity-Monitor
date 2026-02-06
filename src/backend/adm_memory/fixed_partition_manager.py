"""
Gestor de Particiones Fijas
Implementa el algoritmo First Fit para particiones fijas del mismo tamaño
"""
from typing import List
from .MemoryProcess import MemoryProcess
from .Partition import Partition
from .algorithm import MemoryAlgorithm


class FixedPartitionManager:
    """
    Gestor de particiones fijas
    Maneja la asignación de procesos usando particiones de tamaño fijo
    TODAS las particiones tienen el mismo tamaño
    Solo soporta First Fit (ya que Best Fit no tiene sentido con tamaños idénticos)
    """
    
    def __init__(self):
        self.partitions: List[Partition] = []
    
    def setup(self, partition_size: int, num_partitions: int, next_partition_id: int) -> int:
        """
        Configura las particiones fijas (todas del mismo tamaño)
        
        Args:
            partition_size: Tamaño de cada partición en MB
            num_partitions: Número de particiones a crear
            next_partition_id: ID inicial para las particiones
        
        Returns:
            El siguiente ID disponible después de crear las particiones
        """
        self.partitions.clear()
        current_address = 0
        current_id = next_partition_id
        
        for _ in range(num_partitions):
            partition = Partition(
                id=current_id,
                size=partition_size,
                start_address=current_address,
                is_free=True
            )
            self.partitions.append(partition)
            current_id += 1
            current_address += partition_size
    def first_fit(self, process: MemoryProcess) -> bool:
        """
        Algoritmo First Fit para particiones fijas
        Asigna el proceso a la PRIMERA partición libre suficientemente grande
        
        Nota: Como todas las particiones tienen el mismo tamaño,
        este es el único algoritmo necesario
        
        Args:
            process: Proceso a asignar
        
        Returns:
            True si se pudo asignar, False si no
        """
        for partition in self.partitions:
            if partition.is_free and partition.size >= process.memory_size:
                partition.assign_process(process, calculate_fragmentation=True)
                return True
        
        return False
    
    def assign_process(self, process: MemoryProcess) -> bool:
        """
        Asigna un proceso usando First Fit (el único algoritmo válido para particiones fijas)
        
        Args:
            process: Proceso a asignar
        
        Returns:
            True si se pudo asignar, False si no
        """
        return self.first_fit(process)
    
    def release_process(self, partition_id: int):
        """
        Libera un proceso de una partición
        
        Args:
            partition_id: ID de la partición a liberar
        """
        for partition in self.partitions:
            if partition.id == partition_id and not partition.is_free:
                partition.release_process()
                return
    
    def clear_assignments(self):
        """Libera todas las particiones"""
        for partition in self.partitions:
            if not partition.is_free:
                partition.release_process()
    
    def calculate_fragmentation(self) -> int:
        """
        Calcula la fragmentación interna total
        
        Returns:
            Fragmentación interna en MB
        """
        return sum(p.internal_fragmentation for p in self.partitions if not p.is_free)
    
    def get_partitions(self) -> List[Partition]:
        """Retorna la lista de particiones"""
        return self.partitions
