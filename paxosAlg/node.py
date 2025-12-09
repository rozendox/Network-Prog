# node.py

from network import Network


class Node:
    """Classe base para todos os participantes do Paxos (Proposer, Acceptor, Learner)."""

    def __init__(self, node_id: str):
        self.node_id = node_id
        self.network = Network  # Acesso à rede simulada

    def process_messages(self):
        """Méthodo abstrato para processar mensagens recebidas."""
        # Padrão: Template Method (em parte) ou apenas uma interface comum
        received_messages = self.network.get_messages_for_node(self.node_id)
        if received_messages:
            print(f"\n[{self.node_id}] Processando {len(received_messages)} mensagens recebidas.")
            for msg in received_messages:
                self._handle_message(msg)

    def _handle_message(self, message):
        """Deve ser implementado pelas subclasses para lidar com tipos específicos de mensagem."""
        raise NotImplementedError("Subclasses devem implementar _handle_message")