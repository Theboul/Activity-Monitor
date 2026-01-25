import customtkinter as ctk
from src.gui.gui_monitor import MonitorGUI

# Configuración global del tema (Modo Oscuro y Color Azul de acento)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


# Ejecutar la aplicación
if __name__ == "__main__":
    app = MonitorGUI()
    app.mainloop()