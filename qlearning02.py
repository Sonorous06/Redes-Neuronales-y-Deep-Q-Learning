gamma = 0.9

valores = [
    [0, 0, 0, 1],
    [0, 0, 0, 0],
    [0, 0, 0, 0],
]

meta = (0, 3)
# se hace un arreglo de trampas por que estamos aumentando 1 
trampas = [(1,1)]

#Se marca con un ciclo, pq las trampas estan en una lsita , y el ciclo evita escribir una linea por cada una
# 'para cada pareja (f,c) de la lista trampas , pon un -1 en la casilla'
for f, c in trampas:
    valores[f][c] = -1

def vecinos(valores, f, c):
    resultado = []
    if f > 0:
        resultado.append(valores[f - 1][c])
    if f < len(valores) - 1:
        resultado.append(valores[f + 1][c])
    if c > 0:
        resultado.append(valores[f][c - 1])
    if c < len(valores[0]) - 1:
        resultado.append(valores[f][c + 1])
    return resultado

for ronda in range(20):
    for f in range(len(valores)):
        for c in range(len(valores[0])):
            # El not in dice "esta casilla no esta en la lista de trampas?"
            if (f, c) != meta and (f, c) not in trampas:
                valores[f][c] = gamma * max(vecinos(valores, f, c))

for fila in valores:
    print([round(v, 3) for v in fila])

def mejor_vecino(valores, f, c):
    total_filas = len(valores)
    total_columnas = len(valores[0])
    mejor = None
    for fila_vecina, col_vecina in [(f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)]:
        if fila_vecina >= 0 and fila_vecina < total_filas and col_vecina >= 0 and col_vecina < total_columnas:
            if mejor is None or valores[fila_vecina][col_vecina] > valores[mejor[0]][mejor[1]]:
                mejor = (fila_vecina, col_vecina)
    return mejor

print(mejor_vecino(valores, 1, 0))

pos = (0,0)
camino = [pos]
#Y en cada vuelta del while pasa esto:
#pos = mejor_vecino(valores, pos[0], pos[1])   # el robot da un paso
#camino.append(pos)
  
while pos != meta and len(camino) < 30:
    #pos [0] es la fila y pos[1] es la columna
    pos = mejor_vecino(valores, pos[0], pos[1]) 
    #camino es una lista donde el robot anota por donde pasar , empieza por la casilla de salida
    camino.append(pos)
print(camino)