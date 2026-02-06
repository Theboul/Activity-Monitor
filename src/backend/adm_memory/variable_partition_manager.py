"""
Gestor de Particiones Variables
Implementa algoritmos First Fit y Best Fit para particiones variables
Incluye división de particiones y fusión de huecos adyacentes
"""
from typing import List
from .MemoryProcess import MemoryProcess
from .Partition import Partition
from .algorithm import MemoryAlgorithm


class VariablePartitionManager:
    """
    Gestor de particiones variables
    Maneja la asignación de procesos usando particiones de tamaño variable
    Las particiones se dividen dinámicamente según el tamaño del proceso
    """
    
    def __init__(self):
        self.partitions: List[Partition] = []
        self._next_partition_id: int = 1
    
    def setup(self, total_memory: int, next_partition_id: int) -> int:
        """
        Configura las particiones variables (inicialmente un solo hueco libre)
        
        Args:
            total_memory: Memoria total en MB
            next_partition_id: ID inicial para las particiones
        
        Returns:
            El siguiente ID disponible después de crear la partición inicial
        """
        self.partitions.clear()
        self._next_partition_id = next_partition_id
        
        # Crear una sola partición libre con toda la memoria
        partition = Partition(
            id=self._next_partition_id,
            size=total_memory,
            start_address=0,
            is_free=True
        )
        self.partitions.append(partition)
        self._next_partition_id += 1
        
        return self._next_partition_id
    
    def first_fit(self, process: MemoryProcess) -> bool:
        """
        Algoritmo First Fit para particiones variables
        Asigna el proceso al PRIMER hueco libre suficientemente grande
        
        Args:
            process: Proceso a asignar
        
        Returns:
            True si se pudo asignar, False si no
        """
        for i, partition in enumerate(self.partitions):
            if partition.is_free and partition.size >= process.memory_size:
                # Si el hueco es del tamaño exacto, usarlo completo
                if partition.size == process.memory_size:
                    partition.assign_process(process, calculate_fragmentation=False)
                else:
                    # Dividir el hueco
                    self._split_partition(partition, process, i)
                
                return True
        
        return False
    
    def best_fit(self, process: MemoryProcess) -> bool:
        """
        Algoritmo Best Fit para particiones variables
        Asigna el proceso al hueco libre MÁS PEQUEÑO que lo pueda contener
        
        Args:
            process: Proceso a asignar
        
        Returns:
            True si se pudo asignar, False si no
        """
        best_partition = None
        best_index = -1
        min_waste = float('inf')
        
        # Buscar el mejor hueco (menor desperdicio)
        for i, partition in enumerate(self.partitions):
            if partition.is_free and partition.size >= process.memory_size:
                waste = partition.size - process.memory_size
                if waste < min_waste:
                    min_waste = waste
                    best_partition = partition
                    best_index = i
        
        # Si se encontró un hueco adecuado, asignar el proceso
        if best_partition:
            # Si el hueco es del tamaño exacto, usarlo completo
            if best_partition.size == process.memory_size:
                best_partition.assign_process(process, calculate_fragmentation=False)
            else:
                # Dividir el hueco
                self._split_partition(best_partition, process, best_index)
            
            return True
        
        return False
    
    def assign_process(self, process: MemoryProcess, algorithm: MemoryAlgorithm) -> bool:
        """
        Asigna un proceso usando el algoritmo especificado
        
        Args:
            process: Proceso a asignar
            algorithm: Algoritmo a utilizar
        
        Returns:
            True si se pudo asignar, False si no
        """
        if algorithm == MemoryAlgorithm.FIRST_FIT:
            return self.first_fit(process)
        else:  # BEST_FIT
            return self.best_fit(process)
    
    def _split_partition(self, partition: Partition, process: MemoryProcess, index: int):
        """
        Divide una partición libre al asignar un proceso
        Crea una partición del tamaño exacto del proceso y ajusta el hueco restante
        
        Args:
            partition: Partición a dividir
            process: Proceso a asignar
            index: Índice de la partición en la lista
        """
        # Crear nueva partición para el proceso (tamaño exacto)
        process_partition = Partition(
            id=self._next_partition_id,
            size=process.memory_size,
            start_address=partition.start_address,
            is_free=False,
            process=process
        )
        self._next_partition_id += 1
        
        # Actualizar dirección del proceso
        process.partition_id = process_partition.id
        process.start_address = process_partition.start_address
        
        # Ajustar el hueco restante
        partition.size -= process.memory_size
        partition.start_address += process.memory_size
        
        # Insertar la nueva partición del proceso antes del hueco
        self.partitions.insert(index, process_partition)
    
    def release_process(self, partition_id: int):
        """
        Libera un proceso de una partición y fusiona huecos adyacentes
        
        Args:
            partition_id: ID de la partición a liberar
        """
        for partition in self.partitions:
            if partition.id == partition_id and not partition.is_free:
                partition.release_process()
                self._merge_adjacent_holes()
                return
    
    def _merge_adjacent_holes(self):
        """
        Fusiona huecos libres contiguos
        Esto reduce la fragmentación externa
        """
        if len(self.partitions) <= 1:
            return
        
        merged = True
        while merged:
            merged = False
            i = 0
            while i < len(self.partitions) - 1:
                current = self.partitions[i]
                next_partition = self.partitions[i + 1]
                
                # Si ambas particiones están libres y son contiguas, fusionarlas
                if current.is_free and next_partition.is_free:
                    if current.end_address == next_partition.start_address:
                        # Expandir la partición actual
                        current.size += next_partition.size
                        
                        # Eliminar la siguiente partición
                        self.partitions.pop(i + 1)
                        
                        merged = True
                        continue
                
                i += 1
    
    def compact_memory(self, total_memory: int) -> int:
        """
        Compacta la memoria moviendo todos los procesos al inicio
        Elimina la fragmentación externa dejando un solo hueco al final
        
        Args:
            total_memory: Memoria total del sistema
        
        Returns:
            Espacio libre después de la compactación en MB
        """
        # Separar particiones ocupadas
        occupied = [p for p in self.partitions if not p.is_free]
        
        if not occupied:
            return total_memory  # Toda la memoria está libre
        
        # Limpiar lista de particiones
        self.partitions.clear()
        
        # Reorganizar procesos al inicio
        current_address = 0
        for partition in occupied:
            # Actualizar dirección de inicio
            partition.start_address = current_address
            
            # Actualizar dirección del proceso
            if partition.process:
                partition.process.start_address = current_address
            
            self.partitions.append(partition)
            current_address += partition.size
        
        # Crear un solo hueco libre al final
        free_space = total_memory - current_address
        if free_space > 0:
            free_partition = Partition(
                id=self._next_partition_id,
                size=free_space,
                start_address=current_address,
                is_free=True
            )
            self.partitions.append(free_partition)
            self._next_partition_id += 1
        
        return free_space
    
    def clear_assignments(self):
        """Libera todas las particiones y fusiona huecos"""
        for partition in self.partitions:
            if not partition.is_free:
                partition.release_process()
        
        self._merge_adjacent_holes()
    
    def calculate_fragmentation(self) -> dict:
        """
        Calcula la fragmentación externa
        
        Returns:
            Dict con información de fragmentación externa
        """
        free_holes = [p.size for p in self.partitions if p.is_free]
        
        if not free_holes:
            return {
                'external_fragmentation': 0,
                'num_holes': 0,
                'largest_hole': 0,
                'total_free': 0
            }
        
        total_free = sum(free_holes)
        largest_hole = max(free_holes)
        num_holes = len(free_holes)
        external_frag = total_free - largest_hole
        
        return {
            'external_fragmentation': external_frag,
            'num_holes': num_holes,
            'largest_hole': largest_hole,
            'total_free': total_free
        }
    
    def get_partitions(self) -> List[Partition]:
        """Retorna la lista de particiones"""
        return self.partitions
