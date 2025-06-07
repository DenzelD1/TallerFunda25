import sys
from lexer import lexer
from yacc import parser, format_ast_as_tree, EvaluationError

def process_code(code, context):
    print("\nIniciando analisis lexico...")
    lexer.input(code)
    cloned_lexer = lexer.clone() 
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
    ast = parser.parse(code, lexer=lexer)
    
    if ast:
        ast_representation = format_ast_as_tree(ast)
        with open("ast_output.txt", "w", encoding="utf-8") as ast_file:
            ast_file.write(ast_representation)
        
        print("-> Analisis sintactico completado. Revise 'ast_output.txt' para ver el arbol")
        print("-> Detalles del parser guardados en 'parser.out'")

        print("\n--- EJECUCION DEL PROGRAMA ---")
        try:
            ast.evaluate(context)
        except EvaluationError as e:
            print(e)  
        
        print("--- FIN DE LA EJECUCION ---\n")
        
    else:
        print("No se pudo construir el AST debido a errores de sintaxis")

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
            context = {}
            print("\n>>> Escriba su codigo aqui <<<")
            input_code = sys.stdin.read()
            
            if not input_code.strip():
                continue

            process_code(input_code, context)

        except KeyboardInterrupt:
            print("\nSaliendo de la terminal interactiva")
            break
        except EOFError:
            print("\nSaliendo de la terminal interactiva")
            break

def run_file_mode(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            code = file.read()
        
        context = {} 
        process_code(code, context)

    except FileNotFoundError:
        print(f"Error: El archivo '{file_path}' no fue encontrado")
        sys.exit(1)

def main():
    if len(sys.argv) > 1:
        run_file_mode(sys.argv[1])
    else:
        run_interactive_mode()

if __name__ == '__main__':
    main()