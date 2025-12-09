# message.py

from enum import Enum
from typing import Any, Optional


class PaxosMessageType(Enum):
    PREPARE = "PREPARE"
    PROMISE = "PROMISE"
    ACCEPT = "ACCEPT"
    ACCEPTED = "ACCEPTED"
    LEARN = "LEARN"


class Message:
    def __init__(self,
                 sender_id: str,
                 receiver_id: str,
                 msg_type: PaxosMessageType,
                 proposal_id: Optional[int] = None,
                 value: Optional[Any] = None,
                 accepted_proposal_id: Optional[int] = None):
        self.sender_id = sender_id
        self.receiver_id = receiver_id
        self.msg_type = msg_type
        self.proposal_id = proposal_id  # Número da proposta (n)
        self.value = value  # Valor proposto (v)
        self.accepted_proposal_id = accepted_proposal_id  # Maior n aceito pelo Acceptor

    def __repr__(self) -> str:
        return (f"[{self.msg_type.name}] De: {self.sender_id} | Para: {self.receiver_id} | "
                f"ID Prop.: {self.proposal_id if self.proposal_id is not None else 'N/A'} | "
                f"Valor: {self.value if self.value is not None else 'N/A'}")