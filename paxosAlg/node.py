# node.py
import logging
from network import Network


class Node:
    """Classe base para todos os participantes do Paxos."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.network = Network
        self.is_alive = True

    def process_messages(self):
        if not self.is_alive:
            return

        received_messages = self.network.get_messages_for_node(self.node_id)
        if received_messages:
            logging.info(f"[{self.node_id}] Processando {len(received_messages)} mensagens recebidas.")
            for msg in received_messages:
                self._handle_message(msg)

    def fail(self):
        """Simula uma falha do nó"""
        self.is_alive = False
        logging.error(f"[{self.node_id}] FALHOU")

    def recover(self):
        """Simula a recuperacao do nó"""
        self.is_alive = True
        logging.info(f"[{self.node_id}] recuperou-se e está online")

    def _handle_message(self, message):
        raise NotImplementedError("Subclasses devem implementar _handle_message")
