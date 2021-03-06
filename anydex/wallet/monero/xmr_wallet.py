import time
from abc import ABCMeta
from asyncio.futures import Future
from decimal import Decimal

import requests.exceptions
from ipv8.util import fail, succeed

import monero.wallet
from monero.backends.jsonrpc import JSONRPCWallet
from monero.transaction import OutgoingPayment, Payment

from anydex.wallet.wallet import Wallet, InsufficientFunds


class AbstractMoneroWallet(Wallet, metaclass=ABCMeta):
    """
    This class is responsible for handling your Monero wallet.
    The class operates on the Monero wallet connected to the `monero-wallet-rpc` server.
    A Tribler specific account is created in the wallet, storing its address in database.
    Anytime AnyDex is started up, the address is retrieved to select the appropriate account.

    NOTE: no support for account management or multiple accounts as of yet.
    """

    def __init__(self, testnet, host: str, port: int):
        super(AbstractMoneroWallet, self).__init__()

        self.network = 'monero_testnet' if testnet else 'monero'
        self.wallet_name = f'tribler_{self.network}'
        self.testnet = testnet
        self.unlocked = True

        self.min_confirmations = 0
        self.host = host
        self.port = port

        self.wallet = None
        self.created = False

    def _wallet_connection_alive(self) -> bool:
        """
        Verify connection to wallet is still alive.

        :return: True if alive, else False
        """
        if self.wallet:
            try:
                self.wallet.refresh()
                return True
            except requests.exceptions.ConnectionError:
                pass
        return False

    def create_wallet(self):
        """
        Anydex operates on existing wallet with corresponding `wallet-rpc-server`.
        Creates instance of `monero-python` Wallet instance.
        """
        self._logger.info('Connect to wallet-rpc-server on %s at %d', self.host, self.port)
        try:
            self.wallet = monero.wallet.Wallet(JSONRPCWallet(host=self.host, port=self.port))
            self.created = True
            self._logger.info('Connection to wallet-rpc-server established')
            return succeed(None)
        except requests.exceptions.ConnectionError:
            return fail(WalletConnectionError(f'Cannot connect to wallet-rpc-server on {self.host} at {self.port}'))

    def get_balance(self):
        """
        Return the balance in this wallet.
        Pending balance is the amount of newly-received XMR that cannot be spent yet.
        Locked balance turns into unlocked balance after 10 blocks.
        See: https://monero.stackexchange.com/questions/3262/whats-the-difference-between-balance-and-unlocked-balance

        :return: dictionary of available balance, pending balance, currency and precision.
                    In case wallet does not exist yet, return balance of 0.
                    Convert Monero Decimal output to float.
        """
        if not self._wallet_connection_alive():
            return succeed({
                'available': 0,
                'pending': 0,
                'currency': self.get_identifier(),
                'precision': self.precision()
            })

        unlocked_balance = self.wallet.balance(unlocked=True)
        total_balance = self.wallet.balance(unlocked=False)

        return succeed({
            'available': float(unlocked_balance),  # convert Decimal to float
            'pending': float(total_balance - unlocked_balance),
            'currency': self.get_identifier(),
            'precision': self.precision()
        })

    async def transfer(self, amount: float, address, **kwargs) -> Future:
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
        :return: Future of transfer hash, None or InsufficientFundsException
        """
        if self._wallet_connection_alive():
            balance = await self.get_balance()

            if balance['available'] < amount:
                return fail(InsufficientFunds('Insufficient funds found in Monero wallet'))

            self._logger.info('Transfer %f to %s', amount, address)
            transaction = await self.wallet.transfer(address, Decimal(str(amount)), **kwargs, relay=False)
            return succeed(transaction.hash)
        return succeed(None)

    async def transfer_multiple(self, transfers: list, **kwargs) -> list:
        """
        Submit multiple transfers simultaneously to the Monero blockchain.
        May reduce fee.

        :param transfers: list of tuples of format (address, Decimal(amount))
        :param kwargs: payment_id, priority, unlock_time (see `transfer` method above)
        :return: list of resulting hashes or return InsufficientFundsException
        """
        balance = await self.get_balance()

        total_amount = float(sum([transfer[1] for transfer in transfers]))

        if balance['available'] < total_amount:
            return fail(InsufficientFunds('Insufficient funds found in Monero wallet for all transfers'))

        if self._wallet_connection_alive():
            results = await self.wallet.transfer_multiple(transfers, **kwargs)
            hashes = [result[0].hash for result in results]
            return succeed(hashes)
        return fail(WalletConnectionError('No connection to wallet for making transfers'))

    def get_address(self):
        """
        If wallet exists or connection is alive, return address.
        """
        if self._wallet_connection_alive():
            return succeed(self.wallet.address())
        else:
            return succeed('')

    def get_integrated_address(self, payment_id) -> monero.address.IntegratedAddress:
        """
        Get integrated address from `get_address` and `payment_id` parameter.
        :param payment_id: payment_id to include into address
                    PaymentID must be either an int or hexadecimal string, or bytes
        :return: integrated address
        """
        address = self.wallet.address()
        return address.with_payment_id(payment_id)

    def generate_subaddress(self) -> monero.address.SubAddress:
        """
        Generate a new subaddress in main wallet account.
        NOTE: no support for account management or multiple accounts yet.
        :return: subaddress in main wallet account: str
        """
        address, _ = self.wallet.new_address()
        return address

    def get_addresses(self) -> list:
        """
        Return list of all addresses contained in this main wallet account.
        :return: list of `monero.address.Address`.
        """
        return self.wallet.addresses()

    async def get_transactions(self):
        """
        Retrieve all transactions associated with this Monero wallet.

        :return: list of dictionary representations of transactions
        """
        if self._wallet_connection_alive():
            payments = await self._get_payments()
            transactions = [self._normalize_transaction(payment) for payment in payments]
            return succeed(transactions)
        return fail(WalletConnectionError('No connection to wallet for retrieving transactions'))

    async def _get_payments(self) -> list:
        """
        Retrieve all payments.

        :return: list of Payment instances: [Payment, ... ]
        """
        incoming_payments = await self.get_incoming_payments()
        outgoing_payments = await self.get_outgoing_payments()
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

    def get_confirmations(self, transaction: Payment):
        """
        Return number of confirmations transactions has received.

        :param transaction: Payment object from monero-python library
        :return: integer count
        """
        if self._wallet_connection_alive():
            return succeed(self.wallet.confirmations(transaction))
        return fail(WalletConnectionError())

    def min_unit(self):
        return 1  # atomic unit: single piconero

    def precision(self):
        return 12


class MoneroWallet(AbstractMoneroWallet):
    def __init__(self, host: str = '127.0.0.1', port: int = 18081):
        super(MoneroWallet, self).__init__(False, host, port)

    def get_identifier(self):
        return 'XMR'

    def get_name(self):
        return 'monero'


class MoneroTestnetWallet(AbstractMoneroWallet):
    def __init__(self, host: str = '127.0.0.1', port: int = 18081):
        super(MoneroTestnetWallet, self).__init__(True, host, port)

    def get_identifier(self):
        return 'TXMR'

    def get_name(self):
        return 'testnet monero'


class NotSupportedOperationException(Exception):
    """
    Raise exception if operation is not supported.
    """


class WalletConnectionError(Exception):
    """
    Raise in case connection to wallet is no longer alive.
    """
