# TallerFunda25

## Integrante

Denzel Martin Delgado Urquieta, 21.401.250-2, denzel.delgado@alumnos.ucn.cl, ITI.

## Lenguaje Medievo
Es un lenguaje de programación que consta en una mezcla del lenguaje C++ y Python con la intencionalidad de agregar caracterizaciones medievales. Asimismo, cuenta con una funcion única relacionada a la edad media llamada "parias", cuyo uso de concepto difiere ligeramente, sin embargo, mantiene el significado mismo del periodo.

## Requisitos previos para el uso

### Linux
Actualizar el sistema
```sudo apt update && sudo apt upgrade -y```

Instalar Python3 y PIP
```sudo apt install python3 python3-pip -y```

Instalar la libreria PLY
```sudo apt install python3-ply```

### Windows
Instalar Python 3 en python.org

Instalar la libreria PLY
```pip install ply```

## Como ejecutar en entorno Linux o Windows

### Linux

#### Modo Archivo
```python3 test_parser.py <programa_ejecutable>.txt```

#### Modo Interactivo
```python3 test_parser.py```

### Windows

### Modo Archivo
```python test_parser.py <programa_ejecutable>.txt```

### Modo Interactivo
```python test_parser.py```

## Diccionario (Tenga en cuenta que algunos deben de llevar ';')
```
-> + = inherit
-> - = plunder
-> * = forge
-> / = cleave
-> % = shatter
-> asignacion de variable(=) = devote
-> if = judge
-> else = exile
-> for = march
-> while = vigil
-> print = print
-> negativo (numero) = menos
-> funcion personalizada = parias(variable)
```
## Ejemplos de codigo (actualmente en programa.txt)
```
// CODIGO PARA PROBAR

entero devote 100;
flotante devote 25.5;
cadena devote "Hola, ";

print("Variable entera:");
print(entero);
print("Variable flotante:");
print(flotante);
print("Variable de cadena:");
print(cadena);

suma devote entero inherit 20; 
resta devote suma plunder 50; 
multiplicacion devote resta forge 2; 
division devote multiplicacion cleave 10; 
modulo devote 10 shatter 3;

print("Suma (100 + 20):");
print(suma);
print("Resta (120 - 50):");
print(resta);
print("Multiplicacion (70 * 2):");
print(multiplicacion);
print("Division (140 / 10):");
print(division);
print("Modulo (10 % 3):");
print(modulo);

negativo devote menos 5;
print("Numero negativo:");
print(negativo);


saludo devote cadena unir "Mundo";
print(saludo);

valorSecreto devote 42;
judge (valorSecreto == 42 && (suma > 100 || resta < 50)) {
    print("Condicion verdadera.");
} exile {
    print("Condicion falsa.");
}

judge (valorSecreto != 42) {
    print("El valor secreto no es 42.");
} exile {
    print("El valor secreto no es diferente de 42");
}

contado devote 3;
vigil (contador > 0) {
    print("Contador en:");
    print(contador);
    contador devote contador plunder 1;
}
print("Fin del bucle vigil.");

march (i devote 1; i <= 3; i devote i inherit 1) {
    print("Iteracion del bucle march:");
    print(i);
}
print("Fin del bucle march.");

nombreUsuario devote inquire("Ingrese nombre: ");
print("Bienvenido, " unir nombreUsuario);
edadUsuario devote inquire("Ingrese edad: ");

judge(edadUsuario >= 18) {
    print("Eres mayor de edad.");
} exile {
    print("Eres menor de edad.");
}

capital devote 1000;
print("Capital inicial:");
print(capital);
parias(capital);
print("Capital despues del impuesto es:");
print(capital);
```
