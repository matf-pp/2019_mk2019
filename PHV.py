import sys
import random
from PyQt5 import QtGui


from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class PlotCanvas(FigureCanvas):
    def dodajData(self, arg):
        self.data = arg

    def __init__(self, parent=None, width=1, height=1, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = plt.gca()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        # FigureCanvas.setSizePolicy(self,
        #                            QSizePolicy.Expanding,
        #                            QSizePolicy.Expanding)
        # FigureCanvas.updateGeometry(self)

    def plot(self):
        # Ovaj broj ima značenje 1X1 grid, prvi subplot, 234 bi značio 2X3, četvrti subplot
        ax = self.figure.add_subplot(111)
        ax.clear()
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])
        
        for((x1, y1), (x2, y2), (x3, y3)) in self.data["trouglovi"]:
            ax.fill([x1, x2, x3], [y1, y2, y3],alpha = 0.5)

        for ((x1, y1), (x2, y2)) in self.data["duzi"]:
            ax.plot([x1, x2], [y1, y2])

        for (x, y) in self.data["tacke"]:
            ax.plot([x], [y], 'bo')  # crta tačke

        ax.set_title('Treba li nam naslov?')
        self.draw()


class Window(QWidget):
    def on_slide_epsilon(self):
        print(self.sliderEpsilon.value())

    def generisiSkupTacaka(self):
        numOfDots = self.sliderNumDots.value()
        tacke = []
        duzi = []
        trouglovi = []

        for i in range(numOfDots):
            tacke.append((random.random(),random.random()))
        self.skupTacaka["tacke"]=tacke
        duzi = []
        for i in range(numOfDots):
            for j in range(numOfDots):
                if(i!=j):
                    duzi.append((tacke[i],tacke[j]))
        self.skupTacaka["duzi"]= duzi
        for i in range(numOfDots):
            for j in range(numOfDots):
                for k in range(numOfDots):
                    if(i!=j and j!=k and k!=i):
                        trouglovi.append((tacke[i],tacke[j],tacke[k]))
        self.skupTacaka["trouglovi"] = trouglovi



        self.canvas.dodajData(self.skupTacaka)
        self.canvas.plot()
    def promeniEpsilon(self,num):
        self.epsilon = num
        print(epsilon)

    def __init__(self, parent=None):

        self.epsilon = 0
        self.skupTacaka ={"tacke":[],"duzi":[],"trouglovi":[]}

        super(Window, self).__init__(parent)
        grid = QGridLayout()
        labelaNumDots = QLabel("Broj tačaka:")
        labelaEpsilon = QLabel("Epsilon:")

        self.sliderNumDots = QSlider(Qt.Horizontal)
        self.sliderEpsilon = QSlider(Qt.Horizontal)

        self.sliderNumDots.setMaximum(10)
        self.sliderNumDots.setMinimum(0)

        self.sliderEpsilon.setMaximum(1000)
        self.sliderEpsilon.setMinimum(0)
        # TODO DOTERAJ OVAJ DEO KODA
        self.sliderNumDots.setSingleStep(1)
        self.sliderEpsilon.setSingleStep(1)

        self.textBoxNumOfDots = QLineEdit("0")
        self.textBoxEpsilon = QLineEdit("0")

        self.textBoxEpsilon.setMaximumWidth(50)
        self.textBoxNumOfDots.setMaximumWidth(50)

        self.textBoxNumOfDots.setMaxLength(3)
        self.textBoxEpsilon.setMaxLength(4)

        self.canvas = PlotCanvas(self, width=1, height=1)
        # tacka (x,y), duz ((x1,y1),(x2,y2))...
        self.canvas.dodajData({"tacke": [(0, 0.2), (0.3, 0.4)],
                                "duzi": [((0, 0), (0.1, 0.1))],
                                "trouglovi": [
            ((0, 0.3), (0.4, 0), (0, 0))]})
        self.canvas.plot()

        #Eventovi:
        self.sliderNumDots.valueChanged.connect(self.generisiSkupTacaka)
        self.sliderEpsilon.valueChanged.connect(self.promeniEpsilon)

        grid.setContentsMargins(8, 8, 8, 8)

        grid.addWidget(labelaNumDots, 0, 0)
        grid.addWidget(self.sliderNumDots, 0, 1)
        grid.addWidget(self.textBoxNumOfDots, 0, 2)
        grid.addWidget(labelaEpsilon, 1, 0)
        grid.addWidget(self.sliderEpsilon, 1, 1)
        grid.addWidget(self.textBoxEpsilon, 1, 2)
        grid.addWidget(self.canvas, 3, 0, 1, 3)
        #grid.addWidget(self.createSlider("Epsilon okolina"), 1, 0)
        grid.addWidget(
            QCheckBox("Izračunaj perzistentnu homologiju"), 2, 0, 1, 3)

        #grid.addWidget(self.createSlider("Random faktor"), 2, 0)
        self.setLayout(grid)
        self.setWindowTitle("Perzistentna homologija")
        self.resize(500, 800)


def main():
    app = QApplication(sys.argv)
    clock = Window()
    clock.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
