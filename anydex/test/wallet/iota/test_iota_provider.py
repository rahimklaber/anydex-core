import unittest
from iota.crypto.types import Seed
from iota.transaction import ProposedTransaction, Bundle, Transaction
from iota.types import Address
from iota.api import Iota
from anydex.wallet.iota.iota_provider import IotaProvider


class TestIotaProvider(unittest.TestCase):
    def setUp(self):
        self.node = 'https://nodes.devnet.iota.org:443'

        self.own_seed_1 = 'BZTTWRWPZWQDCQRXEJNGVZJUBPRDYRNSQZIZOVGLDJIRRAXFJTZOUDVOBJ9I9CIKX99KVZDLKIWMYQDZK'
        self.seed_1_address_1 = 'RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY'
        self.seed_1_address_2 = 'PUKLSGSYSWQCLQPEAJ9JDOPL9Z9PJGASKMGFQASCXQQD9IYU9XNLNUPTNKPLFRQDLZOOKKCCDUNFYGFCW'
        self.seed_1_address_3 = 'WICRRECOZVUSKVDOVNDOWLHGMCLODVTXMOGDDVPFFPNFMSGHSS9YTKQZVZLAODAFABQBBIKXGYGERQOFD'
        self.seed_1_address_4 = 'GTIGTKBBPOYIMJTKSUNDWMF9OGBFUOZ9TFMOFSE9KGXZBWP9IEZL9VGCKMDCOZSAFJHSTBEZVCFORVXDW'
        self.seed_1_address_5 = 'EOBQZSWB9XOOWIW9RJZVUTFFKGLINYUHJEVMY9EAJRITVFTCOYTYJPVZNRNVXNLLTTEFIBUYHT9CBY9TZ'

        self.own_seed_2 = 'BXNU9FGKBFSBBI9LYRYQFCY9OFBSRKYVZ9ZREROULMYW9HJKJTHEOKEVITUVNBSJHUHIMKABXKWEIZQIO'
        self.seed_2_address_1 = 'EEWRFWF9VOHUWUAZCP9MNHVPYKKOYWPOUOQX9NRPNHZIZWTZFBBIJKPHUWBHTUCMWWOUNGSSUYYXKMOID'
        self.seed_2_address_2 = 'ZEPOKKCNEOJACKJRYYAIM9FVRKKZGVBSBRFLBMFETBSBFVNQKGOSCPUIWXVYFEIWXLRPSTSCB9VPIXDZW'
        self.seed_2_address_3 = 'HLVNCULKQLCKHDCXIMDSVWAD9LRDYRTKKVRFFVQSNDYPQ9EIVWT9BAWRLHDYWZADYDJEOYMUNEGYXLPSD'
        self.seed_2_address_4 = 'OABUCGBMVKCBWZSAKPYVVMAERAVVTYTPDBLQRRJOU9ITZXIYNZUAYSXYCAPIJGJO9ATFVSVSPIWPMDEQ9'
        self.seed_2_address_5 = 'YEMTYEYGGPMLOHOJVRYITRKHMQSUEB9VVMRZPOYIJ9KBFSN9EQYYABGDLMGOGKNGBKMPGJQMCRLBMHUIW'

        self.other_seed = 'JBN9ZRCOH9YRUGSWIQNZWAIFEZUBDUGTFPVRKXWPAUCEQQFS9NHPQLXCKZKRHVCCUZNF9CZZWKXRZVCWQ'
        self.other_seed_address_1 = 'MBYBBFONQZPYZYZHSEZJ9EBEBAFHAZKUFSPBM9YOXJUUAMBUCQQABOWFNPEAGXIGMAVWWFZWDCZJGUTBB'

        self.random_receiving_address_1 = \
            'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW '

        self.api_seed_1 = Iota(adapter=self.node, seed=self.own_seed_1, devnet=True)
        self.api_seed_2 = Iota(adapter=self.node, seed=self.own_seed_2, devnet=True)
        self.api_random_seed = Iota(adapter=self.node, seed=self.other_seed, devnet=True)

        self.submit_response_tryte = \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '99999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999' \
            '999EEWRFWF9VOHUWUAZCP9MNHVPYKKOYWPOUOQX9NRPNHZIZWTZFBBIJKPHUWBHTUCMWWOUNGSSUYYXKMOID99999999999999999999' \
            '9999999YA9999999999999999999999999MAKDWCD99999999999999999999NDNAFYFCSNFLTAIFJRFYVBKNRCKDJVBKOERSIHQXSJT' \
            'GGYWOOYHQHJWTV9JWQASBUXLCTYJKHYPFDIJIZXLP9MRUPSQPZQTLTNNEGSZZYDXZWVEVEQ9LLJCFRPTOHGZLX9JZOHRHWYGDKQQSWZH' \
            'RIPLSBNANYML999XLP9MRUPSQPZQTLTNNEGSZZYDXZWVEVEQ9LLJCFRPTOHGZLX9JZOHRHWYGDKQQSWZHRIPLSBNANYML999YA999999' \
            '9999999999999999999NJLHXWBQF999999999MMMMMMMMMPUCTRIO9LOFTHEBSQKTGABGJNDZ '
        self.get_transactions_tryte = [
            'NY9PEUUVPCHCKQLVYHTYUCVUTQTQZASPXVDCPGLHVJXCFOUGFRSNZGGYSAXICHGRQGWNEKOXKDSYSIDZBVWYQZKJETKOFHPAWLPGCTMYGY'
            'KOTNZNGQKBUMXTDDTZYSRPTEBQVIDNGEXCQORA999JDOIFW9LWDGMSG9YCI9MYYEQMWGGWPNHKPUFJBYBSZ9PZSRWZRGTVIGMTQOBKKWEU'
            'IWZJYEOGXMEVXBKFVENVGGPAUKHHFACVWKDOCNRUWITYPTBSMFZGTFDJEZAFJEFKXYZABDGBOCVUSTHGIJZ9AAWS9URSQBHWDSHVHJGWGF'
            'OMJWIAQMJRXJRTGIGPWLKDHSJYLBE9LXJUOTKLHY9QJLSBNXOVVTZHLVJ9C9XZYLFUTAYGODZLEX9LUKP9OYUAWIK9HSBOKLWJWPTMZQMY'
            'RSVCRVZKXJOAZCOJLDLKJW9XYFJCYFUDPWOERAXVNULVRM9FWXSENRMYPRFECDGYPY9EBCJHIXQYKCKBKF9SXWZDLBUUAKTGPJVKSXQYKC'
            'FGEMJNHRYYUAQRYKAOZLVK9JXSCNBYHPHFLPYJAOLFXFHAFCRORHLTTOSUNEOU9F9RHLXMCMIITIGJHTHAWKYJAPBWHUOKRGP9GRNSBJFX'
            'WCZRKNWLQOCWOPFX9QACUFLVRS9OVCSDA9PCIKTUOFYYXMJFRENZFYFXNDBVMUYGLHMCZQWNYUGHKOBWKWMWUKD9DALLYOH9UUKAGX9BKK'
            'PMOFAVRXHUACUQZSACNV9GRJYUVB9HQBOMVYOTZPOPAGTZGLERBMJAMDVHBWKDDSGZY9JRBGPM9VLONA9JJFFNZGMJIUDQQDGV9M9TAMLU'
            'UYRILOIEO9KXAMB9LQHFEPTRDUYAGQUIRWOYPRJDZE9HOXGZNTNOBAJOCOCZPEWXTAXQSYRRELSFMHOBZKSLBBAY9WXXMTAJTLSRKNCJYH'
            'JBHRYSRBOXSVLSMPFANYGUCTCKJRONHIEMFSYWOCAENCBIZSHNHMLWVNHPZCCZIUITFHJWEH9KWKDLHDMIFVCKDES9ZCQUVABBC9JWVFUN'
            'KGPKMTZRJVQFQRPAEXRESKWYEFHKXGYGIPRZAMNFKIQCUISVBRWPAXRJV9KWNYAUOLG9ZLYVEANW9HREMZMWDDLTTXJFWWGFYBQHOIYSRW'
            'RDUAWO99QEDYBNFXVRLNPT9PNFY9JRCPRFYZRGZTWI9NMJAP9EMBFJZWBVRWJRQZOXWNX9WXGKRCEOJEFF9LVDBWXMBCUXRBDDBEQFFJGD'
            'DYFRNICYPMKUCSIMGOXDNXEBGZHNXZVHNBSGJHPJASSXIPKXCESLZWZXDIJMY9LJURHMPZ9XUXLGINIELRWZWDF9AJLZBEVBBELCCYYTBR'
            'CQPYAEEBAWGBHRENIMOPQQMWOUKPVYBQYB9KXE9ZFQQRIUHYJFO9UMKSEYRMAPZFFFDZATENXPBQCENWXZDCEIEEOGZJYFQAWNRGEOGFQO'
            'PY9XFQPSOVMKHB9OOTNQXAYMNMWFAHGSMVHVF9SJQXLVHMQAWHLLQSBTCMDUJJQVTHJKHW9IIJSNQTOQSXPPIYDHXAQRMMUTGXLFFXXHTQ'
            'LZFWSNRGWOHRWWBCRSJPUVTBETZPEYKQNMZORJRLJOTIQRZUEOQWUAWXIUZLANIDWIBWQWTNOSLPVKGPZYTEOMJPO9VOLLCJOKRUTWVU99'
            'YNNCZSI9AWPYMOSFNDQCPSMIQBZXBMTVYSTWRWRDKQJSUCPPHKRXWDYNXVUZEYVNBEXAZVHUWWRVDQ9TMSHUZWRMBEU9DTYMCHXHMIPMPC'
            'SLLYYWSLQKYSCFUKUHSBIWIPJSMAOEV9ZXEMUWPAPITNPSBYDCZPCKBMHXBVXXHJCOGQ9LJQWD9RUCXISXLDCNPYACEGXTHYAEVJYARYKF'
            'KYJBNM9XFHKVHAYNDQCZWPAHKGVOKPNPCKOWNUQI9KKYUVWHFTTGBEKRXCKJTECMARAS9ACMBWQOYLUMPR9LDADMAVRISEWDAYRHEPLPGX'
            'FFIIGNSIRWWHEHLXAOPPHQOJSDAFRSATZEM9CWD9IWP9OXOBAGZVXNXBOSJOVFJKSXEXUGTCVWZU9UODR9WBD9LD9BBCEOECFUIAIKZBEH'
            'VWIZIUVCOOJGLPSAW9JDGPDZQJOVBEHVUJPYHVFEDTOSBUVRLUXDFTWZKEMIQZLLJBZRGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVR'
            'WJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999999999999999999999999999999QYSDWCD99B'
            '99999999C999999999TWJTTHEDVBCIFFBAAUPDEHKVJBPYJCIAROHABAUIWC9WD9XGGG9TSEQZBEHCSBN9LDOFCNVLQK9YJE9ZZRDDKYIW'
            'TUORFYN9PKRVDLCEJ9ZIOFLYBHVBHJKCBZVLVKWXHJLRRIWSMRQUNAI9CVOISQD9J9ISVO999PXFKCRCIWSRNTYNGTJJ9VEXL9LAXDVA9W'
            'MGGKRALVOKBNWYWVARYXZPBMEESSZCSSPAAJRXOPDVGGT999999999999999999999999999999FKPBYVBQF999999999MMMMMMMMMARTF'
            'KPAYUZWLZNVDTMWEGUFN9QL'
        ]
        self.get_seed_transactions_tryte = [
            Transaction.from_tryte_string(
                'LEINZHQPBKVSEFVJELUKLRKRLIVSBMEMFQNXVGZYPPPU9LMWUQTAAIZKYPIOKRKPGYCIIGLKVJSBANCZWEIZAKRJDKKWJVVLVSDOMU'
                'YWZE9YOGGSLNNWIZMLDZG9KMKWVRCHHJVCAXBSNBYNTQOJORNFUOJWNMNLNDDEQMTUBJXRDNLUBRFRRMCYUTLQJAMBWWHXFOZHFAPF'
                'ANADVQBLQZGIHHTVGBEU9SUDQY9DOIKQXUFPOIBBXBEKZXHWXPQDUPYOTDG9RQWMADJYYRVJPLWKRYIZZOVRLZSHQGSWTRCWJFTUEX'
                'VQWSMFJTPPAMLDDJHZYXXBHNYLSYFUBJRPXZGCZTJJVVWJDIKPIZJCSPMEZZ9ODGB9OSHSHGWVXEPTSXIFHWNUPW9EMFZCBAJUAYZJ'
                '9OLPDNGRMHLZUTORRNHPBZNEPFCUOGJCBPNATBLNLKHHFZZPVPJWBZPOLEDMQMCLEOBCYGDHXWWUVWOQXWJTFYXYNEAOWTDWPDUCEM'
                'RCMFYLX9LETQLHFNAMKUBULSGBXPBUWZXGG9HGCHWOLKSXOBLWDJKXJEZGZOZIIHBCKENJHJYGU9OPPUPDJJYYKUOLOMXCHYDCPZNS'
                'GSQCHMRKYZUBLRIUHIFMTAGPUPXJCFICJWYXFTMQFJVEJSEZZLXLUNQQSDKQHQNGWRRAXRQGVRYFELRXYDDANGNDUJBTYOUHBAOOWI'
                'NZPULTCNLUDKFSCOFFU9ALNCUGWXCHFUCHX9ZXUDKVXF9PLRONQJUZIOGK9BLRLE9OYPDWQQQX9SCYZTKHZJVATWZFWMMNAZHXFIOU'
                '9NSDFFPDABYHHCWJNKNSPDZUBZWRZZRMLEXTVMIFGXBDXQXRIUEJBSLIYMLFB9AKJIEOKGSNKQXJXIEOPEIDDSCS9VCBYPDEJMHOHP'
                'FAFO9RBCYQXSZDOSYCAF9TSYNLXIIAKSUHMOTTFLJMRSWVCGLYRNTXEYGQNLOXPCXPVKXNSZKLIPUQUV9FOSGNBX9GDPXYEIORUOBV'
                'PGHRPVTFTYGWVWAFY9FZQMUEQZAUNRWRYZOLLDSFZEQ9URFKJPBWPGHSFMGDVCBVMPGMXYXYQNOKJWYNSGRTOYAHBGZVFHNAPMIPFL'
                'RYIXCJLAGMNWJIYUHYKI9XYXKOQXJACTNJPPIUJQMZIULCIOS9QZULITPLGSXOTLGJJSJJVMQYXCFMLPABVMYGGMDIKMCJDWCRIXTD'
                'QLGUTGSKOVBPOHANUUNNGPMJXGDSQCSJLGBVIHCNUGJETWGWCHSWXPNXAYRTLCQAULPMH9ICKAJPSL9ZLFAQNGHYVJSNSYLBUJXTGJ'
                'COTJPVCGNPVJDWWBAMKHEVNAVCOJRCLKKVJPPIKDGSHZGJTBPUXEAINWUWTQJ9VLFBFDRFWSTRCGLSWCJLDBPYCWLSTBGZ9VDTQOJT'
                'SNT9JCTYCTQGBMJEXIPSDRGAZ9IALDZES9FBYLMTELZYEKPOKARSQZAKEMOLHAG9XVISPQMKHRZXEJFAYSRQCAHO9SOJHFDPLUYGOP'
                'AQCOYIPBXJVZRBHOVQWKOMX9LMGEZSCOGL9TVLPUPBLRBPSASDMMWUHAEIHZYMGWBVXVYIUGERMXUEZKJGDDJCWFIXXDOMRKODKIZY'
                'PSYL9AXKIUIQBWZDVLSOFOGHVXEBZWPMPNLUZURDRNQKURCXVRIBYGOJGCV9LGCZFCP9DOYNZNPSSSWQQJOOBCTNFUKKRKI9YWQPST'
                'EPIPREBRBEDIOWMXTYO9QFZGPDVABIMDDDZKCLWH9JQJYZQYHDLTAJLFBJHEMDYQXNW9VSHMGG9NZOCLTUHLPYAHHQM9JQACPYWOKN'
                'VKXFXXRDHQERUWDLYOOZJ9TOJZDYNTSGHXTP9ZJTWAVDHLFYOKMXJC9EXUXT9OAM9OIWKCETJBPFVBNA9JIXSWVLKWTSGLSOAWUVUB'
                'WJPOGDPGQCTPQEEVJLMNYHZIYPJPI9MRONVLWV9MIVWGRVPWWRQUBPVVQVHEAMQQROCLZTR9AVKXASYQEIRCWC9PPWVJWVNXMTFAOM'
                'BTSFHMJNYPHDUCYZFNXZCDSX9WDQQMKJ9KAWEILQUIW9EKXTGYXUCPGGRQMJFJVKDCHSXIAOFQMOHRPWNOVSHMMKVOTWV9MLRIZZRH'
                'YJXBFGAXEOHNWFBWT9MTRMUSZAJNMCXRZAS9YJ9VXBGNZPUKLSGSYSWQCLQPEAJ9JDOPL9Z9PJGASKMGFQASCXQQD9IYU9XNLNUPTN'
                'KPLFRQDLZOOKKCCDUNFYGFCW999999999999999999999999999999999999999999999999999999RBSDWCD99B99999999C99999'
                '999GLGANLOPBCZCIXQYAZIJHSZYKTEKASBFQOHRWFLWOHYEQXEBCGKUUFNUDFFVQNEKYPZEASHEBIOFSLYFWG9JEQJDNLFZTHVTNQO'
                'VYOGTH9TGLEIUBBGUUKNJIOGBDZRJ9PUYO9PEYUANHOPPTRLBEYFLOBIHUKW999IFEPDTOCAHE9TWFDPYXUAGU9MOTFLZRJZVPLDVA'
                'GMBMFOMMVRQBTDUANRPE9MYTMVRWPYRDWXNISJQ999999999999999999999999999999EHFGYVBQF999999999MMMMMMMMMM9DGEY'
                'LIZOIQB9SFSCIUKPEVD9J'),
            Transaction.from_tryte_string(
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999'
                '999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHM'
                'OYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999SB9999999999999999999999999NUJCWCD99999999999999999'
                '999VJCAOVXLZL9XEGSFSNAPG9KVIY9TCFDHFRXXJIWPZSEFVAKOHQCLDJJFBPBHVLART9BCXGBVJ9OXXCGSXFNILHXPKKUBQJPAUOO'
                'SBEFIGGTPVNCJLGWOSHGNKCFZCGIANMPJB9UCEFJMVI9BFYLLRUVPCCVFRDF999FNILHXPKKUBQJPAUOOSBEFIGGTPVNCJLGWOSHGN'
                'KCFZCGIANMPJB9UCEFJMVI9BFYLLRUVPCCVFRDF999SB9999999999999999999999999HBSNMUBQF999999999MMMMMMMMMFUMSRI'
                'ATHUEKBDFFCBIWTHLM9V9')
        ]

        self.wrong_address = 'EEWRFWF9VOHUWUAZCP9MNHVPYKKOYWPOUOQX9NRPNHZIZWTZFBBIJKPHUWBHTUCMWWOUNGSSUYYXWRONG'

    def tearDown(self):
        pass

    def test_initialize_api_correct_seed(self):
        seed = Seed.random()
        provider = IotaProvider(testnet=True, node=self.node, seed=seed)
        provider.api.get_account_data = lambda: {'balance': 0}
        self.assertEqual(provider.get_seed_balance(), 0)

    # TODO: test_initialize_api_invalid_seed ?

    def test_submit_transaction(self):
        bundle = Bundle([Transaction.from_tryte_string(self.get_transactions_tryte[0])])
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.send_transfer = lambda transfers: {'bundle': bundle}
        self.assertEqual(Bundle.as_tryte_strings(bundle), Bundle.as_tryte_strings(
            provider.submit_transaction(tx=[Transaction.from_tryte_string(self.get_transactions_tryte[0])])))

    def test_submit_transaction_invalid_tx(self):
        transaction1 = ProposedTransaction(
            address='123',
            value='wrong'
        )
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.send_transfer = lambda transfers: {'bundle': [TypeError]}
        self.assertRaises(TypeError, provider.submit_transaction(tx=[transaction1]))

    def test_get_balance(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_2)
        provider.api.get_balances = lambda addresses: {'balances': [4]}
        self.assertEqual(provider.get_balance(address=[Address(self.seed_2_address_1)]), 4)

    def test_get_balance_invalid_address(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.get_balances = lambda addresses: {'balances': [0]}
        self.assertEqual(provider.get_balance(
            address=[Address(self.wrong_address)]), 0)

    def test_get_seed_balance(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.get_account_data = lambda: {'balance': 996}
        self.assertEqual(provider.get_seed_balance(), 996)

    def test_get_transactions(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.find_transaction_objects = lambda addresses: self.get_transactions_tryte
        self.assertEqual(provider.get_transactions(address=[Address(self.seed_1_address_1)]),
                         self.get_transactions_tryte)

    def test_get_transactions_invalid_address(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.find_transaction_objects = lambda addresses: {'transactions': []}
        self.assertEqual(len(provider.get_transactions(address=[Address(self.wrong_address)])['transactions']), 0)

    def test_get_seed_transactions(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.find_transaction_objects = lambda addresses: self.get_seed_transactions_tryte
        self.assertEqual(provider.get_seed_transactions(), self.get_seed_transactions_tryte)

    def test_get_bundles(self):
        bundle1 = Bundle([self.get_seed_transactions_tryte[0]])
        bundle2 = Bundle([self.get_seed_transactions_tryte[1]])
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        transaction_hash1 = self.get_seed_transactions_tryte[0].hash
        transaction_hash2 = self.get_seed_transactions_tryte[1].hash
        bundles = [bundle1, bundle2]
        provider.api.get_bundles = lambda transactions: {'bundles': bundles}
        transaction_hashes = [transaction_hash1, transaction_hash2]
        self.assertListEqual(bundles, provider.get_bundles(tail_tx_hashes=transaction_hashes))

    def test_generate_address(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.get_new_addresses = lambda index, count, security_level: \
            {'addresses': [Address(self.seed_1_address_1)]}
        new_address = provider.generate_address()
        self.assertEqual(new_address, self.seed_1_address_1)

    def test_is_spent_true(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.were_addresses_spent_from = lambda *_: {'states': [True], 'duration': 0}
        is_spent = provider.is_spent(Address(self.seed_1_address_1))
        self.assertTrue(is_spent)

    def test_is_spent_false(self):
        provider = IotaProvider(testnet=True, node=self.node, seed=self.own_seed_1)
        provider.api.were_addresses_spent_from = lambda *_: {'states': [False], 'duration': 0}
        is_spent = provider.is_spent(Address(self.seed_1_address_1))
        self.assertFalse(is_spent)


if __name__ == '__main__':
    unittest.main()
