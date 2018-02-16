"""
Test the performance of HMF for recovering the CTRP dataset, where we vary the 
fraction of entries that are missing.
We repeat this 10 times per fraction and average that.
This is the real-valued D-MTF version with column-wise posterior draws.
"""

import sys, os
project_location = os.path.dirname(__file__)+"/../../../../../"
sys.path.append(project_location)

from HMF.code.models.hmf_Gibbs import HMF_Gibbs
from HMF.code.generate_mask.mask import try_generate_M_from_M
from HMF.drug_sensitivity.load_dataset import load_data_without_empty,load_data_filter

import numpy, random


''' Settings '''
metrics = ['MSE', 'R^2', 'Rp']

fractions_unknown = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]
repeats = 10

iterations, burn_in, thinning = 200, 180, 2
settings = {
    'priorF'  : 'normal',
    'orderG'  : 'normal',
    'priorSn' : 'normal',
    'priorSm' : 'normal',
    'orderF'  : 'columns',
    'orderG'  : 'columns',
    'orderSn' : 'individual',
    'orderSm' : 'individual',
    'ARD'     : True
}
hyperparameters = {
    'alphatau' : 1.,
    'betatau'  : 1.,
    'alpha0'   : 0.001,
    'beta0'    : 0.001,
    'lambdaF'  : 0.1,
    'lambdaG'  : 0.1,
    'lambdaSn' : 0.1,
    'lambdaSm' : 0.1,
}
init = {
    'F'       : 'kmeans',
    'Sn'      : 'least',
    'Sm'      : 'least',
    'G'       : 'least',
    'lambdat' : 'exp',
    'tau'     : 'exp'
}

K = {'Cell_lines':10, 'Drugs':10}
alpha_n = [1., 1., 1., 1.] # GDSC, CTRP, CCLE IC, CCLE EC


''' Load data '''
location = project_location+"HMF/drug_sensitivity/data/overlap/"
location_data = location+"data_row_01/"

R_ctrp,     M_ctrp,   cell_lines, drugs   = load_data_without_empty(location_data+"ctrp_ec50_row_01.txt")
R_ccle_ec,  M_ccle_ec                     = load_data_filter(location_data+"ccle_ec50_row_01.txt",cell_lines,drugs)
R_gdsc,     M_gdsc                        = load_data_filter(location_data+"gdsc_ic50_row_01.txt",cell_lines,drugs)
R_ccle_ic,  M_ccle_ic                     = load_data_filter(location_data+"ccle_ic50_row_01.txt",cell_lines,drugs)


#''' Seed all of the methods the same '''
#numpy.random.seed(0)
#random.seed(0)

