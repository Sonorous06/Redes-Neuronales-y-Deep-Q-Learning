import random

gamma = 0.9
filas = 3
columnas = 4
meta = (0, 3)
trampa = (1, 1)

# son las 4 direcciones posibles que puede tomar el robot
# (cambio de fila, cambio de columna)
movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

# lista para traducir el número de la mejor dirección a un dibujito
flechas = ['↑', '↓', '←', '→']

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

# 1. IMPRESIÓN DEL MAPA DE VALORES (el número más alto de cada libreta)
print("--- MAPA DE VALORES MÁXIMOS ---")
for f in range(filas):
    fila_texto = ""
    for c in range(columnas):
        casilla = (f, c)
        if casilla == meta:
            fila_texto += " [ META  ] "
        elif casilla == trampa:
            fila_texto += " [TRAMPA ] "
        else:
            # Muestra el valor más alto de la hoja redondeado a 2 decimales
            max_valor = max(q[casilla])
            fila_texto += f"   {max_valor:.2f}   "
    print(fila_texto)

print("\n")

# 2. IMPRESIÓN DEL MAPA DE FLECHAS (hacia dónde decide ir)
print("--- MAPA DE DECISIONES (FLECHAS) ---")
for f in range(filas):
    fila_texto = ""
    for c in range(columnas):
        casilla = (f, c)
        if casilla == meta:
            fila_texto += " [ META ] "
        elif casilla == trampa:
            fila_texto += " [TRAMPA] "
        else:
            hoja = q[casilla]
            # busca qué número de la hoja es el más alto y saca su flecha
            mejor_accion = hoja.index(max(hoja))
            fila_texto += f"   {flechas[mejor_accion]}   "
    print(fila_texto)

# EL ROBOT CAMINA USANDO SU LIBRETA APRENDIDA
print("\n--- CAMINO REAL DEL ROBOT ---")
pos_actual = (2, 0)
camino = [pos_actual]
pasos_recorrido = 0

# Mientras no llegue a la meta, ni a la trampa, y no pase de 10 pasos
while pos_actual != meta and pos_actual != trampa and pasos_recorrido < 10:
    # Revisa la hoja de la casilla actual en la libreta del robot
    hoja_actual = q[pos_actual]
    # Busca cuál de las 4 opciones tiene el número más alto
    mejor_accion = hoja_actual.index(max(hoja_actual))
    # Traduce esa acción en el movimiento real de fila y columna
    cambio_fila, cambio_columna = movimientos[mejor_accion]
    # Calcula la nueva posición aplicando el cambio
    pos_actual = (pos_actual[0] + cambio_fila, pos_actual[1] + cambio_columna)

    # Guarda el paso en la lista para ver la ruta final
    camino.append(pos_actual)
    pasos_recorrido += 1

print("Ruta seguida:", camino)