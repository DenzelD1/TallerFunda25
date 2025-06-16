import ply.yacc as yacc
import random
from lexer import tokens

class EvaluationError(Exception):
    pass

def format_ast_as_tree(node, prefix=""):
    if not isinstance(node, Node): return str(node)
    children = node.get_children()
    buffer = prefix + node.get_label() + "\n"
    for i, child in enumerate(children):
        is_last = (i == len(children) - 1)
        connector = "└── " if is_last else "├── "
        child_prefix = "    " if is_last else "│   "
        buffer += format_ast_as_tree(child, prefix + child_prefix)
    return buffer

class Node:
    def get_label(self): return self.__class__.__name__
    def get_children(self): return []
    def evaluate(self, context): raise NotImplementedError("Evaluate no implementado")

class LiteralNode(Node):
    def __init__(self, value): self.value = value
    def get_label(self): return f"LiteralNode: {repr(self.value)}"
    def evaluate(self, context): return self.value

class IdentifierNode(Node):
    def __init__(self, name): self.name = name
    def get_label(self): return f"IdentifierNode: {self.name}"
    def evaluate(self, context):
        if self.name in context:
            return context[self.name]
        raise EvaluationError(f"Error: Variable '{self.name}' no definida.")

class BinaryOpNode(Node):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
    def get_label(self): return f"BinaryOpNode: {self.op}"
    def get_children(self): return [self.left, self.right]
    def evaluate(self, context):
        left_val = self.left.evaluate(context)
        right_val = self.right.evaluate(context)
        try:
            if self.op == 'inherit': return left_val + right_val
            elif self.op == 'plunder': return left_val - right_val
            elif self.op == 'forge': return left_val * right_val
            elif self.op == 'cleave':
                if right_val == 0:
                    raise EvaluationError("Error: Division por cero.")
                return left_val / right_val
            elif self.op == 'shatter': return left_val % right_val
            elif self.op == 'UNIR':
                if isinstance(left_val, str) and isinstance(right_val, str): return left_val + right_val
                raise EvaluationError("Error: Operacion invalida entre numero y cadena.")
            elif self.op == '>': return left_val > right_val
            elif self.op == '<': return left_val < right_val
            elif self.op == '>=': return left_val >= right_val
            elif self.op == '<=': return left_val <= right_val
            elif self.op == '==': return left_val == right_val
            elif self.op == '!=': return left_val != right_val
            elif self.op == '&&': return left_val and right_val
            elif self.op == '||': return left_val or right_val
        except TypeError:
            raise EvaluationError(f"Error de tipo: Operacion '{self.op}' invalida entre {type(left_val).__name__} y {type(right_val).__name__}.")
        except Exception as e:
            raise EvaluationError(f"Error desconocido en operacion binaria: {e}")

class UnaryOpNode(Node):
    def __init__(self, op, expr): self.op, self.expr = op, expr
    def get_label(self): return f"UnaryOpNode: {self.op}"
    def get_children(self): return [self.expr]
    def evaluate(self, context):
        val = self.expr.evaluate(context)
        if self.op == 'NOT' or self.op == '!': return not val
        elif self.op == 'UMINUS':
            try:
                return -val
            except TypeError:
                raise EvaluationError(f"Error de tipo: Operador unario '{self.op}' invalido para {type(val).__name__}.")
        else:
            raise EvaluationError(f"Error: Operador unario desconocido '{self.op}'.")

class AssignmentNode(Node):
    def __init__(self, identifier, expr): self.identifier, self.expr = identifier, expr
    def get_label(self): return "AssignmentNode: devote"
    def get_children(self): return [IdentifierNode(self.identifier), self.expr]
    def evaluate(self, context):
        value = self.expr.evaluate(context)
        context[self.identifier] = value
        return None

class PrintNode(Node):
    def __init__(self, expr): self.expr = expr
    def get_label(self): return "PrintNode"
    def get_children(self): return [self.expr]
    def evaluate(self, context):
        value = self.expr.evaluate(context)
        print(value)
        return None

class BlockNode(Node):
    def __init__(self, statements): self.statements = statements
    def get_label(self): return getattr(self, 'custom_label', 'BlockNode')
    def get_children(self): return self.statements
    def evaluate(self, context):
        for stmt in self.statements:
            stmt.evaluate(context)
        return None
        
