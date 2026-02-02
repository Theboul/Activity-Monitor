"""
Componente de Diagrama de Gantt para visualizar ejecución de procesos
"""
import customtkinter as ctk
from typing import List, Dict, Any


class GanttChart(ctk.CTkCanvas):
    """Canvas personalizado para dibujar diagramas de Gantt"""
    
    def __init__(self, parent, **kwargs):
        super().__init__(
            parent,
            bg="#2b2b2b",
            highlightthickness=0,
            **kwargs
        )
        
        # Configuración de colores
        self.colors = [
            "#3498db",  # Azul
            "#e74c3c",  # Rojo
            "#2ecc71",  # Verde
            "#f39c12",  # Naranja
            "#9b59b6",  # Púrpura
            "#1abc9c",  # Turquesa
            "#34495e",  # Gris oscuro
            "#e67e22",  # Naranja oscuro
        ]
        
        # Configuración de layout
        self.scale = 30  # Pixels por unidad de tiempo
        self.bar_height = 40  # Altura de cada barra
        self.bar_spacing = 10  # Espacio entre barras
        self.margin_left = 150  # Margen izquierdo para nombres
        self.margin_top = 50  # Margen superior
        self.margin_bottom = 50  # Margen inferior para eje
        
    def draw_gantt(self, execution_order: List[Dict[str, Any]], algorithm_name: str = ""):
        """
        Dibuja el diagrama de Gantt basado en el orden de ejecución
        
        Args:
            execution_order: Lista con información de ejecución de cada proceso
            algorithm_name: Nombre del algoritmo
        """
        self.delete("all")  # Limpiar canvas
        
        if not execution_order:
            self._draw_empty_message()
            return
        
        # Calcular dimensiones
        max_time = int(max(exec_info['end'] for exec_info in execution_order))
        num_processes = len(set(exec_info['name'] for exec_info in execution_order))
        
        # Actualizar tamaño del canvas
        canvas_width = self.margin_left + (max_time * self.scale) + 50
        canvas_height = self.margin_top + (num_processes * (self.bar_height + self.bar_spacing)) + self.margin_bottom
        self.configure(width=canvas_width, height=canvas_height)
        
        # Dibujar título
        self._draw_title(algorithm_name)
        
        # Agrupar ejecuciones por proceso
        process_executions = {}
        for exec_info in execution_order:
            proc_name = exec_info['name']
            if proc_name not in process_executions:
                process_executions[proc_name] = []
            process_executions[proc_name].append(exec_info)
        
        # Dibujar cada proceso
        y_position = self.margin_top
        for idx, (proc_name, executions) in enumerate(process_executions.items()):
            color = self.colors[idx % len(self.colors)]
            self._draw_process_row(proc_name, executions, y_position, color, idx)
            y_position += self.bar_height + self.bar_spacing
        
        # Dibujar eje de tiempo
        self._draw_time_axis(max_time, y_position)
    
    def _draw_title(self, algorithm_name: str):
        """Dibuja el título del diagrama"""
        title = f"📊 DIAGRAMA DE GANTT"
        if algorithm_name:
            title += f" - {algorithm_name}"
        
        self.create_text(
            self.winfo_reqwidth() / 2,
            20,
            text=title,
            fill="#ffffff",
            font=("Arial", 14, "bold"),
            anchor="n"
        )
    
    def _draw_process_row(self, proc_name: str, executions: List[Dict], y: int, color: str, idx: int):
        """Dibuja una fila de proceso con sus ejecuciones"""
        # Dibujar nombre del proceso (lado izquierdo)
        self.create_text(
            10,
            y + self.bar_height / 2,
            text=proc_name,
            fill="#ffffff",
            font=("Arial", 10, "bold"),
            anchor="w"
        )
        
        # Dibujar PID si está disponible
        if executions and 'pid' in executions[0]:
            self.create_text(
                10,
                y + self.bar_height / 2 + 15,
                text=f"PID: {executions[0]['pid']}",
                fill="#888888",
                font=("Arial", 8),
                anchor="w"
            )
        
        # Dibujar cada segmento de ejecución
        for exec_info in executions:
            self._draw_execution_bar(exec_info, y, color)
    
    def _draw_execution_bar(self, exec_info: Dict, y: int, color: str):
        """Dibuja una barra de ejecución individual"""
        start = int(exec_info['start'])
        end = int(exec_info['end'])
        
        x1 = self.margin_left + (start * self.scale)
        x2 = self.margin_left + (end * self.scale)
        y1 = y
        y2 = y + self.bar_height
        
        # Dibujar rectángulo de la barra
        self.create_rectangle(
            x1, y1, x2, y2,
            fill=color,
            outline="#ffffff",
            width=2
        )
        
        # Dibujar texto con el tiempo
        text = f"{start} → {end}"
        text_x = (x1 + x2) / 2
        text_y = (y1 + y2) / 2
        
        # Fondo semi-transparente para el texto
        self.create_rectangle(
            text_x - 30, text_y - 10,
            text_x + 30, text_y + 10,
            fill="#000000",
            outline="",
            stipple="gray50"
        )
        
        self.create_text(
            text_x, text_y,
            text=text,
            fill="#ffffff",
            font=("Arial", 9, "bold")
        )
        
        # Mostrar tiempo restante si está disponible (Round Robin)
        if 'remaining' in exec_info and exec_info['remaining'] > 0:
            self.create_text(
                text_x, text_y + 18,
                text=f"({exec_info['remaining']} rest.)",
                fill="#ffff00",
                font=("Arial", 7)
            )
    
    def _draw_time_axis(self, max_time: int, y_position: int):
        """Dibuja el eje de tiempo en la parte inferior"""
        y = y_position + 20
        
        # Línea horizontal
        x_start = self.margin_left
        x_end = self.margin_left + (max_time * self.scale)
        self.create_line(
            x_start, y,
            x_end, y,
            fill="#888888",
            width=2
        )
        
        # Marcas de tiempo
        for t in range(0, max_time + 1, max(1, max_time // 20)):
            x = self.margin_left + (t * self.scale)
            
            # Línea vertical
            self.create_line(
                x, y - 5,
                x, y + 5,
                fill="#888888",
                width=2
            )
            
            # Número
            self.create_text(
                x, y + 15,
                text=str(t),
                fill="#ffffff",
                font=("Arial", 8)
            )
        
        # Etiqueta del eje
        self.create_text(
            (x_start + x_end) / 2,
            y + 35,
            text="Tiempo (unidades)",
            fill="#888888",
            font=("Arial", 10, "italic")
        )
    
    def _draw_empty_message(self):
        """Muestra un mensaje cuando no hay datos"""
        self.create_text(
            self.winfo_reqwidth() / 2,
            self.winfo_reqheight() / 2,
            text="No hay datos para mostrar\nEjecuta un algoritmo primero",
            fill="#888888",
            font=("Arial", 12),
            justify="center"
        )
