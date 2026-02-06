"""
Clase para representar una partición de memoria
"""
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, TYPE_CHECKING

# Evitar imports circulares
if TYPE_CHECKING:
    from .MemoryProcess import MemoryProcess


@dataclass
class Partition:
    """
    Representa una partición de memoria (fija o variable)
    
    Una partición es un bloque continuo de memoria que puede estar
    libre u ocupado por un proceso.
    """
    id: int                                   # Identificador único de la partición
    size: int                                 # Tamaño en MB
    start_address: int                        # Dirección de inicio en MB
    is_free: bool = True                      # ¿Está libre?
    process: Optional['MemoryProcess'] = None  # Proceso asignado (None si está libre)
    internal_fragmentation: int = 0           # Fragmentación interna (solo para fijas)
    
    def __post_init__(self):
        """Validación de datos al crear la partición"""
        if self.size <= 0:
            raise ValueError(f"Tamaño de partición inválido: {self.size}. Debe ser mayor a 0 MB")
        
        if self.start_address < 0:
            raise ValueError(f"Dirección de inicio inválida: {self.start_address}. Debe ser >= 0")
    
    @property
    def end_address(self) -> int:
        """
        Calcula la dirección final de la partición
        
        Returns:
            Dirección final en MB
        """
        return self.start_address + self.size
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte la partición a diccionario para la UI
        
        Returns:
            Dict con información de la partición
        """
        return {
            'id': self.id,
            'size': self.size,
            'start_address': self.start_address,
            'end_address': self.end_address,
            'is_free': self.is_free,
            'process': self.process.to_dict() if self.process else None,
            'internal_fragmentation': self.internal_fragmentation
        }
    
    def assign_process(self, process: 'MemoryProcess', calculate_fragmentation: bool = False):
        """
        Asigna un proceso a esta partición
        
        Args:
            process: Proceso a asignar
            calculate_fragmentation: Si es True, calcula fragmentación interna (para fijas)
        
        Raises:
            ValueError: Si la partición no está libre o el proceso no cabe
        """
        if not self.is_free:
            raise ValueError(f"La partición {self.id} ya está ocupada")
        
        if process.memory_size > self.size:
            raise ValueError(
                f"El proceso {process.name} ({process.memory_size} MB) "
                f"no cabe en la partición {self.id} ({self.size} MB)"
            )
        
        # Asignar proceso
        self.process = process
        self.is_free = False
        
        # Actualizar datos del proceso
        process.partition_id = self.id
        process.start_address = self.start_address
        
        # Calcular fragmentación interna si es necesario (particiones fijas)
        if calculate_fragmentation:
            self.internal_fragmentation = self.size - process.memory_size
    
    def release_process(self):
        """
        Libera el proceso de esta partición
        
        Raises:
            ValueError: Si la partición ya está libre
        """
        if self.is_free:
            raise ValueError(f"La partición {self.id} ya está libre")
        
        # Desasignar proceso
        if self.process:
            self.process.unassign()
        
        self.process = None
        self.is_free = True
        self.internal_fragmentation = 0
    
    def get_used_space(self) -> int:
        """
        Obtiene el espacio usado en la partición
        
        Returns:
            Espacio usado en MB (0 si está libre)
        """
        return self.process.memory_size if self.process else 0
    
    def get_free_space(self) -> int:
        """
        Obtiene el espacio libre en la partición
        
        Returns:
            Espacio libre en MB
        """
        if self.is_free:
            return self.size
        return self.size - self.get_used_space()
