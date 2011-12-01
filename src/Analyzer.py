
from GPR import gpr
import numpy as np
import copy

class Predict:
    
    def __init__(self, xr, yr):

        self.init_kernel()
        
        
    def init_kernel(self):

#        self.logtheta = np.array([ np.log(1.0), np.log(8.0),np.log(1.0), np.log(8.0), np.log(0.0001)])
#        self.covfunc = ['kernels.covSum', ['kernels.covSEiso', 'kernels.covSEiso', 'kernels.covNoise']]
        self.logtheta = np.array([ np.log(3.0), np.log(8.0)])
        self.covfunc = ['kernels.covSum', ['kernels.covSEiso']]
        
    def predict(self, X, y):
        
        prediction = gpr.gp_pred(self.logtheta, self.covfunc, X, y, self.x_star)
        return prediction
    
    def predict_2(self, X, y, x_star):
        
        prediction = gpr.gp_pred(self.logtheta, self.covfunc, X, y, x_star)
        return prediction
    

class GPR_Controller:



    def convert_to_numpy_array(self, fire_time_grid, X, y, x_star, fire_cells):
        
        fire_sensors = []
        
        for time_frame in fire_time_grid:
            for new_row in time_frame:
                for new_cell in new_row:
                    if new_cell.v < 40:#values are 0 - 8
                        if new_cell.v > 0: #sensors which detect fire
                            fire_sensors.append(new_cell)
                        if len(X) == 0:
                            X = [(new_cell.x, new_cell.y, new_cell.t)]
                            if new_cell.v == 0:
                                y = [(-1)]
                            else:
                                y = [(new_cell.v)]
                        else:
                            X = np.concatenate((X, [(new_cell.x, new_cell.y, new_cell.t)]))
                            if new_cell.v == 0:
                                y = np.concatenate((y, [(-1)]))
                            else:
                                y = np.concatenate((y, [(new_cell.v)]))
        
        for new_row in fire_time_grid[len(fire_time_grid) -1]:
            for new_cell in new_row:
                
                if new_cell.v < 40:#only 127
                    continue
                
                is_close_to_fire_sensors = self.square_is_close_to(new_cell, fire_sensors, 2)
                is_close_to_calculated_fire = self.square_is_close_to(new_cell, fire_cells, 3)
                
                if (not is_close_to_fire_sensors) and (not is_close_to_calculated_fire):
                    continue

                if len(x_star) == 0:
                    x_star = [(new_cell.x, new_cell.y, new_cell.t)]
                else:
                    x_star = np.concatenate((x_star, [(new_cell.x, new_cell.y, new_cell.t)]))
        
        return X, y, x_star
    
    def square_is_close_to(self, square, fire_cells, max_distance):
        shortest_distance = 100000.0
        
        if fire_cells == None:
            return True
        
        for fire_cell in fire_cells:
            distance = np.sqrt( ((square.x - fire_cell.x)**2) + ((square.y - fire_cell.y)**2) )
            if distance < shortest_distance:
                shortest_distance = distance
                if shortest_distance < max_distance:
                    return True
        if shortest_distance < max_distance:
                    return True
        return False
    
    

    def __init__(self, grid, time_fire, fire_cells):

        xr = grid.sizeX
        yr = grid.sizeY
        predict = Predict(xr, yr)
        
        y = np.array([]).transpose()
        X = np.array([]).transpose()
        x_star = np.array([]).transpose()
        
        self.add_fire_to_time_list(time_fire, grid.cells)
        
        X, y, x_star = self.convert_to_numpy_array(time_fire, y, X, x_star, fire_cells)
        
        
        self.predict = predict.predict_2(X, y, x_star)
        
        self.add_prediction_to_grid_cells(self.predict, x_star, grid.cells)

        self.fire_cells = self.convert_to_discrete_values(grid.cells)
        self.large_prediction_string, self.large_s2_string = self.create_large_string(grid.cells)
        
        self.large_string = self.large_prediction_string
    
    def add_fire_to_time_list(self, time_fire, cells):
        timestamp = len(time_fire)
        
        for row in cells:
            for cell in row:
                cell.t = timestamp
        copied_fire = copy.deepcopy(cells)
        time_fire.append(copied_fire)
    
    def create_large_string(self, fire):
        large_prediction_string = ""
        large_s2_string = ""
        for row in fire:
            for cell in row:
                large_prediction_string += chr(cell.v)
                large_s2_string += chr(cell.v)
        return (large_prediction_string, large_s2_string)
    
    def convert_to_discrete_values(self,fire):
        fire_cells = []
        for row in fire:
            for cell in row:
                if cell.v > 0.04:
                    cell.v = 126
                    fire_cells.append(cell)
                else:
                    cell.v = 0
        return fire_cells
    
        
    def add_prediction_to_grid_cells(self, predictions, x_star, cells):
        prediction = predictions[0]
        S2 = predictions[1]
        
        for row in cells:
            for cell in row:
                if len(x_star) == 0:
                    cell.v = 0
                    cell.S2 = 0
                if cell.v == 127 and cell.x == x_star[0][0] and cell.y == x_star[0][1] and cell.t == x_star[0][2]:
                    cell.v = prediction[0]
                    cell.S2 = S2[0][0]
                    prediction = prediction[1:]
                    S2 = S2[1:]
                    x_star = x_star[1:]
                elif cell.v > 0.9999999 and cell.v < 25:
                    cell.S2 = 0
                else:
                    cell.v = 0
                    cell.S2 = 0
        return

    