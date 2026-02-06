import psutil
import os
import platform
from ..base_monitor import BaseMonitor

class StorageMonitor(BaseMonitor):
    """Monitor especializado en detectar pendrives y discos con letra de unidad"""
    
    def collect_data(self):
        """Implementación del motor de búsqueda de unidades"""
        devices = []
        try:
            for part in psutil.disk_partitions():
                # Detectamos unidades removibles (USB) o discos que no sean el principal C:
                if 'removable' in part.opts or (platform.system() == "Windows" and part.mountpoint != 'C:\\'):
                    try:
                        # Aseguramos el formato de ruta 'F:/' para evitar errores de Python 3.12
                        path = part.mountpoint.rstrip('\\') + os.sep
                        usage = psutil.disk_usage(path)
                        
                        devices.append({
                            'unit': part.mountpoint,
                            'total': usage.total // (1024**3), # GB
                            'free': usage.free // (1024**3),   # GB
                            'files': os.listdir(path) if os.path.exists(path) else []
                        })
                    except Exception:
                        # Ignora unidades que no están listas (como lectores de SD vacíos)
                        continue
        except Exception as e:
            print(f"[ERROR] Fallo crítico en StorageMonitor: {e}")
            
        return devices

    def execute_format(self, unit):
        """Lógica para la acción de formateo de la pizarra"""
        print(f"[INFO] Simulando formateo de la unidad {unit}")
        return True
