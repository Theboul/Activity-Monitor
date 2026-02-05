"""
Logica central para la administracion de memoria simulada.

Este modulo transforma el ejemplo proporcionado por el usuario en una clase
reutilizable y alineada con el estilo del proyecto.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .allocation_strategy import AllocationStrategy
from .memory_block import MemoryBlock


class MemoryManager:
    """Gestiona la lista de bloques y aplica las estrategias de asignacion."""

    def __init__(self, total_size: int):
        if total_size <= 0:
            raise ValueError("El tamano total de memoria debe ser positivo")
        self.total_size = total_size
        self._next_block_id = 1
        self._blocks: List[MemoryBlock] = [self._create_block(0, total_size)]

    # --------------------------------------------------------------------- #
    # Propiedades de solo lectura

    @property
    def blocks(self) -> List[MemoryBlock]:
        """Devuelve una copia superficial de los bloques para mantener encapsulacion."""
        return list(self._blocks)

    # --------------------------------------------------------------------- #
    # Operaciones publicas

    def allocate(
        self,
        process_name: str,
        size: int,
        strategy: AllocationStrategy = AllocationStrategy.FIRST_FIT,
    ) -> bool:
        """
        Intenta asignar memoria al proceso indicado usando la estrategia deseada.

        Args:
            process_name: Identificador del proceso.
            size: Tamano solicitado.
            strategy: Algoritmo a utilizar.

        Returns:
            True si se asigno memoria, False en caso contrario.
        """
        process_name = (process_name or "").strip()
        if not process_name:
            raise ValueError("El nombre del proceso no puede estar vacio")
        if size <= 0:
            raise ValueError("El tamano solicitado debe ser positivo")
        if self._process_exists(process_name):
            raise ValueError(f"El proceso {process_name} ya tiene memoria asignada")

        index = self._find_block_index(size, strategy)
        if index is None:
            return False

        self._split_and_assign(index, size, process_name)
        return True

    def release(self, process_name: str) -> bool:
        """Libera los bloques asociados al proceso y compacta si es necesario."""
        released = False
        for block in self._blocks:
            if not block.is_free and block.process == process_name:
                block.release()
                released = True

        if released:
            self._merge_free_blocks()
        return released

    def compact(self):
        """Fusiona todos los bloques libres contiguos."""
        self._merge_free_blocks()

    def reset(self):
        """Reinicia la memoria al estado inicial (todo libre)."""
        self._blocks = [self._create_block(0, self.total_size)]

    def get_snapshot(self) -> Dict[str, object]:
        """Retorna un resumen listo para mostrarse en la UI."""
        blocks_data = [block.to_dict() for block in self._blocks]
        used = sum(block.size for block in self._blocks if not block.is_free)
        free = self.total_size - used
        largest_free = max((block.size for block in self._blocks if block.is_free), default=0)

        return {
            "blocks": blocks_data,
            "summary": {
                "total": self.total_size,
                "used": used,
                "free": free,
                "largest_free_block": largest_free,
                "fragmentation": len([b for b in self._blocks if b.is_free]),
            },
        }

    # --------------------------------------------------------------------- #
    # Helpers internos

    def _create_block(self, start: int, size: int, is_free: bool = True) -> MemoryBlock:
        block = MemoryBlock(start=start, size=size, is_free=is_free, block_id=self._next_block_id)
        self._next_block_id += 1
        return block

    def _process_exists(self, process_name: str) -> bool:
        return any(not block.is_free and block.process == process_name for block in self._blocks)

    def _find_block_index(
        self,
        size: int,
        strategy: AllocationStrategy,
    ) -> Optional[int]:
        """Devuelve el indice del bloque que cumple con la estrategia solicitada."""
        candidate_index: Optional[int] = None

        if strategy == AllocationStrategy.FIRST_FIT:
            for idx, block in enumerate(self._blocks):
                if block.is_free and block.size >= size:
                    candidate_index = idx
                    break
        elif strategy == AllocationStrategy.BEST_FIT:
            best_size = None
            for idx, block in enumerate(self._blocks):
                if block.is_free and block.size >= size:
                    if best_size is None or block.size < best_size:
                        best_size = block.size
                        candidate_index = idx
        else:
            raise ValueError(f"Estrategia no soportada: {strategy}")

        return candidate_index

    def _split_and_assign(self, index: int, size: int, process_name: str):
        """Divide un bloque libre y asigna la primera porcion al proceso."""
        block = self._blocks[index]
        if not block.is_free or block.size < size:
            raise RuntimeError("El bloque seleccionado ya no esta disponible")

        remaining_size = block.size - size
        block.size = size
        block.assign(process_name)

        if remaining_size > 0:
            new_block = self._create_block(block.start + size, remaining_size, True)
            self._blocks.insert(index + 1, new_block)

    def _merge_free_blocks(self):
        """Combina bloques libres adyacentes."""
        i = 0
        while i < len(self._blocks) - 1:
            current_block = self._blocks[i]
            next_block = self._blocks[i + 1]
            if current_block.is_free and next_block.is_free:
                current_block.size += next_block.size
                del self._blocks[i + 1]
            else:
                i += 1
