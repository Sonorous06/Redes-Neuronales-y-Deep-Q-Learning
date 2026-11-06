#PILAR 2 , hasta ahora con el pilar 1 , la misma red neuronal hacia dos tareas al mismo tiempo , decidir el sig movimiento del robot y calcular la meta matematica a futuro . El problema es que como la red actuliza sus pesos constantemente en cada lote , intentabamos disparale a un blanco movil, la regla con la que mediamos el exito se movia y cambiaba de lugar a cada milisegundo , provocando inestablidad matematica , haciendo que el entrenamiento colapse

#Le agregamos al programa un segundo cerebro identico que actua como una red objetivo congelada .La red principal sigue tomando decisiones y aprendiendo de forma activa, pero cuando necesitamos calcular el valor a futuro para aprender, consultamos esta copia estática que no cambia de opinión a cada segundo. Cada cierta cantidad de episodios, le copiamos los avances de la red principal para actualizarla de golpe. Al fijar el punto de referencia y evitar que el blanco se mueva, le damos estabilidad matemática absoluta al sistema.
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch #calculos matematicos masivmos , manejar tensores
import torch.nn as nn #submodulo de redes neruonales
import torch.optim as optim #algoritmos como adam , ajustar y corregir pesos
import random 
import numpy as np #manejo de vectores y matrices
from collections import deque # construir caja de recuerdos

