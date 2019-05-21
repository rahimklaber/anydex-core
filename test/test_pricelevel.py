import unittest

from core.assetamount import AssetAmount
from core.assetpair import AssetPair
from core.message import TraderId
from core.order import OrderId, OrderNumber
from core.price import Price
from core.pricelevel import PriceLevel
from core.tick import Tick
from core.tickentry import TickEntry
from core.timeout import Timeout
from core.timestamp import Timestamp


class PriceLevelTestSuite(unittest.TestCase):
    """PriceLevel test cases."""

    def setUp(self):
        # Object creation
        tick = Tick(OrderId(TraderId(b'0' * 20), OrderNumber(1)), AssetPair(AssetAmount(60, 'BTC'),
                                                                            AssetAmount(30, 'MC')),
                    Timeout(100), Timestamp.now(), True)
        tick2 = Tick(OrderId(TraderId(b'0' * 20), OrderNumber(2)), AssetPair(AssetAmount(30, 'BTC'),
                                                                             AssetAmount(30, 'MC')),
                     Timeout(100), Timestamp.now(), True)

        self.price_level = PriceLevel(Price(50, 5, 'MC', 'BTC'))
        self.tick_entry1 = TickEntry(tick, self.price_level)
        self.tick_entry2 = TickEntry(tick, self.price_level)
        self.tick_entry3 = TickEntry(tick, self.price_level)
        self.tick_entry4 = TickEntry(tick, self.price_level)
        self.tick_entry5 = TickEntry(tick2, self.price_level)

    def test_appending_length(self):
        # Test for tick appending and length
        self.assertEquals(0, self.price_level.length)
        self.assertEquals(0, len(self.price_level))

        self.price_level.append_tick(self.tick_entry1)
        self.price_level.append_tick(self.tick_entry2)
        self.price_level.append_tick(self.tick_entry3)
        self.price_level.append_tick(self.tick_entry4)

        self.assertEquals(4, self.price_level.length)
        self.assertEquals(4, len(self.price_level))

    def test_tick_removal(self):
        # Test for tick removal
        self.price_level.append_tick(self.tick_entry1)
        self.price_level.append_tick(self.tick_entry2)
        self.price_level.append_tick(self.tick_entry3)
        self.price_level.append_tick(self.tick_entry4)

        self.price_level.remove_tick(self.tick_entry2)
        self.price_level.remove_tick(self.tick_entry1)
        self.price_level.remove_tick(self.tick_entry4)
        self.price_level.remove_tick(self.tick_entry3)
        self.assertEquals(0, self.price_level.length)

    def test_str(self):
        # Test for price level string representation
        self.price_level.append_tick(self.tick_entry1)
        self.price_level.append_tick(self.tick_entry2)
        self.assertEquals('60 BTC\t@\t0.5 MC\n'
                          '60 BTC\t@\t0.5 MC\n', str(self.price_level))
