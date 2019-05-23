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

import itertools

class DrawingData:

    def __init__(self):
        self.dots = np.empty([0,2])
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
        self.lines = list(itertools.combinations(self.dots, 2))

        self.triangles.clear()
        self.triangles = list(itertools.combinations(self.dots, 3))

    def clear(self):
        self.dots = np.empty([0,2])
        self.lines.clear()
        self.triangles.clear()
        self.diagrams.clear()



drawingData = DrawingData()


def constructTriangleArray(triangles):
    '''
    Constructs polygons to be drawn by matplot
    :param triangles:
    :return:
    '''
    trianglesIntersection = []
    for ((x1, y1), (x2, y2), (x3, y3)) in triangles:
        #print((x1, y1), (x2, y2), (x3, y3))
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

        multiPoligon = constructTriangleArray(drawingData.triangles)

        # plot triangles
        if isinstance(multiPoligon, Polygon):
            x, y = multiPoligon.exterior.coords.xy
            self.ax.fill(x, y, 'b', alpha=0.5,)
        else:
            for i in multiPoligon:
                x, y = i.exterior.coords.xy
                self.ax.fill(x, y, 'b', alpha=0.5)

        # plot lines
        for ((x1, y1), (x2, y2)) in self.data.lines:
            if((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1) <= drawingData.epsilon*drawingData.epsilon):
                self.ax.plot([x1, x2], [y1, y2], "black")

        # plot dots
        for dot in self.data.dots:
            self.ax.plot([dot[0]], [dot[1]], 'bo')

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

    def onDeleteDotsButtonPressed(self):
        drawingData.clear()
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

            # gui postavi broj tacaka, slider ...
        except IOError:
            pass


    def changeH2(self):
        drawingData.drawH2 = self.H2CheckBox.isChecked()

        self.canvas.barCode()


    def onPlotCanvasClick(self, event):
        if self.canvas.ax == event.inaxes:
            drawingData.dots = np.append(drawingData.dots, [[float(event.xdata), float(event.ydata)]], axis=0)
            drawingData.recalculateDrawingData()

            vrc = VietorisRipsComplex(drawingData.dots)

            drawingData.diagrams = vrc.compute_persistence(drawingData.max_distance)

            self.canvas.setDrawingData(drawingData)
            self.canvas.barCode()
            self.canvas.plot()


    def __init__(self, parent=None):
        '''

        :param parent:
        '''

        super(Window, self).__init__(parent)
        grid = QGridLayout()

        labelaEpsilon = QLabel("Epsilon:")

        self.sliderEpsilon = QSlider(Qt.Horizontal)

        self.sliderEpsilon.setMaximum(1420)
        self.sliderEpsilon.setMinimum(0)

        self.sliderEpsilon.setSingleStep(1)

        self.textBoxEpsilon = QLineEdit("0")

        self.textBoxEpsilon.setMaximumWidth(50)

        self.textBoxEpsilon.setMaxLength(4)

        self.DarkThemeCheckBox = QCheckBox("Come to the dark side")
        self.H2CheckBox = QCheckBox("Show H2")

        self.Button = QPushButton("Open file")
        self.Button.clicked.connect(self.onLoadFileButtonClick)

        self.DeleteDotsButton = QPushButton("Clear")

        self.canvas = PlotCanvas(self, width=1, height=1)
        self.canvas.setDrawingData(drawingData)
        self.canvas.barCode()
        self.canvas.plot()

        self.canvas.mpl_connect('button_press_event', self.onPlotCanvasClick)

        # Register events:
        self.sliderEpsilon.valueChanged.connect(self.onEpsilonChanged)
        self.DeleteDotsButton.clicked.connect(self.onDeleteDotsButtonPressed)
        self.textBoxEpsilon.textEdited.connect(self.onTextBoxEpsilonChanged)

        self.DarkThemeCheckBox.stateChanged.connect(self.changeTheme)
        self.H2CheckBox.stateChanged.connect(self.changeH2)
        self.Labela = QLabel("Kristina Popović & Marko Spasić, 2019")
        grid.setContentsMargins(8, 8, 8, 8)

        grid.addWidget(labelaEpsilon, 0, 0)
        grid.addWidget(self.sliderEpsilon, 0, 1)

        grid.addWidget(self.textBoxEpsilon, 0, 2)
        grid.addWidget(self.Button, 0,3)
        grid.addWidget(self.DeleteDotsButton, 0,4)
        grid.addWidget(self.H2CheckBox,0,5)
        grid.addWidget(self.canvas, 1, 0, 1,6)
        
        grid.addWidget(self.Labela,2,0)
        grid.addWidget(self.DarkThemeCheckBox, 2, 5)
        
        self.setLayout(grid)
        self.setWindowTitle("Persistent homology")
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
