"""
Monitor de hardware del sistema usando psutil
Recolecta información de CPU, RAM y almacenamiento
"""
import psutil
import platform
from typing import Dict, Any
from ..base_monitor import BaseMonitor

# Para esta clase se usa la clase base monitor para usar los hilos 
# y el sistema de callbacks, para mandar los datos recolectados se usa el metodo collect_data
# de tipo Dict[str, Any] (Listas de tipo Diccionario) que contiene 
# la informacion de cpu, ram y almacenamiento
class HardwareMonitor(BaseMonitor):
    """
    Monitor de hardware que recolecta datos de CPU, RAM y almacenamiento.
    
    Hereda de BaseMonitor para tener threading automático y sistema de callbacks.
    
    Uso:
        monitor = HardwareMonitor(update_interval=2.0)
        monitor.set_callback(mi_funcion_actualizar_ui)
        monitor.start()
    """
    
    def __init__(self, update_interval: float = 2.0):
        """
        Inicializa el monitor de hardware
        
        Args:
            update_interval: Intervalo en segundos entre actualizaciones (default: 2.0)
        """
        super().__init__(update_interval)
        self._cpu_info = self._get_cpu_info()
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Recolecta datos actuales de hardware usando psutil
        
        Returns:
            Dict con las claves:
                - 'cpu': {'percentage': float, 'info': str}
                - 'ram': {'used': float, 'total': float, 'available': float}
                - 'storage': {'used': int, 'total': int, 'free': int, 'percent': float}
        """
        return {
            'cpu': self._get_cpu_data(),
            'ram': self._get_ram_data(),
            'storage': self._get_storage_data()
        }
    
    def _get_cpu_info(self) -> str:
        """
        Obtiene información estática del CPU (solo se llama una vez)
        
        Returns:
            String con el nombre del CPU y número de núcleos
        """
        try:
            cpu_name = platform.processor()
            cpu_count = psutil.cpu_count(logical=False)  # Núcleos físicos
            cpu_threads = psutil.cpu_count(logical=True)  # Hilos lógicos
            
            # Si no se puede obtener el nombre, usar uno genérico
            if not cpu_name or cpu_name.strip() == "":
                cpu_name = "CPU"
            
            # Formato: "Intel Core i7 - 8 Cores"
            if cpu_count:
                return f"{cpu_name} - {cpu_count} Cores ({cpu_threads} Threads)"
            else:
                return f"{cpu_name} - {cpu_threads} Threads"
                
        except Exception as e:
            print(f"Error obteniendo info de CPU: {e}")
            return "CPU - Info no disponible"
    
    def _get_cpu_data(self) -> Dict[str, Any]:
        """
        Obtiene datos actuales del CPU
        
        Returns:
            Dict con 'percentage' (float 0-100) y 'info' (str)
        """
        try:
            # cpu_percent() con interval=1 hace una medición de 1 segundo
            # Para evitar bloquear, usamos interval=None después de la primera llamada
            cpu_percent = psutil.cpu_percent(interval=1)
            
            return {
                'percentage': round(cpu_percent, 1),
                'info': self._cpu_info
            }
        except Exception as e:
            print(f"Error obteniendo datos de CPU: {e}")
            return {'percentage': 0.0, 'info': self._cpu_info}
    
    def _get_ram_data(self) -> Dict[str, float]:
        """
        Obtiene datos actuales de la memoria RAM
        
        Returns:
            Dict con 'used', 'total' y 'available' en GB (float)
        """
        try:
            ram = psutil.virtual_memory()
            
            # Convertir de bytes a GB
            used_gb = ram.used / (1024 ** 3)
            total_gb = ram.total / (1024 ** 3)
            available_gb = ram.available / (1024 ** 3)
            
            return {
                'used': round(used_gb, 1),
                'total': round(total_gb, 1),
                'available': round(available_gb, 1)
            }
        except Exception as e:
            print(f"Error obteniendo datos de RAM: {e}")
            return {'used': 0.0, 'total': 1.0, 'available': 1.0}
    
    def _get_storage_data(self) -> Dict[str, Any]:
        """
        Obtiene datos del disco principal del sistema
        
        En Windows usa C:
        
        Returns:
            Dict con 'used', 'total', 'free' en GB (int) y 'percent' (float)
        """
        try:
            # Determinar la partición principal según el SO
            if platform.system() == "Windows":
                partition = "C:\\"
            else:
                partition = "/"
            
            disk = psutil.disk_usage(partition)
            
            # Convertir de bytes a GB
            used_gb = disk.used // (1024 ** 3)
            total_gb = disk.total // (1024 ** 3)
            free_gb = disk.free // (1024 ** 3)
            
            return {
                'used': int(used_gb),
                'total': int(total_gb),
                'free': int(free_gb),
                'percent': round(disk.percent, 1)
            }
        except Exception as e:
            print(f"Error obteniendo datos de almacenamiento: {e}")
            return {'used': 0, 'total': 1, 'free': 1, 'percent': 0.0}
    
    def get_all_disks(self) -> Dict[str, Dict[str, Any]]:
        """
        Obtiene información de todas las particiones del sistema
        
        Útil para extensiones futuras (mostrar múltiples discos)
        
        Returns:
            Dict donde la clave es el punto de montaje y el valor son los datos del disco
        """
        disks = {}
        try:
            partitions = psutil.disk_partitions()
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    disks[partition.mountpoint] = {
                        'device': partition.device,
                        'fstype': partition.fstype,
                        'used': usage.used // (1024 ** 3),
                        'total': usage.total // (1024 ** 3),
                        'free': usage.free // (1024 ** 3),
                        'percent': round(usage.percent, 1)
                    }
                except PermissionError:
                    # Algunas particiones pueden no ser accesibles
                    continue
        except Exception as e:
            print(f"Error obteniendo lista de discos: {e}")
        
        return disks
