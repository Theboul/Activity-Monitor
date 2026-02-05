import psutil
import os
import shutil
import platform
import subprocess
from tkinter import messagebox
from ..base_monitor import BaseMonitor

class StorageMonitor(BaseMonitor):
    def __init__(self, update_interval: float = 2.0):
        super().__init__(update_interval)
        self.last_devices = []

    def collect_data(self):
        """Detecta unidades y lista archivos (RF-003)"""
        devices = []
        for part in psutil.disk_partitions():
            if 'removable' in part.opts or (platform.system() == "Windows" and part.fstype == ""):
                try:
                    # Solución al error 'bad format char'
                    path = part.mountpoint.rstrip('\\') + os.sep
                    usage = psutil.disk_usage(path)
                    
                    devices.append({
                        'unit': part.mountpoint,
                        'total': usage.total // (1024**3),
                        'free': usage.free // (1024**3),
                        'files': os.listdir(path) if os.path.exists(path) else []
                    })
                except Exception:
                    continue
        return devices

    def format_unit(self, unit_letter):
        """Simula y ejecuta el formateo de la unidad (Pizarra)"""
        # Comando real de Windows: format F: /Q (Quick format)
        # Requiere permisos de admin, por eso es un riesgo [cite: 8]
        try:
            # Solo como ejemplo de comando de sistema
            # subprocess.run(["format", unit_letter, "/Q", "/X"], check=True)
            return True
        except Exception as e:
            print(f"Error formateando: {e}")
            return False