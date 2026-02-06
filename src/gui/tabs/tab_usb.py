import customtkinter as ctk
from tkinter import messagebox, filedialog
import os

class USBTab(ctk.CTkFrame):
    def __init__(self, parent, usb_monitor, **kwargs):
        super().__init__(parent, **kwargs)
        self.usb_monitor = usb_monitor
        self.selected_file = None
        self.current_unit_path = ""
        self._setup_ui()
        if self.usb_monitor:
            self.usb_monitor.set_callback(self._on_data_received)

    def _setup_ui(self):
        self.unit_label = ctk.CTkLabel(self, text="Unidad USB: Buscando...", font=("Arial", 16, "bold"))
        self.unit_label.pack(pady=15)

        self.file_list = ctk.CTkScrollableFrame(self, label_text="Explorador de Archivos")
        self.file_list.pack(fill="both", expand=True, padx=20, pady=10)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=10)

        # Botones principales
        ctk.CTkButton(btn_frame, text="Copiar", command=self._on_copy, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Pegar", command=self._on_paste, width=100).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Mover", command=self._on_move, width=100).pack(side="left", padx=5)
        
        # NUEVO: Botón Eliminar
        ctk.CTkButton(btn_frame, text="Eliminar", fg_color="#e67e22", hover_color="#d35400", 
                      command=self._on_delete, width=100).pack(side="left", padx=5)
        
        ctk.CTkButton(btn_frame, text="Formatear", fg_color="#e74c3c", hover_color="#c0392b", 
                      command=self._on_format, width=100).pack(side="right", padx=5)

    def _on_data_received(self, data):
        self.after(0, self._update_ui, data)

    def _update_ui(self, data):
        if data:
            dev = data[0]
            self.current_unit_path = dev['unit']
            self.unit_label.configure(text=f"Unidad USB: {dev['unit']} ({dev['free']} GB Libres)")
            
            for widget in self.file_list.winfo_children(): widget.destroy()
            for f in dev['files']:
                btn = ctk.CTkButton(self.file_list, text=f"📄 {f}", anchor="w", fg_color="transparent", 
                                    command=lambda name=f: self._select_file(name))
                btn.pack(fill="x", padx=10, pady=2)
        else:
            self.unit_label.configure(text="Unidad USB: No detectada")

    def _select_file(self, filename):
        self.selected_file = os.path.join(self.current_unit_path, filename)
        print(f"Seleccionado: {self.selected_file}")

    def _on_copy(self):
        if self.selected_file:
            self.usb_monitor.set_to_clipboard(self.selected_file)
            messagebox.showinfo("Copiado", "Archivo en portapapeles.")
        else:
            messagebox.showwarning("Atención", "Selecciona un archivo.")

    def _on_paste(self):
        if self.current_unit_path and self.usb_monitor.paste_to(self.current_unit_path):
            messagebox.showinfo("Éxito", "Archivo pegado.")
        else:
            messagebox.showerror("Error", "No se pudo pegar.")

    def _on_move(self):
        if self.selected_file:
            dest = filedialog.askdirectory()
            if dest and self.usb_monitor.move_file(self.selected_file, dest):
                messagebox.showinfo("Éxito", "Archivo movido.")
        else:
            messagebox.showwarning("Atención", "Selecciona un archivo.")

    def _on_delete(self):
        """Lógica de eliminación con confirmación"""
        if self.selected_file:
            if messagebox.askyesno("Confirmar", f"¿Eliminar permanentemente {os.path.basename(self.selected_file)}?"):
                if self.usb_monitor.delete_file(self.selected_file):
                    messagebox.showinfo("Éxito", "Archivo eliminado.")
                    self.selected_file = None
        else:
            messagebox.showwarning("Atención", "Selecciona un archivo primero.")

    def _on_format(self):
        if messagebox.askyesno("⚠️ Peligro", "¿Formatear la unidad?"):
            self.usb_monitor.execute_format(self.current_unit_path)