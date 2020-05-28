import os

from ipv8.util import fail, succeed
from stellar_sdk import Keypair

from wallet.cryptocurrency import Cryptocurrency
from wallet.stellar.xlm_db import initialize_db, Secret
from wallet.stellar.xlm_provider import StellarProvider
from wallet.wallet import Wallet


class StellarWallet(Wallet):
    """
    Wallet provider support for the native stellar token: lumen.
    """
    TESTNET = False

    def __init__(self, db_path, provider: StellarProvider = None):

        super().__init__()
        self.provider = provider
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
        return 'XLM'

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

        return succeed(None)

    def get_balance(self):

        if not self.created:
            return succeed({
                'available': 0,
                'pending': 0,
                'currency': 'XLM',
                'precision': self.precision()
            })
        xlm_balance = int(float(self.provider.get_balance(
            address=self.get_address())) * 1e7)  # balance is not in smallest denomination
        balance = {
            'available': xlm_balance,
            'pending': 0,
            'currency': 'XLM',
            'precision': self.precision()
        }
        return succeed(balance)

    async def transfer(self, *args, **kwargs):
        pass

    def get_address(self):
        if not self.created:
            return ''
        return self.keypair.public_key

    def get_transactions(self):
        """
        Transactions in stellar is different from etheruem or bitcoin.
        A payment in stellar is the same as a transactions in ethereum or bitcoin.
        Even though this method is called get_transactions (for compat with the wallet api) it returns the `payments`
        related to this wallet.
        :return: list of payments related to the wallet.
        """
        

    def min_unit(self):
        return 1

    def precision(self):
        return 7

    def monitor_transaction(self, txid):
        pass
