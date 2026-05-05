from generator import Assignment, Goto, ConditionalGoto, Label

class Translator:
    def __init__(self, generator):
        self.gen = generator

    def translate_program(self, program_structure):
        """
        Recorre la estructura generada por el Parser y decide qué 
        tipo de bloque traducir, manteniendo el orden secuencial.
        """
        for block in program_structure:
            if block['type'] == 'assignment':
                var_name, _, expr_tree = block['data']
                # Procesamos la expresión y luego la asignación final
                temp_res = self.translate_expression(expr_tree)
                self.gen.add_instruction(
                    Assignment(var_name, temp_res, comment=f"Asignación final a '{var_name}'")
                )
            
            elif block['type'] == 'while':
                self.translate_while(block['condition'], block['body'])
            
            elif block['type'] == 'if':
                self.translate_if(block['condition'], block['body'])

    def translate_expression(self, expr):
        """
        Traduce expresiones aritméticas recursivamente.
        Asigna comentarios según la jerarquía de la operación.
        """
        if not isinstance(expr, tuple):
            return str(expr)

        left_val, op, right_val = expr
        left_res = self.translate_expression(left_val)
        right_res = self.translate_expression(right_val)

        target = self.gen.new_temporal()
        
        # Comentario dinámico según el operador
        if op in ['*', '/']:
            msg = "Operación de mayor precedencia"
        else:
            msg = "Operación aritmética"
            
        self.gen.add_instruction(Assignment(target, left_res, op, right_res, comment=msg))
        return target

    def translate_while(self, condition, body):
        """
        Genera el esquema C3D para un bucle While:
        L0: Etiqueta de inicio
        if cond goto L1 (Cuerpo)
        goto L2 (Salida)
        L1: ...
        goto L0
        L2: ...
        """
        l_start = self.gen.new_label()
        l_body = self.gen.new_label()
        l_end = self.gen.new_label()

        self.gen.add_instruction(Label(l_start, "Etiqueta de inicio del while"))
        
        # Extraemos la condición (izq, op, der)
        left, op, right = condition[0], condition[1], condition[2]
        self.gen.add_instruction(
            ConditionalGoto(left, op, right, l_body, f"Condición: si {left} {op} {right} es verdadero")
        )
        self.gen.add_instruction(Goto(l_end, "Salto de salida (condición falsa)"))
        
        self.gen.add_instruction(Label(l_body, "Cuerpo del ciclo"))
        
        # Traducimos las instrucciones dentro del while
        # Convertimos el formato del parser a la estructura que entiende translate_program
        body_structure = [{'type': 'assignment', 'data': b} for b in body]
        self.translate_program(body_structure)
        
        self.gen.add_instruction(Goto(l_start, "Regreso al inicio del ciclo"))
        self.gen.add_instruction(Label(l_end, "Salto de salida del while"))

    def translate_if(self, condition, body):
        """
        Genera el esquema C3D para un condicional IF:
        if cond goto L_true
        goto L_end
        L_true: ...
        L_end: ...
        """
        l_true = self.gen.new_label()
        l_end = self.gen.new_label()

        left, op, right = condition[0], condition[1], condition[2]
        self.gen.add_instruction(
            ConditionalGoto(left, op, right, l_true, f"Si {left} {op} {right} es verdad")
        )
        self.gen.add_instruction(Goto(l_end, "Saltar bloque if (falso)"))
        
        self.gen.add_instruction(Label(l_true, "Inicio del bloque IF"))
        
        # Traducimos el cuerpo del IF
        body_structure = [{'type': 'assignment', 'data': b} for b in body]
        self.translate_program(body_structure)
        
        self.gen.add_instruction(Label(l_end, "Fin de la estructura IF"))