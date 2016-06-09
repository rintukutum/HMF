'''
Script for using multiple matrix factorisation to predict the promoter region 
methylation values, using gene expression as a second dataset.

We append the columns of the two matrices, and mark the unknown rows as 0 in M.
'''

project_location = "/home/tab43/Documents/Projects/libraries/"
import sys
sys.path.append(project_location)
from HMF.methylation.load_methylation import load_ge_pm_top_n_genes, filter_driver_genes
from HMF.code.models.hmf_Gibbs import HMF_Gibbs

from sklearn.cross_validation import KFold

import numpy

''' Model settings '''
no_genes = 100 #13966
iterations, burn_in, thinning = 100, 80, 2

settings = {
    'priorF'  : 'exponential',
    'priorG'  : ['exponential','normal'], #PM,GE
    'orderF'  : 'columns',
    'orderG'  : ['columns','columns'],
    'ARD'     : True
}
hyperparameters = {
    'alphatau' : 1.,
    'betatau'  : 1.,
    'alpha0'   : 0.001,
    'beta0'    : 0.001,
    'lambdaF'  : 0.1,
    'lambdaG' : 0.1,
}
init = {
    'F'       : 'kmeans',
    'G'       : ['random','least'],
    'lambdat' : 'exp',
    'tau'     : 'exp'
}

E = ['genes','samples']
#I = {'genes':no_genes, 'samples':254}
K = {'genes':10, 'samples':10}
alpha_m = [1., 1.] # PM, GE


''' Load in data '''
#(R_ge, R_pm, genes, samples) = load_ge_pm_top_n_genes(no_genes)
R_ge, R_pm, R_gm, genes, samples = filter_driver_genes()

X, Y = R_pm.T, R_ge.T
R, C = [], []

''' Compute the folds '''
n = len(R_ge)
n_folds = 10
shuffle = True
folds = KFold(n=n,n_folds=n_folds,shuffle=shuffle)

''' Run HMF to predict Y from X '''
all_MSE, all_R2, all_Rp = numpy.zeros(n_folds), numpy.zeros(n_folds), numpy.zeros(n_folds)
for i, (train_index, test_index) in enumerate(folds):
    print "Training fold %s for NMF." % (i+1)
    
    ''' Split into train and test '''
    M_X, M_Y_train = numpy.ones(X.shape), numpy.ones(Y.shape)
    M_Y_train[test_index] = 0.
    M_Y_test = 1. - M_Y_train
    
    D = [
        (X, M_X,       'samples', alpha_m[0]),
        (Y, M_Y_train, 'samples', alpha_m[1])
    ]
    
    ''' Train and predict '''
    HMF = HMF_Gibbs(R,C,D,K,settings,hyperparameters)
    HMF.initialise(init)
    HMF.run(iterations)
    
    ''' Compute the performances '''
    performances = HMF.predict_Dl(l=1,M_pred=M_Y_test,burn_in=burn_in,thinning=thinning)
    
    all_MSE[i], all_R2[i], all_Rp[i] = performances['MSE'], performances['R^2'], performances['Rp']
    print "MSE: %s. R^2: %s. Rp: %s." % (performances['MSE'], performances['R^2'], performances['Rp'])

print "Average MSE: %s +- %s. \nAverage R^2: %s +- %s. \nAverage Rp:  %s +- %s." % \
    (all_MSE.mean(),all_MSE.std(),all_R2.mean(),all_R2.std(),all_Rp.mean(),all_Rp.std())

HMF.approx_expectation_all(burn_in,thinning)

"""
160 driver genes, F ~ Exp, G_ge ~ N, G_me ~ Exp (kmeans, least/random)

    K = {'genes':1, 'samples':1}
        alpha_n = [1., 1.]
            Average MSE: 0.528897254113 +- 0.0522417575275. 
            Average R^2: 0.559634676153 +- 0.0355780244151. 
            Average Rp:  0.74916479729 +- 0.0244541602587.

    K = {'genes':5, 'samples':5}
        alpha_n = [1., 1.]
            Average MSE: 0.426424340109 +- 0.0535872760878. 
            Average R^2: 0.645080860465 +- 0.0382176674342. 
            Average Rp:  0.804053167205 +- 0.0240809636776.
        
    K = {'genes':10, 'samples':10}
        alpha_n = [1., 1.]
        
        
        
160 driver genes, G ~ Exp, G ~ N (kmeans, least)

    K = {'genes':1, 'samples':1}
        alpha_n = [1., 1.]
        
        
160 driver genes, F, G ~ N (kmeans, least)

    K = {'genes':1, 'samples':1}
        alpha_n = [1., 1.]
"""