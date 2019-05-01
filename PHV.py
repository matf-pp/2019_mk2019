import sys
import random
from PyQt5 import QtGui
import numpy
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from persistence import *
import qdarkstyle
numOfDots = 0
epsilon = 0
skupTacaka = {"tacke": [], "duzi": [], "trouglovi": []}
dgms = []


class PlotCanvas(FigureCanvas):
    def setData(self, arg):
        self.data = arg

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor('cornflowerblue')
        self.ax = self.fig.add_subplot(211)
        self.ay = self.fig.add_subplot(212)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self):
        global epsilon
        global dgms

        self.ax.set_facecolor('lightgray')
        self.ax.clear()
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])

        nizTrouglovaZaPresek = []
        for((x1, y1), (x2, y2), (x3, y3)) in self.data["trouglovi"]:
            if ((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1) <= epsilon*epsilon and
                (x3-x1)*(x3-x1)+(y3-y1)*(y3-y1) <= epsilon*epsilon and
                    (x2-x3)*(x2-x3)+(y2-y3)*(y2-y3) <= epsilon*epsilon):

                trougao = Polygon([(x1, y1), (x2, y2), (x3, y3)])
                nizTrouglovaZaPresek.append(trougao)

        multiPoligon = cascaded_union(nizTrouglovaZaPresek)
        if isinstance(multiPoligon, Polygon):
            x, y = multiPoligon.exterior.coords.xy
            self.ax.fill(x, y, alpha=0.5)
        else:
            for i in multiPoligon:
                x, y = i.exterior.coords.xy
                self.ax.fill(x, y, alpha=0.5)

        for ((x1, y1), (x2, y2)) in self.data["duzi"]:
            if((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1) <= epsilon*epsilon):
                self.ax.plot([x1, x2], [y1, y2], "black")

        for (x, y) in self.data["tacke"]:
            self.ax.plot([x], [y], 'bo')  # crta tačke
        self.linija_epsilon.remove()
        linije = self.ay.plot([epsilon, epsilon], [0, self.num], "black")
        self.linija_epsilon = linije.pop()

        self.draw()

    def barCode(self):
        global epsilon
        global dgms
        self.ay.clear()
        self.ay.set_facecolor('lightgray')
        self.num = 0
        h = 0
        self.ay.set_xlim([0,1.42])
        self.ay.axes.set_yticks([])
        self.ay.set_yticklabels(["H0          ", "H1     ", "H2"])
        yticks = []
        for niz in ([[(i, p) for p in dgm] for i, dgm in enumerate(dgms)]):

            self.ay.plot([0, 1.42], [self.num, self.num], "black")
            yticks.append(self.num)
            self.ay.axes.set_yticks(yticks)
            for(a, b) in niz:
                self.ay.fill([b.birth, b.birth, min(b.death, 1.42), min(b.death, 1.42)], [
                             self.num, self.num+1, self.num+1, self.num], alpha=0.9)
                # self.ay.plot([b.birth,min(b.death,1.42)],[self.num,self.num],"blue")
                self.num = self.num + 1
        linije = self.ay.plot([epsilon, epsilon], [0, self.num], "black")
        self.linija_epsilon = linije.pop()

        self.draw()


