# proposer.py
import logging
from node import Node
from message import Message, PaxosMessageType
from typing import Set, Any, Dict, Optional


class Proposer(Node):
    def __init__(self, node_id: str, all_acceptor_ids: Set[str], initial_value: Any):
        super().__init__(node_id)
        self.all_acceptor_ids = all_acceptor_ids
        self.quorum_size = (len(all_acceptor_ids) // 2) + 1

        numeric_part = ''.join(filter(str.isdigit, node_id))
        if not numeric_part:
            numeric_part = str(abs(hash(node_id)) % 100)

        self.current_proposal_id = int(numeric_part + '00')
        self.current_value = initial_value
        self.is_proposing = False

        self.promises_received: Dict[str, Message] = {}
        self.highest_accepted_id = -1
        self.highest_accepted_value: Optional[Any] = None

    def _handle_message(self, message: Message):
        if message.msg_type == PaxosMessageType.PROMISE:
            self._handle_promise(message)
        elif message.msg_type == PaxosMessageType.ACCEPTED:
            pass # Proposer recebe Accepted mas a lógica de decisão final está no Learner neste exemplo
        else:
            logging.warning(f"[{self.node_id}] Recebeu tipo inesperado: {message.msg_type}")

    def start_proposal(self):
        if self.is_proposing:
            logging.warning(f"[{self.node_id}] Já está propondo. Ignorando solicitação.")
            return

        self.current_proposal_id += 1
        self.promises_received = {}
        self.is_proposing = True
        self.highest_accepted_id = -1
        self.highest_accepted_value = None

        logging.info(f"[{self.node_id}] Iniciando Proposta ID: {self.current_proposal_id} | Valor: {self.current_value}")

        for acceptor_id in self.all_acceptor_ids:
            prepare_msg = Message(
                sender_id=self.node_id,
                receiver_id=acceptor_id,
                msg_type=PaxosMessageType.PREPARE,
                proposal_id=self.current_proposal_id
            )
            self.network.send_message(prepare_msg)

    def _handle_promise(self, promise_msg: Message):
        if not self.is_proposing or promise_msg.proposal_id != self.current_proposal_id:
            return

        self.promises_received[promise_msg.sender_id] = promise_msg

        if len(self.promises_received) == self.quorum_size:
            logging.info(f"[{self.node_id}] quorum alcançado ({self.quorum_size} PROMISEs).")

            for msg in self.promises_received.values():
                if msg.accepted_proposal_id is not None and msg.accepted_proposal_id > self.highest_accepted_id:
                    self.highest_accepted_id = msg.accepted_proposal_id
                    self.highest_accepted_value = msg.value

            if self.highest_accepted_value is not None:
                new_value = self.highest_accepted_value
                logging.info(f"[{self.node_id}] Adotando valor de proposta anterior: {new_value}")
            else:
                new_value = self.current_value

            self._send_accept(new_value)

    def _send_accept(self, value_to_propose: Any):
        logging.info(f"[{self.node_id}] Enviando ACCEPT | ID: {self.current_proposal_id} | Valor: {value_to_propose}")
        for acceptor_id in self.all_acceptor_ids:
            accept_msg = Message(
                sender_id=self.node_id,
                receiver_id=acceptor_id,
                msg_type=PaxosMessageType.ACCEPT,
                proposal_id=self.current_proposal_id,
                value=value_to_propose
            )
            self.network.send_message(accept_msg)