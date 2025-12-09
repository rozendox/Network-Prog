# learner.py

from node import Node
from message import Message, PaxosMessageType
from typing import Dict, Any, Set


class Learner(Node):
    """Implementa a função Learner no Paxos."""

    def __init__(self, node_id: str, all_acceptor_ids: Set[str]):
        super().__init__(node_id)
        self.all_acceptor_ids = all_acceptor_ids
        self.quorum_size = (len(all_acceptor_ids) // 2) + 1

        # Estado do Learner
        # Armazena { (proposal_id, value): [lista de acceptor_ids que aceitaram] }
        self.accepted_counts: Dict[tuple, Set[str]] = {}
        self.learned_value: Optional[Any] = None
        self.is_learned = False

    def _handle_message(self, message: Message):
        if message.msg_type == PaxosMessageType.LEARN:
            self._handle_learn(message)
        else:
            pass  # Ignora outros tipos de mensagem

    def _handle_learn(self, learn_msg: Message):
        if self.is_learned:
            return  # Valor já foi decidido

        # Chave para contagem: (proposal_id, value)
        key = (learn_msg.proposal_id, learn_msg.value)

        if key not in self.accepted_counts:
            self.accepted_counts[key] = set()

        self.accepted_counts[key].add(learn_msg.sender_id)

        current_count = len(self.accepted_counts[key])

        print(
            f"[{self.node_id}] Recebeu LEARN para ID: {learn_msg.proposal_id} | Valor: {learn_msg.value} | Contagem: {current_count}")

        # Verifica se o Quorum foi alcançado
        if current_count >= self.quorum_size:
            self.learned_value = learn_msg.value
            self.is_learned = True
            print("=" * 60)
            print(f"[{self.node_id}] 🎉 CONSENSO ALCANÇADO! O valor decidido é: {self.learned_value}")
            print("=" * 60)