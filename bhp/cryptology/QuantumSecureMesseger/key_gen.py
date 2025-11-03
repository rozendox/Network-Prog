import os
from pqcrypto.kem.kyber512 import generate_keypair
from sqlalchemy.orm import Session
from database import SessionLocal, User

KEYS_DIR = "keys"


def generate_user_keys(username):
    public_key, secret_key = generate_keypair()

    db = SessionLocal()
    user = User(username=username, public_key=public_key, secret_key=secret_key)
    db.add(user)
    db.commit()
    db.close()

    print(f"User {username} keys generated.")


def get_user_keys(username): # aqui a gente recupera as chaves de um user
    db = SessionLocal()
    user = db.query(User).filter(User.username == username).first()
    db.close()
    if not user:
        raise ValueError(f"User {username} not found.")
    return user.public_key, user.secret_key
