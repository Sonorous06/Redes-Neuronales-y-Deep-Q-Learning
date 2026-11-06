# Redes-Neuronales-y-Deep-Q-Learning
# Bitácora de Aprendizaje: De las Bases de la IA a Redes Neuronales y Deep Q-Learning

Este repositorio documenta el viaje de estudio autodidacta enfocado en comprender los cimientos de la Inteligencia Artificial, transitando desde la lógica simbólica y la recursividad hasta arquitecturas avanzadas de aprendizaje profundo y sistemas multi-agente.

## Evolución del Trayecto de Aprendizaje

1. **Lógica Simbólica y Búsqueda (Prolog):**
   - Introducción a la representación del conocimiento mediante hechos y reglas.
   - Comprensión del motor de inferencia y la estrategia de búsqueda con retroceso (**Backtracking**).

2. **Recursividad y Estructuras Matemáticas:**
   - Análisis de funciones recursivas (Factorial, Potencias, Máximo Común Divisor y la lógica de la Torre de Hanoi) como motores lógicos y matemáticos aplicados a la resolución de problemas algorítmicos.

3. **Perceptrón y Redes Neuronales Básicas:**
   - Comprensión de los componentes microscópicos de una red: **Pesos ($w$)** (importancia de las entradas) y **Sesgos ($b$)** (umbrales de activación).
   - Ajuste de parámetros mediante cálculo de errores y tasas de aprendizaje ($\alpha$) aplicados a compuertas lógicas (AND) y modelos de clasificación.

4. **Aprendizaje por Refuerzo y Deep Q-Learning (DQN):**
   - Implementación de un agente autónomo resolviendo un laberinto mediante prueba y error guiado por la **Ecuación de Bellman**.
   - Integración de los dos pilares fundamentales de estabilidad en redes profundas:
     - **Experience Replay (Caja de Recuerdos):** Rompe la correlación temporal entrenando con lotes de vivencias revueltas (`batch size`).
     - **Target Network (Cuaderno Congelado):** Detiene el problema del "blanco móvil" para estabilizar los cálculos matemáticos.

5. **Sistemas Multi-Agente (MARL - Zero-Sum):**
   - Escalado del entorno a un escenario competitivo de dos agentes compartiendo el mismo tablero.
   - Enfoque en el reto de la **no-estacionariedad**, donde el entorno cambia dinámicamente debido a que los rivales adaptan y mejoran sus estrategias de manera simultánea.
