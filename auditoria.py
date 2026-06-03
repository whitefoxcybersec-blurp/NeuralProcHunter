import os
import math
import random


# =====================================================================
# 1. MOTOR DA REDE NEURAL (MATEMÁTICA PURA)
# =====================================================================

def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


# Dataset de Treinamento Teórico:
# Entradas: [É Root? (0=Não, 1=Sim), Tá em pasta temporária? (0=Não, 1=Sim)]
# Saídas:   [Nível de Alerta (0=Seguro, 1=Altamente Suspeito)]
inputs_treino = [
    [0, 0],  # Usuário comum, pasta padrão (/usr/bin) -> SEGURO (0)
    [1, 0],  # Root, pasta padrão (/usr/sbin)         -> SEGURO (0)
    [0, 1],  # Usuário comum, pasta temporária (/tmp)  -> SUSPEITO (0.5)
    [1, 1]  # Root, pasta temporária (/tmp)           -> CRÍTICO (1)
]
outputs_treino = [[0.0], [0.1], [0.6], [1.0]]

# Inicialização de Pesos e Biases
random.seed(1337)
weights_input_hidden = [[random.uniform(-1, 1) for _ in range(3)] for _ in range(2)]
bias_hidden = [random.uniform(-1, 1) for _ in range(3)]
weights_hidden_output = [[random.uniform(-1, 1) for _ in range(1)] for _ in range(3)]
bias_output = [random.uniform(-1, 1) for _ in range(1)]

learning_rate = 0.5
epochs = 15000

print("[*] Treinando o cérebro da IA local para auditoria...")
for epoch in range(epochs):
    for i in range(len(inputs_treino)):
        # Forward pass
        hidden_inputs = [bias_hidden[h] + sum(inputs_treino[i][inp] * weights_input_hidden[inp][h] for inp in range(2))
                         for h in range(3)]
        hidden_outputs = [sigmoid(x) for x in hidden_inputs]

        output_input = bias_output[0] + sum(hidden_outputs[h] * weights_hidden_output[h][0] for h in range(3))
        final_output = sigmoid(output_input)

        # Backpropagation
        error = outputs_treino[i][0] - final_output
        delta_output = error * sigmoid_derivative(final_output)

        delta_hidden = [0.0, 0.0, 0.0]
        for h in range(3):
            error_hidden = delta_output * weights_hidden_output[h][0]
            delta_hidden[h] = error_hidden * sigmoid_derivative(hidden_outputs[h])

        # Atualização dos pesos
        for h in range(3):
            weights_hidden_output[h][0] += learning_rate * delta_output * hidden_outputs[h]
        bias_output[0] += learning_rate * delta_output

        for inp in range(2):
            for h in range(3):
                weights_input_hidden[inp][h] += learning_rate * delta_hidden[h] * inputs_treino[inp]
            bias_hidden[h] += learning_rate * delta_hidden[h]

print("[+] IA treinada com sucesso!\n")

# =====================================================================
# 2. COLETA DE DADOS EM TEMPO REAL (SISTEMA OPERACIONAL DEBIAN)
# =====================================================================

print(f"{'PID':<8} | {'DONO':<6} | {'PASTA SUSPEITA?':<15} | {'SCORE IA':<10} | {'COMANDO'}")
print("-" * 80)

# Pastas comumente usadas em táticas de evasão/persistência
pastas_perigosas = ["/tmp", "/dev/shm", "/var/tmp", "/run/user"]

# Varre o diretório /proc
for pid_dir in os.listdir("/proc"):
    if pid_dir.isdigit():  # Filtra apenas pastas que são PIDs
        pid = pid_dir
        path_proc = f"/proc/{pid}"

        try:
            # 1. Descobrir se é Root (Lendo /proc/[PID]/status)
            is_root = 0
            with open(f"{path_proc}/status", "r") as f:
                for line in f:
                    if line.startswith("Uid:"):
                        # O primeiro número é o Real UID. 0 significa root.
                        uid = line.split()[1]
                        if uid == "0":
                            is_root = 1
                        break

            # 2. Descobrir o caminho do executável (Lendo o link simbólico /proc/[PID]/exe)
            exe_path = os.readlink(f"{path_proc}/exe")

            is_suspicious_path = 0
            for pasta in pastas_perigosas:
                if exe_path.startswith(pasta):
                    is_suspicious_path = 1
                    break

            # 3. Ler a linha de comando executada para exibir no relatório
            with open(f"{path_proc}/cmdline", "r") as f:
                cmd = f.read().replace("\x00", " ").strip()
            if not cmd:
                cmd = exe_path  # Se cmdline estiver vazio, usa o caminho do executável

            # =====================================================================
            # 3. VEREDITO DA IA
            # =====================================================================
            # Passa os dados coletados do Debian pela nossa rede treinada
            hidden_inputs = [bias_hidden[h] + (is_root * weights_input_hidden[0][h]) + (
                        is_suspicious_path * weights_input_hidden[1][h]) for h in range(3)]
            hidden_outputs = [sigmoid(x) for x in hidden_inputs]

            output_input = bias_output[0] + sum(hidden_outputs[h] * weights_hidden_output[h][0] for h in range(3))
            score_ia = sigmoid(output_input)

            # Filtragem para o relatório: Mostrar tudo, mas destacar os scores altos
            dono = "root" if is_root == 1 else "user"
            pasta_status = "SIM" if is_suspicious_path == 1 else "Nao"

            # Só exibe se o score passar de um limite mínimo para não inundar a tela,
            # ou se você quiser ver o comportamento, ajuste o filtro.
            if score_ia > 0.1 or is_suspicious_path == 1:
                print(f"{pid:<8} | {dono:<6} | {pasta_status:<15} | {score_ia:.4f}   | {cmd[:40]}")

        except (FileNotFoundError, ProcessLookupError, PermissionError):
            # Processos que sumiram no meio do caminho ou restrições de permissão do kernel
            continue