import customtkinter as ctk
from tkinter import messagebox

class USBTab(ctk.CTkFrame):
    def __init__(self, parent, usb_monitor, **kwargs):
        super().__init__(parent, **kwargs)
        self.usb_monitor = usb_monitor
        self._setup_ui()
        # Conectamos el monitor con la interfaz
        if self.usb_monitor:
            self.usb_monitor.set_callback(self._on_data_received)

    def _setup_ui(self):
        """Diseño de la interfaz USB"""
        self.unit_label = ctk.CTkLabel(self, text="Unidad USB: Buscando...", font=("Arial", 16, "bold"))
        self.unit_label.pack(pady=15)

        self.file_list = ctk.CTkScrollableFrame(self, label_text="Explorador de Archivos")
        self.file_list.pack(fill="both", expand=True, padx=20, pady=10)

        # Botones de la pizarra
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        ctk.CTkButton(btn_frame, text="Copiar", command=self._on_copy).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Pegar", command=self._on_paste).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Mover", command=self._on_move).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Formatear", fg_color="#e74c3c", command=self._on_format).pack(side="right", padx=5)

    def _on_data_received(self, data):
        """Actualiza la UI cuando el monitor detecta cambios"""
        self.after(0, self._update_ui, data)

    def _update_ui(self, data):
        if data:
            dev = data[0]
            self.unit_label.configure(text=f"Unidad USB: {dev['unit']} ({dev['free']} GB Libres)")
            # Actualizar lista de archivos
            for widget in self.file_list.winfo_children(): widget.destroy()
            for f in dev['files']:
                ctk.CTkLabel(self.file_list, text=f"📄 {f}", anchor="w").pack(fill="x", padx=10)
        else:
            self.unit_label.configure(text="Unidad USB: No detectada")

    # Métodos requeridos por los botones
    def _on_copy(self): print("Copiar seleccionado")
    def _on_paste(self): print("Pegar seleccionado")
    def _on_move(self): print("Mover seleccionado")
    def _on_format(self):
        if messagebox.askyesno("⚠️ Confirmación", "¿Seguro que deseas formatear?"):
            self.usb_monitor.execute_format("F:")