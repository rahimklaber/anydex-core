import os
from abc import ABCMeta

from iota.transaction import ProposedTransaction
from iota.types import Address

from anydex.wallet.wallet import Wallet
from iota.crypto.types import Seed
from ipv8.util import fail, succeed

from wallet.cryptocurrency import Cryptocurrency
from wallet.iota.iota_database import initialize_db, DatabaseSeed


class AbstractIotaWallet(Wallet, metaclass=ABCMeta):

    def __init__(self, provider, db_path, testnet):
        super().__init__()
        self.provider = provider
        self.network = 'iota_testnet' if testnet else 'iota'
        self.wallet_name = 'iota testnet' if testnet else 'iota'
        self.database = initialize_db(os.path.join(db_path, 'iota.db'))
        self.testnet = testnet
        self.created = self.wallet_initialized()
        self.seed = None
        self.address = None

    def get_address(self):
        address = ''
        # TODO: update status of all non-spent addresses in db with api.were_addresses_spent_from([sender])['states'][0]
        # TODO: check db for non-spent addresses
        # TODO: if no exist: generate a new address and check that it is not in the database
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

    def wallet_initialized(self) -> bool:
        """
        Checks whether the wallet has been created or not
        :return: boolean
        """
        # TODO implement database querying by wallet name
        pass

    def create_wallet(self):
        if self.created:
            return fail(RuntimeError(f'IOTA wallet with name {self.wallet_name} already exists.'))

        self.seed = Seed.random()
        self.database.add(DatabaseSeed(seed=self.seed.as_string()))
        self.provider.initialize_api()
        self.address = self.get_address()
        self.created = True

    def transfer(self, amount, address):
        tx = ProposedTransaction(
            address=Address(address),
            value=amount
        )
        self.provider.submit_transaction(tx)

    def get_balance(self):
        if not self.created:
            return succeed({'available': 0, 'pending': 0, 'currency': 'IOTA', 'precision': self.precision()})

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
    def __init__(self, provider, db_path):
        super(IotaWallet, self).__init__(provider, db_path, False)

    def get_name(self):
        return Cryptocurrency.IOTA.value

    def get_identifier(self):
        return 'IOTA'  # or MIOTA, depends if we decide to trade 1 Million IOTAs or 1 IOTA


class IotaTestnetWallet(AbstractIotaWallet, metaclass=ABCMeta):
    def __init__(self, provider, db_path):
        super(IotaTestnetWallet, self).__init__(provider, db_path, True)

    def get_name(self):
        return 'Testnet IOTA'

    def get_identifier(self):
        return 'TIOTA'  # or TMIOTA, depends if we decide to trade 1 Million IOTAs or 1 IOTA
