from generator import Assignment, Goto, ConditionalGoto, Label

class Translator:
    def __init__(self, generator):
        self.gen = generator
        # Memoria para el Grafo DAG. Evita recalcular expresiones repetidas.
        self.expression_cache = {}
        # NUEVO: Memoria Matemática. Guarda el valor numérico real de cada temporal.
        self.value_map = {}

    def translate_program(self, program_structure):
        """
        Recorre la estructura generada por el Parser y decide qué 
        tipo de bloque traducir, manteniendo el orden secuencial.
        """
        # Limpiamos los cachés al inicio de un nuevo programa
        self.expression_cache = {}
        self.value_map = {} 
        
        for block in program_structure:
            if block['type'] == 'assignment':
                var_name, _, expr_tree = block['data']
                # Procesamos la expresión y luego la asignación final
                temp_res = self.translate_expression(expr_tree)
                
                # Si el temporal final tiene un valor matemático conocido, se lo pasamos a la variable final
                if temp_res in self.value_map:
                    self.value_map[var_name] = self.value_map[temp_res]

                self.gen.add_instruction(
                    Assignment(var_name, temp_res, comment=f"Asignación final a '{var_name}'")
                )
                self.expression_cache[(temp_res, '', '')] = var_name
            
            elif block['type'] == 'while':
                self.translate_while(block['condition'], block['body'])
            
            elif block['type'] == 'if':
                self.translate_if(block['condition'], block['body'])

    def _get_numeric_value(self, val):
        """
        NUEVO: Intenta obtener el valor numérico de un operando.
        Si es un temporal (ej. t0), busca su valor en la memoria.
        Si es un número directo (ej. 5), lo convierte.
        Si es una letra sin valor asignado (ej. 'a'), devuelve None.
        """
        if val in self.value_map:
            return self.value_map[val]
        try:
            # Intenta convertir el string a float o int
            return float(val) if '.' in str(val) else int(val)
        except ValueError:
            return None 

    def translate_expression(self, expr):
        """
        Traduce expresiones aritméticas recursivamente.
        LÓGICA DAG + CÁLCULO MATEMÁTICO REAL.
        """
        if not isinstance(expr, tuple):
            return str(expr)

        left_val, op, right_val = expr
        left_res = self.translate_expression(left_val)
        right_res = self.translate_expression(right_val)

        # --- LÓGICA DAG ---
        expr_key = (left_res, op, right_res)
        if expr_key in self.expression_cache:
            msg = f"DAG: Reutilizando cálculo de ({left_res} {op} {right_res})"
            return self.expression_cache[expr_key]

        target = self.gen.new_temporal()
        
        # --- NUEVO: EL CEREBRO MATEMÁTICO (PASO A PASO) ---
        num_left = self._get_numeric_value(left_res)
        num_right = self._get_numeric_value(right_res)
        
        # Si ambos lados son números (o temporales que ya resolvimos), hacemos la operación
        if num_left is not None and num_right is not None:
            try:
                # Evaluamos de forma segura según el operador
                if op == '+': result = num_left + num_right
                elif op == '-': result = num_left - num_right
                elif op == '*': result = num_left * num_right
                elif op == '/': result = num_left / num_right if num_right != 0 else 0
                
                # Formateamos para no mostrar decimales innecesarios (ej. 15.0 -> 15)
                if isinstance(result, float) and result.is_integer():
                    result = int(result)

                # Guardamos el resultado en la memoria matemática para futuros cálculos
                self.value_map[target] = result
                
                # Le enviamos el texto de la reducción al generador
                if hasattr(self.gen, 'add_math_step'):
                    self.gen.add_math_step(left_res, op, right_res, result, target)
            except Exception:
                pass # Previene colapsos por división entre cero u otros errores extraños
        
        # Comentario dinámico para el C3D
        if op in ['*', '/']:
            msg = f"Prioridad alta: resolviendo {left_res} {op} {right_res}"
        else:
            msg = f"Operación base: resolviendo {left_res} {op} {right_res}"
            
        self.gen.add_instruction(Assignment(target, left_res, op, right_res, comment=msg))
        
        self.expression_cache[expr_key] = target
        self.gen.add_dag_connection(target, left_res, op, right_res)
        
        return target

    def translate_while(self, condition, body):
        l_start = self.gen.new_label()
        l_body = self.gen.new_label()
        l_end = self.gen.new_label()

        self.gen.add_instruction(Label(l_start, "Etiqueta de inicio del while"))
        
        left, op, right = condition[0], condition[1], condition[2]
        self.gen.add_instruction(
            ConditionalGoto(left, op, right, l_body, f"Condición: si {left} {op} {right} es verdadero")
        )
        self.gen.add_instruction(Goto(l_end, "Salto de salida (condición falsa)"))
        
        self.gen.add_instruction(Label(l_body, "Cuerpo del ciclo"))
        
        self.expression_cache = {} 
        
        body_structure = [{'type': 'assignment', 'data': b} for b in body]
        self.translate_program(body_structure)
        
        self.gen.add_instruction(Goto(l_start, "Regreso al inicio del ciclo"))
        self.gen.add_instruction(Label(l_end, "Salto de salida del while"))

    def translate_if(self, condition, body):
        l_true = self.gen.new_label()
        l_end = self.gen.new_label()

        left, op, right = condition[0], condition[1], condition[2]
        self.gen.add_instruction(
            ConditionalGoto(left, op, right, l_true, f"Si {left} {op} {right} es verdad")
        )
        self.gen.add_instruction(Goto(l_end, "Saltar bloque if (falso)"))
        
        self.gen.add_instruction(Label(l_true, "Inicio del bloque IF"))
        
        self.expression_cache = {}
        
        body_structure = [{'type': 'assignment', 'data': b} for b in body]
        self.translate_program(body_structure)
        
        self.gen.add_instruction(Label(l_end, "Fin de la estructura IF"))