class IfNode(Node):
    def __init__(self, condition, true_block, false_block=None):
        self.condition, self.true_block, self.false_block = condition, true_block, false_block
    def get_label(self): return "IfNode: judge"
    def get_children(self):
        children = [self.condition, self.true_block]
        if self.false_block:
            self.false_block.custom_label = "BlockNode: exile"
            children.append(self.false_block)
        return children
    def evaluate(self, context):
        if self.condition.evaluate(context): self.true_block.evaluate(context)
        elif self.false_block: self.false_block.evaluate(context)
        return None

class WhileNode(Node):
    def __init__(self, condition, block): self.condition, self.block = condition, block
    def get_label(self): return "WhileNode: vigil"
    def get_children(self): return [self.condition, self.block]
    def evaluate(self, context):
        while self.condition.evaluate(context): self.block.evaluate(context)
        return None

class ForNode(Node):
    def __init__(self, init, condition, update, block):
        self.init, self.condition, self.update, self.block = init, condition, update, block
    def get_label(self): return "ForNode: march"
    def get_children(self): return [self.init, self.condition, self.update, self.block]
    def evaluate(self, context):
        self.init.evaluate(context)
        while self.condition.evaluate(context):
            self.block.evaluate(context)
            self.update.evaluate(context)
        return None

class PariasCallNode(Node):
    def __init__(self, identifier): self.identifier = identifier
    def get_label(self): return "PariasCallNode: parias"
    def get_children(self): return [IdentifierNode(self.identifier)]
    def evaluate(self, context):
        old_value = self.get_children()[0].evaluate(context)
        if not isinstance(old_value, (int, float)):
            raise EvaluationError(f"Error: La variable para 'parias' debe ser numerica.")
        impuesto = random.randint(1, 100)
        print(f"Impuesto: '{impuesto}'%")
        sobrante = 100 - impuesto
        new_value = (old_value * sobrante) / 100
        context[self.identifier] = new_value
        print(f"Valor de entrada: {old_value}, Valor final: {new_value}")
        return new_value

class InputNode(Node):
    def __init__(self, prompt_expr): self.prompt_expr = prompt_expr
    def get_label(self): return "InputNode: inquire"
    def get_children(self): return [self.prompt_expr]
    def evaluate(self, context):
        prompt = self.prompt_expr.evaluate(context)
        try:
            user_input = input(prompt)
            try: return int(user_input)
            except ValueError:
                try: return float(user_input)
                except ValueError: return user_input
        except Exception as e: raise EvaluationError(f"Error durante la entrada de datos: {e}")

class ConquistarCallNode(Node):
    def __init__(self, pueblo, ejercito):
        self.pueblo = pueblo
        self.ejercito = ejercito

    def get_label(self):
        return "ConquistarCallNode: conquistar"

    def get_children(self):
        return [self.pueblo, self.ejercito]

    def evaluate(self, context):
        pueblo_val = self.pueblo.evaluate(context)

        # Para obtener el nombre de la variable de ejército y su valor actual
        ejercito_nombre = self.ejercito.name  # si self.ejercito es un nodo de variable
        ejercito_val = context.get(ejercito_nombre, None)

        if ejercito_val is None:
            raise EvaluationError(f"Variable '{ejercito_nombre}' no encontrada en el contexto.")

        if not isinstance(ejercito_val, int):
             raise EvaluationError("Error: El ejército debe ser un número entero.")

        defensa = random.randint(10, 100)
        print(f"Pueblo '{pueblo_val}' tiene defensa {defensa}. Ejército disponible: {ejercito_val}")

        if ejercito_val > defensa:
            print(f"¡'{pueblo_val}' ha sido conquistado con éxito!")
            return True
        else:
            perdidas = int(defensa * 0.3)
            perdidas = min(perdidas, ejercito_val)  # Que no pierdas más soldados de los que tienes
            nuevo_valor = ejercito_val - perdidas
            # Actualizamos el valor de la variable del ejército en el contexto
            for key in context:
                if context[key] == ejercito_val:
                    context[key] = nuevo_valor
                    break
            print(f"'{pueblo_val}' resistió el ataque. El ejército perdió {perdidas} soldado(s) y ahora tiene {nuevo_valor}.")
            return False

