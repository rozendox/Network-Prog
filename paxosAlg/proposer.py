# proposer.py

from node import Node
from message import Message, PaxosMessageType
from typing import Set, Any, Dict


class Proposer(Node):
    """Implementa a função Proposer no Paxos."""

    def __init__(self, node_id: str, all_acceptor_ids: Set[str], initial_value: Any):
        super().__init__(node_id)
        self.all_acceptor_ids = all_acceptor_ids
        self.quorum_size = (len(all_acceptor_ids) // 2) + 1

        # --- CORREÇÃO AQUI ---
        # Extrai apenas os dígitos do node_id (ex: "P1" vira "1", "Proposer_02" vira "02")
        numeric_part = ''.join(filter(str.isdigit, node_id))

        if not numeric_part:
            # Fallback seguro caso o ID não tenha números (ex: "Master")
            # Usamos hash para gerar um número único
            numeric_part = str(abs(hash(node_id)) % 100)

        # Cria um ID de proposta base (ex: 100 para P1, 200 para P2)
        # Isso garante que P1 gere 101, 102... e P2 gere 201, 202... evitando colisão inicial
        self.current_proposal_id = int(numeric_part + '00')
        # ---------------------

        self.current_value = initial_value
        self.is_proposing = False

        # Estado da Fase 1 (Prepare)
        self.promises_received: Dict[str, Message] = {}
        self.highest_accepted_id = -1
        self.highest_accepted_value: Optional[Any] = None

    def _handle_message(self, message: Message):
        if message.msg_type == PaxosMessageType.PROMISE:
            self._handle_promise(message)
        elif message.msg_type == PaxosMessageType.ACCEPTED:
            pass
        else:
            print(f"[{self.node_id}] Recebeu tipo de mensagem inesperado: {message.msg_type}")

    def start_proposal(self):
        """Inicia um novo ciclo de consenso (FASE 1)."""
        if self.is_proposing:
            print(f"[{self.node_id}] Já está propondo. Cancelando novo ciclo.")
            return

        self.current_proposal_id += 1
        self.promises_received = {}
        self.is_proposing = True
        self.highest_accepted_id = -1
        self.highest_accepted_value = None

        print(f"\n[{self.node_id}] Iniciando Proposta ID: {self.current_proposal_id} com Valor: {self.current_value}")

        # Envia a mensagem PREPARE para todos os Acceptors
        for acceptor_id in self.all_acceptor_ids:
            prepare_msg = Message(
                sender_id=self.node_id,
                receiver_id=acceptor_id,
                msg_type=PaxosMessageType.PREPARE,
                proposal_id=self.current_proposal_id
            )
            self.network.send_message(prepare_msg)

    # --- FASE 1: Promise ---
    def _handle_promise(self, promise_msg: Message):
        if not self.is_proposing or promise_msg.proposal_id != self.current_proposal_id:
            return  # Mensagem obsoleta ou não relacionada ao ciclo atual

        self.promises_received[promise_msg.sender_id] = promise_msg

        # 1. Monitora se o Quorum foi alcançado
        if len(self.promises_received) == self.quorum_size:
            print(f"[{self.node_id}] Quorum alcançado ({self.quorum_size} PROMISEs).")
            # Nota: Não setamos is_proposing = False aqui pois ainda precisamos enviar ACCEPT

            # 2. Verifica se algum Acceptor já aceitou um valor
            for msg in self.promises_received.values():
                if msg.accepted_proposal_id is not None and msg.accepted_proposal_id > self.highest_accepted_id:
                    self.highest_accepted_id = msg.accepted_proposal_id
                    self.highest_accepted_value = msg.value

            # 3. Define o valor para a FASE 2
            if self.highest_accepted_value is not None:
                new_value = self.highest_accepted_value
                print(f"[{self.node_id}] Adotando valor de proposta anterior: {new_value}")
            else:
                new_value = self.current_value

            # 4. Inicia a FASE 2 (Accept)
            self._send_accept(new_value)

    # --- FASE 2: Accept ---
    def _send_accept(self, value_to_propose: Any):
        for acceptor_id in self.all_acceptor_ids:
            accept_msg = Message(
                sender_id=self.node_id,
                receiver_id=acceptor_id,
                msg_type=PaxosMessageType.ACCEPT,
                proposal_id=self.current_proposal_id,
                value=value_to_propose
            )
            self.network.send_message(accept_msg)
        print(f"[{self.node_id}] Enviando ACCEPT com ID: {self.current_proposal_id} e Valor: {value_to_propose}")