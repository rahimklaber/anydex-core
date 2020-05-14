import abc

from web3 import Web3

from wallet.provider import Provider


class EthereumProvider(Provider, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_transaction_count(self, address):
        """
        Retrieve the number of transactions created by this address
        :param address: address from which to retrieve the transaction count
        :return: the number of sent transactions
        """
        return

    @abc.abstractmethod
    def estimate_gas(self, tx):
        """
        Estimate the amount of gas needed for this transaction.
        :param tx: the transaction for which to estimate the gas
        :return: the estimated gas
        """
        return

    @abc.abstractmethod
    def get_gas_price(self):
        """
        Retrieve the current gas price
        :return: the current gas price
        """
        return

    @abc.abstractmethod
    def get_transactions(self, address, start_block=None, end_block=None):
        """
        Retrieve all the transactions associated with the given address

        Note: depending on the implementation start_block and end_block might not be needed.
        :param start_block: block to start searching from
        :param end_block: block where to stop searching
        :param address: The address of which to retrieve the transactions
        :return: A list of all transactions retrieved
        """
        return

    @abc.abstractmethod
    def get_transactions_received(self, address, start_block=None, end_block=None):
        """
        returns the transactions where you are the recipient.

        In most cases this method will be enough since we should persist transactions when we sent them.
        :param start_block: block to start searching
        :param end_block: block where to stop searching
        :param address: The address of which to retrieve the transactions
        """
        return


class InvalidNode(Exception):
    """
    Used for throwing exceptions when the given node is invalid ( you can't connect to it).
    """
    pass


class Web3Provider(EthereumProvider):
    """
    Wrapper around Web3.
    Used for directly connecting to nodes.
    #TODO: check for failed requests.
    """

    def __init__(self, url):
        self.w3 = Web3(Web3.HTTPProvider(url))
        if not self.w3.isConnected():
            raise InvalidNode(f"invalid node url: {url}, the node may be down")

    def get_transaction_count(self, address):
        return self.w3.eth.getTransactionCount(address)

    def estimate_gas(self, tx):
        return self.w3.eth.estimateGas(tx)

    def get_gas_price(self):
        return self.w3.eth.gasPrice

    def submit_transaction(self, raw_tx):
        return self.w3.eth.sendRawTransaction(raw_tx)

    def get_balance(self, address):
        return self.w3.eth.getBalance(address)

    def get_transactions(self, address, start_block, stop_block):
        # use ethereum-etl ?
        transactions = []
        for block_nr in range(start_block, stop_block + 1):
            current_block = self.w3.eth.getBlock(block_nr, True)
            for tx in current_block["transactions"]:
                if tx["from"] == address or tx["to"] == address:
                    transactions.append(tx)
        return transactions

    def get_transactions_received(self, address, start_block, stop_block):
        # use ethereum-etl ?
        transactions = []
        for block_nr in range(start_block, stop_block + 1):
            current_block = self.w3.eth.getBlock(block_nr, True)
            for tx in current_block["transactions"]:
                if tx["to"] == address:
                    transactions.append(tx)
        return transactions
