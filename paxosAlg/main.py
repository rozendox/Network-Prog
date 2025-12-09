import time
import logging
import random
import threading
import sys
from typing import Dict, List
from config_logs import setup_logging

from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
from node import Node

# Variável global para controlar o loop da thread
SIMULATION_RUNNING = True


def simulation_loop(all_nodes: List[Node], learners: Dict[str, Learner]):
    """
    Função que roda em uma Thread separada.
    Ela processa as mensagens e avança o tempo da simulação.
    """
    cycle = 0
    while SIMULATION_RUNNING:
        cycle += 1
        # Logging menos frequente para não poluir o terminal de comandos
        if cycle % 5 == 0:
            logging.info(f"--- CICLO {cycle} (Simulação rodando...) ---")

        # Aleatoriedade na ordem de execução
        random.shuffle(all_nodes)

        for node in all_nodes:
            try:
                node.process_messages()
            except Exception as e:
                logging.error(f"Erro no nó {node.node_id}: {e}")

        time.sleep(1.0)  # Velocidade da simulação (1 segundo por ciclo)


def main():
    setup_logging()
    logging.info("--- SISTEMA PAXOS INTERATIVO INICIALIZADO ---")

    # --- Configuração ---
    ACCEPTOR_IDS = {"A1", "A2", "A3", "A4", "A5"}
    LEARNER_IDS = {"L1", "L2"}

    acceptors = {id: Acceptor(id, LEARNER_IDS) for id in ACCEPTOR_IDS}
    learners = {id: Learner(id, ACCEPTOR_IDS) for id in LEARNER_IDS}

    # Valores iniciais
    proposer_1 = Proposer("P1", ACCEPTOR_IDS, initial_value="AZUL")
    proposer_2 = Proposer("P2", ACCEPTOR_IDS, initial_value="VERMELHO")

    all_nodes = list(acceptors.values()) + list(learners.values()) + [proposer_1, proposer_2]

    # --- Inicia a Thread de Simulação ---
    sim_thread = threading.Thread(target=simulation_loop, args=(all_nodes, learners))
    sim_thread.daemon = True  # Thread morre se o programa principal fechar
    sim_thread.start()

    # --- Loop de Comandos do Usuário ---
    print("\n" + "=" * 50)
    print("COMANDOS DISPONIVEIS:")
    print("  status        -> Ver se o consenso foi atingido")
    print("  p1 <valor>    -> P1 propõe um novo valor (ex: p1 AMARELO)")
    print("  p2 <valor>    -> P2 propõe um novo valor")
    print("  sair          -> Encerrar simulação")
    print("=" * 50 + "\n")

    # P1 começa automaticamente
    logging.info("Auto-iniciando P1 com valor AZUL...")
    proposer_1.start_proposal()

    global SIMULATION_RUNNING

    while True:
        try:
            # Input bloqueante (aguarda o usuário digitar)
            user_input = input("CMD> ").strip().split()

            if not user_input:
                continue

            command = user_input[0].lower()

            if command == "sair":
                print("Encerrando simulação...")
                SIMULATION_RUNNING = False
                sim_thread.join()
                break

            elif command == "status":
                print("\n--- STATUS ATUAL ---")
                for l_id, l in learners.items():
                    status = f"Valor: {l.learned_value}" if l.is_learned else "Ainda não decidiu"
                    print(f"[{l_id}] {status}")
                print("--------------------\n")

            elif command == "p1":
                if len(user_input) < 2:
                    print("Erro: Digite o valor. Ex: p1 VERDE")
                    continue
                new_val = user_input[1]
                logging.info(f"!!! COMANDO MANUAL: P1 vai propor '{new_val}' !!!")
                proposer_1.current_value = new_val
                proposer_1.start_proposal()

            elif command == "p2":
                if len(user_input) < 2:
                    print("Erro: Digite o valor. Ex: p2 ROXO")
                    continue
                new_val = user_input[1]
                logging.info(f"!!! COMANDO MANUAL: P2 vai propor '{new_val}' !!!")
                proposer_2.current_value = new_val
                proposer_2.start_proposal()

            else:
                print("Comando desconhecido.")

        except KeyboardInterrupt:
            SIMULATION_RUNNING = False
            break


if __name__ == "__main__":
    main()