# network.py
import logging
from typing import List
from message import Message

class Network:
    """Simula a camada de comunicação assíncrona."""

    _message_queue: List[Message] = []

    @classmethod
    def send_message(cls, message: Message):
        cls._message_queue.append(message)
        # Usamos DEBUG ou INFO dependendo do quão verboso você quer que seja
        logging.info(f"\t[NETWORK] Enviado: {message}")

    @classmethod
    def get_messages_for_node(cls, node_id: str) -> List[Message]:
        messages = [msg for msg in cls._message_queue if msg.receiver_id == node_id]
        cls._message_queue = [msg for msg in cls._message_queue if msg.receiver_id != node_id]
        return messages