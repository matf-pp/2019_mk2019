import sys
import random
from shapely.geometry import Polygon
from shapely.ops import cascaded_union
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from persistence import *
import qdarkstyle
import numpy as np
import os
class DrawingData:

    def __init__(self):
        self.dots = []
        self.lines = []
        self.triangles = []

        # diagrams that persistent homology will compute
        self.diagrams = []

        # current value of epsilon
        self.epsilon = 0

        # max distance for points in the 1x1 plane
        self.max_distance = 1.42

        self.drawH2 = False

    def recalculateDrawingData(self):
        '''
        Recalculates drawing data when the number of dots change.
        When the newNumOfDots is greater than current number of dots than the number of new random dots
        equal to the difference between newNumberOfDots and len(self.dots) is added and lines and triangles are
        recalculated.
        When the newNumberOfDots is less then the current number of dots than the extra dots are removed and
        the lines and triangles are recalculated.
        :param newNumOfDots:
        :return: None
        '''
        self.lines.clear()
        self.lines = calculateLines(self.dots)

        self.triangles.clear()
        self.triangles = calculateTriangles(self.dots)


    def changeNumberOfDots(self, newNumOfDots):
        '''
        Helper method for recalculateDrawingData
        :param newNumOfDots:
        :return:
        '''
        if (newNumOfDots > len(self.dots)):
            self.dots.extend(generateNRandomDots(newNumOfDots - len(self.dots)))

        if (newNumOfDots < len(self.dots)):
            for i in range(len(self.dots) - newNumOfDots):
                self.dots.pop()


drawingData = DrawingData()


def constructTriangleArray(triangles):
    '''
    Constructs polygons to be drawn by matplot
    :param triangles:
    :return:
    '''
    trianglesIntersection = []
    for ((x1, y1), (x2, y2), (x3, y3)) in triangles:
        if ((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1) <= drawingData.epsilon * drawingData.epsilon and
                (x3 - x1) * (x3 - x1) + (y3 - y1) * (y3 - y1) <= drawingData.epsilon * drawingData.epsilon and
                (x2 - x3) * (x2 - x3) + (y2 - y3) * (y2 - y3) <= drawingData.epsilon * drawingData.epsilon):
            triangle = Polygon([(x1, y1), (x2, y2), (x3, y3)])
            trianglesIntersection.append(triangle)
    return trianglesIntersection


class PlotCanvas(FigureCanvas):
    def setDrawingData(self, arg):
        '''
        Sets arg to drawingData. This data (dots, lines, triangles) is latter drawn in self.plot
        :param arg: type of DrawingData
        :return:
        '''
        self.data = arg

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        '''
        Initializes parameters for matplotlib
        :param parent:
        :param width:
        :param height:
        :param dpi:
        '''
        #matplotlib.pyplot.subplots_adjust(hspace=20)
        
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
        '''
        Draws dots, lines, triangles in the left canvas.
        :return: None
        '''
        self.ax.set_facecolor('lightgray')
        self.ax.clear()
        self.ax.set_xlim([0, 1])
        self.ax.set_ylim([0, 1])

        triangleIntersectionArray = constructTriangleArray(drawingData.triangles)

        multiPoligon = cascaded_union(triangleIntersectionArray)

        # plot triangles
        if isinstance(multiPoligon, Polygon):
            x, y = multiPoligon.exterior.coords.xy
            self.ax.fill(x, y, alpha=0.5)
        else:
            for i in multiPoligon:
                x, y = i.exterior.coords.xy
                self.ax.fill(x, y, alpha=0.5)

        # plot lines
        for ((x1, y1), (x2, y2)) in self.data.lines:
            if((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1) <= drawingData.epsilon*drawingData.epsilon):
                self.ax.plot([x1, x2], [y1, y2], "black")

        # plot dots
        for (x, y) in self.data.dots:
            self.ax.plot([x], [y], 'bo')

        self.epsilon_line.remove()

        lines = self.ay.plot([drawingData.epsilon, drawingData.epsilon], [0, self.num], "black")

        self.epsilon_line = lines.pop()

        self.draw()

    def barCode(self):
        '''
        Draws the barcode in the right canvas.
        :return:
        '''
        self.ay.clear()
        self.ay.set_facecolor('lightgray')
        self.num = 0
        self.ay.set_xlim([0,1.42])
        self.ay.axes.set_yticks([])
        self.ay.set_yticklabels(["H0          ", "H1     ", "H2"])
        yticks = []

        # Begin section MAGIC
        for homology in ([[(degree, component) for component in dgm] for (degree, dgm) in enumerate(drawingData.diagrams)]):
            self.ay.plot([0, 1.42], [self.num, self.num], "black")
            yticks.append(self.num)
            self.ay.axes.set_yticks(yticks)
            if not drawingData.drawH2:
                homology = filter(lambda hom: hom[0] < 2, homology)

            for (_, component) in homology:
                self.ay.fill([component.birth, component.birth, min(component.death, drawingData.max_distance), min(component.death, drawingData.max_distance)], [
                            self.num, self.num+1, self.num+1, self.num], alpha=0.9)
                self.num = self.num + 1
        # End section MAGIC
        lines = self.ay.plot([drawingData.epsilon, drawingData.epsilon], [0, self.num], "black")

        self.epsilon_line = lines.pop()

        self.draw()


def generateNRandomDots(n):
    return [(random.random(), random.random()) for _ in range(n)]

