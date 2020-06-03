import abc
import os
import time
from asyncio import Future
from base64 import b64decode
from decimal import Decimal
from typing import List

from ipv8.util import fail, succeed
from sqlalchemy import func, or_
from stellar_sdk import Keypair, TransactionBuilder, Account, Network
from stellar_sdk.xdr.StellarXDR_pack import StellarXDRUnpacker

from anydex.wallet.cryptocurrency import Cryptocurrency
from anydex.wallet.stellar.xlm_db import initialize_db, Secret, Payment, Transaction
from anydex.wallet.stellar.xlm_provider import StellarProvider
from anydex.wallet.wallet import Wallet, InsufficientFunds


class AbstractStellarWallet(Wallet, metaclass=abc.ABCMeta):
    """
    Wallet provider support for the native stellar token: lumen.
    """

    def __init__(self, db_path, testnet=False, provider: StellarProvider = None):

        super().__init__()
        self.testnet = testnet
        self.provider = provider
        self.network = 'testnet' if self.testnet else Cryptocurrency.STELLAR.value
        self.min_confirmations = 0
        self.unlocked = True
        self._session = initialize_db(os.path.join(db_path, 'stellar.db'))
        self.wallet_name = 'stellar_tribler_testnet' if self.testnet else 'stellar_tribler'

        row = self._session.query(Secret).filter(Secret.name == self.wallet_name).first()
        if row:
            self.keypair = Keypair.from_secret(row.secret)
            self.created = True
            self.account = Account(self.get_address(), self.get_sequence_number())

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
        self.account = Account(self.get_address(), self.get_sequence_number())
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
        latest_sent_payment_sequence = self._session.query(Transaction.sequence_number).filter(
            Transaction.source_account == self.get_address()).order_by(
            Transaction.sequence_number.desc()
        ).first()
        return latest_sent_payment_sequence[0] if latest_sent_payment_sequence else self.provider.get_account_sequence(
            self.get_address())

    async def transfer(self, amount, address, memo_id: int = None, asset='XLM'):
        """
        Transfer stellar lumens to the specified address.
        In the future sending other assets might also be possible.

        Normally a payment operation is used, but if the account is not created
        then an account create operation will be done.

        if you wish to send all of your balance then a merge account operation is used.

        :param amount: amount of lumens to send, in stroop (0.0000001 XLM)
        :param address: address to sent lumens to. Should be a normal encoded public key.
        :param memo_id: memo id for sending lumens to exchanges.
        :param asset: asset type. only XLM is currently supported.
        :return: Transaction hash
        """
        balance = await self.get_balance()

        if balance['available'] < int(amount):
            raise InsufficientFunds('Insufficient funds')

        self._logger.info(f"Creating Stellar Lumens payment with amount {address} to address {address}")
        network = Network.PUBLIC_NETWORK_PASSPHRASE if not self.testnet else Network.TESTNET_NETWORK_PASSPHRASE
        tx_builder = TransactionBuilder(
            source_account=self.account,
            base_fee=self.provider.get_base_fee(),
            network_passphrase=network,
        )
        amount_in_xlm = Decimal(amount / 1e7)  # amount in xlm instead of stroop (0.0000001 xlm)
        if self.provider.check_account_created(address):
            tx_builder.append_payment_op(address, amount_in_xlm, asset)
        else:
            tx_builder.append_create_account_op(address, amount_in_xlm)
        if memo_id:
            tx_builder.add_id_memo(memo_id)
        tx = tx_builder.build()
        tx.sign(self.keypair)
        xdr_tx_envelope = tx.to_xdr()
        # todo add tx to databaese
        tx_hash = self.provider.submit_transaction(xdr_tx_envelope)
        tx_db = Transaction(hash=tx_hash,
                            source_account=self.get_address(),
                            operation_count=len(tx.transaction.operations),
                            sequence_number=tx.transaction.sequence,
                            succeeded=False,
                            transaction_envelope=xdr_tx_envelope,
                            is_pending=True,
                            fee=tx.transaction.fee,
                            )
        self._insert_transaction(tx_db)
        self._session.commit()
        return tx_hash

    def get_address(self):
        if not self.created:
            return ''
        return self.keypair.public_key

    def get_outgoing_amount(self):
        """
        Get the amount of lumens we are sending but is not yet confirmed.
        :return:
        """
        pending_outgoing = self._session.query(func.sum(Payment.amount)) \
            .join(Transaction,
                  Payment.transaction_hash == Transaction.hash).filter(
            Transaction.is_pending.is_(True)).filter(
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

        transactions = self.provider.get_transactions(self.get_address())

        self._update_db(transactions)
        self._session.commit()

        # list of tuples with payment and transaction
        payments = self._session.query(Payment, Transaction).join(Transaction,
                                                                  Payment.transaction_hash == Transaction.hash).filter(
            Transaction.succeeded.is_(True)).filter(
            or_(Payment.from_ == self.get_address(), Payment.to == self.get_address())).all()
        latest_ledger_height = self.provider.get_ledger_height()
        payments_to_return = []
        for payment in payments:
            confirmations = latest_ledger_height - payment[1].ledger_nr + 1 if payment[1].ledger_nr else 0
            payments_to_return.append({
                'id': payment[1].hash,  # use tx hash for now
                'outgoing': payment[0].from_ == self.get_address(),
                'from': payment[0].from_,
                'to': payment[0].to,
                'amount': payment[0].amount,
                'fee_amount': payment[1].fee,
                'currency': self.get_identifier(),
                'timestamp': time.mktime(payment[1].date_time.timetuple()),
                'description': f'confirmations: {confirmations}'
            })

        return succeed(payments_to_return)

    def _update_db(self, transactions: List[Transaction]):
        """
        Update the transactions and payments table with the specified transactions.
        The payments are derived from the transaction envelope.
        """
        pending_txs = self._session.query(Transaction).filter(Transaction.is_pending.is_(True)).all()
        confirmed_txs = self._session.query(Transaction).filter(Transaction.is_pending.is_(False)).all()
        for transaction in transactions:
            if transaction in pending_txs:
                self._update_transaction(transaction)
            elif transaction not in confirmed_txs:
                self._insert_transaction(transaction)
        self._session.commit()
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

    def min_unit(self):
        return 1

    def precision(self):
        return 7

    def monitor_transaction(self, txid):
        monitor_future = Future()

        async def monitor():
            transactions = await self.get_transactions()
            for transaction in transactions:
                if transaction['id'] == txid:
                    self._logger.debug("Found transaction with id %s", txid)
                    monitor_future.set_result(None)
                    monitor_task.cancel()

        self._logger.debug("Start polling for transaction %s", txid)
        monitor_task = self.register_task(f"{self.name}_poll_{txid}", monitor, interval=5)

        return monitor_future

    def _insert_transaction(self, transaction):
        """
        Update a pending transaction and it's corresponding payments
        :param transaction: transaction to update
        """
        self._session.add(transaction)

        xdr_unpacker = StellarXDRUnpacker(b64decode(transaction.transaction_envelope))
        operations = xdr_unpacker.unpack_TransactionEnvelope().tx.operations

        for operation in operations:
            source_account = operation.sourceAccount
            # check if the operation has a source account
            if not source_account:
                source_account = transaction.source_account

            else:
                source_account = Keypair.from_raw_ed25519_public_key(source_account[0].ed25519).public_key
            body = operation.body
            # we only care about create account and payment for the time being
            if body.type == 0:  # create account
                create_account_op = body.createAccountOp
                payment = Payment(
                    amount=create_account_op.startingBalance,
                    asset_type="native",
                    transaction_hash=transaction.hash,
                    to=Keypair.from_raw_ed25519_public_key(create_account_op.destination.ed25519).public_key,
                    from_=source_account
                )
            elif body.type == 1:  # payment
                payment_op = body.paymentOp
                payment = Payment(amount=payment_op.amount,
                                  asset_type="native",
                                  transaction_hash=transaction.hash,
                                  to=Keypair.from_raw_ed25519_public_key(payment_op.destination.ed25519).public_key,
                                  from_=source_account)
            self._session.add(payment)


class StellarWallet(AbstractStellarWallet):

    def __init__(self, db_path, provider: StellarProvider = None):
        super().__init__(db_path, False, provider)

class StellarTestnetWallet(AbstractStellarWallet):
    def __init__(self, db_path, provider: StellarProvider = None):
        super().__init__(db_path, True, provider)
