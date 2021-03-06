"""
Measure the time it takes to train a single model.

Time taken: 28.0801270008 seconds. Average per iteration: 0.0561602540016.
"""

import sys, os
project_location = os.path.dirname(__file__)+"/../../../../"
sys.path.append(project_location)

from HMF.code.models.bnmtf_gibbs import bnmtf_gibbs
from HMF.drug_sensitivity.load_dataset import load_data_without_empty

import time


''' Load datasets '''
location = project_location+"HMF/drug_sensitivity/data/overlap/"
location_data =                 location+"data_row_01/"
location_features_drugs =       location+"features_drugs/"
location_features_cell_lines =  location+"features_cell_lines/"
location_kernels =              location+"kernels_features/"

R_gdsc,     M_gdsc,     _, _ = load_data_without_empty(location_data+"gdsc_ic50_row_01.txt")
R_ctrp,     M_ctrp,     _, _ = load_data_without_empty(location_data+"ctrp_ec50_row_01.txt")
R_ccle_ec,  M_ccle_ec,  _, _ = load_data_without_empty(location_data+"ccle_ec50_row_01.txt")
R_ccle_ic,  M_ccle_ic,  _, _ = load_data_without_empty(location_data+"ccle_ic50_row_01.txt")

R, M = R_ccle_ec, M_ccle_ec


''' Settings BNMTF '''
iterations = 500
init_S = 'random'
init_FG = 'kmeans'
K, L = 10, 10

alpha, beta = 1., 1.
lambdaF = 1.
lambdaS = 1.
lambdaG = 1.
priors = { 'alpha':alpha, 'beta':beta, 'lambdaF':lambdaF, 'lambdaS':lambdaS, 'lambdaG':lambdaG }


''' Run the method and time it. '''
time_start = time.time()

BNMTF = bnmtf_gibbs(R,M,K,L,priors)
BNMTF.initialise(init_FG=init_FG, init_S=init_S)
BNMTF.run(iterations)
    
time_end = time.time()
time_taken = time_end - time_start
time_average = time_taken / iterations
print "Time taken: %s seconds. Average per iteration: %s." % (time_taken, time_average)