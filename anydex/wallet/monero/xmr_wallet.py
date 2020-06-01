import time
from decimal import Decimal

from ipv8.util import fail, succeed
from monero.backends.jsonrpc import JSONRPCWallet
from monero.transaction import OutgoingPayment, Payment
from monero.wallet import Wallet

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

    def __init__(self, host: str = '127.0.0.1', port: int = 18081):
        super().__init__()

        try:
            self._logger.info(f'Connect to wallet-rpc-server on {host} at {port}')
            self.wallet = Wallet(JSONRPCWallet(host=host, port=port))
        except ConnectionError as err:
            self._logger.error(f'Cannot connect to wallet-rpc-server on {host} at {port}: {err}')
            self.wallet = None

        self.network = 'testnet' if self.TESTNET else Cryptocurrency.MONERO.value
        self.min_confirmations = 0
        self.unlocked = True
        # set internal name, irrelevant with regards to actual wallet name
        self.wallet_name = 'tribler_testnet' if self.TESTNET else 'tribler'

    def _wallet_connection_alive(self) -> bool:
        """
        Verify connection to wallet is still alive.

        :return: True if alive, else False
        """
        try:
            self.wallet.refresh()
        except ConnectionError:
            return False
        return True

    def get_name(self):
        return Cryptocurrency.MONERO.value

    def create_wallet(self):
        """
        Anydex operates on existing wallet with corresponding `wallet-rpc-server`.
        """
        return fail(NotSupportedOperationException('Anydex is using `wallet-rpc-server` wallet'))

    def get_balance(self):
        """
        Return the balance in this wallet.
        Pending balance is the amount of newly-received XMR that cannot be spent yet.
        Locked balance turns into unlocked balance after 10 blocks.
        See: https://monero.stackexchange.com/questions/3262/whats-the-difference-between-balance-and-unlocked-balance

        :return: dictionary of available balance, pending balance, currency and precision.
        """
        unlocked_balance = self.wallet.balance(unlocked=True)
        total_balance = self.wallet.balance(unlocked=False)

        balance = {
            'available': unlocked_balance,
            'pending': total_balance - unlocked_balance,
            'currency': 'XMR',
            'precision': self.precision()
        }
        return succeed(balance)

    async def transfer(self, amount: float, address, **kwargs) -> str:
        """
        Transfer Monero to another wallet.
        If the amount exceeds the available balance, an `InsufficientFunds` exception is raised.

        :param kwargs:
            payment_id: str,
            priority: transaction priority, implies fee.
                The priority can be a number from 1 to 4 (unimportant, normal, elevated, priority).
                Default is 1.
            unlock_time: int, default is 0
        :param amount: the transfer amount
        :param address: the receiver address
        :return: transfer hash
        """
        balance = await self.get_balance()

        if balance['available'] < int(amount):
            return fail(InsufficientFunds('Insufficient funds found in Monero wallet'))

        self._logger.info(f'Transfer {amount} to {address}')
        transaction = self.wallet.transfer(address, Decimal(str(amount)), **kwargs)
        return transaction.hash

    async def transfer_multiple(self, transfers: list, **kwargs) -> list:
        """
        Submit multiple transfers simultaneously to the Monero blockchain.
        May reduce fee.

        :param transfers: list of tuples of format (address, Decimal(amount))
        :param kwargs: payment_id, priority, unlock_time (see `transfer` method above)
        :return: list of resulting hashes
        """
        balance = await self.get_balance()

        total_amount = sum([transfer[1] for transfer in transfers])

        if balance['available'] < total_amount:
            return fail(InsufficientFunds('Insufficient funds found in Monero wallet for all transfers'))

        if self._wallet_connection_alive():
            results = self.wallet.transfer_multiple(transfers, **kwargs)
            hashes = [result[0].hash for result in results]
            return succeed(hashes)
        return fail([])

    def get_address(self):
        return self.wallet.address()

    def get_transactions(self):
        """
        Retrieve all transactions associated with this Monero wallet.

        :return: list of dictionary representations of transactions
        """
        payments = self._get_payments()
        transactions = [self._normalize_transaction(payment) for payment in payments]
        return succeed(transactions)

    def _get_payments(self) -> list:
        """
        Retrieve all payments.

        :return: list of Payment instances: [Payment, ... ]
        """
        incoming_payments = self.get_incoming_payments()
        outgoing_payments = self.get_outgoing_payments()
        payments = incoming_payments + outgoing_payments
        return payments

    def _normalize_transaction(self, payment: Payment) -> dict:
        """
        Take monero.transaction.Payment instance and turn it into Anydex dictionary format.

        :return: formatted transaction dictionary
        """
        transaction = payment.transaction

        if isinstance(payment, OutgoingPayment):
            outgoing = True
            from_ = payment.local_address
            to = ''  # Monero hides recipient address
        else:
            outgoing = False
            from_ = ''  # Monero hides sender address
            to = payment.local_address

        return {
            'id': transaction.hash,
            'outgoing': outgoing,
            'from': from_,
            'to': to,
            'amount': payment.amount,
            'fee_amount': transaction.fee,
            'currency': self.get_identifier(),
            'timestamp': time.mktime(transaction.timestamp.timetuple()),
            'description': f'Confirmations: {transaction.confirmations}'
        }

    def get_incoming_payments(self, confirmed=True):
        """
        Get all confirmed incoming payments for this wallet.

        :param: if set to True return only confirmed payments, else only mempool payments
        :return: list of payments
        """
        if self._wallet_connection_alive():
            return succeed(self.wallet.incoming(confirmed=confirmed, unconfirmed=(not confirmed)))
        return fail(WalletConnectionError())

    def get_outgoing_payments(self, confirmed=True):
        """
        Get all confirmed outgoing payments for this wallet.

        :param: if True return only confirmed outgoing payments, else mempool payments
        :return: list of payments
        """
        if self._wallet_connection_alive():
            return succeed(self.wallet.outgoing(confirmed=confirmed, unconfirmed=(not confirmed)))
        return fail(WalletConnectionError())

    def min_unit(self):
        # atomic unit: single piconero
        return 1

    def precision(self):
        return 12

    def get_identifier(self):
        return 'XMR'

    def get_confirmations(self, transaction: Payment):
        """
        Return number of confirmations transactions has received.

        :param transaction: Payment object from monero-python library
        :return: integer count
        """
        if self._wallet_connection_alive:
            return succeed(self.wallet.confirmations(transaction))
        return fail(WalletConnectionError())

    def monitor_transaction(self, txid):
        """
        Blockchain is used to retrieve all transactions related to wallet.
        No need for database and `monitor_transaction` method to store historical transactions.

        :param txid: transaction id
        """
        pass


class MoneroTestnetWallet(MoneroWallet):
    """
    This wallet represents a wallet or account in the Monero testnet.
    """

    TESTNET = True

    def get_name(self):
        return 'Testnet XMR'

    def get_identifier(self):
        return 'TXMR'


class NotSupportedOperationException(Exception):
    """
    Raise exception if operation is not supported.
    """
    pass


class WalletConnectionError(Exception):
    """
    Raise in case connection to wallet is no longer alive.
    """
    pass
