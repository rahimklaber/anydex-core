from datetime import datetime

from sqlalchemy import Column, Integer, String, LargeBinary, create_engine, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Key(Base):
    """
    Database definition for keys table.
    """
    __tablename__ = "keys"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    # public_key = Column(String(32))
    private_key = Column(LargeBinary(32))
    address = Column(String(42))  # including "0x" address is 42 bytes long


class Transaction(Base):
    """
    Database definition for transactions
    """
    __tablename__ = "transactions"
    # need to include a relation to the key table.
    id = Column(Integer, primary_key=True)
    # blockHash = Column(String)
    block_number = Column(Integer)
    # chainId = Column(Integer)
    from_ = Column(String(42))
    gas = Column(Integer)
    gas_price = Column(Integer)
    hash = Column(String)
    nonce = Column(Integer)
    # r = Column(LargeBinary)
    # s = Column(LargeBinary)
    to = Column(String(42))
    # v = Column(Integer)
    value = Column(Integer)
    date_time = Column(DateTime, default=datetime.utcnow())
    is_pending = Column(Boolean, default=False)
    # transaction_index = Column(Integer)


def initialize_db(db_path):
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    session.query(Key)
    return session
