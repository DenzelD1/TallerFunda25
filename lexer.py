import ply.lex as lex

# --- Definición de Tokens ---
# Tokens simples y lista de palabras reservadas que el lenguaje reconocerá.
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
    'COMA',
)

# Diccionario de palabras reservadas.
# Mapea la palabra (como 'judge') a su tipo de token (como 'IF').
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
    'conquistar': 'CONQUISTAR',
    'decree': 'DECREE',
    'yield': 'YIELD',
}

# Se añaden las palabras reservadas a la lista principal de tokens.
tokens = tokens + tuple(reservadas.values())

# --- Expresiones Regulares para Tokens Simples ---
# Definen patrones para operadores y delimitadores.
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
t_COMA = r','

# --- Reglas de Tokens con Lógica ---

# Ignorar espacios en blanco y tabulaciones.
t_ignore = ' \t'

# Ignorar comentarios de una sola línea (estilo //).
def t_ignore_COMMENT(t):
    r'//.*'
    pass

# Contar los saltos de línea para el seguimiento del número de línea.
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# --- Manejo de Errores Léxicos Específicos ---
# Estas reglas capturan patrones inválidos comunes para dar mensajes de error más claros.

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

# --- Reglas de Tokens Complejas ---

# Regla para identificadores y palabras reservadas.
def t_IDENTIFICADOR(t):
    r'[A-Za-z_][A-Za-z0-9_]*'
    # Comprueba si el identificador es una palabra reservada.
    if t.value in reservadas:
        t.type = reservadas[t.value]
    return t

# Regla para números (enteros y flotantes).
def t_NUMERO(t):
    r'\d+(\.\d+)?'
    # Convierte el valor a float si tiene un punto decimal, de lo contrario a int.
    if '.' in t.value:
        t.value = float(t.value)
    else:
        t.value = int(t.value)
    return t

# Regla para cadenas de texto.
def t_CADENA(t):
    r'\"([^\\\"]|\\.)*\"'
    # Elimina las comillas dobles del inicio y del final.
    t.value = t.value[1:-1]
    return t

# Regla general para el manejo de errores léxicos.
# Se activa si ningún otro patrón coincide.
def t_error(t):
    print(f"Caracter ilegal: {t.value[0]}")
    t.lexer.skip(1)

# Construye el analizador léxico.
lexer = lex.lex()