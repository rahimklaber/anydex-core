import abc

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
