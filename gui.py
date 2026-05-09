import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
import os
import sys
import subprocess
from generator import Generator
from translator import Translator
from parser import SimpleParser

class C3DVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Compiladores: Generador de Código de Tres Direcciones")
        self.root.geometry("1150x750") # Ligeramente más ancha para los nuevos botones
        self.root.configure(bg="#2c3e50")

        self.setup_ui()

    def setup_ui(self):
        # Encabezado Estilizado
        header = tk.Frame(self.root, bg="#34495e", height=80)
        header.pack(fill="x")
        
        title = tk.Label(header, text="Generador de Código Intermedio (C3D)", 
                         font=("Segoe UI", 24, "bold"), bg="#34495e", fg="#ecf0f1")
        title.pack(pady=20)

        # Contenedor para las cajas de texto
        content_frame = tk.Frame(self.root, bg="#2c3e50")
        content_frame.pack(expand=True, fill="both", padx=30, pady=10)

        # Panel Izquierdo: Entrada de Código
        input_frame = tk.Frame(content_frame, bg="#2c3e50")
        input_frame.pack(side="left", expand=True, fill="both", padx=10)
        
        tk.Label(input_frame, text="CÓDIGO FUENTE:", bg="#2c3e50", fg="#bdc3c7", font=("Arial", 10, "bold")).pack(anchor="w")
        self.input_text = scrolledtext.ScrolledText(input_frame, width=45, height=25, 
                                                    font=("Consolas", 12), undo=True, bg="#ffffff")
        self.input_text.pack(expand=True, fill="both", pady=5)
        # Ejemplo por defecto
        self.input_text.insert(tk.INSERT, "// Escribe o carga tu código aquí\nx = 10;\nwhile (a < b) {\n    c = a + b * 5;\n}")

        # Panel Derecho: Salida C3D y Paso a Paso
        output_frame = tk.Frame(content_frame, bg="#2c3e50")
        output_frame.pack(side="right", expand=True, fill="both", padx=10)

        tk.Label(output_frame, text="RESULTADOS (PASO A PASO Y C3D):", bg="#2c3e50", fg="#2ecc71", font=("Arial", 10, "bold")).pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(output_frame, width=50, height=25, 
                                                    font=("Consolas", 12, "bold"), fg="#2ecc71", bg="#1e1e1e")
        self.output_text.pack(expand=True, fill="both", pady=5)

        # Barra de Herramientas (Botones)
        toolbar = tk.Frame(self.root, bg="#2c3e50", pady=20)
        toolbar.pack(fill="x")

        btn_open = tk.Button(toolbar, text="📂 ABRIR .TXT", command=self.load_file, 
                            bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15, relief="flat")
        btn_open.pack(side="left", padx=10)

        btn_create = tk.Button(toolbar, text="➕ CREAR OPERACIÓN", command=self.open_create_dialog, 
                              bg="#9b59b6", fg="white", font=("Arial", 10, "bold"), width=18, relief="flat")
        btn_create.pack(side="left", padx=10)

        btn_clear = tk.Button(toolbar, text="🧹 LIMPIAR", command=self.clear_screens, 
                             bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=12, relief="flat")
        btn_clear.pack(side="left", padx=10)

        # --- NUEVO BOTÓN PARA MOSTRAR LA GRÁFICA DAG ---
        btn_dag = tk.Button(toolbar, text="📊 VER GRAFO DAG", command=self.show_dag_image, 
                             bg="#f1c40f", fg="black", font=("Arial", 10, "bold"), width=18, relief="flat")
        btn_dag.pack(side="left", padx=10)

        btn_compile = tk.Button(toolbar, text="⚙️ GENERAR C3D", command=self.process_code, 
                               bg="#e67e22", fg="white", font=("Arial", 14, "bold"), width=18, relief="flat")
        btn_compile.pack(side="right", padx=15)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'r') as f:
                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.INSERT, f.read())

    def clear_screens(self):
        self.input_text.delete(1.0, tk.END)
        self.output_text.config(state="normal")
        self.output_text.delete(1.0, tk.END)
        self.output_text.config(state="disabled")

    def open_create_dialog(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Nueva Operación")
        dialog.geometry("500x250")
        dialog.configure(bg="#34495e")
        dialog.transient(self.root) 
        dialog.grab_set() 

        tk.Label(dialog, text="Ingresa tu operación matemática:", bg="#34495e", fg="white", font=("Arial", 12, "bold")).pack(pady=15)
        tk.Label(dialog, text="Ejemplo 3 números: a + b + c\nEjemplo complejo: 5 + 2 - (3 * 5) + 3 - 2 + 1", bg="#34495e", fg="#bdc3c7", font=("Arial", 10)).pack(pady=5)

        entry_expr = tk.Entry(dialog, font=("Consolas", 14), width=40)
        entry_expr.pack(pady=10)

        def save_and_load():
            expr = entry_expr.get().strip()
            if not expr:
                messagebox.showwarning("Vacío", "Debes ingresar una operación.", parent=dialog)
                return

            code_to_save = f"// Operación generada desde la interfaz\nresultado = {expr};\n"

            file_path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt")],
                title="Guardar operación como",
                parent=dialog
            )

            if file_path:
                with open(file_path, 'w') as f:
                    f.write(code_to_save)

                self.input_text.delete(1.0, tk.END)
                self.input_text.insert(tk.INSERT, code_to_save)
                dialog.destroy()
                messagebox.showinfo("Éxito", "Operación guardada y cargada exitosamente.")

        tk.Button(dialog, text="💾 GUARDAR Y CARGAR .TXT", command=save_and_load, 
                  bg="#2ecc71", fg="white", font=("Arial", 10, "bold"), relief="flat", pady=5).pack(pady=15)

    # --- NUEVA FUNCIÓN PARA ABRIR LA IMAGEN DEL DAG ---
    def show_dag_image(self):
        image_path = 'dag_output.png' # Este es el nombre que le daremos a la imagen en generator.py
        if os.path.exists(image_path):
            try:
                if os.name == 'nt': # Para Windows
                    os.startfile(image_path)
                else: # Para macOS y Linux
                    opener = "open" if sys.platform == "darwin" else "xdg-open"
                    subprocess.call([opener, image_path])
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo abrir la imagen: {e}")
        else:
            messagebox.showinfo("Grafo no encontrado", "Aún no se ha generado un grafo DAG. Ejecuta 'GENERAR C3D' primero.")

    def process_code(self):
        raw_code = self.input_text.get(1.0, tk.END).strip()
        if not raw_code:
            messagebox.showwarning("Vacío", "Por favor ingresa código.")
            return

        gen = Generator()
        trans = Translator(gen)
        parser = SimpleParser()

        try:
            structure = parser.parse_full_code(raw_code)
            trans.translate_program(structure)

            # --- PREPARAMOS LA PANTALLA PARA RECIBIR EL PASO A PASO Y EL C3D ---
            self.output_text.config(state="normal")
            self.output_text.delete(1.0, tk.END)
            
            final_output = ""
            
            # Si el generator tiene el método del paso a paso (que agregaremos luego), lo imprimimos primero
            if hasattr(gen, 'get_math_steps'):
                steps = gen.get_math_steps()
                if steps:
                    final_output += "=== PASO A PASO MATEMÁTICO ===\n"
                    final_output += steps + "\n\n"
            
            final_output += "=== CÓDIGO DE TRES DIRECCIONES ===\n"
            final_output += gen.get_code()
            
            # Si el generator tiene el método para crear la imagen, lo ejecutamos
            if hasattr(gen, 'generate_dag_image'):
                gen.generate_dag_image()

            self.output_text.insert(tk.INSERT, final_output)
            self.output_text.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error de Análisis", f"Hubo un problema procesando el código:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = C3DVisualizer(root)
    root.mainloop()