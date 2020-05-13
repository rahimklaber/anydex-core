import os
import time

from asyncio import Future
from binascii import hexlify
from configparser import ConfigParser

from ipv8.util import fail, succeed
from anydex.wallet.wallet import InsufficientFunds, Wallet
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
        return 8


class BitcoinTestnetWallet(BitcoinWallet):
    """
    This wallet represents testnet Bitcoin.
    """
    TESTNET = True

    def get_name(self):
        return 'Testnet BTC'

    def get_identifier(self):
        return 'TBTC'
