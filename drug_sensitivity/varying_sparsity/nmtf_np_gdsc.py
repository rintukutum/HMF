"""
Test the performance of NP-NMTF for recovering the GDSC dataset, where we vary 
the fraction of entries that are missing.
We repeat this 10 times per fraction and average that.
"""

import sys, os
project_location = os.path.dirname(__file__)+"/../../../"
sys.path.append(project_location)

from HMF.code.models.nmtf_np import nmtf_np
from HMF.code.generate_mask.mask import try_generate_M_from_M
from HMF.drug_sensitivity.load_dataset import load_data_without_empty

import numpy, matplotlib.pyplot as plt, random

''' Settings '''
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
repeats = 20
iterations = 1000

init_FG = 'kmeans'
init_S = 'random'
expo_prior = 1.
K, L = 4, 4

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
    
        NMTF = nmtf_np(R,M_train,K,L)
        NMTF.initialise(init_S,init_FG,expo_prior=expo_prior)
        NMTF.run(iterations)
    
        # Measure the performances
        performances = NMTF.predict(M_test)
        for metric in metrics:
            # Add this metric's performance to the list of <repeat> performances for this fraction
            all_performances[metric][-1].append(performances[metric])
            
    # Compute the average across attempts
    for metric in metrics:
        average_performances[metric].append(sum(all_performances[metric][-1])/repeats)
    
 
print "repeats=%s \nfractions_unknown = %s \nall_performances = %s \naverage_performances = %s" % \
    (repeats,fractions_unknown,all_performances,average_performances)

