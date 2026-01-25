import customtkinter as ctk
from src.gui.components.cpu_card import CPUCard
from src.gui.components.ram_card import RAMCard
from src.gui.components.storage_card import StorageCard


class HardwareTab(ctk.CTkFrame):
    """Pestaña que contiene el monitor de hardware con todas sus tarjetas"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario de la pestaña"""
        # Configurar grid de 1 fila y 3 columnas para las tres tarjetas
        self.grid_columnconfigure(0, weight=1, uniform="cards")
        self.grid_columnconfigure(1, weight=1, uniform="cards")
        self.grid_columnconfigure(2, weight=1, uniform="cards")
        
        # Crear las tres tarjetas
        self.cpu_card = CPUCard(self)
        self.cpu_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        self.ram_card = RAMCard(self)
        self.ram_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        self.storage_card = StorageCard(self)
        self.storage_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
    
    def update_all_data(self, cpu_data=None, ram_data=None, storage_data=None):
        """
        Actualiza todas las tarjetas con nuevos datos
        
        Args:
            cpu_data (dict): Datos del CPU {'percentage': float, 'info': str}
            ram_data (dict): Datos de la RAM {'used': float, 'total': float}
            storage_data (dict): Datos del almacenamiento {'used': int, 'total': int}
        """
        if cpu_data:
            self.cpu_card.update_cpu_usage(
                cpu_data.get('percentage', 0),
                cpu_data.get('info')
            )
        
        if ram_data:
            self.ram_card.update_ram_usage(
                ram_data.get('used', 0),
                ram_data.get('total', 1)
            )
        
        if storage_data:
            self.storage_card.update_storage(
                storage_data.get('used', 0),
                storage_data.get('total', 1)
            )
