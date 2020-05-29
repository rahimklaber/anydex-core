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
    payment_id = Column(Integer, unique=True)
    succeeded = Column(Boolean)
    from_ = Column(String)
    to = Column(String)
    transaction_hash = Column(String)  # tx this payment is a part of
    amount = Column(Integer)
    asset_type = Column(String)  # we might support more assets
    date_time = Column(DateTime)  # this is in utc
    is_pending = Column(Boolean, default=False)

    def __repr__(self):
        return f"xlm_db.Payment({self.payment_id}, {self.from_}, {self.to}, {self.asset_type}, {self.amount} )"

    def __eq__(self, other):
        if not isinstance(other, Payment):
            raise NotImplementedError(f'cannot compare equality between{self} and {other}')
        return self.payment_id == other.payment_id


class Transaction:
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    hash = Column(String, unique=True)
    date_time = Column(DateTime)
    fee = Column(Integer)
    source_account = Column(String)
    operation_count = Column(Integer)
    succeeded = Column(Boolean, default=True)
    sequence_number = Column(Integer)
    transaction_envelope = Column(String)  # base64 encode xdr
    min_time_bound = Column(DateTime)  # unix time stamp
    max_time_bound = Column(DateTime)  # unix time stamp


def initialize_db(db_path):
    engine = create_engine(f'sqlite:///{db_path}', echo=False)
    Base.metadata.create_all(engine)
    session_maker = sessionmaker(bind=engine)
    session = session_maker()
    return session
