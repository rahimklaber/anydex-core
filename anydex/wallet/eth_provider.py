import abc
from wallet.provider import RequestLimit, Blocked, RateExceeded, RequestException, ConnectionException
import requests
from web3 import Web3
from wallet.eth_db import Transaction
from datetime import datetime
from wallet.provider import Provider
from hexbytes import HexBytes


class EthereumProvider(Provider, metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def get_transaction_count(self, address):
        """
        Retrieve the number of transactions created by this address
        :param address: address from which to retrieve the transaction count
        :return: the number of sent transactions
        """
        return

    def estimate_gas(self, tx):
        """
        Estimate the amount of gas needed for this transaction.
        :param tx: the transaction for which to estimate the gas
        :return: the estimated gas
        """
        return 21000  # just return the gas limit for simple transactions

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
        Note: depending on the implementation start_block and end_block might not be needed.
        :param start_block: block to start searching
        :param end_block: block where to stop searching
        :param address: The address of which to retrieve the transactions
        :return: A list of all transactions retrieved
        """
        return


class InvalidNode(Exception):
    """
    Used for throwing exceptions when the given node is invalid ( you can't connect to it).
    """
    pass


class Web3Provider(EthereumProvider):
    """
    Wrapper around Web3. Used for directly connecting to nodes.
    TODO: check for failed requests.
    TODO: use filters
    (this is not suported by all nodes) to get transactions https://web3py.readthedocs.io/en/stable/filters.html
    """

    def check_connection(self):
        """
        Check the connection to the node
        """
        if not self.w3.isConnected():
            raise ConnectionException(f"We were not able to establish a connection with the node")

    def __init__(self, url):
        self.w3 = Web3(Web3.HTTPProvider(url))
        self.check_connection()

    def get_transaction_count(self, address):
        self.check_connection()
        return self.w3.eth.getTransactionCount(address)

    # def estimate_gas(self, tx):
    #     self.check_connection()
    #     return self.w3.eth.estimateGas(tx)

    def get_gas_price(self):
        self.check_connection()
        return self.w3.eth.gasPrice

    def submit_transaction(self, raw_tx):
        self.check_connection()
        return self.w3.eth.sendRawTransaction(raw_tx)

    def get_balance(self, address):
        self.check_connection()
        return self.w3.eth.getBalance(address)

    def get_transactions(self, address, start_block, stop_block):
        # TODO figure out a faster and more efficiant way to do this.
        # use ethereum-etl ?
        self.check_connection()
        transactions = []
        for block_nr in range(start_block, stop_block + 1):
            current_block = self.w3.eth.getBlock(block_nr, True)
            for tx in current_block["transactions"]:
                if tx["from"] == address or tx["to"] == address:
                    transactions.append(tx)
        return transactions

    def get_transactions_received(self, address, start_block, stop_block):
        # TODO figure out a faster and more efficiant way to do this. filters? Could we use web apis for this?
        # use ethereum-etl ?
        self.check_connection()
        transactions = []
        for block_nr in range(start_block, stop_block + 1):
            current_block = self.w3.eth.getBlock(block_nr, True)
            for tx in current_block["transactions"]:
                if tx["to"] == address:
                    transactions.append(tx)
        return transactions


class EthereumBlockchairProvider(EthereumProvider):
    """
    wrapper around blockchair: https://blockchair.com/api/docs
    TODO: check for the rate limit and also check mempool for tx?
    """

    def __init__(self, base_url="https://api.blockchair.com/", network="ethereum"):
        self.base_url = f"{base_url}{network}"
        self.network = network

    def send_request(self, path, data={}, method="get"):
        """
        Makes a request to the specified path.

        This method was created to have one place where all calls to the requests library are made
        , to reduce the possibility of errors.

        :param path: the path after the base url
        :param data: Data that is send with the request. It is sent as url params if the method is get
        and in the body if the method is post
        :param method: The type of the request (get, post...)
        :return: the response object
        """
        response = None
        if method == "get":
            response = requests.get(f"{self.base_url}{path}", data)
        elif method == "post":
            response = requests.post(f"{self.base_url}{path}", data)
        else:
            raise RequestException(f"Unsupported method: {method} ")
        self._check_response(response)
        return response

    def get_balance(self, address):
        response = self.send_request(f"/dashboards/address/{address}")
        return response.json()["data"][address.lower()]["address"]["balance"]

    def get_transaction_count(self, address):
        # Todo: return also unconfirmed txs
        response = self.send_request(f"/dashboards/address/{address}")
        return response.json()["data"][address.lower()]["address"]["transaction_count"]

    # def estimate_gas(self, tx):
    #     # Todo estimate the gas better or just set to the max for smiple transactions (21000)
    #     response = self.send_request("/stats")
    #     return response.json()["data"]["median_simple_transaction_fee_24h"]

    def get_gas_price(self):
        response = self.send_request("/stats")
        return response.json()["data"]["mempool_median_gas_price"]

    def submit_transaction(self, raw_tx):
        response = self.send_request("/push/transactions", data={"data": raw_tx}, method="post")
        return response.json()["data"]["transaction_hash"]

    def get_transactions_received(self, address):
        received = self.send_request("/transactions", data={"q": f"recipient({address})"})
        return self._normalize_transactions(received.json()["data"])

    def get_transactions(self, address):
        received = self.send_request("/transactions", data={"q": f"recipient({address})"})
        sent = self.send_request("/transactions", data={"q": f"sender({address})"})
        received_data = received.json()["data"]
        sent_data = sent.json()["data"]
        txs = received_data + sent_data
        return self._normalize_transactions(txs)

    def _check_response(self, response):
        """
        Checks the response for errors, such as exceeding request limits.
        :param response: the response object
        """
        # status codes are described in : https://blockchair.com/api/docs
        # 402, 429 : if you exceed the request limit
        # 430, 434, 503 : if you have been blocked
        # 435: if 5 request/second are sent
        request_exceeded = [402, 429]
        blocked_codes = [430, 434, 503]
        if response.status_code in request_exceeded:
            raise RequestLimit(
                "The server indicated the request limit has been exceeded")
        elif response.status_code in blocked_codes:
            raise Blocked("The server has blocked you")
        elif response.status_code == 435:
            raise RateExceeded("You are sending requests too fast")
        elif response.status_code != 200:
            raise RequestException(f"something went wrong, status code: {response.status_code}")

    def _normalize_transactions(self, txs):
        """
        Turns a list of txs from blockchair into the tx format of the wallet.
        :param txs: Txs from blockchair
        :return: list of Transaction objects
        """
        normalized_txs = []
        for tx in txs:
            normalized_txs.append(self._normalize_transaction(tx))
        return normalized_txs

    def _normalize_transaction(self, tx) -> Transaction:
        """
        Turns the tx from blockchair into the tx format of the wallet.
        :param tx: Tx from blockchair
        :return: Transaction object
        """

        return Transaction(
            block_number=tx["block_id"],
            hash=tx["hash"],
            date_time=datetime.fromisoformat(tx["time"]),
            to=tx["recipient"],
            from_=tx["sender"],
            value=tx["value"],
            gas_price=tx["gas_price"],
            gas=tx["gas_used"],
            nonce=tx["nonce"]
        )


class EthereumBlockcypherProvider(EthereumProvider):
    """
    Wrapper around blockcypher
    """

    def __init__(self, api_url="https://api.blockcypher.com/", network="ethereum"):
        if network == "ethereum":
            self.base_url = f"{api_url}1/eth/main/"
        elif network == "testnet":
            self.base_url = f"{api_url}1/beth/test/"
        else:
            # raise invalidargumentexception
            pass

    def send_request(self, path, data={}, method="get"):
        """
        Makes a request to the specified path.

        This method was created to have one place where all calls to the requests library are made
        , to reduce the possibility of errors.

        :param path: the path after the base url
        :param data: Data that is send with the request. It is sent as url params if the method is get
        and in the body if the method is post
        :param method: The type of the request (get, post...)
        :return: the response object
        """
        response = None
        if method == "get":
            response = requests.get(f"{self.base_url}{path}", data)
        elif method == "post":
            response = requests.post(f"{self.base_url}{path}", data)
        else:
            raise RequestException(f"Unsupported method: {method} ")
        self._check_response(response)
        return response

    def get_transaction_count(self, address):
        response = self.send_request(f"addrs/{address}/balance")
        return response.json()["final_n_tx"]

    # def estimate_gas(self, tx):
    #     pass

    def get_gas_price(self):
        response = self.send_request("")
        return response["medium_gas_price"]

    def get_balance(self, address):
        response = self.send_request(f"addrs/{address}/balance")
        return response.json()["balance"]

    def get_transactions(self, address, start_block=None, end_block=None):
        pass

    def get_transactions_received(self, address, start_block=None, end_block=None):
        pass

    def submit_transaction(self, tx):
        pass

    def _check_response(self, response):
        """
        Checks the response for errors, such as exceeding request limits.
        :param response: the response object
        """
        # 429 request limit : 3/sec 200/h
        if response.status_code == 429:
            raise RateExceeded(
                "The server indicated the rate limit has been reached")
        elif response.status_code != 200:
            raise RequestException("something went wrong")
