import ply.yacc as yacc
import random
from lexer import tokens

# Excepción para errores semánticos (como variables no definidas, etc.)
class EvaluationError(Exception):
    pass

# Excepción especial para retornar valores desde funciones personalizadas
class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

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

# Nodo base del AST (árbol de sintaxis abstracta)
class Node:
    def get_label(self): return self.__class__.__name__
    def get_children(self): return []
    def evaluate(self, context_stack): raise NotImplementedError("Evaluate no implementado")

# Nodo para representar literales (números, cadenas, etc.)
class LiteralNode(Node):
    def __init__(self, value): self.value = value
    def get_label(self): return f"LiteralNode: {repr(self.value)}"
    def evaluate(self, context_stack): return self.value

# Nodo para representar identificadores (variables)
class IdentifierNode(Node):
    def __init__(self, name): self.name = name
    def get_label(self): return f"IdentifierNode: {self.name}"
    def evaluate(self, context_stack):
        # Busca la variable en la pila de contextos
        for context in reversed(context_stack):
            if self.name in context:
                return context[self.name]
        raise EvaluationError(f"Error: Variable '{self.name}' no definida.")

# Nodo para operaciones binarias como suma, resta, etc.
class BinaryOpNode(Node):
    def __init__(self, left, op, right): self.left, self.op, self.right = left, op, right
    def get_label(self): return f"BinaryOpNode: {self.op}"
    def get_children(self): return [self.left, self.right]
    def evaluate(self, context_stack):
        # Ejecuta la operación correspondiente entre left y right
        left_val = self.left.evaluate(context_stack)
        right_val = self.right.evaluate(context_stack)
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
                raise EvaluationError("Error: Operacion 'UNIR' solo permitida entre cadenas.")
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

# Nodo para operaciones unarias como negación (!, -)
class UnaryOpNode(Node):
    def __init__(self, op, expr): self.op, self.expr = op, expr
    def get_label(self): return f"UnaryOpNode: {self.op}"
    def get_children(self): return [self.expr]
    def evaluate(self, context_stack):
        val = self.expr.evaluate(context_stack)
        if self.op == 'NOT' or self.op == '!': return not val
        elif self.op == 'UMINUS':
            try:
                return -val
            except TypeError:
                raise EvaluationError(f"Error de tipo: Operador unario '{self.op}' invalido para {type(val).__name__}.")
        else:
            raise EvaluationError(f"Error: Operador unario desconocido '{self.op}'.")

# Nodo para asignaciones con 'devote'
class AssignmentNode(Node):
    def __init__(self, identifier, expr): self.identifier, self.expr = identifier, expr
    def get_label(self): return "AssignmentNode: devote"
    def get_children(self): return [IdentifierNode(self.identifier), self.expr]
    def evaluate(self, context_stack):
        value = self.expr.evaluate(context_stack)
        context_stack[-1][self.identifier] = value
        return None

# Nodo que permite imprimir múltiples valores concatenados
class MultiPrintNode(Node):
    def __init__(self, expressions):
        self.expressions = expressions
    
    def get_label(self):
        return "MultiPrintNode"
    
    def get_children(self):
        return self.expressions
    
    def evaluate(self, context_stack):
        values_to_print = [str(expr.evaluate(context_stack)) for expr in self.expressions]
        print("".join(values_to_print))
        return None

# Nodo para agrupar un bloque de sentencias
class BlockNode(Node):
    def __init__(self, statements): self.statements = statements
    def get_label(self): return getattr(self, 'custom_label', 'BlockNode')
    def get_children(self): return self.statements
    def evaluate(self, context_stack):
        for stmt in self.statements:
            stmt.evaluate(context_stack)
        return None
        
# Nodo para estructura condicional 'judge ... exile ...'
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
    def evaluate(self, context_stack):
        if self.condition.evaluate(context_stack): self.true_block.evaluate(context_stack)
        elif self.false_block: self.false_block.evaluate(context_stack)
        return None

# Nodo para bucle 'vigil' (while)
class WhileNode(Node):
    def __init__(self, condition, block): self.condition, self.block = condition, block
    def get_label(self): return "WhileNode: vigil"
    def get_children(self): return [self.condition, self.block]
    def evaluate(self, context_stack):
        while self.condition.evaluate(context_stack): self.block.evaluate(context_stack)
        return None

# Nodo para bucle 'march' (for)
class ForNode(Node):
    def __init__(self, init, condition, update, block):
        self.init, self.condition, self.update, self.block = init, condition, update, block
    def get_label(self): return "ForNode: march"
    def get_children(self): return [self.init, self.condition, self.update, self.block]
    def evaluate(self, context_stack):
        self.init.evaluate(context_stack)
        while self.condition.evaluate(context_stack):
            self.block.evaluate(context_stack)
            self.update.evaluate(context_stack)
        return None

