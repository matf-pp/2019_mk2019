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

numOfDots = 0
epsilon = 0
skupTacaka ={"tacke":[],"duzi":[],"trouglovi":[]}

class PlotCanvas(FigureCanvas):
    def setData(self, arg):
        self.data = arg

    def __init__(self, parent=None, width=5, height=5, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = plt.gca()
        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,QSizePolicy.Expanding,QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)

    def plot(self):
        # Ovaj broj ima značenje 1X1 grid, prvi subplot, 234 bi značio 2X3, četvrti subplot
        global epsilon
        ax = self.figure.gca()
        ax.clear()
        ax.set_xlim([0, 1])
        ax.set_ylim([0, 1])

        nizTrouglovaZaPresek = []
        for((x1, y1), (x2, y2), (x3, y3)) in self.data["trouglovi"]:
            if ((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1)<=epsilon*epsilon and
               (x3-x1)*(x3-x1)+(y3-y1)*(y3-y1)<=epsilon*epsilon and
               (x2-x3)*(x2-x3)+(y2-y3)*(y2-y3)<=epsilon*epsilon):
                    #ax.fill([x1, x2, x3], [y1, y2, y3],alpha = 0.5)
                    
                    trougao = Polygon([(x1,y1),(x2,y2),(x3,y3)])
                    nizTrouglovaZaPresek.append(trougao)

        multiPoligon = cascaded_union(nizTrouglovaZaPresek)
        if isinstance(multiPoligon,Polygon):
                x, y = multiPoligon.exterior.coords.xy
                ax.fill(x,y,alpha = 0.5)
        else:
            for i in multiPoligon:
                x, y = i.exterior.coords.xy
                ax.fill(x,y,alpha = 0.5)
        

        for ((x1, y1), (x2, y2)) in self.data["duzi"]:
            if((x2-x1)*(x2-x1)+(y2-y1)*(y2-y1)<=epsilon*epsilon):
                ax.plot([x1, x2], [y1, y2],"black")

        for (x, y) in self.data["tacke"]:
            ax.plot([x], [y], 'bo')  # crta tačke

        ax.set_title('Treba li nam naslov?')
        self.draw()


class Window(QWidget):

    def generisiSkupTacaka(self, newNumOfDots):
        global numOfDots
        global skupTacaka
        global epsilon
        if(newNumOfDots>numOfDots):
            for i in range(newNumOfDots-numOfDots):
                skupTacaka["tacke"].append((random.random(),random.random()))
        if(newNumOfDots<numOfDots):
            for i in range(numOfDots - newNumOfDots):
                skupTacaka["tacke"].pop()
        numOfDots = newNumOfDots
        skupTacaka["duzi"] = []
        for i in range(numOfDots):
            for j in range(numOfDots):
                if i!=j:
                    skupTacaka["duzi"].append((skupTacaka["tacke"][i],skupTacaka["tacke"][j]))
        skupTacaka["trouglovi"] = []
        for i in range(numOfDots):
            for j in range(numOfDots):
                for k in range(numOfDots):
                    if i!= j and j!=k and k!=i:
                        skupTacaka["trouglovi"].append((skupTacaka["tacke"][i],skupTacaka["tacke"][j],skupTacaka["tacke"][k]))

        
        self.canvas.setData(skupTacaka)
        self.canvas.plot()

    def promeniEpsilon(self,num):
        global epsilon
        epsilon = num/1000.0
        self.textBoxEpsilon.setText(str(epsilon))
        self.canvas.plot()
    
    def promeniNumOfDots(self,num):
        self.textBoxNumOfDots.setText(str(num))
        self.generisiSkupTacaka(num)

    def promeniTextBoxEpsilon(self,string):
        try:
            a = float(string)
            if(a>=0 and a<=1.42):
                self.sliderEpsilon.setValue((a*1000))
        except:
            return
    def promeniTextBoxNumOfDots(self,string):
        try:
            a = float(string)
            if(a>=0 and a<=30):
                self.sliderNumDots.setValue((a))
        except:
            return
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

        self.canvas = PlotCanvas(self, width=1, height=1)
        self.canvas.setData(skupTacaka)
        self.canvas.plot()

        #Eventovi:
        self.sliderNumDots.valueChanged.connect(self.promeniNumOfDots)
        self.sliderEpsilon.valueChanged.connect(self.promeniEpsilon)

        self.textBoxEpsilon.textEdited.connect(self.promeniTextBoxEpsilon)
        self.textBoxNumOfDots.textEdited.connect(self.promeniTextBoxNumOfDots)

        grid.setContentsMargins(8, 8, 8, 8)

        grid.addWidget(labelaNumDots, 0, 0)
        grid.addWidget(self.sliderNumDots, 0, 1)
        grid.addWidget(self.textBoxNumOfDots, 0, 2)
        grid.addWidget(labelaEpsilon, 1, 0)
        grid.addWidget(self.sliderEpsilon, 1, 1)
        grid.addWidget(self.textBoxEpsilon, 1, 2)
        grid.addWidget(self.canvas, 3, 0, 1, 3)
        grid.addWidget(QCheckBox("Izračunaj perzistentnu homologiju"), 2, 0, 1, 3)

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
