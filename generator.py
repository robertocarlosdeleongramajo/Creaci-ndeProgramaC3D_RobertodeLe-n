import networkx as nx
import matplotlib.pyplot as plt

class Generator:
    """Administrador de Temporales, Etiquetas, Comentarios, DAG y Paso a Paso"""
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.instructions = []
        self.dag_connections = []
        self.math_steps = []

    def new_temporal(self):
        temp = f"t{self.temp_count}"
        self.temp_count += 1
        return temp

    def new_label(self):
        label = f"L{self.label_count}"
        self.label_count += 1
        return label

    def add_instruction(self, instruction):
        self.instructions.append(instruction)

    # --- FUNCIONES DEL CEREBRO MATEMÁTICO ---
    def add_math_step(self, left, op, right, result, target):
        step = f" ↳ Paso [{target}]: Se resolvió '{left} {op} {right}' dando como resultado {result}"
        self.math_steps.append(step)

    def get_math_steps(self):
        if not self.math_steps:
            return "No se detectaron operaciones aritméticas para resolver."
        return "\n".join(self.math_steps)

    # --- FUNCIONES DEL DAG ---
    def add_dag_connection(self, target, left, op, right):
        self.dag_connections.append({
            'target': target,
            'left': left,
            'op': op,
            'right': right
        })

    def generate_dag_image(self):
        """
        Genera una imagen PNG del grafo DAG utilizando librerías 100% Python 
        (NetworkX y Matplotlib), sin necesidad de instalar programas externos.
        """
        if not self.dag_connections:
            return

        try:
            # Creamos un grafo dirigido
            G = nx.DiGraph()
            labels = {}
            node_colors = []

            # 1. Construimos los nodos y las conexiones
            for conn in self.dag_connections:
                target = conn['target']
                op = conn['op']
                left = str(conn['left'])
                right = str(conn['right'])

                # Nodo temporal (padre)
                if target not in G:
                    G.add_node(target)
                    labels[target] = f"{target}\n({op})"
                
                # Nodos hijos
                if left not in G:
                    G.add_node(left)
                    labels[left] = left
                if right not in G:
                    G.add_node(right)
                    labels[right] = right

                # Conexiones
                G.add_edge(target, left)
                G.add_edge(target, right)

            # 2. Asignamos colores (Azul para temporales/operaciones, Gris para hojas/números)
            for node in G.nodes():
                if node.startswith('t') and node in labels and '\n' in labels[node]:
                    node_colors.append('#3498db') # Azul
                else:
                    node_colors.append('#ecf0f1') # Gris claro

            # 3. Dibujamos y guardamos el gráfico
            plt.figure(figsize=(8, 6))
            
            # Usamos un layout automático de NetworkX (spring_layout o planar_layout)
            pos = nx.spring_layout(G, seed=42) 
            
            nx.draw(
                G, pos, 
                with_labels=True, 
                labels=labels, 
                node_color=node_colors, 
                node_size=2000, 
                font_size=10, 
                font_weight='bold', 
                arrows=True,
                arrowsize=20,
                font_color='black'
            )
            
            plt.title("Representación del Grafo DAG (Generado con Python Puro)")
            
            # Guardamos la imagen para que la GUI la pueda abrir
            plt.savefig('dag_output.png', format='png', bbox_inches='tight')
            plt.close() # Cerramos para liberar memoria
            
        except Exception as e:
            print("\n" + "="*70)
            print("🚨 ERROR AL GENERAR LA IMAGEN 🚨")
            print("Asegúrate de haber instalado las librerías en tu consola con:")
            print("pip install networkx matplotlib")
            print("Detalle:", e)
            print("="*70 + "\n")

    def get_code(self):
        code_lines = []
        for inst in self.instructions:
            line = str(inst)
            comentario = getattr(inst, 'comment', '')
            if comentario:
                line = f"{line.ljust(30)} // {comentario}"
            code_lines.append(line)
            
        if self.dag_connections:
            code_lines.append("\n" + "="*45)
            code_lines.append(" MAPA DE TEXTO DEL DAG (Respaldo visual)")
            code_lines.append("="*45)
            for conn in self.dag_connections:
                code_lines.append(f"Nodo [{conn['target']}] ({conn['op']})")
                code_lines.append(f"  ├─ Izq: {conn['left']}")
                code_lines.append(f"  └─ Der: {conn['right']}")
                code_lines.append("-" * 45)
                
        return "\n".join(code_lines)

# --- Modelos de Instrucciones Mejorados ---

class ThreeAddressInstruction:
    def __init__(self, comment=""):
        self.comment = comment

class Assignment(ThreeAddressInstruction):
    def __init__(self, target, op1, operator=None, op2=None, comment=""):
        super().__init__(comment)
        self.target = target
        self.op1 = op1
        self.operator = operator
        self.op2 = op2

    def __str__(self):
        if self.operator:
            return f"{self.target} = {self.op1} {self.operator} {self.op2}"
        return f"{self.target} = {self.op1}"

class Goto(ThreeAddressInstruction):
    def __init__(self, label, comment=""):
        super().__init__(comment)
        self.label = label

    def __str__(self):
        return f"goto {self.label}"

class ConditionalGoto(ThreeAddressInstruction):
    def __init__(self, left, op, right, label, comment=""):
        super().__init__(comment)
        self.left = left
        self.op = op
        self.right = right
        self.label = label

    def __str__(self):
        return f"if {self.left} {self.op} {self.right} goto {self.label}"

class Label(ThreeAddressInstruction):
    def __init__(self, name, comment=""):
        super().__init__(comment)
        self.name = name

    def __str__(self):
        return f"{self.name}:"