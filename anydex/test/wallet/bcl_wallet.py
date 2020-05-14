import datetime

from ipv8.util import succeed

from sqlalchemy.orm import session as db_session

from anydex.test.base import AbstractServer
from anydex.wallet.btc_wallet import BitcoinTestnetWallet


class TestWallet(AbstractServer):

    NETWORK_INFO = {
        'bitcoin': ['Bitcoin', 'BTC'],
        'litecoin': ['Litecoin', 'LTC'],
        'dash': ['Dash', 'DASH'],
        'testnet': ['Testnet', 'BTC']
    }

    WALLET_INFO = {
        'Bitcoin': {
            'min_unit': 10000,
            'name': 'Testnet BTC',
            'identifier': 'TBTC',
            'precision': 8
        },
        'Litecoin': {
            'min_unit': 123,
            'name': 'Testnet LTC',
            'identifier': 'TLTC',
            'precision': 123
        },
        'Dash': {
            'min_unit': 123,
            'name': 'Testnet DASH',
            'identifier': 'TDASH',
            'precision': 123
        }
    }

    def set_wallet_and_network(self, network, wallet):
        self.network_name = self.NETWORK_INFO[network][0]
        self.network_currency = self.NETWORK_INFO[network][1]
        self.wallet = wallet

    def test_wallet_name(self):
        """
        Test the name of a wallet
        """
        self.assertEqual(self.wallet.get_name(), self.WALLET_INFO[self.network_name]['name'])

    def test_wallet_identfier(self):
        """
        Test the identifier of a wallet
        """
        self.assertEqual(self.wallet.get_identifier(), self.WALLET_INFO[self.network_name]['identifier'])

    def test_wallet_address(self):
        """
        Test the address of a wallet
        """
        self.assertEqual(self.wallet.get_address(), '')

    def test_wallet_unit(self):
        """
        Test the mininum unit of a wallet
        """
        self.assertEqual(self.wallet.min_unit(), self.WALLET_INFO[self.network_name]['min_unit'])

    async def test_balance_no_wallet(self):
        """
        Test the retrieval of the balance of a wallet that is not created yet
        """
        balance = await self.wallet.get_balance()
        self.assertDictEqual(balance,
                             {'available': 0, 'pending': 0, 'currency': self.NETWORK_INFO[self.network_name][1],
                              'precision': self.WALLET_INFO[self.network_name]['precision']})

    def runTests(self):
        self.test_wallet_name()
        self.test_wallet_identfier()
        self.test_wallet_address()
        self.test_wallet_unit()
        self.test_balance_no_wallet()
