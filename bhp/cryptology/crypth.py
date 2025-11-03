from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64


def decrypt_aes(ciphertext, key, iv):
    backend = default_backend()
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=backend)
    decryptor = cipher.decryptor()
    padded_data = decryptor.update(base64.b64decode(ciphertext)) + decryptor.finalize()
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    return unpadder.update(padded_data) + unpadder.finalize()


# Exemplo de uso
key = b'0123456789abcdef'  # Chave de 16 bytes (128 bits)
iv = b'0123456789abcdef'  # IV de 16 bytes (128 bits)
ciphertext = "base64_encoded_ciphertext_here"  # Texto criptografado em base64

try:
    decrypted_text = decrypt_aes(ciphertext, key, iv)
    print("Texto descriptografado:", decrypted_text.decode('utf-8'))
except Exception as e:
    print("Erro durante a descriptografia:", e)
