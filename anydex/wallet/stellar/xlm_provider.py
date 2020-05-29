import abc

from stellar_sdk import Server

from wallet.provider import Provider
from wallet.stellar.xlm_db import Payment
from datetime import datetime


class StellarProvider(Provider, metaclass=abc.ABCMeta):
    """
    Abstract class defining all method a stellar provider needs to have
    """


class HorizonProvider(StellarProvider):
    """
    Horizon is a software that allows you to query nodes via http.
    """

    def __init__(self, horizon_url='https://horizon-testnet.stellar.org/'):
        self.server = Server(horizon_url=horizon_url)

    def submit_transaction(self, tx):
        pass

    def get_balance(self, address):
        # We only care about the native token right now.
        return self.server.accounts().account_id(address).call()['balances'][0]['balance']

    def get_transactions(self, address):
        response = self.server.payments().for_account(address).call()
        payments = response['_embedded']['records']
        return self._normalize_payments_all_types(payments)

    def _normalize_payments_all_types(self, payments):
        """
        Transform a list of payments (of all types) from the api to the format used in this project
        :param payments: List of payments from the api
        :return: A list of payment objects
        """
        transformed_payments = []
        for payment in payments:
            transformed_payments.append(self._normalize_payment_all_type(payment))
        return transformed_payments

    def _normalize_create_account(self, payment) -> Payment:
        """
        Transform a creat account operation into a payment object
        :param payment: create account payment from api
        :return: Payment object
        """
        return Payment(payment_id=int(payment['id']),
                       from_=payment['funder'],
                       to=payment['account'],
                       amount=int(float(payment['starting_balance']) * 1e7),  # todo make this not use a literal
                       asset_type='native',
                       transaction_hash=payment['transaction_hash'],
                       date_time=datetime.fromisoformat(payment['created_at'][:-1]),
                       succeeded=payment['transaction_successful'])

    def _normalize_payment(self, payment) -> Payment:
        """
        Transform a payment (operation type == 'payment') from the api to the format used in this project
        :param payment: Payment from the api
        :return: A list of payment objects
        """
        return Payment(payment_id=int(payment['id']),
                       from_=payment['from'],
                       to=payment['to'],
                       amount=int(float(payment['amount']) * 1e7),  # todo make this not use a literal
                       asset_type=payment['asset_type'],
                       transaction_hash=payment['transaction_hash'],
                       date_time=datetime.fromisoformat(payment['created_at'][:-1]),
                       succeeded=payment['transaction_successful'])

    def _normalize_payment_all_type(self, payment) -> Payment:
        """
        Transform a any type of payment payment from the api in the format we use

        :param payment: Payment from api
        :return: Payment object
        """
        if payment['type'] == 'create_account':
            return self._normalize_create_account(payment)
        elif payment['type'] == 'payment':
            return self._normalize_payment(payment)
        else:
            raise RuntimeError("Payment type not supported")
