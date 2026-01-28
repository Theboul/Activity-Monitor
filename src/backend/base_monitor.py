"""
Clase base para todos los monitores del sistema
Proporciona funcionalidad común de threading y callbacks
"""
import threading
import time
from abc import ABC, abstractmethod
from typing import Callable, Optional, Any


class BaseMonitor(ABC):
    """
    Clase base abstracta para monitores del sistema.
    
    Proporciona:
    - Threading seguro para ejecución en segundo plano
    - Sistema de callbacks para notificar cambios
    - Control de inicio/parada del monitoreo
    - Intervalo de actualización configurable
    
    Los monitores hijos deben implementar collect_data()
    """
    
    def __init__(self, update_interval: float = 2.0):
        """
        Inicializa el monitor base
        
        Args:
            update_interval: Intervalo en segundos entre actualizaciones (default: 2.0)
        """
        self.update_interval = update_interval
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[Any], None]] = None
        self._lock = threading.Lock()
    
    @abstractmethod
    def collect_data(self) -> Any:
        """
        Método abstracto que debe implementar cada monitor hijo.
        Recolecta los datos específicos del monitor.
        
        Returns:
            Los datos recolectados (el formato depende del monitor)
        """
        pass
    
    def set_callback(self, callback: Callable[[Any], None]):
        """
        Establece la función callback que se llamará con los datos actualizados
        
        Args:
            callback: Función que recibe los datos como parámetro
        """
        with self._lock:
            self._callback = callback
    
    def start(self):
        """Inicia el monitoreo en un hilo separado"""
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
    
    def stop(self):
        """Detiene el monitoreo"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=self.update_interval + 1)
    
    def _monitor_loop(self):
        """Loop principal del monitor que se ejecuta en el hilo separado"""
        while self._running:
            try:
                # Recolectar datos
                data = self.collect_data()
                
                # Notificar a través del callback si está configurado
                # se esta usando un candado para evitar condiciones de carrera
                # (Condicion de concurso - como dice ginno)
                with self._lock:
                    if self._callback:
                        self._callback(data)
                
                # Esperar el intervalo antes de la siguiente actualización
                time.sleep(self.update_interval)
                
            except Exception as e:
                print(f"Error en {self.__class__.__name__}: {e}")
                time.sleep(self.update_interval)
    
    def is_running(self) -> bool:
        """Retorna True si el monitor está activo"""
        return self._running
    
    def get_current_data(self) -> Any:
        """
        Obtiene los datos actuales sin esperar.
        Útil para obtener una lectura inmediata.
        
        Returns:
            Los datos actuales
        """
        try:
            return self.collect_data()
        except Exception as e:
            print(f"Error obteniendo datos de {self.__class__.__name__}: {e}")
            return None
