import os
import random
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn
import torch.optim as optim


# El cerebro (la red neuronal)
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
    

# El entorno (mapa de 8x8 y sus reglas)
class EntornoLaberinto:
    def __init__(self):
        # Definimos las dimensiones del tablero
        self.ancho = 8
        self.alto = 8
        
        # Posiciones iniciales 
        self.pos_robot = [0, 0] # Empieza en la esquina superior izquierda
        self.pos_meta = [7, 7]
        
    def reiniciar(self):
        "Devuelve al robot a su posicion de salida y entrega el estado inicial"
        self.pos_robot = [0, 0]
        return self.obtener_estado()
    
    def obtener_estado(self):
        "Empaqueta la posicion del robot y de la meta para el cerebro DQN"
        return [
            float(self.pos_robot[0]),
            float(self.pos_robot[1]),
            float(self.pos_meta[0]),
            float(self.pos_meta[1]),
        ]
        
    def paso(self, accion):
        # Guardamos la posición actual por si se necesita
        x_anterior, y_anterior = self.pos_robot

        # Modificar las coordenas segun la accion
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

        # Definir las coordenadas de las trampas [X, Y]
        trampas = [[0, 5], [5, 0]]

        # Aca detecta las zonas prohibidas 
        llego_a_meta = self.pos_robot == self.pos_meta
        cayo_en_trampa = self.pos_robot in trampas

        # Sistema de recompensa y finalización
        if llego_a_meta:
            recompensa = 10.0
            terminado = True
        elif cayo_en_trampa:
            recompensa = -5.0  # Castigo severo por caer en la trampa
            terminado = True  # Termina el episodio al caer en trampa
        elif self.pos_robot == [x_anterior, y_anterior]:
            recompensa = -1.0  # castigo por chocar contra la pared
            terminado = False
        else:
            recompensa = -0.1  # castigo leve por paso
            terminado = False

        return self.obtener_estado(), recompensa, terminado
    

# El bucle de prueba 
if __name__ == "__main__":
    entorno = EntornoLaberinto()
    cerebro = RedNeuronalDQN()

    criterio = nn.MSELoss()
    optimizer = optim.Adam(cerebro.parameters(), lr=0.001)
    
    numero_episodios = 1000
    
    # Parametros de la curiosidad
    epsilon = 1.0 
    epsilon_decay = 0.98 
    epsilon_min = 0.05 
    
    # ==========================================
    # MODIFICACIÓN: Variable para registrar una sola vez el primer éxito
    # ==========================================
    primera_vez_exito = None
    
    print("Iniciando entrenamiento...")
    
    for episodio in range(numero_episodios):
        estado_actual = entorno.reiniciar()
        pasos_totales = 0
        llego_a_meta_en_episodio = False
        
        for turno in range(75):
            pasos_totales += 1
            tensor_estado = torch.tensor(estado_actual, dtype=torch.float32)
   
            if random.random() < epsilon:
                accion_elegida = random.randint(0, 3)
            else:
                with torch.no_grad():
                    q_valores = cerebro(tensor_estado)
                    accion_elegida = torch.argmax(q_valores).item()
         
            nuevo_estado, recompensa, terminado = entorno.paso(accion_elegida)
            
            q_valores = cerebro(tensor_estado)
            q_predicho = q_valores[accion_elegida]
            
            with torch.no_grad():
                q_objetivo = q_predicho.clone()
                q_objetivo = recompensa + 0.9 * torch.max(cerebro(torch.tensor(nuevo_estado, dtype=torch.float32)))
            
            loss = criterio(q_predicho, q_objetivo)
                
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            
            if terminado:
                if entorno.pos_robot == entorno.pos_meta:
                    llego_a_meta_en_episodio = True
                    
                    # ==========================================
                    # MODIFICACIÓN: Imprime y guarda el primer éxito UNA SOLA VEZ
                    # ==========================================
                    if primera_vez_exito is None:
                        primera_vez_exito = episodio + 1
                        print(f"[PUNTO CLAVE] El agente encontró la ruta ganadora por primera vez en el **Episodio {primera_vez_exito}** (en {pasos_totales} pasos).\n")
                break
            
            estado_actual = nuevo_estado
        
        # ==========================================
        # MODIFICACIÓN: Telemetría restringida ÚNICAMENTE a los primeros 5 episodios (elimina el spam de loops)
        # ==========================================
        if (episodio + 1) <= 5:
            with torch.no_grad():
                tensor_final = torch.tensor(entorno.obtener_estado(), dtype=torch.float32)                    
                q_actuales = cerebro(tensor_final)
                q_redondeados = [round(val.item(), 2) for val in q_actuales]
                
            estado_texto = "¡LLEGÓ A LA META!" if llego_a_meta_en_episodio else f"Posición final: {entorno.pos_robot}"
            print(f"[Episodio {episodio + 1}] {estado_texto} | Q-values: {q_redondeados} | Curiosidad: {epsilon:.2f}")
            
        epsilon = max(epsilon_min, epsilon * epsilon_decay)

    print("ENTRENAMIENTO TERMINADO")

    # --- PRUEBA EN FRÍO (Cerebro puro sin azar) ---
    print("\n--- PRUEBA EN FRÍO (Cerebro puro sin azar) ---")
    estado_actual = entorno.reiniciar()
    pasos_prueba = 0
    terminado = False

    # Lista para guardar el camino exacto y poder imprimirlo
    camino_recorrido = [list(entorno.pos_robot)]

    for _ in range(75):
        with torch.no_grad():
            tensor_estado = torch.tensor(estado_actual, dtype=torch.float32)
            q_valores = cerebro(tensor_estado)
            accion = torch.argmax(q_valores).item()
        
        nuevo_estado, recompensa, terminado = entorno.paso(accion)
        pasos_prueba += 1
        
        # Guardamos cada paso que da el robot en la prueba
        camino_recorrido.append(list(entorno.pos_robot))
        
        if terminado:
            break
        estado_actual = nuevo_estado

    # Verificamos si realmente ganó o si cayó en trampa
    llego_a_meta = (entorno.pos_robot == entorno.pos_meta)

    if llego_a_meta:
        print(f"¡El robot llegó a la meta usando solo su cerebro en {pasos_prueba} pasos!")
        print("Camino exacto que siguió:", camino_recorrido)
    else:
        print("El robot cayó en una trampa o se quedó varado.")
        print("Camino que intentó seguir:", camino_recorrido)