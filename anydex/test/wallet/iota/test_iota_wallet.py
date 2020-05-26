import unittest

from test.base import AbstractServer
from wallet.iota.iota_wallet import IotaWallet, IotaTestnetWallet


class TestIotaWallet(AbstractServer):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_name(self):
        """
        Test for get_name
        """
        wallet = IotaWallet(self.session_base_dir, True)
        self.assertEqual('IOTA', wallet.get_name())

    def test_get_identifier(self):
        """
        Test for get identifier
        """
        wallet = IotaWallet(self.session_base_dir, True)
        self.assertEqual('IOTA', wallet.get_identifier())

    # TODO: test_create_wallet
    # TODO: test_create_already_created_wallet
    # TODO: test_wallet_exists_true
    # TODO: test_wallet_exists_false
    # TODO: test_get_seed
    # TODO: test_get_seed_none
    # TODO: test_get_address_from_database
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
