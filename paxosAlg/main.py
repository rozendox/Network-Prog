# main.py

from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
from network import Network
from node import Node
from typing import List
import time


def main():
    # --- Configuração ---
    ACCEPTOR_IDS = {"A1", "A2", "A3", "A4", "A5"}
    LEARNER_IDS = {"L1", "L2"}
    PROPOSER_IDS = {"P1", "P2"}

    # --- Instanciação dos Nós ---

    # Acceptors e Learners precisam da lista de Learners/Acceptors para comunicação
    acceptors: Dict[str, Acceptor] = {
        id: Acceptor(id, LEARNER_IDS) for id in ACCEPTOR_IDS
    }
    learners: Dict[str, Learner] = {
        id: Learner(id, ACCEPTOR_IDS) for id in LEARNER_IDS
    }

    # Proposers precisam da lista de Acceptors e um valor inicial
    proposer_1 = Proposer("P1", ACCEPTOR_IDS, initial_value="Valor_Original_P1")
    proposer_2 = Proposer("P2", ACCEPTOR_IDS, initial_value="Valor_Concorrente_P2")

    all_nodes: List[Node] = list(acceptors.values()) + list(learners.values()) + [proposer_1, proposer_2]

    print("--- ⚙️ SISTEMA PAZOS INICIALIZADO ⚙️ ---")
    print(f"Total de Acceptors: {len(ACCEPTOR_IDS)}. Quorum necessário: {(len(ACCEPTOR_IDS) // 2) + 1}")

    # --- Simulação do Fluxo ---

    # Passo 1: P1 inicia a primeira proposta
    proposer_1.start_proposal()

    # Simula a passagem do tempo e o processamento de mensagens
    for i in range(1, 4):
        print(f"\n\n--- 🔄 CICLO DE REDE {i} ---")

        # Cada nó processa as mensagens destinadas a ele
        for node in all_nodes:
            node.process_messages()

        # O P2 tenta concorrer a partir do ciclo 2
        if i == 2:
            proposer_2.start_proposal()

        # Parar se o consenso for alcançado
        if any(learner.is_learned for learner in learners.values()):
            print("\n--- ✅ Consenso Alcançado. Encerrando Simulação. ---")
            break

        time.sleep(0.5)  # Pequeno atraso para visualização


if __name__ == "__main__":
    main()