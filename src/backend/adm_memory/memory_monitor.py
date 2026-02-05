"""
Monitor de memoria virtual inspirado en adm_process_simulator.
"""
from __future__ import annotations

import threading
from typing import Dict, Any, List

import psutil

from ..base_monitor import BaseMonitor
from .allocation_strategy import AllocationStrategy
from .memory_manager import MemoryManager


class MemoryMonitor(BaseMonitor):
    """
    Proporciona un hilo de monitoreo (para callbacks en la UI) y metodos
    imperativos para asignar/liberar bloques de memoria simulada.
    """

    def __init__(self, total_memory: int | None = None, update_interval: float = 1.5):
        super().__init__(update_interval)
        initial_total = total_memory or self._get_system_total_mb()
        self._manager = MemoryManager(initial_total)
        self._manager_lock = threading.Lock()

    # ------------------------------------------------------------------ #
    # API publica que podra usar la UI

    def collect_data(self) -> Dict[str, Any]:
        """Implementacion requerida por BaseMonitor."""
        with self._manager_lock:
            snapshot = self._manager.get_snapshot()
        snapshot["system_ram"] = self._get_system_ram()
        return snapshot

    def allocate_process(
        self,
        process_name: str,
        size: int,
        strategy: AllocationStrategy = AllocationStrategy.FIRST_FIT,
    ) -> Dict[str, Any]:
        """
        Asigna memoria usando la estrategia solicitada.

        Returns:
            Dict con claves 'success' y 'message' para la UI.
        """
        with self._manager_lock:
            allocated = self._manager.allocate(process_name, size, strategy)

        if allocated:
            return {"success": True, "message": f"Proceso {process_name} asignado ({strategy.value})"}
        return {
            "success": False,
            "message": f"No hay bloques disponibles para {process_name} ({size} MB)",
        }

    def release_process(self, process_name: str) -> Dict[str, Any]:
        """Libera la memoria asociada al proceso indicado."""
        with self._manager_lock:
            released = self._manager.release(process_name)

        if released:
            return {"success": True, "message": f"Proceso {process_name} liberado"}
        return {"success": False, "message": f"Proceso {process_name} no encontrado"}

    def compact_memory(self) -> Dict[str, Any]:
        """Fuerza la compactacion manual."""
        with self._manager_lock:
            self._manager.compact()
        return {"success": True, "message": "Memoria compactada"}

    def reset(self, total_memory: int | None = None):
        """Reinicia la memoria y opcionalmente actualiza el tamano total."""
        with self._manager_lock:
            if total_memory is None:
                total_memory = self._get_system_total_mb()
            self._manager = MemoryManager(total_memory)

    # ------------------------------------------------------------------ #
    # Datos adicionales para la UI

    def _get_system_ram(self) -> Dict[str, float]:
        """Obtiene el estado actual de la RAM física."""
        try:
            ram = psutil.virtual_memory()
            total = ram.total / (1024 ** 2)
            used = ram.used / (1024 ** 2)
            available = ram.available / (1024 ** 2)
            percent = ram.percent
        except Exception:
            total = used = available = percent = 0.0

        return {
            "total": round(total, 1),
            "used": round(used, 1),
            "available": round(available, 1),
            "percent": round(percent, 1),
        }

    def _get_system_total_mb(self) -> int:
        """Devuelve la RAM física total en MB (entero)."""
        try:
            ram = psutil.virtual_memory()
            return max(1, int(ram.total / (1024 ** 2)))
        except Exception:
            return 256

    def get_real_processes(self, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Retorna procesos reales del sistema ordenados por uso de memoria.

        Args:
            limit: número máximo de procesos a retornar.
        """
        processes: List[Dict[str, Any]] = []
        for proc in psutil.process_iter(["pid", "name", "memory_info"]):
            try:
                info = proc.info
                memory_bytes = getattr(info.get("memory_info"), "rss", 0) or 0
                memory_mb = memory_bytes / (1024 ** 2)
                processes.append(
                    {
                        "pid": info.get("pid"),
                        "name": info.get("name") or "Proceso",
                        "memory_mb": round(memory_mb, 2),
                    }
                )
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        processes.sort(key=lambda x: x["memory_mb"], reverse=True)
        return processes[:limit]
