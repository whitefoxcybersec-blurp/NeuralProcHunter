import os
import math
import random
import threading
import time


# =====================================================================
# 1. MOTOR MATEMÁTICO DA IA (REDE NEURAL)
# =====================================================================
def sigmoid(x):
    return 1 / (1 + math.exp(-x))


def sigmoid_derivative(x):
    return x * (1 - x)


# Dataset focado em Redes:
# Entradas: [Binário Legítimo? (0=Não, 1=Sim), Estado Crítico ESTABLISHED/LISTEN? (0=Não, 1=Sim), Porta Suspeita? (0=Não, 1=Sim)]
# Saídas:   [Score de Risco]
inputs_treino = [
    [1, 1, 0],  # Ex: sshd ou nginx em portas padrão -> SEGURO (0.05)
    [1, 0, 0],  # Ex: curl legítimo conectando fora -> SEGURO (0.1)
    [0, 1, 1],  # Ex: Binário estranho escutando porta alta -> BACKDOOR (0.95)
    [0, 1, 0],  # Ex: Script python conectado para fora -> SUSPEITO (0.6)
]
outputs_treino = [[0.05], [0.10], [0.95], [0.60]]

# Inicialização de Pesos e Biases (3 entradas -> 4 neurônios ocultos -> 1 saída)
random.seed(2444)
weights_in_hidden = [[random.uniform(-1, 1) for _ in range(4)] for _ in range(3)]
bias_hidden = [random.uniform(-1, 1) for _ in range(4)]
weights_hidden_out = [[random.uniform(-1, 1) for _ in range(1)] for _ in range(4)]
bias_output = [random.uniform(-1, 1) for _ in range(1)]

print("[*] Treinando o cérebro da IA 2/4 (Network Hunting)...")
for epoch in range(15000):
    for i in range(len(inputs_treino)):
        # Forward pass
        hidden_out = [
            sigmoid(bias_hidden[h] + sum(inputs_treino[i][inp] * weights_in_hidden[inp][h] for inp in range(3))) for h
            in range(4)]
        final_out = sigmoid(bias_output[0] + sum(hidden_out[h] * weights_hidden_out[h][0] for h in range(4)))

        # Backpropagation
        error = outputs_treino[i][0] - final_out
        delta_out = error * sigmoid_derivative(final_out)

        delta_hidden = [delta_out * weights_hidden_out[h][0] * sigmoid_derivative(hidden_out[h]) for h in range(4)]

        # Ajuste de Pesos
        for h in range(4):
            weights_hidden_out[h][0] += 0.5 * delta_out * hidden_out[h]
        bias_output[0] += 0.5 * delta_out

        for inp in range(3):
            for h in range(4):
                weights_in_hidden[inp][h] += 0.5 * delta_hidden[h] * inputs_treino[i][inp]
            bias_hidden[h] += 0.5 * delta_hidden[h]

print("[+] IA 2/4 Pronta para o combate.\n")

# =====================================================================
# 2. MOTOR DE PARSING PARALELO (THREADING & HEX PARSER)
# =====================================================================

# Lista compartilhada de sockets ativos capturados pelas threads
sockets_capturados = []
lock = threading.Lock()


def decodificar_ip_porta(hex_str):
    """Converte o formato de rede Hex do Kernel Linux para IP e Porta amigáveis."""
    try:
        hex_ip, hex_port = hex_str.split(':')
        # Inversão Little-Endian para IPs do Kernel
        ip_bytes = [int(hex_ip[i:i + 2], 16) for i in range(0, 8, 2)]
        ip_dec = f"{ip_bytes[3]}.{ip_bytes[2]}.{ip_bytes[1]}.{ip_bytes[0]}"
        port_dec = int(hex_port, 16)
        return ip_dec, port_dec
    except Exception:
        return "0.0.0.0", 0


def thread_parse_net():
    """Thread dedicada a quebrar o /proc/net/tcp em tempo real."""
    global sockets_capturados
    estados_validos = {"01": "ESTABLISHED", "0A": "LISTEN"}

    while True:
        novos_sockets = []
        try:
            with open("/proc/net/tcp", "r") as f:
                lines = f.readlines()[1:]  # Pula o cabeçalho
                for line in lines:
                    parts = line.split()
                    state_hex = parts[3]
                    if state_hex in estados_validos:
                        ip_local, porta_local = decodificar_ip_porta(parts[1])
                        ip_remoto, porta_remota = decodificar_ip_porta(parts[2])
                        inode = parts[9]

                        novos_sockets.append({
                            "local": f"{ip_local}:{porta_local}",
                            "remoto": f"{ip_remoto}:{porta_remota}",
                            "estado": estados_validos[state_hex],
                            "porta_num": porta_local if estados_validos[state_hex] == "LISTEN" else porta_remota,
                            "inode": inode,
                            "pid": None,
                            "cmd": "Desconhecido"
                        })
            with lock:
                sockets_capturados = novos_sockets
        except Exception as e:
            pass
        time.sleep(1)  # Executa o ciclo a cada 1 segundo


