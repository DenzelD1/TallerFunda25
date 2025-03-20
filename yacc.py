import ply.yacc as yacc
import random
from lexer import tokens

class Node:
    def evaluate(self, context):
        raise NotImplementedError("No se ha implementado 'evaluate' en el nodo base.")

class LiteralNode(Node):
    def __init__(self, value):
        self.value = value
    def evaluate(self, context):
        return self.value

class IdentifierNode(Node):
    def __init__(self, name):
        self.name = name
    def evaluate(self, context):
        if self.name in context:
            return context[self.name]
        else:
            print(f"Error: Variable '{self.name}' no definida")
            return None

class BinaryOpNode(Node):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right
    def evaluate(self, context):
        left_val = self.left.evaluate(context)
        right_val = self.right.evaluate(context)
        if left_val is None or right_val is None:
            return None
        try:
            if self.op == 'inherit':
                return left_val + right_val
            elif self.op == 'plunder':
                return left_val - right_val
            elif self.op == 'forge':
                return left_val * right_val
            elif self.op == 'cleave':
                if right_val == 0:
                    print("Error: Division por cero")
                    return None
                return left_val / right_val
            elif self.op == 'shatter':
                return left_val % right_val
            elif self.op == 'UNIR':
                if isinstance(left_val, str) and isinstance(right_val, str):
                    return left_val + right_val
                else:
                    print("Error: Operacion invalida entre numero y cadena")
                    return None
            elif self.op == '>':
                return left_val > right_val
            elif self.op == '<':
                return left_val < right_val
            elif self.op == '>=':
                return left_val >= right_val
            elif self.op == '<=':
                return left_val <= right_val
            elif self.op == '==':
                return left_val == right_val
            elif self.op == '&&':
                return left_val and right_val
            elif self.op == '||':
                return left_val or right_val
        except Exception as e:
            print("Error durante la operacion binaria:", e)
            return None

class UnaryOpNode(Node):
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def evaluate(self, context):
        val = self.expr.evaluate(context)
        if val is None:
            return None
        if self.op == 'NOT' or self.op == '!':
            return not val
        elif self.op == 'UMINUS':
            return -val
        else:
            print(f"Error: Operador unario desconocido '{self.op}'")
            return None

class AssignmentNode(Node):
    def __init__(self, identifier, expr):
        self.identifier = identifier
        self.expr = expr
    def evaluate(self, context):
        value = self.expr.evaluate(context)
        if value is None:
            print(f"Error: No se puede asignar un valor indefinido a '{self.identifier}'")
        else:
            context[self.identifier] = value
        return value

class PrintNode(Node):
    def __init__(self, expr):
        self.expr = expr
    def evaluate(self, context):
        value = self.expr.evaluate(context)
        print(f"Imprimiendo: {value}")
        return value

class IfNode(Node):
    def __init__(self, condition, true_block, false_block=None):
        self.condition = condition
        self.true_block = true_block
        self.false_block = false_block
    def evaluate(self, context):
        if self.condition.evaluate(context):
            for stmt in self.true_block:
                stmt.evaluate(context)
        elif self.false_block:
            for stmt in self.false_block:
                stmt.evaluate(context)
        return None

class WhileNode(Node):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block
    def evaluate(self, context):
        while self.condition.evaluate(context):
            for stmt in self.block:
                stmt.evaluate(context)
        return None

class ForNode(Node):
    def __init__(self, init, condition, update, block):
        self.init = init
        self.condition = condition
        self.update = update
        self.block = block
    def evaluate(self, context):
        self.init.evaluate(context)
        while self.condition.evaluate(context):
            for stmt in self.block:
                stmt.evaluate(context)
            self.update.evaluate(context)
        return None

class PariasCallNode(Node):
    def __init__(self, identifier):
        self.identifier = identifier
    def evaluate(self, context):
        if self.identifier not in context:
            print(f"Error: Variable '{self.identifier}' no definida")
            return None
        old_value = context[self.identifier]
        if not isinstance(old_value, (int, float)):
            print(f"Error: La variable '{self.identifier}' debe ser numerica para aplicar parias")
            return None
        impuesto = random.randint(1, 100)
        print(f"Impuesto: '{impuesto}'%")
        sobrante = 100 - impuesto
        new_value = (old_value * sobrante) / 100
        context[self.identifier] = new_value
        print(f"Valor de entrada: {old_value}, Valor final: {new_value}")
        return new_value

