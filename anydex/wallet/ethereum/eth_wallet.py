import os
import time

from ipv8.util import fail, succeed
from sqlalchemy import func, or_
from web3 import Web3

from wallet.cryptocurrency import Cryptocurrency
from wallet.ethereum.eth_db import initialize_db, Key, Transaction
from wallet.ethereum.eth_provider import AutoEthereumProvider, AutoTestnetEthereumProvider
from wallet.wallet import Wallet, InsufficientFunds


class EthereumWallet(Wallet):
    """
    This class is responsible for handling your Ethereum wallet.
    """
    TESTNET = False

    def __init__(self, db_path, provider=None):
        super().__init__()
        if provider:
            self.provider = provider
        else:
            self.provider = AutoTestnetEthereumProvider() if self.TESTNET else AutoEthereumProvider()

        self.network = 'testnet' if self.TESTNET else Cryptocurrency.ETHEREUM.value
        self.min_confirmations = 0
        self.unlocked = True
        self._session = initialize_db(os.path.join(db_path, "eth.db"))
        self.wallet_name = 'tribler_testnet' if self.TESTNET else 'tribler'

        row = self._session.query(Key).filter(Key.name == self.wallet_name).first()
        if row:
            self.account = Web3().eth.account.from_key(row)
            self.created = True
        else:
            self.account = None

    def get_name(self):
        return Cryptocurrency.ETHEREUM.value

    def create_wallet(self):
        """
        If no account exists yet, create a new one.
        """
        if self.account:
            return fail(RuntimeError(f'Ethereum wallet with name {self.wallet_name} already exists'))

        self._logger.info(f'Creating Ethereum wallet with name {self.wallet_name}')
        if not self.account:
            self.account = Web3().eth.account.create()
            self.created = True
            self._session.add(Key(name=self.wallet_name, private_key=self.account.key, address=self.account.address))
            self._session.commit()

        return succeed(None)

    def get_balance(self):
        if not self.account:
            return succeed({
                'available': 0,
                'pending': 0,
                'currency': 'ETH',
                'precision': self.precision()
            })
        address = self.get_address()
        self._update_database(self.get_transactions())
        pending_outgoing = self.get_outgoing_amount()
        balance = {
            'available': self.provider.get_balance(address) - pending_outgoing,
            'pending': self.get_incoming_amount(),
            'currency': 'ETH',
            'precision': self.precision()
        }
        return succeed(balance)

    def get_outgoing_amount(self):
        """
        Get the current amount of ethereum that we are sending, but is still unconfirmed.
        :return: pending outgoing amount
        """
        return self._session.query(func.sum(Transaction.value)).filter(Transaction.is_pending.is_(True)).filter(
            func.lower(Transaction.from_) == self.account.address.lower()).first()[0]

    def get_incoming_amount(self):
        """
        Get the current amount of ethereum that is being sent to us, but is still unconfirmed.
        :return: pending incoming amount
        """
        return self._session.query(func.sum(Transaction.value)).filter(Transaction.is_pending.is_(True)).filter(
            func.lower(Transaction.to) == self.account.address.lower()).first()[0]

    async def transfer(self, amount, address) -> str:
        """
        Transfer Ethereum to another wallet.
        If the amount exceeds the available balance, an `InsufficientFunds` exception is raised.

        :param amount: the transfer amount
        :param address: the receiver address
        :return: transfer hash
        """
        balance = await self.get_balance()

        if balance['available'] < int(amount):
            raise InsufficientFunds('Insufficient funds')

        self._logger(f'Creating Ethereum payment with amount {amount} to address {address}')

        transaction = {
            'to': address,
            'value': amount,
            'gas': self.provider.estimate_gas(),
            'nonce': 1,
            'gasPrice': self.provider.get_gas_price(),
            'chainId': 1
        }

        # submit to blockchain
        signed = self.account.sign_transaction(transaction)
        self.provider.submit_transaction(signed, signed['rawTransaction'])

        # add transaction to database
        self._session.add(
            Transaction(
                from_=transaction['from'],
                to=transaction['to'],
                value=transaction['value'],
                gas=transaction['gas'],
                nonce=transaction['nonce'],
                gas_price=transaction['gasPrice'],
                hash=signed['hash'],
                is_pending=True
            )
        )
        self._session.commit()
        return signed['hash']

    def get_address(self):
        if not self.account:
            return ''
        return self.account.address

    def get_transactions(self):
        """
        Retrieve list of transactions from provider.

        :return: list of transactions
        """
        if not self.account:
            return succeed([])

        transactions = self.provider.get_transactions()

        self._update_database(transactions)
        # in the future we might use the provider to only retrieve transactions past a certain date/block

        transactions_db = self._session.query(Transaction).filter(
            or_(func.lower(Transaction.from_) == self.get_address().lower(),
                func.lower(Transaction.to) == self.get_address().lower()
                )).all()

        transactions_to_return = []
        latest_block_height = self.provider.get_latest_blocknr()
        for tx in transactions_db:
            transactions_to_return.append({
                'id': tx.hash,
                'outgoing': tx.from_.lower() == self.get_address().lower(),
                'from': tx.from_,
                'to': tx.to,
                'amount': tx.value,
                'fee_amount': tx.gas * tx.gas_price,
                'currency': self.get_identifier(),
                'timestamp': time.mktime(tx.date_time.timetuple()),
                'description': f'Confirmations: {latest_block_height - tx.block_number + 1}'
            })

        return succeed(transactions_to_return)

    def min_unit(self):
        # TODO determine minimal transfer unit
        return 1

    def precision(self):
        return 18

    def get_identifier(self):
        return 'ETH'

    def _update_database(self, transactions):
        """
        Update transactions in the database.
        Pending transactions that have been confirmed will be updated to have a block number and will no longer be pending.
        Other transactions that are not in the database will be added.

        :param transactions: list of transactions retrieved by self.provider
        """
        pending_transactions = self._session.query(Transaction).filter(Transaction.is_pending.is_(True)).all()
        confirmed_transactions = self._session.query(Transaction).filter(Transaction.is_pending.is_(False)).all()
        self._logger.debug('Updating ethereum database')
        for transaction in transactions:
            if transaction in pending_transactions:
                # update transaction set is_pending = false where hash = ''
                self._session.query(Transaction).filter(Transaction.hash == transaction.hash).update({
                    Transaction.is_pending: False,
                    Transaction.block_number: transaction.block_number
                })
            elif transaction not in confirmed_transactions:
                self._session.add(transaction)
        self._session.commit()


class EthereumTestnetWallet(EthereumWallet):
    """
    This wallet represents testnet Ethereum.
    """
    TESTNET = True

    def get_name(self):
        return 'Testnet ETH'

    def get_identifier(self):
        return 'TETH'