def thread_map_processos():
    """Thread dedicada a caçar quais PIDs são donos dos inodes de rede."""
    global sockets_capturados
    binarios_legitimos = ["sshd", "nginx", "apache2", "systemd", "dhclient", "chrome", "firefox", "curl", "wget"]

    while True:
        with lock:
            sockets_atuais = list(sockets_capturados)

        if not sockets_atuais:
            time.sleep(0.5)
            continue

        # Cria um mapa de inodes para busca rápida
        mapa_inodes = {s["inode"]: i for i, s in enumerate(sockets_atuais)}

        # Varre os PIDs no /proc
        for pid_dir in os.listdir("/proc"):
            if pid_dir.isdigit():
                path_fd = f"/proc/{pid_dir}/fd"
                try:
                    # Varre os descritores de arquivos abertos pelo processo
                    for fd in os.listdir(path_fd):
                        link = os.readlink(f"{path_fd}/{fd}")
                        if link.startswith("socket:["):
                            inode_extraido = link.split("[")[1].split("]")[0]

                            if inode_extraido in mapa_inodes:
                                idx = mapa_inodes[inode_extraido]
                                sockets_atuais[idx]["pid"] = pid_dir

                                # Pega o nome real do executável
                                try:
                                    with open(f"/proc/{pid_dir}/cmdline", "r") as f:
                                        cmd = f.read().replace("\x00", " ").strip()
                                        sockets_atuais[idx]["cmd"] = cmd if cmd else "Processo Oculto"
                                except:
                                    pass
                except (PermissionError, FileNotFoundError):
                    continue

        # Atualiza a lista global com os PIDs mapeados
        with lock:
            sockets_capturados = sockets_atuais
        time.sleep(1)


# =====================================================================
## =====================================================================
# 3. INTERFACE E ORQUESTRAÇÃO CENTRAL (INFERÊNCIA DA IA REFINADA)
# =====================================================================

# Dispara os motores paralelos
t1 = threading.Thread(target=thread_parse_net, daemon=True)
t2 = threading.Thread(target=thread_map_processos, daemon=True)
t1.start()
t2.start()

print("[*] Motores de Threading ativados. Monitorando sockets do Debian 13...")
print(f"{'PID':<7} | {'CONEXÃO LOCAL':<22} | {'ESTADO':<11} | {'SCORE IA':<9} | {'PROCESSO / COMANDO'}")
print("-" * 90)

# Lista expandida e normalizada (letras minúsculas)
binarios_rede_comuns = ["sshd", "nginx", "apache", "systemd", "chrome", "firefox", "curl", "wget", "discord", "spotify", "slack", "code"]
portas_comuns = [22, 80, 443, 53, 68, 123, 8080, 9050]

# Dicionário para rastrear o que já foi exibido (evita flooding no terminal)
historico_alertas = {}

try:
    while True:
        with lock:
            copia_sockets = list(sockets_capturados)

        for sock in copia_sockets:
            if sock["pid"] is None:
                continue

            cmd_formatado = sock["cmd"].lower()

            # --- Extração de Features Corrigida ---
            # 1. Validação robusta de binário legítimo
            is_legit = 1 if any(b in cmd_formatado for b in binarios_rede_comuns) else 0

            # 2. Estado Crítico
            is_critical_state = 1 if sock["estado"] in ["LISTEN", "ESTABLISHED"] else 0

            # 3. Porta incomum
            is_suspicious_port = 0 if sock["porta_num"] in portas_comuns else 1

            # --- Inferência do Neurônio ---
            risco_binario = 1 - is_legit
            inputs_ia = [risco_binario, is_critical_state, is_suspicious_port]

            hidden_out = [sigmoid(bias_hidden[h] + sum(inputs_ia[inp] * weights_in_hidden[inp][h] for inp in range(3))) for h in range(4)]
            score_ia = sigmoid(bias_output[0] + sum(hidden_out[h] * weights_hidden_out[h][0] for h in range(4)))

            # --- Mecanismo Anti-Spam (Filtro Dinâmico) ---
            # Identificador único baseado no PID e na Conexão Local
            id_conexao = f"{sock['pid']}_{sock['local']}_{sock['estado']}"

            # Limiar de Alerta: Filtra ruídos muito baixos
            if score_ia > 0.45:
                # Só exibe se for uma nova conexão ou se o score flutuar muito
                if id_conexao not in historico_alertas or abs(historico_alertas[id_conexao] - score_ia) > 0.05:
                    print(f"{sock['pid']:<7} | {sock['local']:<22} | {sock['estado']:<11} | {score_ia:.4f}   | {sock['cmd'][:35]}")
                    historico_alertas[id_conexao] = score_ia

        # Limpa conexões antigas do histórico para não estagnar a memória do script
        if len(historico_alertas) > 500:
            historico_alertas.clear()

        time.sleep(2)
except KeyboardInterrupt:
    print("\n[-] Auditoria encerrada pelo operador.")