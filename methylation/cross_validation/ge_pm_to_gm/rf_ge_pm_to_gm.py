'''
Script for using a random forest regressor to predict the promoter region
methylation values, using gene expression as features.
'''

import sys, os
project_location = os.path.dirname(__file__)+"/../../../../"
sys.path.append(project_location)

from HMF.methylation.load_methylation import load_ge_pm_top_n_genes, filter_driver_genes, filter_driver_genes_std
from HMF.code.statistics.statistics import all_statistics_matrix

from sklearn.ensemble import RandomForestRegressor
from sklearn.cross_validation import KFold

import numpy

''' Model settings '''
no_genes = 100      #13966
n_estimators = 100  # number of trees
max_depth = None    # until what depth of feature splits we go

''' Load in data '''
#(R_ge, R_pm, genes, samples) = load_ge_pm_top_n_genes(no_genes)
#R_ge, R_pm, R_gm, genes, samples = filter_driver_genes()
R_ge, R_pm, R_gm, genes, samples = filter_driver_genes_std()

X1 = R_ge.T
X2 = R_pm.T
X = numpy.concatenate((X1,X2),axis=1)
Y = R_gm.T

''' Compute the folds '''
n = len(X)
n_folds = 10
shuffle, random_state = True, None
folds = KFold(n=n,n_folds=n_folds,shuffle=shuffle,random_state=random_state)

''' Run the RF regression to predict Y from X '''
all_MSE, all_R2, all_Rp = numpy.zeros(n_folds), numpy.zeros(n_folds), numpy.zeros(n_folds)
for i, (train_index, test_index) in enumerate(folds):
    print "Training fold %s for the Random Forest regressor." % (i+1)
    
    ''' Split into train and test '''
    X_train, Y_train = X[train_index], Y[train_index]
    X_test,  Y_test  = X[test_index],  Y[test_index]
    
    ''' Train and predict '''
    rf = RandomForestRegressor(n_estimators=n_estimators,max_depth=max_depth)
    rf.fit(X=X_train,y=Y_train)
    Y_pred = rf.predict(X=X_test)
    
    ''' Measure performance '''
    rows, cols = Y_test.shape
    no_datapoints = rows * cols
    MSE, R2, Rp = all_statistics_matrix(R=Y_test, R_pred=Y_pred, M=numpy.ones((rows,cols)))
    
    all_MSE[i], all_R2[i], all_Rp[i] = MSE, R2, Rp
    print "MSE: %s. R^2: %s. Rp: %s." % (MSE,R2,Rp)

print "Average MSE: %s +- %s. \nAverage R^2: %s +- %s. \nAverage Rp:  %s +- %s." % \
    (all_MSE.mean(),all_MSE.std(),all_R2.mean(),all_R2.std(),all_Rp.mean(),all_Rp.std())


"""
160 driver genes (std)
    10 folds, 1 estimator:
    Average MSE: 1.46709001973 +- 0.182019120002. 
    Average R^2: -0.485011107561 +- 0.127933832686. 
    Average Rp:  0.248016713438 +- 0.0410400877553.
        
    10 folds, 10 estimators:
    Average MSE: 0.781619341636 +- 0.140983626516. 
    Average R^2: 0.213895178348 +- 0.0456605569223. 
    Average Rp:  0.470531880539 +- 0.0455656476401.
    
    10 folds, 100 estimators:
    Average MSE: 0.713779710382 +- 0.164694799003. 
    Average R^2: 0.285708305385 +- 0.0388017416. 
    Average Rp:  0.551205476354 +- 0.0375892971606.
"""