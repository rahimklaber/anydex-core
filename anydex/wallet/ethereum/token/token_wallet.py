# from typing import TypedDict

from ipv8.util import fail, succeed

from anydex.wallet.ethereum.eth_wallet import EthereumWallet, EthereumTestnetWallet
from anydex.wallet.wallet import Wallet, InsufficientFunds
from web3 import Web3
import pathlib
import json

from anydex.wallet.ethereum.eth_db import Transaction
from anydex.wallet.ethereum.token.token_provider import TokenProvider


# class TokenDict(TypedDict):
#     """
#     Definition of a token dict from which a new token wallet can be created
#     """
#     identifier: str
#     name: str
#     precision: int
#     contract_address: str


class Erc20TokenWallet(EthereumTestnetWallet):

    def __init__(self, contract_address, identifier, name, decimals, abi, provider: TokenProvider, db_folder):
        self.identifier = identifier
        self.name = name
        self.decimals = decimals
        self.contract_address = contract_address
        # self.eth_wallet = EthereumWallet(r'C:\Users\Rahim\Desktop\anydex-core\eth.db')
        # self.created = self.eth_wallet.created
        self.contract = Web3().eth.contract(Web3.toChecksumAddress(contract_address), abi=abi)
        self.provider = provider if provider else TokenProvider(contract_address)
        super().__init__(db_folder, self.provider)

    @staticmethod
    def abi_from_json(path_to_file=None):
        if not path_to_file:
            path_to_file = pathlib.Path.joinpath(pathlib.Path(__file__).parent.absolute(), 'abi.json')
        with open(path_to_file) as abi_file:
            abi_json = json.loads(abi_file.read())
        return abi_json

    @classmethod
    def from_dict(cls, token, db_folder):
        """
        Create a new wallet from the given dictionary

        :param db_folder: folder enclosing the database file
        :param token: a dictionary that contains the info defined in the TokenDict class
        :return: a new instance of this class
        """
        abi = cls.abi_from_json()
        return cls(token['contract_address'], token['identifier'], token['name'], token['precision'], abi, None,
                   db_folder)

    def get_identifier(self):
        return self.identifier

    def get_name(self):
        return self.name

    # def create_wallet(self):
    #     if self.created:
    #         return fail(RuntimeError(f'Ethereum Token wallet for {self.get_name()} already exists'))
    #
    #     self._logger.info('Creating Ethereum Token wallet for %s', self.get_name())
    #     self.created = True
    #
    #     return succeed(None)

    # def get_balance(self):
    #     if not self.created:
    #         return succeed({
    #             'available': 0,
    #             'pending': 0,
    #             'currency': self.identifier(),
    #             'precision': self.precision()
    #         })
    #     address = self.get_address()
    #     # self._update_database(self.get_transactions())
    #     # pending_outgoing = self.get_outgoing_amount()
    #     balance = {
    #         'available': self.provider.get_balance(address),  # - pending_outgoing,
    #         'pending': 0,  # self.get_incoming_amount(),
    #         'currency': self.get_identifier(),
    #         'precision': self.precision()
    #     }
    #     return succeed(balance)

    async def transfer(self, amount, address):

        balance = await self.get_balance()
        if balance['available'] < int(amount):
            raise InsufficientFunds('Insufficient funds')

        self._logger.info('Creating Ethereum Token (%s) payment with amount %f to address %s', self.get_name(), amount,
                          address)
        tx = self.contract.functions.transfer(address, amount).buildTransaction(
            {'gas': self.provider.estimate_gas(), 'gasPrice': self.provider.get_gas_price(),
             'chainId': self.chain_id})
        tx.update({'nonce': self.database.get_transaction_count(self.get_address().result())})
        s_tx = self.account.sign_transaction(tx)

        # add transaction to database
        self.database.add(
            Transaction(
                from_=self.get_address().result(),
                to=address,
                value=amount,
                gas=tx['gas'],
                nonce=tx['nonce'],
                gas_price=tx['gasPrice'],
                hash=s_tx['hash'].hex(),
                is_pending=True,
                token_identifier=self.get_identifier()
            )
        )

        return self.provider.submit_transaction(s_tx['rawTransaction'].hex())

    def min_unit(self):
        return 1

    def precision(self):
        return self.decimals
