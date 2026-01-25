import customtkinter as ctk


class CPUCard(ctk.CTkFrame):
    """Tarjeta que muestra la información del CPU"""
    
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
            text="CPU", 
            font=("Arial", 16, "bold"), 
            text_color="gray"
        ).pack(pady=(20, 10))
        
        # Porcentaje grande
        self.cpu_percentage_label = ctk.CTkLabel(
            self, 
            text="24%", 
            font=("Arial", 70, "bold"), 
            text_color="#3399FF"
        )
        self.cpu_percentage_label.pack()
        
        # Subtítulo
        self.cpu_info_label = ctk.CTkLabel(
            self, 
            text="Intel Core i7 - 8 Cores", 
            font=("Arial", 14), 
            text_color="gray"
        )
        self.cpu_info_label.pack(pady=(0, 20))
        
        # Gráfico placeholder
        self.cpu_graph_placeholder = ctk.CTkProgressBar(
            self, 
            height=4, 
            progress_color="#3399FF"
        )
        self.cpu_graph_placeholder.set(0.3)
        self.cpu_graph_placeholder.pack(fill="x", padx=30, pady=20)
    
    def update_cpu_usage(self, percentage, cpu_info=None):
        """
        Actualiza los valores mostrados en la tarjeta
        
        Args:
            percentage (float): Porcentaje de uso del CPU (0-100)
            cpu_info (str, optional): Información del CPU
        """
        self.cpu_percentage_label.configure(text=f"{int(percentage)}%")
        self.cpu_graph_placeholder.set(percentage / 100)
        
        if cpu_info:
            self.cpu_info_label.configure(text=cpu_info)
