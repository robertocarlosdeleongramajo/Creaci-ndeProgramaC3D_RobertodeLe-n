import re

class SimpleParser:
    def __init__(self):
        # Reconoce variables, números, operadores, y ahora corchetes y paréntesis.
        self.token_pattern = re.compile(r'\s*([a-zA-Z_]\w*|\d+|[+\-*/()\[\]=<>]|==|!=)\s*')

    def tokenize(self, code):
        # Limpiamos los tokens de espacios en blanco vacíos para evitar errores en el caché del DAG
        tokens = self.token_pattern.findall(code)
        return [t.strip() for t in tokens if t.strip()]

    def parse_full_code(self, text):
        """
        Divide el código completo en una lista de bloques procesables.
        """
        lines = text.split('\n')
        program_structure = []
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Omitir líneas vacías o comentarios
            if not line or line.startswith("//"):
                i += 1
                continue
            
            # PARTE 1: Detectar bloque WHILE
            if line.startswith("while"):
                match = re.search(r'while\s*\((.*)\)\s*\{', line)
                if match:
                    condition_str = match.group(1).strip()
                    body, new_i = self._extract_block(lines, i + 1)
                    program_structure.append({
                        'type': 'while',
                        'condition': self.tokenize(condition_str),
                        'body': body
                    })
                    i = new_i
                    continue

            # PARTE 2: Detectar bloque IF
            elif line.startswith("if"):
                match = re.search(r'if\s*\((.*)\)\s*\{', line)
                if match:
                    condition_str = match.group(1).strip()
                    body, new_i = self._extract_block(lines, i + 1)
                    program_structure.append({
                        'type': 'if',
                        'condition': self.tokenize(condition_str),
                        'body': body
                    })
                    i = new_i
                    continue

            # PARTE 3: Detectar ASIGNACIÓN (x = 10)
            elif "=" in line:
                program_structure.append({
                    'type': 'assignment',
                    'data': self.parse_assignment(line)
                })
            
            i += 1
        return program_structure

    def _extract_block(self, lines, start_index):
        """Extrae las líneas dentro de llaves { ... }"""
        block = []
        i = start_index
        while i < len(lines) and "}" not in lines[i]:
            line = lines[i].strip()
            # Ignoramos líneas vacías o comentarios dentro del bloque
            if line and not line.startswith("//") and "=" in line:
                block.append(self.parse_assignment(line))
            i += 1
        return block, i

    def parse_assignment(self, line):
        line = line.replace(";", "")
        parts = line.split('=', 1)
        target = parts[0].strip()
        expression_tokens = self.tokenize(parts[1].strip())
        tree = self._build_expression_tree(expression_tokens)
        return (target, '=', tree)

    # --- LA MAGIA SUCEDE AQUÍ ---
    def _build_expression_tree(self, tokens):
        """
        Construye el árbol respetando la jerarquía de operadores y 
        la profundidad de paréntesis () y corchetes [].
        """
        if not tokens: return ""
        if len(tokens) == 1: return tokens[0]

        # 1. Si toda la expresión está envuelta en ( ) o [ ], se los quitamos
        if (tokens[0] == '(' and tokens[-1] == ')') or (tokens[0] == '[' and tokens[-1] == ']'):
            # Verificamos que los paréntesis exteriores realmente coincidan entre sí
            depth = 0
            is_valid_wrapper = True
            for i in range(len(tokens) - 1):
                if tokens[i] in ['(', '[']: depth += 1
                elif tokens[i] in [')', ']']: depth -= 1
                if depth == 0:  # Si la profundidad llega a 0 antes del final, no envuelven todo
                    is_valid_wrapper = False
                    break
            
            if is_valid_wrapper:
                return self._build_expression_tree(tokens[1:-1]) # Llamada recursiva sin los extremos

        # 2. Buscar el operador principal (el que está fuera de cualquier paréntesis)
        depth = 0
        min_prec = 3
        split_idx = -1

        precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

        # Recorremos de derecha a izquierda para mantener la asociatividad por la izquierda (ej: 5-3-2)
        for i in range(len(tokens) - 1, -1, -1):
            token = tokens[i]
            if token in [')', ']']:
                depth += 1
            elif token in ['(', '[']:
                depth -= 1
            # Si estamos "afuera" de los paréntesis y encontramos un operador
            elif depth == 0 and token in precedence:
                prec = precedence[token]
                if prec < min_prec:
                    min_prec = prec
                    split_idx = i

        # 3. Dividimos la expresión por el operador principal
        if split_idx != -1:
            op = tokens[split_idx]
            left_part = self._build_expression_tree(tokens[:split_idx])
            right_part = self._build_expression_tree(tokens[split_idx+1:])
            return (left_part, op, right_part)

        return tokens[0]