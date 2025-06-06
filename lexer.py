import ply.lex as lex

tokens = (
    'IDENTIFICADOR',
    'NUMERO',
    'CADENA',
    'MAYOR',
    'MENOR',
    'MAYORIGUAL',
    'MENORIGUAL',
    'IGUAL',
    'DESIGUAL',
    'AND',
    'OR',
    'NOT',
    'PARIZQ',
    'PARDER',
    'LLAVEIZQ',
    'LLAVEDER',
    'PUNTOYCOMA',
)

reservadas = {
    'devote' : 'ASIGNAR',
    'inherit' : 'SUMA',
    'plunder' : 'RESTA',
    'forge' : 'MULTIPLICACION',
    'cleave' : 'DIVISION',
    'shatter' : 'MODULO',
    'judge': 'IF',
    'exile': 'ELSE',
    'vigil': 'WHILE',
    'march': 'FOR',
    'print': 'PRINT',
    'unir' : 'UNIR',
    'menos' : 'MENOS',
    'parias' : 'PARIAS',
    'inquire': 'INQUIRE',
}

tokens = tokens + tuple(reservadas.values())

t_MAYOR = r'>'
t_MENOR = r'<'
t_MAYORIGUAL = r'>='
t_MENORIGUAL = r'<='
t_IGUAL = r'=='
t_DESIGUAL = r'!='
t_AND = r'&&'
t_OR = r'\|\|'
t_NOT = r'!'
t_PARIZQ = r'\('
t_PARDER = r'\)'
t_LLAVEIZQ = r'\{'
t_LLAVEDER = r'\}'
t_PUNTOYCOMA = r';'

t_ignore = ' \t'

def t_ignore_COMMENT(t):
    r'//.*'
    pass

def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

def t_IDENTIFICADOR_INVALIDO(t):
    r'\d+[A-Za-z_]+[A-Za-z0-9_]*'
    print(f"Error lexico: El nombre de una variable no puede comenzar con un numero -> {t.value}")
    t.lexer.skip(len(t.value))
    return None

def t_COMILLAS_NO_CERRADAS(t):
    r'\"[^\"]*$'
    print(f"Error lexico: Cadena sin cerrar -> {t.value}")
    t.lexer.skip(len(t.value))
    return None

def t_IDENTIFICADOR(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    if t.value in reservadas:
        t.type = reservadas[t.value]
    return t

def t_NUMERO(t):
    r'\d+(\.\d+)?'
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

def t_CADENA(t):
    r'\"([^\\\"]|\\.)*\"'
    t.value = t.value[1:-1]
    return t

def t_error(t):
    print(f"Caracter ilegal: {t.value[0]}")
    t.lexer.skip(1)

lexer = lex.lex()