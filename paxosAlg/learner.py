# learner.py
import logging
from node import Node
from message import Message, PaxosMessageType
from typing import Dict, Any, Set, Optional


class Learner(Node):
    def __init__(self, node_id: str, all_acceptor_ids: Set[str]):
        super().__init__(node_id)
        self.all_acceptor_ids = all_acceptor_ids
        self.quorum_size = (len(all_acceptor_ids) // 2) + 1

        self.accepted_counts: Dict[tuple, Set[str]] = {}
        self.learned_value: Optional[Any] = None
        self.is_learned = False

    def _handle_message(self, message: Message):
        if message.msg_type == PaxosMessageType.LEARN:
            self._handle_learn(message)

    def _handle_learn(self, learn_msg: Message):
        if self.is_learned:
            return

        key = (learn_msg.proposal_id, learn_msg.value)

        if key not in self.accepted_counts:
            self.accepted_counts[key] = set()

        self.accepted_counts[key].add(learn_msg.sender_id)
        current_count = len(self.accepted_counts[key])

        logging.info(
            f"[{self.node_id}] Recebeu LEARN | ID: {learn_msg.proposal_id} | Votos: {current_count}/{self.quorum_size}")

        if current_count >= self.quorum_size:
            self.learned_value = learn_msg.value
            self.is_learned = True

            logging.info("=" * 60)
            logging.info(f"[{self.node_id}] CONSENSO ALCANÇADO! O valor decidido é: {self.learned_value}")
            logging.info("=" * 60)