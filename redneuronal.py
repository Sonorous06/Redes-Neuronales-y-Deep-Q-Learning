import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import torch
import torch.nn as nn
import torch.optim as optim

#1. Definimos la estructura de la red neuronal

#Aquí estás creando tu propio modelo de red neuronal. Al poner (nn.Module) entre paréntesis, le dices a Python: "Esta clase no es cualquier clase de programación, es una red neuronal , Esto le otorga superpoderes automáticos, como la capacidad de guardar pesos, aprender y actualizarse sola.
class RedNeuronalDQN(nn.Module):
    #Aquí es donde declaras qué piezas va a tener tu red (cuántas capas, de qué tamaño, etc.).
    def __init__(self, dimension_entradas, dimension_acciones):
        #"Oye, inicializa la maquinaria interna de PyTorch para que pueda empezar a rastrear los pesos y sesgos de esta red
        super(RedNeuronalDQN, self).__init__()
        
        #----------------------------------------------------------------
        #Primera capa oculta : recibe las coordenadas y aplica pesos y sesgos iniciales
        #el 24 representa la cantidad de neuronas
        #recibe las 4 coordenadas crudas del tablero y hace una primera mezcla para dacar o24 ideas preliminares
        self.capa_entrada_oculta = nn.Linear(dimension_entradas, 24)
        
        #Segunda capa oculta : procesa mas a fondo las relaciones
        #toma esas 24 preliminares del primer supervisor , las vuelve a cruzar y entrega otras 24 conclusiones pero mas maduras        
        self.capa_oculta_intermedia = nn.Linear(24,24)
        
        #Capa de salida : escupe un valor numero (VALOR : Q) para cada accion posinle
        #recibe los 24 datos refinados que salieron
        # "dimension_acciones" , significa cauntos datos va a escupir hacia afuera
        #Como definimos que nuestro robot tiene 4 acciones posibles (Arriba, Abajo, Izquierda, Derecha), ese parámetro vale 4.
        #Por lo tanto, esta última línea crea una capa lineal que toma esos 24 conceptos internos y los convierte exactamente en 4 números finales.
        
        ##Qué significan esos 4 números que salen?
        #Son las famosas predicciones de los Valores Q para cada dirección:
        #El número 1 representa qué tan bueno cree la red que es ir Arriba.
        #El número 2 representa ir Abajo.
        #El número 3 representa ir a la Izquierda.
        #El número 4 representa ir a la Derecha.
        self.capa_salifa_vectores_q = nn.Linear(24, dimension_acciones)
        
        #Entrada (4 coordenadas): Dónde están el robot y la meta.

        #Capa oculta 1 y 2 (24 y 24): El "cerebro" procesando y cruzando relaciones espaciales.

        #Salida (4 valores Q): Las calificaciones o "corazonadas" para cada botón del control de nuestro robot.
        #----------------------------------------------------------------
        
    #forward define como viajan los datos a traves de esas piezas cuando la red recibe la info
    def forward(self, vector_estado_actual):
        
        #Funcion de activacion : filtra y descarta valores negativos (simula neuronas activadas/apagadas)
        
        #"Toma el vector con las coordenadas actuales (vector_estado_actual), pásalo por la primera capa de la red (self.capa_entrada_oculta —donde se multiplica por los pesos y se le suman los sesgos), y al resultado pásale el filtro torch.relu para apagar los números negativos y guardar el resultado limpio en activacion_capa_1".
        activacion_capa_1 = torch.relu(self.capa_entrada_oculta(vector_estado_actual))
        #segunda pasada
        activacion_capa_2 = torch.relu(self.capa_oculta_intermedia(activacion_capa_1))
        
        #retorna las predicciones brutas de los valores q para todas las acciones
        #llegan los 24 numeros limpios y refinados que salieron del segundo supervisor (la capa intermedia)
        #esos datos se multiplican por el ultimo juego de pesos de cada salida nn.Linear(24, dimension_acciones)
        #Porque los valores Q (las calificaciones de qué tan bueno es ir arriba, abajo, izquierda o derecha) pueden ser negativos o positivos. Si aplicáramos ReLU aquí, borraríamos los números negativos y arruinaríamos las calificaciones del robot
        
        vector_valores_q = self.capa_salifa_vectores_q(activacion_capa_2)
        
        #Toma estos 4 números calculados y devuélveselos al programa principal".
        return vector_valores_q
    
#2. Iniciamos nuestro modelo

#Aqui mandamos a fabricar la red neural usando nuestros planos, le decimos tendras 4 entradas(las coordenadas) y 4 salidas (las acciones posibles) , en este momento pythorch genera todos los pesos y sesgos de manera aleatoria
# Entradas (4): [posicion_robot_x, posicion_robot_y, posicion_meta_x, posicion_meta_y]
# Salidas (4): Valores Q estimados para [Arriba, Abajo, Izquierda, Derecha]
modelo_dqn = RedNeuronalDQN(dimension_entradas=4 , dimension_acciones=4)

#3. Simulamos un estado actual del tablero

# Aca creamos la fotografia numerica del mundo , ponemos al robot en la celda de origen y la meta en la posicion , todo se empaqueta en un tensor de pytoch , pq es el formato que las capas matematicas de la red sabeen leer y multiplicar
#El robot esta en la celda (0,0) y le meta se encuentra en (2,1)
estado_robot_y_meta = torch.tensor([[0.0, 0.0, 2.0, 1.0]], dtype=torch.float32)

#4. La red neuronal adivina los valores Q actuales (sus pesos aun son al azar)

#le pasamos el estado del tablero al modelo modelo_dqn(estado_robot_y_meta) y los datos cruzan las capas ocultas multiplicandose por los pesos y la red escupe 4 numeros crudos (los valores Q estimados para cada dirección).

prediccion_valores_q = modelo_dqn(estado_robot_y_meta)

#------------------------------------------------------------#
#estas lineas son mera informacion , sirve para ver entro al sistema y que calificicones arrojo a la red antes ese estimulo
print("--------------------------------------------------")
print("Estado de entrada [Robot X, Robot Y, Meta X, Meta Y]:", estado_robot_y_meta.tolist())
print("Valores Q predichos por la red (sin entrenar):", prediccion_valores_q)
#------------------------------------------------------------#

#------------------------------------------------------------#
# Seleccionamos el índice de la acción que obtuvo el número más alto
#torch.argmax(prediccion_valores_q).item() , esta funcion busca enrte los 4 numeros de salida el numero mas alto y extrae su posicion , Si el número más grande estaba en la segunda posición, argmax regresa un 1. El .item() simplemente saca el número limpio del tensor de PyTorch para que Python lo pueda leer como un entero normal.
indice_accion_optima = torch.argmax(prediccion_valores_q).item()

#como la red no entiende la palabras , creamos el diccionario de traduccion
mapeo_acciones = {0: "Arriba", 1: "Abajo", 2: "Izquierda", 3: "Derecha"}

print("Acción elegida por la red:", mapeo_acciones[indice_accion_optima], f"(Índice: {indice_accion_optima})")
print("--------------------------------------------------")
#------------------------------------------------------------#
