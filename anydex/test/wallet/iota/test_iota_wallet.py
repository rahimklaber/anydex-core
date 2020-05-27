import unittest
from asyncio import Future

from iota import Address
from ipv8.util import succeed
from sqlalchemy.orm import session as db_session

from anydex.test.base import AbstractServer
from anydex.wallet.iota.iota_wallet import IotaWallet, IotaTestnetWallet
from anydex.wallet.wallet import InsufficientFunds


class TestIotaWallet(AbstractServer):

    async def tearDown(self):
        db_session.close_all_sessions()
        await super().tearDown()

    def test_get_name(self):
        """
        Test for get_name
        """
        wallet = IotaWallet(self.session_base_dir, True)
        self.assertEqual('iota', wallet.get_name())

    def test_get_identifier(self):
        """
        Test for get identifier
        """
        wallet = IotaWallet(self.session_base_dir, True)
        self.assertEqual('IOTA', wallet.get_identifier())

    def test_create_wallet(self):
        """
        Test wallet creation and side effects
        """
        wallet = IotaWallet(self.session_base_dir, None)
        # Check that wallet is not automatically created
        self.assertFalse(wallet.created)
        # Create the wallet
        wallet.create_wallet()
        # Check that all initializations occurred correctly
        self.assertTrue(wallet.created)
        self.assertIsNotNone(wallet.seed)
        self.assertIsNotNone(wallet.provider)

    def test_erronous_wallet_creation(self):
        """
        Tests creating an already created wallet
        """
        wallet = IotaWallet(self.session_base_dir, True)
        wallet.create_wallet()  # Create the wallet once
        response = wallet.create_wallet()
        # Check that an exception is returned when a wallet is created again
        self.assertIsInstance(response.exception(), RuntimeError)
        # Check that the second wallet creation did not damage the first
        self.assertTrue(wallet.created)
        self.assertIsNotNone(wallet.seed)
        self.assertIsNotNone(wallet.provider)

    def test_wallet_exists(self):
        """
        Tests the good and bad weather cases of wallet_exist
        """
        wallet = IotaWallet(self.session_base_dir, True)
        # Wallet is instantiated, but not created
        self.assertFalse(wallet.wallet_exists())
        # Create the wallet
        wallet.create_wallet()
        # Check that the creation is correctly identified
        self.assertTrue(wallet.wallet_exists())

    def test_get_address_before_creation(self):
        """
        Bad weather test case for getting an address
        """
        wallet = IotaWallet(self.session_base_dir, True)
        # Prepare the expected result
        future = Future()
        future.set_result([])
        # Get the address
        result = wallet.get_address()
        # Assert the type and content
        self.assertIsInstance(result, Future)
        self.assertEqual(future.result(), result.result())

    def test_get_address_after_creation(self):
        """
        Tests correct address retrieval from the database.
        """
        wallet = IotaWallet(self.session_base_dir, True)
        address_length = 81
        # Create the wallet
        wallet.create_wallet()
        # Get the address
        result = wallet.get_address()
        # Assert the type and length
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Address)
        self.assertEqual(address_length, len(result.__str__()))

    async def test_transfer_before_creation(self):
        """
        Tests the bad weather case of transfering before wallet creation.
        """
        wallet = IotaWallet(self.session_base_dir, True)
        # Address taken from IOTA documentation.
        to_address = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9' \
                     'KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        # Try sending a transfer
        result = await wallet.transfer(0, to_address)
        # Assert tpye and contents.
        self.assertIsInstance(result, Future)
        self.assertIsInstance(result.exception(), RuntimeError)

    async def test_transfer_insufficient_funds(self):
        """
        Tests the transfer when the balance of the wallet is insufficient
        """
        wallet = IotaWallet(self.session_base_dir, True)
        wallet.create_wallet()
        # Address taken from IOTA documentation.
        to_address = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9' \
                     'KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        # Set up mocks.
        wallet.get_balance = lambda: succeed({'available': 0, 'pending': 0,
                                              'currency': 'IOTA', 'precision': 6})
        # Try sending a transfer with a value higher than the
        # Available amount.
        result = await wallet.transfer(1, to_address)
        # Assert type and contents.
        self.assertIsInstance(result, Future)
        self.assertIsInstance(result.exception(), InsufficientFunds)

    async def test_correct_transfer(self):
        """
        Tests the good weather case for transfers
        """
        wallet = IotaWallet(self.session_base_dir, True)
        wallet.create_wallet()
        # Address taken from IOTA documentation.
        to_address = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9' \
                     'KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        # Set up mocks.
        wallet.get_balance = lambda: succeed({'available': 1, 'pending': 0,
                                              'currency': 'IOTA', 'precision': 6})
        # Send a correct transfer
        result = await wallet.transfer(1, to_address)
        # Assert type and contents.
        self.assertIsInstance(result, Future)
        self.assertIsInstance(result.exception(), InsufficientFunds)



    # TODO: test_get_address_from_provider
    # TODO: test_transfer
    # TODO: test_transfer_zero
    # TODO: test_transfer_invalid ? invalid address, negative value ?
    # TODO: test_get_balance
    # TODO: test_get_balance_not_created
    # TODO: test_get_transactions
    # TODO: test_monitor_transaction
    # TODO: test_monitor_transaction_invalid ? invalid transaction id ?


class TestIotaTestnetWallet(AbstractServer):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_name(self):
        """
        Test for get_name
        """
        wallet = IotaTestnetWallet(self.session_base_dir, True)
        self.assertEqual('Testnet IOTA', wallet.get_name())

    def test_get_identifier(self):
        """
        Test for get identifier
        """
        wallet = IotaTestnetWallet(self.session_base_dir, True)
        self.assertEqual('TIOTA', wallet.get_identifier())


if __name__ == '__main__':
    unittest.main()
