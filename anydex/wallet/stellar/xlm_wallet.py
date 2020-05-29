import os
import time

from ipv8.util import fail, succeed
from sqlalchemy import func
from stellar_sdk import Keypair, TransactionBuilder, Account

from wallet.cryptocurrency import Cryptocurrency
from wallet.stellar.xlm_db import initialize_db, Secret, Payment, Transaction
from wallet.stellar.xlm_provider import StellarProvider
from wallet.wallet import Wallet
from stellar_sdk.xdr.StellarXDR_pack import StellarXDRUnpacker

class StellarWallet(Wallet):
    """
    Wallet provider support for the native stellar token: lumen.
    """
    TESTNET = False

    def __init__(self, db_path, provider: StellarProvider = None):

        super().__init__()
        self.provider = provider
        self.network = 'testnet' if self.TESTNET else Cryptocurrency.STELLAR.value
        self.min_confirmations = 0
        self.unlocked = True
        self._session = initialize_db(os.path.join(db_path, 'stellar.db'))
        self.wallet_name = 'stellar_tribler_testnet' if self.TESTNET else 'stellar_tribler'

        row = self._session.query(Secret).filter(Secret.name == self.wallet_name).first()
        if row:
            self.keypair = Keypair.from_secret(row.secret)
            self.account = Account(self.get_address(), )
            self.created = True

    def get_identifier(self):
        return 'XLM'

    def get_name(self):
        return Cryptocurrency.STELLAR.value

    def create_wallet(self):
        if self.created:
            return fail(RuntimeError(f'Stellar wallet with name {self.wallet_name} already exists'))

        self._logger.info(f'Creating Stellar wallet with name {self.wallet_name}')
        keypair = Keypair.random()
        self.keypair = keypair
        self.created = True
        self._session.add(Secret(name=self.wallet_name, secret=keypair.secret, address=keypair.public_key))
        self._session.commit()

        return succeed(None)

    def get_balance(self):

        if not self.created:
            return succeed({
                'available': 0,
                'pending': 0,
                'currency': 'XLM',
                'precision': self.precision()
            })
        xlm_balance = int(float(self.provider.get_balance(
            address=self.get_address())) * 1e7)  # balance is not in smallest denomination
        pending_outgoing = self.get_outgoing_amount()
        balance = {
            'available': xlm_balance - pending_outgoing,
            'pending': 0,  # transactions are confirmed every 5 secs, so is this worth doing?
            'currency': 'XLM',
            'precision': self.precision()
        }
        return succeed(balance)

    def get_sequence_number(self):
        latest_sent_payment_sequence = self._session.query(Payment).filter(Payment.from_ == self.get_address()).filter(

        )

    async def transfer(self, amount, address, asset='XLM'):
        tx = TransactionBuilder()

    def get_address(self):
        if not self.created:
            return ''
        return self.keypair.public_key

    def get_outgoing_amount(self):
        """
        Get the amount of lumens we are sending but is not yet confirmed.
        :return:
        """
        pending_outgoing = self._session.query(func.sum(Payment.amount)).filter(Payment.is_pending.is_(True)).filter(
            Payment.from_ == self.get_address()).first()[0]

        return pending_outgoing if pending_outgoing else 0

    def get_transactions(self):
        """
        Transactions in stellar is different from etheruem or bitcoin.
        A payment in stellar is the same as a transactions in ethereum or bitcoin.
        Even though this method is called get_transactions (for compat with the wallet api) it returns the `payments`
        related to this wallet.
        :return: list of payments related to the wallet.
        """
        if not self.created:
            return succeed(None)

        payments = self.provider.get_transactions(self.get_address())

        self._update_db(payments)

        payments_to_return = []
        for payment in payments:
            payments_to_return.append({
                'id': payment.payment_id,
                'outgoing': payment.from_ == self.get_address(),
                'from': payment.from_,
                'to': payment.to,
                'amount': payment.amount,
                'fee_amount': 0,  # placeholder
                'currency': self.get_identifier(),
                'timestamp': time.mktime(payment.date_time.timetuple()),
                'description': f'memo:  '
            })

        return succeed(payments_to_return)

    def _update_db(self, transactions: Transaction):
        """
        Update the transactions and payments table with the specified transactions.
        The payments are derived from the transaction envelope.
        """
        pending_txs = self._session.query(Transaction).filter(Transaction.is_pending.is_(True)).all()
        confirmed_txs = self._session.query(Transaction).filter(Transaction.is_pending.is_(False)).all()
        for transaction in transactions:
            if transaction in pending_txs:
                self._update_transaction(transaction)
        # pending_payments = self._session.query(Payment).filter(Payment.is_pending.is_(True)).all()
        # confirmed_payments = self._session.query(Payment).filter(Payment.is_pending.is_(False)).all()
        # for payment in payments:
        #     if payment in pending_payments:
        #         self._session.query(Payment).filter(Payment.payment_id == payment.payment_id).update({
        #             Payment.is_pending: False,
        #             Payment.succeeded: payment.succeeded
        #         })
        #     elif payment not in confirmed_payments:
        #         self._session.add(payment)
        # self._session.commit()

    def _update_transaction(self, transaction):
        """
        Update a pending transaction and it's corresponding payments
        :param transaction: transaction to update
        """
        self._session.query(Transaction).filter(Transaction.hash == transaction.hash).update({
            Transaction.is_pending: False,
            Transaction.succeeded: transaction.succeeded
        })
        from base64 import b64decode
        xdr_unpacker = StellarXDRUnpacker(b64decode(transaction.transaction_envelope))
        xdr_unpacker.unpack_TransactionEnvelope()


    def min_unit(self):
        return 1

    def precision(self):
        return 7

    def monitor_transaction(self, txid):
        pass
