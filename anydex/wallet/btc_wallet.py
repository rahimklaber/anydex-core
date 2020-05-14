from anydex.wallet.bitcoinlib_wallet import BitcoinlibWallet


class BitcoinWallet(BitcoinlibWallet):
    """
    This class is responsible for handling your bitcoin wallet.
    """

    TESTNET = False

    def __init__(self, wallet_dir):
        super(BitcoinWallet, self).__init__(wallet_dir, network='bitcoin', testnet=self.TESTNET)

    def min_unit(self):
        return 100000  # The minimum amount of BTC we can transfer in this market is 1 mBTC (100000 Satoshi)

    def precision(self):
        return 8       # One BTC is defined as 10^8 Satoshi


class BitcoinTestnetWallet(BitcoinWallet):
    """
    This wallet represents testnet Bitcoin.
    """
    TESTNET = True

    def get_name(self):
        return 'Testnet BTC'

    def get_identifier(self):
        return 'TBTC'


class LitecoinWallet(BitcoinlibWallet):
    TESTNET = False

    def __init__(self, wallet_dir):
        super(LitecoinWallet, self).__init__(wallet_dir, network='litecoin', testnet=self.TESTNET)

    def min_unit(self):
        return 100000

    def precision(self):
        return 8    # The precision of LTC is the same as that of BTC, 10^(-8)


class LitecoinTestnetWallet(LitecoinWallet):
    """
    This wallet represents testnet Dash.
    """
    TESTNET = True

    def get_name(self):
        return 'Testnet LTC'

    def get_identifier(self):
        return 'TLTC'


class DashWallet(BitcoinlibWallet):

    TESTNET = False

    def __init__(self, wallet_dir):
        super(DashWallet, self).__init__(wallet_dir, network='dash', testnet=self.TESTNET)

    def min_unit(self):
        return 100000

    def precision(self):
        return 8    # The precision of DASH is the same as that of BTC and ETC, 10^(-8)


class DashTestnetWallet(DashWallet):

    """
    This wallet represents testnet Litecoin.
    """
    TESTNET = True

    def get_name(self):
        return 'Testnet DASH'

    def get_identifier(self):
        return 'TDASH'
