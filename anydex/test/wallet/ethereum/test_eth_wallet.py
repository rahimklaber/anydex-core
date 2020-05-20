from sqlalchemy.orm import session as db_session

from test.base import AbstractServer
from test.util import MockObject
from wallet.ethereum.eth_db import Key
from wallet.ethereum.eth_wallet import EthereumWallet


class TestEthereumWallet(AbstractServer):

    async def tearDown(self):
        db_session.close_all_sessions()
        await super().tearDown()

    async def test_create_wallet(self):
        """
        Test the creation of the wallet
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        addr = wallet.session.query(Key.address).first()[0]
        self.assertEqual(addr, wallet.account.address)
        self.assertIsNotNone(wallet.account)
        self.assertTrue(wallet.created)

    async def test_create_wallet_allready_created(self):
        """
        Test the creation of the wallet when the wallet is already created
        """
        wallet = EthereumWallet(None, self.session_base_dir)
        wallet.create_wallet()
        self.assertIsNotNone(wallet.account)
        self.assertTrue(wallet.created)
        future = wallet.create_wallet()
        self.assertIsInstance(future.exception(), RuntimeError)

    async def test_get_name(self):
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
        self.assertEqual(balance, wallet.get_balance().result())

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
        wallet.update_database = lambda *_: None
        wallet.get_outgoing_amount = lambda *_: 0
        wallet.get_incoming_amount = lambda *_: 0
        balance = {
            'available': 992,
            'pending': 0,
            'currency': 'ETH',
            'precision': 18
        }
        self.assertEqual(balance, wallet.get_balance().result())
