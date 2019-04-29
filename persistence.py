import numpy as np
import dionysus as d

# points = np.random.random((20,2))
# f = d.fill_rips(points, 2, 2)
# m = d.homology_persistence(f)
# dgms = d.init_diagrams(m, f)
# print(type(m))
# print(type(dgms))
# for i, dgm in enumerate(dgms):
#     for pt in dgm:
#         print(i, pt.birth, pt.death)
#
# print([o for o in enumerate(dgms[0])])
# d.plot.plot_bars(dgms[0], show = True)

class PersistenceHomology:
    def __init__(self, points):
        self.points = points

    def compute(self, eps):
        filtration = d.fill_rips(self.points, 2, eps)
        reduced_matrix = d.homology_persistence(filtration)
        diagrams = d.init_diagrams(reduced_matrix, filtration)

        result = PersistenceHomologyResult()
        result.b0 = sum(1 for i,_ in diagrams if i == 0)
        result.b1 = sum(1 for i,_ in diagrams if i == 1)
        result.b2 = sum(1 for i,_, in diagrams if i == 2)
        result.H = diagrams

        return result

class PersistenceHomologyResult:
    def __init__(self):
        self.b0 = 0
        self.b1 = 0
        self.b2 = 0
        self.H = None

