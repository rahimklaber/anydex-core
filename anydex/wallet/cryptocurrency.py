from enum import Enum


class Cryptocurrency(Enum):
    """
    Enum representing currently implemented cryptocurrencies.
    """
    BANDWIDTH_TOKEN = 'bandwidth_token'

    BITCOIN = 'bitcoin'
    LITECOIN = 'litecoin'
    DASH = 'dash'

    ETHEREUM = 'ethereum'
    IOTA = 'iota'
    MONERO = 'monero'
    STELLAR = 'stellar'
