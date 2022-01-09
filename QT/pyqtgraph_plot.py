from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QMessageBox, QFileDialog, QHBoxLayout)
from PyQt5.QtCore import QTimer, QEventLoop, QCoreApplication
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import sys
import time

x = np.random.randint(0, 100, 100)
y = np.random.randint(0, 100, 100)


app = QtWidgets.QApplication(sys.argv)
spec_win = QtWidgets.QMainWindow()
spec_win.resize(800,800)

graphWidget = pg.PlotWidget()
spec_win.setCentralWidget(graphWidget)

pen = pg.mkPen(color=(255, 0, 0), width=2)

data =graphWidget.plot(x, y, pen=pen)
graphWidget.setBackground('w')
graphWidget.showGrid(x=True, y=True)
graphWidget.setTitle("<span style=\"font-size:20px\">IR absorption Chart</span>")
graphWidget.setLabel("left", "<span style=\"font-size:20px\">IR absorption</span>")
graphWidget.setLabel('bottom', "<span style=\"font-size:20px\">ν, cm⁻¹</span>")

spec_win.show()

# print(dir(graphWidget))

for _ in range(20):
    x = np.random.randint(0, 100, 100)
    y = np.random.randint(0, 100, 100)
    data.setData(x, y)


    QtCore.QCoreApplication.processEvents()
    time.sleep(0.2)

pg.exec()