# Nodo para función especial 'parias'
class PariasCallNode(Node):
    def __init__(self, identifier): self.identifier = identifier
    def get_label(self): return "PariasCallNode: parias"
    def get_children(self): return [IdentifierNode(self.identifier)]
    def evaluate(self, context_stack):
        old_value = self.get_children()[0].evaluate(context_stack)
        if not isinstance(old_value, (int, float)):
            raise EvaluationError(f"Error: La variable para 'parias' debe ser numerica.")
        impuesto = random.randint(1, 100)
        print(f"Impuesto: '{impuesto}'%")
        sobrante = 100 - impuesto
        new_value = (old_value * sobrante) / 100
        context_stack[-1][self.identifier] = new_value
        print(f"Valor de entrada: {old_value}, Valor final: {new_value}")
        return new_value

# Nodo para entrada del usuario con 'inquire'
class InputNode(Node):
    def __init__(self, prompt_expr): self.prompt_expr = prompt_expr
    def get_label(self): return "InputNode: inquire"
    def get_children(self): return [self.prompt_expr]
    def evaluate(self, context_stack):
        prompt = self.prompt_expr.evaluate(context_stack)
        try:
            user_input = input(prompt)
            try: return int(user_input)
            except ValueError:
                try: return float(user_input)
                except ValueError: return user_input
        except Exception as e: raise EvaluationError(f"Error durante la entrada de datos: {e}")

# Nodo para la función 'conquistar(pueblo, ejercito, defensa)' con lógica de batalla
class ConquistarCallNode(Node):
    def __init__(self, pueblo, ejercito, defensa):
        self.pueblo = pueblo
        self.ejercito = ejercito
        self.defensa = defensa

    def get_label(self):
        return "ConquistarCallNode: conquistar"

    def get_children(self):
        return [self.pueblo, self.ejercito, self.defensa]

    def evaluate(self, context_stack):
        pueblo_val = self.pueblo.evaluate(context_stack)

        # Obtener valor del ejército (variable o literal)
        if isinstance(self.ejercito, IdentifierNode):
            ejercito_nombre = self.ejercito.name
            ejercito_val = None
            for context in reversed(context_stack):
                if ejercito_nombre in context:
                    ejercito_val = context[ejercito_nombre]
                    break
            if ejercito_val is None:
                raise EvaluationError(f"Variable '{ejercito_nombre}' no encontrada en el contexto.")
        else:
            ejercito_val = self.ejercito.evaluate(context_stack)
            ejercito_nombre = None  # No se actualiza si no es variable

        if not isinstance(ejercito_val, int):
            raise EvaluationError("Error: El ejército debe ser un número entero.")

        # Obtener defensa desde argumento
        defensa_val = self.defensa.evaluate(context_stack)
        if not isinstance(defensa_val, int):
            raise EvaluationError("Error: La defensa del pueblo debe ser un número entero.")

        print(f"Pueblo '{pueblo_val}' tiene defensa {defensa_val}. Ejército disponible: {ejercito_val}")

        if ejercito_val > defensa_val:
            print(f"¡'{pueblo_val}' ha sido conquistado con éxito!")
            return True

        elif ejercito_val == defensa_val:
            print(f"¡Combate igualado! El destino decidirá...")
            if random.random() < 0.5:
                print(f"¡'{pueblo_val}' ha sido conquistado en una batalla pareja!")
                return True
            else:
                perdidas = int(defensa_val * 0.3)
                perdidas = min(perdidas, ejercito_val)
                nuevo_valor = ejercito_val - perdidas

                if ejercito_nombre:
                    for context in reversed(context_stack):
                        if ejercito_nombre in context:
                            context[ejercito_nombre] = nuevo_valor
                            break

                print(f"'{pueblo_val}' resistió el ataque por suerte. El ejército perdió {perdidas} soldado(s) y ahora tiene {nuevo_valor}.")
                return False

        else:
            perdidas = int(defensa_val * 0.3)
            perdidas = min(perdidas, ejercito_val)
            nuevo_valor = ejercito_val - perdidas

            if ejercito_nombre:  # Solo si es una variable
                for context in reversed(context_stack):
                    if ejercito_nombre in context:
                        context[ejercito_nombre] = nuevo_valor
                        break

            print(f"'{pueblo_val}' resistió el ataque. El ejército perdió {perdidas} soldado(s) y ahora tiene {nuevo_valor}.")
            return False



# Nodo para declarar funciones con 'decree'
class FunctionDefNode(Node):
    def __init__(self, name, params, body):
        self.name = name
        self.params = params 
        self.body = body     
    
    def get_label(self):
        return f"FunctionDefNode: decree {self.name}({', '.join(self.params)})"
    
    def get_children(self):
        return [self.body]

    def evaluate(self, context_stack):
        context_stack[0][self.name] = self
        return None

