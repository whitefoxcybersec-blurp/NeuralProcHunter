# NeuralProcHunter 🧠🛡️

Um ecossistema modular de IA preditiva e detecção heurística de anomalias em tempo real para sistemas Linux (homologado em Debian 13), construído **100% em Python puro**, sem dependências externas, bibliotecas de terceiros (como TensorFlow ou PyTorch) ou APIs.

O projeto utiliza **Redes Neurais Artificiais Feedforward (Multilayer Perceptron)** criadas e matematicamente deduzidas do zero para analisar o comportamento do sistema direto nas fontes nativas do Kernel Linux.

---

## 🚀 Módulos do Ecossistema

O sistema é dividido em 4 motores independentes de caça a ameaças (Threat Hunting). Atualmente, as seguintes fases estão operacionais:

### 1/4: Local Process Audit IA
Monitora os processos em tempo real diretamente através do sistema de arquivos virtual `/proc`.
* **Heurística de Entrada:** Analisa privilégios de execução (UID 0) e caminhos de binários suspeitos baseados em diretórios temporários de escrita livre (`/tmp`, `/dev/shm`, `/var/tmp`).
* **Objetivo:** Detectar a execução de payloads de persistência e escalada de privilégios.

### 2/4: Network Hunter IA 🌐 *(Novo)*
Um motor baseado em **Threading de alta velocidade** que monitora sockets ativos, portas abertas e o estado das conexões de rede do sistema.
* **Heurística de Entrada:** Avalia o estado dos sockets (`LISTEN`, `ESTABLISHED`), portas altas dinâmicas e o escopo de vinculação (`0.0.0.0` vs `127.0.0.1`).
* **Objetivo:** Identificar comportamentos anômalos que simulam **Reverse Shells**, backdoors ativos e conexões persistentes de Command & Control (C2), isolando comportamentos legítimos de tráfego pesado (como navegadores e streams P2P).

---

## 🧠 A Arquitetura das Redes

Cada módulo possui seu próprio cérebro matemático isolado, ajustado para as variáveis específicas de seu vetor de ataque:

* **Camada Oculta:** Neurônios baseados na função de ativação **Sigmóide** para processamento e mapeamento não-linear de comportamentos.
* **Camada de Saída:** 1 neurônio gerando um **Score IA** preditivo contínuo entre `0.0` e `1.0`.
* **Algoritmo de Aprendizado:** Backpropagation nativo via Gradiente Descendente.

---

## 🛠️ Requisitos

* **Sistema Operacional:** Linux (Desenvolvido e homologado no Debian 13).
* **Linguagem:** Python 3.x (Utilizando estritamente as bibliotecas nativas: `os`, `sys`, `math`, `random`, `threading`).
* **Permissões:** Acesso de superusuário (`sudo`) para leitura completa dos metadados de rede e processos de outros contextos de usuário.

---

## 💻 Como Executar

### Executando o Auditor de Processos (Módulo 1/4)
```bash
sudo python3 auditor_ia.py

```

### Executando o Caçador de Redes (Módulo 2/4)

```bash
python3 network_hunter_ia.py

```

---

## 📊 Exemplo de Saída do Motor de Rede (2/4)

O motor analisa o comportamento bruto dos descritores de arquivo de rede e exibe o nível de ameaça calculado pela heurística da IA:

```text
[*] Treinando o cérebro da IA 2/4 (Network Hunting)...
[+] IA 2/4 Pronta para o combate.

[*] Motores de Threading ativados. Monitorando sockets do Debian 13...
PID     | CONEXÃO LOCAL          | ESTADO      | SCORE IA  | PROCESSO / COMANDO
------------------------------------------------------------------------------------------
6996    | 0.0.0.0:46203          | LISTEN      | 0.9501    | /usr/share/spotify/spotify
4123    | 127.0.0.1:6463         | LISTEN      | 0.9501    | /proc/self/exe --type=renderer
7034    | 192.168.1.104:60974    | ESTABLISHED | 0.5999    | /usr/share/spotify/spotify --type=u
3549    | 192.168.1.104:57946    | ESTABLISHED | 0.9501    | /opt/google/chrome/chrome --type=ut

```

> ⚠️ **Nota de Análise Heurística:** Processos legítimos que utilizam conexões peer-to-peer (P2P) ou abrem portas dinâmicas altas para escuta (ex: Spotify, instâncias de renderização do Chrome) receberão scores elevados devido à natureza de seus sockets espelharem o comportamento padrão de backdoors e canais de exfiltração.

```

