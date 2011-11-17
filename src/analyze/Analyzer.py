
from GPR import gpr
import numpy as np
import random


class Predict:
    
    def __init__(self, xr, yr):

        helper = Helper()
        
#        self.x_star = helper.init_x_star(xr, yr)
        #self.x_star = helper.init_x_star_removes_existing_points(xr, yr)
        self.init_kernel()
        
        
    def init_kernel(self):
        #two first are coSEiso and last is to covNoise
#        self.logtheta = logtheta = np.array([np.log(0.205), np.log(2.0), np.log(1.0), np.log(8.0), np.log(0.0001)])
#        self.logtheta = logtheta = np.array([np.log(4.5), np.log(0.01), np.log(1.0), np.log(1.0), np.log(0.000001)])
#        self.covfunc = ['kernels.covSum', ['kernels.covSEiso', 'kernels.covSEiso', 'kernels.covNoise']]

        self.logtheta = logtheta = np.array([ np.log(1.0), np.log(8.0),np.log(1.0), np.log(8.0), np.log(0.0001)])
        self.covfunc = ['kernels.covSum', ['kernels.covSEiso', 'kernels.covSEiso', 'kernels.covNoise']]
        
    def predict(self, X, y):
        
        prediction = gpr.gp_pred(self.logtheta, self.covfunc, X, y, self.x_star)
        return prediction
    
    def predict_2(self, X, y, x_star):
        
        prediction = gpr.gp_pred(self.logtheta, self.covfunc, X, y, x_star)
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
    
    def init_x_star_removes_existing_points(self, xr, yr, cells):
        x_star = np.array([]).transpose()

        
        
        for x, x1 in range(xr):
            for y in range(yr):
                if len(x_star) == 0:
                    x_star = [(x,y)]
                else:
                    x_star = np.concatenate((x_star,[(x,y)]))
        return x_star
        
    
class Plotter:
    
    def __init__(self):
        print ""
        

class GPR_Controller:
    

    def update_grid(self, grid, old_fire, prediction, all_y):
        #creating large string and changing the grid
#        large_string = ""
#        if old_fire == None:
#            old_fire = grid.cells
#        for new_row, old_row in zip(grid.cells, old_fire):
#            for new_cell, old_cell in zip(new_row, old_row):
#                print "x:{0} y:{1} v:{2}".format(new_cell.x, new_cell.y, new_cell.v)
#                if new_cell.v > 8:
#                    if prediction[0] > 0.007:
#                        new_cell.v = 126
#                        large_string += chr(126)
#                    elif old_cell.v > 0:
#                        new_cell.v = old_cell.v
#                        large_string += chr(126)
#                    else:
#                        new_cell.v = 0
#                        large_string += chr(0)
#                    prediction = prediction[1:]
#                elif old_cell.v > 0:
#                    new_cell.v = old_cell.v
#                    large_string += chr(126)
#                else:
#                    new_cell.v = 0
#                    large_string += chr(0)
#                all_y.append(new_cell.v)
        large_string = ""
        for row in grid.cells:
            for cell in row:
                print "x:{0} y:{1} v:{2}".format(cell.x,cell.y,cell.v)
                if cell.v > 8:
                    if prediction[0] > 0.007:
                        cell.v = 126
                        large_string += chr(126)
                    else:
                        cell.v = 0
                        large_string += chr(0)
                    prediction = prediction[1:]
                else:
                    large_string += chr(0)
                all_y.append(cell.v)
        return large_string

    def __init__(self, grid, old_fire):
        #TODO remove already measured points
        
        print ""
        self.grid = grid
        xr = grid.sizeX
        yr = grid.sizeY
        helper = Helper()
        
        
        
        
        y = np.array([]).transpose()
        X = np.array([]).transpose()
        x_star = np.array([]).transpose()
        
        for new_row in grid.cells:
            for new_cell in new_row:
                if new_cell.v < 9:        

                    if len(X) == 0:
                        X = [(new_cell.x,new_cell.y)]
                        y = [(new_cell.v)]
                    else:
                        X = np.concatenate((X,[(new_cell.x,new_cell.y)]))
                        y = np.concatenate((y,[(new_cell.v)]))

                else:
                    print new_cell.v
                    if len(x_star) == 0:
                        x_star = [(new_cell.x,new_cell.y)]
                    else:
                        x_star = np.concatenate((x_star,[(new_cell.x,new_cell.y)]))
        
        
        predict = Predict(xr, yr)
        
        self.predict = predict.predict_2(X, y, x_star)
        
        prediction = []
        for p in self.predict[0]:
            prediction.append(p)
            print p
        
        all_y = []
        
        
        large_string = self.update_grid(grid, old_fire, prediction, all_y)
                
        
        #mash together old and new
        
        self.old_fire = grid.cells
        
        
        self.grid = grid
        self.large_string = large_string
        
        t22 = np.sort(all_y)
        fd = 0
        for t1 in t22:
            if t1 > 0.007:
                print "sorted y : {0}".format(t1)
                fd +=1
        print fd
                
        
        
    

class GPR_d:
    
    def __init__(self):
        print ""
        
        

    def test_gpr(self):
        xr = 10
        yr = 10
        helper = Helper()
        X = helper.init_x_star(xr, yr)[:10]
        y = np.array([]).transpose()
        for y1 in range(len(X)):
            
            rand = random.random()
            if len(y) == 0:
                y = [(rand)]
            else:
                y = np.concatenate((y, [(rand)]))
        
        predict = Predict(xr, yr)
        prediction = predict.predict(X, y)
        MU = prediction[0]
        S2 = prediction[1]
        for i in range(len(X)):
            print "x,y {0}, z {1}".format(X[i], y[i])
        
        print "###################"
        for i in range(len(predict.x_star)):
            print "x,y {0}, MU {1}, S2 {2}".format(predict.x_star[i], MU[i], S2[i])


if __name__ == '__main__':
    gp = GPR_d()
    gp.test_gpr()

    