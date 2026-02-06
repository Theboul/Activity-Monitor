import psutil
import os
import platform
import shutil
from ..base_monitor import BaseMonitor

class StorageMonitor(BaseMonitor):
    def __init__(self, update_interval: float = 3.0):
        super().__init__(update_interval)
        self.clipboard_path = None

    def collect_data(self):
        devices = []
        try:
            for part in psutil.disk_partitions():
                if 'removable' in part.opts or (platform.system() == "Windows" and part.mountpoint != 'C:\\'):
                    try:
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
        except Exception as e:
            print(f"[ERROR] StorageMonitor: {e}")
        return devices

    # --- LÓGICA DE ARCHIVOS REAL ---
    def set_to_clipboard(self, file_path):
        if os.path.exists(file_path):
            self.clipboard_path = file_path
            return True
        return False

    def paste_to(self, dest_folder):
        if self.clipboard_path and os.path.exists(dest_folder):
            try:
                shutil.copy2(self.clipboard_path, dest_folder)
                return True
            except Exception as e:
                print(f"[ERROR] Al pegar: {e}")
        return False

    def move_file(self, src, dest):
        try:
            shutil.move(src, dest)
            return True
        except Exception as e:
            print(f"[ERROR] Al mover: {e}")
        return False

    def delete_file(self, file_path):
        """Elimina el archivo físicamente del sistema"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
        except Exception as e:
            print(f"[ERROR] Al eliminar: {e}")
        return False

    def execute_format(self, unit):
        print(f"[INFO] Formateando unidad {unit}...")
        return True