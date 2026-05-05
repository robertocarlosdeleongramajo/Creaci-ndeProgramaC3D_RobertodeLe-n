class Generator:
    """Administrador de Temporales, Etiquetas y Comentarios"""
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.instructions = []

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

    def get_code(self):
        # Alineamos los comentarios para que se vean ordenados en la GUI
        code_lines = []
        for inst in self.instructions:
            line = str(inst)
            if inst.comment:
                # Rellena con espacios para que todos los // empiecen en la misma columna
                line = f"{line.ljust(30)} // {inst.comment}"
            code_lines.append(line)
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