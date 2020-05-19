from web3 import Web3
from ipv8.util import fail, succeed

from anydex.wallet.cryptocurrency import Cryptocurrency
from anydex.wallet.ethereum.eth_db import initialize_db, Key, Transaction
from anydex.wallet.ethereum.eth_provider import NotSupportedOperationException, EthereumBlockchairProvider
from anydex.wallet.wallet import Wallet, InsufficientFunds


class EthereumWallet(Wallet):
    """
    This class is responsible for handling your Ethereum wallet.
    """
    TESTNET = False
    default_provider = EthereumBlockchairProvider()

    def __init__(self, provider, db_path):
        super().__init__()
        self.provider = provider

        self.network = 'testnet' if self.TESTNET else Cryptocurrency.ETHEREUM.value
        self.min_confirmations = 0
        self.unlocked = True
        self.session = initialize_db(db_path)
        self.wallet_name = 'tribler_testnet' if self.TESTNET else 'tribler'

        row = self.session.query(Key).filter(Key.name == self.wallet_name).first()
        if row:
            self.account = Web3.eth.account.from_key(row)
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
            self.account = Web3.eth.account.create()
            self.created = True

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
        # TODO verify .get_balance() maintains same format as above dictionary
        return succeed(self.provider.get_balance(address))

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
        self.session.add(
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
        self.session.commit()
        return signed['hash']

    def get_address(self):
        if not self.account:
            return ''
        return self.account.address

    def get_transactions(self):
        """
        Retrieve list of transactions from provider.
        If the operation is not supported by the provider, use a default provider.

        :return: list of transactions
        """
        if not self.account:
            return succeed([])
        try:
            transactions = self.provider.get_transactions()
        except NotSupportedOperationException:
            # use `default` provider to perform operation
            # here: BlockChairEthereumProvider
            transactions = self.default_provider.get_transactions(self.get_address())

        self.update_database(transactions)
        return succeed(transactions)

    def min_unit(self):
        # TODO determine minimal transfer unit
        return 1

    def precision(self):
        return 18

    def get_identifier(self):
        return 'ETH'

    def update_database(self, transactions):
        """
        Update pending transactions in the database.
        Set is_pending field to False if they can be retrieved by a provider.
        Set block_number to value retrieved by provider.

        :param transactions: list of transactions retrieved by self.provider
        """
        pending_transactions = self.session.query(Transaction).filter(Transaction.is_pending)
        self._logger.debug('Update `is_pending` and `block_number` fields for transactions')
        for pending_transaction in pending_transactions:
            if pending_transaction in transactions:
                candidate = transactions[transactions.index(pending_transaction)]
                # update transaction set is_pending = false where hash = ''
                self.session.query(Transaction).filter(Transaction.hash == candidate.hash).update({
                    Transaction.is_pending: False,
                    Transaction.block_number: candidate.block_number
                })


class EthereumTestnetWallet(EthereumWallet):
    """
    This wallet represents testnet Ethereum.
    """
    TESTNET = True

    def get_name(self):
        return 'Testnet ETH'

    def get_identifier(self):
        return 'TETH'
