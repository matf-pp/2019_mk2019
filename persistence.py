# -*- coding: UTF-8 -*-
import numpy as np
from math import sqrt
import dionysus as d


def list_of_pairs_to_numpyarray(list):
    '''
    :param list:
    :return:
    '''
    return np.array([[x,y] for (x,y) in list])

class VietorisRipsComplex:
    '''

    '''
    def __init__(self, points, degree = 2):
        '''

        :param points:
        :param degree:
        '''
        self.points = points
        self.degree = degree
    
    def compute_persistence(self, max_epsilon):
        '''

        :param max_epsilon:
        :return:
        '''
        filtration = d.fill_rips(self.points, self.degree, max_epsilon)
        filtration.sort()
        matrix = d.homology_persistence(filtration, prime = 2)
        diagrams = d.init_diagrams(matrix, filtration)
        return diagrams
    
    def betti_number(self, i):
        '''

        :param i:
        :return:
        '''
        pass
            

