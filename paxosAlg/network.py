# network.py

from typing import List, Dict
from message import Message


class Network:
    """Simula a camada de comunicação assíncrona."""

    # Armazena mensagens pendentes (fila de mensagens)
    _message_queue: List[Message] = []

    @classmethod
    def send_message(cls, message: Message):
        """Adiciona uma mensagem para ser processada pelo destinatário."""
        cls._message_queue.append(message)
        print(f"\t[NETWORK] Mensagem enviada: {message}")

    @classmethod
    def get_messages_for_node(cls, node_id: str) -> List[Message]:
        """Retorna e remove todas as mensagens destinadas a um nó específico."""
        messages = [msg for msg in cls._message_queue if msg.receiver_id == node_id]
        # Remove as mensagens processadas da fila
        cls._message_queue = [msg for msg in cls._message_queue if msg.receiver_id != node_id]
        return messages