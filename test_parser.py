import sys
from lexer import lexer
from yacc import parser, format_ast_as_tree, EvaluationError, ReturnValue

# Función principal que procesa el código fuente:
# Realiza análisis léxico, sintáctico, genera AST y lo ejecuta
def process_code(code, context_stack): 
    print("\nIniciando analisis lexico...")
    lexer.input(code)
    cloned_lexer = lexer.clone()  # Clona el lexer para recorrer tokens sin perder el estado original

    # Guarda los tokens reconocidos en un archivo
    with open("lexer_output.txt", "w", encoding="utf-8") as lex_file:
        lex_file.write(f"{'TIPO':<20} | {'VALOR':<30} | {'LINEA':<5} | {'POSICION':<5}\n")
        lex_file.write("-" * 70 + "\n")
        while True:
            tok = cloned_lexer.token()
            if not tok: break
            token_info = f"{tok.type:<20} | {str(tok.value):<30} | {tok.lineno:<5} | {tok.lexpos:<5}"
            lex_file.write(token_info + "\n")
            
    print("-> Analisis lexico completado. Revise 'lexer_output.txt' para ver los tokens")

    print("\nIniciando analisis sintactico...")
    ast = parser.parse(code, lexer=lexer)  # Genera el árbol de sintaxis abstracta (AST)
    
    if ast:
        # Guarda el AST en un archivo legible
        ast_representation = format_ast_as_tree(ast)
        with open("ast_output.txt", "w", encoding="utf-8") as ast_file:
            ast_file.write(ast_representation)
        
        print("-> Analisis sintactico completado. Revise 'ast_output.txt' para ver el arbol")
        print("-> Detalles del parser guardados en 'parser.out'")

        print("\n--- EJECUCION DEL PROGRAMA ---")
        try:
            ast.evaluate(context_stack)  # Ejecuta el árbol usando el contexto actual
        except EvaluationError as e:
            print(e)
        except ReturnValue as r:
            # 'yield' fue llamado fuera de una función (advertencia)
            print(f"Advertencia: 'yield' en el contexto global con valor: {r.value}")
        
        print("--- FIN DE LA EJECUCION ---\n")
        
    else:
        print("No se pudo construir el AST debido a errores de sintaxis")

# Modo interactivo: permite escribir y ejecutar código desde la terminal
def run_interactive_mode():
    print("============================================================")
    print("        Terminal interactiva para su lenguaje")
    print("============================================================")
    print("* INDICACIONES")
    print("    ---Ejecutar y procesar el codigo ciclicamente.")
    print("        > (Windows) Presione Ctrl+Z y luego Enter")
    print("        > (Linux) Presione Ctrl+D\n")
    print("    ---Finalizar la terminal completamente")
    print("        > (Windows y Linux) Presione Ctrl+C\n")
    print("    ---Revisar contenido de analisis lexico generado")
    print("        > (Windows) Escriba 'type lexer_output.txt'")
    print("        > (Linux) Escriba 'cat lexer_output.txt'\n")
    print("    ---Revisar contenido de arbol AST generado")
    print("        > (Windows) Escriba 'type ast_output.txt'")
    print("        > (Linux) Escriba 'cat ast_output.txt'\n")
    print("    ---Revisar contenido detallado de analizador sintactico")
    print("        > (Windows) Escriba 'type parser.out'")
    print("        > (Linux) Escriba 'cat parser.out'")

    while True:
        try:
            global_context = {}  # Diccionario para variables globales
            context_stack = [global_context]  # Pila de contextos (para funciones y scopes)
            print("\n>>> Escriba su codigo aqui <<<")
            input_code = sys.stdin.read()  # Lee el código desde entrada estándar
            
            if not input_code.strip():
                continue

            process_code(input_code, context_stack)

        except KeyboardInterrupt:
            print("\nSaliendo de la terminal interactiva")
            break
        except EOFError:
            print("\nSaliendo de la terminal interactiva")
            break

# Modo archivo: ejecuta el código que está guardado en un archivo de texto
def run_file_mode(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()
        
        global_context = {}
        context_stack = [global_context] 
        process_code(code, context_stack)

    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado")
        sys.exit(1)

# Punto de entrada principal: decide si se usa modo archivo o interactivo
def main():
    if len(sys.argv) > 1:
        run_file_mode(sys.argv[1])
    else:
        run_interactive_mode()

if __name__ == '__main__':
    main()
