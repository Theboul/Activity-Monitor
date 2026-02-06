"""
Panel de estadísticas de memoria (mem avail, max avail, fragmentación)
"""
import customtkinter as ctk
from typing import Dict, Any


class MemoryStatsPanel(ctk.CTkFrame):
    """Panel que muestra estadísticas de la memoria simulada"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color="#2b2b2b", border_width=2, border_color="#34495e", corner_radius=10, **kwargs)
        self._setup_ui()
    
    def _setup_ui(self):
        ctk.CTkLabel(self, text="Estadisticas", font=("Arial", 14, "bold")).pack(pady=(10, 15))
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))
        
        self._create_stat("Mem. Total:", "0 MB", "total")
        self._create_stat("Mem Avail:", "0 MB", "available", "#2ecc71")
        self._create_stat("Max Avail:", "0 MB", "max_available", "#3498db")
        ctk.CTkFrame(self.stats_frame, height=2, fg_color="#34495e").pack(fill="x", pady=10)
        self._create_stat("Mem. Usada:", "0 MB", "used", "#9b59b6")
        self._create_stat("Fragmentacion:", "0 MB", "fragmentation", "#f39c12")
        ctk.CTkFrame(self.stats_frame, height=2, fg_color="#34495e").pack(fill="x", pady=10)
        self._create_stat("Proc. Asignados:", "0", "assigned")
        self._create_stat("Part. Libres:", "0", "free_partitions", "#2ecc71")
        self._create_stat("Uso:", "0%", "usage_percent", "#e74c3c")
    
    def _create_stat(self, label_text: str, default_value: str, key: str, value_color: str = "#ecf0f1"):
        row = ctk.CTkFrame(self.stats_frame, fg_color="transparent")
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=label_text, font=("Arial", 11), text_color="#bdc3c7", anchor="w").pack(side="left")
        value_label = ctk.CTkLabel(row, text=default_value, font=("Arial", 11, "bold"), text_color=value_color, anchor="e")
        value_label.pack(side="right")
        setattr(self, f"_{key}_label", value_label)
    
    def update_stats(self, stats: Dict[str, Any]):
        if "total_memory" in stats:
            self._total_label.configure(text=f"{stats['total_memory']} MB")
        if "free_memory" in stats:
            self._available_label.configure(text=f"{stats['free_memory']} MB")
        if "largest_free_space" in stats:
            self._max_available_label.configure(text=f"{stats['largest_free_space']} MB")
        if "used_memory" in stats:
            self._used_label.configure(text=f"{stats['used_memory']} MB")
        if "fragmentation" in stats:
            frag = stats["fragmentation"]
            val = frag.get("internal_fragmentation", 0) if frag["type"] == "Interna" else frag.get("external_fragmentation", 0)
            self._fragmentation_label.configure(text=f"{val} MB")
        if "assigned_processes" in stats:
            self._assigned_label.configure(text=str(stats["assigned_processes"]))
        if "free_partitions" in stats:
            self._free_partitions_label.configure(text=str(stats["free_partitions"]))
        if "usage_percent" in stats:
            p = stats["usage_percent"]
            self._usage_percent_label.configure(text=f"{p}%", text_color="#2ecc71" if p < 50 else "#f39c12" if p < 75 else "#e74c3c")
