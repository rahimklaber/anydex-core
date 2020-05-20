from sqlalchemy.orm import session as db_session

from test.base import AbstractServer
from test.util import MockObject
from wallet.ethereum.eth_db import Key, Transaction
from wallet.ethereum.eth_wallet import EthereumWallet


class TestEthereumWallet(AbstractServer):

    async def tearDown(self):
        db_session.close_all_sessions()
        await super().tearDown()

    def test_create_wallet(self):
        """
        Test the creation of the wallet
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        addr = wallet._session.query(Key.address).first()[0]
        self.assertEqual(addr, wallet.account.address)
        self.assertIsNotNone(wallet.account)
        self.assertTrue(wallet.created)

    def test_create_wallet_allready_created(self):
        """
        Test the creation of the wallet when the wallet is already created
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        self.assertIsNotNone(wallet.account)
        self.assertTrue(wallet.created)
        future = wallet.create_wallet()
        self.assertIsInstance(future.exception(), RuntimeError)

    def test_get_name(self):
        """
        Test for get_name
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        self.assertEqual("ethereum", wallet.get_name())

    async def test_get_balance_not_created(self):
        """
        Test for getting a balance of a wallet that has not been created
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        balance = {
            'available': 0,
            'pending': 0,
            'currency': 'ETH',
            'precision': 18
        }
        self.assertEqual(balance, await wallet.get_balance())

    async def test_get_balance(self):
        """
        Test for getting the balance of a created wallet.
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        mock_obj = MockObject()
        mock_obj.get_balance = lambda *_: 992
        wallet.provider = mock_obj
        wallet.get_transactions = lambda *_: []
        wallet._update_database = lambda *_: None
        wallet.get_outgoing_amount = lambda *_: 0
        wallet.get_incoming_amount = lambda *_: 0
        balance = {
            'available': 992,
            'pending': 0,
            'currency': 'ETH',
            'precision': 18
        }
        self.assertEqual(balance, await wallet.get_balance())

    def test_get_outgoing_amount(self):
        """
        Test for the get_outgoing_amount function.
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        wallet._session.add(
            Transaction(is_pending=True, value=100, from_=wallet.account.address, hash=wallet.generate_txid()))
        wallet._session.add(
            Transaction(is_pending=True, value=200, from_=wallet.account.address, hash=wallet.generate_txid()))
        self.assertEqual(300, wallet.get_outgoing_amount())

    def test_get_incoming_amount(self):
        """
        Test for the get_incoming_amount function
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        wallet._session.add(
            Transaction(is_pending=True, value=100, to=wallet.account.address, hash=wallet.generate_txid()))
        wallet._session.add(
            Transaction(is_pending=True, value=200, to=wallet.account.address, hash=wallet.generate_txid()))
        self.assertEqual(300, wallet.get_incoming_amount())

    async def test_get_address_not_created(self):
        """
        Test for getting the address of the wallet when it's not yet created
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        self.assertEqual("", wallet.get_address())

    async def test_get_address(self):
        """
        Test for getting the address of the wallet when it's created
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        self.assertEqual(wallet.account.address, wallet.get_address())

    async def test_precision(self):
        """
        Test for the precision function
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        self.assertEqual(18, wallet.precision())

    async def test_get_idetifier(self):
        wallet = EthereumWallet(None, self.session_base_dir)
        self.assertEqual("ETH", wallet.get_identifier())


class TestTestnetEthereumWallet(AbstractServer):
    pass
