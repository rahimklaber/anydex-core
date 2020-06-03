import unittest
from asyncio import Future

from iota import Address, Transaction, Bundle
from iota.crypto.types import Seed
from ipv8.util import succeed
from sqlalchemy.orm import session as db_session

from anydex.test.base import AbstractServer
from anydex.wallet.iota.iota_database import DatabaseBundle, DatabaseAddress, DatabaseTransaction, DatabaseSeed
from anydex.wallet.iota.iota_provider import IotaProvider
from anydex.wallet.iota.iota_wallet import IotaWallet, IotaTestnetWallet
from anydex.wallet.wallet import InsufficientFunds


class TestIotaWallet(AbstractServer):

    def setUp(self):
        super(TestIotaWallet, self).setUp()
        self.tx1 = Transaction.from_tryte_string(
            b'PCGDSCPCSCGD99999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'9999999999999999999999999999999999999999999999VETULPZOCVDREKATOFLE'
            b'RUIOSIIG9XTCMMVTDPFFPSDXXPMLRAZXUBLLRMTEWJZPBNJBAMFCJQDSWPTV9OB999'
            b'9999999999999999999999EINFACHIOTA999999999999999999999999999999999'
            b'9C99999999NXPJH9TJ99PQGWXYAJKDTNHBWPJURJTIIYSNZH9EUYTDJGAICWTE9LC9'
            b'KPLVTLIDSJSGRGWAUBFPAPKXAFIFEQNHUHEJNRBARNJYEEVIUPZXMTLTWGOBDLKMGO'
            b'V9ISJMYPWLMHMXZLQKUMNBIFBEAUJW9CBERPC999JNOBIMVGJEHXXTMMEDOEJFYKIM'
            b'EFGA9MAITXIBCPCDJSDPMKXFSXRIMBDHUFEYOV9GWAQVXEHWLKMZ999EINFACHIOTA'
            b'9999999999999999999999999999999999999999999EX99999999CCA9999999999'
            b'9999')

        self.txn = Transaction.from_tryte_string(
            b'GYPRVHBEZOOFXSHQBLCYW9ICTCISLHDBNMMVYD9JJHQMPQCTIQAQTJNNNJ9IDXLRCC'
            b'OYOXYPCLR9PBEY9ORZIEPPDNTI9CQWYZUOTAVBXPSBOFEQAPFLWXSWUIUSJMSJIIIZ'
            b'WIKIRH9GCOEVZFKNXEVCUCIIWZQCQEUVRZOCMEL9AMGXJNMLJCIA9UWGRPPHCEOPTS'
            b'VPKPPPCMQXYBHMSODTWUOABPKWFFFQJHCBVYXLHEWPD9YUDFTGNCYAKQKVEZYRBQRB'
            b'XIAUX9SVEDUKGMTWQIYXRGSWYRK9SRONVGTW9YGHSZRIXWGPCCUCDRMAXBPDFVHSRY'
            b'WHGB9DQSQFQKSNICGPIPTRZINYRXQAFSWSEWIFRMSBMGTNYPRWFSOIIWWT9IDSELM9'
            b'JUOOWFNCCSHUSMGNROBFJX9JQ9XT9PKEGQYQAWAFPRVRRVQPUQBHLSNTEFCDKBWRCD'
            b'X9EYOBB9KPMTLNNQLADBDLZPRVBCKVCYQEOLARJYAGTBFR9QLPKZBOYWZQOVKCVYRG'
            b'YI9ZEFIQRKYXLJBZJDBJDJVQZCGYQMROVHNDBLGNLQODPUXFNTADDVYNZJUVPGB9LV'
            b'PJIYLAPBOEHPMRWUIAJXVQOEM9ROEYUOTNLXVVQEYRQWDTQGDLEYFIYNDPRAIXOZEB'
            b'CS9P99AZTQQLKEILEVXMSHBIDHLXKUOMMNFKPYHONKEYDCHMUNTTNRYVMMEYHPGASP'
            b'ZXASKRUPWQSHDMU9VPS99ZZ9SJJYFUJFFMFORBYDILBXCAVJDPDFHTTTIYOVGLRDYR'
            b'TKHXJORJVYRPTDH9ZCPZ9ZADXZFRSFPIQKWLBRNTWJHXTOAUOL9FVGTUMMPYGYICJD'
            b'XMOESEVDJWLMCVTJLPIEKBE9JTHDQWV9MRMEWFLPWGJFLUXI9BXPSVWCMUWLZSEWHB'
            b'DZKXOLYNOZAPOYLQVZAQMOHGTTQEUAOVKVRRGAHNGPUEKHFVPVCOYSJAWHZU9DRROH'
            b'BETBAFTATVAUGOEGCAYUXACLSSHHVYDHMDGJP9AUCLWLNTFEVGQGHQXSKEMVOVSKQE'
            b'EWHWZUDTYOBGCURRZSJZLFVQQAAYQO9TRLFFN9HTDQXBSPPJYXMNGLLBHOMNVXNOWE'
            b'IDMJVCLLDFHBDONQJCJVLBLCSMDOUQCKKCQJMGTSTHBXPXAMLMSXRIPUBMBAWBFNLH'
            b'LUJTRJLDERLZFUBUSMF999XNHLEEXEENQJNOFFPNPQ9PQICHSATPLZVMVIWLRTKYPI'
            b'XNFGYWOJSQDAXGFHKZPFLPXQEHCYEAGTIWIJEZTAVLNUMAFWGGLXMBNUQTOFCNLJTC'
            b'DMWVVZGVBSEBCPFSM99FLOIDTCLUGPSEDLOKZUAEVBLWNMODGZBWOVQT9DPFOTSKRA'
            b'BQAVOQ9RXWBMAKFYNDCZOJGTCIDMQSQQSODKDXTPFLNOKSIZEOY9HFUTLQRXQMEPGO'
            b'XQGLLPNSXAUCYPGZMNWMQWSWCKAQYKXJTWINSGPPZG9HLDLEAWUWEVCTVRCBDFOXKU'
            b'ROXH9HXXAXVPEJFRSLOGRVGYZASTEBAQNXJJROCYRTDPYFUIQJVDHAKEG9YACV9HCP'
            b'JUEUKOYFNWDXCCJBIFQKYOXGRDHVTHEQUMHO999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999999999999999999999999999999999999'
            b'999999999999RKWEEVD99A99999999A99999999NFDPEEZCWVYLKZGSLCQNOFUSENI'
            b'XRHWWTZFBXMPSQHEDFWZULBZFEOMNLRNIDQKDNNIELAOXOVMYEI9PGTKORV9IKTJZQ'
            b'UBQAWTKBKZ9NEZHBFIMCLV9TTNJNQZUIJDFPTTCTKBJRHAITVSKUCUEMD9M9SQJ999'
            b'999TKORV9IKTJZQUBQAWTKBKZ9NEZHBFIMCLV9TTNJNQZUIJDFPTTCTKBJRHAITVSK'
            b'UCUEMD9M9SQJ999999999999999999999999999999999999999999999999999999'
            b'999999999999999999999999999999999'
        )

    async def tearDown(self):
        db_session.close_all_sessions()
        await super().tearDown()

    def new_wallet(self):
        return IotaWallet(self.session_base_dir, True)

    def name(self):
        return 'iota'

    def identifier(self):
        return 'IOTA'

    def testnet(self):
        return False

    def test_min_unit(self):
        """
        Test the min_unit function
        """
        wallet = self.new_wallet()
        result = wallet.min_unit()
        self.assertEqual(0, result)

    def test_is_testnet(self):
        """
        Test the is_testnet function
        """
        wallet = self.new_wallet()
        result = wallet.is_testnet()
        self.assertEqual(self.testnet(), result)

    def test_get_name(self):
        """
        Test for get_name
        """
        wallet = self.new_wallet()
        result = wallet.get_name()
        self.assertEqual(self.name(), result)

    def test_get_identifier(self):
        """
        Test for get identifier
        """
        wallet = self.new_wallet()
        result = wallet.get_identifier()
        self.assertEqual(self.identifier(), result)

    def test_create_wallet(self):
        """
        Test wallet creation and side effects
        """
        wallet = self.new_wallet()
        # Check that wallet is not automatically created
        self.assertFalse(wallet.created)
        # Create the wallet
        wallet.create_wallet()
        # Check that all initializations occurred correctly
        self.assertTrue(wallet.created)
        self.assertIsNotNone(wallet.seed)
        self.assertIsNotNone(wallet.provider)

    def test_erronous_wallet_creation(self):
        """
        Tests creating an already created wallet
        """
        wallet = self.new_wallet()
        wallet.create_wallet()  # Create the wallet once
        response = wallet.create_wallet()
        # Check that an exception is returned when a wallet is created again
        self.assertIsInstance(response.exception(), RuntimeError)
        # Check that the second wallet creation did not damage the first
        self.assertTrue(wallet.created)
        self.assertIsNotNone(wallet.seed)
        self.assertIsNotNone(wallet.provider)

    def test_double_wallet_instantiation(self):
        """
        Tests that parameters of two wallets with the same name
        Are identical.
        """
        # Create a wallet
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Instantiate another wallet, without creating it
        new_wallet = self.new_wallet()
        # Assert equality of name and seed
        self.assertEqual(wallet.wallet_name, new_wallet.wallet_name)
        self.assertEqual(wallet.seed, new_wallet.seed)

    def test_wallet_exists(self):
        """
        Tests the good and bad weather cases of wallet_exist
        """
        wallet = self.new_wallet()
        # Wallet is instantiated, but not created
        self.assertFalse(wallet.wallet_exists())
        # Create the wallet
        wallet.create_wallet()
        # Check that the creation is correctly identified
        self.assertTrue(wallet.wallet_exists())

    def test_get_address_before_creation(self):
        """
        Bad weather test case for getting an address
        """
        wallet = self.new_wallet()
        # Prepare the expected result
        future = Future()
        future.set_result([])
        # Get the address
        result = wallet.get_address()
        # Assert the type and content
        self.assertIsInstance(result, Future)
        self.assertEqual(future.result(), result.result())

    def test_get_address_after_creation(self):
        """
        Tests correct address retrieval from the database.
        """
        wallet = self.new_wallet()
        address_length = 81
        # Create the wallet
        wallet.create_wallet()
        # Get the address
        result = wallet.get_address()
        # Assert the type and length
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Address)
        self.assertEqual(address_length, len(result.__str__()))

    def test_get_address_all_spent(self):
        """
        Tests getting a new address when all current addresses are spent
        """
        wallet = self.new_wallet()
        address_length = 81
        # Create the wallet
        wallet.create_wallet()
        # Add an unspent address to the database
        old_address = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        wallet.database.add(DatabaseAddress(
            address=old_address,
            is_spent=False
        ))
        # Mock the api call
        wallet.provider.is_spent = lambda address: True
        result = wallet.get_address()
        # Assert the type and length
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Address)
        self.assertEqual(address_length, len(result.__str__()))
        # Check correct database storage of the new address
        non_spent = wallet.database.query(DatabaseAddress)\
            .filter(DatabaseAddress.seed.__eq__(wallet.seed.__str__()))\
            .first()
        previous = wallet.database.query(DatabaseAddress)\
            .filter(DatabaseAddress.address.__eq__(old_address))\
            .first()
        # Check if the new address is unspent
        self.assertEqual(False, non_spent.is_spent)
        # Check if the old address has been correctly updated
        self.assertEqual(True, previous.is_spent)

    async def test_transfer_before_creation(self):
        """
        Tests the bad weather case of transfering before wallet creation.
        """
        wallet = self.new_wallet()
        # Address taken from IOTA documentation.
        to_address = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9' \
                     'KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        # Try sending a transfer
        result = await wallet.transfer(0, to_address)
        # Assert tpye and contents.
        self.assertIsInstance(result, Future)
        self.assertIsInstance(result.exception(), RuntimeError)

    async def test_transfer_insufficient_funds(self):
        """
        Tests the transfer when the balance of the wallet is insufficient
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Address taken from IOTA documentation.
        to_address = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9' \
                     'KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        # Set up mocks.
        wallet.get_balance = lambda: succeed({'available': 0, 'pending': 0,
                                              'currency': self.identifier(), 'precision': 6})
        # Try sending a transfer with a value higher than the
        # Available amount.
        result = await wallet.transfer(1, to_address)
        # Assert type and contents.
        self.assertIsInstance(result, Future)
        self.assertIsInstance(result.exception(), InsufficientFunds)

    async def test_transfer_negative_amount(self):
        """
        Test the transfer of a negative amount of IOTA
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Address taken from IOTA documentation.
        to_address = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9' \
                     'KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        wallet.get_balance = lambda: succeed({'available': 42, 'pending': 0,
                                              'currency': self.identifier(), 'precision': 6})
        # Try sending the invalid amount
        result = await wallet.transfer(-1, to_address)
        # Assert type and contents.
        self.assertIsInstance(result, Future)
        self.assertIsInstance(result.exception(), RuntimeError)

    async def test_transfer_invalid_address(self):
        """
        Test the transfer of a negative amount of IOTA
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Address contains a random lower case letter
        to_address = 'ZLGVEQ9JUZZWCZXLWVaTHBDX9G9' \
                     'KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW'
        wallet.get_balance = lambda: succeed({'available': 42, 'pending': 0,
                                              'currency': self.identifier(), 'precision': 6})
        # Try sending the invalid amount
        result = await wallet.transfer(0, to_address)
        # Assert type and contents.
        self.assertIsInstance(result, Future)
        self.assertIsInstance(result.exception(), RuntimeError)

    async def test_correct_transfer(self):
        """
        Tests the good weather case for transfers
        """
        bundle = Bundle([self.txn])
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Set up mocks.
        wallet.get_balance = lambda: succeed({'available': 42, 'pending': 0,
                                              'currency': self.identifier(), 'precision': 6})
        wallet.provider.submit_transaction = lambda *_: bundle
        wallet.provider.get_bundles = lambda tail_hashes: [bundle]
        # Send a correct transfer
        result = await wallet.transfer(1, self.txn.address.__str__())

        # Check correct bundle storage
        all_bundles = wallet.database.query(DatabaseBundle)\
            .all()
        # Get the bundle sent in the transaction
        bundle_query = wallet.database.query(DatabaseBundle)\
            .filter(DatabaseBundle.hash.__eq__(bundle.hash.__str__()))\
            .all()
        self.assertEqual(len(all_bundles), 1)
        self.assertEqual(bundle_query, all_bundles)

        # Check correct transaction storage
        all_txs = wallet.database.query(DatabaseTransaction)\
            .all()
        # Get the transaction that's part of the bundle
        tx_query = wallet.database.query(DatabaseTransaction)\
            .filter(DatabaseTransaction.hash.__eq__(self.txn.hash.__str__()))\
            .all()
        self.assertEqual(len(all_txs), 1)
        self.assertEqual(all_txs, tx_query)

        # Assert correct return type
        self.assertIsInstance(result, Future)
        self.assertEqual(result.result(), bundle)

    async def test_get_balance_before_creation(self):
        """
        Tests getting a balance before a wallet is created
        """
        wallet = self.new_wallet()
        expected = {
            'available': 0,
            'pending': 0,
            'currency': self.identifier(),
            'precision': 6
        }
        # Get the balance of the uncreated wallet
        result = await wallet.get_balance()
        self.assertIsInstance(result, Future)
        self.assertDictEqual(expected, result.result())

    async def test_get_balance_correct(self):
        """
        Tests getting a balance before a wallet is created
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        expected = {
            'available': 42,
            'pending': 0,
            'currency': self.identifier(),
            'precision': 6
        }
        # Set up other wallet variables
        wallet.get_pending = lambda: 0
        wallet.provider.get_seed_balance = lambda: 42
        wallet.provider.get_seed_transactions = lambda: []
        wallet.update_transactions_database = lambda transactions: None
        wallet.update_bundles_database = lambda: None
        # Get the balance of the uncreated wallet
        result = await wallet.get_balance()
        self.assertIsInstance(result, Future)
        self.assertDictEqual(expected, result.result())

    def test_get_pending_before_creation(self):
        """
        Tests the pending balance of an uncreated wallet
        """
        wallet = self.new_wallet()
        result = wallet.get_pending()
        self.assertEqual(0, result)

    def test_get_pending_no_transactions(self):
        """
        Tests the pending balance with no transactions
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        wallet.provider.get_seed_transactions = lambda: []
        wallet.update_bundles_database = lambda: None
        result = wallet.get_pending()
        self.assertEqual(0, result)

    def test_get_pending_confirmed_transaction(self):
        """
        Tests the pending balance with no transactions
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Inject the valued transaction
        self.tx1.is_confirmed = True
        wallet.update_bundles_database = lambda: None
        wallet.provider.get_seed_transactions = lambda: [self.tx1]
        result = wallet.get_pending()
        # Since the transaction is confirmed, no value should be added
        self.assertEqual(0, result)

    def test_get_pending_multiple(self):
        """
        Tests the pending balance with no transactions
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Inject the valued transaction
        self.tx1.is_confirmed = False
        self.txn.is_confirmed = False
        self.txn.value = 1
        wallet.update_bundles_database = lambda: None
        wallet.provider.get_seed_transactions = lambda: [self.tx1, self.txn]
        # Since the transaction is confirmed, no value should be added
        self.assertEqual(self.txn.value + self.tx1.value,
                         wallet.get_pending())

    def test_get_transactions_before_creation(self):
        """
        Tests the get transaction method for a wallet not yet created
        """
        wallet = self.new_wallet()
        result = wallet.get_transactions()
        expected = []
        self.assertIsInstance(result, Future)
        self.assertEqual(expected, result.result())

    def test_get_transactions_zero_transactions(self):
        """
        Tests the get transaction method no transactions
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        wallet.provider.get_seed_transactions = lambda: []
        result = wallet.get_transactions()
        expected = []
        self.assertIsInstance(result, Future)
        self.assertEqual(expected, result.result())

    def test_get_transactions_one_transaction(self):
        """
        Tests the get_transactions method for one transaction
        :return:
        """
        wallet = self.new_wallet()
        # Circumvent wallet creation
        # In order to control the seed
        wallet.seed = Seed('WKRHZILTMDEHELZCVZJSHWTLVGZBVDHEQQMG9LENEOMVRWGTJLSNWAMNF9HMPRTMGIONXXNDHUNRENDPX')
        wallet.created = True
        # Instantiate API
        wallet.provider = IotaProvider(testnet=wallet.testnet, seed=wallet.seed)
        # Mock the API call return
        wallet.provider.get_seed_transactions = lambda: [self.tx1]
        # Add the seed and the bundle to the database
        wallet.database.add(DatabaseSeed(name=wallet.wallet_name, seed=wallet.seed.__str__()))
        wallet.database.add(DatabaseBundle(hash=self.tx1.bundle_hash.__str__()))
        # Commit changes
        wallet.database.commit()
        # Call the tested function
        result = wallet.get_transactions()
        # Construct expected response based on the values of tx1
        expected = [{
            'hash': self.tx1.hash.__str__(),
            'outgoing': False,
            'address': self.tx1.address.__str__(),
            'amount': self.tx1.value,
            'currency': self.identifier(),
            'timestamp': self.tx1.timestamp,
            'bundle': self.tx1.bundle_hash.__str__()
        }]
        self.assertIsInstance(result, Future)
        self.assertEqual(expected, result.result())

    def test_bundle_updates_change_one_bundle(self):
        """
        Tests updating the confirmation value of a bundle
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        bundle = Bundle([self.tx1])
        # Make sure the bundle is confirmed
        bundle.is_confirmed = True
        # Create DatabaseBundle based on tx1
        database_bundle = DatabaseBundle(
            hash=bundle.hash.__str__(),
            tail_transaction_hash=self.tx1.hash.__str__(),
            count=1,
            is_confirmed=False
        )
        # Add it to the database
        wallet.database.add(database_bundle)
        # Mock API response
        wallet.provider.get_bundles = lambda tail_hashes: [bundle]
        wallet.update_bundles_database()
        # Get the bundle after the method
        bundle_after = wallet.database.query(DatabaseBundle)\
            .filter(DatabaseBundle.hash.__eq__(bundle.hash.__str__()))\
            .one()
        self.assertEqual(bundle_after.is_confirmed, True)
        self.assertEqual(bundle_after.hash, bundle.hash.__str__())

    def test_bundle_updates_no_bundle(self):
        """
        Tests that updating the bundles does incorrectly update confirmation
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        bundle = Bundle([self.tx1])
        # Make sure the bundle is confirmed
        bundle.is_confirmed = False
        # Create DatabaseBundle based on tx1
        database_bundle = DatabaseBundle(
            hash=bundle.hash.__str__(),
            tail_transaction_hash=self.tx1.hash.__str__(),
            count=1,
            is_confirmed=False
        )
        # Add it to the database
        wallet.database.add(database_bundle)
        # Mock API response
        wallet.provider.get_bundles = lambda tail_hashes: [bundle]
        wallet.update_bundles_database()
        # Get the bundle after the method
        bundle_after = wallet.database.query(DatabaseBundle)\
            .filter(DatabaseBundle.hash.__eq__(bundle.hash.__str__()))\
            .one()
        self.assertEqual(bundle_after.is_confirmed, bundle.is_confirmed)
        self.assertEqual(bundle_after.hash, bundle.hash.__str__())

    def test_bundle_no_tangle_bundles(self):
        wallet = self.new_wallet()
        wallet.create_wallet()
        # Mock API response
        wallet.provider.get_bundles = lambda tail_hashes: []
        wallet.update_bundles_database()
        bundles_after = wallet.database.query(DatabaseBundle).\
            all()
        self.assertEqual(len(bundles_after), 0)

    def test_bundle_add_bundle_to_database(self):
        """
        Tests that new bundles are correctly inserted in the database
        """
        wallet = self.new_wallet()
        wallet.create_wallet()
        bundle = Bundle([self.tx1])
        # Create DatabaseBundle based on tx1
        expected = DatabaseBundle(
            hash=bundle.hash.__str__(),
            tail_transaction_hash='9TVXQWXUXFNDVXJI9JG9VPVQLWYLMNQEFHMRIDXXXMZNOHYHVNAUXFVQVSU9FORFJJWYXZVRZKEIETTYN',
            count=len(bundle.transactions),
            is_confirmed=False
        )
        # Mock API response
        wallet.provider.get_bundles = lambda tail_hashes: [bundle]
        wallet.update_bundles_database([bundle])
        # Get the bundle after the method
        bundles_after = wallet.database.query(DatabaseBundle)\
            .all()
        # Check that exactly one bundle has been added as a result
        self.assertEqual(1, len(bundles_after))
        # Get the only bundle
        bundle_after = bundles_after[0]
        # Check equivalence with the original
        self.assertEqual(expected.hash, bundle_after.hash)
        self.assertEqual(expected.tail_transaction_hash,
                         bundle_after.tail_transaction_hash)
        self.assertEqual(expected.count, bundle_after.count)
        self.assertEqual(expected.is_confirmed, bundle_after.is_confirmed)


class TestIotaTestnetWallet(TestIotaWallet):

    def new_wallet(self):
        return IotaTestnetWallet(self.session_base_dir, True)

    def identifier(self):
        return 'TIOTA'

    def name(self):
        return 'Testnet IOTA'

    def testnet(self):
        return True


if __name__ == '__main__':
    unittest.main()
