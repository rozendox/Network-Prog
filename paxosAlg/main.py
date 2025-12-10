# main.py

import time
import logging
import threading
import sys
from random import random
from typing import Dict, List
from config_logs import setup_logging
# Importa as classes
from proposer import Proposer
from acceptor import Acceptor
from learner import Learner
from node import Node

SIMULATION_RUNNING = True


def simulation_loop(all_nodes: List[Node], learner: Dict[str, Learner]):
    """

    :param all_nodes:
    :param learner:
    :return:
    """
    cycle = 0
    while SIMULATION_RUNNING:
        cycle += 1
    if cycle % 10 == 0:
        logging.info(f"SIMULACAO EM ANDAMENTO ----{cycle}")

    random.shuffle(all_nodes)

    for node in all_nodes:
        try:
            node.process_messages()
        except Exception as e:
            logging.error(f"error ao processar mensagem no nó {node.node_id}: {e}")
    time.sleep(1.0)


def main():
    setup_logging()
    logging.info("--- SISTEMA PAXOS INICIALIZADO ---")
    ACCEPTOR_IDS = {"A1", "A2", "A3", "A4", "A5"}
    LEARNER_IDS = {"L1", "L2"}

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

    nodes_map = {node.node_id: node for node in all_nodes}

    sim_thread = threading.Thread(target=simulation_loop, args=(all_nodes, learners))
    sim_thread.daemon = True
    sim_thread.start()

    print("comandos disp")
    print("status")
    print("p1 <valor>")
    print("p2 <valor>")
    print("kill <id>")
    print("revive <id>")
    print("sair ")

    global SIMULATION_RUNNING

    while True:
        try:
            user_input = input("CMD> ").strip().split()
            if not user_input:
                continue

            command = user_input[0].lower()
            if command == "sair":
                logging.info("Encerrando")
                print("3")
                time.sleep(1)
                print("2")
                time.sleep(1)
                print("1")
                time.sleep(1)
                print("@@@ Ending @@@")
                SIMULATION_RUNNING = False
                sim_thread.join()
                break
            elif command == "status":
                print("STATUS DO SISTEMA")
                for l_id, l in learners.items():
                    decisao = f"VALOR DECIDIDO, {l.learned_value}" if l.is_learned else "ainda indeciso"
                    print(f"[{l_id}] {decisao}]")

                dead_nodes = [n_id for n_id, n in nodes_map.items() if not n.is_alive]
                if dead_nodes:
                    print(f"[ALERTA] Nos Offline (Mortos): {dead_nodes}")
                else:
                    print("[OK] Todos os nos estao online.")
                print("-------------------------\n")
            elif command == "p1":
                if len(user_input) < 2:
                    print(f"[{user_input[0]}] {user_input[0]}")
                    continue
                if proposer_1.is_alive:
                    valor = user_input[1]
                    logging.info(f"comando manual p1 vai propor: '{valor}'")
                    proposer_1.current_value = valor
                    proposer_1.start_proposal()
                else:
                    print("erro, 0 no p1 esta morto use o 'revive p1' primeiro")
            elif command == "p2":
                if len(user_input) < 2:
                    print("ERRO: digite o valor")
                    continue
                if proposer_2.is_alive:
                    valor = user_input[1]
                    logging.info("comando manual p2 vai propor: '{valor}'")
                    proposer_2.current_value = valor
                    proposer_2.start_proposal()
                else:
                    print("ERRO: 0 no p2 esta morto, use o 'revive p2' primeiro")
            elif command == "kill":
                if len(user_input) < 2:
                    print("uso: kill <ID> (ex: kill A1")
                    continue

                target_id = user_input[1].upper()
                if target_id in nodes_map:
                    nodes_map[target_id].fail()
                    print(f"[{target_id}] foi desligado")
                else:
                    print(f"No {target_id} nao encontrado")
            elif command == "revive":
                if len(user_input) < 2:
                    print("uso: revive <ID> (ex: revive A1")
                    continue

                    target_id = user_input[1].upper()
                    if target_id in nodes_map:
                        nodes_map[target_id].recover()
                        print(f"[{target_id}] foi revivido e esta online novamente")
                    else:
                        print(f"No {target_id} nao encontrado")
            else:
                print("comando nao encontrado")
        except KeyboardInterrupt:
            SIMULATION_RUNNING = False
            print("interrupt detected")
            break
        except Exception as e:
            print(f"erro inesperado no loop principal {e}")


if __name__ == "__main__":
    main()