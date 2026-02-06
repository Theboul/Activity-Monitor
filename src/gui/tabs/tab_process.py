"""
Pestaña de Simulación de Procesos
Interfaz para el simulador semi-real de algoritmos de despacho
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any
from ..windows.results_window import ResultsWindow


class ProcessTab(ctk.CTkFrame):
    """Pestaña que contiene el simulador de procesos con los 3 algoritmos"""
    
    def __init__(self, parent, process_monitor, **kwargs):
        super().__init__(parent, **kwargs)
        self.process_monitor = process_monitor
        self.selected_process_items = []  # Para trackear procesos seleccionados
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario de la pestaña"""
        # Layout principal: izquierda (selección) y derecha (resultados)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # Panel izquierdo: Selección de procesos
        self._create_selection_panel()
        
        # Panel derecho: Resultados de simulación
        self._create_results_panel()
    
    def _create_selection_panel(self):
        """Crea el panel de selección de procesos reales"""
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Título
        title = ctk.CTkLabel(
            left_frame,
            text="🖥️ Procesos Reales del Sistema",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(10, 5))
        
        # Instrucciones
        instructions = ctk.CTkLabel(
            left_frame,
            text="Selecciona procesos para simular algoritmos",
            font=("Arial", 11),
            text_color="gray"
        )
        instructions.pack(pady=(0, 10))
        
        # Frame para la lista de procesos (con scrollbar)
        list_frame = ctk.CTkFrame(left_frame)
        list_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Scrollable frame para los procesos
        self.process_list = ctk.CTkScrollableFrame(
            list_frame,
            label_text="Procesos Disponibles",
            label_font=("Arial", 12, "bold")
        )
        self.process_list.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Frame para botones de carga
        buttons_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        buttons_frame.pack(pady=5, padx=10, fill="x")
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=1)
        
        # Botón para cargar procesos (primera vez)
        btn_load = ctk.CTkButton(
            buttons_frame,
            text="🔄 Cargar Procesos",
            command=self._load_real_processes,
            height=35,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        btn_load.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Botón para refrescar procesos
        btn_refresh = ctk.CTkButton(
            buttons_frame,
            text="🔃 Refrescar Lista",
            command=self._refresh_processes,
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        btn_refresh.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Frame para procesos seleccionados
        selected_frame = ctk.CTkFrame(left_frame)
        selected_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            selected_frame,
            text="Procesos Seleccionados:",
            font=("Arial", 12, "bold")
        ).pack(pady=5)
        
        self.selected_label = ctk.CTkLabel(
            selected_frame,
            text="0 procesos",
            font=("Arial", 11),
            text_color="gray"
        )
        self.selected_label.pack(pady=5)
        
        # Botón para limpiar selección
        btn_clear = ctk.CTkButton(
            left_frame,
            text="🗑️ Limpiar Selección",
            command=self._clear_selection,
            height=30,
            fg_color="darkred",
            hover_color="#8B0000"
        )
        btn_clear.pack(pady=5, padx=10, fill="x")
    
    def _create_results_panel(self):
        """Crea el panel de resultados y configuración de algoritmos"""
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        right_frame.grid_rowconfigure(1, weight=1)  # Permitir que el área de resultados se expanda
        
        # Título
        title = ctk.CTkLabel(
            right_frame,
            text="📊 Algoritmos de Planificación",
            font=("Arial", 16, "bold")
        )
        title.pack(pady=(10, 5))
        
        # Frame de configuración (Quantum para Round Robin)
        config_frame = ctk.CTkFrame(right_frame)
        config_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            config_frame,
            text="Quantum (Round Robin):",
            font=("Arial", 12)
        ).pack(side="left", padx=10, pady=5)
        
        self.quantum_entry = ctk.CTkEntry(
            config_frame,
            width=60,
            placeholder_text="2"
        )
        self.quantum_entry.pack(side="left", padx=5, pady=5)
        self.quantum_entry.insert(0, "2")
        
        # Botones de algoritmos
        algo_frame = ctk.CTkFrame(right_frame)
        algo_frame.pack(fill="x", padx=10, pady=10)
        
        btn_fifo = ctk.CTkButton(
            algo_frame,
            text="▶️ Ejecutar FIFO",
            command=self._run_fifo,
            height=40,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        btn_fifo.pack(fill="x", padx=5, pady=5)
        
        btn_sjf = ctk.CTkButton(
            algo_frame,
            text="▶️ Ejecutar SJF",
            command=self._run_sjf,
            height=40,
            fg_color="#3498db",
            hover_color="#2980b9"
        )
        btn_sjf.pack(fill="x", padx=5, pady=5)
        
        btn_rr = ctk.CTkButton(
            algo_frame,
            text="▶️ Ejecutar Round Robin",
            command=self._run_round_robin,
            height=40,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        )
        btn_rr.pack(fill="x", padx=5, pady=5)
        
        btn_compare = ctk.CTkButton(
            algo_frame,
            text="🔬 Comparar Todos",
            command=self._compare_algorithms,
            height=40,
            fg_color="#9b59b6",
            hover_color="#8e44ad"
        )
        btn_compare.pack(fill="x", padx=5, pady=10)
        
        # Mensaje informativo
        info_frame = ctk.CTkFrame(right_frame)
        info_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="ℹ️ Información",
            font=("Arial", 14, "bold")
        ).pack(pady=(20, 10))
        
        ctk.CTkLabel(
            info_frame,
            text="Los resultados se mostrarán en\nuna ventana emergente",
            font=("Arial", 12),
            text_color="gray"
        ).pack(pady=10)
        
        ctk.CTkLabel(
            info_frame,
            text="✓ Selecciona procesos del sistema\n"
                 "✓ Ejecuta un algoritmo\n"
                 "✓ Visualiza los resultados completos\n"
                 "✓ Compara múltiples algoritmos",
            font=("Arial", 11),
            text_color="#5a5a5a",
            justify="left"
        ).pack(pady=20)
    
    def _load_real_processes(self):
        """Carga y muestra los procesos reales del sistema"""
        # Limpiar lista actual
        for widget in self.process_list.winfo_children():
            widget.destroy()
        
        # Obtener procesos reales
        data = self.process_monitor.collect_data()
        processes = data.get('real_processes', [])
        
        if not processes:
            ctk.CTkLabel(
                self.process_list,
                text="No se pudieron cargar procesos",
                text_color="red"
            ).pack(pady=10)
            return
        
        # Mostrar solo los primeros 50 para no saturar la UI
        for proc in processes[:50]:
            self._create_process_item(proc)
        
        self._show_message(f"✅ Cargados {len(processes[:50])} procesos", "info")
    
    def _create_process_item(self, process: Dict[str, Any]):
        """Crea un item visual para un proceso"""
        frame = ctk.CTkFrame(self.process_list)
        frame.pack(fill="x", pady=2, padx=5)
        
        # Checkbox para selección
        var = ctk.BooleanVar()
        checkbox = ctk.CTkCheckBox(
            frame,
            text="",
            variable=var,
            width=20,
            command=lambda: self._on_process_selected(process, var.get())
        )
        checkbox.pack(side="left", padx=5)
        
        # Info del proceso
        info_text = f"{process['name']} (PID: {process['pid']})"
        label = ctk.CTkLabel(
            frame,
            text=info_text,
            font=("Arial", 10),
            anchor="w"
        )
        label.pack(side="left", fill="x", expand=True, padx=5)
        
        # Guardar referencia
        self.selected_process_items.append({
            'process': process,
            'var': var,
            'checkbox': checkbox,
            'frame': frame
        })
    
    def _on_process_selected(self, process: Dict[str, Any], selected: bool):
        """Callback cuando se selecciona/deselecciona un proceso"""
        if selected:
            try:
                # Agregar al monitor con burst aleatorio
                self.process_monitor.add_process_from_real(
                    pid=process['pid'],
                    name=process['name']
                )
                # Deshabilitar el checkbox para evitar duplicados
                self._disable_selected_checkbox(process['pid'])
            except ValueError as e:
                # Si hay un error (ej: proceso duplicado), desmarcar el checkbox
                for item in self.selected_process_items:
                    if item['process']['pid'] == process['pid']:
                        item['var'].set(False)
                        break
                self._show_message(f"⚠️ {str(e)}", "warning")
                return
        else:
            # Remover del monitor
            self.process_monitor.selected_processes = [
                p for p in self.process_monitor.selected_processes
                if p.pid != process['pid']
            ]
            # Rehabilitar el checkbox
            self._enable_selected_checkbox(process['pid'])
        
        # Actualizar contador
        count = len(self.process_monitor.selected_processes)
        self.selected_label.configure(text=f"{count} proceso{'s' if count != 1 else ''}")
    
    def _clear_selection(self):
        """Limpia todos los procesos seleccionados"""
        self.process_monitor.clear_selected_processes()
        
        # Desmarcar y rehabilitar todos los checkboxes
        for item in self.selected_process_items:
            item['var'].set(False)
            item['checkbox'].configure(state="normal")
        
        self.selected_label.configure(text="0 procesos")
        self._show_message("🗑️ Selección limpiada", "info")
    
    def _refresh_processes(self):
        """Recarga la lista de procesos del sistema y limpia la selección"""
        # Limpiar selección primero (porque los procesos anteriores ya no existen)
        self.process_monitor.clear_selected_processes()
        
        # Limpiar la lista visual
        for widget in self.process_list.winfo_children():
            widget.destroy()
        
        # Limpiar el tracking de items seleccionados
        self.selected_process_items.clear()
        
        # Recargar procesos del sistema
        data = self.process_monitor.collect_data()
        processes = data.get('real_processes', [])
        
        if not processes:
            ctk.CTkLabel(
                self.process_list,
                text="No se pudieron cargar procesos",
                text_color="red"
            ).pack(pady=10)
            self._show_message("❌ Error al cargar procesos", "error")
            return
        
        # Mostrar los procesos
        for proc in processes[:50]:
            self._create_process_item(proc)
        
        # Actualizar contador
        self.selected_label.configure(text="0 procesos")
        self._show_message(f"🔃 Lista actualizada: {len(processes[:50])} procesos disponibles", "info")
    
    def _disable_selected_checkbox(self, pid: int):
        """Deshabilita el checkbox de un proceso seleccionado"""
        for item in self.selected_process_items:
            if item['process']['pid'] == pid:
                item['checkbox'].configure(state="disabled")
                break
    
    def _enable_selected_checkbox(self, pid: int):
        """Habilita el checkbox de un proceso deseleccionado"""
        for item in self.selected_process_items:
            if item['process']['pid'] == pid:
                item['checkbox'].configure(state="normal")
                break
    
    def _run_fifo(self):
        """Ejecuta el algoritmo FIFO"""
        if not self.process_monitor.selected_processes:
            self._show_message("⚠️ Selecciona al menos un proceso", "warning")
            return
        
        results = self.process_monitor.run_fifo()
        self._open_results_window(results)
    
    def _run_sjf(self):
        """Ejecuta el algoritmo SJF"""
        if not self.process_monitor.selected_processes:
            self._show_message("⚠️ Selecciona al menos un proceso", "warning")
            return
        
        results = self.process_monitor.run_sjf()
        self._open_results_window(results)
    
    def _run_round_robin(self):
        """Ejecuta el algoritmo Round Robin"""
        if not self.process_monitor.selected_processes:
            self._show_message("⚠️ Selecciona al menos un proceso", "warning")
            return
        
        try:
            quantum = int(self.quantum_entry.get())
            if quantum <= 0:
                raise ValueError()
        except ValueError:
            self._show_message("⚠️ El quantum debe ser un número entero positivo", "warning")
            return
        
        results = self.process_monitor.run_round_robin(quantum)
        self._open_results_window(results)
    
    def _compare_algorithms(self):
        """Compara los tres algoritmos"""
        if not self.process_monitor.selected_processes:
            self._show_message("⚠️ Selecciona al menos un proceso", "warning")
            return
        
        try:
            quantum = int(self.quantum_entry.get())
            self.process_monitor.set_quantum(quantum)
        except ValueError:
            pass
        
        comparison = self.process_monitor.get_statistics_comparison()
        self._open_results_window(comparison, is_comparison=True)
    
    def _open_results_window(self, results: Dict[str, Any], is_comparison: bool = False):
        """Abre una ventana emergente con los resultados"""
        ResultsWindow(self, results, is_comparison)
    
    def _show_message(self, message: str, msg_type: str = "info"):
        """Muestra un mensaje temporal en la UI"""
        if msg_type == "warning":
            messagebox.showwarning("Advertencia", message)
        elif msg_type == "error":
            messagebox.showerror("Error", message)
        else:
            messagebox.showinfo("Información", message)
    
    def cleanup(self):
        """Limpia recursos cuando se cierra la pestaña"""
        print("[INFO] Limpiando ProcessTab...")
        
        # Limpiar procesos seleccionados
        if hasattr(self, 'process_monitor'):
            self.process_monitor.clear_selected_processes()
        
        # Limpiar referencias de items
        self.selected_process_items.clear()
        
        # Destruir widgets hijos del process_list
        if hasattr(self, 'process_list'):
            for widget in self.process_list.winfo_children():
                try:
                    widget.destroy()
                except:
                    pass
        
        print("[INFO] ProcessTab limpiado")
