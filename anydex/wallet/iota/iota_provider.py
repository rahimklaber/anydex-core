from iota.api import Iota

from wallet.provider import Provider


class IotaProvider(Provider):
    """
    An IOTA provider for interaction with an IOTA ledger.
    """

    def __init__(self, testnet, node=None):
        super().__init__()
        self.api = None
        self.testnet = testnet
        self.node = 'https://nodes.devnet.iota.org:443' if node is None else node

    def initialize_api(self, seed=None):  # seed=None allows to still access the tangle
        """
        Initializes API instance
        """
        # TODO get optimal node
        self.api = Iota(adapter=self.node, seed=seed, testnet=self.testnet)

    def submit_transaction(self, tx):
        """
        Submit a signed transaction to the network
        :param tx: the signed transaction to submit to the network
        :return: the transaction hash
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        return self.api.send_transfer(transfers=[tx])['bundle']

    def get_balance(self, address):
        """
        Get the balance of the given address
        :return: the balance
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        response = self.api.get_balances(addresses=[address])

        if response['balances'][0]:
            return response['balances'][0]
        else:
            raise Exception('No balance found!')

    def get_seed_balance(self):
        """
        Get the balance of the given seed
        :return: the balance
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        account_data = self.api.get_account_data()
        return account_data['balance']

    def get_transactions(self, address):
        """
        Retrieve all the transactions associated with the given address
        :return: A list of all transactions retrieved
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        # TODO: return all transactions associated with a particular address

    def get_seed_transactions(self):
        """
        Retrieve all the transactions associated with the given seed
        :return: A list of all transactions retrieved
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        # fetch transactions from wallet_addresses from account_data
        account_data = self.api.get_account_data()
        wallet_addresses = account_data['addresses']
        transactions = Iota.find_transaction_objects(wallet_addresses)

        return transactions

    def get_pending(self):
        """
        Get the pending balance of the given address
        :return: the balance
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        transactions = self.get_transactions()
        pending_balance = 0

        # iterate through transaction and check whether they are confirmed
        for tx in transactions:
            if not tx.is_confirmed:
                pending_balance += tx.value

        return pending_balance

    def generate_address(self, index=0, security_level=3):
        """
        Get the newly generated address
        :return: the new unspent address
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        return self.api.get_new_addresses(index=index, count=None, security_level=security_level)['addresses'][0]

    def is_spent(self, address):
        """
        Check whether an address is spent
        :return: the new unspent address
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        return self.api.were_addresses_spent_from([address])['states'][0]
