from web3.auto import w3

from anydex.wallet.ethereum.eth_provider import Web3Provider
from anydex.wallet.provider import Provider


class TokenProvider(Provider):

    def __init__(self, contract_address, web3_provider_url):
        """
        Instantiate TokenProvider attributs.

        :param contract_address: main token contract address
        :param abi: abi or application binary interface
        :param web3_provider_url: web3 provider endpoint
        """
        abi = self.get_abi()
        self.contract = w3.eth.contract(contract_address, abi=abi)
        self._web3_provider = Web3Provider(web3_provider_url)

    @staticmethod
    def get_abi():
        """
        Read locally stored ABI in as string
        :return: str formatted ABI
        """
        return ''

    def get_transaction_count(self, address):
        """
        Retrieve the number of transactions created by this address.
        :param address: address from which to retrieve the transaction count
        :return: the number of sent transactions
        """
        return self._web3_provider.get_transaction_count(address)

    def estimate_gas(self):
        """
        Estimate the amount of gas needed for this transaction.
        :return: the estimated gas
        """
        return self._web3_provider.estimate_gas()

    def get_gas_price(self):
        """
        Retrieve the current gas price.
        :return: the current gas price
        """
        return self._web3_provider.get_gas_price()

    def get_transactions(self, address, start_block=None, end_block=None):
        """
        Retrieve all the transactions associated with the given address.

        Note: depending on the implementation start_block and end_block might not be needed.
        :param start_block: block to start searching from
        :param end_block: block where to stop searching
        :param address: The address of which to retrieve the transactions
        :return: A list of all transactions retrieved
        """
        return self._web3_provider.get_transactions(address, start_block, end_block)

    def get_transactions_received(self, address, start_block=None, end_block=None):
        """
        returns the transactions where you are the recipient.

        In most cases this method will be enough since we should persist transactions when we sent them.
        Note: depending on the implementation start_block and end_block might not be needed.
        :param start_block: block to start searching
        :param end_block: block where to stop searching
        :param address: The address of which to retrieve the transactions
        :return: A list of all transactions retrieved
        """
        return self._web3_provider.get_transactions_received(address, start_block, end_block)

    def get_latest_blocknr(self):
        """
        Retrieve the latest block's number.
        :return: latest block number
        """
        return self._web3_provider.get_latest_blocknr()

    def submit_transaction(self, tx):
        """
        Provide signed transaction for submission to network.

        :param tx: signed transcation (using `w3.eth.account.signTransaction()`)
        """
        tx_hash = w3.eth.sendRawTransaction(tx.rawTransaction)
        return tx_hash

    def get_balance(self, address):
        """
        Get balance of given address.
        Divide raw balance by precision count.

        :param address: str representation of an address
        :return: balance
        """
        return self.contract.functions.balanceOf(address).call() // (10 ** self.get_precision())

    def get_contract_address(self):
        """
        Get main token address.
        :return: str representation of main token address
        """
        return self.contract.address

    def get_precision(self):
        """
        Get precision in decimal places of token contract.
        :return: precision in int
        """
        return self.contract.functionas.decimals.call()

    def get_raw_total_supply(self):
        """
        Get raw total supply of token constract.
        :return: integer representation of total supply
        """
        return self.contract.functions.totalSupply().call() // (10 ** self.get_precision())

    def get_contract_name(self):
        """
        Get name of contract.

        :return: str name
        """
        return self.contract.functions.name().call()

    def get_contract_symbol(self):
        """
        Get token contract symbol.

        :return: str symbol
        """
        return self.contract.functions.symbol().call()
