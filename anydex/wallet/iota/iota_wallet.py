import os
from abc import ABCMeta
from asyncio import Future

from iota.transaction import ProposedTransaction
from iota.types import Address
from iota.crypto.types import Seed

from anydex.wallet.wallet import Wallet
from ipv8.util import succeed

from wallet.cryptocurrency import Cryptocurrency
from wallet.iota.iota_database import initialize_db, DatabaseSeed, DatabaseTransaction, DatabaseBundle, DatabaseAddress
from wallet.iota.iota_provider import IotaProvider


class AbstractIotaWallet(Wallet, metaclass=ABCMeta):

    def __init__(self, db_path, testnet, node):
        super().__init__()
        self.seed = None
        self.provider = None
        self.node = node
        self.testnet = testnet
        self.network = 'iota_testnet' if testnet else 'iota'
        self.wallet_name = 'iota testnet' if testnet else 'iota'
        self.database = initialize_db(os.path.join(db_path, 'iota.db'))
        self.created = self.wallet_exists()

    def create_wallet(self):
        if self.created:
            raise Exception(f'IOTA wallet with name {self.wallet_name} already exists.')

        # generate random seed and store it in the database as a String instead of TryteString
        self.seed = Seed.random()
        self.database.add(DatabaseSeed(name=self.wallet_name, seed=self.seed.as_string()))
        self.database.commit()

        # initialize connection with API through the provider and get an active non-spent address
        self.provider = IotaProvider(self.testnet)
        self.provider.initialize_api(self.seed)
        self.created = True

    def wallet_exists(self) -> bool:
        """
        Checks whether the wallet has been created or not
        :return: boolean
        """
        query = self.database.query(DatabaseSeed)
        wallet_count = query.filter(DatabaseSeed.name.__eq__(self.wallet_name)).count()

        # return self.database.query(exists().where(DatabaseSeed.name == self.wallet_name)).scalar() ???
        return wallet_count > 0

    def get_address(self):
        """
        Returns a non-spent address: either old one from the database or a newly generated one
        :return: a non-spent address
        """
        # fetch all non-spent transactions from the database
        address_query = self.database.query(DatabaseAddress)
        non_spent = address_query.filter(DatabaseAddress.is_spent.is_(False)).all()

        # update the database: check whether any of non-spent addresses became spent
        for address in non_spent:
            if self.provider.is_spent(address):
                address_query.filter(DatabaseAddress.address.__eq__(address.address)).update({
                    DatabaseAddress.is_spent: True,
                })
        self.database.commit()

        # if any non spent addresses left in the database, return first one
        non_spent = self.database.query(DatabaseAddress).filter(DatabaseAddress.is_spent.is_(False)).all()
        if non_spent.len() > 0:
            return non_spent[0]

        # otherwise generate a new one with the new index
        spent_count = self.database.query(DatabaseAddress).count()
        address = self.provider.generate_address(index=spent_count)

        # generating address with checksum and fetching seed's id
        address_with_checksum = address.with_valid_checksum()
        seed_id = self.database.query(DatabaseSeed).filter(DatabaseSeed.seed.__eq__(self.seed.as_string)).one()
        # store address in the database
        self.database.add(DatabaseAddress(
            address=address_with_checksum,
            seed_id=seed_id,
        ))

        return address

    async def transfer(self, value, address):
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

        # store bundle transactions in the database
        self.update_transactions_database(bundle.transactions)
        self.database.commit()

    def get_balance(self):
        if not self.created:
            return succeed({'available': 0, 'pending': 0, 'currency': 'IOTA', 'precision': self.precision()})

        # if wallet created, fetch needed data
        return succeed({
            'available': self.provider.get_seed_balance(),
            'pending': self.get_pending(),
            'currency': 'IOTA',
            'precision': self.precision()
        })

    def get_pending(self):
        """
        Get the pending balance of the given seed
        :return: the balance
        """
        transactions = self.provider.get_seed_transactions()
        pending_balance = 0

        # iterate through transaction and check whether they are confirmed
        for tx in transactions:
            query = self.database.query(DatabaseBundle).filter(DatabaseAddress.address.__eq__(tx.address)).all()
            # return self.database.query(exists().where(DatabaseAddress.address == tx.address)).scalar() ???
            if not tx.is_confirmed and query.len() > 0:
                pending_balance += tx.value

        return pending_balance

    def get_transactions(self):
        transactions = self.provider.get_seed_transactions()
        self.update_transactions_database(transactions)
        return transactions

    def monitor_transaction(self, txid):
        """
        Monitor a given transaction ID. Returns a Deferred that fires when the transaction is present.
        """
        monitor_future = Future()

        async def monitor():
            transactions = await self.get_transactions()
            for transaction in transactions:
                if transaction.hash == txid:
                    self._logger.debug("Found transaction with id %s", txid)
                    monitor_future.set_result(None)
                    monitor_task.cancel()

        self._logger.debug("Start polling for transaction %s", txid)
        monitor_task = self.register_task(f"{self.network}_poll_{txid}", monitor, interval=5)

        return monitor_future

    def update_transactions_database(self, transactions):
        # store all the transactions in the database
        for tx in transactions:
            # if transaction already exists in the database, update it
            database_transactions = self.database.query(DatabaseTransaction)
            query = database_transactions.filter(DatabaseTransaction.hash.__eq__(tx.hash))
            if query.all().len() > 0:
                query.update({
                    DatabaseTransaction.is_pending: tx.is_confirmed,
                })
            # if no transaction in the database, create it
            else:
                self.database.add(DatabaseTransaction(
                    seed=self.seed,
                    address=tx.address,
                    value=tx.value,
                    hash=tx.hash,
                    msg_sig=tx.signature_message_fragment,
                    current_index=tx.current_index,
                    date_time=tx.timestamp,
                    bundle_id=tx.bundle_hash
                ))
                # if sending from an address, mark it as spent in the database
                if tx.value <= 0:
                    address_query = self.database.query(DatabaseAddress)
                    address_query.filter(DatabaseAddress.address.__eq__(tx.address)).update({
                        DatabaseAddress.is_spent: True,
                    })

        self.database.commit()

    def is_testnet(self):
        return self.testnet

    def precision(self):
        return 6  # or 1, depends if we decide to trade 1 Million IOTAs or 1 IOTA

    def min_unit(self):
        return 0  # valueless and feeless transactions are possible


class IotaWallet(AbstractIotaWallet):
    def __init__(self, db_path, node=None):
        super(IotaWallet, self).__init__(db_path, False, node)

    def get_name(self):
        return Cryptocurrency.IOTA.value

    def get_identifier(self):
        return 'IOTA'  # or MIOTA, depends if we decide to trade 1 Million IOTAs or 1 IOTA


class IotaTestnetWallet(AbstractIotaWallet):
    def __init__(self, db_path, node=None):
        super(IotaTestnetWallet, self).__init__(db_path, True, node)

    def get_name(self):
        return 'Testnet IOTA'

    def get_identifier(self):
        return 'TIOTA'  # or TMIOTA, depends if we decide to trade 1 Million IOTAs or 1 IOTA
