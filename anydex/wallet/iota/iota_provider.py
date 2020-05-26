from iota.api import Iota

from wallet.provider import Provider


class IotaProvider(Provider):
    """
    An IOTA provider for interaction with an IOTA ledger.
    """

    def __init__(self, testnet, seed=None, node='https://nodes.devnet.iota.org:443'):
        super().__init__()
        self.testnet = testnet,
        self.node = node,
        self.api = self.initialize_api(seed)

    def initialize_api(self, seed):
        """
        Initializes API instance
        """
        # TODO: ensure couple of checked nodes / fetch regularly best from site such as https://iota-nodes.net/
        # noinspection PyTypeChecker
        api = Iota(adapter=self.node, seed=seed, testnet=self.testnet)
        return api

    def submit_transaction(self, tx):
        """
        Submit a signed transaction to the network
        :param tx: the signed transaction to submit to the network
        :return: the transaction hash
        """
        response = self.api.send_transfer(transfers=[tx])
        return response['bundle']

    def get_balance(self, address):
        """
        Get the balance of the given address
        :return: the balance
        """
        response = self.api.get_balances(addresses=[address])
        return response['balances'][0]

    def get_seed_balance(self):
        """
        Get the balance of the given seed
        :return: the balance
        """
        account_data = self.api.get_account_data()
        return account_data['balance']

    def get_transactions(self, address):
        """
        Retrieve all the transactions associated with the given address
        :return: A list of all transactions retrieved
        """
        transactions = self.api.find_transaction_objects(addresses=[address])
        return transactions

    def get_seed_transactions(self):
        """
        Retrieve all the transactions associated with the given seed
        :return: A list of all transactions retrieved
        """
        # fetch transactions from wallet_addresses from account_data
        account_data = self.api.get_account_data()
        wallet_addresses = account_data['addresses']
        transactions = Iota.find_transaction_objects(wallet_addresses)

        return transactions

    def generate_address(self, index=0, security_level=3):
        """
        Get the newly generated address
        :return: the new unspent address
        """
        new_addresses = self.api.get_new_addresses(index=index, count=None, security_level=security_level)
        return new_addresses['addresses'][0]

    def is_spent(self, address):
        """
        Check whether an address is spent
        :return: the new unspent address
        """
        response = self.api.were_addresses_spent_from([address])
        return response['states'][0]
