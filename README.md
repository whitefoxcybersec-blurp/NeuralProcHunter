# Local Process Audit IA 🧠🛡️

Um detector heurístico de anomalias e processos suspeitos para sistemas Linux (homologado em Debian 13), construído **100% em Python puro**, sem dependências externas, bibliotecas de terceiros (como TensorFlow ou PyTorch) ou APIs de terceiros.

O projeto utiliza uma **Rede Neural Artificial Feedforward (Multilayer Perceptron)** criada do zero para analisar o comportamento de processos em execução direto no sistema de arquivos virtual `/proc` do Kernel Linux.

## 🚀 Como Funciona

A IA monitora os processos em tempo real e calcula um **Score de Ameaça** com base em indicadores de comprometimento (IoCs) clássicos:
1. **Privilégios do Processo:** Se o binário está rodando com privilégios de `root` (UID 0).
2. **Origem do Executável:** Se o binário está sendo executado a partir de diretórios temporários de escrita livre (`/tmp`, `/dev/shm`, `/var/tmp`), comportamento padrão de vetores de ataque e persistência.

### A Arquitetura da Rede
* **Camada de Entrada:** 2 neurônios (Mapeamento de privilégio e caminho suspeito).
* **Camada Oculta:** 3 neurônios com função de ativação **Sigmóide** para processamento não-linear.
* **Camada de Saída:** 1 neurônio (Score preditivo entre `0.0` e `1.0`).
* **Algoritmo de Aprendizado:** Backpropagation via Gradiente Descendente.

---

## 🛠️ Requisitos

* **Sistema Operacional:** Linux (Desenvolvido e testado no Debian 13).
* **Linguagem:** Python 3.x (Apenas bibliotecas nativas `os`, `math` e `random`).
* **Permissões:** Acesso de superusuário (`sudo`) para leitura completa dos metadados de processos de outros usuários no `/proc`.

---

## 💻 Como Executar

1. Clone ou salve o script `auditor_ia.py` na sua máquina.
2. Execute o auditor com privilégios administrativos:

```bash
sudo python3 auditor_ia.py