''' Generate matrices M - one list of (M_train,M_test)'s for each fraction '''
M_attempts = 10000
all_Ms_train_test = [ 
    [try_generate_M_from_M(M=M_ctrp,fraction=fraction,attempts=M_attempts) for r in range(0,repeats)]
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
     
        R = [(R_ctrp,    M_train,   'Cell_lines', 'Drugs', alpha_n[1]),
             (R_gdsc,    M_gdsc,    'Cell_lines', 'Drugs', alpha_n[0]),  
             (R_ccle_ic, M_ccle_ic, 'Cell_lines', 'Drugs', alpha_n[2]),
             (R_ccle_ec, M_ccle_ec, 'Cell_lines', 'Drugs', alpha_n[3])]
        C, D = [], []

        HMF = HMF_Gibbs(R,C,D,K,settings,hyperparameters)
        HMF.initialise(init)
        HMF.run(iterations)
        
        # Measure the performances
        performances = HMF.predict_Rn(n=0,M_pred=M_test,burn_in=burn_in,thinning=thinning)
        for metric in metrics:
            # Add this metric's performance to the list of <repeat> performances for this fraction
            all_performances[metric][-1].append(performances[metric])
            
    # Compute the average across attempts
    for metric in metrics:
        average_performances[metric].append(sum(all_performances[metric][-1])/repeats)
    
 
print "repeats=%s \nfractions_unknown = %s \nall_performances = %s \naverage_performances = %s" % \
    (repeats,fractions_unknown,all_performances,average_performances)

'''
repeats=10 
fractions_unknown = [0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9] 
all_performances = {'R^2': [[0.5617566707767097, 0.3446004815443049, 0.43648767017448653, 0.34350255630883253, 0.40450529583326855, 0.31882965651187767, 0.5028850532650179, 0.3134244615084898, 0.4478967075566638, 0.3995058505080479], [0.41589645018898347, 0.39513053416498933, 0.4294670613393604, 0.39272656663883476, 0.4687378341811962, 0.3857059642372396, 0.4094001206971617, 0.42978983991169517, 0.434533132128771, 0.42562827959269356], [0.4475156564595969, 0.4222098229864839, 0.4441198141390169, 0.3968860436368449, 0.4084310220386118, 0.43459201835899286, 0.42260030979708707, 0.42723531464410036, 0.39595301771881974, 0.4323999724782259], [0.43298543230831676, 0.458837571810514, 0.4108973661441889, 0.41797964712889646, 0.4477480897948749, 0.4110380661873958, 0.4288627806590407, 0.407547319759628, 0.44113490546465184, 0.3820684060360867], [0.40821776823278044, 0.4231901893025397, 0.4110611421589757, 0.4180071644359915, 0.41321487558962733, 0.41420839331955617, 0.40525409160232506, 0.4031741167034679, 0.41968256050845776, 0.4260346222498548], [0.41155693240808067, 0.4088389056952808, 0.4040686171019814, 0.4147301591454914, 0.42220092741518966, 0.4144922530566775, 0.41890568910707304, 0.41531132232562384, 0.3940367038710729, 0.42517940621202777], [0.4018604419944045, 0.4057975402001881, 0.4089297098536344, 0.3943591907029934, 0.4054503935157382, 0.3992595728182531, 0.4168541600177982, 0.41321725284177246, 0.4222497725713448, 0.4118473968271831], [0.3764927998996237, 0.40750097314956546, 0.40518663936175503, 0.38532707210952544, 0.3855452865137423, 0.37575077059143147, 0.38714400235997914, 0.397352794992774, 0.41026863559224447, 0.3928416171443462], [0.38392401026481715, 0.41240790997558296, 0.39089666960332614, 0.392699744543319, 0.389764313401612, 0.4005431086827721, 0.3763314976666512, 0.3739666562678482, 0.35533708282484167, 0.3805345936746656], [0.3770333048239687, 0.3958618441008924, 0.3993617155460828, 0.36180615200784594, 0.3797727803913282, 0.3662786674483237, 0.37462052681984925, 0.37270477054911866, 0.3798963999271685, 0.37781637600384577], [0.3530396626027671, 0.3716947531231223, 0.3575269473461151, 0.36683436631851796, 0.3775766610981416, 0.3575902119623088, 0.3738328682085009, 0.3635407597404414, 0.3787232287236689, 0.35610819435321184], [0.3517196692097493, 0.3434083350527428, 0.36252230366783555, 0.34330114632637543, 0.3577435701562286, 0.34373835243784756, 0.3539218969478566, 0.3582927594314631, 0.36625021365177624, 0.36761072181046595], [0.3380669912372647, 0.3215779861149697, 0.3458810669918908, 0.33607585048972677, 0.35338488720211514, 0.36859542871548134, 0.331302263465189, 0.33677016027797435, 0.3311619400904128, 0.3636916571374862], [0.32878553564336144, 0.2999102575891709, 0.33014871458314765, 0.3453393079933924, 0.329885666397676, 0.33055614514409604, 0.319620688210118, 0.3192469554626792, 0.30885816705213454, 0.34403084416852137], [0.30788924835221887, 0.27892282842792804, 0.25194623382386394, 0.3055455011508774, 0.3111752311593753, 0.3075518033600515, 0.28005667559135905, 0.3212201742909302, 0.3044662396266874, 0.29795594543252846], [0.282035183589216, 0.2300900352256393, 0.26544575830660466, 0.26939581849769545, 0.16495075033989226, 0.2817813907144824, 0.2745514344087241, 0.264006778103011, 0.23715511328515093, 0.2129761689061821]], 'MSE': [[0.06934303169743998, 0.096913643540383843, 0.090963382227247966, 0.11755318225192327, 0.10559553655130136, 0.10842778319373422, 0.085217104475916947, 0.10386566760965786, 0.084571417363006968, 0.099134371212473107], [0.090526883426342103, 0.094033474260895825, 0.089015109352829136, 0.10014616975355745, 0.082967574404791383, 0.097691736977903912, 0.096948585647854774, 0.091233790930522612, 0.088602121503823267, 0.09311419873669699], [0.08578031213126032, 0.093819824662882079, 0.091113266392496797, 0.096834419013272693, 0.094203642797239251, 0.092479969837066703, 0.091527409518843389, 0.088352394636050144, 0.092578181689837488, 0.091555402220031612], [0.091452638745396039, 0.088497218341929959, 0.091824115466437178, 0.091174677279145633, 0.088920917018717488, 0.094810682770838567, 0.091627216709321613, 0.092625455875103721, 0.086932216596312936, 0.097600150708769373], [0.094168706770479227, 0.092790743180979615, 0.093791006358261708, 0.092851796153944274, 0.091815101213713723, 0.091214485923668862, 0.09424699794764721, 0.093749481599738199, 0.091772926466040738, 0.091678491473378171], [0.093865721136299998, 0.091521029597117928, 0.095446941232607482, 0.091735714831241419, 0.092273941448314675, 0.092393393211832223, 0.093731901856456259, 0.093041269878815391, 0.097254049003207679, 0.089774284924868816], [0.09589751563240842, 0.094198665442763674, 0.093071581827940578, 0.095931111969917368, 0.094091471386945708, 0.096041068710929503, 0.092854647812166305, 0.093970846166368194, 0.092616283541058692, 0.094799734277266179], [0.099130744775287008, 0.093628746084757936, 0.093999413178456712, 0.096873983185345444, 0.096807844461917938, 0.10091327890738255, 0.096513796924372133, 0.097444621313228744, 0.093990912267836887, 0.09614109715637692], [0.097428702815509971, 0.093596363182855469, 0.096209895622600683, 0.097023074596275044, 0.096405422837664845, 0.094895777942642812, 0.098641460397557862, 0.099777903711532168, 0.10315944262708836, 0.099132420767601412], [0.099861378171691592, 0.096473533259823357, 0.096013015075209346, 0.10140475317048914, 0.098509387957214908, 0.10022459841929024, 0.100205390427937, 0.10008000821847181, 0.098957773486291076, 0.09881953981951011], [0.10330002986771245, 0.099858693507921245, 0.10158182607699139, 0.10046142317950359, 0.099410112619283009, 0.10150914265951817, 0.09955909281051771, 0.10166116180308639, 0.098915443748217133, 0.10331042985809227], [0.10332648098100715, 0.10540622295234796, 0.10085655304287404, 0.10385902300550895, 0.10273745693698932, 0.10358871412093409, 0.10308887731964868, 0.10162791298474784, 0.10053620553260187, 0.10002645352983083], [0.10548714724383397, 0.10688497081359141, 0.103733515305082, 0.10548696207285249, 0.10331686953024655, 0.099385028317813207, 0.10667068663760966, 0.10546968740108216, 0.10651773497037831, 0.10133617845176833], [0.10668702964758314, 0.11137211856020443, 0.10724299562613149, 0.10406930358336711, 0.10617488811130484, 0.10685649708315659, 0.10886509521445731, 0.10870150954775368, 0.11026852634814473, 0.10415426201017827], [0.10943966642928106, 0.1148398603622047, 0.11993028036798033, 0.10993675523448397, 0.10963828905369327, 0.11013523958959982, 0.11488334903423429, 0.10827164320845323, 0.11099793996613438, 0.11152849003040796], [0.11393311813732927, 0.12209974512959011, 0.11674832771184505, 0.11626184388011362, 0.13237235759702692, 0.11390517880587428, 0.11542975347137685, 0.11723725448987526, 0.12024681050410088, 0.12495579492660418]], 'Rp': [[0.7514155756376304, 0.59915480352351369, 0.66416764267439665, 0.60235822202685529, 0.63966961338307782, 0.57703150364323186, 0.70995806414244356, 0.57664620716623094, 0.6755314233916424, 0.63614164346835977], [0.64927615996391874, 0.63567189023764714, 0.65937512693435607, 0.62928199205663449, 0.68649389920027892, 0.6255863623044492, 0.64449894923638218, 0.65946300420542781, 0.66190455134176818, 0.65732054601930656], [0.67135934139868159, 0.65191706068348698, 0.66855803989949036, 0.63381775986011457, 0.64423702779189018, 0.66157819181727107, 0.65324584688112119, 0.656454399270477, 0.63871172022178202, 0.65935564514499656], [0.65941232906096603, 0.67848473778415275, 0.64490230943131466, 0.64909127821758061, 0.66975972014087704, 0.6440763178894493, 0.65838418130463072, 0.64142188559813207, 0.66587692510594121, 0.62331085483486215], [0.64102856143641296, 0.6518782823980287, 0.64528671965281903, 0.64942849911823397, 0.64697845903552842, 0.64805799893602445, 0.64070423336308124, 0.63889265080475965, 0.64976743352189936, 0.65594352099237607], [0.64472667354316049, 0.64403189965931917, 0.63874749204543213, 0.64776366568761312, 0.65167312314029369, 0.64636006701584614, 0.64958746511824905, 0.64766124588341778, 0.63174873166593126, 0.65437660668458963], [0.63706178499673327, 0.64135047449159766, 0.64460392826751378, 0.6332591966910126, 0.64077976398399472, 0.63473615687645391, 0.64833213215585683, 0.64600068358718032, 0.65216250632321948, 0.64500805704969899], [0.62258983900114651, 0.64186285609562943, 0.64090354931371363, 0.6265062669542022, 0.6277178323498025, 0.61902938000408947, 0.62927608424295556, 0.63446279240516024, 0.64376264446682341, 0.63143914988688077], [0.62484960405439971, 0.64391329491575766, 0.62889234876608202, 0.63064173649601962, 0.62922985024606493, 0.63708789738921501, 0.62039858318173324, 0.61984478289002309, 0.60683131905154719, 0.62387491061299361], [0.6197670681746188, 0.63358183510760535, 0.63505297280323469, 0.60994950451892271, 0.62224490388675913, 0.61405831168798408, 0.6181719984932017, 0.61894390471966809, 0.62373174458585645, 0.62383049273477442], [0.60470825442020348, 0.61727162852729867, 0.60678484936806631, 0.61326054269069641, 0.62077781388781395, 0.60858418131084135, 0.61698375309494913, 0.61176789949777943, 0.62221498150900034, 0.60640653362047559], [0.60080781847807252, 0.59758892012715115, 0.61141578424858312, 0.59834711433695931, 0.60777328257197505, 0.59715474255962941, 0.60682458958689234, 0.60810431366276685, 0.61062158977360104, 0.61378765173163474], [0.59733684930147712, 0.58838395536840515, 0.6012964866864714, 0.59413456482537674, 0.60332663469641579, 0.61323464392684501, 0.58852563234454691, 0.59182900994242804, 0.59026584820887729, 0.60874273545050606], [0.58924664163495288, 0.57004720120335761, 0.5863913358465348, 0.60125778690253751, 0.58602828576125165, 0.58791199784225023, 0.58245089278705231, 0.5814594111400806, 0.57521540520452408, 0.59671345028076184], [0.57789647636820463, 0.55402869643026553, 0.5355647622835501, 0.58022295354546527, 0.57515697317385373, 0.57570637948492087, 0.55712609037722471, 0.57688276080058565, 0.5734502670577557, 0.57056551253702548], [0.5614344218019679, 0.53596028753149305, 0.5466396553111561, 0.5551528344119091, 0.49958771186425244, 0.55987500454612027, 0.54918822958405078, 0.54867575299529603, 0.53644192748513231, 0.52908745243965205]]} 
average_performances = {'R^2': [0.4073394403987699, 0.4187015783080925, 0.4231942992257781, 0.4239099585293594, 0.4142044924103576, 0.4129320916338499, 0.4079825431343311, 0.3923410591714987, 0.3856405586905437, 0.37851525376184236, 0.36564676534767954, 0.3548508968692341, 0.34265082317225115, 0.3256382282244298, 0.29667298812158205, 0.24823884313765981], 'MSE': [0.096158512012308558, 0.092427964499521759, 0.091824482289898063, 0.091546528951197248, 0.092807973708785171, 0.093103824712076191, 0.094347292676776467, 0.096544443825496234, 0.097627046450132857, 0.099054937800592852, 0.10095673561308434, 0.10250539004064907, 0.1044288780744258, 0.10743922257322816, 0.11196015132764729, 0.11931901846537363], 'Rp': [0.64320746990573818, 0.65088724815001697, 0.65392350329693127, 0.65347205393679064, 0.6467966359259163, 0.64566769704438531, 0.64232946844232619, 0.63175503947204037, 0.62655643276038364, 0.6219332736712625, 0.61287604379271254, 0.60524258070772652, 0.59770763607513488, 0.58567224086033032, 0.56766008720588512, 0.54220432779710293]}
'''