from anydex.wallet.abstract_bitcoinlib_wallet import ConcreteBitcoinlibWallet, TestnetBitcoinlibWallet


class BitcoinWallet(ConcreteBitcoinlibWallet):
    """
    This class is responsible for handling your bitcoin wallet.
    """
    def __init__(self, wallet_dir):
        super(BitcoinWallet, self).__init__(wallet_dir, network='bitcoin')


class BitcoinTestnetWallet(TestnetBitcoinlibWallet):
    """
    This wallet represents testnet Bitcoin.
    """

    def __init__(self, wallet_dir):
        super(BitcoinTestnetWallet, self).__init__(wallet_dir, network='bitcoin')


class LitecoinWallet(ConcreteBitcoinlibWallet):
    """
    This class is responsible for handling your bitcoin wallet.
    """

    def __init__(self, wallet_dir):
        super(LitecoinWallet, self).__init__(wallet_dir, network='litecoin')


class LitecoinTestnetWallet(TestnetBitcoinlibWallet):
    """
    This wallet represents testnet Bitcoin.
    """

    def __init__(self, wallet_dir):
        super(LitecoinTestnetWallet, self).__init__(wallet_dir, network='litecoin')


class DashWallet(ConcreteBitcoinlibWallet):
    """
    This class is responsible for handling your bitcoin wallet.
    """

    def __init__(self, wallet_dir):
        super(DashWallet, self).__init__(wallet_dir, network='dash')


class DashTestnetWallet(TestnetBitcoinlibWallet):
    """
    This wallet represents testnet Bitcoin.
    """

    def __init__(self, wallet_dir):
        super(DashTestnetWallet, self).__init__(wallet_dir, network='dash')


def create_bitcoinlib_wallet(network: str, testnet: bool, wallet_dir):
    return {
        'bitcoin': {
            True: BitcoinTestnetWallet(wallet_dir),
            False: BitcoinWallet(wallet_dir)
        },
        'litecoin': {
            True: LitecoinTestnetWallet(wallet_dir),
            False: LitecoinWallet(wallet_dir)
        },
        'dash': {
            True: DashTestnetWallet(wallet_dir),
            False: DashWallet(wallet_dir)
        }
    }[network][testnet]
