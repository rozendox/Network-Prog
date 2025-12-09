import asyncio
import ssl
import oqs
from Crypto.Cipher import AES
from key_gen import get_user_keys


class SecureClient:
    def __init__(self, username, host="127.0.0.1", port=65432):
        self.username = username
        self.host = host
        self.port = port
        self.ssl_context = self.setup_tls()

    def setup_tls(self):
        ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        ctx.load_verify_locations("cert.pem")
        return ctx

    def symmetric_encrypt(self, key: bytes, plaintext: str):
        cipher = AES.new(key[:32], AES.MODE_GCM)
        nonce = cipher.nonce
        ciphertext, tag = cipher.encrypt_and_digest(plaintext.encode())
        return nonce + tag + ciphertext

    async def send_message(self, receiver: str, message: str):
        print(f"[CLIENT]~ Preparing secure message to {receiver}...")

        # Load receiver public key (Kyber512)
        pk_recv, _ = get_user_keys(receiver)

        # ---- 1) Kyber512 encapsulation (gera shared secret + ciphertext) ----
        with oqs.KeyEncapsulation("Kyber512") as kem:
            kem.import_public_key(pk_recv)
            kem_cipher, shared_secret = kem.encap_secret()

        # ---- 2) AES-GCM encrypt message with shared secret ----
        encrypted_msg = self.symmetric_encrypt(shared_secret, message)

        # ---- 3) Sign with Dilithium3 ----
        pk_sender, sk_sender = get_user_keys(self.username)

        with oqs.Signature("Dilithium3") as sig:
            sig.import_secret_key(sk_sender)
            signature = sig.sign(message.encode())

        # ---- 4) Construct final packet ----
        packet = b"|".join([
            self.username.encode(),
            receiver.encode(),
            kem_cipher,
            encrypted_msg,
            signature,
        ])

        # ---- 5) Send to server over TLS ----
        reader, writer = await asyncio.open_connection(
            self.host, self.port, ssl=self.ssl_context
        )

        writer.write(packet)
        await writer.drain()
        writer.close()
        await writer.wait_closed()

        print(f"[CLIENT]~ Secure message sent to {receiver}!")
