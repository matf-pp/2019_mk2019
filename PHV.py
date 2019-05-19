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


class DrawingData:
    def __init__(self, dots = [], lines = [], triangles = [], dgms = []):
        self.dots = dots
        self.lines = lines
        self.triangles = triangles
        self.diagrams = dgms
        self.epsilon = 0
        self.max_distance = 1.42

    def recalculateDrawingData(self, newNumOfDots):
        self.__changeNumberOfDots(newNumOfDots)

        self.lines.clear()
        self.lines = calculateLines(self.dots)

        self.triangles.clear()
        self.triangles = calculateTriangles(self.dots)


    def __changeNumberOfDots(self, newNumOfDots):
        if (newNumOfDots > len(self.dots)):
            self.dots.extend(generateNRandomDots(newNumOfDots - len(self.dots)))

        if (newNumOfDots < len(self.dots)):
            for i in range(len(self.dots) - newNumOfDots):
                self.dots.pop()

drawingData = DrawingData()


class PlotCanvas(FigureCanvas):
    def setData(self, arg):
        self.data = arg

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.fig.set_facecolor('cornflowerblue')
        self.ax = self.fig.add_subplot(121)
        self.ay = self.fig.add_subplot(122)
        FigureCanvas.__init__(self, self.fig)
        self.setParent(parent)
        FigureCanvas.setSizePolicy(
            self, QSizePolicy.Expanding, QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self):

        self.ax.set_facecolor('lightgray')
        self.ax.clear()
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])

        nizTrouglovaZaPresek = []
        for((x1, y1), (x2, y2), (x3, y3)) in self.data.triangles:
            if ((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1) <= drawingData.epsilon*drawingData.epsilon and
                (x3-x1)*(x3-x1)+(y3-y1)*(y3-y1) <= drawingData.epsilon*drawingData.epsilon and
                    (x2-x3)*(x2-x3)+(y2-y3)*(y2-y3) <= drawingData.epsilon*drawingData.epsilon):

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

        for ((x1, y1), (x2, y2)) in self.data.lines:
            if((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1) <= drawingData.epsilon*drawingData.epsilon):
                self.ax.plot([x1, x2], [y1, y2], "black")

        for (x, y) in self.data.dots:
            self.ax.plot([x], [y], 'bo')  # crta tačke
        self.linija_epsilon.remove()
        linije = self.ay.plot([drawingData.epsilon, drawingData.epsilon], [0, self.num], "black")
        self.linija_epsilon = linije.pop()

        self.draw()

    def barCode(self):
        self.ay.clear()
        self.ay.set_facecolor('lightgray')
        self.num = 0
        h = 0
        self.ay.set_xlim([0,1.42])
        self.ay.axes.set_yticks([])
        self.ay.set_yticklabels(["H0          ", "H1     ", "H2"])
        yticks = []
        for niz in ([[(i, p) for p in dgm] for i, dgm in enumerate(drawingData.diagrams)]):

            self.ay.plot([0, 1.42], [self.num, self.num], "black")
            yticks.append(self.num)
            self.ay.axes.set_yticks(yticks)
            for(a, b) in niz:
                if a != 2:
                    self.ay.fill([b.birth, b.birth, min(b.death, 1.42), min(b.death, 1.42)], [
                                self.num, self.num+1, self.num+1, self.num], alpha=0.9)
                    # self.ay.plot([b.birth,min(b.death,1.42)],[self.num,self.num],"blue")
                    self.num = self.num + 1
        linije = self.ay.plot([drawingData.epsilon, drawingData.epsilon], [0, self.num], "black")
        self.linija_epsilon = linije.pop()

        self.draw()


def generateNRandomDots(n):
    return [(random.random(), random.random()) for _ in range(n)]

def calculateLines(dots):
    lines = []
    for i in range(len(dots)):
        for j in range(len(dots)):
            if i != j:
                lines.append(
                    (dots[i], dots[j]))
    return lines

def calculateTriangles(dots):
    triangles = []
    for i in range(len(dots)):
        for j in range(len(dots)):
            for k in range(len(dots)):
                if i != j and j != k and k != i:
                    triangles.append(
                        (dots[i], dots[j], dots[k]))
    return triangles


class Window(QWidget):
    def onEpsilonChanged(self, num):
        drawingData.epsilon = num/1000.0
        self.textBoxEpsilon.setText(str(drawingData.epsilon))
        self.canvas.plot()

    def onNumberOfDotsChanged(self, num):
        self.textBoxNumOfDots.setText(str(num))

        drawingData.recalculateDrawingData(num)

        vrc = VietorisRipsComplex(
            list_of_pairs_to_numpyarray(drawingData.dots))

        drawingData.diagrams = vrc.compute_persistence(drawingData.max_distance)

        self.canvas.setData(drawingData)

        self.canvas.barCode()

        self.canvas.plot()


    def onTextBoxEpsilonChanged(self, string):
        try:
            a = float(string)
            if(a >= 0 and a <= 1.42):
                self.sliderEpsilon.setValue((a*1000))
        except:
            return

    def onTextBoxNumOfDotsChanged(self, string):
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
        self.canvas.setData(drawingData)
        self.canvas.barCode()
        self.canvas.plot()

        # Eventovi:
        self.sliderNumDots.valueChanged.connect(self.onNumberOfDotsChanged)
        self.sliderEpsilon.valueChanged.connect(self.onEpsilonChanged)

        self.textBoxEpsilon.textEdited.connect(self.onTextBoxEpsilonChanged)
        self.textBoxNumOfDots.textEdited.connect(self.onTextBoxNumOfDotsChanged)

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
