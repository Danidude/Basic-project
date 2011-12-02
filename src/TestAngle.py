'''
Created on Dec 2, 2011

@author: enok
'''
import unittest
from GPR import kernels


class Test(unittest.TestCase):


    def test_calculate_weight_with_same_as_wind(self):
        vector = [-1,0]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight == 0.0,weight)

    def test_calculate_weight_with_total_opposite_of_wind(self):
        vector = [1,0]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight > 1.0,weight)
        
    def test_calculate_weight_with_upward_vector(self):
        vector = [0,1]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight == 1, weight)
        
    def test_calculate_weight_with_downward_vector(self):
        vector = [0,-1]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight == 1, weight)
        
    def test_calculate_weight_with_45_oppsite_1(self):
        vector = [1,1]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight == 1.5, weight)
        
    def test_calculate_weight_with_45_oppsite_2(self):
        vector = [1,-1]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight == 1.5, weight)
        
    def test_calculate_weight_with_45_same_1(self):
        vector = [-1,1]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight > 0.24, weight)
    
    def test_calculate_weight_with_45_same_2(self):
        vector = [-1,-1]
        wind_vector = [-1,0]
        
        weight = kernels.calculate_weight(vector, wind_vector)
        print weight
        self.assertTrue(weight > 0.24, weight)
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()