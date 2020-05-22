import abc
from abc import ABCMeta

from iota.transaction import ProposedTransaction
from iota.types import Address

from anydex.wallet.wallet import Wallet
from iota.crypto.types import Seed
from ipv8.util import fail, succeed


class AbstractIotaWallet(Wallet, metaclass=abc.ABCMeta):

    def __init__(self, provider, db_path, wallet_name, network, testnet):
        super().__init__()
        self.provider = provider
        self.network = network
        self.wallet_name = wallet_name
        self.directory = db_path
        self.testnet = testnet
        self.created = self.wallet_initialized()
        self.seed = None

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
            return fail(RuntimeError(f"IOTA wallet with name {self.wallet_name} already exists."))

        # TODO create database
        self.seed = Seed.random()
        # TODO store seed in database!
        self.provider.initialize_api()
        # TODO store current address in database for the num_of_addresses function
        self.created = True

    def transfer(self, amount, address):
        tx = ProposedTransaction(
            address=Address(address),
            value=amount
        )
        self.provider.submit_transaction(tx)

    def precision(self):
        return 6    # Exchanges generally trade MIOTAs or 1 Million IOTAs

    def min_unit(self):
        return 0    # Valueless and feeless transactions are possible

    def get_balance(self):
        if not self.created:
            return succeed({'available': 0, 'pending': 0, 'currency': 'MIOTA', 'precision': self.precision()})

        return succeed({
            'available': self.provider.get_balance(),
            'pending': self.provider.get_pending(self.seed),
            'currency': 'MIOTA',
            'precision': self.precision()
        })

    def is_testnet(self):
        return self.testnet


class IotaWallet(AbstractIotaWallet, metaclass=ABCMeta):
    pass


class IotaTestnetWallet(AbstractIotaWallet, metaclass=ABCMeta):
    # TODO pick tesnet
    pass

