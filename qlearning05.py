import random

gamma = 0.9
filas = 3
columnas = 4
meta = (0, 3)
trampa = (1, 1)
movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

def simular_experimento(episodios_entrenamiento):
    # Inicializa la libreta en ceros para cada simulación
    q = {}
    for f in range(filas):
        for c in range(columnas):
            q[(f, c)] = [0.0, 0.0, 0.0, 0.0]

    # Fase de entrenamiento
    for episodio in range(episodios_entrenamiento):
        pos = (2, 0)
        pasos = 0
        while pos != meta and pos != trampa and pasos < 100:
            if random.random() < 0.1:
                accion = random.randint(0, 3)
            else:
                hoja_actual = q[pos]
                accion = hoja_actual.index(max(hoja_actual))

            df, dc = movimientos[accion]
            nueva_f = pos[0] + df
            nueva_c = pos[1] + dc

            if 0 <= nueva_f < filas and 0 <= nueva_c < columnas:
                nueva_pos = (nueva_f, nueva_c)
                if nueva_pos == meta:
                    recompensa = 1.0
                elif nueva_pos == trampa:
                    recompensa = -1.0
                else:
                    recompensa = 0.0

                q[pos][accion] = recompensa + gamma * max(q[nueva_pos])
                pos = nueva_pos
            pasos += 1

    # Fase de prueba: comprobamos si llega a la meta usando lo aprendido
    pos_actual = (2, 0)
    pasos_recorrido = 0
    while pos_actual != meta and pos_actual != trampa and pasos_recorrido < 10:
        hoja_actual = q[pos_actual]
        mejor_accion = hoja_actual.index(max(hoja_actual))
        cambio_fila, cambio_columna = movimientos[mejor_accion]
        
        nueva_f = pos_actual[0] + cambio_fila
        nueva_c = pos_actual[1] + cambio_columna
        if nueva_f < 0 or nueva_f >= filas or nueva_c < 0 or nueva_c >= columnas:
            break
            
        pos_actual = (nueva_f, nueva_c)
        pasos_recorrido += 1

    return pos_actual == meta

# --- APLICANDO LA LEY DE LOS GRANDES NÚMEROS ---
total_simulaciones = 1000
episodios_por_prueba = 12  
exitos = 0

print(f"Calculando estadísticas con {total_simulaciones} simulaciones...")

for i in range(total_simulaciones):
    if simular_experimento(episodios_por_prueba):
        exitos += 1

porcentaje_exito = (exitos / total_simulaciones) * 100

print(f"\n--- RESULTADOS ESTADÍSTICOS ---")
print(f"Éxitos logrados: {exitos} de {total_simulaciones}")
print(f"Porcentaje de efectividad global: {porcentaje_exito:.2f}%")