from dataclasses import dataclass, field
from typing import Dict, Any, Optional

@dataclass
class Process:
    """Representa un proceso semi-simulado"""
    pid: int
    name: str
    arrival_time: float
    burst_time: int  # Tiempo de ráfaga (simulado)
    remaining_time: int = field(init=False)
    waiting_time: int = 0
    turnaround_time: int = 0
    completion_time: int = 0
    start_time: Optional[int] = None
    
    def __post_init__(self):
        """Inicializa el tiempo restante igual al burst time"""
        self.remaining_time = self.burst_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte el proceso a diccionario para la UI"""
        return {
            'pid': self.pid,
            'name': self.name,
            'arrival_time': round(self.arrival_time, 2),
            'burst_time': self.burst_time,
            'remaining_time': self.remaining_time,
            'waiting_time': self.waiting_time,
            'turnaround_time': self.turnaround_time,
            'completion_time': self.completion_time,
            'start_time': self.start_time
        }