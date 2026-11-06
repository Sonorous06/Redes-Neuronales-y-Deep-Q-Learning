#PILAR 1 , hasta ahora el robot da un paso , calcula el error ya actualiza su cerebro con ese unico paso , el probelma es que los pasos estan conectados en cadena , si el robot se queda atorado chocando 5 veces contra la pared su cerebro se obsesiona con esa racha negativa y olvida todo lo de los caps anterirores
#Le agregamos al programa memoria historia ( una especie de libreta) , cada vez que el robot se meuve guardamos esa vivencia ( [estado_actual, accion, recompensa, nuevo_estado] ) , cuando la red va a entrenar , no solo usa el ultimo paso que dio si no que abre la libreta y saca un punado de recuerdos Al entrenar con recuerdos revueltos y aleatorios del pasado, rompemos la racha del momento y la red aprende de forma equilibrada y general.

import os
import random
from collections import deque
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn
import torch.optim as optim


# El cerebro (la red neuronal) - 4 entradas originales
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
    

#BUFFER ---> caja de recuerdos
class ReplayBuffer:
    def __init__(self, capacidad=2000):
        #una cola de tamano fijo que elimina los recuerdos mas viejos cuando se llena
        self.buffer = deque(maxlen=capacidad)
    def guardar(self, experiencia):
        #guarda la foto (estado, accion, recompensa, nuevo_estado, terminado)
        self.buffer.append(experiencia)
    def muestrear(self, batch_size):
        #saca un puno de recuerdos al azar de la caja
        return random.sample(self.buffer, batch_size)
    def __len__(self):
        return len(self.buffer)


# El entorno (mapa de 8x8 con inicio aleatorio)
class EntornoLaberinto:
    def __init__(self):
        self.ancho = 8
        self.alto = 8
        self.pos_meta = [7, 7]
        self.trampas = [[0, 5], [5, 0], [4 ,7], [7,3], [4,4]]
        self.pos_robot = [0, 0]
        
    def reiniciar(self):
        while True:
            self.pos_robot = [random.randint(0, self.ancho - 1), random.randint(0, self.alto - 1)]
            if self.pos_robot != self.pos_meta and self.pos_robot not in self.trampas:
                break
        return self.obtener_estado()
    
    def obtener_estado(self):
        return [
            float(self.pos_robot[0]),
            float(self.pos_robot[1]),
            float(self.pos_meta[0]),
            float(self.pos_meta[1]),
        ]
        
    def paso(self, accion):
        x_anterior, y_anterior = self.pos_robot

        if accion == 0:  # arriba
            self.pos_robot[1] -= 1
        elif accion == 1:  # abajo
            self.pos_robot[1] += 1
        elif accion == 2:  # izquierda
            self.pos_robot[0] -= 1
        elif accion == 3:  # derecha
            self.pos_robot[0] += 1

        self.pos_robot[0] = max(0, min(self.pos_robot[0], self.ancho - 1))
        self.pos_robot[1] = max(0, min(self.pos_robot[1], self.alto - 1))

        llego_a_meta = self.pos_robot == self.pos_meta
        cayo_en_trampa = self.pos_robot in self.trampas

        if llego_a_meta:
            recompensa = 10.0
            terminado = True
        elif cayo_en_trampa:
            recompensa = -5.0  
            terminado = True  
        elif self.pos_robot == [x_anterior, y_anterior]:
            recompensa = -1.0  
            terminado = False
        else:
            recompensa = -0.1  
            terminado = False

        return self.obtener_estado(), recompensa, terminado
    

