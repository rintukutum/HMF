"""
Test the performance of BNMTF for recovering the GDSC dataset, where we vary 
the fraction of entries that are missing.
We repeat this 10 times per fraction and average that.
"""

import sys, os
project_location = os.path.dirname(__file__)+"/../../../"
sys.path.append(project_location)

from HMF.code.models.bnmtf_gibbs import bnmtf_gibbs
from HMF.code.generate_mask.mask import try_generate_M_from_M
from HMF.drug_sensitivity.load_dataset import load_data_without_empty

import numpy, matplotlib.pyplot as plt, random

''' Settings '''
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
repeats = 20
iterations, burn_in, thinning = 1000, 900, 2

init_S = 'random'
init_FG = 'kmeans'
K, L = 7,7

alpha, beta = 1., 1.
lambdaF = 1.
lambdaS = 1.
lambdaG = 1.
priors = { 'alpha':alpha, 'beta':beta, 'lambdaF':lambdaF, 'lambdaS':lambdaS, 'lambdaG':lambdaG }

metrics = ['MSE', 'R^2', 'Rp']

''' Load data '''
location = project_location+"DI_MMTF/data/datasets_drug_sensitivity/overlap/"
location_data = location+"data_row_01/"
R, M_original, _, _ = load_data_without_empty(location_data+"gdsc_ic50_row_01.txt")

#''' Seed all of the methods the same '''
#numpy.random.seed(0)
#random.seed(0)

''' Generate matrices M - one list of (M_train,M_test)'s for each fraction '''
M_attempts = 1000
all_Ms_train_test = [ 
    [try_generate_M_from_M(M=M_original,fraction=fraction,attempts=M_attempts) for r in range(0,repeats)]
    for fraction in fractions_unknown
]

''' Make sure each M has no empty rows or columns '''
def check_empty_rows_columns(M,fraction):
    sums_columns = M.sum(axis=0)
    sums_rows = M.sum(axis=1)
    for i,c in enumerate(sums_rows):
        assert c != 0, "Fully unobserved row in M, row %s. Fraction %s." % (i,fraction)
    for j,c in enumerate(sums_columns):
        assert c != 0, "Fully unobserved column in M, column %s. Fraction %s." % (j,fraction)
        
for Ms_train_test,fraction in zip(all_Ms_train_test,fractions_unknown):
    for (M_train,M_test) in Ms_train_test:
        check_empty_rows_columns(M_train,fraction)

''' Run the method on each of the M's for each fraction '''
all_performances = {metric:[] for metric in metrics} 
average_performances = {metric:[] for metric in metrics} # averaged over repeats
for (fraction,Ms_train_test) in zip(fractions_unknown,all_Ms_train_test):
    print "Trying fraction %s." % fraction
    
    # Run the algorithm <repeats> times and store all the performances
    for metric in metrics:
        all_performances[metric].append([])
    for repeat,(M_train,M_test) in zip(range(0,repeats),Ms_train_test):
        print "Repeat %s of fraction %s." % (repeat+1, fraction)
    
        BNMTF = bnmtf_gibbs(R,M_train,K,L,priors)
        BNMTF.initialise(init_FG=init_FG,init_S=init_S)
        BNMTF.run(iterations)
    
        # Measure the performances
        performances = BNMTF.predict(M_test,burn_in,thinning)
        for metric in metrics:
            # Add this metric's performance to the list of <repeat> performances for this fraction
            all_performances[metric][-1].append(performances[metric])
            
    # Compute the average across attempts
    for metric in metrics:
        average_performances[metric].append(sum(all_performances[metric][-1])/repeats)
    
 
print "repeats=%s \nfractions_unknown = %s \nall_performances = %s \naverage_performances = %s" % \
    (repeats,fractions_unknown,all_performances,average_performances)

