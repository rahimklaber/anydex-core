import unittest
from anydex.wallet.iota.iota_provider import IotaProvider
from iota.crypto.types import Seed
from iota.transaction import ProposedTransaction, Bundle, Transaction
from iota.types import Address
from iota.api import Iota


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

        self.random_receiving_address_1 = 'ZLGVEQ9JUZZWCZXLWVNTHBDX9G9KZTJP9VEERIIFHY9SIQKYBVAHIMLHXPQVE9IXFDDXNHQINXJDRPFDXNYVAPLZAW '

        self.api_seed_1 = Iota(adapter=self.node, seed=self.own_seed_1, devnet=True)
        self.api_seed_2 = Iota(adapter=self.node, seed=self.own_seed_2, devnet=True)
        self.api_random_seed = Iota(adapter=self.node, seed=self.other_seed, devnet=True)

        self.submit_response_tryte = '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999EEWRFWF9VOHUWUAZCP9MNHVPYKKOYWPOUOQX9NRPNHZIZWTZFBBIJKPHUWBHTUCMWWOUNGSSUYYXKMOID999999999999999999999999999YA9999999999999999999999999MAKDWCD99999999999999999999NDNAFYFCSNFLTAIFJRFYVBKNRCKDJVBKOERSIHQXSJTGGYWOOYHQHJWTV9JWQASBUXLCTYJKHYPFDIJIZXLP9MRUPSQPZQTLTNNEGSZZYDXZWVEVEQ9LLJCFRPTOHGZLX9JZOHRHWYGDKQQSWZHRIPLSBNANYML999XLP9MRUPSQPZQTLTNNEGSZZYDXZWVEVEQ9LLJCFRPTOHGZLX9JZOHRHWYGDKQQSWZHRIPLSBNANYML999YA9999999999999999999999999NJLHXWBQF999999999MMMMMMMMMPUCTRIO9LOFTHEBSQKTGABGJNDZ '
        self.get_transactions_tryte = [
            'NY9PEUUVPCHCKQLVYHTYUCVUTQTQZASPXVDCPGLHVJXCFOUGFRSNZGGYSAXICHGRQGWNEKOXKDSYSIDZBVWYQZKJETKOFHPAWLPGCTMYGYKOTNZNGQKBUMXTDDTZYSRPTEBQVIDNGEXCQORA999JDOIFW9LWDGMSG9YCI9MYYEQMWGGWPNHKPUFJBYBSZ9PZSRWZRGTVIGMTQOBKKWEUIWZJYEOGXMEVXBKFVENVGGPAUKHHFACVWKDOCNRUWITYPTBSMFZGTFDJEZAFJEFKXYZABDGBOCVUSTHGIJZ9AAWS9URSQBHWDSHVHJGWGFOMJWIAQMJRXJRTGIGPWLKDHSJYLBE9LXJUOTKLHY9QJLSBNXOVVTZHLVJ9C9XZYLFUTAYGODZLEX9LUKP9OYUAWIK9HSBOKLWJWPTMZQMYRSVCRVZKXJOAZCOJLDLKJW9XYFJCYFUDPWOERAXVNULVRM9FWXSENRMYPRFECDGYPY9EBCJHIXQYKCKBKF9SXWZDLBUUAKTGPJVKSXQYKCFGEMJNHRYYUAQRYKAOZLVK9JXSCNBYHPHFLPYJAOLFXFHAFCRORHLTTOSUNEOU9F9RHLXMCMIITIGJHTHAWKYJAPBWHUOKRGP9GRNSBJFXWCZRKNWLQOCWOPFX9QACUFLVRS9OVCSDA9PCIKTUOFYYXMJFRENZFYFXNDBVMUYGLHMCZQWNYUGHKOBWKWMWUKD9DALLYOH9UUKAGX9BKKPMOFAVRXHUACUQZSACNV9GRJYUVB9HQBOMVYOTZPOPAGTZGLERBMJAMDVHBWKDDSGZY9JRBGPM9VLONA9JJFFNZGMJIUDQQDGV9M9TAMLUUYRILOIEO9KXAMB9LQHFEPTRDUYAGQUIRWOYPRJDZE9HOXGZNTNOBAJOCOCZPEWXTAXQSYRRELSFMHOBZKSLBBAY9WXXMTAJTLSRKNCJYHJBHRYSRBOXSVLSMPFANYGUCTCKJRONHIEMFSYWOCAENCBIZSHNHMLWVNHPZCCZIUITFHJWEH9KWKDLHDMIFVCKDES9ZCQUVABBC9JWVFUNKGPKMTZRJVQFQRPAEXRESKWYEFHKXGYGIPRZAMNFKIQCUISVBRWPAXRJV9KWNYAUOLG9ZLYVEANW9HREMZMWDDLTTXJFWWGFYBQHOIYSRWRDUAWO99QEDYBNFXVRLNPT9PNFY9JRCPRFYZRGZTWI9NMJAP9EMBFJZWBVRWJRQZOXWNX9WXGKRCEOJEFF9LVDBWXMBCUXRBDDBEQFFJGDDYFRNICYPMKUCSIMGOXDNXEBGZHNXZVHNBSGJHPJASSXIPKXCESLZWZXDIJMY9LJURHMPZ9XUXLGINIELRWZWDF9AJLZBEVBBELCCYYTBRCQPYAEEBAWGBHRENIMOPQQMWOUKPVYBQYB9KXE9ZFQQRIUHYJFO9UMKSEYRMAPZFFFDZATENXPBQCENWXZDCEIEEOGZJYFQAWNRGEOGFQOPY9XFQPSOVMKHB9OOTNQXAYMNMWFAHGSMVHVF9SJQXLVHMQAWHLLQSBTCMDUJJQVTHJKHW9IIJSNQTOQSXPPIYDHXAQRMMUTGXLFFXXHTQLZFWSNRGWOHRWWBCRSJPUVTBETZPEYKQNMZORJRLJOTIQRZUEOQWUAWXIUZLANIDWIBWQWTNOSLPVKGPZYTEOMJPO9VOLLCJOKRUTWVU99YNNCZSI9AWPYMOSFNDQCPSMIQBZXBMTVYSTWRWRDKQJSUCPPHKRXWDYNXVUZEYVNBEXAZVHUWWRVDQ9TMSHUZWRMBEU9DTYMCHXHMIPMPCSLLYYWSLQKYSCFUKUHSBIWIPJSMAOEV9ZXEMUWPAPITNPSBYDCZPCKBMHXBVXXHJCOGQ9LJQWD9RUCXISXLDCNPYACEGXTHYAEVJYARYKFKYJBNM9XFHKVHAYNDQCZWPAHKGVOKPNPCKOWNUQI9KKYUVWHFTTGBEKRXCKJTECMARAS9ACMBWQOYLUMPR9LDADMAVRISEWDAYRHEPLPGXFFIIGNSIRWWHEHLXAOPPHQOJSDAFRSATZEM9CWD9IWP9OXOBAGZVXNXBOSJOVFJKSXEXUGTCVWZU9UODR9WBD9LD9BBCEOECFUIAIKZBEHVWIZIUVCOOJGLPSAW9JDGPDZQJOVBEHVUJPYHVFEDTOSBUVRLUXDFTWZKEMIQZLLJBZRGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999999999999999999999999999999QYSDWCD99B99999999C999999999TWJTTHEDVBCIFFBAAUPDEHKVJBPYJCIAROHABAUIWC9WD9XGGG9TSEQZBEHCSBN9LDOFCNVLQK9YJE9ZZRDDKYIWTUORFYN9PKRVDLCEJ9ZIOFLYBHVBHJKCBZVLVKWXHJLRRIWSMRQUNAI9CVOISQD9J9ISVO999PXFKCRCIWSRNTYNGTJJ9VEXL9LAXDVA9WMGGKRALVOKBNWYWVARYXZPBMEESSZCSSPAAJRXOPDVGGT999999999999999999999999999999FKPBYVBQF999999999MMMMMMMMMARTFKPAYUZWLZNVDTMWEGUFN9QL',
            '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999SB9999999999999999999999999NUJCWCD99999999999999999999VJCAOVXLZL9XEGSFSNAPG9KVIY9TCFDHFRXXJIWPZSEFVAKOHQCLDJJFBPBHVLART9BCXGBVJ9OXXCGSXFNILHXPKKUBQJPAUOOSBEFIGGTPVNCJLGWOSHGNKCFZCGIANMPJB9UCEFJMVI9BFYLLRUVPCCVFRDF999FNILHXPKKUBQJPAUOOSBEFIGGTPVNCJLGWOSHGNKCFZCGIANMPJB9UCEFJMVI9BFYLLRUVPCCVFRDF999SB9999999999999999999999999HBSNMUBQF999999999MMMMMMMMMFUMSRIATHUEKBDFFCBIWTHLM9V9',
            '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999AB9999999999999999999999999GMJCWCD99999999999999999999IXGBRLKTYYCAHTIZHLNDJGLFUNKKIQBREILXVFCEVFZHEOQJRHZJTOOG9DRIGEVTERP9HIKYEWEWOCKACTITTFYZPYOQEPVUPIWJGOQJOGBLGYHAXPTLLLFLCYUO9IU9AJZNBFSRHLBZGAXWYJEGYDZZFAQRUQL999TITTFYZPYOQEPVUPIWJGOQJOGBLGYHAXPTLLLFLCYUO9IU9AJZNBFSRHLBZGAXWYJEGYDZZFAQRUQL999AB9999999999999999999999999ULYNNVBQF999999999MMMMMMMMMXAOHNYVFISAVDCXITDWCSTCFUGU',
            '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999OH9999999999999999999999999HSJCWCD99999999999999999999JCYJFIBH9IBXXHQOSKBGQQAADGGYDYBEBFDLC9OCFKOH9HCLNDAQJGKUL9CGDZEWYPOAELKFETKPESTYDBQKCNFAFASTZKZMLDCUPKPZNVYFONCADINRSMHLPHEETAJJKHMRKKWNJHHPY9BYKFKCJQKIIXUOKCR999BQKCNFAFASTZKZMLDCUPKPZNVYFONCADINRSMHLPHEETAJJKHMRKKWNJHHPY9BYKFKCJQKIIXUOKCR999OH9999999999999999999999999ODZLLUBQF999999999MMMMMMMMMHDKYYIUTSYOLRXOYIMNTBGDA9ZC',
            'QJZVLRYJGRZPRETVOHTOERIUCFVJCYYETPKRNAAHTXOVLUQLFOLWOWZYGLXEQ9WHSQGKM9ZKICGNVQJNXRPIMPUWGMUESQTNDYPCMNZWFPOSDXBV9MMEVKKEUDOOT9RTHTHYTUMCDBYFNXWAM9QJHBUKRADAJHVGNAZOQBKKYRYKJYVLTWEMSKWKKCVQSULOLLAIRMFARFUUQNKRKZKFCVPRMEYDLJONBHJAMWYHUQBALHPEBB9UL9KOMUBEQSNICGNLZJHREND9P9VKERPJYSWCAFDL9XUWARBRJCMDIIVAVQEVQHRMUUWCTFAXDMGHMSMDIGVKZF9RMIDXXCYGZTRTGNWUOLKOUVGZZNWUYMUYKEDXTTDTBHCMBNRFMBLYNADYFZJ9XZMYRWAJJAH9DHHSOWIXGLYNYHBWVZNFHDHKVVT9CBLAVVHZPAQKWBJEQY9DBRLPX9RVSNZYRAGUZTTFP9FVFKDZEAQBPCGZBKOWZCPBVVO9R9C9ERTITSFVFVFYZQXBRJBGVADXAA9MNFNWDGAKSOLUOMSRWJHRBNUAIZSFLGF9QGCDWOKFEYGWQYOSZUMVTXJVRJNTODTWHFFEJULDFYGILJE9NFANOXSSSOZMSVWNVRLJYVKLPUPQCRIMCAODNCLHOQK9UWRRQJFVWGAGIBDFCKSXATULSLLFV99BKFIIXVMKCVJ9RLCJDUGXODXMQ9DQDKZNSWOCICSRYHGNMYQYJNDFULEFWTPWIUHIKFEHZIJZJULK9XPHDL9NVLWJHDHMJTPZYRRUNYIUXRHLDQAPPLPUL9JHCCTYUTKQETPXEUDZWTDAVFBCNDVARNGJBEVQOCIQHNTLNWOGACXHFGWHTUIGGKEVTGOWBASTKOVU9QVN9RZDB9CFZQALMAWIATLDTJSUBLWRJUEGSMSPRSKJBILNRHE9AOTIC9RCDSUFRKQKDCKECVZNVNSH9ZLOTKSDQLUAGMUAXNGJPNYBHYZP9PGMLGDTVFLEZBMCZAEHZVMNPIKFEVCSBHOLZNQWQYVLZWE9NFCZX9UAKNGMZDPOOEBWIDDGCEOIYJYBLIMPVLUPJSQPGEFDNAKLWSPQTKKVIBWWCHXUPKBYUWIB9AAMXAKNVUCTGRORYDPWCTQQ9ZUZFTNILEUENKBDXB9ZZRROLDJCDZAVFXYAEDYZNGFQLFLWF9OSKRBPJSNTWCCULXS9QXBPWRYURWLTLVGFGBDSXAXLLEMNAPNVIRHFWUACKBSNIIRJDSJEJWTKTK9DHPTGQSXNSGPVPXIXSYYKPMOVYR9WBTM9VYAHABWTUBZZHXKVOVGSHDPRJB9R9BVQXGQITGJMPQWB9PJFDXPEJBBXRHLSNXVXMCTYPMBUSZTGWZJGUFXRQQZJYZEELBEQHUNHBIVLZHX9ZSTFZYNXBCCFDBHGUHMQAVTXGBENV9QIEEWSQLTFAENUUTSVYBUSTWSORCWEDYQJHHFWBDJABBYRAMOVJPXUMGSIPDKHUOUUSTLLXXKNSAWPYXMIJKXARVSPDEQAYESOSVXOKYARPCVYILTMIGECCIZUIQCYQ9GIFSEPNMJBABMVGTSDDZXONUBAMDAHJOGAUFB9LPTSA9FSNOQHTWE9HJAY9QQJGKREIHRUFTABCQPDRIZMULYDPH9URUNGIEUELTYVFRWBRKWKNYEZHPSCWCKNKTNSPIMHAAMADGJPNLZSEV9OYWHUYFVTMYYDGGBWGXQIFTHFXSDQEXZMEIPQWSSLQQLGSKNNEBYQQXKEI9DIRBVRZKVYI9LGNJLTOCIQUVBBDSL9GKBOLXQEWFTLSPBIFKGEIGZGKNJYSNCYQFJQJY9VYSQBKFZNZ9LBKRSBBGSNWGCOPUNGLBLJOKKDOTMAUXMVLPJHRGZUA9V9YDTZAELLXLSQGKBKYVCCELLRRZQJBTGBBBKDFFJXHKSHVIUZMKIQADLYABQKAQQEVEJWONWYCZ9OCBFZNMKD9ZCZEYZHDN9ERTNEBNRWNQDUXIO9IAZOTKBEWPQEWVXHXVUDSUOXWV9KAANWBAFNBWWCW9V9KCZUIPEZCVQSMDLYTUXMLRMRGCWICYMGMMJZBHCHNWEBA9FDHYEV9XQLFLOKZKFARKEPOALKNWWNRFXTSZLEPXOROOMSI9UEDXOTFCGBEESHXYIGEWZQOMIAUIEA9TBPCO9YPVXRGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCYZQZ999999999999999999999999999999999999999999999999999QYSDWCD99A99999999C999999999TWJTTHEDVBCIFFBAAUPDEHKVJBPYJCIAROHABAUIWC9WD9XGGG9TSEQZBEHCSBN9LDOFCNVLQK9YJE9ZJELUIFMQOFZFAMSIKYCHZBQIINQUVPNACORNWICXHFDQLKO9BJDVFCGZJSDWJKPDODGJWXQGGOXMXO999PXFKCRCIWSRNTYNGTJJ9VEXL9LAXDVA9WMGGKRALVOKBNWYWVARYXZPBMEESSZCSSPAAJRXOPDVGGT999999999999999999999999999999RLPBYVBQF999999999MMMMMMMMMXJIVGUQNKCENYCCRBHBTUGIEYSF',
            '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999BB9999999999999999999999999KUJCWCD99999999999999999999TMIBILJNZDKFCBQHWPWTPIXLXAZQDLCLTBBSHCTJDH9DOWLXZIPPKRSNWOZSEILJYJORWGZERNIZJGIFDIIVIRHVZZJRPOJHDHZRY9DREESGPKITDDDNOFMBAYVIYTATFQZERNYNDCUEZUEMQNAM9BMAGPWNAUK999IIVIRHVZZJRPOJHDHZRY9DREESGPKITDDDNOFMBAYVIYTATFQZERNYNDCUEZUEMQNAM9BMAGPWNAUK999BB9999999999999999999999999MYZOMUBQF999999999MMMMMMMMMJUULBNEEDRCEGCMRYFZ9TLS9VWR',
            '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999WH9999999999999999999999999HWJCWCD99999999999999999999NDAHOLLLDYDSZIPVILVWGSVZLVBGXSKKCYRBRLJDWQKYYHZNTCW9X9LXHA9ZG9LDUIFYESWZGHRTCZGHXMSLODZWYPKKRXS9HXLFTTSDLOQGAPLEMDUNKYRV9CQRFKGVOMLRPUHQQOHDWMOHHNYUUPZP9DJYZSA999MSLODZWYPKKRXS9HXLFTTSDLOQGAPLEMDUNKYRV9CQRFKGVOMLRPUHQQOHDWMOHHNYUUPZP9DJYZSA999WH9999999999999999999999999BRRRMUBQF999999999MMMMMMMMMM9AESGUVTFHLJNJCNREVXK9LQRA',
            '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999WC9999999999999999999999999YBQDWCD99999999999999999999WGXTFKVVIUQCKLUYBDPHSND9VGTHGWXSPUZRHJXBYDUFKUCNRXJDAKJZCJ9ABXOQSHBKXNPFRCNKDGEYDMIRBHJDCSNEVPMERWRYQNMG9JVSCZ9LNOSSWRZIJOZRXGIHHTVEIJNC9GQVUTCICEKHQFTAFNSWI99999MIRBHJDCSNEVPMERWRYQNMG9JVSCZ9LNOSSWRZIJOZRXGIHHTVEIJNC9GQVUTCICEKHQFTAFNSWI99999WC9999999999999999999999999BHWOWVBQF999999999MMMMMMMMMUCAQDDYAPCOFTTTLKFXLJSBNWDE',
            'HDTCGDHDXCBDVCEAHDXCADTC999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCYAJA999999999999999999999999NTOFACHIOTA9999999999999999R9QDWCD99999999999C99999999MHCIJUQGBHCIVGKYAPEQWL9YNRVJLGZNHDDP9CHWOIOAILE9EUPDTZ9SKFLLNDLSCHWTQOROKUIBUXOKDJFW9ZHKPFPLYRNBBBSMAYKTCZLODNTKRLOUORZTEVGCLRLAXFDKRCCOZOBTMIMKE9WXCFZUMGRVEZH999QRZSTD9ZXS9TYCHSXPLPHNROANHCPAXVIFFAWMLBUPIAHHSOQXSGHUOMKBUHSTWFTVVDKUYDSSULYG999EINFACHIOTA9999999999999999XTJKVVBQF999999999MMMMMMMMMJXWHKGGYEAUXLERYWQGGXG9NPMS',
            '999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999RGJLBAMAXIUHYPVAPKGVGGHTWXYJHVVQD9TDEVRWJKUINBNATQIBBNNHMOYBBWVXCQQHZJBXDCNJCJFCY999999999999999999999999999XA9999999999999999999999999XOJCWCD99999999999999999999EMDWGNGWXBFGBSSNXL99YWHLZJIGJBLFVTGYJAQICJ9LUBLYGJCPUHJIERXHAYKALSTLEIVWQZVCLFEABSGPARCTDJNXPZCMGQVMSXCUYIMRJKOCUZYKYNVUQMK9THUXBEBYDCFJ9GPSVJQZCCWAYWMWSCTIAUW999SGPARCTDJNXPZCMGQVMSXCUYIMRJKOCUZYKYNVUQMK9THUXBEBYDCFJ9GPSVJQZCCWAYWMWSCTIAUW999XA9999999999999999999999999F9WFLUBQF999999999MMMMMMMMMVIHTOLARPMEXWGOZJYITJSKOQHX'
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

    # TODO: test_get_seed_transactions
    # TODO: test_get_pending
    # TODO: test_generate_address
    # TODO: test_is_spent_true
    # TODO: test_is_spent_false


if __name__ == '__main__':
    unittest.main()
