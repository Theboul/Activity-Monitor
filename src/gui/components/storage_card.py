import customtkinter as ctk


class StorageCard(ctk.CTkFrame):
    """Tarjeta que muestra la información del almacenamiento"""
    
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
            text="Almacenamiento Principal (C:)", 
            font=("Arial", 16, "bold"), 
            text_color="gray"
        ).pack(pady=(20, 30))
        
        # Barra de progreso del disco
        self.storage_bar = ctk.CTkProgressBar(
            self, 
            height=15, 
            progress_color="#3399FF"
        )
        self.storage_bar.set(0.85)
        self.storage_bar.pack(fill="x", padx=30, pady=(0, 10))
        
        # Frame de resumen horizontal
        summary_frame = ctk.CTkFrame(self, fg_color="transparent")
        summary_frame.pack(fill="x", padx=30)
        
        self.used_summary_label = ctk.CTkLabel(
            summary_frame, 
            text="850 GB usados de 1 TB", 
            font=("Arial", 12, "bold")
        )
        self.used_summary_label.pack(side="left")
        
        self.free_summary_label = ctk.CTkLabel(
            summary_frame, 
            text="150 GB Libres", 
            font=("Arial", 12, "bold"), 
            text_color="#3399FF"
        )
        self.free_summary_label.pack(side="right")
        
        # Grid de detalles
        details_grid = ctk.CTkFrame(self, fg_color="transparent")
        details_grid.pack(fill="x", padx=30, pady=(30, 20))
        
        # Columna izquierda: Usado
        ctk.CTkLabel(
            details_grid, 
            text="Usado", 
            font=("Arial", 12, "bold"), 
            text_color="gray"
        ).grid(row=0, column=0, sticky="w")
        
        self.used_detail_label = ctk.CTkLabel(
            details_grid, 
            text="850 GB", 
            font=("Arial", 18, "bold")
        )
        self.used_detail_label.grid(row=1, column=0, sticky="w")
        
        # Columna derecha: Disponible
        ctk.CTkLabel(
            details_grid, 
            text="Disponible", 
            font=("Arial", 12, "bold"), 
            text_color="gray"
        ).grid(row=0, column=1, sticky="e", padx=(100, 0))
        
        self.free_detail_label = ctk.CTkLabel(
            details_grid, 
            text="150 GB", 
            font=("Arial", 18, "bold"), 
            text_color="#3399FF"
        )
        self.free_detail_label.grid(row=1, column=1, sticky="e", padx=(100, 0))
    
    def update_storage(self, used_gb, total_gb):
        """
        Actualiza los valores mostrados en la tarjeta
        
        Args:
            used_gb (int): GB usados en el disco
            total_gb (int): GB totales del disco
        """
        free_gb = total_gb - used_gb
        percentage = (used_gb / total_gb) * 100
        
        self.storage_bar.set(percentage / 100)
        
        # Actualizar labels de resumen
        self.used_summary_label.configure(text=f"{used_gb} GB usados de {total_gb // 1000} TB")
        self.free_summary_label.configure(text=f"{free_gb} GB Libres")
        
        # Actualizar labels de detalle
        self.used_detail_label.configure(text=f"{used_gb} GB")
        self.free_detail_label.configure(text=f"{free_gb} GB")
