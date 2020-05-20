from datetime import datetime
from unittest import TestCase

from anydex.test.util import MockObject
from anydex.wallet.ethereum.eth_db import Transaction
from anydex.wallet.ethereum.eth_provider import EthereumBlockchairProvider
from anydex.wallet.provider import *


class TestEthereumBlockChairProvider(TestCase):
    sample_transactions_repsonse = {
        "data": [
            {
                "block_id": 46147,
                "id": 46147000000,
                "index": 0,
                "hash": "0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
                "date": "2015-08-07",
                "time": "2015-08-07 03:30:33",
                "failed": False,
                "type": "call",
                "sender": "0xa1e4380a3b1f749673e270229993ee55f35663b4",
                "recipient": "0x5df9b87991262f6ba471f09758cde1c0fc1de734",
                "call_count": 1,
                "value": "31337",
                "value_usd": 3.1337e-14,
                "internal_value": "31337",
                "internal_value_usd": 3.1337e-14,
                "fee": "1050000000000000000",
                "fee_usd": 1.05,
                "gas_used": 21000,
                "gas_limit": 21000,
                "gas_price": 50000000000000,
                "input_hex": "",
                "nonce": "0",
                "v": "1c",
                "r": "88ff6cf0fefd94db46111149ae4bfc179e9b94721fffd821d38d16464b3f71d0",
                "s": "45e0aff800961cfce805daef7016b9b675c137a6a41a548f7b60a3484c06a33a"
            }
        ],
        "context": {
            "code": 200,
            "limit": 10,
            "offset": 0,
            "rows": 2,
            "total_rows": 2,
            "state": 8791945,
            "state_layer_2": 8791935,
        }
    }
    sample_stats_response = {
        "data": {
            "blocks": 8765932,
            "transactions": 563679664,
            "blocks_24h": 6345,
            "circulation_approximate": "108198544155730000000000000",
            "transactions_24h": 732332,
            "difficulty": 2384281079680802,
            "volume_24h_approximate": "1942030242954258000000000",
            "mempool_transactions": 34803,
            "mempool_median_gas_price": 100000000,
            "mempool_tps": 1.8333333333333333,
            "mempool_total_value_approximate": "890993462756481300000",
            "best_block_height": 8765929,
            "best_block_hash": "18164bed364f1ceef954e98f2d0ee8af4b45ba2144baa74e203e882dbf4a32f6",
            "best_block_time": "2019-10-18 16:27:20",
            "uncles": 943033,
            "uncles_24h": 353,
            "blockchain_size": 106821332817,
            "calls": 1416512303,
            "average_transaction_fee_24h": "631689895242411",
            "median_transaction_fee_24h": "315000000000000",
            "inflation_24h": 13293.0625,
            "average_simple_transaction_fee_24h": "319074939493396",
            "median_simple_transaction_fee_24h": "210000000000000",
            "largest_transaction_24h": {
                "hash": "0x8cdda43621c13cd6f6f5001c39792aec8602c1bb1fe406558224201b0a79f465",
                "value_usd": 17709550.4761
            },
            "hashrate_24h": "198690089973400",
            "inflation_usd_24h": 2302358.425,
            "average_transaction_fee_usd_24h": 0.10940868985598558,
            "median_transaction_fee_usd_24h": 0.054557999999999995,
            "average_simple_transaction_fee_usd_24h": 0.05526377952025618,
            "median_simple_transaction_fee_usd_24h": 0.036372,
            "market_price_usd": 173.2,
            "market_price_btc": 0.021793263465708,
            "market_price_usd_change_24h_percentage": -3.30365,
            "market_cap_usd": 18739592599,
            "market_dominance_percentage": 8.63,
            "layer_2": {
                "erc_20": {
                    "tokens": 120889,
                    "transactions": 273663782,
                    "tokens_24h": 164,
                    "transactions_24h": 495265
                }
            }
        },
        "context": {
            "code": 200,
        }
    }
    sample_address_response = {
        "data": {
            "0x3282791d6fd713f1e94f4bfd565eaa78b3a0599d": {
                "address": {
                    "type": "account",
                    "contract_code_hex": None,
                    "contract_created": None,
                    "contract_destroyed": None,
                    "balance": "1337000000000000001337",
                    "balance_usd": 217088.92828369106,
                    "received_approximate": "1337000000000000000000",
                    "received_usd": 1337,
                    "spent_approximate": "0",
                    "spent_usd": 0,
                    "fees_approximate": "0",
                    "fees_usd": 0,
                    "receiving_call_count": 2,
                    "spending_call_count": 0,
                    "call_count": 2,
                    "transaction_count": 2,
                    "first_seen_receiving": "2015-07-30 00:00:00",
                    "last_seen_receiving": "2018-11-16 00:52:45",
                    "first_seen_spending": None,
                    "last_seen_spending": None
                },
                "calls": [

                ],
                "layer_2": {
                    "erc_20": [

                    ]
                }
            }
        },
        "context": {
            "code": 200,
            "limit": 100,
            "offset": 0,
            "results": 1,
            "state": 8805160,
            "state_layer_2": 8805148,

        }
    }

    def setUp(self):
        self.bcp = EthereumBlockchairProvider()

    def test_get_balance(self):
        mock_response = MockObject()
        mock_response.json = lambda: self.sample_address_response
        self.bcp.send_request = lambda *_, **x: mock_response
        self.assertEqual(1337000000000000001337, self.bcp.get_balance("0x3282791d6fd713f1e94f4bfd565eaa78b3a0599d"))

    def test_get_transaction_count(self):
        mock_response = MockObject()
        mock_response.json = lambda: self.sample_address_response
        self.bcp.send_request = lambda *_, **x: mock_response
        self.assertEqual(2,
                         self.bcp.get_transaction_count("0x3282791d6fd713f1e94f4bfd565eaa78b3a0599d"))

    def test_get_gas_price(self):
        mock_response = MockObject()
        mock_response.json = lambda: self.sample_stats_response
        self.bcp.send_request = lambda *_, **x: mock_response
        self.assertEqual(100000000,
                         self.bcp.get_gas_price())

    def test_get_transactions(self):
        # 4 txs because get_transactions calls get_transactions_received and they both request confirmed transactions
        # and unconfirmed transactions
        txs = [Transaction(hash="0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
                           date_time=datetime(2015, 8, 7, 3, 30, 33),
                           from_="0xa1e4380a3b1f749673e270229993ee55f35663b4",
                           to="0x5df9b87991262f6ba471f09758cde1c0fc1de734",
                           gas=21000,
                           gas_price=50000000000000,
                           nonce=0,
                           is_pending=False,
                           value=31337,
                           block_number=46147),
               Transaction(hash="0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
                           date_time=datetime(2015, 8, 7, 3, 30, 33),
                           from_="0xa1e4380a3b1f749673e270229993ee55f35663b4",
                           to="0x5df9b87991262f6ba471f09758cde1c0fc1de734",
                           gas=21000,
                           gas_price=50000000000000,
                           nonce=0,
                           is_pending=False,
                           value=31337,
                           block_number=46147),
               Transaction(hash="0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
                           date_time=datetime(2015, 8, 7, 3, 30, 33),
                           from_="0xa1e4380a3b1f749673e270229993ee55f35663b4",
                           to="0x5df9b87991262f6ba471f09758cde1c0fc1de734",
                           gas=21000,
                           gas_price=50000000000000,
                           nonce=0,
                           is_pending=False,
                           value=31337,
                           block_number=46147),
               Transaction(hash="0x5c504ed432cb51138bcf09aa5e8a410dd4a1e204ef84bfed1be16dfba1b22060",
                           date_time=datetime(2015, 8, 7, 3, 30, 33),
                           from_="0xa1e4380a3b1f749673e270229993ee55f35663b4",
                           to="0x5df9b87991262f6ba471f09758cde1c0fc1de734",
                           gas=21000,
                           gas_price=50000000000000,
                           nonce=0,
                           is_pending=False,
                           value=31337,
                           block_number=46147)
               ]
        mock_response = MockObject()
        mock_response.json = lambda: self.sample_transactions_repsonse
        self.bcp.send_request = lambda *_, **x: mock_response
        self.assertEqual(txs,
                         self.bcp.get_transactions("0xa1e4380a3b1f749673e270229993ee55f35663b4"))

    # see EthereumBlockchairProvider for the manning of the codes
    def test_check_response_402(self):
        mock_response = MockObject()
        mock_response.status_code = 402
        self.assertRaises(RequestLimit, self.bcp._check_response, mock_response)

    def test_check_response_429(self):
        mock_response = MockObject()
        mock_response.status_code = 429
        self.assertRaises(RequestLimit, self.bcp._check_response, mock_response)

    def test_check_response_430(self):
        mock_response = MockObject()
        mock_response.status_code = 430
        self.assertRaises(Blocked, self.bcp._check_response, mock_response)

    def test_check_response_434(self):
        mock_response = MockObject()
        mock_response.status_code = 434
        self.assertRaises(Blocked, self.bcp._check_response, mock_response)

    def test_check_response_503(self):
        mock_response = MockObject()
        mock_response.status_code = 503
        self.assertRaises(Blocked, self.bcp._check_response, mock_response)

    def test_check_response_435(self):
        mock_response = MockObject()
        mock_response.status_code = 435
        self.assertRaises(RateExceeded, self.bcp._check_response, mock_response)

    def test_check_response_200(self):
        mock_response = MockObject()
        mock_response.status_code = 200
        self.assertIsNone(self.bcp._check_response(mock_response))