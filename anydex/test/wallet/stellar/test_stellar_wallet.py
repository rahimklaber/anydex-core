from sqlalchemy.orm import session as db_session
from stellar_sdk import Keypair

from anydex.wallet.stellar.xlm_wallet import StellarWallet
from test.base import AbstractServer
from test.util import MockObject
from wallet.stellar.xlm_db import Secret, Transaction


class TestStellarWallet(AbstractServer):
    async def tearDown(self):
        db_session.close_all_sessions()
        await super().tearDown()

    def setUp(self):
        super().setUp()
        self.wallet = StellarWallet(self.session_base_dir, True)  # trick the wallet to not use default provider

    def test_get_identifier(self):
        self.assertEqual('XLM', self.wallet.get_identifier())

    def create_wallet(self):
        """
        Create the wallet
        """
        self.wallet.get_sequence_number = lambda: 100
        self.wallet.create_wallet()

    def test_create_wallet(self):
        """
        Test for wallet creation
        """

        self.create_wallet()
        addr = self.wallet.stellar_db.session.query(Secret.address).first()[0]
        self.assertIsNotNone(self.wallet.keypair)
        self.assertTrue(self.wallet.created)
        self.assertEqual(addr, self.wallet.get_address())

    def test_init_wallet_created(self):
        """
        Test for the wallet constructor when the wallet is already created
        """
        self.create_wallet()
        StellarWallet.get_sequence_number = lambda *_: 100

        wallet = StellarWallet(self.session_base_dir, True)
        self.assertEqual(wallet.created, True)

    def test_create_wallet_already_created(self):
        """
        Test for wallet creation where we tried to create a wallet that is  already created
        """
        self.create_wallet()
        future = self.wallet.create_wallet()

        self.assertIsInstance(future.exception(), RuntimeError)

    def test_get_name(self):
        self.assertEqual('stellar', self.wallet.get_name())

    async def test_get_balance_not_created(self):
        """
        Test for getting balance when the wallet has not yet been created
        """
        balance = {
            'available': 0,
            'pending': 0,
            'currency': 'XLM',
            'precision': 7
        }
        self.assertEquals(balance, await self.wallet.get_balance())

    async def test_get_balance(self):
        """
        Test for getting the balance when the wallet has been created
        """
        self.wallet.provider = MockObject()
        self.create_wallet()
        self.wallet.provider.get_balance = lambda *_, **x: 100
        balance = {
            'available': 100 * 1e7,  # balance form api is not in the lowest denomination
            'pending': 0,
            'currency': 'XLM',
            'precision': 7
        }
        self.assertEquals(balance, await self.wallet.get_balance())

    def test_get_sequence_number_db(self):
        """
        Test for getting sequence number from the database
        """
        self.wallet.stellar_db.session.add(Transaction(sequence_number=1, succeeded=True, source_account='xxx'))
        self.wallet.get_address = lambda: 'xxx'
        self.assertEqual(1, self.wallet.get_sequence_number())

    def test_get_sequence_number_api(self):
        """
        Test for getting sequence number from the api
        """
        mock = MockObject()
        mock.get_account_sequence = lambda *_: 2
        self.wallet.provider = mock

        self.wallet.get_address = lambda: 'xxx'
        self.assertEqual(2, self.wallet.get_sequence_number())

    def test_get_address_not_created(self):
        """
        Test for get_address when the wallet has not been created
        """

        self.assertEqual('', self.wallet.get_address())

    def test_get_address_created(self):
        """
        Test for get_address when the wallet has been created
        """
        secret = 'SD7FUHVVDQ3NSMTFI4EQ6JRPKABZUZHTKH6N7AEQMKZQDEMO7SZFOBXN'
        address = 'GCEYPGQX75YWCWL77NOWWHHMGS2R5DP2FAOWLT65NSORFXZHQIDDCOO7'
        self.create_wallet()
        self.wallet.keypair = Keypair.from_secret(secret)
        self.assertEqual(address, self.wallet.get_address())

    def test_precision(self):
        self.assertEqual(7, self.wallet.precision())

    async def test_get_transactions_not_created(self):
        """
        Test for get_transactions when wallet has not been created
        """
        self.assertEqual([], await self.wallet.get_transactions())
