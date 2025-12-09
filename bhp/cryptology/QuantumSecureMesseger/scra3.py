import numpy as np
import secrets

# Configurações de parâmetros para segurança
n = 256  # Dimensão do vetor secreto (segurança aumenta com n)
q = 4096  # Módulo (deve ser um número primo ou potência de 2 para facilitar operações)
error_std_dev = 3.2  # Desvio padrão do erro gaussiano


def generate_key_pair():
    """Gera um par de chaves público e privado para criptografia."""
    secret_key = np.random.randint(0, q, n)  # Chave privada
    public_key_a = np.random.randint(0, q, (n, n))  # Matriz pública A
    error = np.random.normal(0, error_std_dev, n).astype(int) % q  # Erro Gaussiano

    # Chave pública: b = A*s + erro
    public_key_b = (np.dot(public_key_a, secret_key) + error) % q

    return (public_key_a, public_key_b), secret_key


def encrypt(public_key, message):
    """Criptografa uma mensagem usando a chave pública."""
    public_key_a, public_key_b = public_key

    # Convertendo
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    #
    # a mensagem em vetor binário e ajuste ao espaço de mensagem
    message_vector = np.array([int(bit) for bit in bin(message)[2:].zfill(n)]) * (q // 2)

    # Vetores aleatórios
    r = np.random.randint(0, 2, n)

    # Criptografia
    u = (np.dot(r, public_key_a)) % q
    v = (np.dot(r, public_key_b) + message_vector) % q

    return u, v


def decrypt(private_key, ciphertext):
    """Descriptografa uma mensagem usando a chave privada."""
    u, v = ciphertext
    partial = (v - np.dot(u, private_key)) % q

    # Decodificar a mensagem
    message_vector = (partial + (q // 4)) // (q // 2) % 2
    message = int("".join(map(str, message_vector.astype(int))), 2)

    return message


# Exemplo de uso
def main():
    print("Gerando chaves...")
    (public_key, secret_key) = generate_key_pair()

    print("Chaves geradas com sucesso!")

    # Mensagem para criptografar
    original_message = 22
    print(f"Mensagem original: {original_message}")

    # Criptografar mensagem
    ciphertext = encrypt(public_key, original_message)
    print(f"Texto cifrado: {ciphertext}")

    # Descriptografar mensagem
    decrypted_message = decrypt(secret_key, ciphertext)
    print(f"Mensagem descriptografada: {decrypted_message}")

    # Verificação
    assert original_message == decrypted_message, "Erro: Mensagem descriptografada não coincide!"
    print("Criptografia e descriptografia bem-sucedidas!")


if __name__ == "__main__":
    main()
