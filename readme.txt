"""
Problema del Puente de Tajuña
"""

Idioma: Python

1. Motivación

El objetivo es solucionar el problema del puente de tajuña en el cual no pueden cruzar el puente de manera simultanea ni coches en sentido contrario ni coches
con peatones

2. Descripción

El archivo pdf nos muestra la demostración teórica de que la solución implementada es correcta, esto es, se cumple la exclusión mutua como consecuencia del invariante del monitor, no hay deadlocks ni se produce inanición.

El archivo puente_tajuna_simple ofrece una solución sin utilizar turnos. Esta solución tiene el riesgo de sufrir inanición si, por ejemplo, estuvieran pasando coches de forma continua, entrando uno antes de que el anterior saliera. En ese caso habría una inanición de peatones.

Para evitar dicho problema, en el archivo puente_tajuna_sin_inanicion añadimos tanto turnos como procesos esperando, de esa forma evitamos una posible inanición cambiando de turno nada más salir el primer coche o peatón. Para evitar posibles bloqueos permitimos que un coche o peatón cruce pese a no ser su turno siempre que no haya un proceso distinto esperando para entrar.

Para obtener el resultado hemos utilizado el módulo multiprocessing, concretamente un monitor con un semáforo mutex propio que bloquea el acceso simultaneo a las funciones de cruce del puente. Hemos utilizado también variables del tipo Condition que, junto a su función asociada que devuelve un booleano, permiten que un proceso ejecute una función del monitor solo cuando las condiciones para hacerlo son las correctas.

3. Modo de uso

Se requieren los módulos multiprocessing, random y time, los cuales pueden ser instalados fácilmente en el ordenador. 

Se pueden cambiar los valores numéricos iniciales (número de coches, número de peatones, tiempo de cada uno en el puente etc) para comprobar que el programa funciona en diferentes situaciones. Basta con ejecutar el programa desde cualquier sitio que permita la ejecución de programas en python, como podría ser la propia terminal.
