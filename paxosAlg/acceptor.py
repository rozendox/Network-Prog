# acceptor.py

from node import Node
from message import Message, PaxosMessageType
from typing import Set


class Acceptor(Node):
    """Implementa a função Acceptor no Paxos."""

    def __init__(self, node_id: str, all_learner_ids: Set[str]):
        super().__init__(node_id)
        self.all_learner_ids = all_learner_ids
        # Estado do Acceptor
        self.promised_id: Optional[int] = -1  # Maior proposal_id (n) prometido
        self.accepted_id: Optional[int] = -1  # proposal_id (n) da última proposta aceita
        self.accepted_value: Optional[Any] = None  # Valor (v) da última proposta aceita

    def _handle_message(self, message: Message):
        if message.msg_type == PaxosMessageType.PREPARE:
            self._handle_prepare(message)
        elif message.msg_type == PaxosMessageType.ACCEPT:
            self._handle_accept(message)
        else:
            print(f"[{self.node_id}] Recebeu tipo de mensagem inesperado: {message.msg_type}")

    # --- FASE 1: Prepare/Promise ---
    def _handle_prepare(self, prepare_msg: Message):
        if prepare_msg.proposal_id > self.promised_id:
            # 1. Promete não aceitar mais propostas com ID menor
            self.promised_id = prepare_msg.proposal_id

            # 2. Responde com PROMISE
            promise_msg = Message(
                sender_id=self.node_id,
                receiver_id=prepare_msg.sender_id,
                msg_type=PaxosMessageType.PROMISE,
                proposal_id=self.promised_id,  # Retorna o ID que prometeu
                accepted_proposal_id=self.accepted_id,  # Retorna o maior ID que já aceitou
                value=self.accepted_value  # Retorna o valor associado
            )
        else:
            # Rejeita: Já prometeu para uma proposta com ID igual ou maior
            promise_msg = Message(
                sender_id=self.node_id,
                receiver_id=prepare_msg.sender_id,
                msg_type=PaxosMessageType.PROMISE,
                proposal_id=self.promised_id,  # Retorna o ID mais alto que viu
            )

        self.network.send_message(promise_msg)

    # --- FASE 2: Accept/Accepted ---
    def _handle_accept(self, accept_msg: Message):
        # Condição de aceitação: O ID da proposta deve ser >= ao ID prometido mais alto.
        # Na prática, se o Acceptor não recebeu um PREPARE posterior, é igual.
        if accept_msg.proposal_id >= self.promised_id:
            # 1. Aceita a proposta
            self.promised_id = accept_msg.proposal_id  # Atualiza, garantindo que seja o mais alto
            self.accepted_id = accept_msg.proposal_id
            self.accepted_value = accept_msg.value

            # 2. Responde com ACCEPTED para o Proposer
            accepted_msg_to_proposer = Message(
                sender_id=self.node_id,
                receiver_id=accept_msg.sender_id,
                msg_type=PaxosMessageType.ACCEPTED,
                proposal_id=self.accepted_id,
                value=self.accepted_value
            )
            self.network.send_message(accepted_msg_to_proposer)

            # 3. Notifica todos os Learners
            learn_msg = Message(
                sender_id=self.node_id,
                receiver_id="ALL_LEARNERS",  # Marca para broadcast (tratado pela Network ou main)
                msg_type=PaxosMessageType.LEARN,
                proposal_id=self.accepted_id,
                value=self.accepted_value
            )
            # Na simulação, vamos enviar individualmente para cada learner
            for learner_id in self.all_learner_ids:
                learn_msg_clone = Message(
                    sender_id=self.node_id,
                    receiver_id=learner_id,
                    msg_type=PaxosMessageType.LEARN,
                    proposal_id=self.accepted_id,
                    value=self.accepted_value
                )
                self.network.send_message(learn_msg_clone)
        else:
            # Rejeita: ID de proposta menor que o ID prometido mais alto
            print(f"[{self.node_id}] Rejeitou ACCEPT {accept_msg.proposal_id} < {self.promised_id}")