import abc
from abc import ABCMeta

import os
import time

from asyncio import Future
from binascii import hexlify
from configparser import ConfigParser

from ipv8.util import fail, succeed
from anydex.wallet.wallet import InsufficientFunds, Wallet
from bitcoinlib.wallets import wallet_exists, HDWallet, WalletError


class UnsupportedNetwork(Exception):
    """
    Used for throwing exceptions when a wallet is initialised with an invalid network
    """
    def __init__(self, network):
        super(UnsupportedNetwork, self).__init__(f'Network {network} is not supported.')


class BitcoinlibWallet(Wallet):
    SUPPORTED_NETWORKS = ['bitcoin', 'litecoin', 'dash']

    def __init__(self, wallet_dir, testnet, network, name, currency):
        if network not in self.SUPPORTED_NETWORKS:
            raise(UnsupportedNetwork(network))
        super(BitcoinlibWallet, self).__init__()
        self.testnet = testnet
        self.network = network
        self.currency = currency
        self.name = name
        self.wallet_dir = wallet_dir
        self.min_confirmations = 0
        self.wallet = None
        self.unlocked = True
        self.db_path = os.path.join(wallet_dir, 'wallets.sqlite')
        self.wallet_name = 'tribler testnet' if self.testnet else 'tribler_' + network

        if wallet_exists(self.wallet_name, db_uri=self.db_path):
            self.wallet_dir = HDWallet(self.wallet_name, db_uri=self.db_path)
            self.created = True

        self.lib_init()

    def cfg_init(self):

        config = ConfigParser()

        config['locations'] = {}
        locations = config['locations']
        locations['data_dir'] = self.wallet_dir.__str__()
        # locations['database_dir'] = 'database'
        # locations['default_databasefile'] = 'bitcoinlib.sqlite'
        # locations['default_databasefile_cache'] = 'bitcoinlib_cache.sqlite'
        locations['log_file'] = 'bitcoin_config.log'

        config['common'] = {}
        common = config['common']
        # common['allow_database_threads'] = 'True'
        # common['timeout_requests'] = '5'
        # common['default_language'] = 'english'
        common['default_network'] = 'bitcoin'
        # common['default_witness_type'] = ''
        # common['service_caching_enabled'] = 'True'

        config['logs'] = {}
        logs = config['logs']
        # logs['enable_bitcoinlib_logging'] = 'True'
        logs['log_file'] = 'bitcoin_config.log'
        # logs['loglevel'] = 'WARNING'

        return config

    def lib_init(self):

        cfg_name = 'bitcoin_config.ini'

        config = self.cfg_init()
        with open(cfg_name, 'w+') as configfile:
            config.write(configfile)

        os.environ['BCL_CONFIG_FILE'] = os.path.abspath(cfg_name)

    def get_name(self):
        return self.name

    def get_identifier(self):
        return self.currency

    def create_wallet(self):
        if wallet_exists(self.wallet_name, db_uri=self.db_path):
            return fail(RuntimeError(f"{self.network} wallet with name {self.wallet_name} already exists."))

        self._logger.info("Creating wallet in %s", self.wallet_dir)
        try:
            self.wallet = HDWallet.create(self.wallet_name, network=self.network, db_uri=self.db_path)
            self.wallet.new_key('tribler_payments')
            self.wallet.new_key('tribler_change', change=1)
            self.created = True
        except WalletError as exc:
            self._logger.error(f"Cannot create {self.network} wallet!")
            return fail(exc)
        return succeed(None)

    def get_balance(self):
        if self.created:
            self.wallet.utxos_update(networks=self.network)
            return succeed({
                "available": self.wallet.balance(network=self.network),
                "pending": 0,
                "currency": self.currency,
                "precision": self.precision()
            })

        return succeed({"available": 0, "pending": 0, "currency": self.currency, "precision": self.precision()})

    async def transfer(self, amount, address):
        balance = await self.get_balance()

        if balance['available'] >= int(amount):
            self._logger.info(f"Creating {self.network} payment with amount %f to address %s", amount, address)
            tx = self.wallet.send_to(address, int(amount))
            return str(tx.hash)
        raise InsufficientFunds("Insufficient funds")

    def monitor_transaction(self, txid):
        """
        Monitor a given transaction ID. Returns a Deferred that fires when the transaction is present.
        """
        monitor_future = Future()

        async def monitor():
            transactions = await self.get_transactions()
            for transaction in transactions:
                if transaction['id'] == txid:
                    self._logger.debug("Found transaction with id %s", txid)
                    monitor_future.set_result(None)
                    monitor_task.cancel()

        self._logger.debug("Start polling for transaction %s", txid)
        monitor_task = self.register_task(f"{self.name}_poll_{txid}", monitor, interval=5)

        return monitor_future

    def get_address(self):
        if not self.created:
            return ''
        return self.wallet.keys(name='tribler_payments', is_active=False)[0].address

    def get_transactions(self):
        if not self.created:
            return succeed([])

        from bitcoinlib.transactions import Transaction
        from bitcoinlib.wallets import DbTransaction, DbTransactionInput

        # Update all transactions
        self.wallet.transactions_update(network=self.network)

        txs = self.wallet._session.query(DbTransaction.raw, DbTransaction.confirmations,
                                         DbTransaction.date, DbTransaction.fee) \
            .filter(DbTransaction.wallet_id == self.wallet.wallet_id) \
            .all()
        transactions = []

        for db_result in txs:
            transaction = Transaction.import_raw(db_result[0], network=self.network)
            transaction.confirmations = db_result[1]
            transaction.date = db_result[2]
            transaction.fee = db_result[3]
            transactions.append(transaction)

        # Sort them based on locktime
        transactions.sort(key=lambda tx: tx.locktime, reverse=True)

        my_keys = [key.address for key in self.wallet.keys(network=self.network, is_active=False)]

        transactions_list = []
        for transaction in transactions:
            value = 0
            input_addresses = []
            output_addresses = []
            for tx_input in transaction.inputs:
                input_addresses.append(tx_input.address)
                if tx_input.address in my_keys:
                    # At this point, we do not have the value of the input so we should do a database query for it
                    db_res = self.wallet._session.query(DbTransactionInput.value).filter(
                        hexlify(tx_input.prev_hash) == DbTransactionInput.prev_hash,
                        tx_input.output_n_int == DbTransactionInput.output_n).all()
                    if db_res:
                        value -= db_res[0][0]

            for tx_output in transaction.outputs:
                output_addresses.append(tx_output.address)
                if tx_output.address in my_keys:
                    value += tx_output.value

            transactions_list.append({
                'id': transaction.hash,
                'outgoing': value < 0,
                'from': ','.join(input_addresses),
                'to': ','.join(output_addresses),
                'amount': abs(value),
                'fee_amount': transaction.fee,
                'currency': self.currency,
                'timestamp': time.mktime(transaction.date.timetuple()),
                'description': f'Confirmations: {transaction.confirmations}'
            })

        return succeed(transactions_list)

    def min_unit(self):
        return 100000  # For LTC, BTC and DASH, the minimmum trade should be 100.000 basic units (Satoshi, duffs)

    def precision(self):
        return 8       # The precision for LTC, BTC and DASH is the same.\

    @abc.abstractmethod
    def is_testnet(self):
        return


class ConcreteBitcoinlibWallet(BitcoinlibWallet):

    NETWORK_INFO = {
        'bitcoin': ['Bitcoin', 'BTC'],
        'litecoin': ['Litecoin', 'LTC'],
        'dash': ['Dash', 'DASH']
    }

    def is_testnet(self):
        return False

    def __init__(self, wallet_dir, network):
        super(ConcreteBitcoinlibWallet, self)\
            .__init__(wallet_dir, False, network, self.NETWORK_INFO[network][0], self.NETWORK_INFO[network][1])


class TestnetBitcoinlibWallet(BitcoinlibWallet, metaclass=ABCMeta):

    NETWORK_INFO = {
        'bitcoin': ['Testnet', 'TBTC'],
        'litecoin': ['Testnet', 'TLTC'],
        'dash': ['Testnet', 'TDASH']
    }

    def is_testnet(self):
        return True

    def __init__(self, wallet_dir, network):
        super(TestnetBitcoinlibWallet, self)\
            .__init__(wallet_dir, True, network, self.NETWORK_INFO[network][0], self.NETWORK_INFO[network][1])
