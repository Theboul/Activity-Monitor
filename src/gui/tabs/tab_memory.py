"""
Pestaña de Administración de Memoria
Interfaz para simulación semi-real de particiones fijas y variables
"""
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Optional
from src.backend.adm_memory import MemoryMonitor, MemoryAlgorithm, PartitionType
from ..components import MemoryVector, MemoryStatsPanel


class MemoryTab(ctk.CTkFrame):
    """Pestaña que contiene el simulador de administración de memoria"""
    
    def __init__(self, parent, memory_monitor: MemoryMonitor, **kwargs):
        super().__init__(parent, **kwargs)
        self.memory_monitor = memory_monitor
        self.memory_monitor.set_callback(self._on_memory_update)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario"""
        # Layout: izquierda (config + procesos), centro (vector), derecha (stats)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self._create_config_panel()
        self._create_vector_panel()
        self._create_stats_panel()
    
    # ==================== PANEL DE CONFIGURACIÓN ====================
    
    def _create_config_panel(self):
        """Panel izquierdo: configuración y procesos"""
        left_frame = ctk.CTkFrame(self)
        left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Título
        ctk.CTkLabel(left_frame, text="Configuracion", font=("Arial", 16, "bold")).pack(pady=(10, 5))
        
        # Frame principal para selectores (dos columnas)
        selectors_frame = ctk.CTkFrame(left_frame)
        selectors_frame.pack(fill="x", padx=10, pady=10)
        selectors_frame.grid_columnconfigure(0, weight=1)
        selectors_frame.grid_columnconfigure(1, weight=1)
        
        # Columna izquierda: Tipo de particiones
        type_column = ctk.CTkFrame(selectors_frame, fg_color="transparent")
        type_column.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        ctk.CTkLabel(type_column, text="Tipo de Particiones:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.partition_type_var = tk.StringVar(value="fixed")
        self.fixed_radio = ctk.CTkRadioButton(type_column, text="Fijas", variable=self.partition_type_var, value="fixed", command=self._on_partition_type_change)
        self.fixed_radio.pack(anchor="w", padx=10, pady=2)
        self.variable_radio = ctk.CTkRadioButton(type_column, text="Variables", variable=self.partition_type_var, value="variable", command=self._on_partition_type_change)
        self.variable_radio.pack(anchor="w", padx=10, pady=2)
        
        # Columna derecha: Algoritmo de asignación
        algorithm_column = ctk.CTkFrame(selectors_frame, fg_color="transparent")
        algorithm_column.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        ctk.CTkLabel(algorithm_column, text="Algoritmo de Asignación:", font=("Arial", 12, "bold")).pack(anchor="w", pady=(0, 5))
        self.algorithm_var = ctk.StringVar(value="first_fit")
        self.ff_radio = ctk.CTkRadioButton(algorithm_column, text="First Fit", variable=self.algorithm_var, value="first_fit")
        self.ff_radio.pack(anchor="w", padx=10, pady=2)
        self.bf_radio = ctk.CTkRadioButton(algorithm_column, text="Best Fit", variable=self.algorithm_var, value="best_fit", state="disabled")
        self.bf_radio.pack(anchor="w", padx=10, pady=2)        
        # Frame para configuración de particiones fijas
        self.fixed_config_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        self.fixed_config_frame.pack(fill="x", padx=10, pady=5)
        
        # Configurar grid para 3 columnas
        self.fixed_config_frame.grid_columnconfigure(0, weight=1)
        self.fixed_config_frame.grid_columnconfigure(1, weight=1)
        self.fixed_config_frame.grid_columnconfigure(2, weight=1)
        
        # Memoria Total
        ctk.CTkLabel(self.fixed_config_frame, text="Total (MB):", font=("Arial", 10)).grid(row=0, column=0, sticky="w", padx=(0, 2))
        self.fixed_total_entry = ctk.CTkEntry(self.fixed_config_frame, placeholder_text="2048", width=80)
        self.fixed_total_entry.grid(row=1, column=0, sticky="ew", padx=(0, 2))
        
        # Tamaño Partición
        ctk.CTkLabel(self.fixed_config_frame, text="Tamaño (MB):", font=("Arial", 10)).grid(row=0, column=1, sticky="w", padx=2)
        self.fixed_size_entry = ctk.CTkEntry(self.fixed_config_frame, placeholder_text="512", width=80)
        self.fixed_size_entry.grid(row=1, column=1, sticky="ew", padx=2)
        
        # Cantidad Particiones
        ctk.CTkLabel(self.fixed_config_frame, text="Cantidad:", font=("Arial", 10)).grid(row=0, column=2, sticky="w", padx=(2, 0))
        self.fixed_num_entry = ctk.CTkEntry(self.fixed_config_frame, placeholder_text="4", width=80)
        self.fixed_num_entry.grid(row=1, column=2, sticky="ew", padx=(2, 0))
        
        # Frame para configuración de particiones variables
        self.variable_config_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        
        ctk.CTkLabel(self.variable_config_frame, text="Memoria Total (MB):", font=("Arial", 11)).pack(anchor="w")
        self.variable_total_entry = ctk.CTkEntry(self.variable_config_frame, placeholder_text="2048")
        self.variable_total_entry.pack(fill="x", pady=2)
        
        # Botón para configurar (inicializa el sistema de memoria)
        self.configure_button = ctk.CTkButton(
            left_frame, 
            text="🚀 Configurar Memoria", 
            command=self._configure_memory, 
            fg_color="#2ecc71", 
            hover_color="#27ae60", 
            height=35,
            font=("Arial", 12, "bold")
        )
        self.configure_button.pack(fill="x", padx=10, pady=10)
        
        # Botón para reiniciar simulación (inicialmente deshabilitado)
        self.restart_button = ctk.CTkButton(
            left_frame,
            text="🔄 Reiniciar Simulación",
            command=self._restart_simulation,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            height=35,
            font=("Arial", 12, "bold"),
            state="disabled"
        )
        self.restart_button.pack(fill="x", padx=10, pady=(0, 10))
        
        # Lista de procesos del sistema
        ctk.CTkLabel(left_frame, text="Procesos del Sistema", font=("Arial", 14, "bold")).pack(pady=(5, 5))
        
        # Botones de carga y refresh
        load_buttons_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        load_buttons_frame.pack(fill="x", padx=10, pady=5)
        load_buttons_frame.grid_columnconfigure(0, weight=1)
        load_buttons_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(
            load_buttons_frame,
            text="🔄 Cargar Procesos",
            command=self._load_processes,
            height=30,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        ).grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        ctk.CTkButton(
            load_buttons_frame,
            text="🔃 Refrescar Lista",
            command=self._refresh_processes,
            height=35,
            fg_color="#3498db",
            hover_color="#2980b9"
        ).grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Frame scrollable para los procesos (altura limitada)
        self.process_list = ctk.CTkScrollableFrame(left_frame, label_text="Procesos Disponibles", height=180)
        self.process_list.pack(fill="both", expand=False, padx=10, pady=5)
        
        # Label para procesos seleccionados
        selected_info_frame = ctk.CTkFrame(left_frame)
        selected_info_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            selected_info_frame,
            text="Procesos Seleccionados:",
            font=("Arial", 11, "bold")
        ).pack(side="left", padx=5)
        
        self.selected_count_label = ctk.CTkLabel(
            selected_info_frame,
            text="0",
            font=("Arial", 11),
            text_color="#3498db"
        )
        self.selected_count_label.pack(side="left", padx=5)
        
        # Botones de asignación
        btn_frame = ctk.CTkFrame(left_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=10, pady=5)
        btn_frame.grid_columnconfigure(0, weight=1)
        btn_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkButton(btn_frame, text="Asignar (FF)", command=lambda: self._assign_processes(MemoryAlgorithm.FIRST_FIT), height=30, fg_color="#3498db").grid(row=0, column=0, padx=(0, 5), sticky="ew")
        
        # Botón para Best Fit (solo variables)
        self.bf_button = ctk.CTkButton(btn_frame, text="Asignar (BF)", command=lambda: self._assign_processes(MemoryAlgorithm.BEST_FIT), height=30, fg_color="#9b59b6")
        self.bf_button.grid(row=0, column=1, padx=(5, 0), sticky="ew")
        
        # Botón para limpiar selección
        ctk.CTkButton(
            left_frame,
            text="🗑️ Limpiar Selección",
            command=self._clear_selection,
            height=30,
            fg_color="darkred",
            hover_color="#8B0000"
        ).pack(pady=5, padx=10, fill="x")
        
    # ==================== PANEL DEL VECTOR ====================
    
    def _create_vector_panel(self):
        """Panel central: vector de memoria"""
        center_frame = ctk.CTkFrame(self)
        center_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(center_frame, text="Vector de Memoria", font=("Arial", 16, "bold")).pack(pady=(10, 5))
        
        self.memory_vector = MemoryVector(center_frame, on_release_callback=self._on_release_partition)
        self.memory_vector.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ==================== PANEL DE ESTADÍSTICAS ====================
    
    def _create_stats_panel(self):
        """Panel derecho: estadísticas"""
        right_frame = ctk.CTkFrame(self)
        right_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        self.stats_panel = MemoryStatsPanel(right_frame)
        self.stats_panel.pack(fill="both", expand=True, padx=10, pady=10)
    
    # ==================== EVENTOS ====================
    
    def _on_partition_type_change(self):
        """Cambia la configuración según el tipo seleccionado"""
        if self.partition_type_var.get() == "fixed":
            # Ocultar variables
            self.variable_config_frame.pack_forget()
            # Mostrar fijas ANTES del botón de configurar
            self.fixed_config_frame.pack(fill="x", padx=10, pady=5, before=self.configure_button)
            # Deshabilitar Best Fit
            self.bf_button.configure(state="disabled")
            self.algorithm_var.set("first_fit")
            self.bf_radio.configure(state="disabled")
        else:
            # Ocultar fijas
            self.fixed_config_frame.pack_forget()
            # Mostrar variables ANTES del botón de configurar
            self.variable_config_frame.pack(fill="x", padx=10, pady=5, before=self.configure_button)
            # Habilitar Best Fit
            self.bf_button.configure(state="normal")
            self.bf_radio.configure(state="normal")
    
    def _configure_memory(self):
        """Configura la memoria según el tipo seleccionado"""
        try:
            if self.partition_type_var.get() == "fixed":
                total = int(self.fixed_total_entry.get() or 2048)
                size = int(self.fixed_size_entry.get() or 512)
                num = int(self.fixed_num_entry.get() or 4)
                self.memory_monitor.setup_fixed_partitions(total, size, num)
                messagebox.showinfo("Éxito", f"Particiones fijas configuradas: {num} x {size} MB")
            else:
                total = int(self.variable_total_entry.get() or 2048)
                self.memory_monitor.setup_variable_partitions(total)
                messagebox.showinfo("Éxito", f"Particiones variables configuradas: {total} MB")
            
            # Actualizar vector y estadísticas
            self._update_vector()
            stats = self.memory_monitor.get_statistics()
            self._update_stats(stats)
            
            # Bloquear configuración y habilitar reinicio
            self._lock_configuration()
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def _load_processes(self):
        """Carga y muestra los procesos reales del sistema"""
        # Limpiar lista actual
        for widget in self.process_list.winfo_children():
            widget.destroy()
        
        # Obtener procesos reales
        data = self.memory_monitor.collect_data()
        real_procs = data.get("real_processes", [])
        
        if not real_procs:
            ctk.CTkLabel(
                self.process_list,
                text="No se pudieron cargar procesos",
                text_color="red"
            ).pack(pady=10)
            return
        
        # Mostrar solo los primeros 50 para no saturar la UI
        for proc in real_procs[:50]:
            self._create_process_item(proc)
        
        messagebox.showinfo("Éxito", f"Cargados {len(real_procs[:50])} procesos del sistema")
    
    def _create_process_item(self, proc):
        """Crea un item visual para un proceso"""
        frame = ctk.CTkFrame(self.process_list)
        frame.pack(fill="x", pady=2, padx=5)
        
        # Info del proceso
        info_label = ctk.CTkLabel(
            frame,
            text=f"{proc['name'][:20]} - {proc['memory_mb']} MB",
            font=("Arial", 10),
            anchor="w"
        )
        info_label.pack(side="left", fill="x", expand=True, padx=5)
        
        # PID en gris
        pid_label = ctk.CTkLabel(
            frame,
            text=f"PID:{proc['pid']}",
            font=("Arial", 9),
            text_color="gray"
        )
        pid_label.pack(side="left", padx=5)
        
        # Botón para agregar
        add_btn = ctk.CTkButton(
            frame,
            text="+",
            command=lambda p=proc: self._add_process(p),
            width=30,
            height=25,
            fg_color="#2ecc71",
            hover_color="#27ae60"
        )
        add_btn.pack(side="right", padx=5)
    
    def _add_process(self, proc_data):
        """Agrega un proceso a la simulación y lo asigna automáticamente"""
        try:
            # 1. Agregar proceso a la lista interna
            process = self.memory_monitor.add_process_from_real(
                proc_data["pid"], 
                proc_data["name"], 
                proc_data["memory_mb"]
            )
            
            # 2. Obtener algoritmo seleccionado
            algorithm = MemoryAlgorithm.FIRST_FIT if self.algorithm_var.get() == "first_fit" else MemoryAlgorithm.BEST_FIT
            
            # 3. Intentar asignar inmediatamente
            if self.memory_monitor.partition_type == PartitionType.FIXED:
                success = self.memory_monitor.fixed_manager.assign_process(process)
            else:
                success = self.memory_monitor.variable_manager.assign_process(process, algorithm)
            
            # 4. Actualizar interfaz visual
            self._update_vector()
            stats = self.memory_monitor.get_statistics()
            self._update_stats(stats)
            
            # 5. Actualizar contador
            count = len(self.memory_monitor.selected_processes)
            self.selected_count_label.configure(text=str(count))
            
            # 6. Notificar al usuario
            if success:
                messagebox.showinfo(
                    "✓ Asignado", 
                    f"Proceso: {proc_data['name']}\n"
                    f"Tamaño: {proc_data['memory_mb']} MB\n"
                    f"Algoritmo: {algorithm.value}\n"
                    f"Estado: Asignado correctamente"
                )
            else:
                frag_info = self.memory_monitor.calculate_fragmentation()
                messagebox.showwarning(
                    "⚠ No Asignado", 
                    f"Proceso: {proc_data['name']}\n"
                    f"Tamaño: {proc_data['memory_mb']} MB\n"
                    f"Razón: No hay espacio suficiente\n\n"
                    f"Fragmentación: {frag_info['description']}"
                )
                
        except ValueError as e:
            messagebox.showwarning("Advertencia", str(e))
    
    def _refresh_processes(self):
        """Recarga la lista de procesos del sistema"""
        # Limpiar la lista visual
        for widget in self.process_list.winfo_children():
            widget.destroy()
        
        # Recargar procesos
        self._load_processes()
    
    def _clear_selection(self):
        """Limpia todos los procesos seleccionados"""
        self.memory_monitor.clear_selected_processes()
        self.selected_count_label.configure(text="0")
        self._update_vector()
        stats = self.memory_monitor.get_statistics()
        self._update_stats(stats)
        messagebox.showinfo("Limpiado", "Selección de procesos limpiada")
    
    def _assign_processes(self, algorithm: MemoryAlgorithm):
        """Asigna los procesos usando el algoritmo especificado"""
        try:
            result = self.memory_monitor.assign_processes(algorithm)
            assigned = len(result["assigned_processes"])
            failed = len(result["failed_processes"])
            messagebox.showinfo("Resultado", f"Asignados: {assigned}\nFallidos: {failed}")
            self._update_vector()
            self._update_stats(result["statistics"])
        except ValueError as e:
            messagebox.showerror("Error", str(e))
    
    def _on_release_partition(self, partition_id: int):
        """Libera una partición y gestiona huecos disponibles"""
        try:
            partitions = self.memory_monitor._get_current_partitions()
            partition = next((p for p in partitions if p.id == partition_id), None)
            
            if not partition:
                messagebox.showerror("Error", f"No se encontró la partición {partition_id}")
                return
                
            if not partition.process:
                messagebox.showwarning("Advertencia", "Esta partición ya está libre")
                return
            
            # Guardar info del proceso antes de liberar
            proc_name = partition.process.name
            proc_size = partition.process.memory_size
            proc_pid = partition.process.pid
            
            # Liberar proceso (esto también lo elimina de selected_processes)
            self.memory_monitor.release_process(proc_pid)
            
            # Actualizar interfaz completa
            self._update_vector()
            stats = self.memory_monitor.get_statistics()
            frag_info = self.memory_monitor.calculate_fragmentation()
            self._update_stats(stats)
            
            # Actualizar contador de procesos seleccionados
            count = len(self.memory_monitor.selected_processes)
            self.selected_count_label.configure(text=str(count))
            
            # Notificar con detalles
            messagebox.showinfo(
                "✓ Proceso Cerrado",
                f"Proceso: {proc_name} (PID: {proc_pid})\n"
                f"Memoria liberada: {proc_size} MB\n"
                f"Fragmentación: {frag_info['description']}\n\n"
                f"El proceso ha sido cerrado y el espacio liberado"
            )
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def _on_memory_update(self, data):
        """Callback cuando el monitor actualiza"""
        self._update_stats(data.get("statistics", {}))
    
    # ==================== CONTROL DE CONFIGURACIÓN ====================
    
    def _lock_configuration(self):
        """Bloquea los controles de configuración después de iniciar la simulación"""
        # Deshabilitar radio buttons de tipo de partición
        self.fixed_radio.configure(state="disabled")
        self.variable_radio.configure(state="disabled")
        
        # Deshabilitar radio buttons de algoritmo
        self.ff_radio.configure(state="disabled")
        self.bf_radio.configure(state="disabled")
        
        # Deshabilitar campos de entrada para particiones fijas
        self.fixed_total_entry.configure(state="disabled")
        self.fixed_size_entry.configure(state="disabled")
        self.fixed_num_entry.configure(state="disabled")
        
        # Deshabilitar campo de entrada para particiones variables
        self.variable_total_entry.configure(state="disabled")
        
        # Deshabilitar botón de configurar
        self.configure_button.configure(state="disabled")
        
        # Habilitar botón de reinicio
        self.restart_button.configure(state="normal")
    
    def _unlock_configuration(self):
        """Desbloquea los controles de configuración para permitir cambios"""
        # Habilitar radio buttons de tipo de partición
        self.fixed_radio.configure(state="normal")
        self.variable_radio.configure(state="normal")
        
        # Habilitar radio button de First Fit siempre
        self.ff_radio.configure(state="normal")
        
        # Habilitar Best Fit solo si es variable
        if self.partition_type_var.get() == "variable":
            self.bf_radio.configure(state="normal")
        else:
            self.bf_radio.configure(state="disabled")
        
        # Habilitar campos de entrada para particiones fijas
        self.fixed_total_entry.configure(state="normal")
        self.fixed_size_entry.configure(state="normal")
        self.fixed_num_entry.configure(state="normal")
        
        # Habilitar campo de entrada para particiones variables
        self.variable_total_entry.configure(state="normal")
        
        # Habilitar botón de configurar
        self.configure_button.configure(state="normal")
        
        # Deshabilitar botón de reinicio
        self.restart_button.configure(state="disabled")
    
    def _restart_simulation(self):
        """Reinicia completamente la simulación y desbloquea la configuración"""
        # Confirmar con el usuario
        respuesta = messagebox.askyesno(
            "Confirmar Reinicio",
            "¿Está seguro de que desea reiniciar la simulación?\n\n"
            "Se perderán todos los datos y configuraciones actuales."
        )
        
        if not respuesta:
            return
        
        try:
            # 1. Limpiar memoria del monitor
            self.memory_monitor.selected_processes.clear()
            self.memory_monitor.fixed_manager = None
            self.memory_monitor.variable_manager = None
            self.memory_monitor.partition_type = None
            
            # 2. Limpiar vector visual
            if hasattr(self.memory_vector, 'clear_partitions'):
                self.memory_vector.clear_partitions()
            else:
                self.memory_vector.load_partitions([])
            
            # 3. Limpiar lista de procesos
            for widget in self.process_list.winfo_children():
                widget.destroy()
            
            # 4. Resetear contador de procesos seleccionados
            self.selected_count_label.configure(text="0")
            
            # 5. Limpiar estadísticas
            self.stats_panel.update_stats({
                "total_memory": 0,
                "used_memory": 0,
                "free_memory": 0,
                "num_processes": 0,
                "fragmentation": {
                    "type": "none",
                    "description": "No configurado",
                    "internal_fragmentation": 0,
                    "external_fragmentation": 0
                }
            })
            
            # 6. Resetear valores de entrada a defaults
            self.fixed_total_entry.delete(0, 'end')
            self.fixed_size_entry.delete(0, 'end')
            self.fixed_num_entry.delete(0, 'end')
            self.variable_total_entry.delete(0, 'end')
            
            # 7. Resetear tipo de partición a fijas
            self.partition_type_var.set("fixed")
            self._on_partition_type_change()
            
            # 8. Resetear algoritmo a First Fit
            self.algorithm_var.set("first_fit")
            
            # 9. Desbloquear configuración
            self._unlock_configuration()
            
            messagebox.showinfo(
                "Reinicio Exitoso",
                "La simulación ha sido reiniciada correctamente.\n\n"
                "Puede configurar nuevamente la memoria."
            )
            
        except Exception as e:
            messagebox.showerror("Error al Reiniciar", f"Ocurrió un error: {str(e)}")
    
    # ==================== ACTUALIZACIÓN UI ====================
    
    def _update_vector(self):
        """Actualiza el vector de memoria"""
        partitions = self.memory_monitor._get_current_partitions()
        partitions_data = [p.to_dict() for p in partitions]
        self.memory_vector.load_partitions(partitions_data)
    
    def _update_stats(self, stats):
        """Actualiza el panel de estadísticas"""
        frag_info = self.memory_monitor.calculate_fragmentation()
        stats_with_frag = {**stats, "fragmentation": frag_info}
        self.stats_panel.update_stats(stats_with_frag)
