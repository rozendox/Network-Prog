import logging
import random
import threading
from typing import List
from message import Message


class Network:
    """Simula a camada de comunicação assíncrona com latência variável e Thread-Safe."""

    _message_queue: List[Message] = []
    _lock = threading.Lock()  # Bloqueio para controle de concorrência

    @classmethod
    def send_message(cls, message: Message):
        with cls._lock:  # Só entra aqui um por vez
            cls._message_queue.append(message)
        # logging.debug(f"\t[NETWORK] Enviado: {message}")

    @classmethod
    def get_messages_for_node(cls, node_id: str) -> List[Message]:
        with cls._lock:
            # Filtra mensagens
            messages = [msg for msg in cls._message_queue if msg.receiver_id == node_id]

            # Remove da fila global as mensagens que foram pegas
            cls._message_queue = [msg for msg in cls._message_queue if msg.receiver_id != node_id]

        # O embaralhamento pode ocorrer fora do lock
        if messages:
            random.shuffle(messages)

        return messages