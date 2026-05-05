import tkinter as tk
from gui import C3DVisualizer

def main():
    """
    Punto de entrada principal para la aplicación del 
    Generador de Código de Tres Direcciones (C3D).
    """
    try:
        # 1. Crear la ventana principal de Tkinter
        root = tk.Tk()
        
        # 2. Inicializar la interfaz gráfica (que a su vez usa el Parser, Translator y Generator)
        app = C3DVisualizer(root)
        
        # 3. Mantener la ventana abierta y escuchando eventos
        print("Iniciando el Generador C3D...")
        root.mainloop()
        
    except Exception as e:
        print(f"Error al iniciar la aplicación: {e}")

if __name__ == "__main__":
    main()