class Window(QWidget):

    def generisiSkupTacaka(self, newNumOfDots):
        global numOfDots
        global skupTacaka
        global epsilon
        global dgms
        if(newNumOfDots > numOfDots):
            for i in range(newNumOfDots-numOfDots):
                skupTacaka["tacke"].append((random.random(), random.random()))
        if(newNumOfDots < numOfDots):
            for i in range(numOfDots - newNumOfDots):
                skupTacaka["tacke"].pop()
        numOfDots = newNumOfDots
        skupTacaka["duzi"] = []
        for i in range(numOfDots):
            for j in range(numOfDots):
                if i != j:
                    skupTacaka["duzi"].append(
                        (skupTacaka["tacke"][i], skupTacaka["tacke"][j]))
        skupTacaka["trouglovi"] = []
        for i in range(numOfDots):
            for j in range(numOfDots):
                for k in range(numOfDots):
                    if i != j and j != k and k != i:
                        skupTacaka["trouglovi"].append(
                            (skupTacaka["tacke"][i], skupTacaka["tacke"][j], skupTacaka["tacke"][k]))

        vrc = VietorisRipsComplex(
            list_of_pairs_to_numpyarray(skupTacaka["tacke"]))

        dgms = vrc.compute_persistence(1.42)

        self.canvas.setData(skupTacaka)
        self.canvas.barCode()
        self.canvas.plot()

    def promeniEpsilon(self, num):
        global epsilon
        epsilon = num/1000.0
        self.textBoxEpsilon.setText(str(epsilon))
        self.canvas.plot()

    def promeniNumOfDots(self, num):
        self.textBoxNumOfDots.setText(str(num))
        self.generisiSkupTacaka(num)

    def promeniTextBoxEpsilon(self, string):
        try:
            a = float(string)
            if(a >= 0 and a <= 1.42):
                self.sliderEpsilon.setValue((a*1000))
        except:
            return

    def promeniTextBoxNumOfDots(self, string):
        try:
            a = float(string)
            if(a >= 0 and a <= 30):
                self.sliderNumDots.setValue((a))
        except:
            return

    def changeTheme(self):
        global app
        if self.CheckBox.isChecked():
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        else:
            app.setStyleSheet('')

    def __init__(self, parent=None):

        super(Window, self).__init__(parent)
        grid = QGridLayout()
        labelaNumDots = QLabel("Broj tačaka:")
        labelaEpsilon = QLabel("Epsilon:")

        self.sliderNumDots = QSlider(Qt.Horizontal)
        self.sliderEpsilon = QSlider(Qt.Horizontal)

        self.sliderNumDots.setMaximum(30)
        self.sliderNumDots.setMinimum(0)

        self.sliderEpsilon.setMaximum(1420)
        self.sliderEpsilon.setMinimum(0)

        self.sliderNumDots.setSingleStep(1)
        self.sliderEpsilon.setSingleStep(1)

        self.textBoxNumOfDots = QLineEdit("0")
        self.textBoxEpsilon = QLineEdit("0")

        self.textBoxEpsilon.setMaximumWidth(50)
        self.textBoxNumOfDots.setMaximumWidth(50)

        self.textBoxNumOfDots.setMaxLength(3)
        self.textBoxEpsilon.setMaxLength(4)

        self.CheckBox = QCheckBox("Pređi na \ntamnu stranu")

        self.canvas = PlotCanvas(self, width=1, height=1)
        self.canvas.setData(skupTacaka)
        self.canvas.barCode()
        self.canvas.plot()

        # Eventovi:
        self.sliderNumDots.valueChanged.connect(self.promeniNumOfDots)
        self.sliderEpsilon.valueChanged.connect(self.promeniEpsilon)

        self.textBoxEpsilon.textEdited.connect(self.promeniTextBoxEpsilon)
        self.textBoxNumOfDots.textEdited.connect(self.promeniTextBoxNumOfDots)

        self.CheckBox.stateChanged.connect(self.changeTheme)
        self.Labela = QLabel("Kristina Popović & Marko Spasić, 2019")
        grid.setContentsMargins(8, 8, 8, 8)

        grid.addWidget(labelaNumDots, 0, 0)
        grid.addWidget(self.sliderNumDots, 0, 1)
        grid.addWidget(self.textBoxNumOfDots, 0, 2)
        grid.addWidget(labelaEpsilon, 1, 0)
        grid.addWidget(self.sliderEpsilon, 1, 1)
        grid.addWidget(self.textBoxEpsilon, 1, 2)
        grid.addWidget(self.canvas, 3, 0, 1, 3)
        grid.addWidget(self.CheckBox, 4, 2)
        grid.addWidget(self.Labela,4,0)

        #grid.addWidget(self.createSlider("Random faktor"), 2, 0)
        self.setLayout(grid)
        self.setWindowTitle("Perzistentna homologija")
        self.resize(800, 800)


def main():
    global app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    clock = Window()
    clock.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
