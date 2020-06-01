import logging

from ipv8.util import fail
from monero.wallet import Wallet
from monero.backends.jsonrpc import JSONRPCWallet
from requests.exceptions import ConnectionError

from anydex.wallet.provider import Provider, NotSupportedOperationException

_logger = logging.getLogger(__name__)


class MoneroProvider(Provider):
    def __init__(self, host: str = '127.0.0.1', port: int = 18081):
        """
        Intialize concrete provider class for Monero cryptocurrency.
        `18081` for port number is inspired by the default argument for the JSON RPC wallet command.

        :param host: hostname or ip address of node running JSON RPC Wallet server.
        :param port: port of node running JSON RPC Wallet server.
        """
        try:
            _logger.info(f'Connect to wallet-rpc-server on {host} at {port}')
            self.wallet = Wallet(JSONRPCWallet(host=host, port=port))
        except ConnectionError as err:
            _logger.error(f'{host} refused connection at port {port}: {err}')

    def wallet_connection_alive(self) -> bool:
        """
        Verify connection to wallet is still alive.

        :return: True if alive, else False
        """
        try:
            self.wallet.refresh()
        except ConnectionError:
            return False
        return True

    def submit_transaction(self, tx):
        """
        Connect to (remote) node to submit transaction to the Monero blockchain.

        :param tx: transaction to submit
        :return: transaction JSONRPC response object
        """
        return fail(NotSupportedOperationException())

    def get_balance(self, address):
        # Monero JSONRPC backend does not support retrieving balance of an account/wallet by arbitrary address.
        return fail(NotSupportedOperationException())

    def get_transactions(self, address):
        # Official Monero JSONRPC backend does not support retrieving transactions for any address.
        return fail(NotSupportedOperationException())


class WalletConnectionError(Exception):
    """
    Raise in case connection to wallet is no longer alive.
    """
    pass