'''
200 iterations
repeats=10 
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.5941929599474387, 0.5968491052848404, 0.6106399966584322, 0.5747983319636255, 0.5569201486639157, 0.6080661505915745, 0.5660788382623474, 0.543287325070379, 0.5797668208719176, 0.6068486259434914], [0.5854150873567245, 0.5473538645539486, 0.5860857495459351, 0.5809250055909023, 0.583538936506822, 0.5671182607151077, 0.5928974813762868, 0.6100612533373422, 0.5920062566668283, 0.6154231900517017], [0.584426987583068, 0.6007306547456885, 0.5840749948347832, 0.6060098519262915, 0.5903258100679247, 0.5712475102433576, 0.5947353926389474, 0.5702207240438959, 0.5943648884675565, 0.5489544600772971], [0.5623650277470954, 0.5849070871787971, 0.5804924711174851, 0.5732629781164881, 0.578603128551517, 0.5787610098537443, 0.5569165734195822, 0.5733106425345196, 0.5872824789307423, 0.5790127020644471], [0.5841364713098784, 0.5625071342284721, 0.553414885900496, 0.5789165174394189, 0.5731507797660512, 0.556302254502138, 0.5751077406587155, 0.5816281033350199, 0.5968467946061626, 0.5795110715580771], [0.5791164622681151, 0.5702055831101803, 0.5561989288056723, 0.5677443893662977, 0.5682371781538549, 0.5763462915449601, 0.5648514179437465, 0.5552940932707378, 0.5711211870692408, 0.5642903260837506], [0.5600743545506364, 0.5531882003202768, 0.5707508378847957, 0.5450334261949854, 0.5526317038021961, 0.5547612246382561, 0.5674035439388387, 0.5516553926888992, 0.546266197179326, 0.5620688066302071], [0.5374947546511608, 0.5472602739400619, 0.544514115223371, 0.5592133260017639, 0.5454578297502141, 0.5603233356008892, 0.5365616005592324, 0.5528884464324122, 0.5509226613333051, 0.5529627836090476], [0.5332495218213473, 0.537312822063635, 0.5308552044036863, 0.5383632208944443, 0.539039104119168, 0.5434649358327914, 0.5242858140533704, 0.5482011544720105, 0.5410834425727185, 0.5559596533852306], [0.5310201375727599, 0.5391145317818341, 0.5362529507763594, 0.5255449871656166, 0.5184708235663289, 0.507319207737583, 0.5065748947322809, 0.5297866171158615, 0.5218270142007155, 0.5285019575594061], [0.5156442765541576, 0.49901073383771577, 0.5091546922445104, 0.49783560565235696, 0.5028484505684676, 0.5132254799405133, 0.5152478868972215, 0.5070112619323204, 0.515729813807532, 0.5126529638284281], [0.5124783202879708, 0.501225727361974, 0.4819650222593641, 0.498130277460641, 0.4908021400994358, 0.49502563542967537, 0.4810226828612414, 0.5023141072004862, 0.49998294123226794, 0.5010983459337773], [0.4857096319886841, 0.47611234976930217, 0.4858708348221581, 0.48312670336859953, 0.48841534632113137, 0.4795168869786578, 0.476013811327178, 0.4856878567658217, 0.490825844994085, 0.48134637581178863]], 'MSE': [[0.079492606864839346, 0.078025770105755177, 0.077452636267685976, 0.084299658933671431, 0.087615755520830604, 0.080423604523058898, 0.086561411311570038, 0.091400113487509871, 0.083807519725123764, 0.076571041280984325], [0.082225481009121873, 0.091018975501313132, 0.082757286043696074, 0.084248346408462502, 0.083414963615133911, 0.0859436689113936, 0.081139086090595211, 0.077491320120495408, 0.081663402568907556, 0.076388925828361459], [0.08255119065371247, 0.081131522628289876, 0.082694839661872133, 0.078210086734722267, 0.081758632070636453, 0.086895414612430208, 0.080969521774811329, 0.085788779789318745, 0.080969514308704568, 0.089128244390265593], [0.087784166193538918, 0.082619007878507483, 0.08291198633479277, 0.085445918442843272, 0.083437941598933557, 0.083662490709301568, 0.087925337630881201, 0.0852083443708683, 0.081911610405968519, 0.083466262719250686], [0.08329772790263093, 0.087565356923330201, 0.089164492148831584, 0.084285005779547215, 0.085037987154454764, 0.087988782769688176, 0.08448893378955119, 0.083633072647305434, 0.080076517174577894, 0.083964098387851765], [0.083817447378352616, 0.085661351621261678, 0.088650651903866881, 0.086656774391729183, 0.086031377854652258, 0.084993451971259265, 0.08615203121935841, 0.08884411586142428, 0.085611858161689161, 0.086415658233183437], [0.087863369407030698, 0.088785660954818726, 0.085381782167658238, 0.09047211324619038, 0.089040787167787669, 0.089170780004054678, 0.086315108629707898, 0.089173093314508317, 0.090863800986810878, 0.087042185583582621], [0.09225423917725796, 0.090614885932062031, 0.090740497409613902, 0.088306105149232456, 0.090526211818751076, 0.087708906506296314, 0.092272460638397877, 0.089573949410881246, 0.089877223218570543, 0.08932376445908749], [0.092888976592316055, 0.092957580570368431, 0.0936021204613144, 0.092430743093878179, 0.091994927348356278, 0.091017812895278605, 0.094432007115192104, 0.090302051728626542, 0.091914672918883111, 0.088286396868607467], [0.093902302181876826, 0.092052579297898729, 0.092279963445974902, 0.094639001363633679, 0.095829577805821117, 0.097522133036692979, 0.098349365016629137, 0.093881543713809371, 0.095511975731774001, 0.093870461899353816], [0.096507495591716563, 0.099834673050447312, 0.097843740150572608, 0.10021779324780293, 0.099053480404210331, 0.096850986330592345, 0.096910359251592582, 0.09823928958375025, 0.096595669534984566, 0.097470275196013312], [0.097382192109762761, 0.099666596405893579, 0.10300653902566025, 0.099961183505811152, 0.10136071643348232, 0.10066043528918109, 0.10358738510469066, 0.09936950774910866, 0.099781378774220122, 0.099611399127216158], [0.10255167301786651, 0.10433177051856955, 0.10238664494083358, 0.10295536833030379, 0.10206328029568754, 0.10387462443996022, 0.10459571708068126, 0.10260602923136587, 0.10157772910609153, 0.10332439105651946]], 'Rp': [[0.77098364527170316, 0.77270381234441532, 0.78144431662644653, 0.75850064237860004, 0.75032334428968694, 0.78010032436497845, 0.75399946431626097, 0.73813375574884565, 0.76380049571423614, 0.77945695492600831], [0.76548948478687462, 0.7402504787587898, 0.76603619334825035, 0.76228039945261727, 0.7639584803230145, 0.75411874600076678, 0.77009380114819559, 0.78224153616485115, 0.76948656223674838, 0.78452930498316353], [0.76516126871301304, 0.77526043970083947, 0.76531768174913162, 0.77877144576975499, 0.76872236853369247, 0.75623102463665126, 0.77140972580145839, 0.75544782122099752, 0.77219219796840588, 0.74233475022403828], [0.75024670658669734, 0.76527893130743474, 0.76275707448322505, 0.75814066074045394, 0.76093384221364613, 0.76097488518179002, 0.74689075479450295, 0.75870827078570824, 0.76641377712589587, 0.76118281886246431], [0.76492038016648556, 0.75070734999194699, 0.74441022103270083, 0.76089069911196028, 0.7579259006188579, 0.74630560117451639, 0.75846164616751066, 0.76293750629590606, 0.7729596881439974, 0.76139651499790295], [0.76122877013832846, 0.75563975656120452, 0.74601459717076768, 0.7535421313476689, 0.75451763599841559, 0.76002905597467341, 0.7523093614047951, 0.74537831380185804, 0.75776983067886072, 0.75140575686027955], [0.74863262493518068, 0.74419392651742322, 0.7558206804249783, 0.73891975329170689, 0.74470854169661593, 0.74487002733490515, 0.75338787336342272, 0.74314428227535279, 0.73992005453826126, 0.75007834758715486], [0.73336796285058115, 0.74006513175696731, 0.73823088304914075, 0.74796431258817264, 0.73905275881335841, 0.74974709735615508, 0.73308976311057827, 0.74366059901479609, 0.74249373388167961, 0.7445877677413858], [0.73245996146080805, 0.73321894140068189, 0.72879082311278875, 0.734254442766619, 0.73465772539407126, 0.73771384595342293, 0.72605102041892411, 0.74120136791494196, 0.73573732928075619, 0.74570983005180214], [0.72891658521309133, 0.73490391845968939, 0.73263239337125885, 0.72597732088028677, 0.72218445032472822, 0.7141828347088689, 0.7132261520509845, 0.72844360061386049, 0.72400013910688665, 0.72711022263458036], [0.71857933591613854, 0.70767278808980139, 0.71434287484692949, 0.70811754700214236, 0.70950338911936783, 0.7173928745414162, 0.71860226854198128, 0.71246953131685131, 0.7184403770470551, 0.71639754022127722], [0.71638834192477951, 0.70829503378686187, 0.69740019716259738, 0.70624291713075049, 0.70316287083305917, 0.70441687613303128, 0.69471567118152611, 0.70980131273825953, 0.70760100226464473, 0.70802099948480901], [0.69903226639966975, 0.69201108037973835, 0.69760963564088074, 0.69648939697131418, 0.69921080039451666, 0.69355475664661959, 0.69145838856496844, 0.69739307385914362, 0.70311582416355245, 0.69595202705071812]]} 
average_performances = {'R^2': [0.5837448303257962, 0.58608250857016, 0.5845091274628811, 0.5754914099514419, 0.574152175330443, 0.5673405857616557, 0.5563833687828418, 0.5487599127101459, 0.5391814873618402, 0.5244413122208746, 0.5088361165263223, 0.49640452001268337, 0.48326256421474073], 'MSE': [0.082565011802102947, 0.082629145609748073, 0.08300977466247636, 0.084437306628488626, 0.084950197467776906, 0.086283471859677718, 0.088410868146215016, 0.0901198243720151, 0.091982728959282112, 0.094783890349346464, 0.097952376234168276, 0.10043873335250268, 0.10302672280178793], 'Rp': [0.76494467559811807, 0.76584849872032712, 0.76508487243179812, 0.75915277220818178, 0.75809155077017853, 0.75378352099368517, 0.74636761119650008, 0.74122600101628155, 0.73497952877548167, 0.72515776173642355, 0.71415185266429604, 0.70560452226403192, 0.69658272500711227]}

1000 iterations
repeats=10 
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.6056942861099961, 0.6141388200272883, 0.6067842422679758, 0.5722024151393201, 0.5659573322572442, 0.6275376252079007, 0.5842792492830786, 0.5701832256860475, 0.5961138581032752, 0.6027508911953992], [0.5922546710328855, 0.5598584729374989, 0.6009560761917756, 0.5939771667971747, 0.598078590163217, 0.5696803972472531, 0.6009082083010908, 0.627786271882117, 0.6005846406510957, 0.6268699213891397], [0.5963442272157937, 0.6094347196161924, 0.589894904219247, 0.6102150617837405, 0.6010703534424602, 0.5804251879216458, 0.5918035688436817, 0.5788253308687701, 0.5954947597060095, 0.5519789000141476], [0.5746611633110035, 0.5933962525605189, 0.5815482278962333, 0.5714920735524749, 0.5895967783237825, 0.5757961355628876, 0.5604598778336048, 0.5912125383780107, 0.5952213203161516, 0.587119884231147], [0.5904979522243624, 0.5672910537550448, 0.5634004539411592, 0.57967983688392, 0.5790000798059372, 0.5594677648505719, 0.5815176395079135, 0.5829772380345597, 0.5981504925869485, 0.5918263095314871], [0.5860161707859528, 0.5822784116199573, 0.5616262944777345, 0.5810091770487876, 0.5736122101892924, 0.579503298948669, 0.5669099709160959, 0.5645236021487847, 0.5734887437521501, 0.5685896122824796], [0.5585625414333979, 0.5675744587018816, 0.5677114617938179, 0.5568942090655038, 0.562638682056781, 0.5540396750965665, 0.5694445806654373, 0.5603209280827789, 0.5508979450000999, 0.5560198624899944], [0.547982468336409, 0.5536333851954183, 0.5546665310922354, 0.5564331279553969, 0.5543746425222422, 0.5587359631093394, 0.5464693902344706, 0.5518062761190321, 0.5609034796761156, 0.5580589150962035], [0.536124135292638, 0.5293760001105634, 0.542162364828791, 0.5426383291192327, 0.5435442203757485, 0.5484875907082298, 0.5367241879176892, 0.5537711982398842, 0.5468762826069493, 0.5637689553933687], [0.5387001646547449, 0.5431708948599574, 0.5354643289737095, 0.540981089531221, 0.5334855008306545, 0.5261333328452573, 0.5266331845773891, 0.5351332665034829, 0.5319691108239605, 0.5454405953836339], [0.5390221515515623, 0.4988266690773743, 0.5216191920645684, 0.4922771100375053, 0.5132051291210133, 0.5192986201507326, 0.5259505635901128, 0.5006601701945237, 0.5225566403289348, 0.5204431213903798], [0.5144850084892016, 0.5074045390243065, 0.49342703069564786, 0.5034640943106554, 0.5022451589770431, 0.4951689949124579, 0.4972613670516324, 0.5030553425570947, 0.504562818418993, 0.5063237833720282], [0.4911770176574246, 0.483277880044643, 0.4887142445484237, 0.489345253544093, 0.49221957394956406, 0.4846135763051671, 0.4830384075433042, 0.4838998229410586, 0.49441971015343966, 0.4955203013616106]], 'MSE': [[0.077239638560134619, 0.074679521032833041, 0.078219634263829857, 0.084814320374017427, 0.085828719468700715, 0.076428118610352411, 0.082930675124157124, 0.086017542554921431, 0.080547413876135635, 0.07736912526913696], [0.08086897226863525, 0.088504524244606197, 0.079784139131158005, 0.081624417485584119, 0.08050274735522249, 0.085434986299398358, 0.079542478278397666, 0.073968882050540988, 0.079946366373757308, 0.074115248662985078], [0.080183899488038501, 0.079362856828140371, 0.081537716460770848, 0.077375320105920006, 0.079614344756194499, 0.085035371519766784, 0.081555283191719813, 0.084071203439387426, 0.08074397878969268, 0.088530604023659823], [0.085317713381681343, 0.080929346600535884, 0.082703325260590821, 0.085800508176536547, 0.081261163436095282, 0.084251345904607533, 0.08722220540285737, 0.081633399556251013, 0.080335996942911062, 0.08185890734307448], [0.082023519250716867, 0.086607842747417688, 0.087170789100850105, 0.084132218062963823, 0.083872674725438842, 0.087361036955719659, 0.083214338859751324, 0.083363378910137495, 0.079817569478386599, 0.081504966213549995], [0.082443395167291225, 0.083255143519437219, 0.087566518637459553, 0.083997505928167682, 0.084960369910882683, 0.084360092810735074, 0.085744472681301157, 0.087000228600883675, 0.085139251633187807, 0.085562967395597336], [0.088165313600937906, 0.085926977589712517, 0.085986343271625645, 0.08811354417137765, 0.08704907423566427, 0.089315289285376243, 0.085907864639829537, 0.087449569525668777, 0.089936256665467396, 0.08824445965404952], [0.090162293071843008, 0.089339321372127661, 0.088717964337481969, 0.088863083105918964, 0.088750347367483162, 0.088025563533437601, 0.090299779622053225, 0.089790750493589158, 0.087879687024105438, 0.088305492082827078], [0.092316893828761848, 0.09455215202459788, 0.09134615556066833, 0.09157476400401976, 0.091095831901381194, 0.09001646360675436, 0.09196291822956329, 0.089188754549061056, 0.090754446754887891, 0.086733711078648287], [0.092364555507456592, 0.091242402562768374, 0.092436889492713212, 0.091559979594845756, 0.092841492652212199, 0.093798030858294412, 0.094351351845986864, 0.092814046027700187, 0.093486157219819635, 0.090498151490013196], [0.091849472450780109, 0.09987135256917147, 0.095359101381023367, 0.10132711157177869, 0.096989994818717673, 0.095642645311814628, 0.094770708458483316, 0.099504889976262084, 0.095233946477410264, 0.095912229809406252], [0.096981357225800119, 0.098431927414326228, 0.10072742300061141, 0.098898806914864537, 0.099082873805034041, 0.10063185833765206, 0.10034615899080687, 0.099221510400624227, 0.098867437035043776, 0.098568081010241518], [0.10146145320773989, 0.10290476138788758, 0.10182039194103777, 0.10171670282374545, 0.10130432095639304, 0.10285746043130467, 0.10319349943771447, 0.1029627446099619, 0.10086077075694574, 0.10050071036093378]], 'Rp': [[0.77939286778673988, 0.78379075372310014, 0.77903660050560442, 0.75691093708781843, 0.75690993883190572, 0.79281350511242199, 0.76548119282328986, 0.75540866070955459, 0.77566114237892325, 0.77718635034500816], [0.77077047902704154, 0.74838529774977014, 0.77592499238852597, 0.77108749825264966, 0.77344285646834765, 0.75632672530448497, 0.77531058389168894, 0.7942725305980507, 0.77516649898011347, 0.79213834022181684], [0.77343971286186985, 0.7811615284026463, 0.77002662705139213, 0.78186660257747442, 0.77592889108537455, 0.76274494268121895, 0.76959295957424056, 0.76137871102493382, 0.77323148286234344, 0.74483235174871509], [0.75885686151109177, 0.77136712590698997, 0.7637379965318023, 0.75712573362947666, 0.76860566929133478, 0.75918656580312649, 0.74968717936109908, 0.77072287126227668, 0.77181921702477563, 0.766773258630573], [0.76937810303238807, 0.75465386095098919, 0.75083393097032181, 0.76177797822911753, 0.76189133903150008, 0.74842864001507103, 0.76323916270541503, 0.76429477418517133, 0.77410203202827355, 0.76983965493359408], [0.76609473555281116, 0.76356112846241442, 0.74975864472915243, 0.76239433570706805, 0.75868577573000173, 0.76251451363034839, 0.7538088687563389, 0.75184881181604735, 0.7600995562692493, 0.75432912516623662], [0.74772064161289276, 0.75406561814751527, 0.75457074519872191, 0.74722768393668193, 0.75155659709284284, 0.74455252421997353, 0.75489649747184262, 0.74961295847986986, 0.74332859583971711, 0.74709104962198603], [0.74055353235155419, 0.74551803447654252, 0.74512979469545415, 0.74636136686091947, 0.74570582760017257, 0.74940858658178311, 0.74136979297401795, 0.74335121765377787, 0.74994994361601441, 0.74819281963882356], [0.73628102687328378, 0.72848571847169041, 0.73660169233998429, 0.73742334699607537, 0.73809454564390775, 0.74112553158811312, 0.73446549169338082, 0.74545629305295769, 0.74011017139833268, 0.75134303184403173], [0.73410683674958854, 0.73853467283533347, 0.73203184911821528, 0.73677663684107375, 0.73267123006938562, 0.72707721050496976, 0.72644560784832646, 0.73252613291918833, 0.73124916095655701, 0.73862344837162053], [0.73486322486452571, 0.70726438223338095, 0.72272980935754105, 0.70526165872053703, 0.71683703235539997, 0.72233785968541298, 0.7257846637957609, 0.71059687926256743, 0.72362060496899205, 0.72206167609673011], [0.71815121292888973, 0.71318854691019617, 0.70511992104336951, 0.71054317570035785, 0.71194125803719077, 0.70521787589059204, 0.70659400821092722, 0.71122173648366205, 0.71141006208491686, 0.7120169592243234], [0.70522181987704136, 0.69734574176085518, 0.70136859977962518, 0.70265674174297188, 0.70177949605188183, 0.6993303818327512, 0.6974907506804654, 0.69699722251559204, 0.70749368647236088, 0.70713972983920825]]} 
average_performances = {'R^2': [0.5945641945277526, 0.5970954416593247, 0.5905487013631688, 0.5820504251965815, 0.5793808821121904, 0.5737557492169904, 0.5604104344386258, 0.5543064179336862, 0.5443473264593095, 0.5357111468984013, 0.5153859367506708, 0.502739813780906, 0.4886225788048728], 'MSE': [0.08040747091342193, 0.080429276215028558, 0.081801057860329068, 0.083131391200514132, 0.083906833430493225, 0.085002994628494338, 0.087609469263970952, 0.089013428201086736, 0.09095420915383437, 0.092539305725181042, 0.096646145282484788, 0.099175743413500467, 0.10195828159136644], 'Rp': [0.77225919493043671, 0.77328258028824903, 0.76942038098702092, 0.76378824789525468, 0.76184394760818408, 0.75830954958196695, 0.74946229116220442, 0.74555409164490605, 0.73893868499017579, 0.73300427862142581, 0.71913577913408466, 0.7105404756514424, 0.70168241705527534]}

repeats=20 
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.6396495829938857, 0.5612889131494925, 0.5990461946113412, 0.5957745834372077, 0.5121707467261551, 0.6504749290247032, 0.6153420153682677, 0.5826909245378077, 0.5731495063904792, 0.6098351538791551, 0.6508588900334185, 0.5884517645337839, 0.5535248457626974, 0.6032346640081545, 0.5895262603030731, 0.5832064644105361, 0.5928175183566615, 0.6099474954010227, 0.6146846375147488, 0.6075160948379708], [0.5969670690369691, 0.5743161132200573, 0.6102670586857839, 0.5917854446823628, 0.5923146194790289, 0.5966860399896792, 0.5782074769589376, 0.5819617791688734, 0.5792695934899292, 0.5776544597582824, 0.6183648752793831, 0.6099454726634228, 0.6293275017387701, 0.5844771726263707, 0.591322321202107, 0.5928183365193456, 0.6053449618829179, 0.5983150329518997, 0.595354003158842, 0.5875136628716549], [0.5956236217920541, 0.5861763008178589, 0.5771342767123633, 0.6136672063037389, 0.5947140365874258, 0.6023243914910243, 0.5917968547281858, 0.587370200025559, 0.6032983666702588, 0.5929550776257224, 0.5862337848152482, 0.5846739759326589, 0.6071998664672089, 0.6089911601658992, 0.5803335080070277, 0.5966011601839281, 0.6175505985508665, 0.602389041403061, 0.5748517887116238, 0.5942594525841716], [0.5891358653119354, 0.5867060786255835, 0.5926627286434955, 0.5741010531743191, 0.5787176450362084, 0.6001986310126802, 0.5741752499041918, 0.5804939049298956, 0.5852091282669638, 0.5909209557956132, 0.5824253097929503, 0.5823084908801461, 0.589864482093551, 0.5858506633227235, 0.58621719213537, 0.5905293660152653, 0.5922860254898037, 0.5676385702575235, 0.5874772954550366, 0.5858259952118468], [0.5766327092947823, 0.5861532825195422, 0.5752475420422957, 0.5758572635646546, 0.5734315944189936, 0.5676869807516705, 0.5606920994308571, 0.5790444465517595, 0.5830662916806195, 0.580786346621312, 0.5926572018087726, 0.5915257628625568, 0.5897165812466827, 0.5839473743597602, 0.5692942868249893, 0.5945928132271892, 0.5891980487406863, 0.5951130789633841, 0.5734807908658994, 0.5817504989586566], [0.5549087132619583, 0.5740673859146361, 0.5804462047759866, 0.5590587630485183, 0.5735595671026288, 0.5686313654248561, 0.572213479058808, 0.5654493324235123, 0.5623463171375422, 0.565530783688685, 0.577225551056429, 0.555589973923079, 0.5656334405155399, 0.5664309163221746, 0.5767909336362801, 0.5809364389231759, 0.5805348986039683, 0.5726003457451739, 0.5582564963929539, 0.5638617373959469], [0.5650114740559096, 0.5641328634254996, 0.5713231599593842, 0.5565859387826031, 0.5631765479856754, 0.5622709637034062, 0.5468497643588243, 0.5651409567970467, 0.5739032469441904, 0.5577981170360427, 0.5645014407514823, 0.5638036361404994, 0.5691608813734761, 0.5598999648877081, 0.5714833747232457, 0.5445152152322073, 0.5664750332841729, 0.5550206795405498, 0.5623527662997693, 0.5583730956513281], [0.5637368933410106, 0.554691786173255, 0.5460713996228341, 0.5499244340899742, 0.564775269676628, 0.5585677416212604, 0.5379079383613639, 0.5732604892443682, 0.5537506868855981, 0.5488940956203899, 0.5455010406210816, 0.5565759659861529, 0.5576173065763793, 0.5563391317051336, 0.5632591883838765, 0.5634556010931613, 0.5614664548375377, 0.5786129761556829, 0.5533900600611825, 0.5507142268982366], [0.541060295603788, 0.5443073156760023, 0.5488379546709299, 0.5425290048660698, 0.5549584458309463, 0.5421189335765492, 0.5473757580376137, 0.5442661020815125, 0.5380879715352043, 0.55672305550423, 0.5531381342513337, 0.5369611363689188, 0.5490909125755061, 0.5502421311772232, 0.542532797685707, 0.5404132945959315, 0.5561190327770673, 0.5436423348845312, 0.5480176758286689, 0.549666000082718], [0.5276922847373597, 0.5308992972348408, 0.5436252447880883, 0.529807985548643, 0.5480073781707027, 0.5340760654462249, 0.5388546973479356, 0.539467060224857, 0.5361927391904217, 0.5398662374080101, 0.5148456592601869, 0.531013643165943, 0.5366224183903829, 0.5296028535057018, 0.5321805058362963, 0.5287673055847253, 0.5283564646411945, 0.5134319197247821, 0.5283102575974495, 0.5368721757083816], [0.5144398031368066, 0.5164480422135225, 0.5291657860372936, 0.5044084586603406, 0.5200904276364993, 0.5106756221910416, 0.5095653158260434, 0.5064161031514822, 0.519512530831521, 0.5318930237463468, 0.5140471783111349, 0.5155358213500691, 0.5205215298776056, 0.5117818989264538, 0.523105149910843, 0.5184906014311805, 0.5223597788601975, 0.5176745579645313, 0.5310767983732868, 0.5162797753177271], [0.5061858485396357, 0.49963981794904755, 0.49034798563991, 0.5101006450818713, 0.5037442729863317, 0.5012410513751451, 0.5192935952069397, 0.4967971860157273, 0.4973871983883875, 0.4973976653845499, 0.498595538083209, 0.5119797498512264, 0.5044798558186426, 0.5064150514957755, 0.5076588954087577, 0.5073301195474269, 0.5105084955878787, 0.494831045798124, 0.49871353764057824, 0.5084515133768499], [0.46530781183638703, 0.4863557393923289, 0.4833040885793184, 0.4859188850313604, 0.47497370318485577, 0.4802931373896492, 0.4827521265255551, 0.4732211825791687, 0.4859014139518356, 0.4770518877101533, 0.4822276417639786, 0.49380437797119714, 0.4891701146890405, 0.48249346424060946, 0.4819292854684468, 0.48345418132636264, 0.4919436219610763, 0.4871027708792208, 0.4829339342809964, 0.4890648791788459]], 'MSE': [[0.07371736617706294, 0.086562326069366133, 0.082062677490392422, 0.08176651625766912, 0.096746348208436042, 0.069561469185594693, 0.074691278801952782, 0.080711036337781164, 0.081366745327595233, 0.079711709972846975, 0.071015956670687122, 0.081332598867472045, 0.089641847597225793, 0.078942508427376587, 0.081375159507113312, 0.082581373431421301, 0.079551180083086898, 0.07695309108346686, 0.077860334300067335, 0.079851639226415999], [0.080264514613500842, 0.084548833474206386, 0.077836084260093336, 0.081421514521637775, 0.080577692744409291, 0.080140984850970168, 0.084427372601869485, 0.08356779653178642, 0.083433330739245887, 0.083878173899332539, 0.076022054568080144, 0.078244029423387762, 0.075426968051089394, 0.081913894974946028, 0.082444670819473001, 0.082136798852139037, 0.080450360215020694, 0.08101680405169491, 0.080978384997986638, 0.082267323452177382], [0.080254747691219361, 0.083163952241714648, 0.083846841087072327, 0.077381834684223105, 0.080764641939376686, 0.079667821346825526, 0.082444706524652508, 0.081521302245378069, 0.07904676193739929, 0.08052468102862613, 0.081661441961394951, 0.082025338875351836, 0.078614344672973083, 0.07792912989649986, 0.084904787978098625, 0.080315050174685682, 0.077134907716441006, 0.0784210054855356, 0.084466754836615893, 0.080803748097713651], [0.081695789985552283, 0.082808262659550894, 0.08064921971377971, 0.083827982020070607, 0.083415717999763037, 0.080008949082013156, 0.08459671049976536, 0.083604146211466598, 0.082606074742935409, 0.081910831136960793, 0.08378455328335932, 0.083221748319828134, 0.082013940114937831, 0.081816146401728795, 0.082526140536778606, 0.08157579658390457, 0.080844117249114791, 0.086610880616675628, 0.081228618974627922, 0.082724815709914135], [0.08396685674684444, 0.081664155362791119, 0.084953460966000163, 0.084317228299093036, 0.085159208627983554, 0.086685886233150683, 0.087122174594526869, 0.083985562614258241, 0.083900248965734239, 0.083905732351833365, 0.081754318676751245, 0.080837295812046239, 0.08117505447678007, 0.082942838582004436, 0.08543975242527066, 0.080833559148755424, 0.08179571336881078, 0.080521545241280273, 0.083963912172626498, 0.083477794515105133], [0.088280797375717215, 0.08491513902850803, 0.084023498995666898, 0.0877436167553792, 0.084776428260982251, 0.086314926842189985, 0.084911702009373272, 0.086493913394248653, 0.087239207859471118, 0.086964881692228158, 0.084431624731277577, 0.088798479946946313, 0.086445980390783536, 0.086526646061969817, 0.084422929062528504, 0.083844474603569627, 0.083754892434541345, 0.084991999507155261, 0.087783968877279753, 0.086898622114358684], [0.086641242292695375, 0.087308656847531307, 0.085553089868715071, 0.088047371200316193, 0.086980997036742017, 0.088059441282516193, 0.090371688489585919, 0.08642412692597011, 0.085624942786361818, 0.088052934545256756, 0.086812925029418911, 0.087073657860797293, 0.085945789052289404, 0.087711693869374094, 0.085585159301823796, 0.09052197084940089, 0.08640531290122784, 0.087978538587047239, 0.087119873766410963, 0.0875584435170257], [0.087098613849195664, 0.088677187639560978, 0.09011563100945813, 0.089448237400039654, 0.087150945146626677, 0.088217447730066262, 0.092118635027125681, 0.085656410283040232, 0.088756297801937001, 0.089931678927652609, 0.090574369891297454, 0.088409790595313981, 0.088147230433951285, 0.088334321950287106, 0.08706644488810826, 0.087566667273250992, 0.087748737732927615, 0.084488315653334256, 0.089239929125885062, 0.089641228891630731], [0.092169184546303143, 0.090944192930776047, 0.089402872427102861, 0.091194373136267992, 0.088805446400827978, 0.091368210558191276, 0.090283598268403376, 0.091252905467798656, 0.092347526853339343, 0.088610362198135034, 0.089076645992304276, 0.092561416299132726, 0.090110622777356625, 0.089678830761210762, 0.09167170425787384, 0.091749528897599575, 0.088590924901730497, 0.090954930445988721, 0.090042582394008794, 0.090042513522507389], [0.094491886518588267, 0.093360315004681754, 0.09111245153055908, 0.093804391522172931, 0.090048105172796544, 0.092705002600089445, 0.091593494867588277, 0.091999169206410658, 0.092409388545440688, 0.091516975519796401, 0.096882379912741068, 0.093626207204947492, 0.092310465333887717, 0.093770676689829136, 0.093132696093090439, 0.093983973046317754, 0.09375581540367707, 0.096779883495978325, 0.094163201165183924, 0.092522064033451534], [0.096585208104988093, 0.096574351078412835, 0.093742000848959145, 0.098879245332477439, 0.095779963245166813, 0.097787820965482469, 0.097897351665456503, 0.097955958611278759, 0.095670277804631207, 0.093241836076920034, 0.096616877716521776, 0.096509827402556078, 0.095216950531065783, 0.097293718527353246, 0.094907625254231145, 0.096031785811995077, 0.094932056684271002, 0.096140362596263351, 0.093711040958513653, 0.096475576696632231], [0.098743811621149286, 0.099770285900577141, 0.10152635910676461, 0.097891407349839643, 0.09911553880494535, 0.099331366874512633, 0.095793523102513989, 0.10045840216839834, 0.1006884057486821, 0.10026466941699626, 0.09999443221833311, 0.097162450317181667, 0.098811637143288264, 0.098336753958968029, 0.098238814623460638, 0.098532380507733275, 0.097955834945034584, 0.1006413372091353, 0.099935176442564222, 0.098257171504776766], [0.10660563897236158, 0.10224279719169251, 0.10278871228151691, 0.10268826745437774, 0.10464334767348794, 0.10375421271171242, 0.10322009190206859, 0.1051707505339738, 0.10281597405753298, 0.10403366264334039, 0.10347323858526995, 0.10108162416338184, 0.10184458999616026, 0.10341652344299737, 0.10363833805362246, 0.10292041758052706, 0.10135091389545355, 0.10233021189414995, 0.10319214668312375, 0.10219948494584773]], 'Rp': [[0.80178856050791436, 0.74939652752131236, 0.77421843458987161, 0.77363134263095823, 0.71819318514477193, 0.80706958671088436, 0.7861709108434688, 0.76646773447044569, 0.75862507067548135, 0.78116130310596588, 0.80740769768664766, 0.76717595919982895, 0.74459012958367388, 0.77953142623415683, 0.76793274924557997, 0.76419346932384247, 0.77014870946318481, 0.78210194441267156, 0.78690375849489735, 0.77984696177310353], [0.77360561244817727, 0.75783969803528073, 0.78139903065528704, 0.76941672584302145, 0.76973697235123495, 0.77487028428497617, 0.76203770438067286, 0.76423185855070164, 0.76240425180219351, 0.76083507304835041, 0.78680569911070419, 0.78174942852481755, 0.79397769888437331, 0.76641139000515468, 0.76976181259320109, 0.77044688187888721, 0.77816674175619227, 0.7740600192585867, 0.77268313978486458, 0.76681266275397109], [0.77197931248623375, 0.76739444349341634, 0.7601608288209486, 0.7854726346387797, 0.7713407328651104, 0.77642573316480501, 0.77014916227540264, 0.7672439466295442, 0.77749101675052501, 0.77102310518314532, 0.76765340934923754, 0.76473640872582538, 0.77929997298498177, 0.78048059249357837, 0.76222214622152007, 0.7725496658594514, 0.78704654772234273, 0.77971394052045206, 0.75830781039441397, 0.77118805770513099], [0.76773519674412216, 0.76619699424534016, 0.7706021224249513, 0.75814842876306354, 0.76088419820531139, 0.77598465753043488, 0.75889789459514656, 0.76209484731663746, 0.76572872347162413, 0.76880403779872863, 0.76393042867698868, 0.76438433624037982, 0.76835262911341418, 0.76560051064236956, 0.7657914118680802, 0.76921599690867459, 0.77075252013883766, 0.75354318614878468, 0.7674835802039095, 0.76552685313763369], [0.76049645572677194, 0.76629537278116244, 0.7587082563143499, 0.75909580080175698, 0.75780112599755267, 0.75455024480686761, 0.74984591156814806, 0.76192987766060827, 0.76374617634679798, 0.76291509676060953, 0.77082045107681241, 0.76928674905609307, 0.76857446783756544, 0.76476830720515032, 0.75567676663284877, 0.77176403980639141, 0.76809703422985609, 0.77324646853488788, 0.75818916098477396, 0.76309990895010704], [0.74698161064085733, 0.7577733724020258, 0.76191322957258834, 0.74873318731619343, 0.75762645505959958, 0.7540888025245277, 0.75693232509911645, 0.75291215503468789, 0.75057710353279772, 0.75217390603296641, 0.7615437947166952, 0.74646024199103123, 0.75282984302589151, 0.75285156776468021, 0.76028611840821891, 0.76247346072837563, 0.76271245284100542, 0.75784603454589095, 0.74854247773481575, 0.75243277671830533], [0.75220990310892744, 0.75147963310647781, 0.75623457676424322, 0.74650883377330091, 0.75164615859928952, 0.75097189611968607, 0.74004752788363348, 0.75188080839490012, 0.75827328194299026, 0.74815744851434696, 0.75163597518237069, 0.75181770458072994, 0.75532522000970914, 0.74968554041455571, 0.75679224640311338, 0.73819156834546873, 0.7532039862436859, 0.74676344375060189, 0.7506497692929458, 0.74772807785996021], [0.75104773027198457, 0.74591765031464319, 0.74051657017713346, 0.74237952943244956, 0.75163576444994173, 0.74785301168657559, 0.73525522279171351, 0.75744776382167167, 0.74531733602364902, 0.74117409647999433, 0.73915165250535275, 0.74708315549074122, 0.74820308270012614, 0.74669813492299142, 0.75091637902541808, 0.75103404902102766, 0.74944778803635759, 0.76137355915598603, 0.74461176272091378, 0.7427545810685604], [0.73680420351553411, 0.73784946717162536, 0.74106668410209942, 0.7383354335383715, 0.74579153360256323, 0.73774019527634216, 0.74026173877853019, 0.73778421867648458, 0.73515233493070875, 0.74673024823143519, 0.74373875569144221, 0.73421212916496548, 0.74137724458376564, 0.74183521174772538, 0.7368005389729837, 0.73533034052715851, 0.74705161979034984, 0.7383091516566056, 0.74073279829593974, 0.74177503639907083], [0.72821497818517822, 0.73061011993163016, 0.73904879468282703, 0.72891593172109281, 0.74104073338285059, 0.73213765415139309, 0.73606009941460449, 0.73566309741286373, 0.73391135522743356, 0.73524766078328396, 0.71967661974979114, 0.72925118708445769, 0.73383319342327802, 0.73012092048029953, 0.73050560236254658, 0.72848419058963865, 0.7288646825536238, 0.71823760991630992, 0.72791805524983588, 0.73363382527823529], [0.7180892824229349, 0.71945245550774461, 0.72868634319712422, 0.71249900608330674, 0.72259491117050245, 0.71505844757552506, 0.71557519950051385, 0.71294630386737778, 0.72210056591337002, 0.7299213545639911, 0.71940728771955165, 0.71879935051694488, 0.72223409237120018, 0.71714392755490597, 0.72486189527618983, 0.72177421872601366, 0.72501019998271987, 0.72064265667513261, 0.73108184262305997, 0.72017096705733663], [0.71179445176007494, 0.70904292151420467, 0.70211854526325401, 0.71499374047141262, 0.70988978749608844, 0.70986472298845749, 0.72265165006030985, 0.70641153457445349, 0.70773345693694589, 0.70536502025726866, 0.70955800257093593, 0.71683281855309355, 0.71135681555203245, 0.71249448794306469, 0.71346185878127633, 0.71236570778962072, 0.7155718261535623, 0.70583210087165826, 0.70750608647960367, 0.71504922457137465], [0.68417772086462059, 0.69871985595580577, 0.69853952469254599, 0.69813728491092364, 0.69044281093541715, 0.69525041727797499, 0.69570117228662676, 0.68874640162272205, 0.69812192668169382, 0.69226277660732149, 0.69553786606378976, 0.70317542756795814, 0.70000098460593152, 0.69657800352264099, 0.69482094509967829, 0.6966746794411105, 0.70370111437791905, 0.6986687482574262, 0.69536189645667812, 0.70196725598508358]]} 
average_performances = {'R^2': [0.596659559264028, 0.594610649768231, 0.5949072334787943, 0.5851372315677553, 0.5809937497367532, 0.5687036322175927, 0.562088956046651, 0.5569256343477552, 0.5465044143805227, 0.5324246096756066, 0.5176744101876963, 0.5035549534588006, 0.48296021239701936], 'MSE': [0.080300158151151518, 0.081049879382152357, 0.080744690021089888, 0.082573522092136378, 0.083420114959082303, 0.085978186497208745, 0.087288892800525347, 0.08841940606253447, 0.090542918651842941, 0.09319842714336142, 0.096097491795658824, 0.099072487948242777, 0.10317054723312995], 'Rp': [0.77332777308093292, 0.77186263429753244, 0.77209397341424224, 0.76548292770872162, 0.76294538365395548, 0.75488454578451347, 0.75046018001454695, 0.74699094100486163, 0.73993394423268499, 0.73106881557905867, 0.72090251541527228, 0.71099473802943469, 0.69632934066069341]}
'''