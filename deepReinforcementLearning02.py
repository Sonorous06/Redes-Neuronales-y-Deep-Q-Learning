
#Este es el segundo capitulo , en el 01 el robot avanza de forma ciega ,avanzando a la derecha por la regla (simplemente esta recorriendo el mapa)

#En el 02 , para que el robot tenga incitiva , sistema de recompensa , eleccion badasa en q-values , actualizacion de pesos

#primero se debe entender como el cerebro mide su propio error y modifica sus conexiones , no basta con que arroje q-values , necesitamos compenentes matematicos 

# ----> Loss funciton : calcula distancia matematica entre lo que la red penso que iba a pasar y lo que realmente ocurrio

# ----> Algortimo Adam : toma ese error y ajusta milimetricamente cada uno de los pesos internos de clas capas del cerebro

import os
import random
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn
import torch.optim as optim


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
        self.ancho = 8
        self.alto = 8
        
        #Posiciones iniciales 
        self.pos_robot = [0,0] #Empieza en la esquina superior derecha
        self.pos_meta = [7,7]
        
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
       # Guardamos la posición actual por si se necesita
        x_anterior, y_anterior = self.pos_robot
        
        #Modificar las coordenas segun la accion
        if accion == 0: #arriba
            self.pos_robot[1] -= 1
        elif accion == 1: #abajo
            self.pos_robot[1] += 1
        elif accion == 2: #izquierda
            self.pos_robot[0] -= 1
        elif accion == 3: #derechax|
            self.pos_robot[0] += 1
            
        #Frenar al robot su intenta salirse del tablero (paredes invisibles)
        #el min evita que te pases por la derecha del tablero (tope maximo : ancho - 1)
        #el max evita que te caigas por la izquierda (tope minimo : 0)
        self.pos_robot[0] = max(0, min(self.pos_robot[0], self.ancho -1 ))
        self.pos_robot[1] = max(0, min(self.pos_robot[1], self.alto -1 ))
        
        #Detectar si llego a la meta
        llego_a_meta = self.pos_robot == self.pos_meta
        
        #sistema de recoompensa
        #para que la inteligencia aprenda , necesita saber cuando esta haciendo las cosas bien o mal. Modificamos la funcion paso() para que entregue 3 puntajes numericos estrictos
         
        if llego_a_meta:
            #si el robot logra pisar la casilla de meta
            recompensa = 10.0
        elif self.pos_robot == [x_anterior, y_anterior]:
            recompensa = -1.0 #castigo por chocar contra la pared
        else :
            recompensa = -0.1 #castigo leve por paso
            
        
        #"obtener_estado()" , devuelve la lista de los 4 numeros deciamles
                #toma la foto de donde esta (despues de dar el primer paso) , devuelve 4 numeros los dos primeros son x,y del robot y los otros dos son x,y de la meta
                
         #llego_a_meta , duelve un indicador de verdad , si o no , respondiendo a la pregunta : ¿El robot acaba de pisar la misma casilla que la meta?    
        return self.obtener_estado(), recompensa, llego_a_meta
        
    
    
    
