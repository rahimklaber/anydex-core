from sqlalchemy import Column, Integer, String, create_engine, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class Secret(Base):
    """
    Database definition for keys table.
    """
    __tablename__ = 'secrets'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    secret = Column(String)
    address = Column(String)  # address is same as public key


class Payment(Base):
    """
    Database definition for payments table.
    In stellar there are multiple types of transactions and payment is one of them.
    """
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    payment_id = Column(Integer)
    succeeded = Column(Boolean)
    from_ = Column(String)
    to = Column(String)
    transaction_hash = Column(String)  # tx this payment is a part of
    amount = Column(Integer)
    asset_type = Column(String)  # we might support more assets
    date_time = Column(DateTime)

    def __repr__(self):
        return f"xlm_db.Payment({self.payment_id}, {self.from_}, {self.to}, {self.asset_type}, {self.amount} )"


def initialize_db(db_path):
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session
