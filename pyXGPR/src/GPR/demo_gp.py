#===============================================================================
#    Copyright (C) 2009  
#    Marion Neumann [marion dot neumann at iais dot fraunhofer dot de]
#    Zhao Xu [zhao dot xu at iais dot fraunhofer dot de]
#    Supervisor: Kristian Kersting [kristian dot kersting at iais dot fraunhofer dot de]
# 
#    Fraunhofer IAIS, STREAM Project, Sankt Augustin, Germany
# 
#    This file is part of pyXGPR.
# 
#    pyXGPR is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
# 
#    pyXGPR is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
# 
#    You should have received a copy of the GNU General Public License 
#    along with this program; if not, see <http://www.gnu.org/licenses/>.
#===============================================================================
'''
Created on 15.09.2009

Demo_GP: Standard GP to demonstrate prediction (and training) for generated noisy data.

@author: Marion Neumann
'''

from GPR import gpr
from Tools import general
from numpy import *
from matplotlib import pyplot

## DATA:
## necessary data for   GPR  X, y, Xstar     
## NOTE: y must have zero mean!!

## GENERATE data from a noisy GP
l = 20      # number of labeled/training data 
u = 201     # number of unlabeled/test data
X = array(15*(random.random((l,1))-0.5))

## DEFINE parameterized covariance funcrion
covfunc = ['kernels.covSum', ['kernels.covSEiso','kernels.covNoise']]
## SET (hyper)parameters
#logtheta = array([log(0.3), log(1.08), log(5e-5)])
#logtheta = array([log(3), log(1.16), log(0.89)])
logtheta = array([log(1), log(1), log(sqrt(0.01))])

print 'hyperparameters: ', exp(logtheta)

### GENERATE sample observations from the GP
y = dot(linalg.cholesky(general.feval(covfunc, logtheta, X)).transpose(),random.standard_normal((l,1)))
### TEST POINTS
Xstar = array([linspace(-7.5,7.5,u)]).transpose() # u test points evenly distributed in the interval [-7.5, 7.5]



#_________________________________
# STANDARD GP:


# ***UNCOMMENT THE FOLLOWING LINES TO DO TRAINING OF HYPERPARAMETERS***
### TRAINING GP
#print 'GP: ...training'
### INITIALIZE (hyper)parameters by -1
#d = X.shape[1]
#init = -1*ones((d,1))
#loghyper = array([[-1], [-1]])
#loghyper = vstack((init, loghyper))[:,0]
#print 'initial hyperparameters: ', exp(loghyper)
### TRAINING of (hyper)parameters
#logtheta = gpr.gp_train(loghyper, covfunc, X, y)
#print 'trained hyperparameters: ',exp(logtheta)


## to GET prior covariance of Standard GP use:
#[Kss, Kstar] = general.feval(covfunc, logtheta, X, Xstar)    # Kss = self covariances of test cases, 
#                                                             # Kstar = cov between train and test cases


## PREDICTION 
print 'GP: ...prediction'
results = gpr.gp_pred(logtheta, covfunc, X, y, Xstar) # get predictions for unlabeled data ONLY
MU = results[0]
S2 = results[1]

#print MU


## plot results
pyplot.suptitle('logtheta:', fontsize=12)
pyplot.title(logtheta)

pyplot.plot(Xstar,MU, 'g^', X,y, 'ro')
pyplot.show()
