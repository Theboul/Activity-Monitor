import customtkinter as ctk
from src.gui.tabs.tab_hardware import HardwareTab
from src.backend.adm_hardware.hardware_monitor import HardwareMonitor


class MonitorGUI(ctk.CTk):
    """Ventana principal de la aplicación Monitor de Sistema"""
    
    def __init__(self):
        super().__init__()
        self._configure_window()
        self._setup_tabs()
        self._setup_monitors()
    
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
    
    def _setup_monitors(self):
        """Configura y arranca los monitores del sistema"""
        # Crear monitor de hardware
        self.hardware_monitor = HardwareMonitor(update_interval=2.0)
        
        # Configurar callback thread-safe usando after()
        self.hardware_monitor.set_callback(self._on_hardware_data_update)
        
        # Iniciar monitoreo
        self.hardware_monitor.start()
        
        # Hacer una actualización inicial inmediata
        self._update_hardware_initial()
    
    def _on_hardware_data_update(self, data):
        """
        Callback que recibe datos del hardware monitor (se ejecuta en hilo del monitor).
        Usa after() para actualizar la UI de forma thread-safe.
        
        Args:
            data: Dict con datos de CPU, RAM y almacenamiento
        """
        # Programar actualización en el hilo principal de la UI
        self.after(0, self._update_hardware_ui, data)
    
    def _update_hardware_ui(self, data):
        """
        Actualiza la interfaz con los datos de hardware (se ejecuta en el hilo principal)
        
        Args:
            data: Dict con claves 'cpu', 'ram', 'storage'
        """
        if hasattr(self, 'hardware_tab'):
            self.hardware_tab.update_all_data(
                cpu_data=data.get('cpu'),
                ram_data=data.get('ram'),
                storage_data=data.get('storage')
            )
    
    def _update_hardware_initial(self):
        """Actualiza la UI inmediatamente con los datos actuales"""
        initial_data = self.hardware_monitor.get_current_data()
        if initial_data:
            self._update_hardware_ui(initial_data)
    
    def destroy(self):
        """Sobrescribe destroy para limpiar los monitores antes de cerrar"""
        # Detener todos los monitores
        if hasattr(self, 'hardware_monitor'):
            self.hardware_monitor.stop()
        
        # Llamar al destroy original
        super().destroy()
