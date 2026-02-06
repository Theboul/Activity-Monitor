"""
Clase para representar un proceso en memoria (semi-simulado)
"""
from dataclasses import dataclass
from typing import Optional, Dict, Any


@dataclass
class MemoryProcess:
    """
    Representa un proceso en memoria
    
    Combina datos reales del sistema (PID, nombre) con simulación
    de asignación de memoria (partition_id, start_address)
    """
    pid: int                          # PID real del proceso del sistema
    name: str                         # Nombre real del proceso
    memory_size: int                  # Tamaño en MB (capturado o ajustado por usuario)
    partition_id: Optional[int] = None    # ID de la partición donde está asignado
    start_address: Optional[int] = None   # Dirección de inicio en MB
    
    def __post_init__(self):
        """Validación de datos al crear el proceso"""
        if self.pid <= 0:
            raise ValueError(f"PID inválido: {self.pid}. Debe ser un número positivo")
        
        if not self.name or not isinstance(self.name, str) or self.name.strip() == "":
            raise ValueError("El nombre del proceso no puede estar vacío")
        
        if self.memory_size <= 0:
            raise ValueError(f"Tamaño de memoria inválido: {self.memory_size}. Debe ser mayor a 0 MB")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el proceso a diccionario para la UI
        
        Returns:
            Dict con información del proceso
        """
        return {
            'pid': self.pid,
            'name': self.name,
            'memory_size': self.memory_size,
            'partition_id': self.partition_id,
            'start_address': self.start_address,
            'is_assigned': self.partition_id is not None
        }
    
    def is_assigned(self) -> bool:
        """
        Verifica si el proceso está asignado a una partición
        
        Returns:
            True si está asignado, False si no
        """
        return self.partition_id is not None
    
    def unassign(self):
        """Desasigna el proceso de su partición"""
        self.partition_id = None
        self.start_address = None
