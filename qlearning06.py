####Hasta ahora el robot ha vivido en un mundo estatico 

##MUNDO ESTATICO
#O sea la meta siempre esta en la misma esquina y la trampa en la misma casilla ademas las paredes con dijas , bajo estas condiciones la libre Q funciona como una guia perfecta
#una vez memorizada , puede caminar con los ojos cerrados

##MUNDO DINAMICO
#¿Qué pasa si el laberinto se convierte en una película en movimiento? Imaginemos que la trampa da un paso aleatorio cada vez que el robot se mueve, o que la meta cambia de posición de vez en cuando.

import random

gamma = 0.9
filas = 3
columnas = 4
meta = (0, 3)
trampa = (1, 1)

# son las 4 direcciones posibles que puede tomar el robot
# (cambio de fila, cambio de columna)
movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]


# la libreta del robot: una hoja por casilla, con 4 renglones
# [arriba, abajo, izquierda, derecha], todos en 0 porque no sabe nada
q = {}
for f in range(filas):
    for c in range(columnas):
        q[(f, c)] = [0.0, 0.0, 0.0, 0.0]

# cuántos recorridos completos va a hacer el robot
episodios = 1000
    
for episodio in range(episodios):

    # en cada episodio el robot vuelve a empezar en la esquina de abajo a la izquierda
    pos = (2, 0)
    pasos = 0

    # un recorrido: termina si cae en la meta, en la trampa, o a los 100 pasos
    while pos != meta and pos != trampa and pasos < 100:

        # 10% de las veces tira el dado y se mueve al azar (curiosidad)
        # 90% de las veces hace caso ciego a lo que dice su libreta (experto)
        
        #si saca menos de 0.1 , se mueve como quiera
        if random.random() < 0.1:
            accion = random.randint(0, 3)
        #este es el 90% , solo sigue las anotaciones (cual tiene el valor mayor)
        else:
            hoja_actual = q[pos]
            accion = hoja_actual.index(max(hoja_actual))
            
        df, dc = movimientos[accion]

        # calcula a qué casilla iría, sin moverse todavía
        nueva_f = pos[0] + df
        nueva_c = pos[1] + dc

        # revisa que la casilla a la que quiere ir exista
        if nueva_f >= 0 and nueva_f < filas and nueva_c >= 0 and nueva_c < columnas:
            nueva_pos = (nueva_f, nueva_c)

            # el mapa le da la recompensa después de dar el paso
            if nueva_pos == meta:
                recompensa = 1.0
            elif nueva_pos == trampa:
                recompensa = -1.0
            else:
                recompensa = 0.0

            # Bellman: lo que gané ahora + gamma por lo mejor de la hoja donde caí
            # solo se anota en el renglón que usó (q[pos][accion])
            q[pos][accion] = recompensa + gamma * max(q[nueva_pos])

            # ahora sí se mueve
            pos = nueva_pos

        # suma uno al contador, haya podido moverse o no
        pasos = pasos + 1

# EL ROBOT CAMINA USANDO SU LIBRETA APRENDIDA
print("\n--- CAMINO REAL DEL ROBOT ---")
pos_actual = (2, 0)
camino = [pos_actual]
pasos_recorrido = 0

#creamos una meta dinamica 
meta_dinamica = meta

#El while ahora evalua contra meta_dinamica 
while pos_actual != meta_dinamica and pos_actual != trampa and pasos_recorrido < 10:
    
    #si se cumpple el paso 6 y aun no llega a la meta , la meta cambia de posicion
    if pasos_recorrido == 2:
        
        #este ciclo lo que hace es recorres todas las filas (0 a 2) y todas las columnas (0 a 3) para crear una lista conn todas las coordenas posibles
        todas_las_casillas = [(f, c) for f in range(filas) for c in range(columnas)]
        
        #toma esa lista de 12 casillas y les aplica un filtro , "Guarda en esta nueva lista únicamente las casillas que cumplan dos condiciones":
        # 1. Que la casilla no sea la trampa
        # 2. Que la casilla no sea donde está parado el robot en este preciso instante
        opciones_validas = [c for c in todas_las_casillas if c != trampa and c != pos_actual]
        
        #una vez que tenemos la lista limpia de opciones validas , saca una coordenada al azar y asgina a la variable "meta_dinamica"
        meta_dinamica = random.choice(opciones_validas)
        print("La meta ha huido a otra casilla")
        
    # Revisa la hoja de la casilla actual en la libreta del robot
    hoja_actual = q[pos_actual]
    # Busca cuál de las 4 opciones tiene el número más alto
    mejor_accion = hoja_actual.index(max(hoja_actual))
    # Traduce esa acción en el movimiento real de fila y columna
    cambio_fila, cambio_columna = movimientos[mejor_accion]
    
    # Calcula la nueva posición aplicando el cambio
    nueva_f = pos_actual[0] + cambio_fila
    nueva_c = pos_actual[1] + cambio_columna

    # Validación para asegurarnos de que no se salga del mapa
    if 0 <= nueva_f < filas and 0 <= nueva_c < columnas:
        pos_actual = (nueva_f, nueva_c)

    # Guarda el paso en la lista para ver la ruta final
    camino.append(pos_actual)
    pasos_recorrido += 1

print("Ruta seguida:", camino)
print("La meta terminó en:", meta_dinamica)
        
    
# POR AHORA SI EL ROBOT LLEGA EN 5 PASOS CON 1000 EPISODIOS  NO SE CUMPLE LA CONDICION DE MOVER LA META , POR LO QUE TODO SIGUE EN ORDEN

#PERO SI LLEGA A LA CONDICION , EL ROBOT LLEGA A 0,3 Y SE PIERDE TOTALMENTE , SABE QUE LA META ES 0,3 PERO ESA ESA LA META INDICADA
  
