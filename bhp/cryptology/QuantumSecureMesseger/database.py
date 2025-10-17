from sqlalchemy import create_engine, Column, LargeBinary, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# configs do db

DATABASE_URL = "sqlite:///secure_communication.db"
Base = declarative_base()
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    password = Column(String)
    public_key = Column(LargeBinary)
    private_key = Column(LargeBinary)


class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String)
    receiver = Column(String)
    content = Column(LargeBinary)


Base.metadata.create_all(bind=engine)