# --- 1. CONFIGURACIÓN DE LA RED NEURONAL ---
class RedQ(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(RedQ, self).__init__()
        self.fc1 = nn.Linear(input_dim, 32)
        self.fc2 = nn.Linear(32, 32)
        self.out = nn.Linear(32, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.out(x)

# --- 2. LA CAJA DE RECUERDOS (PILAR 1: Experience Replay) ---
class ReplayBuffer:
    def __init__(self, capacidad=2000):
        self.buffer = deque(maxlen=capacidad)
        
    def guardar(self, experiencia):
        self.buffer.append(experiencia)
        
    def muestrear(self, batch_size):
        return random.sample(self.buffer, batch_size)
        
    def __len__(self):
        return len(self.buffer)

# --- 3. EL ENTORNO (LABERINTO) ---
class EntornoLaberinto:
    def __init__(self):
        self.ancho = 8
        self.alto = 8
        self.pos_meta = [7, 7]
        # Tus trampas estratégicas y la del centro
        self.trampas = [[0, 5], [5, 0], [4, 7], [7, 3], [3, 3]]
        self.pos_robot = [0, 0]

    def reiniciar(self, pos_inicial=None):
        if pos_inicial is not None:
            self.pos_robot = list(pos_inicial)
        else:
            # Posición inicial aleatoria para generalizar
            self.pos_robot = [random.randint(0, self.ancho-1), random.randint(0, self.alto-1)]
            while self.pos_robot == self.pos_meta or self.pos_robot in self.trampas:
                self.pos_robot = [random.randint(0, self.ancho-1), random.randint(0, self.alto-1)]
        return self.obtener_estado()

    def obtener_estado(self):
        # Normalizamos las coordenadas dividiendo entre 7 para la red neuronal
        return np.array([self.pos_robot[0] / 7.0, self.pos_robot[1] / 7.0], dtype=np.float32)

    def paso(self, accion):
        # Acciones: 0=Arriba, 1=Abajo, 2=Izquierda, 3=Derecha
        if accion == 0 and self.pos_robot[1] > 0:
            self.pos_robot[1] -= 1
        elif accion == 1 and self.pos_robot[1] < self.alto - 1:
            self.pos_robot[1] += 1
        elif accion == 2 and self.pos_robot[0] > 0:
            self.pos_robot[0] -= 1
        elif accion == 3 and self.pos_robot[0] < self.ancho - 1:
            self.pos_robot[0] += 1

        estado_siguiente = self.obtener_estado()
        
        # Evaluar recompensas, trampas y meta
        if self.pos_robot == self.pos_meta:
            return estado_siguiente, 10.0, True
        elif self.pos_robot in self.trampas:
            return estado_siguiente, -5.0, True
        else:
            return estado_siguiente, -0.1, False

# --- 4. CONFIGURACIÓN DEL ENTRENAMIENTO ---
env = EntornoLaberinto()

#entrada --> como el robot necesita saber donde esta parado , le pasamos dos coordenadas normalizadas , eje x y eje y
input_dim = 2
#salida --> son las opciones de decision que el cerebro tiene que evaluar y apuntar , arriba , abajo , izquierda y derecha
output_dim = 4

cerebro = RedQ(input_dim, output_dim)

#agregamos segundo cerebro -----------------------

#fabricamos nuestro cuaderno de reglas en el estante, una copia exacta y simetrica de la red principal
cerebro_objetivo = RedQ(input_dim, output_dim)
#como el cerebro principal acaba de nacer con pesos aleatorios , le decimios a la red objetivo que copie exactaamente esos mismos numeros para que ambos arranquen desde el mismo punto de partida
cerebro_objetivo.load_state_dict(cerebro.state_dict())
#esta funcion avisa al sistema que esta red se usara unicamente para leer y evaluar datos , apagando cualquier ajuste autiomatico de pesos 
cerebro_objetivo.eval()

#-------------------------------------------------

optimizar = optim.Adam(cerebro.parameters(), lr=0.005)
criterio = nn.MSELoss()

memoria = ReplayBuffer(capacidad=2000)
batch_size = 32
gamma = 0.99

# Afinamos epsion , ya que a los 130,150 episodios el epsilon cae casi hasta cero. esto significa que el robot pierde toda su iniciativa de explorar y obedece a su red, si en una casilla se quedo con una duda o un bache mental , como ya no tiene aletoriedad para saltar fuera de el , se queda atrapado dando vueltas en un bucle infinito

#epsilon = 1.0
#epsilon_min = 0.01
#epsilon_decay = 0.98

epsilon = 1.0
epsilon_min = 0.08 #mantenemos un 8% para que nunca se quede ciego
epsilon_decay = 0.99 #descenso suave a lo largo de los ep

episodios = 150

print("Iniciando entrenamiento con Experience Replay (Caja de Recuerdos)...")

for ep in range(1, episodios + 1):
    estado = env.reiniciar()
    terminado = False
    pasos = 0
    encontro_meta = False

    while not terminado and pasos < 100:
        pasos += 1
        
        # Estrategia Epsilon-Greedy (Curiosidad)
        if random.random() < epsilon:
            accion = random.randint(0, 3)
        else:
            with torch.no_grad():
                tensor_estado = torch.FloatTensor(estado).unsqueeze(0)
                q_valores = cerebro(tensor_estado)
                accion = torch.argmax(q_valores).item()

        estado_siguiente, recompensa, terminado = env.paso(accion)
        
        if env.pos_robot == env.pos_meta:
            encontro_meta = True

        # Guardar en la caja de recuerdos (Pilar 1)
        memoria.guardar((estado, accion, recompensa, estado_siguiente, terminado))
        estado = estado_siguiente

        # Entrenar por lotes si la caja tiene suficientes recuerdos
        if len(memoria) >= batch_size:
            lote = memoria.muestrear(batch_size)
            estados, acciones, recompensas, estados_sigs, terminados = zip(*lote)

            estados = torch.FloatTensor(np.array(estados))
            acciones = torch.LongTensor(acciones).unsqueeze(1)
            recompensas = torch.FloatTensor(recompensas)
            estados_sigs = torch.FloatTensor(np.array(estados_sigs))
            terminados = torch.FloatTensor(terminados)

            # Cálculo de Q actual
            q_actuales = cerebro(estados).gather(1, acciones).squeeze(1)

            # AQUI ES DONDE ENTRA EL PILAR 2 (Calculo del Objetivo con la Red Congelada)
            with torch.no_grad():
                #q_siguiente_max = cerebro(estados_sigs).max(1)[0] <---- ANTERIOR 
                #en lugar de pregunatarle al cerebro activo (que esta cambiando sus pesos a cada rato y alterando la meta), le ordenamos que consulte al cerebro objetivo congelado
                
                q_siguiente_max = cerebro_objetivo(estados_sigs).max(1)[0] #<---- NUEVO
                q_objetivo = recompensas + (gamma * q_siguiente_max * (1 - terminados))

            perdida = criterio(q_actuales, q_objetivo)
            
            optimizar.zero_grad()
            perdida.backward()
            optimizar.step()

    # PILAR 2: Sincronización periódica (Actualizar el estante cada 5 episodios)
    # cada vez que el numero de ep sea multiplo de 5 , el robot se detiene un moomento
    if ep % 5 == 0:
        #toma su cuaderno de borrador (lleno de tacticas y aprendizajes sobre como esquivar metas), sca la foto identica y reemplaza por completo el cuaderno viejo que estaba guarado
        cerebro_objetivo.load_state_dict(cerebro.state_dict())

    if ep % 10 == 0:
        estado_txt = "¡Llegó a la meta!" if encontro_meta else "Siguiendo explorando"
        print(f"Episodio {ep:3d} | Epsilon: {epsilon:.2f} | Pasos: {pasos:2d} | {estado_txt}")

    if epsilon > epsilon_min:
        epsilon *= epsilon_decay

print("\nENTRENAMIENTO TERMINADO\n")