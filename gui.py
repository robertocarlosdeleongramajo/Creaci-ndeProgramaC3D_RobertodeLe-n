import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox
from generator import Generator
from translator import Translator
from parser import SimpleParser

class C3DVisualizer:
    def __init__(self, root):
        self.root = root
        self.root.title("Compiladores: Generador de Código de Tres Direcciones")
        self.root.geometry("1100x750")
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
        # Ejemplo por defecto para la clase
        self.input_text.insert(tk.INSERT, "// Escribe o carga tu código aquí\nx = 10;\nwhile (a < b) {\n    c = a + b * 5;\n}")

        # Panel Derecho: Salida C3D
        output_frame = tk.Frame(content_frame, bg="#2c3e50")
        output_frame.pack(side="right", expand=True, fill="both", padx=10)

        tk.Label(output_frame, text="RESULTADO C3D (CON ANOTACIONES):", bg="#2c3e50", fg="#2ecc71", font=("Arial", 10, "bold")).pack(anchor="w")
        self.output_text = scrolledtext.ScrolledText(output_frame, width=50, height=25, 
                                                    font=("Consolas", 12, "bold"), fg="#2ecc71", bg="#1e1e1e")
        self.output_text.pack(expand=True, fill="both", pady=5)

        # Barra de Herramientas (Botones)
        toolbar = tk.Frame(self.root, bg="#2c3e50", pady=20)
        toolbar.pack(fill="x")

        btn_open = tk.Button(toolbar, text="📂 ABRIR .TXT", command=self.load_file, 
                            bg="#3498db", fg="white", font=("Arial", 10, "bold"), width=15, relief="flat")
        btn_open.pack(side="left", padx=30)

        btn_clear = tk.Button(toolbar, text="🧹 LIMPIAR", command=self.clear_screens, 
                             bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=15, relief="flat")
        btn_clear.pack(side="left", padx=10)

        btn_compile = tk.Button(toolbar, text="⚙️ GENERAR C3D", command=self.process_code, 
                               bg="#e67e22", fg="white", font=("Arial", 14, "bold"), width=25, relief="flat")
        btn_compile.pack(side="right", padx=30)

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

    def process_code(self):
        # 1. Obtener texto
        raw_code = self.input_text.get(1.0, tk.END).strip()
        if not raw_code:
            messagebox.showwarning("Vacío", "Por favor ingresa código.")
            return

        # 2. Inicializar los componentes actualizados
        gen = Generator()
        trans = Translator(gen)
        parser = SimpleParser()

        try:
            # 3. El Parser divide el código en bloques (Asignaciones, Whiles, Ifs)
            structure = parser.parse_full_code(raw_code)
            
            # 4. El Translator orquesta la traducción secuencial
            trans.translate_program(structure)

            # 5. Mostrar resultado en la pantalla "negra"
            self.output_text.config(state="normal")
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.INSERT, gen.get_code())
            self.output_text.config(state="disabled")
            
        except Exception as e:
            messagebox.showerror("Error de Análisis", f"Hubo un problema procesando el código:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = C3DVisualizer(root)
    root.mainloop()