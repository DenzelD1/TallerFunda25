from yacc import parser

with open("programa.txt", "r", encoding="utf-8") as file:
    code = file.read()

context = {}

ast = parser.parse(code)
if ast:
    for node in ast:
        node.evaluate(context)