# El bucle de entrenamiento y prueba
if __name__ == "__main__":
    entorno = EntornoLaberinto()
    cerebro = RedNeuronalDQN()

    criterio = nn.MSELoss()
    optimizer = optim.Adam(cerebro.parameters(), lr=0.001)
    
    # Inicializamos nuestra caja de recuerdos con capacidad para 2000 experiencias
    memoria = ReplayBuffer(capacidad=2000)
    batch_size = 32  # Cantidad de recuerdos que sacaremos a la vez para entrenar
    
    numero_episodios = 500
    epsilon = 1.0 
    epsilon_decay = 0.98 
    epsilon_min = 0.05 
    
    primera_vez_exito = None
    
    print("Iniciando entrenamiento con Experience Replay (Caja de Recuerdos)...")
    
    for episodio in range(numero_episodios):
        estado_actual = entorno.reiniciar()
        pos_inicio_episodio = list(entorno.pos_robot)
        pasos_totales = 0
        llego_a_meta_en_episodio = False
        
        for turno in range(75):
            pasos_totales += 1
            tensor_estado = torch.tensor(estado_actual, dtype=torch.float32)
   
            # Selección de acción (Exploración vs Explotación)
            if random.random() < epsilon:
                accion_elegida = random.randint(0, 3)
            else:
                with torch.no_grad():
                    q_valores = cerebro(tensor_estado)
                    accion_elegida = torch.argmax(q_valores).item()
         
            # Ejecutar acción en el entorno
            nuevo_estado, recompensa, terminado = entorno.paso(accion_elegida)
            
            # 1. Guardamos la "foto" en la caja de recuerdos
            #metemos 5 datos y los guarda en la caja de recuerdos
            memoria.guardar((estado_actual, accion_elegida, recompensa, nuevo_estado, terminado))
            
            # 2. Solo entrenamos si la caja ya juntó al menos 32 recuerdos
            #si la caja tiene al menos ya 32 recuerdos guardados , saca un paquete aleatorio de 32 fotos revueltas
            if len(memoria) >= batch_size:
                lote = memoria.muestrear(batch_size)
                
                # Desempaquetamos el lote en listas separadas
                #como cada tarjeta tiene 5 datos juntos ,la funcion toma las 32 tarjetas y las desagrupa en cada columna
                estados_b, acciones_b, recompensas_b, nuevos_estados_b, terminados_b = zip(*lote)
                
                t_estados = torch.tensor(estados_b, dtype=torch.float32)
                t_acciones = torch.tensor(acciones_b, dtype=torch.long)
                t_recompensas = torch.tensor(recompensas_b, dtype=torch.float32)
                t_nuevos = torch.tensor(nuevos_estados_b, dtype=torch.float32)
                t_terminados = torch.tensor(terminados_b, dtype=torch.float32)
                
                # Calculamos las predicciones actuales de la red para el lote
                q_valores_actuales = cerebro(t_estados)
                q_predicho = q_valores_actuales.gather(1, t_acciones.unsqueeze(1)).squeeze(1)
                
                # Calculamos los valores objetivo usando la ecuación de Bellman para el lote
                with torch.no_grad():
                    max_q_nuevo = torch.max(cerebro(t_nuevos), dim=1)[0]
                    q_objetivo = t_recompensas + 0.9 * max_q_nuevo * (1 - t_terminados)
                
                # Calculamos el error (Loss) y actualizamos los pesos del cerebro
                loss = criterio(q_predicho, q_objetivo)
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
            
            if terminado:
                if entorno.pos_robot == entorno.pos_meta:
                    llego_a_meta_en_episodio = True
                    if primera_vez_exito is None:
                        primera_vez_exito = episodio + 1
                        print(f"[PUNTO] El agente encontró la ruta con éxito por primera vez en el **Episodio {primera_vez_exito}** (en {pasos_totales} pasos).")
                break
            
            estado_actual = nuevo_estado
        
        if (episodio + 1) <= 5:
            with torch.no_grad():
                tensor_final = torch.tensor(entorno.obtener_estado(), dtype=torch.float32)                    
                q_actuales = cerebro(tensor_final)
                q_redondeados = [round(val.item(), 2) for val in q_actuales]
                
            estado_texto = "¡LLEGÓ A LA META!" if llego_a_meta_en_episodio else f"Posición final: {entorno.pos_robot}"
            print(f"[Episodio {episodio + 1}] Inicio: {pos_inicio_episodio} -> {estado_texto} | Curiosidad: {epsilon:.2f}")
            
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    print("ENTRENAMIENTO TERMINADO")

    if primera_vez_exito is None:
        print("El agente no logró alcanzar la meta durante el entrenamiento con estas condiciones.")

    # --- PRUEBA EN FRÍO ---
    print("--- PRUEBA EN FRÍO (Cerebro con memoria) ---")
    estado_actual = entorno.reiniciar()
    inicio_prueba = list(entorno.pos_robot)
    pasos_prueba = 0
    terminado = False

    camino_recorrido = [list(entorno.pos_robot)]

    for _ in range(75):
        with torch.no_grad():
            tensor_estado = torch.tensor(estado_actual, dtype=torch.float32)
            q_valores = cerebro(tensor_estado)
            accion = torch.argmax(q_valores).item()
        
        nuevo_estado, recompensa, terminado = entorno.paso(accion)
        pasos_prueba += 1
        camino_recorrido.append(list(entorno.pos_robot))
        
        if terminado:
            break
        estado_actual = nuevo_estado

    llego_a_meta = (entorno.pos_robot == entorno.pos_meta)

    if llego_a_meta:
        print(f"¡El robot llegó a la meta desde {inicio_prueba} usando su memoria en {pasos_prueba} pasos!")
        print("Camino exacto que siguió:", camino_recorrido)
    else:
        print(f"El robot salió de {inicio_prueba}, pero cayó en una trampa o se quedó varado.")
        print("Camino que intentó seguir:", camino_recorrido)