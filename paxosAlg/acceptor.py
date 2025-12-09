# acceptor.py
import logging
from node import Node
from message import Message, PaxosMessageType
from typing import Set, Optional, Any


class Acceptor(Node):
    def __init__(self, node_id: str, all_learner_ids: Set[str]):
        super().__init__(node_id)
        self.all_learner_ids = all_learner_ids
        self.promised_id: Optional[int] = -1
        self.accepted_id: Optional[int] = -1
        self.accepted_value: Optional[Any] = None

    def _handle_message(self, message: Message):
        if message.msg_type == PaxosMessageType.PREPARE:
            self._handle_prepare(message)
        elif message.msg_type == PaxosMessageType.ACCEPT:
            self._handle_accept(message)
        else:
            logging.warning(f"[{self.node_id}] Tipo inesperado: {message.msg_type}")

    def _handle_prepare(self, prepare_msg: Message):
        if prepare_msg.proposal_id > self.promised_id:
            self.promised_id = prepare_msg.proposal_id

            promise_msg = Message(
                sender_id=self.node_id,
                receiver_id=prepare_msg.sender_id,
                msg_type=PaxosMessageType.PROMISE,
                proposal_id=self.promised_id,
                accepted_proposal_id=self.accepted_id,
                value=self.accepted_value
            )
        else:
            # Opcional: Logar rejeição de prepare
            # logging.info(f"[{self.node_id}] Rejeitando PREPARE {prepare_msg.proposal_id} <= {self.promised_id}")
            promise_msg = Message(
                sender_id=self.node_id,
                receiver_id=prepare_msg.sender_id,
                msg_type=PaxosMessageType.PROMISE,
                proposal_id=self.promised_id,
            )

        self.network.send_message(promise_msg)

    def _handle_accept(self, accept_msg: Message):
        if accept_msg.proposal_id >= self.promised_id:
            self.promised_id = accept_msg.proposal_id
            self.accepted_id = accept_msg.proposal_id
            self.accepted_value = accept_msg.value

            # Envia ACCEPTED de volta ao Proposer
            accepted_msg = Message(
                sender_id=self.node_id,
                receiver_id=accept_msg.sender_id,
                msg_type=PaxosMessageType.ACCEPTED,
                proposal_id=self.accepted_id,
                value=self.accepted_value
            )
            self.network.send_message(accepted_msg)

            # Notifica Learners
            for learner_id in self.all_learner_ids:
                learn_msg = Message(
                    sender_id=self.node_id,
                    receiver_id=learner_id,
                    msg_type=PaxosMessageType.LEARN,
                    proposal_id=self.accepted_id,
                    value=self.accepted_value
                )
                self.network.send_message(learn_msg)
        else:
            logging.info(f"[{self.node_id}] ❌ Rejeitou ACCEPT {accept_msg.proposal_id} < {self.promised_id}")