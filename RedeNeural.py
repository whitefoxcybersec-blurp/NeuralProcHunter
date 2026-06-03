import math
import random


# --- Funções Matemáticas de Ativação ---
def sigmoid(x):
    """Função de ativação que comprime o valor entre 0 e 1."""
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative(x):
    """Derivada da sigmoid, usada no backpropagation para calcular o gradiente."""
    return x * (1 - x)


# --- Configuração da Rede Neural ---
random.seed(42)  # Para resultados reproduzíveis

# Dataset do XOR
# Entradas: [A, B] | Saídas Esperadas: [A XOR B]
inputs = [[0, 0], [0, 1], [1, 0], [1, 1]]
outputs = [[0], [1], [1], [0]]

# Inicialização de Pesos e Biases (Valores aleatórios entre -1 e 1)
# Camada de Entrada -> Camada Oculta (2 entradas -> 3 neurônios ocultos)
weights_input_hidden = [[random.uniform(-1, 1) for _ in range(3)] for _ in range(2)]
bias_hidden = [random.uniform(-1, 1) for _ in range(3)]

# Camada Oculta -> Camada de Saída (3 neurônios ocultos -> 1 neurônio de saída)
weights_hidden_output = [[random.uniform(-1, 1) for _ in range(1)] for _ in range(3)]
bias_output = [random.uniform(-1, 1) for _ in range(1)]

# Hiperparâmetros
learning_rate = 0.5
epochs = 20000

print("Treinando a rede neural...")

# --- Loop de Treinamento ---
for epoch in range(epochs):
    for i in range(len(inputs)):
        # 1. FORWARD PROPAGATION (Passada para frente)

        # Entrada -> Oculta
        hidden_layer_input = [0.0, 0.0, 0.0]
        for h in range(3):
            activation = bias_hidden[h]
            for inp in range(2):
                activation += inputs[i][inp] * weights_input_hidden[inp][h]
            hidden_layer_input[h] = sigmoid(activation)

        # Oculta -> Saída
        output_layer_input = [0.0]
        for o in range(1):
            activation = bias_output[o]
            for h in range(3):
                activation += hidden_layer_input[h] * weights_hidden_output[h][o]
            output_layer_input[o] = sigmoid(activation)

        # 2. BACKPROPAGATION (Ajuste dos pesos via Gradiente Descendente)

        # Calcular o erro na saída
        error_output = outputs[i][0] - output_layer_input[0]
        delta_output = error_output * sigmoid_derivative(output_layer_input[0])

        # Calcular o erro na camada oculta
        delta_hidden = [0.0, 0.0, 0.0]
        for h in range(3):
            error_hidden = delta_output * weights_hidden_output[h][0]
            delta_hidden[h] = error_hidden * sigmoid_derivative(hidden_layer_input[h])

        # Atualizar pesos e biases da camada Oculta -> Saída
        for h in range(3):
            weights_hidden_output[h][0] += learning_rate * delta_output * hidden_layer_input[h]
        bias_output[0] += learning_rate * delta_output

        # Atualizar pesos e biases da camada Entrada -> Oculta
        for inp in range(2):
            for h in range(3):
                weights_input_hidden[inp][h] += learning_rate * delta_hidden[h] * inputs[i][inp]
            bias_hidden[h] += learning_rate * delta_hidden[h]

print("Treinamento concluído!\n")

# --- Testando a IA ---
print("Resultados dos testes:")
for i in range(len(inputs)):
    # Forward pass final para teste
    hidden_layer_input = [0.0, 0.0, 0.0]
    for h in range(3):
        activation = bias_hidden[h]
        for inp in range(2):
            activation += inputs[i][inp] * weights_input_hidden[inp][h]
        hidden_layer_input[h] = sigmoid(activation)

    output_layer_input = [0.0]
    activation = bias_output[0]
    for h in range(3):
        activation += hidden_layer_input[h] * weights_hidden_output[h][0]
    output_layer_input[0] = sigmoid(activation)

    print(
        f"Entrada: {inputs[i]} -> Saída Esperada: {outputs[i][0]} -> Predição da IA: {output_layer_input[0]:.4f} (Arredondado: {round(output_layer_input[0])})")