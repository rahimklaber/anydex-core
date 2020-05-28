import os

from ipv8.util import fail
from stellar_sdk import Keypair

from wallet.cryptocurrency import Cryptocurrency
from wallet.stellar.xlm_db import initialize_db, Secret
from wallet.wallet import Wallet


class StellarWallet(Wallet):
    """
    Wallet provider support for the native stellar token: lumen.
    """
    TESTNET = False

    def __init__(self, db_path, provider=None):

        super().__init__()

        self.network = 'testnet' if self.TESTNET else Cryptocurrency.STELLAR.value
        self.min_confirmations = 0
        self.unlocked = True
        self._session = initialize_db(os.path.join(db_path, 'stellar.db'))
        self.wallet_name = 'stellar_tribler_testnet' if self.TESTNET else 'stellar_tribler'

        row = self._session.query(Secret).filter(Secret.name == self.wallet_name).first()
        if row:
            self.keypair = Keypair.from_secret(row.secret)
            self.created = True

    def get_identifier(self):
        pass

    def get_name(self):
        return Cryptocurrency.STELLAR.value

    def create_wallet(self):
        if self.created:
            return fail(RuntimeError(f'Stellar wallet with name {self.wallet_name} already exists'))

        self._logger.info(f'Creating Stellar wallet with name {self.wallet_name}')
        keypair = Keypair.random()
        self.keypair = keypair
        self.created = True
        self._session.add(Secret(name=self.wallet_name, secret=keypair.secret, address=keypair.public_key))
        self._session.commit()

    def get_balance(self):
        pass

    async def transfer(self, *args, **kwargs):
        pass

    def get_address(self):
        pass

    def get_transactions(self):
        pass

    def min_unit(self):
        pass

    def precision(self):
        pass

    def monitor_transaction(self, txid):
        pass