# Nodo para invocar funciones declaradas
class FunctionCallNode(Node):
    def __init__(self, name, args):
        self.name = name
        self.args = args 
    
    def get_label(self):
        return f"FunctionCallNode: {self.name}"
    
    def get_children(self):
        return self.args

    def evaluate(self, context_stack):
        func_def = None
        for context in reversed(context_stack):
            if self.name in context and isinstance(context[self.name], FunctionDefNode):
                func_def = context[self.name]
                break
        
        if not func_def:
            raise EvaluationError(f"Error: Funcion '{self.name}' no definida.")

        if len(self.args) != len(func_def.params):
            raise EvaluationError(f"Error: Funcion '{self.name}' espera {len(func_def.params)} argumentos, pero recibió {len(self.args)}.")

        new_context = {}
        for param_name, arg_expr in zip(func_def.params, self.args):
            new_context[param_name] = arg_expr.evaluate(context_stack) 

        context_stack.append(new_context)

        return_value = None
        try:
            func_def.body.evaluate(context_stack) 
        except ReturnValue as r:
            return_value = r.value 
        finally:
            context_stack.pop() 

        return return_value

# Nodo para retornar un valor dentro de una función (yield)
class ReturnNode(Node):
    def __init__(self, expr=None):
        self.expr = expr
    
    def get_label(self):
        return "ReturnNode: yield"
    
    def get_children(self):
        return [self.expr] if self.expr else []

    def evaluate(self, context_stack):
        value = None
        if self.expr:
            value = self.expr.evaluate(context_stack)
        raise ReturnValue(value)

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

# Regla inicial: puede comenzar con una o más sentencias o funciones
def p_inicio(p):
    '''inicio : 
              | sentencia inicio
              | declaracion_funcion inicio''' 
    if len(p) == 1:
        p[0] = BlockNode([])
    else:
        if p[1]:
             p[2].statements.insert(0, p[1])
        p[0] = p[2]

# Regla inicial: puede comenzar con una o más sentencias o funciones
def p_sentencia(p):
    '''sentencia : asignacion PUNTOYCOMA
                   | expresion PUNTOYCOMA
                   | condicional
                   | print PUNTOYCOMA
                   | ciclo
                   | sentencia_yield''' 
    p[0] = p[1]

# Declaración de funciones con 'decree'
def p_declaracion_funcion(p):
    '''declaracion_funcion : DECREE IDENTIFICADOR PARIZQ parametros_opcionales PARDER LLAVEIZQ bloque LLAVEDER'''
    p[0] = FunctionDefNode(p[2], p[4], p[7])

# Declaración de funciones con 'decree'
def p_parametros_opcionales(p):
    '''parametros_opcionales : 
                             | parametros_list'''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]

def p_parametros_list(p):
    '''parametros_list : IDENTIFICADOR
                       | IDENTIFICADOR COMA parametros_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_sentencia_yield(p):
    '''sentencia_yield : YIELD expresion PUNTOYCOMA
                       | YIELD PUNTOYCOMA'''
    if len(p) == 3:
        p[0] = ReturnNode(None)
    else:
        p[0] = ReturnNode(p[2])

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

# Condicionales tipo 'judge ... exile'
def p_condicional(p):
    '''condicional : IF PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER
                   | IF PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER ELSE LLAVEIZQ bloque LLAVEDER'''
    if len(p) == 8: p[0] = IfNode(p[3], p[6])
    else: p[0] = IfNode(p[3], p[6], p[10])

# Ciclos: 'vigil' y 'march'
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

def p_expresiones_list(p):
    '''expresiones_list : expresion
                        | expresion COMA expresiones_list'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = [p[1]] + p[3]

def p_argumentos_opcionales(p):
    '''argumentos_opcionales : 
                             | expresiones_list'''
    if len(p) == 1:
        p[0] = []
    else:
        p[0] = p[1]

# Print personalizado
def p_print(p): 'print : PRINT PARIZQ expresiones_list PARDER'; p[0] = MultiPrintNode(p[3])

# Llamadas a funciones especiales
def p_funcion_parias(p): 'expresion : PARIAS PARIZQ IDENTIFICADOR PARDER'; p[0] = PariasCallNode(p[3])
def p_expresion_input(p): 'expresion : INQUIRE PARIZQ expresion PARDER'; p[0] = InputNode(p[3])
def p_funcion_conquistar(p):
    'expresion : CONQUISTAR PARIZQ expresion COMA expresion COMA expresion PARDER'
    p[0] = ConquistarCallNode(p[3], p[5], p[7])


# Llamada a funciones declaradas por el usuario
def p_expresion_llamada_funcion(p):
    '''expresion : IDENTIFICADOR PARIZQ argumentos_opcionales PARDER'''
    p[0] = FunctionCallNode(p[1], p[3])


def p_error(p):
    if p:
        try:
            lines = p.lexer.lexdata.splitlines(); error_line = lines[p.lineno - 1]
            print(f"Error de sintaxis en la linea {p.lineno}, token '{p.value}': -> {error_line.strip()}")
        except (IndexError, AttributeError): print(f"Error de sintaxis cerca del token '{p.value}'")
    else: print("Error de sintaxis al final del archivo.")

parser = yacc.yacc(debug=True)