'''
1000 iterations
repeats=10 
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.5741460515433148, 0.5686191260030459, 0.5649491534666086, 0.525572361142702, 0.5115320657279884, 0.5675076220285762, 0.5851169312502029, 0.5262619893231215, 0.5686970719143005, 0.5730023178421657], [0.5472946594510142, 0.5143617535648558, 0.5425717118879698, 0.5365181880099156, 0.5525264850314415, 0.5159555166095834, 0.5371438059237321, 0.5829319098108354, 0.5611493878084688, 0.5655455055046974], [0.5585804282455544, 0.5728510453377595, 0.5536929241995628, 0.5696514238315323, 0.5345815388641648, 0.5345520702065443, 0.5594741896318245, 0.5323285072053758, 0.5471383786270179, 0.5213829125503158], [0.5046172227486141, 0.5435022786199599, 0.503000264402141, 0.5213852087364605, 0.4236867910334373, 0.5244136764091856, 0.4709822944777762, 0.5481985816643684, 0.5236918224779579, 0.5332495938638928], [0.5111063614486924, 0.5074915830961142, 0.46660980720853207, 0.49147717827915993, 0.5103653069973269, 0.5012399723279444, 0.4920158005896934, 0.5111046276073463, 0.535223203510347, 0.42259572416833724], [0.47226747558795523, 0.494807265990191, 0.4504844109400884, 0.4111989883537077, 0.3986190749950832, 0.024706310907554818, 0.4657763823469212, 0.489210873965615, 0.496268815494157, 0.48454572078142677], [0.44622231282366065, 0.36726769169544493, 0.13060727414683493, 0.45200773065523936, -0.4283296420026952, 0.4055566181927702, 0.43293199813620553, 0.4474159212647212, 0.041152808842784716, 0.4607608262878281], [-269256.2240936693, 0.2873474829984338, -0.4629419112684814, 0.3420823203130765, -0.7523558861617183, -176.15396908525253, 0.38710282752064495, 0.40083239161268325, -659.141635090169, 0.20809308806829174], [0.04321166051766279, 0.13976418325208062, -24.243565490380863, -0.04320096667933271, -0.06833177397114198, 0.23393836500783116, -0.9550636788238067, -1.1202488886879731, 0.25785975611855794, -812.056100767108], [-0.7547810975798295, -296.6542550411777, 0.0014184980748567222, -2693.5875542822755, -130.92101419435372, -0.27363027230285986, -0.22159438564486367, -2.310272333845568, -938.4156437540988, -161.070345526955], [-180165.90872534286, -0.8862360036319812, -10952.937186505216, -2.560362797652484, -6.1732696861981236, -5111.803099979735, -57.87669372384709, -172.25017205338816, -284270.1734941804, -705980.3921641462], [-120974.49254056875, -488883.91858519014, -2817.08851777897, -39859.11803866698, 0.280079971462014, -5881.178417321092, -21023.72499231114, -25783.38953826947, -133225.83137252176, -587.792618124669], [0.12428869292374456, -109068050.03450751, -3135856.3820224903, -50052.06510868305, -498402.54153391893, -16361.297987445552, -3399135.0626703002, 0.0453593107576542, -72495.14560817298, -1234697.5169788094]], 'MSE': [[0.083419549602003457, 0.083489396510671846, 0.086541593089467433, 0.094059104539909552, 0.096590912405265364, 0.088746088192461645, 0.082763568885286062, 0.094807327048425566, 0.086015170739359603, 0.083163023977356698], [0.089785984117727757, 0.097653094091309914, 0.091457406074417366, 0.093175629115309591, 0.089626594757158645, 0.096101440748263961, 0.092251280354844686, 0.082882650584226267, 0.087839666163073607, 0.086296186606419648], [0.087685461128121756, 0.086796658678508221, 0.088735448975027553, 0.085427515466715065, 0.092883510013641937, 0.094332492069856388, 0.088014505947701771, 0.093352492671605142, 0.090396478236549435, 0.094576482780171264], [0.099367662103845747, 0.090860112698343681, 0.098227641816234459, 0.095833448523728756, 0.11411187678531387, 0.09445644232760271, 0.10497810926880495, 0.090223133451140039, 0.094532380814080622, 0.092539400152726617], [0.097925705112070771, 0.098576865334428429, 0.10649585970485761, 0.10178705825063157, 0.097546268706115671, 0.098908070131836237, 0.10101159163655619, 0.097730804870452395, 0.092316535323317822, 0.11529727930087977], [0.10509603994758659, 0.10068881940738354, 0.10976745745655879, 0.11804033348011889, 0.11982882030568751, 0.19566352345655924, 0.10576720615446442, 0.10204633580858267, 0.10055372617927925, 0.10223165445793174], [0.11060226654448652, 0.12572979549903648, 0.1729305654812652, 0.10897068379235207, 0.28428388140131383, 0.11905292835497555, 0.11314594813597979, 0.10990570827359339, 0.19201677241689971, 0.10717792416435377], [53707.759212561024, 0.14263587403581302, 0.29144278922051148, 0.13180559038907105, 0.34899762995661388, 35.339562387175782, 0.12203030713732382, 0.12003673046263878, 132.11910729903749, 0.15823314901157945], [0.19041242339329337, 0.17282830399907759, 5.0365074494759554, 0.20887382658991943, 0.21320920019173059, 0.15272705216445581, 0.38809140589735519, 0.42377891559265363, 0.14864048087241175, 161.65601647690414], [0.35135407314754619, 59.450435748095501, 0.19870544653544592, 537.48631234963318, 26.253726072405566, 0.25210469497849319, 0.24348787861303725, 0.66092010165332038, 187.64222746358374, 32.266556433731033], [35898.114356706632, 0.37587981906498941, 2183.5274103017518, 0.71054759508753418, 1.4292167631950561, 1017.2677548665315, 11.770472755245638, 34.524062130706888, 56702.570416450711, 141197.53578080321], [24164.78927074093, 97690.475516806968, 560.35124529699146, 7939.2407927417908, 0.14330698460058952, 1172.5399970352532, 4196.5153631491867, 5148.1911243589248, 26586.206792288394, 117.55915421236485], [0.17462053580470061, 21720807.631996911, 624492.71137374139, 9970.0096482254157, 99433.593236498768, 3265.4806964907834, 678519.93356985296, 0.19045222197145675, 14462.622989450861, 245972.39169956776]], 'Rp': [[0.76117721707319708, 0.76153765054803346, 0.76134166663594371, 0.73618873773536153, 0.73036406028392764, 0.76095654766549992, 0.77102500554847031, 0.73490767335123675, 0.7624543659854498, 0.76374776873289185], [0.74799003645625695, 0.72757394963710575, 0.74403896856989804, 0.73992804876075546, 0.75119602475709168, 0.73099810062628867, 0.74263081113763862, 0.77331170984925945, 0.75535525615844046, 0.75916846107387614], [0.75615842994897486, 0.76253478109683948, 0.75496246308036685, 0.76289321807860844, 0.74189494390976307, 0.73940627405954618, 0.75426504264411209, 0.74064627204030908, 0.75018058585599701, 0.73494935314241605], [0.72697513546204673, 0.7463495122791054, 0.7255170848047503, 0.73615634342216074, 0.69214997646883913, 0.73972432318182468, 0.70862710450688893, 0.74931587485234374, 0.73783199989243908, 0.74195115682126833], [0.73247069753645866, 0.72713950844960018, 0.70983026618053013, 0.72249967884246558, 0.7289024306594194, 0.72385832558307961, 0.72259462445110201, 0.73174198499294996, 0.74499962194212777, 0.69170137531520937], [0.71163882023223313, 0.72609941436298631, 0.70212736024925682, 0.68563434391901212, 0.68579459078061467, 0.56719802736626268, 0.71048353337812842, 0.72139797994580235, 0.72339136394418002, 0.71745616915887067], [0.69918762633784781, 0.66267791160756284, 0.58754283836982257, 0.70046040326899761, 0.49334584103653978, 0.67645659741182407, 0.69371728758369322, 0.7018772908787152, 0.56835647285936131, 0.70633176811618326], [-0.0081245389011495705, 0.6347684099806995, 0.48203378541374997, 0.65477820709665224, 0.44162054636025316, 0.073816296103459522, 0.67393998682167777, 0.68073183920167091, 0.053426062950854676, 0.61484015772514466], [0.56809582829268235, 0.590843001708797, 0.10895648552624776, 0.55600133819611097, 0.53661311453420768, 0.61104091807133309, 0.42238357337390131, 0.41375846513416442, 0.61749034398660285, 0.047123260969704477], [0.44212287429190444, 0.077629349925023822, 0.52943256023608831, -0.000133651474130291, 0.065820894986794165, 0.49370422746173692, 0.49880733011978501, 0.31608329490191178, 0.019066474039969156, 0.041194868400885473], [0.020192242817150534, 0.40498832399038714, 0.030575189832604828, 0.30779265596972938, 0.22529381395615117, 0.028107935991871072, 0.1083230835370312, 0.064924960886788508, 0.029762741491927563, 0.022136691774030486], [0.027083891376184471, 0.050811616504727319, 0.016240987226211288, 0.020663309504861831, 0.61577192068514952, 0.054646396284317195, 0.0029590128106269774, 0.0012385740471890885, 0.012196748394282189, 0.053384598758423912], [0.57412993483405983, 0.0098065044937355825, 0.025328846890367691, 0.010596237790628982, 0.0091499981425980075, -0.0083629642025421988, 0.032082793328605211, 0.54120639488405708, 0.026734541804985842, 0.044180878544260033]]} 
average_performances = {'R^2': [0.5565404690242026, 0.5455998923602514, 0.5484233418699652, 0.5096727734433795, 0.49492295652334944, 0.41878853193627014, 0.27555935400427944, -27009.110953753163, -83.7811737600755, -422.4207672390159, -118672.0961404419, -83903.62545407817, -11747504.987676933], 'MSE': [0.087959573499020727, 0.090706993261275154, 0.090220104596789849, 0.097513020794182156, 0.10075960383711464, 0.11596839166541528, 0.14438164740642562, 5387.6533064317455, 16.859108553508101, 84.480583026237682, 23704.782589819217, 16757.60125636154, 2339692.4740283499], 'Rp': [0.75437006935600115, 0.74721913670266116, 0.74978913638569344, 0.73045985116916667, 0.7235738513952944, 0.69512216033373464, 0.64899540374705478, 0.43018307527530136, 0.44723063297937521, 0.24837282228899685, 0.12420976402476717, 0.085499705559197378, 0.1264853166510756]}

repeats=20 
fractions_unknown = [0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.550090693038225, 0.5313998837548772, 0.5961429540020577, 0.5882012616162373, 0.5518983679453954, 0.5650413028415848, 0.6021499179587786, 0.495549951093486, 0.5367952317799929, 0.49075936064648784, 0.548864052406508, 0.5267243020988588, 0.5559502777514425, 0.5896949077018137, 0.5793856143304117, 0.5396458425156635, 0.5553276702424566, 0.5480773918549725, 0.6025135328910838, 0.5624017904469083], [0.5288853508644493, 0.5496807802487576, 0.5460681583063635, 0.5676170907655931, 0.5490497557669795, 0.5469380163416369, 0.6063171828906335, 0.5150513904024998, 0.5363198427113852, 0.5432316907681563, 0.5659909010643345, 0.5806537370247566, 0.5616391550709009, 0.5542399978327455, 0.5912605852062849, 0.5369126900010779, 0.49479678718034237, 0.5461247403026575, 0.5698847253163536, 0.5593687402398939], [0.539047093049753, 0.5665531278296373, 0.5579268255495817, 0.5557511295751304, 0.5398007821135903, 0.5629661586953097, 0.5341598522906713, 0.5318762001460637, 0.5761513897044432, 0.45110419280330394, 0.5451309346352124, 0.5427847937222441, 0.5819327966614438, 0.5571362524664105, 0.5693562888961021, 0.5614679494138338, 0.3847059245153772, 0.5284697970603159, 0.5119919296616131, 0.5543222943306628], [0.06618295412107977, 0.5241128913294637, 0.5373174250515727, 0.5360087738418102, 0.5510625046546918, 0.5248272742865927, 0.5386168386669649, 0.5373808196552639, 0.5564574815301763, 0.5502449059430621, 0.5286552917900883, 0.5151812383143277, 0.510840296878323, 0.5253547784789938, 0.5089559228831406, 0.5264268094556105, 0.48226587377351515, 0.518551773519074, 0.5188671335712687, 0.539665518539671], [0.31939365877278647, 0.5060145391627706, 0.5161919204987628, 0.528310831327272, -0.04508926269393454, 0.5273500929948165, 0.5123772826677777, 0.4801554520414191, 0.5440749196580057, 0.495758730078961, 0.5273338461498935, 0.5019628280357531, 0.5300108005820834, 0.4433270459406199, 0.5062670011049086, 0.5028729969643894, 0.5155140312478119, 0.46678261420177625, 0.5088015900108274, 0.518812981584166], [0.45900876497386, 0.4581780645289102, 0.3650541237148619, 0.4768026866126084, 0.32315286975339474, 0.4621115509962156, 0.49495188226996556, 0.45375270882416396, 0.48653066485857666, -0.5698515508205273, 0.4339855880295863, 0.4734087809028049, 0.47705887179263984, 0.329181655958657, 0.433386814414949, 0.45151515111629814, 0.4233298268681148, 0.4817045657772171, 0.4713276661722543, 0.4827855267252811], [0.3689476298186144, 0.4443479185260073, -28.08503814430715, -0.6870618828208308, 0.4140003302382699, -16.522285079630695, 0.4713351735828337, 0.3758265077601485, 0.45269298157397075, 0.35100678563149745, -0.5412205861599544, 0.40318144859884175, 0.4758780415225424, 0.4119526608488736, 0.4480048910708674, 0.440186228416781, 0.36465685954894556, 0.4303079206168062, 0.4083367176628442, -125.57254993355919], [0.3673741609786433, -1262.1266590988541, 0.23648916310609946, 0.38663701294404595, -6.523526132121087, -8812.497318810887, 0.3357909479967559, 0.3874408415796168, 0.3798598415982867, 0.3826743753445868, 0.10255728518754026, 0.41936500551940703, 0.27468094843571944, 0.38744770562510533, -3.63269544282765, 0.30952543673622135, 0.38741877812320225, 0.1503687062666973, 0.3527617559701416, 0.4036416930001161], [-3.969806283478867, 0.23812989928489914, -126.11602723539552, 0.207295296653775, -8051.8866970966765, -62.02478999235544, 0.08149997284496624, 0.12082835276703618, 0.23020627978354058, -18.174435165097492, -1921.8775166954156, 0.3481510366792302, 0.26096027123667853, -3555.079171144616, 0.02955132070987032, -2.1295380139368345, -2.1915358328434085, -15.836968748667346, 0.30141830410600323, -0.859666730540793], [-799.2973472661431, -3233.1048179116337, -62.166296339210696, -812.9417110841168, -987.161710251258, -2314.550106603232, -56.63488091912891, -3.2699879276580965, -1631.8080894346292, -5.140592933372734, -43.928790251530124, -9.173482924119321, -55.987161524885124, -44.22304879232435, -24.246447021067084, -960.9065190801293, -4805.985494862272, -1237.4382914447012, -28.28528922749572, -0.3024635820244237], [-0.301278029124078, -2189664.781365922, -877.6034906554374, -415.06020069664896, -2338.6576214742286, -103142.46554343456, -10.901191849894168, -412722.0668912695, -83.00554618923702, -32.37300679935581, -5800.183831571415, -115.54186753603295, -0.09883862025167778, -262.1777944908827, -2.6149444509473687, 0.36706726762381203, -631.1933940998376, -51217.28900868198, -17.325543798205164, -70.66608087816482], [-23208.301302937845, 0.2441358393242259, -41.62271244799114, -1622.5792451584339, -22041.31957559156, -7625356.3099996215, -17357.167536079767, -16020.077830356498, -53075.581641261044, -598.1067707358574, -21407.69204757933, 0.31853566121676113, -2910.109688960552, 0.3223881565921318, 0.3461205667921107, -2736696.7997100092, 0.3248726291914905, -43.70639562689822, -2612.06178605837, -1196.04981210676], [-328922.0577955024, -0.43825421539462117, -0.1926151431428369, 0.08519424421969046, -2784841770.3806205, 0.1328603046704192, 0.14894990852506163, -5847960.1906594215, 0.261584408206991, -0.150456973343013, -10.017330533647282, -11128.242153313993, 0.13611968201485514, 0.2103937465024559, 0.12668645363353015, -1252153.2186574282, -0.02980022897412793, -0.12024252425119997, 0.23794268135085894, -47896.04449422938]], 'MSE': [[0.091307097039927704, 0.09240066058444861, 0.081309623432864866, 0.082502282516739023, 0.091119699877634699, 0.087855691291610555, 0.080243421453074726, 0.10083278625408718, 0.091739126844478144, 0.09866357724201999, 0.090202901121340051, 0.093853475171978437, 0.088438185852994053, 0.081285688357322097, 0.084242363119216401, 0.091146738664649632, 0.087796752608004971, 0.088073743738046009, 0.07975319118738261, 0.088354514414192384], [0.094542350378786971, 0.089824808320535091, 0.089041851407183251, 0.085636683370492489, 0.090116137989370668, 0.092264992379066393, 0.078852825958000639, 0.098057426322541441, 0.092530426963536347, 0.091859309319322846, 0.086876326123693851, 0.084383936141204346, 0.086465977962399965, 0.088636261729618387, 0.082185374802912964, 0.092654745196591018, 0.10084009162012565, 0.090744596169302971, 0.087359571787942139, 0.087596689218745707], [0.091149800889936308, 0.085700723078238839, 0.087830341144494936, 0.087869690176186746, 0.091505368662338521, 0.086308441832605984, 0.093525812156389929, 0.092577329423844931, 0.085208501015030677, 0.10850690268544654, 0.090594180699934995, 0.09150833869246125, 0.084198037420824143, 0.087324877900611733, 0.085810823672909153, 0.087570026399962156, 0.12221223598915673, 0.094757357422952632, 0.096713160571216067, 0.08913536533084597], [0.18506151585247468, 0.094657489649078885, 0.092039679471709115, 0.091984782309310245, 0.090144780526713333, 0.095238669648103791, 0.092152289271912893, 0.093059834314882794, 0.088755972996199153, 0.090489234174916708, 0.094466224775451219, 0.097940856355594977, 0.097321483766774672, 0.094293288396523164, 0.097060066784135729, 0.094020302304870906, 0.10303770348184189, 0.095999183514344416, 0.0958515663453825, 0.092229566417956904], [0.13573125466628053, 0.098358929488103194, 0.097166154931389068, 0.094066780896074564, 0.20791550496918121, 0.094502176054638273, 0.096738480436804608, 0.10310380365473087, 0.09084503530818018, 0.099800971303592015, 0.095209263188314047, 0.099946170094423276, 0.093571198549700016, 0.11093970440533932, 0.09861331856726889, 0.099044984063958688, 0.096951496662387171, 0.10663381597314728, 0.098726895853489219, 0.095375774963894683], [0.10820034098951806, 0.10777406597821514, 0.12635418857880387, 0.10429737649137727, 0.13596455158494669, 0.10758134240811497, 0.10092124704071721, 0.10820127763208427, 0.10245823725524408, 0.31605569601675754, 0.11293750182560824, 0.10489983844907903, 0.1046766720580674, 0.13364320184818446, 0.11227462896543877, 0.10861426379133472, 0.11505018281430378, 0.10278025484038134, 0.10509133855957137, 0.10295115687062431], [0.12559500263835061, 0.11084472574373305, 5.8007071553689133, 0.3364405215392417, 0.11680693098387478, 3.5003485955517024, 0.10554524989019319, 0.12463478172234629, 0.10949620407586483, 0.12936356445883418, 0.30724628317881236, 0.11853299916547459, 0.10491594629605304, 0.11713838824385714, 0.11031954035150082, 0.11142655717419284, 0.12651511171700405, 0.11408962373906491, 0.1188234415123058, 25.214733327041575], [0.1259282362446672, 252.32636139593581, 0.15170544368323, 0.12229820855678812, 1.4969743219234704, 1761.7530114391427, 0.13238825832547849, 0.1218830212645339, 0.12379225896015313, 0.1235061109071493, 0.17967313770507659, 0.1161668761354363, 0.14482823333248118, 0.12161813841215928, 0.9254328973228465, 0.13796019402167017, 0.12225751589013793, 0.16900416394866066, 0.12904798681215884, 0.11851566817222813], [0.98809070380673214, 0.15151892360901709, 25.41505585695381, 0.15764103535343357, 1606.6321173452181, 12.534299103465969, 0.18353567169435295, 0.17511846199164544, 0.15320815361500353, 3.8122000649324188, 383.68303131046406, 0.13034679468409444, 0.14745064240082162, 705.59760029837207, 0.19380310367880282, 0.62061096202372867, 0.63505978693470322, 3.3576171721457118, 0.13935812545316123, 0.37012511151402083], [159.7175871289017, 645.99415286823046, 12.60063175752774, 162.79564623043399, 197.15267908324392, 462.2491386193991, 11.476814744909644, 0.84807995953745041, 325.49052103709215, 1.2327822560016626, 8.9376349874320358, 2.0288545325039302, 11.32279043371806, 9.006699180173845, 5.0276105297140834, 190.81964324544182, 958.88645199740449, 246.48590663310821, 5.82929570847406, 0.25992141116890383], [0.25970130422110499, 436521.09593912779, 174.68156917363589, 82.926923020837663, 466.88687576390686, 20572.635033860821, 2.3704640652084961, 82419.626483484433, 16.718443842022303, 6.6536861138407613, 1157.5094536701456, 23.192405390209498, 0.21884069184372593, 52.445799768788724, 0.72101395888319264, 0.1263208599692123, 126.19756725056666, 10210.945308279555, 3.6590333792805056, 14.278636336557971], [4625.6214618746571, 0.15087632614688035, 8.4886399068996763, 324.11732496304802, 4397.2333218955864, 1524889.4511314339, 3470.0478639392741, 3191.6893952702221, 10579.390700731648, 119.62058778977934, 4264.0158725586234, 0.13597781962965139, 579.92089329487737, 0.13533496955534982, 0.12993825365794295, 545618.49785139749, 0.13475299589580947, 8.9431786313050399, 520.43004762958594, 238.83031790208253], [65525.500034670411, 0.2873166106313792, 0.23776161010939525, 0.18228808845488711, 554496226.76380837, 0.17298519031492737, 0.1695987704953483, 1168365.9681440056, 0.14715531380675176, 0.22895511470261404, 2.2010756615098712, 2224.8453928224344, 0.17266551850671405, 0.15753796474394036, 0.17449274701646633, 249107.45785984673, 0.20529689122045858, 0.22324161169622941, 0.15187856343172276, 9547.9802404663897]], 'Rp': [[0.74776098490898013, 0.74565947030641488, 0.77481044593637693, 0.77166370698407283, 0.75362528321754363, 0.75768168774631772, 0.78154076158706098, 0.71447549686258716, 0.74431753836846537, 0.71963251962335906, 0.74575046356778041, 0.73628558925299292, 0.7511201804404507, 0.7735452245706681, 0.76663377041086767, 0.74366319475471743, 0.75223205388216585, 0.74883267067750559, 0.78014331161819872, 0.75729717978698163], [0.74062627204181886, 0.75025129578653238, 0.74671264169552998, 0.75976448334273816, 0.74858620755661698, 0.74861921765553319, 0.78254975553450346, 0.7306314376568489, 0.74108733165260732, 0.7465589116918393, 0.75845049479314519, 0.76697383579416223, 0.76032400611668294, 0.75174522823587664, 0.77181525099540427, 0.74256956603717394, 0.72576818027696632, 0.74973263527341893, 0.75851421721524659, 0.75672837057021403], [0.74209377947170785, 0.75966346682897334, 0.75431938377456897, 0.75462616616053835, 0.7448891590188319, 0.75843163177150485, 0.74548389032301698, 0.73726568827597649, 0.76413817711167165, 0.70471528797097749, 0.74976486109324192, 0.74537086910703432, 0.76892472520100008, 0.75404997720770617, 0.76150148932191231, 0.75532115533886057, 0.68022117051383479, 0.73701691983940332, 0.72741099560755806, 0.75160790692766244], [0.57921405770968293, 0.7377719555481741, 0.74592704994992864, 0.7452010516941644, 0.75148744054111027, 0.73796020342988922, 0.74422293029670494, 0.74719065122861805, 0.75390885062593649, 0.74994629009375446, 0.74062481673775526, 0.73504454523119123, 0.73057375958203763, 0.73840593516991271, 0.72997666002626815, 0.73973030847978893, 0.72201476518185226, 0.73288221323726876, 0.73456991012198491, 0.74485486115781163], [0.65360104122226281, 0.72778189979692254, 0.73284495383284887, 0.73931332981399933, 0.55595948423722519, 0.73915261558984879, 0.73170383760585711, 0.71535195171368493, 0.74928044514020298, 0.72218062160577101, 0.73803385715840741, 0.72739790576763141, 0.73850045250027574, 0.69723848189057647, 0.72883203602781732, 0.72532452613209919, 0.73143463375783246, 0.70822115245567741, 0.73039275366265732, 0.73459246183585647], [0.70176288008036458, 0.70434451760600014, 0.66484385636316801, 0.71232451210721515, 0.65538980168657457, 0.70308439265203937, 0.72301926929816551, 0.69983009016130293, 0.71944750008580449, 0.46033438933049575, 0.69136371830010523, 0.70882629161775323, 0.71574751525933888, 0.65704623262352024, 0.69552365121677817, 0.70088054174049896, 0.68460602198454901, 0.71903415105764945, 0.71542333136958114, 0.71568504835312308], [0.67168873865111844, 0.70253798522875877, 0.10824278683789748, 0.4440065541259377, 0.68208258297469515, 0.13368139582094174, 0.70974552498638921, 0.66825391486333974, 0.70200879423052887, 0.66264531230425983, 0.48751310966799782, 0.68361966056327905, 0.71417212970728938, 0.68764276853258821, 0.69989010723038825, 0.69905779444074789, 0.66225468776003182, 0.69531766035931686, 0.68194086786568842, 0.077816200262384186], [0.6670868754616267, 0.030055681273190412, 0.61448400958044525, 0.67476315714116042, 0.18774858127890173, 0.017891785562386759, 0.65494553974084069, 0.68308358780030676, 0.67389556171083898, 0.6700488118714043, 0.5822195839114126, 0.68847720801626211, 0.63782680744579823, 0.67356489138759601, 0.28490200912592811, 0.648102359914149, 0.67467089864940621, 0.59891478092589456, 0.66123877855508206, 0.6859300235232455], [0.28198570009856799, 0.61975497356674925, 0.082121175013973535, 0.60996540089629991, 0.0071917670677053604, 0.089970331594898201, 0.58533203756552632, 0.58748473288283853, 0.61223461219270114, 0.1494627834518277, 0.033988493956783571, 0.65244726086301896, 0.62970948807301586, 0.030871590009712922, 0.55368886132886286, 0.33843660242398466, 0.33808437438431715, 0.15637741779054146, 0.63550395893278966, 0.44195117524840261], [0.035870950212981659, -0.014240572827776399, 0.10171227639027815, 0.028662719255482371, 0.030852341220509463, 0.023905209123311046, 0.11142975976314477, 0.27211297559585812, -0.0026053733488055012, 0.27978529896963644, 0.040985009346579858, 0.18790613021686758, 0.070590068565875769, 0.062214385059504093, 0.13290269643943214, 0.038578467256800475, 0.050514652232137268, 0.013486871885069021, 0.13459175257274095, 0.48409152405165345], [0.48619889765121171, 0.017071631364415269, 0.039540818686478539, -0.00041738356412686822, 0.028270345766053719, -0.010515914905779161, 0.16062097677007048, 0.011493794518953002, 0.047493500992197908, 0.082464908418767233, 0.033702809217625813, 0.075314486509370809, 0.53866650456732512, 0.027778063324866445, 0.32958568625100199, 0.64832075848207149, 0.068412719123284768, 0.025236657918100792, 0.13835488693813269, 0.065411041366675679], [0.0057817420010564105, 0.60987792933132523, 0.12847634118614049, 0.031312406231312533, 0.033542576350357137, 0.040317271943988577, 0.0036393860599334728, 0.03701460707778572, 0.029793878409406956, 0.056674254722233447, 0.050317199373000415, 0.62650977171658895, 0.048489747937257015, 0.625076127277293, 0.63799888244035452, 0.013719325439581159, 0.62193983025334043, 0.10094070662621825, 0.028510323358727364, 0.036619810192292795], [0.029194037663915966, 0.4592582638346126, 0.51027986605177333, 0.55540454343965362, 0.01503367095696685, 0.5548159641554149, 0.56962177712909301, 0.0018084221969949465, 0.60041224603715637, 0.51867858772225794, 0.19187943030449839, 0.044351574266606769, 0.56227796752894155, 0.59378264960031468, 0.56685689516823801, 0.017070726547883046, 0.52508722312740286, 0.50995444777432974, 0.59216656714268379, 0.035460386091755447]]} 
average_performances = {'R^2': [0.5558307153458621, 0.55250156591529, 0.5376317856560349, 0.5048488253142345, 0.4703111950165434, 0.39336881067349166, -8.257374676552999, -503.9758082913139, -687.9164056102478, -855.8276264690467, -138370.19701865903, -526209.296500084, -139616491.98716742], 'MSE': [0.08855607603860062, 0.089523519158068651, 0.092000365758269406, 0.098790224517908892, 0.10566208570154487, 0.12103636819991863, 1.8451761975196448, 100.93211767533484, 137.25388943141556, 170.90814211722085, 27592.657474967134, 105141.84927347917, 27799550.161386497], 'Rp': [0.75333357672517531, 0.7519004669961431, 0.74484083504329912, 0.73207541280219202, 0.71635692208737267, 0.68742588564470142, 0.57870592882067895, 0.55049254664379388, 0.37182813686712596, 0.10416735709906404, 0.14065025946983489, 0.18832760589640971, 0.37266976233702465]}
'''