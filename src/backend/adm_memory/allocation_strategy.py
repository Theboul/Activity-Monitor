from enum import Enum


class AllocationStrategy(Enum):
    """Algoritmos de asignacion soportados para la memoria simulada."""

    FIRST_FIT = "First Fit"
    BEST_FIT = "Best Fit"

    @classmethod
    def from_string(cls, value: str) -> "AllocationStrategy":
        """
        Convierte una cadena (por ejemplo ingresada en la UI) a la estrategia correspondiente.

        Args:
            value: Nombre legible de la estrategia.

        Returns:
            AllocationStrategy: enum correspondiente.

        Raises:
            ValueError: si no hay coincidencias.
        """
        normalized = (value or "").strip().lower()
        for strategy in cls:
            if strategy.value.lower() == normalized or strategy.name.lower() == normalized:
                return strategy
        raise ValueError(f"Estrategia de asignacion desconocida: {value}")
