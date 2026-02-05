"""
Ventana emergente para mostrar resultados de algoritmos de planificación
"""
import customtkinter as ctk
from typing import Dict, Any
from CTkTable import CTkTable


class ResultsWindow(ctk.CTkToplevel):
    """Ventana emergente para mostrar resultados detallados de algoritmos"""
    
    def __init__(self, parent, results: Dict[str, Any], is_comparison: bool = False):
        super().__init__(parent)
        
        self.results = results
        self.is_comparison = is_comparison
        
        # Configuración de la ventana
        if is_comparison:
            self.title("🔬 Comparación de Algoritmos")
            width = 1100
            height = 600
        else:
            algorithm = results.get('algorithm', 'Unknown')
            self.title(f"📊 Resultados - {algorithm}")
            width = 1100
            height = 600
        
        # Centrar la ventana en la pantalla
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        
        # Aplicar geometría con tamaño y posición
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        # Configurar para que aparezca al frente
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
        
        # Forzar foco
        self.lift()
        self.focus_force()
        
        # Crear contenido
        self._setup_ui()
        
    def _setup_ui(self):
        """Configura la interfaz de la ventana"""
        # Frame principal con scroll
        main_frame = ctk.CTkScrollableFrame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        if self.is_comparison:
            self._display_comparison(main_frame)
        else:
            self._display_results(main_frame)
        
        # Botones de acción en la parte inferior
        self._create_action_buttons()
    
    def _display_results(self, container):
        """Muestra los resultados de un algoritmo individual"""
        algorithm = self.results.get('algorithm', 'Unknown')
        stats = self.results.get('statistics', {})
        processes = self.results.get('processes', [])
        execution = self.results.get('execution_order', [])
        
        # ============ SECUENCIA DE EJECUCIÓN ============
        seq_frame = ctk.CTkFrame(container)
        seq_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            seq_frame,
            text="🔄 SECUENCIA DE EJECUCIÓN",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        # Mostrar secuencia resumida
        if "Round Robin" in algorithm:
            # Para RR, mostrar secuencia más compacta
            unique_sequence = []
            prev_name = None
            for ex in execution:
                if ex['name'] != prev_name:
                    unique_sequence.append(ex['name'])
                    prev_name = ex['name']
            sequence_text = " → ".join(unique_sequence[:20])
            if len(unique_sequence) > 20:
                sequence_text += " → ..."
        else:
            # Para FIFO y SJF, mostrar secuencia completa
            sequence_text = " → ".join([f"{ex['name']}" for ex in execution])
        
        ctk.CTkLabel(
            seq_frame,
            text=sequence_text,
            font=("Arial", 11, "bold"),
            wraplength=1000
        ).pack(pady=10, padx=10)
        
        # Detalles específicos por algoritmo
        if "Round Robin" in algorithm:
            self._display_round_robin_details(seq_frame, execution)
        elif "FIFO" in algorithm:
            self._display_fifo_details(seq_frame, execution)
        elif "SJF" in algorithm:
            self._display_sjf_details(seq_frame, execution)
        
        # ============ TABLA DE PROCESOS ============
        table_frame = ctk.CTkFrame(container)
        table_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            table_frame,
            text="📋 TABLA DE PROCESOS",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        # Preparar datos de la tabla
        table_data = [
            ["PID", "Proceso", "Tll", "Ts", "Tf", "Tr", "Te"]
        ]
        
        for proc in processes:
            table_data.append([
                str(proc['pid']),
                proc['name'][:20],
                str(proc['arrival_time']),
                str(proc['burst_time']),
                str(proc['completion_time']),
                str(proc['turnaround_time']),
                str(proc['waiting_time'])
            ])
        
        # Crear tabla
        table = CTkTable(
            table_frame,
            values=table_data,
            colors=["#2b2b2b", "#1f1f1f"],
            header_color="#1a472a" if "FIFO" in algorithm else "#1a3a52" if "SJF" in algorithm else "#5a1a1a",
            hover_color="#2d4739"
        )
        table.pack(padx=10, pady=10)
        
        # ============ ESTADÍSTICAS ============
        stats_frame = ctk.CTkFrame(container)
        stats_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            stats_frame,
            text="📊 ESTADÍSTICAS",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        # Grid de estadísticas
        stats_grid = ctk.CTkFrame(stats_frame)
        stats_grid.pack(fill="x", padx=10, pady=5)
        stats_grid.grid_columnconfigure(0, weight=1)
        stats_grid.grid_columnconfigure(1, weight=1)
        stats_grid.grid_columnconfigure(2, weight=1)
        
        # Estadísticas principales
        self._create_stat_card(
            stats_grid, 
            "⏱️ Tiempo de Espera Promedio (Te)", 
            str(stats.get('avg_waiting_time', 0)), 
            0, 0
        )
        self._create_stat_card(
            stats_grid, 
            "⏱️ Tiempo de Retorno Promedio (Tr)", 
            str(stats.get('avg_turnaround_time', 0)), 
            0, 1
        )
        self._create_stat_card(
            stats_grid, 
            "⏱️ Tiempo Total", 
            str(stats.get('total_time', 0)), 
            0, 2
        )
        
        # Información adicional para Round Robin
        if 'quantum' in self.results:
            quantum_frame = ctk.CTkFrame(stats_frame)
            quantum_frame.pack(fill="x", padx=10, pady=5)
            quantum_frame.grid_columnconfigure(0, weight=1)
            quantum_frame.grid_columnconfigure(1, weight=1)
            quantum_frame.grid_columnconfigure(2, weight=1)
            
            self._create_stat_card(
                quantum_frame,
                "🔄 Quantum",
                str(self.results['quantum']),
                0, 0
            )
            self._create_stat_card(
                quantum_frame,
                "🔀 Cambios de Contexto",
                str(stats.get('context_switches', 0)),
                0, 1
            )
            self._create_stat_card(
                quantum_frame,
                "🔁 Total de Vueltas",
                str(stats.get('total_rounds', 0)),
                0, 2
            )
    
    def _display_comparison(self, container):
        """Muestra la comparación de algoritmos"""
        comp = self.results.get('comparison', {})
        
        # ============ TÍTULO ============
        title_frame = ctk.CTkFrame(container)
        title_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            title_frame,
            text="🔬 COMPARACIÓN DE ALGORITMOS",
            font=("Arial", 18, "bold")
        ).pack(pady=10)
        
        # ============ TABLA COMPARATIVA ============
        table_frame = ctk.CTkFrame(container)
        table_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            table_frame,
            text="📊 TABLA COMPARATIVA",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        table_data = [
            ["Algoritmo", "T. Espera (Te)", "T. Retorno (Tr)", "Tiempo Total"]
        ]
        
        for algo, stats in comp.items():
            table_data.append([
                algo,
                str(stats['avg_waiting_time']),
                str(stats['avg_turnaround_time']),
                str(stats['total_time'])
            ])
        
        table = CTkTable(
            table_frame,
            values=table_data,
            colors=["#2b2b2b", "#1f1f1f"],
            header_color="#5a1a5a",
            hover_color="#3d2d3d"
        )
        table.pack(padx=10, pady=10)
        
        # ============ ANÁLISIS ============
        analysis_frame = ctk.CTkFrame(container)
        analysis_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            analysis_frame,
            text="💡 ANÁLISIS COMPARATIVO",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        # Mejores métricas
        best_wait = min(comp.items(), key=lambda x: x[1]['avg_waiting_time'])
        best_turn = min(comp.items(), key=lambda x: x[1]['avg_turnaround_time'])
        
        # Grid de mejores
        best_grid = ctk.CTkFrame(analysis_frame)
        best_grid.pack(fill="x", padx=10, pady=5)
        best_grid.grid_columnconfigure(0, weight=1)
        best_grid.grid_columnconfigure(1, weight=1)
        
        self._create_winner_card(
            best_grid,
            "⭐ Menor Tiempo de Espera",
            best_wait[0],
            str(best_wait[1]['avg_waiting_time']),
            0, 0
        )
        
        self._create_winner_card(
            best_grid,
            "⭐ Menor Tiempo de Retorno",
            best_turn[0],
            str(best_turn[1]['avg_turnaround_time']),
            0, 1
        )
        
        # ============ CONCLUSIONES ============
        conc_frame = ctk.CTkFrame(container)
        conc_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(
            conc_frame,
            text="📌 CONCLUSIONES",
            font=("Arial", 16, "bold")
        ).pack(pady=(10, 5))
        
        conclusions = ctk.CTkTextbox(conc_frame, height=150, font=("Arial", 12))
        conclusions.pack(fill="x", padx=10, pady=5)
        
        conclusions.insert("end", "• FIFO (First In First Out):\n")
        conclusions.insert("end", "  - Algoritmo más simple, ejecuta en orden de llegada\n")
        conclusions.insert("end", "  - Puede causar tiempos de espera largos (efecto convoy)\n\n")
        
        conclusions.insert("end", "• SJF (Shortest Job First):\n")
        conclusions.insert("end", "  - Minimiza el tiempo de espera promedio\n")
        conclusions.insert("end", "  - Favorece procesos cortos, puede causar inanición\n\n")
        
        conclusions.insert("end", "• Round Robin:\n")
        conclusions.insert("end", "  - Más equitativo, mejor para sistemas interactivos\n")
        conclusions.insert("end", "  - Más cambios de contexto, overhead adicional\n")
        
        conclusions.configure(state="disabled")
    
    def _display_round_robin_details(self, parent, execution):
        """Muestra detalles organizados por vueltas para Round Robin"""
        # Agrupar ejecuciones por vuelta
        rounds_dict = {}
        for ex in execution:
            round_num = ex.get('round', 1)
            if round_num not in rounds_dict:
                rounds_dict[round_num] = []
            rounds_dict[round_num].append(ex)
        
        # Frame scrollable para las vueltas
        details_frame = ctk.CTkScrollableFrame(parent, height=150)
        details_frame.pack(fill="both", padx=10, pady=5, expand=False)
        
        # Mostrar cada vuelta
        for round_num in sorted(rounds_dict.keys()):
            round_frame = ctk.CTkFrame(details_frame)
            round_frame.pack(fill="x", pady=2, padx=5)
            
            # Encabezado de la vuelta
            header_text = f"🔁 Vuelta {round_num}:"
            ctk.CTkLabel(
                round_frame,
                text=header_text,
                font=("Arial", 11, "bold"),
                anchor="w"
            ).pack(side="left", padx=5)
            
            # Procesos en esta vuelta
            processes_in_round = " → ".join([
                f"{ex['name']} (t={ex['start']}-{ex['end']}, rest={ex.get('remaining', 0)})"
                for ex in rounds_dict[round_num]
            ])
            
            ctk.CTkLabel(
                round_frame,
                text=processes_in_round,
                font=("Courier", 10),
                text_color="gray",
                anchor="w"
            ).pack(side="left", padx=10)
    
    def _display_fifo_details(self, parent, execution):
        """Muestra detalles de FIFO de forma clara"""
        details_frame = ctk.CTkFrame(parent, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        timeline = " | ".join([
            f"{ex['name']} ({ex['start']}-{ex['end']})"
            for ex in execution
        ])
        
        ctk.CTkLabel(
            details_frame,
            text=f"⏱️ Línea de tiempo: {timeline}",
            font=("Courier", 10),
            text_color="gray",
            wraplength=1000
        ).pack(pady=5)
    
    def _display_sjf_details(self, parent, execution):
        """Muestra detalles de SJF destacando el orden de ejecución"""
        details_frame = ctk.CTkFrame(parent, fg_color="transparent")
        details_frame.pack(fill="x", padx=10, pady=5)
        
        timeline = " | ".join([
            f"{ex['name']} [Ts={ex['burst']}] ({ex['start']}-{ex['end']})"
            for ex in execution
        ])
        
        ctk.CTkLabel(
            details_frame,
            text=f"⏱️ Orden por ráfaga: {timeline}",
            font=("Courier", 10),
            text_color="gray",
            wraplength=1000
        ).pack(pady=5)
    
    def _create_stat_card(self, parent, label: str, value: str, row: int, col: int):
        """Crea una tarjeta de estadística"""
        card = ctk.CTkFrame(parent, corner_radius=10)
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(
            card,
            text=label,
            font=("Arial", 11),
            text_color="gray"
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 18, "bold")
        ).pack(pady=(0, 10))
    
    def _create_winner_card(self, parent, title: str, algorithm: str, value: str, row: int, col: int):
        """Crea una tarjeta de ganador para comparación"""
        card = ctk.CTkFrame(parent, corner_radius=10, fg_color="#1a3a1a")
        card.grid(row=row, column=col, padx=5, pady=5, sticky="ew")
        
        ctk.CTkLabel(
            card,
            text=title,
            font=("Arial", 11, "bold"),
            text_color="#2ecc71"
        ).pack(pady=(10, 0))
        
        ctk.CTkLabel(
            card,
            text=algorithm,
            font=("Arial", 16, "bold")
        ).pack(pady=(5, 0))
        
        ctk.CTkLabel(
            card,
            text=value,
            font=("Arial", 13),
            text_color="gray"
        ).pack(pady=(0, 10))
    
    def _create_action_buttons(self):
        """Crea los botones de acción en la parte inferior"""
        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # Botón de cerrar
        ctk.CTkButton(
            btn_frame,
            text="❌ Cerrar",
            command=self.destroy,
            height=35,
            fg_color="#e74c3c",
            hover_color="#c0392b"
        ).pack(side="right", padx=5)
    
    def _show_message(self, message: str):
        """Muestra un mensaje temporal"""
        from tkinter import messagebox
        messagebox.showinfo("Información", message)
