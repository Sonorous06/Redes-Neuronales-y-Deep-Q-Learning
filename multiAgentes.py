#ENTORNO DEL LABERINTO COMPARTIDIO -------------
import random
import numpy as np

class LaberintoCompetitivo:
    def __init__(self):
        self.ancho = 8
        self.alto = 8
        self.pos_meta = [7,7]
        self.trampas = [[0,5],[0,5],[4,7],[7,3],[3,3]]
        
    def reiniciar(self):
        #posiciones iniciales aleatorias  y separadas por ambos robots
        self.pos_a = [random.randint(0,2), random.randint(0,2)]
        self.pos_b = [random.randint(5,7), random.randint(5,7)]
        
        #nos aseguramos que no nazcan en la meta ni en las trampas
        while self.pos_a == self.pos_meta or self.pos_a in self.trampas:
            self.pos_a = [random.randint(0,2), random.randint(0,2)]
        while self.pos_b == self.pos_meta or self.pos_b in self.trampas or self.pos_b == self.pos_a:
            self.pos_b = [random.randint(5,7), random.randint(5,7)]
        
        