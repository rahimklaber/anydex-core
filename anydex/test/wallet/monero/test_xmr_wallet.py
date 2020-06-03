import monero.backends.jsonrpc
from requests.exceptions import ConnectionError

from anydex.test.base import AbstractServer
from anydex.test.util import MockObject
from anydex.wallet.cryptocurrency import Cryptocurrency
from anydex.wallet.monero.xmr_wallet import MoneroWallet, MoneroTestnetWallet, WalletConnectionError


def succeed_backend():
    mock_backend = MockObject()
    mock_backend.accounts = lambda *_: []
    monero.backends.jsonrpc.JSONRPCWallet.__new__ = lambda *_, **__: mock_backend


def fail_backend():
    mock_backend = MockObject()

    def fail_request():
        raise ConnectionError

    mock_backend.accounts = lambda *_: fail_request()
    monero.backends.jsonrpc.JSONRPCWallet.__new__ = lambda *_, **__: mock_backend


class TestMoneroWallet(AbstractServer):

    def test_wallet_fields(self):
        """
        Verify correct values set for fields in Moneron non-TESTNET wallet instance.
        """
        MoneroWallet.TESTNET = False
        w = MoneroWallet(host='192.168.178.1')
        self.assertEqual('monero', w.network)
        self.assertEqual(0, w.min_confirmations)
        self.assertEqual('192.168.178.1', w.host)
        self.assertEqual(18081, w.port)
        self.assertIsNone(w.wallet)

    async def test_wallet_connection_alive_fail(self):
        """
        Test _wallet_connection_alive method in case wallet is not created yet.
        """
        w = MoneroWallet()
        fail_backend()
        self.assertFalse(w._wallet_connection_alive())

    async def test_wallet_connection_alive_success(self):
        """
        Test _wallet_connection_alive method in case wallet is has been created.
        """
        w = MoneroWallet()
        succeed_backend()
        result = w.create_wallet()
        self.assertIsNone(result.result())
        self.assertTrue(w.created)
        self.assertTrue(w._wallet_connection_alive())

    def test_get_name(self):
        """
        Test `get_name` method on Monero wallet.
        """
        w = MoneroWallet()
        self.assertEqual(Cryptocurrency.MONERO.value, w.get_name())

    async def test_wallet_creation_fail(self):
        """
        Verify wallet create method in case `wallet-rpc-server` is not running.
        """
        w = MoneroWallet()  # use default host, port configuration
        fail_backend()
        self.assertAsyncRaises(WalletConnectionError, w.create_wallet())
        self.assertFalse(w.created)

    async def test_wallet_creation_success(self):
        """
        Verify wallet create method in case `wallet-rpc-server` is running on correct host/port.
        """
        w = MoneroWallet()  # use default host, port configuration
        succeed_backend()
        result = w.create_wallet()
        self.assertIsNone(result.result())
        self.assertTrue(w.created)

    async def test_wallet_creation_success_node(self):
        """
        Verify host and port parameters set to Wallet backend.
        """
        test_host = '192.168.178.1'
        test_port = 1903

        w = MoneroWallet(host=test_host, port=test_port)
        succeed_backend()
        result = w.create_wallet()
        self.assertIsNone(result.result())
        self.assertEqual(test_host, w.host)
        self.assertEqual(test_port, w.port)

    async def test_get_balance_no_wallet(self):
        """
        Check balance in case no connection to wallet exists yet.
        """
        w = MoneroWallet()
        self.assertDictEqual({
            'available': 0,
            'pending': 0,
            'currency': 'XMR',
            'precision': 12
        }, await w.get_balance())

    async def test_get_balance_wallet(self):
        """
        Check balance in case wallet connection exists.
        """
        w = MoneroWallet()
        mock_wallet = MockObject()
        mock_wallet.refresh = lambda *_: None
        mock_wallet.balance = lambda unlocked: 20.2

        w.wallet = mock_wallet

        self.assertDictEqual({
            'available': 20.2,
            'pending': 0,
            'currency': 'XMR',
            'precision': 12
        }, await w.get_balance())

    async def test_transfer_no_wallet(self):
        """
        Attempt XMR transfer in case no wallet exists.
        """
        w = MoneroWallet()
        result = await w.transfer(20.2, 'test_address',
                                  payment_id='test_id',
                                  priority=1,
                                  unlock_time=0)
        self.assertIsNone(result.result())

    async def test_transfer_wallet(self):
        """
        Attempt XMR transfer in case wallet exists.
        """
        w = MoneroWallet()
        result = await w.transfer(20.2, 'test_address',
                                  payment_id='test_id',
                                  priority=1,
                                  unlock_time=0)
        self.assertIsNone(result.result())


class TestTestnetMoneroWallet(AbstractServer):

    def test_wallet_fields(self):
        """
        Verify Testnet Wallet-specific values for wallet fields.
        """
        MoneroWallet.TESTNET = True
        w = MoneroWallet()
        self.assertTrue(w.TESTNET)
        self.assertEqual('tribler_testnet', w.wallet_name)

    def test_get_name(self):
        """
        Ensure name of Monero testnet wallet differs from regular Monero wallet.
        """
        w = MoneroTestnetWallet()
        self.assertEquals('Testnet XMR', w.get_name())

    def test_get_identifier(self):
        """
        Ensure identifier of Monero testnet wallet is equivalent to `TXMR`
        """
        w = MoneroTestnetWallet()
        self.assertEquals('TXMR', w.get_identifier())
