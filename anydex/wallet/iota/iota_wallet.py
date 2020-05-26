import os
from abc import ABCMeta

from iota.transaction import ProposedTransaction
from iota.types import Address

from anydex.wallet.wallet import Wallet
from iota.crypto.types import Seed
from ipv8.util import fail, succeed

from wallet.cryptocurrency import Cryptocurrency
from wallet.iota.iota_database import initialize_db, DatabaseSeed, DatabaseTransaction, DatabaseBundle, DatabaseAddress
from wallet.iota.iota_provider import IotaProvider


class AbstractIotaWallet(Wallet, metaclass=ABCMeta):

    def __init__(self, db_path, testnet, node):
        super().__init__()
        self.seed = None
        self.address = None
        self.provider = None
        self.node = node
        self.network = 'iota_testnet' if testnet else 'iota'
        self.wallet_name = 'iota testnet' if testnet else 'iota'
        self.database = initialize_db(os.path.join(db_path, 'iota.db'))
        self.testnet = testnet
        self.created = self.wallet_exists()

    def get_address(self):
        """
        Returns a non-spent address: either old one from the database or generates a new one
        :return: a non-spent address
        """
        # fetch all non-spent transactions from the database
        address_query = self.database.query(DatabaseAddress)
        non_spent = address_query.filter(DatabaseAddress.is_spent.is_(False)).all()

        # update the database: check whether any of non-spent addresses became spent
        for address in non_spent:
            if self.provider.is_spent(address):
                address_query.filter(DatabaseAddress.address == address.address).update({
                    DatabaseAddress.is_spent: True,
                })
        self.database.commit()

        # if any non spent addresses left in the database, return first one
        non_spent = self.database.query(DatabaseAddress).filter(not DatabaseAddress.is_spent).all()
        if non_spent.len() > 0:
            return non_spent[0]

        # otherwise generate a new one with the new index
        spent_count = self.database.query(DatabaseAddress).count()
        address = self.provider.generate_address(index=spent_count)

        # generating address with checksum and fetching seed's id
        address_with_checksum = address.with_valid_checksum()
        seed_id = self.database.query(DatabaseSeed).filter(DatabaseSeed.seed == self.seed.as_string).one()
        # store address in the database
        self.database.add(DatabaseAddress(
            address=address_with_checksum,
            seed_id=seed_id,
        ))

        return address

    def get_seed(self):
        """
        Returns the seed of the wallet or raises an exception if no seed exists
        :return: the seed
        """
        if not self.created:
            raise Exception('Wallet not created!')

        if self.seed is None:
            raise Exception('Wallet created, seed missing!')

        return self.seed

    def wallet_exists(self) -> bool:
        """
        Checks whether the wallet has been created or not
        :return: boolean
        """
        query = self.database.query(DatabaseSeed)
        wallet_count = query.filter(DatabaseSeed.name == self.wallet_name).count()

        # return self.database.query(exists().where(DatabaseSeed.name == self.wallet_name)).scalar() ???
        return wallet_count > 0

    def create_wallet(self):
        if self.created:
            return fail(RuntimeError(f'IOTA wallet with name {self.wallet_name} already exists.'))

        # generate random seed and store it in the database as a String instead of TryteString
        self.seed = Seed.random()
        self.database.add(DatabaseSeed(name=self.wallet_name, seed=self.seed.as_string()))
        self.database.commit()

        # initialize connection with API through the provider and get an active non-spent address
        self.provider = IotaProvider(self.testnet)
        self.provider.initialize_api(self.seed)
        self.address = self.get_address()
        self.created = True

    def transfer(self, value, address):
        # generate and send a transaction
        transaction = ProposedTransaction(
            address=Address(address),
            value=value
        )
        bundle = self.provider.submit_transaction(transaction)

        # store bundle in the database
        self.database.add(DatabaseBundle(
            hash=bundle.hash,
            count=bundle.transactions.len(),
            is_pending=False
        ))

        # fetch seed_id and bundle_id for storing transaction
        seed_id = self.database.query(DatabaseSeed).filter(DatabaseSeed.seed == self.seed.as_string).one()
        bundle_id = self.database.query(DatabaseBundle).filter(DatabaseBundle.hash == bundle.hash).one()

        # store all the transactions from the bundle in the database
        for tx in bundle.transactions:
            self.database.add(DatabaseTransaction(
                seed_id=seed_id,
                address=tx.address,
                value=tx.value,
                hash=tx.hash,
                msg_sig=tx.signature_message_fragment,
                current_index=tx.current_index,
                date_time=tx.timestamp,
                is_pending=(not tx.is_confirmed),
                bundle_id=bundle_id
            ))
            # if sending address, mark it as spent in the database
            if tx.value < 0:
                address_query = self.database.query(DatabaseAddress)
                address_query.filter(DatabaseAddress.address == tx.address).update({
                    DatabaseAddress.is_spent: True,
                })

        self.database.commit()

    def get_balance(self):
        if not self.created:
            return succeed({'available': 0, 'pending': 0, 'currency': 'IOTA', 'precision': self.precision()})

        # if wallet created, fetch needed data
        return succeed({
            'available': self.provider.get_balance(),
            'pending': self.provider.get_pending(),
            'currency': 'IOTA',
            'precision': self.precision()
        })

    def get_transactions(self):
        return self.provider.get_transactions()

    def is_testnet(self):
        return self.testnet

    def precision(self):
        return 6    # or 1, depends if we decide to trade 1 Million IOTAs or 1 IOTA

    def min_unit(self):
        return 0    # valueless and feeless transactions are possible


class IotaWallet(AbstractIotaWallet, metaclass=ABCMeta):
    def __init__(self, db_path, node=None):
        super(IotaWallet, self).__init__(db_path, False, node)

    def get_name(self):
        return Cryptocurrency.IOTA.value

    def get_identifier(self):
        return 'IOTA'  # or MIOTA, depends if we decide to trade 1 Million IOTAs or 1 IOTA


class IotaTestnetWallet(AbstractIotaWallet, metaclass=ABCMeta):
    def __init__(self, db_path, node=None):
        super(IotaTestnetWallet, self).__init__(db_path, True, node)

    def get_name(self):
        return 'Testnet IOTA'

    def get_identifier(self):
        return 'TIOTA'  # or TMIOTA, depends if we decide to trade 1 Million IOTAs or 1 IOTA

