import re

class SimpleParser:
    def __init__(self):
        # Reconocedor de tokens (números, palabras, símbolos)
        self.token_pattern = re.compile(r'\s*([a-zA-Z_]\w*|\d+|[+\-*/()=<>]|==|!=)\s*')

    def tokenize(self, code):
        return self.token_pattern.findall(code)

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
                    condition_str = match.group(1)
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
                    condition_str = match.group(1)
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
            if "=" in line:
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

    def _build_expression_tree(self, tokens):
        # (Se mantiene la lógica de precedencia que ya teníamos)
        if not tokens: return ""
        if len(tokens) == 1: return tokens[0]
        for op in ['+', '-']:
            if op in tokens:
                idx = tokens.index(op)
                return (self._build_expression_tree(tokens[:idx]), op, self._build_expression_tree(tokens[idx+1:]))
        for op in ['*', '/']:
            if op in tokens:
                idx = tokens.index(op)
                return (self._build_expression_tree(tokens[:idx]), op, self._build_expression_tree(tokens[idx+1:]))
        return tokens[0]