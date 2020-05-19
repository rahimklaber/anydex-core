from anydex.wallet.wallet import Wallet

from web3 import Web3

from anydex.wallet.eth_db import initialize_db, Key, Transaction
from anydex.wallet.eth_provider import NotSupportedOperationException


class EthereumWallet(Wallet):
    TESTNET = False

    def __init__(self, provider, db_path):
        super().__init__()
        self.provider = provider

        self.network = 'testnet' if self.TESTNET else 'ethereum'
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
        return 'Ethereum'

    def create_wallet(self, *args, **kwargs):
        if not self.account:
            self.account = Web3.eth.account.create()

    def get_balance(self):
        address = self.get_address()
        return self.provider.get_balance(address)

    async def transfer(self, amount, address):
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
                hash=transaction['hash'],
                is_pending=True
            )
        )
        self.session.commit()

        return signed

    def get_address(self):
        if self.account:
            return self.account.address

    def get_transactions(self):
        try:
            self.provider.get_transactions()
        except NotSupportedOperationException:
            pass

    def min_unit(self):
        # TODO determine minimal transfer unit
        return 1

    def precision(self):
        return 18

    def get_identifier(self):
        return 'ETH'