def calculateLines(dots):
    '''
    Constructs all posible lines from list of 2d points
    :param dots: list of 2d points
    :return:
    '''
    lines = []
    for i in range(len(dots)):
        for j in range(len(dots)):
            if i != j:
                lines.append(
                    (dots[i], dots[j]))
    return lines

def calculateTriangles(dots):
    '''
    Constructs all possible triangles from list of 2d points
    :param dots:
    :return:
    '''
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
        '''
        Called when the user changes epsilon.
        :param num:
        :return:
        '''
        drawingData.epsilon = num/1000.0
        self.textBoxEpsilon.setText(str(drawingData.epsilon))
        self.canvas.plot()

    def onNumberOfDotsChanged(self, num):
        '''
        Called when the number of dots change. Recalculates and draws drawing data and persistence diagram.
        :param num: new number of dots
        :return:
        '''
        self.textBoxNumOfDots.setText(str(num))

        drawingData.changeNumberOfDots(num)

        drawingData.recalculateDrawingData()

        vrc = VietorisRipsComplex(
            list_of_pairs_to_numpyarray(drawingData.dots))

        drawingData.diagrams = vrc.compute_persistence(drawingData.max_distance)

        self.canvas.setDrawingData(drawingData)

        self.canvas.barCode()

        self.canvas.plot()


    def onTextBoxEpsilonChanged(self, string):
        '''

        :param string:
        :return:
        '''
        try:
            a = float(string)
            if(a >= 0 and a <= 1.42):
                self.sliderEpsilon.setValue((a*1000))
        except:
            return

    def onTextBoxNumOfDotsChanged(self, string):
        '''

        :param string:
        :return:
        '''
        try:
            a = float(string)
            if(a >= 0 and a <= 16):
                self.sliderNumDots.setValue((a))
        except:
            return

    def changeTheme(self):
        '''

        :return:
        '''
        global app
        if self.DarkThemeCheckBox.isChecked():
            app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        else:
            app.setStyleSheet('')

    def onLoadFileButtonClick(self):
        try:
            file = QFileDialog.getOpenFileName(self, 'Open file', os.curdir," (*.csv )")
            drawingData.dots = np.loadtxt(fname = file[0], delimiter=',', dtype=np.float)
            drawingData.recalculateDrawingData()
            
            vrc = VietorisRipsComplex(drawingData.dots)
            
            drawingData.diagrams = vrc.compute_persistence(drawingData.max_distance)

            self.canvas.setDrawingData(drawingData)

            self.canvas.barCode()

            self.canvas.plot()
            
            self.sliderNumDots.setDisabled(True)

            self.textBoxNumOfDots.setDisabled(True)
            

            # gui postavi broj tacaka, slider ...
        except IOError:
            pass


    def changeH2(self):
        drawingData.drawH2 = self.H2CheckBox.isChecked()

        self.canvas.barCode()

    def __init__(self, parent=None):
        '''

        :param parent:
        '''

        super(Window, self).__init__(parent)
        grid = QGridLayout()
        labelaNumDots = QLabel("Broj tačaka:")
        labelaEpsilon = QLabel("Epsilon:")

        self.sliderNumDots = QSlider(Qt.Horizontal)
        self.sliderEpsilon = QSlider(Qt.Horizontal)

        self.sliderNumDots.setMaximum(16)
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

        self.DarkThemeCheckBox = QCheckBox("Pređi na \ntamnu stranu")
        self.H2CheckBox = QCheckBox("Prikaži H2")

        self.Button = QPushButton("Izaberi fajl sa tackama")
        self.Button.clicked.connect(self.onLoadFileButtonClick)

        self.canvas = PlotCanvas(self, width=1, height=1)
        self.canvas.setDrawingData(drawingData)
        self.canvas.barCode()
        self.canvas.plot()

        # Register events:
        self.sliderNumDots.valueChanged.connect(self.onNumberOfDotsChanged)
        self.sliderEpsilon.valueChanged.connect(self.onEpsilonChanged)

        self.textBoxEpsilon.textEdited.connect(self.onTextBoxEpsilonChanged)
        self.textBoxNumOfDots.textEdited.connect(self.onTextBoxNumOfDotsChanged)

        self.DarkThemeCheckBox.stateChanged.connect(self.changeTheme)
        self.H2CheckBox.stateChanged.connect(self.changeH2)
        self.Labela = QLabel("Kristina Popović & Marko Spasić, 2019")
        grid.setContentsMargins(8, 8, 8, 8)

        grid.addWidget(labelaNumDots, 0, 0)
        grid.addWidget(self.sliderNumDots, 0, 1)
        grid.addWidget(self.textBoxNumOfDots, 0, 2)
        grid.addWidget(self.Button, 0,3)
        grid.addWidget(self.H2CheckBox,1,3)
        grid.addWidget(labelaEpsilon, 1, 0)
        grid.addWidget(self.sliderEpsilon, 1, 1)
        grid.addWidget(self.textBoxEpsilon, 1, 2)
        grid.addWidget(self.canvas, 3, 0, 1, 4)
        grid.addWidget(self.DarkThemeCheckBox, 4, 3)
        grid.addWidget(self.Labela,4,0)

        #grid.addWidget(self.createSlider("Random faktor"), 2, 0)
        self.setLayout(grid)
        self.setWindowTitle("Perzistentna homologija")
        self.resize(1490, 960)


def main():
    global app
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    clock = Window()
    clock.show()
    #clock.showFullScreen()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
