import os
import re
from abc import ABCMeta
from asyncio import Future

from iota.transaction import ProposedTransaction
from iota.types import Address
from iota.crypto.types import Seed

from anydex.wallet.wallet import Wallet, InsufficientFunds
from ipv8.util import succeed, fail

from anydex.wallet.cryptocurrency import Cryptocurrency
from anydex.wallet.iota.iota_database import initialize_db, DatabaseSeed, DatabaseTransaction, DatabaseBundle, \
    DatabaseAddress
from anydex.wallet.iota.iota_provider import IotaProvider


class AbstractIotaWallet(Wallet, metaclass=ABCMeta):

    def __init__(self, db_path, testnet, node):
        super().__init__()
        self.node = node
        self.testnet = testnet
        self.network = 'iota_testnet' if testnet else 'iota'
        self.wallet_name = 'iota testnet' if testnet else 'iota'
        self.database = initialize_db(os.path.join(db_path, 'iota.db'))
        self.created = self.wallet_exists()

        if self.created:
            db_seed = self.database.query(DatabaseSeed) \
                .filter(DatabaseSeed.name.__eq__(self.wallet_name)) \
                .one()
            self.seed = Seed(db_seed.seed)
            self.provider = IotaProvider(testnet=self.testnet, seed=self.seed)
        else:
            self.seed = None
            self.provider = None

    def create_wallet(self):
        """
        Create wallet by creating seed, storing it and setting up API access
        """
        if self.created:
            return fail(RuntimeError(f'IOTA wallet with name {self.wallet_name} already exists.'))

        # generate random seed and store it in the database as a String instead of TryteString
        self.seed = Seed.random()
        self.database.add(DatabaseSeed(name=self.wallet_name, seed=self.seed.__str__()))
        self.database.commit()

        # initialize connection with API through the provider and get an active non-spent address
        self.provider = IotaProvider(testnet=self.testnet, seed=self.seed)
        self.created = True

    def wallet_exists(self) -> bool:
        """
        Check whether the wallet has been created or not
        :return: boolean
        """
        wallet_count = self.database.query(DatabaseSeed) \
            .filter(DatabaseSeed.name.__eq__(self.wallet_name)) \
            .count()

        # TODO: return self.database.query(exists().where(DatabaseSeed.name == self.wallet_name)).scalar()
        return wallet_count > 0

    def get_address(self):
        """
        Return a non-spent address: either old one from the database or a newly generated one
        :return: a non-spent address
        """
        if not self.created:
            return succeed([])
        # fetch all non-spent transactions from the database
        address_query = self.database.query(DatabaseAddress)
        non_spent = address_query.filter(DatabaseAddress.is_spent.is_(False)).all()

        # update the database: check whether any of non-spent addresses became spent
        for address in non_spent:
            if self.provider.is_spent(address):
                address_query.filter(DatabaseAddress.address.__eq__(address.address.__str__())).update({
                    DatabaseAddress.is_spent: True,
                })
        self.database.commit()

        # if any non spent addresses left in the database, return first one
        non_spent = self.database.query(DatabaseAddress) \
            .filter(DatabaseAddress.seed.__eq__(self.seed.__str__())) \
            .filter(DatabaseAddress.is_spent.is_(False)) \
            .all()

        if len(non_spent) > 0:
            return non_spent[0]

        # otherwise generate a new one with the new index and append checksum to it
        spent_count = self.database.query(DatabaseAddress).count()
        address = self.provider.generate_address(index=spent_count)
        address_with_checksum = address.with_valid_checksum()

        # store address in the database
        self.database.add(DatabaseAddress(
            address=address_with_checksum.__str__(),
            seed=self.seed.__str__(),
        ))

        return address

    async def transfer(self, value: int, address: str):
        """
        Transfer specified value to a specified address and store the bundle and the transactions
        :param value: amount of IOTA tokens to be sent
        :param address: receiving address of the IOTA tokens
        """
        if not self.created:
            return fail(RuntimeError('The wallet must be created transfers can be made'))

        if value < 0:
            return fail(RuntimeError('Negative value transfers are not allowed.'))

        # The pyota library has no support for address validation
        if not re.compile('^[A-Z9]{81}|[A-Z9]{90}$').match(address):
            return fail(RuntimeError('Invalid IOTA address'))

        balance = self.get_balance().result()

        if balance['available'] < value:
            return fail(InsufficientFunds(
                "Balance %d of the wallet is less than %d", balance['available'], int(value)))

        # generate and send a transaction
        transaction = ProposedTransaction(
            address=Address(address),
            value=value
        )
        bundle = self.provider.submit_transaction(transaction)

        # store bundle and its transactions in the database
        self.update_bundles_database([bundle])
        self.update_transactions_database(bundle.transactions)

        return succeed(bundle)

    def get_balance(self):
        """
        Fetch the balance of the wallet: of all addresses specified for the seed
        :return: available balance, pending balance, currency, precision
        """
        if not self.created:
            return succeed({
                'available': 0,
                'pending': 0,
                'currency': 'IOTA',
                'precision': self.precision()
            })

        # update transactions and bundles database
        transactions = self.provider.get_seed_transactions()
        self.update_transactions_database(transactions)
        self.update_bundles_database()

        response = succeed({
            'available': self.provider.get_seed_balance(),
            'pending': self.get_pending(),
            'currency': 'IOTA',
            'precision': self.precision()
        })

        return response

    def get_pending(self):
        """
        Get the pending balance of the given seed
        :return: the pending balance
        """
        if not self.create_wallet():
            return 0

        # Get all transactions from the seed
        tangle_transactions = self.provider.get_seed_transactions()
        self.update_transactions_database(tangle_transactions)
        self.update_bundles_database()

        database_transactions = self.database.query(DatabaseTransaction) \
            .filter(DatabaseTransaction.seed.__eq__(self.seed.__str__())) \
            .all()

        # iterate through transaction and check whether they are confirmed
        pending_balance = 0
        for tx in database_transactions:
            if not tx.is_confirmed:
                pending_balance += tx.value

        return pending_balance

    def get_transactions(self):
        """
        Fetch the transactions related to the seed through the API and store them
        :return:
        """
        if not self.created:
            return succeed([])
        # Get transactions from the tangle
        transactions_from_node = self.provider.get_seed_transactions()
        # Update the database transactions
        self.update_transactions_database(transactions_from_node)
        # Get the ID of the wallet seed
        # Get all transactions of this seed
        transactions_from_db = self.database.query(DatabaseTransaction) \
            .filter(DatabaseTransaction.seed.__eq__(self.seed.__str__())) \
            .all()

        transactions = []
        # Parse transactions
        for db_tx in transactions_from_db:
            transactions.append({
                'hash': db_tx.hash,
                'outgoing': db_tx.address in self.database.query(DatabaseAddress)
                        .filter(DatabaseAddress.seed == self.seed.__str__())
                        .all(),
                'address': db_tx.address,
                'amount': db_tx.value,
                'currency': self.get_identifier(),
                'timestamp': db_tx.timestamp,
                'bundle': db_tx.bundle_hash
            })
        return succeed(transactions)

    def monitor_transaction(self, txid):
        """
        Monitor a given transaction ID
        :param txid: hash of a transaction that should be monitored
        :return: Deferred that fires when the transaction is present
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

    def update_bundles_database(self, bundles=None):
        """
        Update the database by updating bundle list
        :param bundles: bundle to be stored
        """
        # Get all unconfirmed bundles
        pending_bundles = self.database.query(DatabaseBundle) \
            .filter(DatabaseBundle.is_confirmed.is_(False)) \
            .all()

        # Get all tail transactions from the pending bundles
        tail_hashes = [bundle.tail_transaction_hash for bundle in pending_bundles]

        # Get all bundles from the tangle
        tangle_bundles = self.provider.get_bundles(tail_hashes)

        # Update pending bundles
        for bundle in tangle_bundles:
            self.database.query(DatabaseBundle) \
                .filter(DatabaseBundle.hash.__eq__(bundle.hash.__str__())) \
                .update({DatabaseBundle.is_confirmed: bundle.is_confirmed})

        all_bundles = self.database.query(DatabaseBundle) \
            .all()

        if bundles:
            for bundle in bundles:
                # If the bundle isn't already in the database
                if bundle not in all_bundles:
                    # store bundle in the database
                    self.database.add(DatabaseBundle(
                        hash=bundle.hash.__str__(),
                        tail_transaction_hash=bundle.tail_transaction.hash.__str__(),
                        count=len(bundle.transactions),
                        is_confirmed=bundle.is_confirmed
                    ))

        self.database.commit()

    def update_transactions_database(self, transactions):
        """
        Update the database by updating transaction list and spent addresses list
        :param transactions: transactions to be stored or updated in the database
        """
        # store all the transactions in the database
        for tx in transactions:
            # if transaction already exists in the database, update it
            query = self.database.query(DatabaseTransaction) \
                .filter(DatabaseTransaction.hash.__eq__(tx.hash.__str__())).all()
            if len(query) > 0:
                query.update({
                    DatabaseTransaction.is_confirmed: tx.is_confirmed,
                })
            # if no transaction in the database, create it
            else:
                self.database.add(DatabaseTransaction(
                    seed=self.seed.__str__(),
                    address=tx.address.__str__(),
                    value=tx.value,
                    hash=tx.hash.__str__(),
                    msg_sig=tx.signature_message_fragment.__str__(),
                    current_index=tx.current_index,
                    timestamp=tx.timestamp,
                    is_confirmed=tx.is_confirmed,
                    bundle=tx.bundle_hash.__str__()
                ))
                # if sending from an address, mark it as spent in the database
                if tx.value <= 0:
                    address_query = self.database.query(DatabaseAddress)
                    address_query.filter(DatabaseAddress.address.__eq__(tx.address.__str__())).update({
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
