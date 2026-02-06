"""
Pestaña de Administración de Archivos USB
Interfaz para detectar unidades y gestionar archivos (RF-003)
"""
import customtkinter as ctk
from tkinter import messagebox
import os

class USBTab(ctk.CTkFrame):
    def __init__(self, parent, usb_monitor, **kwargs):
        super().__init__(parent, **kwargs)
        self.usb_monitor = usb_monitor
        self._setup_ui()
        
        # Configurar el callback para recibir datos del monitor en tiempo real
        if self.usb_monitor:
            self.usb_monitor.set_callback(self._on_data_received)

    def _setup_ui(self):
        """Configura la interfaz basada en el diseño de la pizarra"""
        # Título principal: Información de la unidad
        self.unit_label = ctk.CTkLabel(
            self, 
            text="Unidad USB: No detectada", 
            font=("Arial", 18, "bold"),
            text_color="#3399FF"
        )
        self.unit_label.pack(pady=15)

        # Contenedor para la lista de archivos (RF-003.2)
        self.file_list_frame = ctk.CTkScrollableFrame(
            self, 
            label_text="Explorador de Archivos",
            label_font=("Arial", 13, "bold"),
            fg_color="#1f1f1f"
        )
        self.file_list_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # Panel de botones de acción (Copiado de la pizarra)
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=15)

        # Botones de gestión de archivos
        self.btn_copy = ctk.CTkButton(btn_frame, text="Copiar", width=100, command=self._on_copy)
        self.btn_copy.pack(side="left", padx=5)

        self.btn_paste = ctk.CTkButton(btn_frame, text="Pegar", width=100, command=self._on_paste)
        self.btn_paste.pack(side="left", padx=5)

        self.btn_move = ctk.CTkButton(btn_frame, text="Mover", width=100, command=self._on_move)
        self.btn_move.pack(side="left", padx=5)

        # Botón de formateo con color de advertencia
        self.btn_format = ctk.CTkButton(
            btn_frame, 
            text="Formatear", 
            fg_color="#e74c3c", 
            hover_color="#c0392b",
            command=self._on_format
        )
        self.btn_format.pack(side="right", padx=5)

    # --- MANEJO DE DATOS EN TIEMPO REAL ---

    def _on_data_received(self, data):
        """Recibe datos del monitor y programa la actualización de la UI"""
        # Usamos after(0) para asegurar que la actualización ocurra en el hilo principal
        self.after(0, self._update_ui, data)

    def _update_ui(self, data):
        """Actualiza las etiquetas y la lista de archivos"""
        if data and len(data) > 0:
            device = data[0]  # Tomamos la primera unidad detectada
            self.unit_label.configure(
                text=f"Unidad USB: {device['unit']} | Libre: {device['free']} GB / {device['total']} GB"
            )
            
            # Actualizar lista de archivos si han cambiado
            self._refresh_file_list(device.get('files', []))
        else:
            self.unit_label.configure(text="Unidad USB: No detectada")
            self._refresh_file_list([])

    def _refresh_file_list(self, files):
        """Limpia y repuebla la lista visual de archivos"""
        # Limpiar widgets actuales
        for widget in self.file_list_frame.winfo_children():
            widget.destroy()
        
        if not files:
            ctk.CTkLabel(self.file_list_frame, text="No hay archivos o unidad desconectada", text_color="gray").pack(pady=20)
            return

        for file in files:
            file_item = ctk.CTkFrame(self.file_list_frame, fg_color="transparent")
            file_item.pack(fill="x", pady=2)
            ctk.CTkLabel(file_item, text=f"📄 {file}", font=("Arial", 11)).pack(side="left", padx=10)

    # --- MÉTODOS DE ACCIÓN (Resuelven el AttributeError) ---

    def _on_copy(self):
        """Lógica para copiar archivos"""
        print("[INFO] Ejecutando comando: Copiar")
        # Aquí se integrará shutil.copy2 en el futuro

    def _on_paste(self):
        """Lógica para pegar archivos"""
        print("[INFO] Ejecutando comando: Pegar")

    def _on_move(self):
        """Lógica para mover archivos"""
        print("[INFO] Ejecutando comando: Mover")

    def _on_format(self):
        """Lógica de formateo con confirmación de seguridad"""
        confirm = messagebox.askyesno(
            "⚠️ Acción Crítica", 
            "¿Estás seguro de que deseas FORMATEAR la unidad?\nTodos los datos se perderán permanentemente."
        )
        if confirm:
            print("[INFO] Iniciando proceso de formateo...")
            # Aquí se llama al método del backend: self.usb_monitor.execute_format()