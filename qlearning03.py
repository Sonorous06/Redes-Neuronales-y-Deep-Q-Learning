import random

filas = 3
columnas = 4
meta = (0, 3)
trampa = (1, 1)

#intentos
intentos = 1000

#son las 4 direcciones posibles que puede tomar el robot
#fila 
#columna
movimientos = [(-1, 0), (1, 0), (0, -1), (0, 1)]

llegadas = 0
caidas = 0

#pasos del robot
pasos = 0

#repite todo el recorrido 1000 veces , que siempre empieza de nuevo en (2,0)
for intento in range(intentos):
    pos = (2, 0)
    pasos = 0
    
    #el while dice , repite mientras la posicion no sea la meta y no sea la trampa y los pasos sean menos de 100
    while pos != meta and pos != trampa and pasos < 100:
        #toma la lista movimientos y se parte en dos variables
        df, dc = random.choice(movimientos)
        nueva_f = pos[0] + df
        nueva_c = pos[1] + dc
        
        #revisa que la caislla a la que quiere ir exista
        
        #columna:    0   1   2   3
        #fila 0:   [ . | . | . | . ]
        #fila 1:   [ . | . | . | . ]
        #fila 2:   [ . | . | . | . ]
        if nueva_f >= 0 and nueva_f < filas and nueva_c >= 0 and nueva_c < columnas:
            pos = (nueva_f, nueva_c)
        pasos = pasos + 1
        
        #Llegadas y caidas con contadores , pero cuentan como termino cada intento
        if pos == meta:
            llegadas = llegadas + 1
        if pos == trampa:
            caidas = caidas + 1

#EXTRA ----- probabilidades 
#llegadas / intentos da la fraccion. Si llego 120 veces de 1000 , es .12
#las multiplica por 100 para sacar el porcentaje = 12.0
#porcentaje_ninguna es lo que sobra para completar el 100%

porcentaje_meta = llegadas / intentos * 100
porcentaje_trampa = caidas / intentos * 100
porcentaje_ninguna = 100 - porcentaje_meta - porcentaje_trampa
#-----------------------------

#round (...,1) , redondea a 1 decimal
print("llegó a la meta:", round(porcentaje_meta, 1),"%")
print("cayó en la trampa:", round(porcentaje_trampa, 1),"%")
print("sin llegar a ninguna:", round(porcentaje_ninguna, 1),"%")