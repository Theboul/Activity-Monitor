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
    - Context manager para uso con with statement
    
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
        self._stop_event = threading.Event()  # Para interrumpir el sleep
        self._thread: Optional[threading.Thread] = None
        self._callback: Optional[Callable[[Any], None]] = None
        self._lock = threading.Lock()
    
    def __enter__(self):
        """Entrada del context manager - inicia el monitor"""
        self.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Salida del context manager - detiene el monitor"""
        self.stop()
        return False  # No suprime excepciones
    
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
            self._stop_event.clear()
            self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._thread.start()
            print(f"[DEBUG] {self.__class__.__name__} iniciado")
    
    def stop(self):
        """Detiene el monitoreo de forma segura y forzada si es necesario"""
        if self._running:
            print(f"[DEBUG] 🛑 Deteniendo {self.__class__.__name__}...")
            self._running = False
            self._stop_event.set()  # Interrumpe el sleep inmediatamente
            
            if self._thread and self._thread.is_alive():
                # Primer intento: esperar 1 segundo
                self._thread.join(timeout=1.0)
                
                if self._thread.is_alive():
                    print(f"[WARNING] ⚠️ {self.__class__.__name__} aún corriendo, esperando 1s más...")
                    # Segundo intento: esperar 1 segundo más
                    self._thread.join(timeout=1.0)
                    
                    if self._thread.is_alive():
                        print(f"[ERROR] ❌ {self.__class__.__name__} NO SE DETUVO - Thread zombie detectado")
                        # No podemos hacer mucho más con un daemon thread,
                        # pero al menos alertamos
                    else:
                        print(f"[DEBUG] ✓ {self.__class__.__name__} detenido correctamente")
                else:
                    print(f"[DEBUG] ✓ {self.__class__.__name__} detenido correctamente")
            
            self._thread = None
            self._callback = None  # Limpiar callback también
    
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
                
                # Esperar el intervalo O hasta que se llame stop()
                # Usa wait() en lugar de sleep() para poder interrumpir
                if self._stop_event.wait(timeout=self.update_interval):
                    # Si wait() retorna True, significa que stop() fue llamado
                    break
                
            except Exception as e:
                print(f"[ERROR] Error en {self.__class__.__name__}: {e}")
                # También usar wait aquí para poder interrumpir en caso de error
                if self._stop_event.wait(timeout=self.update_interval):
                    break
        
        print(f"[DEBUG] {self.__class__.__name__} loop terminado")
    
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
