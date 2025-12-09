r"""
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
import traceback
import oqs
from typing import Tuple

from database import SessionLocal, Message
from key_gen import get_user_keys  # deve retornar (public_key_bytes, secret_key_bytes) para cada usuário


def setup_tls() -> ssl.SSLContext:
    ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    ssl_context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
    return ssl_context


class SecureServer:
    def __init__(self, host: str = "127.0.0.1", port: int = 65432):
        self.host = host
        self.port = port
        self.ssl_context = setup_tls()

    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        addr = writer.get_extra_info("peername")
        print(f"[SERVER]~ Connection from {addr}")

        try:
            raw = await reader.read(16 * 1024)  # 16KB
            if not raw:
                print("[SERVER]~ No data received.")
                return

            sender, receiver, decrypted_message = self.process_incoming_message(raw)

            # Save to DB
            db = SessionLocal()
            try:
                msg = Message(sender=sender, receiver=receiver, message=decrypted_message)
                db.add(msg)
                db.commit()
            finally:
                db.close()

            print(f"[SERVER]~ Stored message from {sender} to {receiver}")

        except Exception as e:
            print(f"[SERVER]~ Error handling client {addr}: {e}")
            traceback.print_exc()

        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass

    def process_incoming_message(self, raw: bytes) -> Tuple[str, str, str]:
        """
        Process received message:
          - parse parts
          - decapsulate Kyber shared secret for receiver
          - decrypt symmetric ciphertext (AES-GCM assumed)
          - verify Dilithium3 signature (using oqs)
        Returns: (sender, receiver, plaintext string)
        """
        try:
            sender, receiver, kem_cipher, encrypted_message, signature = self.parse_message(raw)

            # Retrieve receiver keys: espera (public_key_bytes, secret_key_bytes)
            pk_recv, sk_recv = get_user_keys(receiver)
            if sk_recv is None:
                raise ValueError(f"Secret key for receiver '{receiver}' not found")

            # --- Kyber512 decapsulation (KEM) ---
            with oqs.KeyEncapsulation("Kyber512") as kem:
                # import_secret_key expects the secret key bytes as exported by oqs
                kem.import_secret_key(sk_recv)
                shared_secret = kem.decap_secret(kem_cipher)
                # shared_secret is bytes

            # --- Symmetric decryption (AES-GCM) ---
            plaintext = self.symmetric_decrypt(shared_secret, encrypted_message)

            # --- Verify Dilithium3 signature with oqs ---
            pk_sender, _ = get_user_keys(sender)
            if pk_sender is None:
                raise ValueError(f"Public key for sender '{sender}' not found")

            if not self.verify_dilithium3(signature, plaintext.encode(), pk_sender):
                raise ValueError("Invalid digital signature (Dilithium3)")

            print(f"[SERVER] Message from {sender} to {receiver} authenticated successfully.")
            return sender, receiver, plaintext

        except Exception as e:
            print(f"[SERVER] Error processing message: {e}")
            traceback.print_exc()
            raise

    @staticmethod
    def verify_dilithium3(signature: bytes, message: bytes, public_key: bytes) -> bool:
        """
        Verifica assinatura Dilithium3 usando oqs.
        oqs.Signature.verify(message, signature, public_key) -> True/False
        """
        try:
            with oqs.Signature("Dilithium3") as sig:
                return sig.verify(message, signature, public_key)
        except Exception as e:
            print(f"[SERVER] Error in signature verification: {e}")
            return False

    @staticmethod
    def symmetric_decrypt(key: bytes, data: bytes) -> str:
        """
        Decifra data (bytes) com AES-GCM.
        Formato esperado (convenção usada aqui):
          nonce (12 bytes) | tag (16 bytes) | ciphertext (resto)
        Usa key[:32] como chave AES-256.
        Retorna string (utf-8) do plaintext.
        """
        from Crypto.Cipher import AES

        if len(data) < 12 + 16:
            raise ValueError("Encrypted payload too short")

        nonce = data[:12]
        tag = data[12:28]
        ciphertext = data[28:]

        cipher = AES.new(key[:32], AES.MODE_GCM, nonce=nonce)
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode("utf-8", errors="strict")

    @staticmethod
    def parse_message(raw: bytes) -> Tuple[str, str, bytes, bytes, bytes]:
        """
        Formato esperado (bytes): sender|receiver|kem_cipher|encrypted_message|signature
        OBS: esse formato falha se qualquer campo binário contiver o separador b'|'.
        Para produção recomendo usar JSON+base64 ou framing com comprimentos.
        """
        parts = raw.split(b"|")
        if len(parts) != 5:
            raise ValueError("Invalid message format: expected 5 parts separated by '|'")

        sender = parts[0].decode("utf-8")
        receiver = parts[1].decode("utf-8")
        kem_cipher = parts[2]
        encrypted = parts[3]
        signature = parts[4]

        return sender, receiver, kem_cipher, encrypted, signature

    async def run(self):
        server = await asyncio.start_server(
            self.handle_client, self.host, self.port, ssl=self.ssl_context
        )
        print(f"[SERVER]~ Server running at {self.host}:{self.port}")
        async with server:
            await server.serve_forever()


if __name__ == "__main__":
    server = SecureServer()
    asyncio.run(server.run())