# El bucle de prueba 
if __name__ == "__main__":
    entorno = EntornoLaberinto()
    cerebro = RedNeuronalDQN()
    
    #Definimos el optimizador y la funcion de perdida antes de arrancar el bucle ( Herramientas de actulizacion de pesos)
    # la funcion MSELoss compara lo que el cerebro penso que iba a pasar contra la realidad de la recompensa, dando un numero exacto que mide su equivocacion
    criterio = nn.MSELoss()
    optimizer = optim.Adam(
        #lr es tasa de aprendizaje 
        #controlo que tan discreto o agresivo es el cerebro para poder modificar sus conexiones (los pesos de la red)
        # un lr con 0.1 , el cerebro cambia de opinion de forma tan violenta ante cualquier error que desconfigura todo lo que ya haboa aprendido
        # un lr con 0.001 aprende con cautela , ajustando sus neuronas paso a paso sin arruinar su progreso anterior 
        cerebro.parameters(), lr = 0.001
    )
    
    numero_episodios = 1000
    
    #Parametros de la curiosidad
    epsilon = 1.0 #100% de exploracion al inicio
    epsilon_decay = 0.98 #la curiosidad baja un 5% por cada episodio
    epsilon_min = 0.05 # un minimo de 5% de curiosidad permanente para que el robot nunca deje de tantear el mapa por completo
    
    #interrupto de aviso de que ya usa el cerebro
    cerebro_activado = False
    
    print("iniciando entrenamiento")
    
    #Ejecuta 100 partidas completas de forma automatica
    for episodio in range(numero_episodios):
        #cada vez que inicia un episodio , reiniciar(), manda al robot directo a la salida [0,0] , eliminando el problema de quedarse infinitamente en una esquina
        estado_actual = entorno.reiniciar()
        pasos_totales = 0
        llego_a_meta_en_episodio = False
        
        #cada episodio dura un maximo de 50 turnos para evitar bucles eternos
        for turno in range(75):
            pasos_totales += 1
            #Convertimos la lista de python en un tensor para el cerebro
            tensor_estado = torch.tensor(estado_actual, dtype=torch.float32)
            
            #Curiosidad
            #genera un numero decimal aleatorio entre 0.0 y 1.0 
            #epsilon representa el porcentaje de curiosidad , al inicio vale 1.0 (100%)
            
            #...si el numero al azar es menor que la curiosidad, el robot activa su modo curioso
            if random.random() < epsilon:
                #si se activo el modo curiosos , el robot ignora por completo su cerebro y eleige una direccion al azar entre 0,3 (arriba , abajo , etc) esto obliga explorar nuevos rincones
                accion_elegida = random.randint(0,3)
            #Si el numero aleatorio fue mayor a la curiosidad (conforme pasa el tiempo y epsilon baja), el robot decide apagar la curiosidad y usar su inteligencia acumulada
            else:
                #esta orden dice "Solo vamos a leer los números del cerebro para tomar una decisión, no calcules gradientes ni ajustes pesos en este microsegundo". Esto ahorra memoria y acelera el programa.
                with torch.no_grad():
                    #este robot le muestra la foto actual del mapa tensor a su red neuronal y el cerebro le regresa los 4 puntajes para cada direccion posible
                    q_valores = cerebro(tensor_estado)
                    #el robot revisa los cuatro puntajes que le dio el cerebro, busca el numero mas alto con argmax y extrae ese indice (.item()) para convenirle en la accion final que va a ejecutar
                    accion_elegida = torch.argmax(q_valores).item()
                
            #esta linea es el puente donde el agente intectua con el mundo fisico del laberinto
            
            #entorno.paso(accion_elegida) : es el metodo que mueve al robot , toma decisiones , verifica si choco y calcula que tan buneno o malo fue el mov
            
            #al terminar de procesar el movimiento , entrega los datos y los reparte
            
            #nuevo_estado : la fotografia actualizada del laberinto 
            #recompensa , el puntaje numero que evalua el resultado de ese paso , 10 meta , -1.0 choco , -0.1 mov normal
            #llego_a_meta , indicardor VERDAD O FALSO si acaba de caer en la casilla
            nuevo_estado, recompensa, llego_a_meta = entorno.paso(accion_elegida)
            
            #El cerebro emite sus 4 corazonadas (q-values)
            q_valores = cerebro(tensor_estado)
            
            #Actualizacion de los pesos 
            q_predicho = q_valores[accion_elegida]
            
            with torch.no_grad():
            #usamos la recompensa que entrego el entorno para calcular que tan bueno fue realmente ese usando bellman
                q_objetivo = q_predicho.clone()
                q_objetivo = recompensa + 0.9 * torch.max(cerebro(torch.tensor(nuevo_estado, dtype=torch.float32)))
            
            #Calculamos el error
            loss = criterio(q_predicho, q_objetivo)
                
            #limpiamos gradientes y actualizamos los pesos dell cerebro
            optimizer.zero_grad()
            loss.backward()
            #toma ese error , hace retropropagacion y ajusta los pesos y conexiones internas del cerebro para que la proxima vez el robot cometa menos erroes
            optimizer.step()
            
            
            if llego_a_meta:
                llegó_a_meta_en_episodio = True
                break
            
            estado_actual = nuevo_estado
        
        # --- REPORTE DE TELEMETRÍA PARA LOS PRIMEROS 5 EPISODIOS ---
        if (episodio + 1) <= 5 or llego_a_meta_en_episodio:
            with torch.no_grad():
                tensor_final = torch.tensor(entorno.obtener_estado(), dtype=torch.float32)                    
                q_actuales = cerebro(tensor_final)
                q_redondeados = [round(val.item(), 2) for val in q_actuales]
                
            estado_texto = "¡LLEGÓ A LA META!" if llego_a_meta_en_episodio else f"Posición final: {entorno.pos_robot}"
            print(f"[Episodio {episodio + 1}] {estado_texto} | Q-values: {q_redondeados} | Curiosidad: {epsilon:.2f}")
            
            # Reducción de la curiosidad al finalizar el episodio
        epsilon = max(epsilon_min, epsilon * epsilon_decay)
        
    #    # Reporte exacto de la posición final y sus Q-values cada 50 episodios
    #     if (episodio + 1) % 50 == 0:
    #         with torch.no_grad():
    #             # Obtenemos la foto del estado en el que terminó el robot
    #             tensor_final = torch.tensor(entorno.obtener_estado(), dtype=torch.float32)
    #             q_actuales = cerebro(tensor_final)
    #             q_redondeados = [round(val.item(), 2) for val in q_actuales]
            
    #         print(f"[Bloque {episodio + 1}] Posición final: {entorno.pos_robot} | Q-values {q_redondeados} | Curiosidad: {epsilon:.2f}")
        
    #     epsilon = max(epsilon_min, epsilon * epsilon_decay)
        
    print("ENTRENAMIENTO TERMINADO")

    print("\n--- PRUEBA EN FRÍO (Cerebro puro sin azar) ---")
    estado_actual = entorno.reiniciar()
    pasos_prueba = 0
    llego = False

    for _ in range(75):
        with torch.no_grad():
            tensor_estado = torch.tensor(estado_actual, dtype=torch.float32)
            q_valores = cerebro(tensor_estado)
            accion = torch.argmax(q_valores).item()
        
        nuevo_estado, recompensa, terminado = entorno.paso(accion)
        pasos_prueba += 1
        
        if terminado:
            llego = True
            break
        estado_actual = nuevo_estado

    if llego:
        print(f"¡El robot llegó a la meta usando solo su cerebro en {pasos_prueba} pasos!")
    else:
        print("El robot se quedó varado; la red todavía no memorizó la ruta perfecta.")