"""
Pestaña de Administración de Memoria.

Replica el estilo de trabajo de tab_process aprovechando MemoryMonitor para
simular asignación dinámica con First Fit y Best Fit.
"""
from __future__ import annotations

import customtkinter as ctk
from tkinter import messagebox
from typing import Dict, Any

from src.backend.adm_memory.allocation_strategy import AllocationStrategy
from src.backend.adm_memory.memory_monitor import MemoryMonitor


class MemoryTab(ctk.CTkFrame):
    """Interfaz para visualizar y administrar la memoria simulada."""

    def __init__(self, parent, memory_monitor: MemoryMonitor, **kwargs):
        super().__init__(parent, **kwargs)
        self.memory_monitor = memory_monitor
        self.strategy_var = ctk.StringVar(value=AllocationStrategy.FIRST_FIT.value)
        self.summary_labels: Dict[str, ctk.CTkLabel] = {}
        self.block_list = None
        self.process_list_frame = None
        self.system_processes = []
        self.process_items = []
        self.assigned_process_names = set()

        self._setup_ui()
        self._load_system_processes()
        self.refresh_snapshot()

    # ------------------------------------------------------------------ #
    # Configuración de la UI

    def _setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)

        self._create_controls_panel()
        self._create_visual_panel()

    def _create_controls_panel(self):
        """Panel izquierdo con lista de procesos reales y acciones."""
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        panel.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            panel,
            text="⚙️ Configuración de Asignación",
            font=("Arial", 16, "bold"),
        ).pack(pady=(10, 5))

        config_frame = ctk.CTkFrame(panel)
        config_frame.pack(fill="x", padx=10, pady=10)

        ctk.CTkLabel(config_frame, text="Estrategia:", font=("Arial", 12)).pack(
            anchor="w", pady=(10, 2)
        )
        strategies = [strategy.value for strategy in AllocationStrategy]
        ctk.CTkOptionMenu(
            config_frame, variable=self.strategy_var, values=strategies
        ).pack(fill="x", pady=(0, 10))

        ctk.CTkButton(
            config_frame,
            text="🔄 Cargar procesos del sistema (Top 50 por RAM)",
            command=self._load_system_processes,
        ).pack(fill="x")

        self.process_list_frame = ctk.CTkScrollableFrame(
            panel,
            label_text="Procesos del Sistema",
            label_font=("Arial", 12, "bold"),
        )
        self.process_list_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

        actions_frame = ctk.CTkFrame(panel)
        actions_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkButton(
            actions_frame,
            text="🧱 Compactar",
            command=self._compact_memory,
            height=32,
            fg_color="#9b59b6",
            hover_color="#8e44ad",
        ).pack(fill="x", pady=3)

        ctk.CTkButton(
            actions_frame,
            text="🔄 Reiniciar",
            command=self._reset_memory,
            height=32,
            fg_color="#e67e22",
            hover_color="#d35400",
        ).pack(fill="x", pady=3)

    def _create_visual_panel(self):
        """Panel derecho con resumen y bloques."""
        panel = ctk.CTkFrame(self)
        panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            panel,
            text="📊 Estado de la Memoria",
            font=("Arial", 16, "bold"),
        ).pack(pady=(10, 5))

        summary_frame = ctk.CTkFrame(panel)
        summary_frame.pack(fill="x", padx=10, pady=10)
        summary_frame.grid_columnconfigure((0, 1, 2), weight=1)

        self.summary_labels["total"] = self._create_summary_card(
            summary_frame, "Total (Simulado MB)", row=0, col=0
        )
        self.summary_labels["used"] = self._create_summary_card(
            summary_frame, "Usado (Simulado MB)", row=0, col=1
        )
        self.summary_labels["free"] = self._create_summary_card(
            summary_frame, "Libre (Simulado MB)", row=0, col=2
        )
        self.summary_labels["largest_free_block"] = self._create_summary_card(
            summary_frame, "Bloque Libre Máx (MB)", row=1, col=0
        )
        self.summary_labels["fragmentation"] = self._create_summary_card(
            summary_frame, "Bloques Libres", row=1, col=1
        )

        ram_frame = ctk.CTkFrame(panel)
        ram_frame.pack(fill="x", padx=10, pady=(0, 10))
        ram_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self.summary_labels["ram_total"] = self._create_summary_card(
            ram_frame, "RAM Total (MB)", row=0, col=0
        )
        self.summary_labels["ram_used"] = self._create_summary_card(
            ram_frame, "RAM Usada (MB)", row=0, col=1
        )
        self.summary_labels["ram_available"] = self._create_summary_card(
            ram_frame, "RAM Disponible (MB)", row=0, col=2
        )
        self.summary_labels["ram_percent"] = self._create_summary_card(
            ram_frame, "Uso RAM (%)", row=0, col=3
        )

        # Lista de bloques
        self.block_list = ctk.CTkScrollableFrame(
            panel, label_text="Bloques de Memoria", label_font=("Arial", 13, "bold")
        )
        self.block_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))

    def _create_summary_card(self, parent, title: str, row: int, col: int):
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

        ctk.CTkLabel(
            card, text=title, font=("Arial", 12), text_color="gray"
        ).pack(pady=(8, 2))
        value_label = ctk.CTkLabel(card, text="0", font=("Arial", 20, "bold"))
        value_label.pack(pady=(0, 10))
        return value_label

    # ------------------------------------------------------------------ #
    # Actualización de datos

    def refresh_snapshot(self):
        """Obtiene datos actuales directamente del monitor para refrescar la UI."""
        data = self.memory_monitor.get_current_data()
        if data:
            self.update_memory_state(data)

    def update_memory_state(self, snapshot: Dict[str, Any]):
        """Metodo invocado por MonitorGUI cuando hay datos nuevos."""
        summary = snapshot.get("summary", {})
        system_ram = snapshot.get("system_ram", {})
        for key, label in self.summary_labels.items():
            if key.startswith("ram_"):
                value = system_ram.get(key.replace("ram_", ""), 0)
            else:
                value = summary.get(key, 0)
            label.configure(text=str(value))

        for widget in self.block_list.winfo_children():
            widget.destroy()

        blocks = snapshot.get("blocks", [])
        if not blocks:
            ctk.CTkLabel(
                self.block_list,
                text="Sin bloques registrados",
                text_color="gray",
            ).pack(pady=10)
            return

        self.assigned_process_names = {
            block.get("process") for block in blocks if not block.get("is_free")
        }
        for block in blocks:
            self._render_block(block)
        self._refresh_process_highlights()

    def _render_block(self, block: Dict[str, Any]):
        frame = ctk.CTkFrame(
            self.block_list,
            fg_color="#1f1f1f" if block.get("is_free") else "#2d3436",
            corner_radius=8,
        )
        frame.pack(fill="x", padx=8, pady=4)

        text_color = "#2ecc71" if block.get("is_free") else "#e67e22"
        ctk.CTkLabel(
            frame,
            text=block.get("label", ""),
            font=("Arial", 12, "bold"),
            text_color=text_color,
        ).pack(anchor="w", padx=10, pady=(6, 0))

        owner = block.get("process") or "???"
        status = "Libre" if block.get("is_free") else f"Ocupado por {owner}"
        details = (
            f"Inicio: {block.get('start')} MB | Tamaño: {block.get('size')} MB | Estado: {status}"
        )
        ctk.CTkLabel(
            frame,
            text=details,
            font=("Arial", 11),
            text_color="gray",
        ).pack(anchor="w", padx=10, pady=(0, 6))

    # ------------------------------------------------------------------ #
    # Acciones

    def _load_system_processes(self):
        """Obtiene procesos reales del sistema y los muestra en la UI."""
        self.system_processes = self.memory_monitor.get_real_processes()
        self.process_items.clear()
        for widget in self.process_list_frame.winfo_children():
            widget.destroy()

        if not self.system_processes:
            ctk.CTkLabel(
                self.process_list_frame,
                text="No fue posible cargar procesos del sistema",
                text_color="red",
            ).pack(pady=10)
            return

        for proc in self.system_processes:
            self._render_process_item(proc)

    def _render_process_item(self, process: Dict[str, Any]):
        frame = ctk.CTkFrame(self.process_list_frame)
        frame.pack(fill="x", padx=5, pady=3)

        info = f"{process['name']} (PID: {process['pid']}) - {process['memory_mb']} MB"
        label = ctk.CTkLabel(frame, text=info, anchor="w")
        label.pack(side="left", padx=5, pady=5, expand=True, fill="x")

        buttons = ctk.CTkFrame(frame, fg_color="transparent")
        buttons.pack(side="right", padx=5)

        ctk.CTkButton(
            buttons,
            text="Asignar",
            width=80,
            height=26,
            fg_color="#2ecc71",
            hover_color="#27ae60",
            command=lambda p=process: self._allocate_from_process(p),
        ).pack(pady=2)

        ctk.CTkButton(
            buttons,
            text="Liberar",
            width=80,
            height=26,
            fg_color="#3498db",
            hover_color="#2980b9",
            command=lambda p=process: self._release_process_by_name(self._format_process_name(p)),
        ).pack(pady=2)

        self.process_items.append({"label": label, "process": self._format_process_name(process)})

    def _allocate_from_process(self, process: Dict[str, Any]):
        process_name = self._format_process_name(process)
        size = max(1, int(process.get("memory_mb") or 1))
        try:
            strategy = AllocationStrategy.from_string(self.strategy_var.get())
            response = self.memory_monitor.allocate_process(process_name, size, strategy)
        except ValueError as exc:
            self._show_message(str(exc), "warning")
            return

        self._show_message(response["message"], "info" if response["success"] else "warning")
        self.refresh_snapshot()

    def _format_process_name(self, process: Dict[str, Any]) -> str:
        return f"{process['name']} (PID {process['pid']})"

    def _release_process_by_name(self, process_name: str):
        response = self.memory_monitor.release_process(process_name)
        self._show_message(response["message"], "info" if response["success"] else "warning")
        self.refresh_snapshot()

    def _compact_memory(self):
        response = self.memory_monitor.compact_memory()
        self._show_message(response["message"], "info")
        self.refresh_snapshot()

    def _reset_memory(self):
        answer = messagebox.askyesno(
            "Reiniciar memoria",
            "¿Deseas reiniciar la memoria al estado inicial? Se liberarán todos los procesos.",
        )
        if answer:
            self.memory_monitor.reset()
            self.refresh_snapshot()

    # ------------------------------------------------------------------ #
    # Utilidades

    def _show_message(self, message: str, level: str = "info"):
        if level == "warning":
            messagebox.showwarning("Administración de Memoria", message)
        elif level == "error":
            messagebox.showerror("Administración de Memoria", message)
        else:
            messagebox.showinfo("Administración de Memoria", message)

    def cleanup(self):
        """Método para liberar recursos cuando se cierra la app."""
        if self.block_list:
            for widget in self.block_list.winfo_children():
                widget.destroy()
        if self.process_list_frame:
            for widget in self.process_list_frame.winfo_children():
                widget.destroy()

    def _refresh_process_highlights(self):
        for item in self.process_items:
            label = item["label"]
            process_name = item["process"]
            if process_name in self.assigned_process_names:
                label.configure(text_color="#2ecc71")
            else:
                label.configure(text_color="white")
