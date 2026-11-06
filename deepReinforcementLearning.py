import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn

#El cerebro (la red neuronal)
class RedNeuronalDQN(nn.Module):
    def __init__(self):
        super(RedNeuronalDQN, self).__init__()
        self.capa1 = nn.Linear(4, 24)
        self.capa2 = nn.Linear(24, 24)
        self.salida = nn.Linear(24, 4)

    def forward(self, x):
        x = torch.relu(self.capa1(x))
        x = torch.relu(self.capa2(x))
        return self.salida(x)
    

#El entorno (mapa de 4x3 y sus reglas)
class EntornoLaberinto:
    def __init__(self):
        #Definimos las dimensiones del tablero (4 columnas x 3 filas)
        self.ancho = 4
        self.alto = 3
        
        #Posiciones iniciales 
        self.pos_robot = [0,0] #Empieza en la esquina superior derecha
        self.pos_meta = [2,1]
        
    def reiniciar(self):
        "Devuelve al robot a su posicion de salida y entrega el estado inicial"
        self.pos_robot = [0,0]
        #En lugar de escribir otra vez todo para empaquetar los numeros , dice Oye obtener_estado, ve a ver dónde quedó el robot (que ahorita es [0,0]) y dónde está la meta, y constrúyeme la lista de 4 números
        return self.obtener_estado()
    
    #Toma esas coordenadas (0.0, 0.0, 2.0, 1.0), les pone punto decimal (float) para que PyTorch no se queje, y regresa una lista limpia: [0.0, 0.0, 2.0, 1.0].
    def obtener_estado(self):
        "Empaqueta la posicion del robot y de la meta para el cerebro DQN"
        return [
            float(self.pos_robot[0]),
            float(self.pos_robot[1]),
            float(self.pos_meta[0]),
            float(self.pos_meta[1]),
        ]
        
    def paso(self, accion):
        "Mueve al robot segun la ccion elegida y valida los limites del mapa"
        #Guardamos la posicion actual por si choca contra una pared
        x_anterior, y_anterior = self.pos_robot
        
        #Modificar las coordenas segun la accion
        if accion == 0: #arriba
            self.pos_robot[1] -= 1
        elif accion == 1: #abajo
            self.pos_robot[1] += 1
        elif accion == 2: #izquierda
            self.pos_robot[0] -= 1
        elif accion == 3: #derecha
            self.pos_robot[0] += 1
            
        #Frenar al robot su intenta salirse del tablero (paredes invisibles)
        #el min evita que te pases por la derecha del tablero (tope maximo : ancho - 1)
        #el max evita que te caigas por la izquierda (tope minimo : 0)
        self.pos_robot[0] = max(0, min(self.pos_robot[0], self.ancho -1 ))
        self.pos_robot[1] = max(0, min(self.pos_robot[1], self.alto -1 ))
        
        #Detectar si llego a la meta
        llego_a_meta = self.pos_robot == self.pos_meta
        
        #Este return entrega dos cosas al mismo tiempo
        
        #"obtener_estado()" , devuelve la lista de los 4 numeros deciamles
        #toma la foto de donde esta (despues de dar el primer paso) , devuelve 4 numeros los dos primeros son x,y del robot y los otros dos son x,y de la meta
        
        #llego_a_meta , duelve un indicador de verdad , si o no , respondiendo a la pregunta : ¿El robot acaba de pisar la misma casilla que la meta?
        return self.obtener_estado(), llego_a_meta
    
    
# El bucle de prueba 
if __name__ == "__main__":
    entorno = EntornoLaberinto()
    cerebro = RedNeuronalDQN()
    
    #Inicia partida
    # 1. Arrancamos partida (¡con los paréntesis!)
    estado_actual = entorno.reiniciar()
    print(f"SALIDA - ESTADO INICIAL : {estado_actual}")
    
    #Simulamos 6 turnos moviendonos a la derecha (accion 3)
    for turno in range(6):
        #Convertimos la lista de python en un tensor para el cerebro
        tensor_estado = torch.tensor(estado_actual, dtype=torch.float32)
        
        #El cerebro emite sus 4 corazonadas (q-values)
        q_valores = cerebro(tensor_estado)
        print(f"\nTurno {turno + 1} | Cerebro analizando... Q-Values: {q_valores}")
        
        ##Por ahora elegimos la accion 3 manualmente para probar el mapa
        accion_elegida = 3
        
        #El entorno ejecuta el movimiento
        nuevo_estado, llego_a_meta = entorno.paso(accion_elegida)
        print(
        f"-> Robot se movió. Nueva posición/estado en el mapa: {nuevo_estado}"
        )
        
        if llego_a_meta:
            print("El robot llego a la meta")
            break
        
        estado_actual = nuevo_estado
        