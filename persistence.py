# -*- coding: UTF-8 -*-
import numpy as np
import dionysus as d

class VietorisRipsComplex:

    def __init__(self, points, k_skeleton = 2):
        '''
        Initializes points to be used in construction of Vietoris-Rips complexes
        :param points: numpy.array of Nx2 representing N points in euclidean plane
        :param k_skeleton: maximum k-skeleton for clique complex
        '''
        self.points = points
        self.k_skeleton = k_skeleton
    
    def compute_persistence(self, max_epsilon):
        '''
        Computes persistence of self.points up to max_epsilon and returns
        persistence diagrams
        :param max_epsilon: max epsilon for persistence
        :return: class Diagram
        '''
        # fill rips complex up to distance max_epsilon using self.points
        filtration = d.fill_rips(self.points, self.k_skeleton, max_epsilon)

        # before computing persistence we sort the filtration
        filtration.sort()

        # compute persistence and return ReducedMatrix
        matrix = d.homology_persistence(filtration, prime = 2)

        # initialize diagrams with ReducedMatrix and filtration
        diagrams = d.init_diagrams(matrix, filtration)

        return diagrams

            

