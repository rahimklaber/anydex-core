from datetime import datetime

from sqlalchemy import Column, Integer, String, LargeBinary, create_engine, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class DatabaseSeed(Base):
    """
    Database definition for keys table.
    """
    __tablename__ = "seeds"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    seed = Column(String)


class DatabaseTransaction(Base):
    """
    Database definition for transactions
    """
    __tablename__ = "transactions"
    # need to include a relation to the key table.
    id = Column(Integer, primary_key=True)
    seed = Column(Integer)      # TODO FK for seeds
    origin = Column(String(90))     # 90 in case address is checksummed
    destination = Column(String(90))
    value = Column(Integer)
    hash = Column(String, unique=True)
    message = Column(String(255))   # TODO figure length
    currentindex = Column(Integer)
    date_time = Column(DateTime, default=datetime.utcnow())
    is_pending = Column(Boolean, default=False)
    bundle = Column(Integer('foreign key'))     # TODO figure out FK

    # transaction_index = Column(Integer)

    def __eq__(self, other):
        return self.hash == other.hash


class DatabaseBundle(Base):
    id = Column(Integer, primary_key=True)
    hash = Column(String(255))      # TODO figure length
    count = Column(Integer)


def initialize_db(db_path):
    engine = create_engine(f"sqlite:///{db_path}", echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session

