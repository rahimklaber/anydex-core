from iota.api import Iota

from anydex.wallet.provider import Provider


class IotaProvider(Provider):
    """
    An IOTA provider for interaction with an IOTA ledger.
    """

    def __init__(self, testnet=True, node=None, seed=None):
        super().__init__()
        self.testnet = testnet
        self.api = self.initialize_api(node, seed)

    def initialize_api(self, node, seed):
        """
        Initialize an API instance
        :param node: node to which API should connect
        :param seed: seed to use for all further API calls
        :return: initialized API
        """
        if node is None:  # TODO: check whether mainnet node works
            if self.testnet:
                node = 'https://nodes.devnet.iota.org:443'
            else:
                node = 'https://nodes.thetangle.org:443'

        api = Iota(adapter=node, seed=seed, devnet=self.testnet, local_pow=True)
        return api

    def submit_transaction(self, tx):
        """
        Submit a proposed transaction to the network
        :param tx: the proposed transaction to submit to the network
        :return: the bundle containing the transaction
        """
        response = self.api.send_transfer(transfers=[tx])
        return response['bundle']

    def get_balance(self, address):
        """
        Get the balance of the given address
        :param address: address whose balance is being retrieved
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
        :param address: address whose transactions are being retrieved
        :return: a list of all fetched transactions
        """
        transactions = self.api.find_transaction_objects(addresses=[address])
        return transactions

    def get_seed_transactions(self):
        """
        Retrieve all the transactions associated with the given seed
        :return: a list of all fetched transactions
        """
        # fetch transactions from wallet_addresses from account_data
        account_data = self.api.get_account_data()
        wallet_addresses = account_data['addresses']
        transactions = self.api.find_transaction_objects(addresses=wallet_addresses)
        return transactions

    def get_bundles(self, tail_tx_hashes: list):
        """
        Retrieve all the bundles associated with the given tail transaction hashes
        :param tail_tx_hashes: tail transaction hash using which bundle can be fetched
        :return: a list of all fetched bundles
        """
        bundles = self.api.get_bundles(tail_tx_hashes)['bundles']
        return bundles

    def generate_address(self, index=0, security_level=3):
        """
        Get the newly generated address
        :param index: index from which start fetching a non-spent address
        :param security_level: factor that affects private key length; from 1 to 3
        :return: the new unspent address
        """
        new_addresses = self.api.get_new_addresses(index=index, count=1, security_level=security_level)
        return new_addresses['addresses'][0]

    def is_spent(self, address):
        """
        Check whether an address is spent
        :param address: address to check whether spent
        :return: boolean
        """
        response = self.api.were_addresses_spent_from([address])
        return response['states'][0]
