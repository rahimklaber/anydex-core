from ipv8.util import fail, succeed

from anydex.wallet.cryptocurrency import Cryptocurrency
from anydex.wallet.wallet import Wallet, InsufficientFunds


class MoneroWallet(Wallet):
    """
    This class is responsible for handling your Monero wallet.
    The class operates on the Monero wallet connected to the `monero-wallet-rpc` server.
    A Tribler specific account is created in the wallet, storing its address in database.
    Anytime AnyDEX is started up, the address is retrieved to select the appropriate account.
    """
    TESTNET = False

    def __init__(self, provider):
        super().__init__()
        self.provider = provider

        self.network = 'testnet' if self.TESTNET else Cryptocurrency.MONERO.value
        self.min_confirmations = 0
        self.unlocked = True
        self.wallet_name = 'tribler_testnet' if self.TESTNET else 'tribler'

        # TODO create account if does not exist yet
        row = None
        if row:
            self.account = ''
            self.created = True
        else:
            self.account = None

    def get_name(self):
        return Cryptocurrency.MONERO.value

    def create_wallet(self):
        """
        Creates Tribler-specific account in existing Monero wallet.
        If account address is not found in database, create account.
        """
        if self.account:
            return fail(RuntimeError(f'Account with name {self.wallet_name} already exists in Monero wallet'))

        self._logger.info(f'Creating acount with name {self.wallet_name} in Monero wallet')
        if not self.account:
            self.account = self.provider.wallet.new_account()
            self.created = True

            # TODO store address in database as account
            await store_address(self.account.address)

        return succeed(None)

    def get_balance(self):
        if not self.account:
            return succeed({
                'available': 0,
                'pending': 0,
                'currency': 'XMR',
                'precision': self.precision()
            })
        return succeed(self.provider.get_balance(self.get_address()))

    async def transfer(self, amount, address) -> str:
        """
        Transfer Monero to another wallet.
        If the amount exceeds the available balance, an `InsufficientFunds` exception is raised.

        :param amount: the transfer amount
        :param address: the receiver address
        :return: transfer hash
        """
        pass

    def get_address(self):
        if not self.account:
            return ''
        return self.account.address

    def get_transactions(self):
        # TODO return transactions matching given hashes
        if self.provider.blockchain_connection_alive():
            transactions = self.provider.blockchain.transactions([])
            return transactions
        else:
            # TODO re-establish blockchain_connection
            return

    def min_unit(self):
        # atomic unit: single piconero
        return 1

    def precision(self):
        return 12

    def get_identifier(self):
        return 'XMR'

    def update_database(self, transactions):
        pass


async def store_address(address: str):
    # TODO ensure async
    pass


class MoneroTestnetWallet(MoneroWallet):
    """
    This wallet represents testnet Monero.
    """
    TESTNET = True

    def get_name(self):
        return 'Testnet XMR'

    def get_identifier(self):
        return 'TXMR'
