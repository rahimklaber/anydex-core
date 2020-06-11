import os
import re
from abc import ABCMeta
from asyncio import Future

from iota.crypto.types import Seed
from iota.transaction import ProposedTransaction
from iota.types import Address
from ipv8.util import succeed, fail
from sqlalchemy import exists

from anydex.wallet.cryptocurrency import Cryptocurrency
from anydex.wallet.iota.iota_database import initialize_db, \
    DatabaseSeed, DatabaseTransaction, DatabaseBundle, DatabaseAddress
from anydex.wallet.iota.iota_provider import IotaProvider
from anydex.wallet.wallet import Wallet, InsufficientFunds


class AbstractIotaWallet(Wallet, metaclass=ABCMeta):

    def __init__(self, db_path, testnet, node):
        super().__init__()

        self.name = 'Iota Test Network' if testnet else 'Iota Network'
        self.network = 'iota_testnet' if testnet else 'iota'
        self.wallet_name = f'tribler_testnet_{self.network}' if testnet else f'tribler_{self.network}'
        self.testnet = testnet
        self.unlocked = True

        self.node = node
        self.seed = None
        self.provider = None
        self.database = initialize_db(os.path.join(db_path, 'iota.db'))
        self.created = self.wallet_exists()

        if self.created:
            db_seed = self.database.query(DatabaseSeed) \
                .filter(DatabaseSeed.name.__eq__(self.wallet_name)) \
                .one()
            self.seed = Seed(db_seed.seed)
            self.provider = IotaProvider(testnet=self.testnet, seed=self.seed)

    def create_wallet(self):
        """
        Create wallet by creating seed, storing it and setting up API access
        """
        if self.created:
            return fail(RuntimeError(f'Iota wallet with name {self.wallet_name} already exists.'))

        self._logger.info(f'Creating Iota wallet with name {self.wallet_name}')

        # generate random seed and store it in the database as a String instead of TryteString
        self.seed = Seed.random()
        self.database.add(DatabaseSeed(name=self.wallet_name, seed=self.seed.__str__()))
        self.database.commit()

        # initialize connection with API through the provider and get an active non-spent address
        self.provider = IotaProvider(testnet=self.testnet, seed=self.seed)
        self.created = True
        return succeed([])

    def wallet_exists(self) -> bool:
        """
        Check whether the wallet has been created or not
        :return: boolean
        """
        return self.database.query(exists().where(DatabaseSeed.name == self.wallet_name)).scalar()

    async def get_address(self):
        """
        Return a non-spent address: either old one from the database or a newly generated one
        :return: a non-spent address
        """
        if not self.created:
            return []
        # fetch all non-spent transactions from the database
        address_query = self.database.query(DatabaseAddress)
        non_spent = address_query.filter(DatabaseAddress.is_spent.is_(False)).all()

        # update the database: check whether any of non-spent addresses became spent
        for address in non_spent:
            if await self.provider.is_spent(Address(address.address)):
                address_query.filter(DatabaseAddress.address.__eq__(address.address)).update({
                    DatabaseAddress.is_spent: True,
                })
        self.database.commit()
        # if any non spent addresses left in the database, return first one
        non_spent = self.database.query(DatabaseAddress) \
            .filter(DatabaseAddress.is_spent.is_(False)) \
            .all()

        if len(non_spent) > 0:
            return non_spent[0].address
        # otherwise generate a new one with the new index and append checksum to it
        spent_count = self.database.query(DatabaseAddress).count()
        address = await self.provider.generate_address(index=2*spent_count)

        # store address in the database
        self.database.add(DatabaseAddress(
            address=address.__str__(),
            seed=self.seed.__str__(),
        ))
        return address.__str__()

    async def transfer(self, value: int, address: str):
        """
        Transfer specified value to a specified address and store the bundle and the transactions
        :param value: amount of IOTA tokens to be sent
        :param address: receiving address of the IOTA tokens
        """
        value = int(value)
        if not self.created:
            return RuntimeError('The wallet must be created transfers can be made')

        if value < 0:
            return RuntimeError('Negative value transfers are not allowed.')

        # The pyota library has no support for address validation
        if not re.compile('^[A-Z9]{81}|[A-Z9]{90}$').match(address):
            return RuntimeError('Invalid IOTA address')

        # Get wallet balance
        balance = await self.get_balance()

        if balance['available'] < value:
            return InsufficientFunds(f'Balance {balance["available"]} of the wallet is less than {value}.')

        # generate and send a transaction
        transaction = ProposedTransaction(
            address=Address(address),
            value=value
        )

        # Submit the transaction to the tangle
        self._logger.info(f"Creating {self.network} payment with amount {value} to address {address}")
        bundle = await self.provider.submit_transaction(transaction)

        # Return bundle hash ID instead of transaction ID
        return bundle.hash.__str__()

    async def get_balance(self):
        """
        Fetch the balance of the wallet: of all addresses specified for the seed
        :return: available balance, pending balance, currency, precision
        """
        if not self.created:
            return {
                'available': 0,
                'pending': 0,
                'currency': self.get_identifier(),
                'precision': self.precision()
            }

        # update bundles and transactions database
        await self.update_bundles_database()
        await self.update_transactions_database()

        # fetch available and pending balance
        available = await self.provider.get_seed_balance()
        pending = await self.get_pending()

        return {
            'available': available,
            'pending': pending,
            'currency': self.get_identifier(),
            'precision': self.precision()
        }

    async def get_pending(self):
        """
        Get the pending balance of the given seed
        :return: the pending balance
        """
        if not self.created:
            return 0

        # fetch pending transactions from the database
        pending_transactions = self.database.query(DatabaseTransaction) \
            .filter(DatabaseTransaction.seed.__eq__(self.seed.__str__())) \
            .filter(DatabaseTransaction.is_confirmed.is_(False)) \
            .all()

        # add up values of all the pending transactions
        pending_balance = sum([tx.value for tx in pending_transactions])

        return pending_balance

    async def get_transactions(self):
        """
        Fetch the transactions related to the seed through the API and store them
        :return:
        """
        if not self.created:
            return []

        # update bundles and transactions database
        await self.update_bundles_database()
        await self.update_transactions_database()

        # get all transactions of this seed
        db_seed_transactions = self.database.query(DatabaseTransaction) \
            .filter(DatabaseTransaction.seed.__eq__(self.seed.__str__())) \
            .all()
        db_addresses = self.database.query(DatabaseAddress).all()
        seed_addresses = [ad.address for ad in db_addresses]

        transactions = []
        for db_tx in db_seed_transactions:
            transactions.append({
                'hash': db_tx.hash,
                'outgoing': db_tx.address in seed_addresses,
                'address': db_tx.address,
                'amount': db_tx.value,
                'currency': self.get_identifier(),
                'timestamp': db_tx.timestamp,
                'bundle': db_tx.bundle_hash,
                'is_confirmed': db_tx.is_confirmed
            })

        return transactions

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
                if transaction['hash'].__eq__(txid):
                    self._logger.debug('Found transaction with id %s', txid)
                    monitor_future.set_result(None)
                    monitor_task.cancel()

        self._logger.debug('Start polling for transaction %s', txid)
        monitor_task = self.register_task(f'{self.name}_poll_{txid}', monitor, interval=5)

        return monitor_future

    async def update_bundles_database(self):
        """
        Update the bundles database
        """
        # get all tangle and database bundles
        tangle_bundles = await self.provider.get_all_bundles()
        db_bundles = self.database.query(DatabaseBundle).all()
        db_bundle_hashes = [bundle.hash for bundle in db_bundles]

        # insert/update bundles
        for bundle in tangle_bundles:
            if bundle.hash.__str__() not in db_bundle_hashes:
                self.database.add(DatabaseBundle(
                    hash=bundle.hash.__str__(),
                    tail_transaction_hash=bundle.tail_transaction.hash.__str__(),
                    count=len(bundle.transactions)
                ))
            else:
                bundle_tail_tx_hash = bundle.tail_transaction.hash.__str__()
                confirmation_check = await self.provider.get_confirmations(bundle_tail_tx_hash)
                self.database.query(DatabaseBundle) \
                    .filter(DatabaseBundle.hash.__eq__(bundle.hash.__str__())) \
                    .update({DatabaseBundle.is_confirmed: confirmation_check})

        self.database.commit()

    async def update_transactions_database(self):
        """
        Update the transactions database and spent addresses list
        """
        # get all tangle and database transactions
        tangle_transactions = await self.provider.get_seed_transactions()
        db_txs = self.database.query(DatabaseTransaction).all()
        db_txs_hashes = [tx.hash for tx in db_txs]

        # insert/update transactions
        for tx in tangle_transactions:
            if tx.hash.__str__() not in db_txs_hashes:
                self.database.add(DatabaseTransaction(
                    seed=self.seed.__str__(),
                    address=tx.address.__str__(),
                    value=tx.value,
                    hash=tx.hash.__str__(),
                    msg_sig=tx.signature_message_fragment.__str__(),
                    current_index=tx.current_index,
                    timestamp=tx.timestamp,
                    bundle_hash=tx.bundle_hash.__str__(),
                    is_confirmed=tx.is_confirmed
                ))
                # if sending from an address, mark it as spent in the database
                if tx.value <= 0:
                    self.database.query(DatabaseAddress) \
                        .filter(DatabaseAddress.address.__eq__(tx.address.__str__())) \
                        .update({DatabaseAddress.is_spent: True})
            else:
                confirmation_check = await self.provider.get_confirmations(tx.hash.__str__())
                self.database.query(DatabaseTransaction) \
                    .filter(DatabaseTransaction.hash.__eq__(tx.hash.__str__())) \
                    .update({DatabaseTransaction.is_confirmed: confirmation_check})

        self.database.commit()

    def is_testnet(self):
        return self.testnet

    def precision(self):
        return 0  # 6 if MIOTAs

    def min_unit(self):
        return 0  # valueless and feeless transactions are possible


class IotaWallet(AbstractIotaWallet):
    def __init__(self, db_path, node=None):
        super(IotaWallet, self).__init__(db_path, False, node)

    def get_identifier(self):
        return 'IOTA'

    def get_name(self):
        return Cryptocurrency.IOTA.value


class IotaTestnetWallet(AbstractIotaWallet):
    def __init__(self, db_path, node=None):
        super(IotaTestnetWallet, self).__init__(db_path, True, node)

    def get_identifier(self):
        return 'TIOTA'

    def get_name(self):
        return 'Testnet IOTA'
