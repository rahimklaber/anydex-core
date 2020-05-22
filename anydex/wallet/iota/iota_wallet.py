import abc

from anydex.wallet.wallet import Wallet
from iota.crypto.types import Seed
from ipv8.util import fail, succeed
from iota import Iota


class AbstractIotaWallet(Wallet, metaclass=abc.ABCMeta):

    def __init__(self, provider, db_path, wallet_name, network, testnet):
        super().__init__()
        self.provider = provider
        self.network = network
        self.wallet_name = wallet_name
        self.directory = db_path
        self.testnet = testnet
        self.created = self.wallet_initialized()
        self.seed = self.get_seed() if self.created else None
        self.api = self.initialize_api() if self.created else None

    def get_seed(self):
        """
        Returns the seed of the wallet or raises an exception if no seed exists
        :return: the seed
        """
        pass

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
        self.initialize_api()
        # TODO store current address in database for the num_of_addresses function
        self.created = True

    def initialize_api(self):
        """
        Initializes API instance with
        """
        if not self.created:
            return fail(RuntimeError(f'Cannot initialize API for unitiliazed wallet {self.wallet_name}'))
        # TODO get optimal node
        self.api = Iota('somenode', self.seed, testnet=self.testnet)

    def transfer(self, amount, address):
        pass
        # transfer
        # transfer
        # transfer

    def precision(self):
        return 6    # Exchanges generally trade MIOTAs or 1 Million IOTAs

    def min_unit(self):
        return 0    # Valueless and feeless transactions are possible

    def get_balance(self):
        pass

    def is_testnet(self):
        pass


class IotaWallet(AbstractIotaWallet):
    pass


class IotaTestnetWallet(AbstractIotaWallet):
    # TODO pick tesnet
    pass

