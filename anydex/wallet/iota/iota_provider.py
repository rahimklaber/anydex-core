from iota.api import Iota

from wallet.provider import Provider


class IotaProvider(Provider):
    """
    An IOTA provider for interaction with an IOTA ledger.
    """

    def __init__(self):
        super().__init__()
        self.api = None
        self.initialized = False
        self.node = 'https://nodes.devnet.iota.org:443'
        self.testnet = True

    def initialize_api(self, seed):
        """
        Initializes API instance
        """
        # TODO get optimal node
        self.api = Iota(self.node, seed, testnet=self.testnet)
        self.initialized = True

    def submit_transaction(self, tx):
        """
        Submit a signed transaction to the network
        :param tx: the signed transaction to submit to the network
        :return: the transaction hash
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        self.api.send_transfer(transfers=[tx])

    def get_balance(self, **kwargs):
        """
        Get the balance of the given address
        :return: the balance
        """
        if self.api is None:
            raise Exception("API is not initialized!")

        account_data = self.api.get_account_data()
        return account_data['balance']

    def get_transactions(self, **kwargs):
        """
        Retrieve all the transactions associated with the given address
        :return: A list of all transactions retrieved
        """
        if self.api is None:
            raise Exception("API is not initialized!")

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

        address = self.api.get_new_addresses(index=index, count=None, security_level=security_level)['addresses'][0]
        # is_spent = self.api.were_addresses_spent_from([address])['states'][0]
        #
        # if is_spent:
        #     raise Exception("Generated address already spent!")
        return address

