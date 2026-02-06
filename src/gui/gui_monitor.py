import customtkinter as ctk
from src.gui.tabs.tab_hardware import HardwareTab
from src.gui.tabs.tab_process import ProcessTab
from src.gui.tabs.tab_memory import MemoryTab
from src.backend.adm_hardware.hardware_monitor import HardwareMonitor
from src.backend.adm_process_simulator.process_monitor import ProcessMonitor
from src.backend.adm_memory import MemoryMonitor
from src.gui.tabs.tab_usb import USBTab
from src.backend.adm_storage_unit.storage_monitor import StorageMonitor

class MonitorGUI(ctk.CTk):
    """Ventana principal de la aplicación Monitor de Sistema"""
    
    def __init__(self):
        super().__init__()
        self._configure_window()
        self._create_monitors()  # ← Crear monitores PRIMERO
        self._setup_tabs()       # ← Luego crear tabs (que usan los monitores)
        self._start_monitors()   # ← Finalmente iniciar monitoreo
    
    def _configure_window(self):
        """Configura las propiedades de la ventana principal"""
        self.title("Monitor de Sistema")
        self.geometry("1100x600")
        self.resizable(True, True)
        
        # Registrar handler para cerrar la ventana correctamente
        self.protocol("WM_DELETE_WINDOW", self._on_closing)
    
    def _setup_tabs(self):
        """Crea y configura el sistema de pestañas principal"""
        # Frame superior con título y botón de salir
        top_frame = ctk.CTkFrame(self, height=50, fg_color="transparent")
        top_frame.pack(fill="x", padx=20, pady=(10, 0))
        
        title_label = ctk.CTkLabel(
            top_frame,
            text="🖥️ Monitor de Sistema",
            font=("Arial", 18, "bold")
        )
        title_label.pack(side="left", padx=10)
        
        # Botón de salir
        exit_button = ctk.CTkButton(
            top_frame,
            text="❌ Salir",
            command=self._on_closing,
            width=100,
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            font=("Arial", 12, "bold")
        )
        exit_button.pack(side="right", padx=10)
        
        # Crear el Tabview principal
        self.tab_view = ctk.CTkTabview(self)
        self.tab_view.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        
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
        self.process_tab = ProcessTab(tab, self.process_monitor)
        self.process_tab.pack(fill="both", expand=True)
    
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
        self.memory_tab = MemoryTab(tab, self.memory_monitor)
        self.memory_tab.pack(fill="both", expand=True)
    
    def _create_monitors(self):
        """Crea las instancias de los monitores (sin iniciar)"""
        # Crear monitor de hardware
        self.hardware_monitor = HardwareMonitor(update_interval=2.0)

        # Crear monitor de procesos (no necesita auto-start, es bajo demanda)
        self.process_monitor = ProcessMonitor(update_interval=1.0)

        # Crear monitor de memoria
        self.memory_monitor = MemoryMonitor(update_interval=2.0)

        # NUEVO: Instancia el monitor de USB
        self.usb_monitor = StorageMonitor(update_interval=3.0)
    
    def _start_monitors(self):
        """Inicia los monitores después de crear la UI"""
        # Configurar callback thread-safe para hardware
        self.hardware_monitor.set_callback(self._on_hardware_data_update)

        # Iniciar monitoreo de hardware
        self.hardware_monitor.start()

        # Hacer una actualización inicial inmediata
        self._update_hardware_initial()

        # Configurar e iniciar monitor de memoria
        self.memory_monitor.set_callback(self._on_memory_data_update)
        self.memory_monitor.start()
        self._update_memory_initial()
    
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

    def _on_memory_data_update(self, data):
        """Callback del monitor de memoria."""
        self.after(0, self._update_memory_ui, data)

    def _update_memory_ui(self, data):
        if hasattr(self, 'memory_tab'):
            self.memory_tab.update_memory_state(data)

    def _update_memory_initial(self):
        data = self.memory_monitor.get_current_data()
        if data:
            self._update_memory_ui(data)
    
    def _on_closing(self):
        """Handler personalizado para cerrar la ventana de forma segura"""
        print("\n" + "="*60)
        print("[INFO] 🛑 INICIANDO CIERRE DE APLICACIÓN")
        print("="*60)
        
        # 1. Detener monitor de hardware
        if hasattr(self, 'hardware_monitor'):
            print("[INFO] 🔧 Deteniendo hardware monitor...")
            try:
                self.hardware_monitor.stop()
                print("[OK] ✓ Hardware monitor detenido")
            except Exception as e:
                print(f"[ERROR] ✗ Error al detener hardware monitor: {e}")
        
        # 2. Detener monitor de procesos
        if hasattr(self, 'process_monitor'):
            print("[INFO] 🔧 Deteniendo process monitor...")
            try:
                self.process_monitor.stop()
                print("[OK] ✓ Process monitor detenido")
            except Exception as e:
                print(f"[ERROR] ✗ Error al detener process monitor: {e}")

        # 3. Detener monitor de memoria
        if hasattr(self, 'memory_monitor'):
            print("[INFO] 🔧 Deteniendo memory monitor...")
            try:
                self.memory_monitor.stop()
                print("[OK] ✓ Memory monitor detenido")
            except Exception as e:
                print(f"[ERROR] ✗ Error al detener memory monitor: {e}")
        
        # 4. Limpiar referencias del tab de procesos
        if hasattr(self, 'process_tab'):
            print("[INFO] 🧹 Limpiando referencias de process_tab...")
            try:
                self.process_tab.cleanup()
                print("[OK] ✓ Process tab limpiado")
            except Exception as e:
                print(f"[ERROR] ✗ Error al limpiar process_tab: {e}")
        
        # 4. Detener monitor de memoria
        if hasattr(self, 'memory_monitor'):
            print("[INFO] 🔧 Deteniendo memory monitor...")
            try:
                self.memory_monitor.stop()
                print("[OK] ✓ Memory monitor detenido")
            except Exception as e:
                print(f"[ERROR] ✗ Error al detener memory monitor: {e}")
        
        if hasattr(self, 'usb_monitor'):
                print("[INFO] 🔧 Deteniendo USB monitor...")
                self.usb_monitor.stop()
        
        # 5. Destruir la ventana
        print("[INFO] 💥 Destruyendo ventana...")
        self.destroy()
        
        # 6. Forzar salida del programa
        print("[INFO] 🚪 Forzando salida del proceso Python...")
        print("="*60)
        print("[INFO] ✅ APLICACIÓN CERRADA COMPLETAMENTE")
        print("="*60 + "\n")
        
        import sys
        import os
        
        # Forzar exit completo
        os._exit(0)  # Exit más agresivo que sys.exit()
    
    def destroy(self):
        """Sobrescribe destroy para asegurar limpieza final"""
        try:
            # Llamar al destroy original
            super().destroy()
        except Exception as e:
            print(f"[WARNING] Error en destroy: {e}")

    def _add_usb_tab(self):
        """Añade la pestaña de Archivos USB real conectada al monitor"""
        tab = self.tab_view.add("Archivos USB")
        # Pasamos el monitor como dependencia a la pestaña
        self.usb_tab = USBTab(tab, self.usb_monitor)
        self.usb_tab.pack(fill="both", expand=True)