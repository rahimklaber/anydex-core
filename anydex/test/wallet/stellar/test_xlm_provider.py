from datetime import datetime
from unittest import TestCase

from anydex.wallet.stellar.xlm_db import Transaction
from anydex.wallet.stellar.xlm_provider import HorizonProvider
from test.util import MockObject


class TestHorizonProvider(TestCase):
    """
    Tests for the Horizon provider.
    These tests only test our code and do send requests to any server.
    """
    # The content of these responses might be incorrect / omitted
    sample_submit_tx_response = {
        "memo": "2324",  # links omitted
        "id": "36df85cf7c8947fd251714bacd69b5df89945abe02337a2a0d3f5fefd1cc8c83",
        "paging_token": "2399336235282432",
        "successful": True,
        "hash": "36df85cf7c8947fd251714bacd69b5df89945abe02337a2a0d3f5fefd1cc8c83",
        "ledger": 558639,
        "created_at": "2020-06-03T15:47:39Z",
        "source_account": "GA6XQF5FLTHFYJLWFUAAHVS3NIO35Y7GE7THZNCXUJOPDW3TYUACWCH5",
        "source_account_sequence": "1978008533467156",
        "fee_account": "GA6XQF5FLTHFYJLWFUAAHVS3NIO35Y7GE7THZNCXUJOPDW3TYUACWCH5",
        "fee_charged": "100",
        "max_fee": "100",
        "operation_count": 1,
        "envelope_xdr": "AAAAAgAAAAA9eBelXM5cJXYtAAPWW2odvuPmJ",
        "result_xdr": "AAAAAAAAAGQAAAAAAAAAAQAAAAAAAAABAAAAAAAAAAA=",
        "result_meta_xdr": "AAAAAgAAAAIAAAADAAiGLwAAAAAAAAAAPXgXpVzOXCV2LQAD1ltqHb7j5ifmfLRXolzx23PFACsAAAATpNgAsAAHBv",
        "fee_meta_xdr": "AAAAAgAAAAMACITLAAAAAAAAAAA9eBelXM5cJXYtAAPWW2odvuPmJ+Z8tFeiXPHbc8UAKwAAABOk2AEUAAcG/QAAABMAA",
        "memo_type": "id",
        "signatures": [
            "V6XapCWcsf2rym9qJcti9+qcnFHXUiJG4ClwgZu8xaOBeCQmbEwWooR3ofUNQrozzk3W1sZLlpZoGr6AxbqlDA=="
        ]
    }
    sample_get_txs_response = {
        "_links": {
            "self": {
                "href": "https://horizon.stellar.org/accounts/GBOQNX4VWQMVN6C7NB5UL2CEV6AGVTM6LWQIXDRU6OBRMUNBTOMNSOAW/transactions?cursor=&limit=1&order=asc"
            },
            "next": {
                "href": "https://horizon.stellar.org/accounts/GBOQNX4VWQMVN6C7NB5UL2CEV6AGVTM6LWQIXDRU6OBRMUNBTOMNSOAW/transactions?cursor=113942965512118272&limit=1&order=asc"
            },
            "prev": {
                "href": "https://horizon.stellar.org/accounts/GBOQNX4VWQMVN6C7NB5UL2CEV6AGVTM6LWQIXDRU6OBRMUNBTOMNSOAW/transactions?cursor=113942965512118272&limit=1&order=desc"
            }
        },
        "_embedded": {
            "records": [
                {
                    "memo": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
                    "id": "96ad71731b1b46fceb0f1c32adbcc16a93cefad1e6eb167efe8a8c8e4e0cbb98",
                    "paging_token": "113942965512118272",
                    "successful": True,
                    "hash": "96ad71731b1b46fceb0f1c32adbcc16a93cefad1e6eb167efe8a8c8e4e0cbb98",
                    "ledger": 26529414,
                    "created_at": "2019-10-29T00:50:35Z",
                    "source_account": "GDQWI6FKB72DPOJE4CGYCFQZKRPQQIOYXRMZ5KEVGXMG6UUTGJMBCASH",
                    "source_account_sequence": "112092925529161789",
                    "fee_account": "GDQWI6FKB72DPOJE4CGYCFQZKRPQQIOYXRMZ5KEVGXMG6UUTGJMBCASH",
                    "fee_charged": "100",
                    "max_fee": "100",
                    "operation_count": 1,
                    "envelope_xdr": "AAAAAOFkeKoP9De5JOCNgRYZVF8IIdi8WZ6olTXYb1KTMlgRAAAAZAGOO+wAAAA9AAAAAQAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAQAAAADhZHiqD/Q3uSTgjYEWGVRfCCHYvFmeqJU12G9SkzJYEQAAAAAAAAAAXQbflbQZVvhfaHtF6ESvgGrNnl2gi44084MWUaGbmNkAAAAAAcnDgAAAAAAAAAABHvBc2AAAAEBUL1wo8IGHEpgpQ7llGaFE+rC9v5kk2KPJe53/gIdWF+792HYg5yTTmhJII97YgM+Be8yponPH0YjMjeYphewI",
                    "result_xdr": "AAAAAAAAAGQAAAAAAAAAAQAAAAAAAAAAAAAAAAAAAAA=",
                    "result_meta_xdr": "AAAAAQAAAAIAAAADAZTOhgAAAAAAAAAA4WR4qg/0N7kk4I2BFhlUXwgh2LxZnqiVNdhvUpMyWBEAAAJGMWnXfAGOO+wAAAA8AAAAAwAAAAAAAAAAAAAAAAABAQIAAAACAAAAAATtjqDoN0Htx8F47wvPo3q8Uub4pR5AKBcvK1Ue8FzYAAAAAQAAAAAHo1PMPBIRC3IkGDtQUcl0pFBGUK7qEBnkUlXX05eiBwAAAAIAAAAAAAAAAAAAAAEBlM6GAAAAAAAAAADhZHiqD/Q3uSTgjYEWGVRfCCHYvFmeqJU12G9SkzJYEQAAAkYxadd8AY477AAAAD0AAAADAAAAAAAAAAAAAAAAAAEBAgAAAAIAAAAABO2OoOg3Qe3HwXjvC8+jerxS5vilHkAoFy8rVR7wXNgAAAABAAAAAAejU8w8EhELciQYO1BRyXSkUEZQruoQGeRSVdfTl6IHAAAAAgAAAAAAAAAAAAAAAQAAAAMAAAADAZTOhgAAAAAAAAAA4WR4qg/0N7kk4I2BFhlUXwgh2LxZnqiVNdhvUpMyWBEAAAJGMWnXfAGOO+wAAAA9AAAAAwAAAAAAAAAAAAAAAAABAQIAAAACAAAAAATtjqDoN0Htx8F47wvPo3q8Uub4pR5AKBcvK1Ue8FzYAAAAAQAAAAAHo1PMPBIRC3IkGDtQUcl0pFBGUK7qEBnkUlXX05eiBwAAAAIAAAAAAAAAAAAAAAEBlM6GAAAAAAAAAADhZHiqD/Q3uSTgjYEWGVRfCCHYvFmeqJU12G9SkzJYEQAAAkYvoBP8AY477AAAAD0AAAADAAAAAAAAAAAAAAAAAAEBAgAAAAIAAAAABO2OoOg3Qe3HwXjvC8+jerxS5vilHkAoFy8rVR7wXNgAAAABAAAAAAejU8w8EhELciQYO1BRyXSkUEZQruoQGeRSVdfTl6IHAAAAAgAAAAAAAAAAAAAAAAGUzoYAAAAAAAAAAF0G35W0GVb4X2h7RehEr4BqzZ5doIuONPODFlGhm5jZAAAAAAHJw4ABlM6GAAAAAAAAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAA",
                    "fee_meta_xdr": "AAAAAgAAAAMBlM6FAAAAAAAAAADhZHiqD/Q3uSTgjYEWGVRfCCHYvFmeqJU12G9SkzJYEQAAAkYxadfgAY477AAAADwAAAADAAAAAAAAAAAAAAAAAAEBAgAAAAIAAAAABO2OoOg3Qe3HwXjvC8+jerxS5vilHkAoFy8rVR7wXNgAAAABAAAAAAejU8w8EhELciQYO1BRyXSkUEZQruoQGeRSVdfTl6IHAAAAAgAAAAAAAAAAAAAAAQGUzoYAAAAAAAAAAOFkeKoP9De5JOCNgRYZVF8IIdi8WZ6olTXYb1KTMlgRAAACRjFp13wBjjvsAAAAPAAAAAMAAAAAAAAAAAAAAAAAAQECAAAAAgAAAAAE7Y6g6DdB7cfBeO8Lz6N6vFLm+KUeQCgXLytVHvBc2AAAAAEAAAAAB6NTzDwSEQtyJBg7UFHJdKRQRlCu6hAZ5FJV19OXogcAAAACAAAAAAAAAAA=",
                    "memo_type": "hash",
                    "signatures": [
                        "VC9cKPCBhxKYKUO5ZRmhRPqwvb+ZJNijyXud/4CHVhfu/dh2IOck05oSSCPe2IDPgXvMqaJzx9GIzI3mKYXsCA=="
                    ],
                    "valid_after": "1970-01-01T00:00:00Z"
                }
            ]
        }
    }

    def setUp(self):
        self.provider = HorizonProvider("yeet")

    def test_submit_transaction(self):
        self.provider.server.submit_transaction = lambda *_: self.sample_submit_tx_response
        dummy_hash = self.provider.submit_transaction('XXX')
        self.assertEqual(dummy_hash, '36df85cf7c8947fd251714bacd69b5df89945abe02337a2a0d3f5fefd1cc8c83')

    def test_get_balance(self):
        mock = MockObject()
        fun = lambda *_: mock  # the library we use uses the builder pattern
        mock.for_account = fun
        mock.include_failed = fun
        mock.call = lambda *_: self.sample_get_txs_response
        self.provider.server.transactions = lambda: mock
        tx = Transaction(hash='96ad71731b1b46fceb0f1c32adbcc16a93cefad1e6eb167efe8a8c8e4e0cbb98',
                         ledger_nr=26529414,
                         date_time=datetime.fromisoformat('2019-10-29T00:50:35'),
                         source_account='DQWI6FKB72DPOJE4CGYCFQZKRPQQIOYXRMZ5KEVGXMG6UUTGJMBCASH',
                         operation_count=1,
                         transaction_envelope="AAAAAOFkeKoP9De5JOCNgRYZVF8IIdi8WZ6olTXYb1KTMlgRAAAAZAGOO"
                                              "+wAAAA9AAAAAQAAAAAAAAAAAAAAAAAAAAAAAAADAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA"
                                              "AAAAAAAAAAAAAAABAAAAAQAAAADhZHiqD/Q3uSTgjYEWGVRfCCHYvFmeqJU12G9SkzJYEQA"
                                              "AAAAAAAAAXQbflbQZVvhfaHtF6ESvgGrNnl2gi44084MWUaGbmNkAAAAAAcnDgAAAAAAAAA"
                                              "ABHvBc2AAAAEBUL1wo8IGHEpgpQ7llGaFE+rC9v5kk2KPJe53/gIdWF+792HYg5yTTmhJII"
                                              "97YgM+Be8yponPH0YjMjeYphewI",
                         fee=100,
                         is_pending=False,
                         succeeded=True,
                         sequence_number=112092925529161789,
                         min_time_bound=datetime.fromisoformat('1970-01-01T00:00:00'))
        self.assertEqual([tx], self.provider.get_transactions('XXX'))
