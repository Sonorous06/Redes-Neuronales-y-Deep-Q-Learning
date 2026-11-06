gamma = 0.9

meta = 2
trampa = 6
pos = 8

valores = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
valores[meta] = 1

recompensa = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
recompensa[trampa] = -0.2

def vecinos(valores, i):
    resultado = []
    if i > 0:
        resultado.append(valores[i - 1])
    if i < len(valores) - 1:
        resultado.append(valores[i + 1])
    return resultado

def mejor_vecino(valores, i):
    mejor = None
    for j in [i - 1, i + 1]:
        if j >= 0 and j < len(valores):
            if mejor is None or valores[j] > valores[mejor]:
                mejor = j
    return mejor

for ronda in range(30):
    for i in range(len(valores)):
        if i != meta:
            #Esto es una castigo por pasar en la trampa
            valores[i] = recompensa[i] + gamma * max(vecinos(valores, i))

print([round(v, 4) for v in valores])

camino = [pos]

while pos != meta and len(camino) < 30:
    pos = mejor_vecino(valores, pos)
    camino.append(pos)

print(camino)