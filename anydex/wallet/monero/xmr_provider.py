import logging

from ipv8.util import fail, succeed
from monero.wallet import Wallet
from monero.daemon import Daemon
from monero.backends.jsonrpc import JSONRPCWallet, JSONRPCDaemon
from requests.exceptions import ConnectionError

from anydex.wallet.provider import Provider, NotSupportedOperationException
from anydex.wallet.node.node import Node

_logger = logging.getLogger(__name__)


class MoneroProvider(Provider):
    def __init__(self, node: Node, wallet_host: str = '127.0.0.1', wallet_port: int = 18081):
        """
        Intialize concrete provider class for Monero cryptocurrency.
        `18081` for port number is inspired by the default argument for the JSON RPC wallet command.

        :param node: abstraction of the (remote) host running the Monero daemon.
        :param wallet_host: hostname or ip address of node running JSON RPC Wallet server.
        :param wallet_port: port of node running JSON RPC Wallet server.
        """
        try:
            _logger.info(f'Connect to wallet-rpc-server on {wallet_host} at {wallet_host}')
            self.wallet = Wallet(JSONRPCWallet(port=wallet_port))
        except ConnectionError as err:
            _logger.error(f'{wallet_host} refused connection at port {wallet_port}: {err}')

        host, port = node.host, node.port
        try:
            _logger.info(f'Connect to Monero daemon on host {host} at port {port}')
            self.blockchain = Daemon(JSONRPCDaemon(protocol=node.protocol,
                                                   user=node.username,
                                                   password=node.password,
                                                   host=host,
                                                   port=port))
        except ConnectionError as err:
            _logger.error(f'{host} refused connection to daemon at port {port}: {err}')

    def blockchain_connection_alive(self) -> bool:
        """
        Verify connection to blockchain is still established
        """
        try:
            self.blockchain.info()
            return True
        except ConnectionError:
            return False
            # TODO handle failure connection to blockchain

    def submit_transaction(self, tx):
        """
        Connect to (remote) node to submit transaction to the Monero blockchain.

        :param tx: transaction to submit
        :return: transaction JSONRPC response object
        """
        return self.blockchain.send_transaction(tx)

    def get_balance(self, address):
        # Official Monero JSONRPC backend does not support retrieving balance of an account/wallet by address.
        return fail(NotSupportedOperationException())

    def get_transactions(self, address):
        # Official Monero JSONRPC backend does not support retrieving transactions for any address.
        return fail(NotSupportedOperationException())
