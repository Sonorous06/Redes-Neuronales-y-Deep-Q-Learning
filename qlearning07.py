import random

#----------------------------------------------
#simplemente define las reglas del mundo , y los desplazamientos en coordenadas de fila y columna 
gamma = 0.9
filas = 3
columnas = 4
meta_original = (0, 3)
trampa = (1, 1)

movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)] # Arriba, abajo, izquierda, derecha
#(-1, 0) -> Arriba: Para subir una fila, le restas 1 a las filas (-1) y no te mueves en las columnas (0).

#(1, 0) -> Abajo: Para bajar una fila, le sumas 1 a las filas (+1) y no te mueves en las columnas (0).

#(0, -1) -> Izquierda: Para ir a la izquierda, te quedas en la misma fila (0) y le restas 1 a las columnas (-1).

#(0, 1) -> Derecha: Para ir a la derecha, te quedas en la misma fila (0) y le sumas 1 a las columnas (+1).

flechas = ['↑', '↓', '←', '→']
#----------------------------------------------

 #---------------------------------------------
 # Aca es la inicilizacion de la libre de doble estado , crea una hoja de 4 ceros para cada combinacion de (DONDE ESTOY YO Y DONDE ESTA LA META)
# Llave: ((f_robot, c_robot), (f_meta, c_meta)) -> Valor: [4 opciones]
q = {}
#primero decimos donde esta el robot
for f_r in range(filas):
    for c_r in range(columnas):
        #luego por cada lugar del robot recorremos donde puede estar la meta
        for f_m in range(filas):
            for c_m in range(columnas):
                if (f_m, c_m) != trampa:
                    #creamos la llave combinada y su hoja con 4 ceros
                    q[((f_r, c_r), (f_m, c_m))] = [0.0, 0.0, 0.0, 0.0]
 #---------------------------------------------

 #---------------------------------------------
#Arranca un ciclo , cadda episodio empieza con el robot en 2,0 y la meta en su sitio clasico 0,3
#el bucle corre hasta que el robot llega a la meta , cae en la trampa o agota un limte de 100 pasos
episodios = 3000

for episodio in range(episodios):
    pos = (2, 0)
    pos_meta = meta_original  # La meta arranca en su sitio original
    pasos = 0

    while pos != pos_meta and pos != trampa and pasos < 100:
 #---------------------------------------------
 
 #---------------------------------------------
#El robot consulta su libreta usando su posicion actual y la posicion actual de la meta , aplica la regla de el 10% de la curiosidad para explorar rutas nuevas y el 90% de experiencia para elegir la mejor opcion que conoce
        # 1. Consultamos la hoja usando el estado combinado actual
        hoja_actual = q[(pos, pos_meta)]
        
        # 10% curiosidad, 90% experto guiado por su libreta combinada
        #si sale el dado de la curiosidad 0.1 o si la pagina esta totamente en blanco , toma un ruta al azar , si no confia en la libreta``
        if random.random() < 0.1 or max(hoja_actual) == 0.0:
            accion = random.randint(0, 3)
        else:
            accion = hoja_actual.index(max(hoja_actual))
 #---------------------------------------------

            
        df, dc = movimientos[accion]
        nueva_f = pos[0] + df
        nueva_c = pos[1] + dc

        # Validamos que el movimiento exista en el mapa
        if 0 <= nueva_f < filas and 0 <= nueva_c < columnas:
            nueva_pos = (nueva_f, nueva_c)

 #---------------------------------------------
 #Mientras el robot esta entrenando , si da 4 pasos y todavia no atrapa la meta , la meta cambia a otra casilla al azar
 #es necesario sufrir durante sus 3000 practicas , su cerebro se ve obligado a aprender que la meta no es estativa , aprende a recalcular sin importar donde aparezca el objetivo
            # 2. REGLA DINÁMICA DURANTE EL ENTRENAMIENTO:
            # Si el robot da 4 pasos sin alcanzarla, ¡la meta huye en plena práctica!
            if pasos > 0 and pasos % 4 == 0 and nueva_pos != pos_meta:
                opciones_meta = [(f, c) for f in range(filas) for c in range(columnas) if (f, c) != trampa and (f, c) != nueva_pos]
                pos_meta = random.choice(opciones_meta)
 #---------------------------------------------

 #---------------------------------------------
#Aca evalua que tan bueno fue el movimiento , si pisa la meta recibe un premio , si caen en la trampa un castigo y luego actualiza la hoja especifica de esas combinaciones de estados en q , propagando el valor hacia atras para que el robot sepa que camino tomar la proxima vez 
            # Recompensas
            if nueva_pos == pos_meta:
                recompensa = 1.0
            elif nueva_pos == trampa:
                recompensa = -1.0
            else:
                recompensa = 0.0

            q[(pos, pos_meta)][accion] = recompensa + gamma * max(q[(nueva_pos, pos_meta)])
 #---------------------------------------------

            pos = nueva_pos

        pasos = pasos + 1

print("¡Entrenamiento dinámico finalizado con éxito!\n")

 #---------------------------------------------
 #Una vez terminando el entrenamiento , arranca la meta en 0,3  y exactamente en el paso 4 le cambiamos la meta 
 #como el robot ya fue entrenado en un entorno caotico y su libreta indexada tanto su posicion como la de la meta , ya no se congela ni se pierde , al ver que la meta cambio colsulta la hoja correspondiente a esa neuva cooordenada y va a a cazarla
print("--- CAMINO REAL DEL ROBOT (BUSCANDO UNA META QUE HUYE) ---")
pos_actual = (2, 0)
meta_dinamica = (0, 3) # Empieza en la esquina
camino = [pos_actual]
pasos_recorrido = 0

while pos_actual != meta_dinamica and pos_actual != trampa and pasos_recorrido < 15:
    
    # Si llega al paso 4, la meta huye frente a sus ojos
    if pasos_recorrido == 4 and pos_actual != meta_dinamica:
        opciones_validas = [(f, c) for f in range(filas) for c in range(columnas) if (f, c) != trampa and (f, c) != pos_actual]
        meta_dinamica = random.choice(opciones_validas)
        print(f"¡ALERTA! La meta huyó a: {meta_dinamica}")

    # Consulta su cerebro inteligente usando su posición y la posición actual de la meta
    hoja_actual = q[(pos_actual, meta_dinamica)]
    mejor_accion = hoja_actual.index(max(hoja_actual))
    
    df, dc = movimientos[mejor_accion]
    nueva_f = pos_actual[0] + df
    nueva_c = pos_actual[1] + dc

    if 0 <= nueva_f < filas and 0 <= nueva_c < columnas:
        pos_actual = (nueva_f, nueva_c)

    camino.append(pos_actual)
    pasos_recorrido += 1

print("Ruta final seguida:", camino)
print("Meta final:", meta_dinamica)