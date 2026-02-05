from dataclasses import dataclass, field
from typing import Dict, Any, Optional


@dataclass
class MemoryBlock:
    """
    Representa un bloque contiguo de memoria en el simulador.

    Attributes:
        start (int): Byte (o MB) donde inicia el bloque.
        size (int): Tamano del bloque.
        is_free (bool): Indica si el bloque esta disponible.
        process (Optional[str]): Identificador del proceso al que pertenece.
        block_id (int): Identificador unico para la UI (asignado automaticamente).
    """

    start: int
    size: int
    is_free: bool = True
    process: Optional[str] = None
    block_id: int = field(default=0)

    def assign(self, process_name: str):
        """Marca el bloque como ocupado."""
        self.is_free = False
        self.process = process_name

    def release(self):
        """Marca el bloque como libre."""
        self.is_free = True
        self.process = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el bloque a un dict listo para la UI."""
        return {
            "id": self.block_id,
            "start": self.start,
            "size": self.size,
            "is_free": self.is_free,
            "process": self.process,
            "label": "[Libre {} MB]".format(self.size)
            if self.is_free
            else "[{} {} MB]".format(self.process, self.size),
        }
