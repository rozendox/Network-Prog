"""

______      ______  ___   __    ______
/_____/\    /_____/\/__/\ /__/\ /_____/\
\:::_ \ \   \:::__\/\::\_\\  \ \\:::_ \ \
 \:(_) ) )_    /: /  \:. `-\  \ \\:\ \ \ \
  \: __ `\ \  /::/___ \:. _    \ \\:\ \ \ \
   \ \ `\ \ \/_:/____/\\. \`-\  \ \\:\/.:| |
    \_\/ \_\/\_______\/ \__\/ \__\/ \____/_/


"""
import asyncio
import ssl
from pqcrypto.kem.kyber512 import decrypt  # This might be incorrect
from pqcrypto.sign.dilithium3 import verify
from database import SessionLocal, Message
from key_gen import get_user_keys


class SecureServer:
    def __init__(self, host="127.0.0.1", port=65432):
        self.host = host
        self.port = port
        self.ssl_context = self.setup_tls()  # Corrected attribute name

    def setup_tls(self):
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
        return ssl_context

    async def handle_client(self, reader, writer):
        addr = writer.get_extra_info("peername")  # Corrected method name
        print(f"[SERVER]~ Connection from {addr}")

        # Receive encrypted messages
        ciphertext = await reader.read(4096)
        sender, receiver, encrypted_msg = self.process_incoming_message(ciphertext)  # Corrected method name

        # Save to database
        db = SessionLocal()
        msg = Message(sender=sender, receiver=receiver, message=encrypted_msg)
        db.add(msg)
        db.commit()
        db.close()

        print(f"[SERVER]~ Received message from {sender} to {receiver}")
        writer.close()

    def process_incoming_message(self, ciphertext):
        """
        Process received message:
        1. Decrypt message using recipient's private key
        2. Verify digital signature to authenticate sender
        """
        try:
            # 1. Split message into parts (metadata and encrypted content)
            sender, receiver, encrypted_message, signature = self.parse_message(ciphertext)

            # 2. Retrieve recipient's keys
            public_key_receiver, private_key_receiver = get_user_keys(receiver)

            # 3. Decrypt message with recipient's private key
            decrypted_message = decrypt(private_key_receiver, encrypted_message)

            # 4. Retrieve sender's public key
            public_key_sender, _ = get_user_keys(sender)

            # 5. Verify sender's digital signature
            is_valid = verify(signature, decrypted_message, public_key_sender)
            if not is_valid:
                raise ValueError("Invalid digital signature! Message may have been tampered.")

            print(f"[SERVER] Message from {sender} to {receiver} authenticated successfully.")
            return sender, receiver, decrypted_message

        except Exception as e:
            print(f"[SERVER] Error processing message: {e}")
            raise

    def parse_message(self, ciphertext):
        """
        Split received message into parts: sender, receiver, content, and signature
        """
        try:
            # Example: Simulate received message as concatenated bytes
            # Format: [sender|receiver|encrypted_message|signature]
            parts = ciphertext.split(b'|')
            if len(parts) != 4:
                raise ValueError("Invalid message format!")

            sender = parts[0].decode()
            receiver = parts[1].decode()
            encrypted_message = parts[2]
            signature = parts[3]
            return sender, receiver, encrypted_message, signature

        except Exception as e:
            print(f"[SERVER] Error splitting message: {e}")
            raise

    async def run(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port, ssl=self.ssl_context  # Corrected attribute name
        )
        print(f"[SERVER]~ Server started at {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


# Main execution
if __name__ == "__main__":
    server = SecureServer()
    asyncio.run(server.run())
