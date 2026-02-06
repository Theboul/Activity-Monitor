"""
Componente visual para representar un bloque de partición de memoria
"""
import customtkinter as ctk
from typing import Optional, Callable


class PartitionBlock(ctk.CTkFrame):
    """
    Bloque visual que representa una partición de memoria
    Compatible con particiones fijas y variables
    """
    
    def __init__(
        self, 
        parent, 
        partition_id: int,
        size: int,
        is_free: bool = True,
        process_name: Optional[str] = None,
        process_size: Optional[int] = None,
        fragmentation: int = 0,
        on_release_callback: Optional[Callable] = None,
        **kwargs
    ):
        # Determinar color según el estado
        if is_free:
            border_color = "#2ecc71"  # Verde para libre
            fg_color = "#1a4d2e"
        else:
            border_color = "#3498db"  # Azul para ocupado
            fg_color = "#1e3a5f"
        
        super().__init__(
            parent,
            fg_color=fg_color,
            border_width=3,
            border_color=border_color,
            corner_radius=8,
            **kwargs
        )
        
        self.partition_id = partition_id
        self.size = size
        self.is_free = is_free
        self.process_name = process_name
        self.process_size = process_size
        self.fragmentation = fragmentation
        self.on_release_callback = on_release_callback
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura el contenido del bloque"""
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=10, pady=8)
        
        if self.is_free:
            self._create_free_partition_ui(content_frame)
        else:
            self._create_occupied_partition_ui(content_frame)
    
    def _create_free_partition_ui(self, parent):
        """Crea la UI para una partición libre"""
        size_label = ctk.CTkLabel(
            parent,
            text=f"tam: {self.size} MB",
            font=("Arial", 11, "bold"),
            text_color="#2ecc71"
        )
        size_label.pack(side="left", padx=(0, 10))
        
        status_label = ctk.CTkLabel(
            parent,
            text="LIBRE",
            font=("Arial", 12, "bold"),
            text_color="#2ecc71"
        )
        status_label.pack(side="right")
    
    def _create_occupied_partition_ui(self, parent):
        """Crea la UI para una partición ocupada"""
        process_label = ctk.CTkLabel(
            parent,
            text=self.process_name or "Proceso",
            font=("Arial", 11, "bold"),
            text_color="white"
        )
        process_label.pack(anchor="w")
        
        info_frame = ctk.CTkFrame(parent, fg_color="transparent")
        info_frame.pack(fill="x", pady=(2, 0))
        
        size_label = ctk.CTkLabel(
            info_frame,
            text=f"tam: {self.process_size} MB",
            font=("Arial", 10),
            text_color="#bdc3c7"
        )
        size_label.pack(side="left")
        
        status_label = ctk.CTkLabel(
            info_frame,
            text="ocupado",
            font=("Arial", 10, "bold"),
            text_color="#e74c3c"
        )
        status_label.pack(side="right")
        
        if self.fragmentation > 0:
            frag_label = ctk.CTkLabel(
                parent,
                text=f"Frag: {self.fragmentation} MB",
                font=("Arial", 9, "italic"),
                text_color="#f39c12"
            )
            frag_label.pack(anchor="w", pady=(2, 0))
        
        if self.on_release_callback:
            btn_release = ctk.CTkButton(
                parent,
                text="Liberar",
                command=lambda: self.on_release_callback(self.partition_id),
                height=25,
                width=80,
                fg_color="#e74c3c",
                hover_color="#c0392b",
                font=("Arial", 9, "bold")
            )
            btn_release.pack(anchor="e", pady=(5, 0))
    
    def update_partition(
        self,
        is_free: bool,
        process_name: Optional[str] = None,
        process_size: Optional[int] = None,
        fragmentation: int = 0
    ):
        """Actualiza el estado de la partición y redibuja"""
        self.is_free = is_free
        self.process_name = process_name
        self.process_size = process_size
        self.fragmentation = fragmentation
        
        for widget in self.winfo_children():
            widget.destroy()
        
        if is_free:
            self.configure(border_color="#2ecc71", fg_color="#1a4d2e")
        else:
            self.configure(border_color="#3498db", fg_color="#1e3a5f")
        
        self._setup_ui()
