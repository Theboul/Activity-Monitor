"""
Componente que muestra el vector de memoria como bloques apilados verticalmente
Compatible con particiones fijas y variables
"""
import customtkinter as ctk
from typing import List, Dict, Any, Callable, Optional
from .partition_block import PartitionBlock


class MemoryVector(ctk.CTkFrame):
    """Vector de memoria que muestra particiones como bloques apilados"""
    
    def __init__(self, parent, on_release_callback: Optional[Callable] = None, **kwargs):
        super().__init__(parent, fg_color="#2b2b2b", border_width=2, border_color="#34495e", corner_radius=10, **kwargs)
        self.on_release_callback = on_release_callback
        self.partition_blocks: Dict[int, PartitionBlock] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        header_frame = ctk.CTkFrame(self, fg_color="#34495e", corner_radius=8)
        header_frame.pack(fill="x", padx=5, pady=(5, 10))
        self.title_label = ctk.CTkLabel(header_frame, text="monitor", font=("Arial", 14, "bold"), text_color="white")
        self.title_label.pack(pady=8)
        self.partitions_container = ctk.CTkScrollableFrame(self, fg_color="transparent", scrollbar_button_color="#34495e")
        self.partitions_container.pack(fill="both", expand=True, padx=5, pady=(0, 5))
    
    def load_partitions(self, partitions: List[Dict[str, Any]]):
        self.clear_partitions()
        for p in partitions:
            process_name = process_size = None
            frag = p.get("internal_fragmentation", 0)
            if not p["is_free"] and p.get("process"):
                process_name = p["process"]["name"]
                process_size = p["process"]["memory_size"]
            block = PartitionBlock(self.partitions_container, p["id"], p["size"], p["is_free"], process_name, process_size, frag, self.on_release_callback)
            block.pack(fill="x", pady=3)
            self.partition_blocks[p["id"]] = block
    
    def clear_partitions(self):
        for w in self.partitions_container.winfo_children():
            w.destroy()
        self.partition_blocks.clear()
    
    def set_title(self, title: str):
        self.title_label.configure(text=title)