precedence = (
    ('right', 'ASIGNAR'),
    ('left', 'UNIR'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'MAYOR', 'MENOR', 'MAYORIGUAL', 'MENORIGUAL', 'IGUAL', 'DESIGUAL'),
    ('right', 'NOT'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION', 'DIVISION'),
    ('left', 'MODULO'),
    ('right', 'MENOS')
)

def p_inicio(p):
    '''inicio : 
              | sentencia inicio'''
    if len(p) == 1:
        p[0] = BlockNode([])
    else:
        if p[1]:
             p[2].statements.insert(0, p[1])
        p[0] = p[2]

def p_sentencia(p):
    '''sentencia : asignacion PUNTOYCOMA
                   | expresion PUNTOYCOMA
                   | condicional
                   | print PUNTOYCOMA
                   | ciclo'''
    p[0] = p[1]

def p_asignacion(p): 'asignacion : IDENTIFICADOR ASIGNAR expresion'; p[0] = AssignmentNode(p[1], p[3])
def p_expresion_unir(p): 'expresion : expresion UNIR expresion'; p[0] = BinaryOpNode(p[1], 'UNIR', p[3])
def p_expresion_binaria(p):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICACION expresion
                 | expresion DIVISION expresion
                 | expresion MODULO expresion'''; p[0] = BinaryOpNode(p[1], p[2], p[3])
def p_expresion_logica(p):
    '''expresion : expresion MAYOR expresion
                 | expresion MENOR expresion
                 | expresion MAYORIGUAL expresion
                 | expresion MENORIGUAL expresion
                 | expresion IGUAL expresion
                 | expresion DESIGUAL expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | NOT expresion'''
    if len(p) == 3: p[0] = UnaryOpNode('NOT', p[2])
    else: p[0] = BinaryOpNode(p[1], p[2], p[3])
def p_condicional(p):
    '''condicional : IF PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER
                   | IF PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER ELSE LLAVEIZQ bloque LLAVEDER'''
    if len(p) == 8: p[0] = IfNode(p[3], p[6])
    else: p[0] = IfNode(p[3], p[6], p[10])
def p_ciclo(p):
    '''ciclo : WHILE PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER
             | FOR PARIZQ asignacion PUNTOYCOMA expresion PUNTOYCOMA asignacion PARDER LLAVEIZQ bloque LLAVEDER'''
    if len(p) == 8: p[0] = WhileNode(p[3], p[6])
    else: p[0] = ForNode(p[3], p[5], p[7], p[10])
def p_bloque(p):
    '''bloque : 
              | sentencia bloque''' 
    if len(p) == 1: p[0] = BlockNode([])
    else:
        if p[1] is None: p[0] = p[2]
        else:
            p[2].statements.insert(0, p[1])
            p[0] = p[2]
def p_expresion_parentesis(p): 'expresion : PARIZQ expresion PARDER'; p[0] = p[2]
def p_expresion_literal_cadena(p): 'expresion : CADENA'; p[0] = LiteralNode(p[1])
def p_expresion_numero(p): 'expresion : NUMERO'; p[0] = LiteralNode(p[1])
def p_expresion_identificador(p): 'expresion : IDENTIFICADOR'; p[0] = IdentifierNode(p[1])
def p_expresion_uminus(p): 'expresion : MENOS expresion %prec MENOS'; p[0] = UnaryOpNode('UMINUS', p[2])
def p_print(p): 'print : PRINT PARIZQ expresion PARDER'; p[0] = PrintNode(p[3])
def p_funcion_parias(p): 'expresion : PARIAS PARIZQ IDENTIFICADOR PARDER'; p[0] = PariasCallNode(p[3])
def p_expresion_input(p): 'expresion : INQUIRE PARIZQ expresion PARDER'; p[0] = InputNode(p[3])
def p_funcion_conquistar(p):
    'expresion : CONQUISTAR PARIZQ expresion COMA expresion PARDER'
    p[0] = ConquistarCallNode(p[3], p[5])

def p_error(p):
    if p:
        try:
            lines = p.lexer.lexdata.splitlines(); error_line = lines[p.lineno - 1]
            print(f"Error de sintaxis en la linea {p.lineno}, token '{p.value}': -> {error_line.strip()}")
        except (IndexError, AttributeError): print(f"Error de sintaxis cerca del token '{p.value}'")
    else: print("Error de sintaxis al final del archivo.")

parser = yacc.yacc(debug=True)