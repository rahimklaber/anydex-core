import abc

from stellar_sdk import Server

from wallet.provider import Provider


class StellarProvider(Provider, metaclass=abc.ABCMeta):
    """
    Abstract class defining all method a stellar provider needs to have
    """


class HorizonProvider(StellarProvider):
    """
    Horizon is a software that allows you to query nodes via http.
    """

    def __init__(self, horizon_url="https://horizon-testnet.stellar.org/"):
        self.server = Server(horizon_url=horizon_url)

    def submit_transaction(self, tx):
        pass

    def get_balance(self, address):
        # We only care about the native token right now.
        return self.server.accounts().account_id(address).call()["balances"][0]["balance"]

    def get_transactions(self, address):
        return self.server.transactions().for_account(address).call()