class BlockNode(Node):
    def __init__(self, statements):
        self.statements = statements
    def evaluate(self, context):
        result = None
        for stmt in self.statements:
            result = stmt.evaluate(context)
        return result

precedence = (
    ('right', 'ASIGNAR'),
    ('left', 'UNIR'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('nonassoc', 'MAYOR', 'MENOR', 'MAYORIGUAL', 'MENORIGUAL', 'IGUAL'),
    ('right', 'NOT'),
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION', 'DIVISION'),
    ('left', 'MODULO'),
    ('right', 'MENOS')
)

def p_inicio(p):
    '''inicio : sentencia
              | inicio sentencia'''
    if len(p) == 2:
        p[0] = [p[1]]
    else:
        p[0] = p[1] + [p[2]]

def p_sentencia(p):
    '''sentencia : asignacion
                 | expresion
                 | condicional
                 | print
                 | ciclo'''
    p[0] = p[1]

def p_asignacion(p):
    'asignacion : IDENTIFICADOR ASIGNAR expresion'
    p[0] = AssignmentNode(p[1], p[3])

def p_expresion_unir(p):
    'expresion : expresion UNIR expresion'
    p[0] = BinaryOpNode(p[1], 'UNIR', p[3])

def p_expresion_binaria(p):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICACION expresion
                 | expresion DIVISION expresion
                 | expresion MODULO expresion'''
    p[0] = BinaryOpNode(p[1], p[2], p[3])

def p_expresion_logica(p):
    '''expresion : expresion MAYOR expresion
                 | expresion MENOR expresion
                 | expresion MAYORIGUAL expresion
                 | expresion MENORIGUAL expresion
                 | expresion IGUAL expresion
                 | expresion AND expresion
                 | expresion OR expresion
                 | NOT expresion'''
    if len(p) == 3:
        p[0] = UnaryOpNode('NOT', p[2])
    else:
        p[0] = BinaryOpNode(p[1], p[2], p[3])

def p_condicional(p):
    '''condicional : IF PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER
                   | IF PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER ELSE LLAVEIZQ bloque LLAVEDER'''
    if len(p) == 8:
        p[0] = IfNode(p[3], p[6].statements if isinstance(p[6], BlockNode) else p[6])
    else:
        p[0] = IfNode(p[3],
                      p[6].statements if isinstance(p[6], BlockNode) else p[6],
                      p[10].statements if isinstance(p[10], BlockNode) else p[10])

def p_ciclo(p):
    '''ciclo : WHILE PARIZQ expresion PARDER LLAVEIZQ bloque LLAVEDER
             | FOR PARIZQ asignacion PUNTOYCOMA expresion PUNTOYCOMA asignacion PARDER LLAVEIZQ bloque LLAVEDER'''
    if len(p) == 8:
        p[0] = WhileNode(p[3], p[6].statements if isinstance(p[6], BlockNode) else p[6])
    else:
        p[0] = ForNode(p[3], p[5], p[7], p[10].statements if isinstance(p[10], BlockNode) else p[10])

def p_bloque(p):
    '''bloque : sentencia
              | sentencia bloque''' 
    if len(p) == 2:
        p[0] = BlockNode([p[1]])
    else:
        if isinstance(p[2], BlockNode):
            statements = p[2].statements
        else:
            statements = p[2]
        p[0] = BlockNode([p[1]] + statements)

def p_expresion_parentesis(p):
    'expresion : PARIZQ expresion PARDER'
    p[0] = p[2]

def p_expresion_literal_cadena(p):
    'expresion : CADENA'
    p[0] = LiteralNode(p[1])

def p_expresion_numero(p):
    'expresion : NUMERO'
    p[0] = LiteralNode(p[1])

def p_expresion_identificador(p):
    'expresion : IDENTIFICADOR'
    p[0] = IdentifierNode(p[1])

def p_expresion_uminus(p):
    'expresion : MENOS expresion'
    p[0] = UnaryOpNode('UMINUS', p[2])

def p_print(p):
    'print : PRINT PARIZQ expresion PARDER'
    p[0] = PrintNode(p[3])

def p_funcion(p):
    'expresion : PARIAS PARIZQ IDENTIFICADOR PARDER'
    p[0] = PariasCallNode(p[3])

def p_error(p):
    if p:
        lines = p.lexer.lexdata.splitlines()
        error_line = lines[p.lineno - 1] if p.lineno - 1 < len(lines) else ""
        print(f"Error de sintaxis en la linea {p.lineno}: '{error_line}'")
    else:
        print("Error de sintaxis al final del archivo")

parser = yacc.yacc(debug=True)