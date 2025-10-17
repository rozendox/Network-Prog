import asyncio
from pqcrypto.kem.kyber512 import encrypt
from key_gen import get_user_keys


class SecureClient:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.ssl.context = self.setup.tls()

    async def send_message(self, receiver, message):
        public_key, private_key = get_user_keys(receiver)
        encrypted_msg, shared_key = encrypt(message.encode(), public_key)

        reader, writer = await asyncio.open_connection(self.host, self.port)
        writer.write(encrypted_msg)
        await writer.drain()
        writer.close()
        await  writer.wait_closed()
        print(f"[CLIENT]~ Message sent to {receiver}")