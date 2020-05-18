import datetime

from ipv8.util import succeed

from sqlalchemy.orm import session as db_session

from anydex.test.base import AbstractServer
from anydex.test.util import timeout, MockObject
from anydex.wallet.abstract_bitcoinlib_wallet import BitcoinlibWallet
from anydex.wallet.bitcoinlib_wallet import BitcoinTestnetWallet, BitcoinWallet, LitecoinWallet, LitecoinTestnetWallet, \
    DashTestnetWallet, DashWallet


def get_info(wallet: BitcoinlibWallet):
    return {
        True: {
            BitcoinTestnetWallet: ['Testnet', 'testnet', 'TBTC'],
            LitecoinTestnetWallet: ['Testnet', 'testnet', 'TLTC'],
            DashTestnetWallet: ['Testnet', 'testnet', 'TDASH']
        },
        False: {
            BitcoinWallet: ['Bitcoin', 'bitcoin', 'BTC'],
            LitecoinWallet: ['Litecoin', 'litecoint', 'LTC'],
            DashWallet: ['Dash', 'dash', 'DASH']
        }
    }[wallet.is_testnet()][wallet.__class__]


class TestWallet(AbstractServer):
    """
    Tests the functionality of bitcoinlib wallets.
    """

    WALLET_UNDER_TEST = BitcoinWallet

    def setUp(self):
        super(TestWallet, self).setUp()
        self.wallet = self.WALLET_UNDER_TEST(self.session_base_dir)
        info = get_info(wallet=self.wallet)
        self.network_name = info[0]
        self.network = info[1]
        self.network_currency = info[2]
        self.min_unit = 100000
        self.precision = 8
        self.testnet = self.network_name == 'Testnet'

    async def tearDown(self):
        # Close all bitcoinlib Wallet DB sessions
        db_session.close_all_sessions()
        await super(TestWallet, self).tearDown()

    def new_wallet(self):
        return self.WALLET_UNDER_TEST(self.session_base_dir)

    def test_wallet_name(self):
        """
        Test the name of a wallet
        """
        self.assertEquals(self.wallet.get_name(), self.network_name)

    def test_wallet_identfier(self):
        """
        Test the identifier of a wallet
        """
        self.assertEquals(self.wallet.get_identifier(), self.network_currency)

    def test_wallet_address(self):
        """
        Test the address of a wallet
        """
        self.assertEquals(self.wallet.get_address(), '')

    def test_wallet_unit(self):
        """
        Test the minimum unit of a wallet
        """
        self.assertEquals(self.wallet.min_unit(), self.min_unit)

    async def test_balance_no_wallet(self):
        """
        Test the retrieval of the balance of a wallet that is not created yet
        """
        balance = await self.wallet.get_balance()
        self.assertEquals(balance,
                             {'available': 0, 'pending': 0, 'currency': self.network_currency,
                              'precision': self.precision})

    def test_get_testnet(self):
        """
        Tests whether the wallet is testnet or concrete
        """
        self.assertEquals(self.testnet, self.wallet.is_testnet())

    @timeout(10)
    async def test_wallet_creation(self):
        """
        Test the creating, opening, transactions and balance query of a wallet
        """
        wallet = self.new_wallet()

        await wallet.create_wallet()
        self.assertIsNotNone(wallet.wallet)
        self.assertTrue(wallet.get_address())

        _ = BitcoinTestnetWallet(self.session_base_dir)
        self.assertRaises(Exception, BitcoinTestnetWallet, self.session_base_dir, testnet=True)

        wallet.wallet.utxos_update = lambda **_: None  # We don't want to do an actual HTTP request here
        wallet.wallet.balance = lambda **_: 3
        balance = await wallet.get_balance()

        self.assertDictEqual(balance, {'available': 3, 'pending': 0, 'currency': self.network_currency, 'precision': 8})
        wallet.wallet.transactions_update = lambda **_: None  # We don't want to do an actual HTTP request here
        transactions = await wallet.get_transactions()
        self.assertFalse(transactions)

        wallet.get_transactions = lambda: succeed([{"id": "abc"}])
        await wallet.monitor_transaction("abc")

    @timeout(10)
    async def test_correct_transfer(self):
        """
        Test that the transfer method of a wallet works
        """
        wallet = self.new_wallet()
        await wallet.create_wallet()
        wallet.get_balance = lambda: succeed({'available': 100000, 'pending': 0, 'currency': self.network_currency, 'precision': self.precision})
        mock_tx = MockObject()
        mock_tx.hash = 'a' * 20
        wallet.wallet.send_to = lambda *_: mock_tx
        await wallet.transfer(3000, '2N8hwP1WmJrFF5QWABn38y63uYLhnJYJYTF')

    @timeout(10)
    async def test_create_error(self):
        """
        Test whether an error during wallet creation is handled
        """
        wallet = self.new_wallet()
        await wallet.create_wallet()  # This should work
        with self.assertRaises(Exception):
            await wallet.create_wallet()

    @timeout(10)
    async def test_transfer_no_funds(self):
        """
        Test that the transfer method of a wallet raises an error when we don't have enough funds
        """
        wallet = self.new_wallet()
        await wallet.create_wallet()
        wallet.wallet.utxos_update = lambda **_: None  # We don't want to do an actual HTTP request here
        with self.assertRaises(Exception):
            await wallet.transfer(3000, '2N8hwP1WmJrFF5QWABn38y63uYLhnJYJYTF')

    @timeout(10)
    async def test_get_transactions(self):
        """
        Test whether transactions in bitcoinlib are correctly returned
        """

        raw_tx = None
        address = None
        amount = None

        if self.WALLET_UNDER_TEST == BitcoinWallet or self.WALLET_UNDER_TEST == BitcoinTestnetWallet:
            raw_tx = '02000000014bca66ebc0e3ab0c5c3aec6d0b3895b968497397752977dfd4a2f0bc67db6810000000006b483045022100fc' \
                     '93a034db310fbfead113283da95e980ac7d867c7aa4e6ef0aba80ef321639e02202bc7bd7b821413d814d9f7d6fc76ff46' \
                     'b9cd3493173ef8d5fac40bce77a7016d01210309702ce2d5258eacc958e5a925b14de912a23c6478b8e2fb82af43d20212' \
                     '14f3feffffff029c4e7020000000001976a914d0115029aa5b2d2db7afb54a6c773ad536d0916c88ac90f4f70000000000' \
                     '1976a914f0eabff37e597b930647a3ec5e9df2e0fed0ae9888ac108b1500'
            address = '1NxrPk33exXrKSuJFCHHsPVvyAstSg4S7s'
            amount = 16250000
        elif self.WALLET_UNDER_TEST == LitecoinWallet or self.WALLET_UNDER_TEST == LitecoinTestnetWallet:
            raw_tx = '020000000001047b95e486a4c85541db0743d85022849f05bbb57f3e7dc4ea981a2c5a9622a9f7000000001716001466f5' \
                     '596df480f9b8aeb5460293a9782780abc6f2feffffff8e66a70a3a2dbaadc9952db44c34bf01f4dc7156243d42696b5eff' \
                     '0fb91ef9370000000017160014afbb70f52f3ee8238278478a9844914735afbc86feffffff1b1036b4810bd144985c774f' \
                     'd52c413437dbcfc3f9e82652e3833f121bbc35e9010000001716001401ba33a4bc8c1a89886282a5591ae30d85cbc469fe' \
                     'ffffffa485a616781bdd79e223b2351b2aca2801e8a56539a1b1f011cb593e2845bcb60000000017160014d46f44356f6a' \
                     '07412f40312b7cdddd5efcf45fc5feffffff03e8b5dc070000000017a914327928c42e1d41c0a47ad9f109bbbcdcab29bc' \
                     '288700372f08000000001976a9143dde321d764f12366ea779eea7f644604e6822d588ac208c37030000000017a914ab81' \
                     'c277a3a8c4835f4508e2dfec4cf4e8ae68ab8702473044022026103da513151a490a47b7faaeb6c0560c2c8fd962d206c4' \
                     'b4d7a89884c9480e02205cdf572d09175cab95ffaeb8c59bbd1ab1fd632ba45d07dbdeec1a93b367d877012102084797fc' \
                     '56939e64e1aef1eac9d1b6356a32f4696cc6389c14adb5551007cf620246304302201e182404e10460c2539eb691b19cdd' \
                     '7fa7ea66dd527c0adb9d3b32ff13b53de9021f71247ec10632c88c16ed0ad687e1eb8796d60a06a322417aa5c5464d9edc' \
                     'ba0121029e065c10c4ccd434d6f95a3030196ac4cd8c45d8dbcb0c3686cc8fee4bfdb3e50247304402205f773cbbe7aea6' \
                     'dee3548fd1fac34b6c0d85fbd2946467e69b547ac3f60594420220015078d0fa241fc1355b977bb5781fcebce1e7edca6e' \
                     'a3b9277c71d3f7e0e601012103166aff7643ff476826b33add5e315ec0fc3fb17a99db8a19c57374e79afb2fa802473044' \
                     '022043b05f6fa3e4f1a81c147195ac468cdfefa54ef04d2c0f986c75bfa4831983e902207fcb4051468710a17c273f0587' \
                     'a06dd435959c28f06027b73a426368b74dafa501210381a710e414fcdebb096bd9f0a60d3f47f75339906520bbeae7a0e6' \
                     'bafaa7b73dcd201c00'
            address = 'MPY1E6E3NALnzX3H3kKEftLpDSEWsdpu2g'
            amount = 53972000
        elif self.WALLET_UNDER_TEST == DashWallet or self.WALLET_UNDER_TEST == DashTestnetWallet:
            raw_tx = '0200000001e2497d3c50e9d01287fe0c26f98bed6f29386a494ae7ce4b96523e9d9b7f46ad0b0000006b483045022100b5' \
                     '7918729e2dadada334ae8b4bad232baae56f451b340247c965351740fed04a022056ba6fb0dfe2b3e892fe2ce5b773064e' \
                     '3e6448a398c12a813ddc233e8c5321170121025637a83cde416c534086a8c30cf364def2601d6275df44c94249ed750cf5' \
                     'b10dfeffffff07aa530000000000001976a9145f1d5c344a7839187b1b90897fc36c59c429b63b88aca186010000000000' \
                     '1976a9140602fe0aa62b3687eaf23d09536a5ad15a90813888aca1860100000000001976a9141a8d918ab028a1e676b646' \
                     '9f02a4208954edc48388aca1860100000000001976a914580a888e9f78d75a48374300325e7ffb267e11fc88aca1860100' \
                     '000000001976a9146019b9bd9884aca97e5def7ebdc3e1653782b07888aca1860100000000001976a9146896dcf3df5ff6' \
                     '73864349b33410112cf7becb8e88aca1860100000000001976a914f04d17fb16a9291d792ba35443d6835f0c2f769088ac' \
                     '306c1300'
            address = 'XxbSMrZBhsRxNfB45pHBohhdaVxsMM8dy3'
            amount = 100001

        wallet = self.new_wallet()
        mock_wallet = MockObject()
        mock_wallet.transactions_update = lambda **_: None
        mock_wallet._session = MockObject()

        mock_all = MockObject()
        mock_all.all = lambda *_: [(raw_tx, 3, datetime.datetime(2012, 9, 16, 0, 0), 12345)]
        mock_filter = MockObject()
        mock_filter.filter = lambda *_: mock_all
        mock_wallet._session.query = lambda *_: mock_filter
        wallet.wallet = mock_wallet
        wallet.wallet.wallet_id = 3

        mock_key = MockObject()
        mock_key.address = address
        wallet.wallet.keys = lambda **_: [mock_key]
        wallet.created = True

        transactions = await wallet.get_transactions()
        print(transactions)
        self.assertTrue(transactions)
        self.assertEqual(transactions[0]["fee_amount"], 12345)
        self.assertEqual(transactions[0]["amount"], amount)


class TestDashWallet(TestWallet):
    WALLET_UNDER_TEST = DashWallet


class TestLitecoinWallet(TestWallet):
    WALLET_UNDER_TEST = LitecoinWallet


class TestBitcoinTestnetWallet(TestWallet):
    WALLET_UNDER_TEST = BitcoinTestnetWallet


class TestLitecoinTestnetWallet(TestWallet):
    WALLET_UNDER_TEST = LitecoinTestnetWallet


class TestDashTestnetWallet(TestWallet):
    WALLET_UNDER_TEST = DashTestnetWallet
