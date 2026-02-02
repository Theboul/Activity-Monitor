"""
Monitor de Sistema - Aplicación Principal
"""
import customtkinter as ctk
from src.gui.gui_monitor import MonitorGUI
import sys

# Configuración global del tema (Modo Oscuro y Color Azul de acento)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# Ejecutar la aplicación
if __name__ == "__main__":
    try:
        app = MonitorGUI()
        app.mainloop()
    except KeyboardInterrupt:
        print("\n[INFO] Aplicación interrumpida por el usuario")
    except Exception as e:
        print(f"[ERROR] Error en la aplicación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[INFO] Saliendo...")
        sys.exit(0)