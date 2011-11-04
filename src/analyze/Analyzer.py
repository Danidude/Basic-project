
from GPR import gpr
import numpy as np
import random


class Predict:
    
    def __init__(self, xr, yr):

        helper = Helper()
        
        self.x_star = helper.init_x_star(xr, yr)
        self.init_kernel()
        
        
    def init_kernel(self):
        
#        self.logtheta = logtheta = np.array([np.log(0.2), np.log(2.0), np.log(1.0), np.log(8.0), np.log(0.0001)])
        self.logtheta = logtheta = np.array([np.log(4.5), np.log(0.01), np.log(1.0), np.log(1.0), np.log(0.000001)])
        self.covfunc = ['kernels.covSum', ['kernels.covSEiso', 'kernels.covSEiso', 'kernels.covNoise']]
        
        
    def predict(self, X, y):
        
        prediction = gpr.gp_pred(self.logtheta, self.covfunc, X, y, self.x_star)
        return prediction

class Helper:
    
    def __init__(self):
        print ""
    
    def init_x_star(self, xr, yr):
        x_star = np.array([]).transpose()
        for x in range(xr):
            for y in range(yr):
                if len(x_star) == 0:
                    x_star = [(x,y)]
                else:
                    x_star = np.concatenate((x_star,[(x,y)]))
        return x_star
    
class Plotter:
    
    def __init__(self):
        print ""

class GPR_d:
    
    def __init__(self):
        xr = 10
        yr = 10
        helper = Helper()
        
        X = helper.init_x_star(xr, yr)[::10]
        y = np.array([]).transpose()
        for y1 in range(len(X)):
            rand = random.random()
            if len(y) == 0:
                y = [(rand)]
            else:
                y = np.concatenate((y,[(rand)]))
        
        predict = Predict(xr,yr)
        prediction = predict.predict(X,y)
        MU = prediction[0]
        S2 = prediction[1]
        
        
        for i in range(len(X)):
            print "x,y {0}, z {1}".format(X[i], y[i])
        print "###################"
            
        for i in range(len(predict.x_star)):
            print "x,y {0}, MU {1}, S2 {2}".format(predict.x_star[i], MU[i], S2[i])

if __name__ == '__main__':
    GPR_d()

    