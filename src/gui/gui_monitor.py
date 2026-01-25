import customtkinter as ctk
from src.gui.tabs.tab_hardware import HardwareTab


class MonitorGUI(ctk.CTk):
    """Ventana principal de la aplicación Monitor de Sistema"""
    
    def __init__(self):
        super().__init__()
        self._configure_window()
        self._setup_tabs()
    
    def _configure_window(self):
        """Configura las propiedades de la ventana principal"""
        self.title("Monitor de Sistema")
        self.geometry("1100x600")
        self.resizable(False, False)
    
    def _setup_tabs(self):
        """Crea y configura el sistema de pestañas principal"""
        # Crear el Tabview principal
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Añadir pestañas
        self._add_hardware_tab()
        self._add_process_tab()
        self._add_usb_tab()
        self._add_memory_tab()
    
    def _add_hardware_tab(self):
        """Añade la pestaña de Monitor de Hardware"""
        tab = self.tab_view.add("Monitor de Hardware")
        self.hardware_tab = HardwareTab(tab)
        self.hardware_tab.pack(fill="both", expand=True)
    
    def _add_process_tab(self):
        """Añade la pestaña de Simulación de Procesos"""
        tab = self.tab_view.add("Simulación Procesos")
        # TODO: Implementar contenido de la pestaña
        placeholder = ctk.CTkLabel(
            tab, 
            text="Simulación de Procesos\n(Por implementar)",
            font=("Arial", 20),
            text_color="gray"
        )
        placeholder.pack(expand=True)
    
    def _add_usb_tab(self):
        """Añade la pestaña de Archivos USB"""
        tab = self.tab_view.add("Archivos USB")
        # TODO: Implementar contenido de la pestaña
        placeholder = ctk.CTkLabel(
            tab, 
            text="Archivos USB\n(Por implementar)",
            font=("Arial", 20),
            text_color="gray"
        )
        placeholder.pack(expand=True)
    
    def _add_memory_tab(self):
        """Añade la pestaña de Administración de Memoria"""
        tab = self.tab_view.add("Admin Memoria")
        # TODO: Implementar contenido de la pestaña
        placeholder = ctk.CTkLabel(
            tab, 
            text="Administración de Memoria\n(Por implementar)",
            font=("Arial", 20),
            text_color="gray"
        )
        placeholder.pack(expand=True)
