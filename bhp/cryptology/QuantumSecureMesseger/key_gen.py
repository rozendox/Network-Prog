import oqs
from database import SessionLocal, User


def generate_user_keys(username: str):
    """
    Gera um par de chaves Kyber512 (Pós-Quântico)
    e armazena no banco de dados.
    """

    # Cria objeto KEM Kyber512
    kem = oqs.KeyEncapsulation("Kyber512")

    # Gera (public_key, secret_key)
    public_key = kem.generate_keypair()
    secret_key = kem.export_secret_key()

    # Salva no banco
    db = SessionLocal()
    user = User(
        username=username,
        public_key=public_key,
        secret_key=secret_key,
    )
    db.add(user)
    db.commit()
    db.close()

    print(f"[KEYGEN] Chaves Kyber512 geradas para '{username}'.")


def get_user_keys(username: str):
    """
    Obtém as chaves (public_key, secret_key) de um usuário no banco.
    """

    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()

    if not user:
        raise ValueError(f"[KEYGEN] Usuário '{username}' não encontrado.")

    return user.public_key, user.secret_key
