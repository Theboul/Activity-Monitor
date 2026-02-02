"""
Pestaña de Simulación de Procesos
Interfaz para el simulador semi-real de algoritmos de despacho
"""
import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Dict, Any


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
        
        # Botón para cargar procesos
        btn_load = ctk.CTkButton(
            left_frame,
            text="🔄 Cargar Procesos del Sistema",
            command=self._load_real_processes,
            height=35
        )
        btn_load.pack(pady=5, padx=10, fill="x")
        
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
        
        # Área de resultados (scrollable)
        results_label = ctk.CTkLabel(
            right_frame,
            text="Resultados de la Simulación",
            font=("Arial", 13, "bold")
        )
        results_label.pack(pady=(10, 5))
        
        self.results_text = ctk.CTkTextbox(
            right_frame,
            font=("Courier New", 11),
            wrap="word"
        )
        self.results_text.pack(fill="both", expand=True, padx=10, pady=5)
        self.results_text.insert("1.0", "Selecciona procesos y ejecuta un algoritmo para ver los resultados...")
        self.results_text.configure(state="disabled")
    
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
        self._display_results(results)
    
    def _run_sjf(self):
        """Ejecuta el algoritmo SJF"""
        if not self.process_monitor.selected_processes:
            self._show_message("⚠️ Selecciona al menos un proceso", "warning")
            return
        
        results = self.process_monitor.run_sjf()
        self._display_results(results)
    
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
        self._display_results(results)
    
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
        self._display_comparison(comparison)
    
    def _display_results(self, results: Dict[str, Any]):
        """Muestra los resultados de un algoritmo en el textbox"""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        
        algorithm = results.get('algorithm', 'Unknown')
        stats = results.get('statistics', {})
        processes = results.get('processes', [])
        execution = results.get('execution_order', [])
        
        # Título
        output = f"{'='*60}\n"
        output += f"  ALGORITMO: {algorithm}\n"
        output += f"{'='*60}\n\n"
        
        # Información del quantum si es Round Robin
        if 'quantum' in results:
            output += f"⏱️  Quantum: {results['quantum']}\n\n"
        
        # Tabla de procesos
        output += "📋 TABLA DE PROCESOS:\n"
        output += "-" * 60 + "\n"
        output += f"{'Proceso':<20} {'Burst':>6} {'Espera':>8} {'Retorno':>8}\n"
        output += "-" * 60 + "\n"
        
        for proc in processes:
            name = proc['name'][:18]
            output += f"{name:<20} {proc['burst_time']:>6} {proc['waiting_time']:>8} {proc['turnaround_time']:>8}\n"
        
        output += "-" * 60 + "\n\n"
        
        # Orden de ejecución
        output += "⚡ ORDEN DE EJECUCIÓN:\n"
        for i, exec_info in enumerate(execution, 1):
            output += f"  {i}. {exec_info['name']} [{exec_info['start']}→{exec_info['end']}]"
            if 'remaining' in exec_info:
                output += f" (quedan {exec_info['remaining']})"
            output += "\n"
        
        output += "\n"
        
        # Estadísticas
        output += "📊 ESTADÍSTICAS:\n"
        output += f"  • Tiempo Promedio de Espera:    {stats.get('avg_waiting_time', 0):.2f}\n"
        output += f"  • Tiempo Promedio de Retorno:   {stats.get('avg_turnaround_time', 0):.2f}\n"
        output += f"  • Tiempo Total de Ejecución:    {stats.get('total_time', 0)}\n"
        
        if 'context_switches' in stats:
            output += f"  • Cambios de Contexto:          {stats['context_switches']}\n"
        
        self.results_text.insert("1.0", output)
        self.results_text.configure(state="disabled")
    
    def _display_comparison(self, comparison: Dict[str, Any]):
        """Muestra la comparación de los tres algoritmos"""
        self.results_text.configure(state="normal")
        self.results_text.delete("1.0", "end")
        
        comp = comparison.get('comparison', {})
        
        output = f"{'='*60}\n"
        output += f"  🔬 COMPARACIÓN DE ALGORITMOS\n"
        output += f"{'='*60}\n\n"
        
        output += f"{'Algoritmo':<20} {'T.Espera':>12} {'T.Retorno':>12} {'T.Total':>10}\n"
        output += "-" * 60 + "\n"
        
        for algo, stats in comp.items():
            output += f"{algo:<20} {stats['avg_waiting_time']:>12.2f} {stats['avg_turnaround_time']:>12.2f} {stats['total_time']:>10}\n"
        
        output += "-" * 60 + "\n\n"
        
        # Análisis
        output += "💡 ANÁLISIS:\n\n"
        
        # Mejor tiempo de espera
        best_wait = min(comp.items(), key=lambda x: x[1]['avg_waiting_time'])
        output += f"⭐ Mejor Tiempo de Espera: {best_wait[0]}\n"
        output += f"   ({best_wait[1]['avg_waiting_time']:.2f} unidades)\n\n"
        
        # Mejor tiempo de retorno
        best_turn = min(comp.items(), key=lambda x: x[1]['avg_turnaround_time'])
        output += f"⭐ Mejor Tiempo de Retorno: {best_turn[0]}\n"
        output += f"   ({best_turn[1]['avg_turnaround_time']:.2f} unidades)\n\n"
        
        output += "📌 CONCLUSIONES:\n"
        output += "• FIFO: Simple pero puede causar esperas largas\n"
        output += "• SJF: Minimiza espera promedio, favorece procesos cortos\n"
        output += "• Round Robin: Equitativo, mejor para interactividad\n"
        
        self.results_text.insert("1.0", output)
        self.results_text.configure(state="disabled")
    
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
