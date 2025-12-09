# node.py
import logging
from network import Network

class Node:
    """Classe base para todos os participantes do Paxos."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.network = Network

    def process_messages(self):
        received_messages = self.network.get_messages_for_node(self.node_id)
        if received_messages:
            logging.info(f"[{self.node_id}] Processando {len(received_messages)} mensagens recebidas.")
            for msg in received_messages:
                self._handle_message(msg)

    def _handle_message(self, message):
        raise NotImplementedError("Subclasses devem implementar _handle_message")