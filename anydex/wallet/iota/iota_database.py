from datetime import datetime

from sqlalchemy import Column, Integer, String, LargeBinary, create_engine, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class DatabaseSeed(Base):
    """
    Database definition for keys table.
    """
    __tablename__ = "seeds"
    id = Column(Integer, primary_key=True)
    name = Column(String)  # TODO: unique=True?
    seed = Column(String, unique=True)


class DatabaseTransaction(Base):
    """
    Database definition for transactions.
    """
    __tablename__ = "transactions"
    # need to include a relation to the key table.
    id = Column(Integer, primary_key=True)
    seed = Column(Integer, ForeignKey('seeds.seed'))  # TODO: FK seed or seedID to avoid large seed storing?
    origin = Column(String(90))  # 81 (address) + 9 (checksum)
    destination = Column(String(90))
    value = Column(Integer)
    hash = Column(String(81), unique=True)
    message = Column(String(2187))
    current_index = Column(Integer)
    date_time = Column(DateTime, default=datetime.utcnow())
    is_pending = Column(Boolean, default=False)
    bundle = Column(Integer, ForeignKey('bundles.id'))  # TODO: FK seed or seedID to avoid large seed storing?

    # transaction_index = Column(Integer)

    def __eq__(self, other):
        return self.hash == other.hash


class DatabaseBundle(Base):
    """
    Database definition for bundles.
    """
    __tablename__ = "bundles"
    id = Column(Integer, primary_key=True)
    hash = Column(String(81), unique=True)
    count = Column(Integer)


def initialize_db(db_path):
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session

