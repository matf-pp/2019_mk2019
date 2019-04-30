# -*- coding: UTF-8 -*-
import numpy as np
from math import sqrt
import dionysus as d


def list_of_pairs_to_numpyarray(list):
    return np.array([[x,y] for (x,y) in list])


class VietorisRipsComplex:
    def __init__(self, points, degree = 2):
        self.points = points
        self.degree = degree
    
    def compute_persistence(self, max_epsilon):
        f = d.fill_rips(self.points, 2, max_epsilon)
        f.sort()
        m = d.homology_persistence(f, prime = 2)
        dgms = d.init_diagrams(m, f)
        # print([s for s in f])
        # print([[(i,p) for p in dgm] for i, dgm in enumerate(dgms)])
        # d.plot.plot_bars(dgms[0], show = True)
        return dgms
            

