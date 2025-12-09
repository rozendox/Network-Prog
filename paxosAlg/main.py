# main.py

import time
import logging
from typing import Dict, List
from config_logs import setup_logging  # <--- Importa a configuração

# Importa as classes
from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
from node import Node


def main():
    # 1. INICIALIZAÇÃO DOS LOGS (Primeira coisa a fazer)
    setup_logging()

    logging.info("--- SISTEMA PAXOS INICIALIZADO ---")

    # --- Configuração ---
    ACCEPTOR_IDS = {"A1", "A2", "A3", "A4", "A5"}
    LEARNER_IDS = {"L1", "L2"}

    # --- Instanciação dos Nós ---
    acceptors: Dict[str, Acceptor] = {
        id: Acceptor(id, LEARNER_IDS) for id in ACCEPTOR_IDS
    }
    learners: Dict[str, Learner] = {
        id: Learner(id, ACCEPTOR_IDS) for id in LEARNER_IDS
    }

    proposer_1 = Proposer("P1", ACCEPTOR_IDS, initial_value="Valor_Original_P1")
    proposer_2 = Proposer("P2", ACCEPTOR_IDS, initial_value="Valor_Concorrente_P2")

    all_nodes: List[Node] = list(acceptors.values()) + list(learners.values()) + [proposer_1, proposer_2]

    logging.info(f"Total de Acceptors: {len(ACCEPTOR_IDS)}. Quorum necessário: {(len(ACCEPTOR_IDS) // 2) + 1}")

    # --- Simulação do Fluxo ---

    # Passo 1: P1 inicia a primeira proposta
    proposer_1.start_proposal()

    # Simula a passagem do tempo
    for i in range(1, 4):
        logging.info(f"--- CICLO DE REDE {i} ---")

        # Cada nó processa as mensagens destinadas a ele
        for node in all_nodes:
            node.process_messages()

        # O P2 tenta concorrer a partir do ciclo 2
        if i == 2:
            logging.info("!!! P2 entrando para concorrer !!!")
            proposer_2.start_proposal()

        # Parar se o consenso for alcançado
        if any(learner.is_learned for learner in learners.values()):
            logging.info("--- Consenso Alcançado em todos os Learners. Encerrando Simulação. ---")
            break

        time.sleep(0.5)


if __name__ == "__main__":
    main()