import customtkinter as ctk


class RAMCard(ctk.CTkFrame):
    """Tarjeta que muestra la información de la memoria RAM"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            fg_color="#1f1f1f",
            border_width=2,
            border_color="#3399FF",
            corner_radius=15,
            **kwargs
        )
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario de la tarjeta"""
        # Título
        ctk.CTkLabel(
            self, 
            text="Memoria RAM", 
            font=("Arial", 16, "bold"), 
            text_color="gray"
        ).pack(pady=(20, 30))
        
        # Barra de progreso como gauge
        self.ram_gauge = ctk.CTkProgressBar(
            self, 
            height=20, 
            corner_radius=10, 
            progress_color="#3399FF"
        )
        self.ram_gauge.set(0.45)
        self.ram_gauge.pack(fill="x", padx=40, pady=(0, 10))
        
        # Porcentaje
        self.percentage_label = ctk.CTkLabel(
            self, 
            text="45%", 
            font=("Arial", 40, "bold"), 
            text_color="#3399FF"
        )
        self.percentage_label.pack()
        
        # Detalles de uso
        self.usage_label = ctk.CTkLabel(
            self, 
            text="7.2 GB / 16 GB", 
            font=("Arial", 18, "bold")
        )
        self.usage_label.pack(pady=(10, 5))
        
        self.status_label = ctk.CTkLabel(
            self, 
            text="45% en uso", 
            font=("Arial", 14), 
            text_color="gray"
        )
        self.status_label.pack(pady=(0, 20))
    
    def update_ram_usage(self, used_gb, total_gb):
        """
        Actualiza los valores mostrados en la tarjeta
        
        Args:
            used_gb (float): GB de RAM en uso
            total_gb (float): GB totales de RAM
        """
        percentage = (used_gb / total_gb) * 100
        
        self.ram_gauge.set(percentage / 100)
        self.percentage_label.configure(text=f"{int(percentage)}%")
        self.usage_label.configure(text=f"{used_gb:.1f} GB / {total_gb} GB")
        self.status_label.configure(text=f"{int(percentage)}% en uso")
