import datetime

from ipv8.util import succeed

from sqlalchemy.orm import session as db_session

from anydex.test.base import AbstractServer
from anydex.wallet.btc_wallet import BitcoinTestnetWallet


class TestWallet(AbstractServer):
    '''
    This class is named as bcl_wallet and not as test_btc_wallet so that it is not detected as a test class itself.
    It should only be called through other test classes by passing the appropriate parameters.
    '''
    NETWORK_INFO = {
        'bitcoin': ['Bitcoin', 'BTC'],
        'litecoin': ['Litecoin', 'LTC'],
        'dash': ['Dash', 'DASH'],
        'testnet': ['Testnet', 'BTC']
    }

    WALLET_INFO = {
        'Bitcoin': {
            'min_unit': 100000,
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
    name = None
    currency = None
    wallet = None

    def __init__(self, network, wallet):
        self.name = self.NETWORK_INFO[network][0]
        self.currency = self.NETWORK_INFO[network][1]
        self.wallet = wallet

    def test_wallet_name(self):
        """
        Test the name of a wallet
        """
        self.assertTrue(self.wallet.get_name() == self.WALLET_INFO[self.name]['name'])

    def test_wallet_identfier(self):
        """
        Test the identifier of a wallet
        """
        self.assertTrue(self.wallet.get_identifier() == self.WALLET_INFO[self.name]['identifier'])

    def test_wallet_address(self):
        """
        Test the address of a wallet
        """
        self.assertTrue(self.wallet.get_address() == '')

    def test_wallet_unit(self):
        """
        Test the mininum unit of a wallet
        """
        self.assertTrue(self.wallet.min_unit() == self.WALLET_INFO[self.name]['min_unit'])

    async def test_balance_no_wallet(self):
        """
        Test the retrieval of the balance of a wallet that is not created yet
        """
        balance = await self.wallet.get_balance()
        self.assertTrue(balance ==
                             {'available': 0, 'pending': 0, 'currency': self.NETWORK_INFO[self.name][1],
                              'precision': self.WALLET_INFO[self.name]['precision']})

    def runTests(self):
        self.test_wallet_name()
        self.test_wallet_identfier()
        self.test_wallet_address()
        self.test_wallet_unit()
        self.test_balance_no_wallet()
