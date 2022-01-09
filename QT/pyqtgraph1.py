from PyQt5.QtWidgets import (QApplication, QWidget, QPushButton,
                             QMessageBox, QFileDialog, QHBoxLayout)
from PyQt5.QtCore import QTimer, QEventLoop, QCoreApplication
import pyqtgraph as pg
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
import sys
import time

app = QtWidgets.QApplication(sys.argv)
imag_win = QtWidgets.QMainWindow()
imag_win.resize(800,800)

imv_r = pg.ImageView()
imag_win.setCentralWidget(imv_r)

imag_win.show()
imag_win.setWindowTitle('Imaging Plot')
start = time.time()

for _ in range(1000):
    r_data = np.random.randint(0, 100, size = (500, 500))
    imv_r.setImage(r_data)
    QtCore.QCoreApplication.processEvents()
    # time.sleep(0.2)

print(time.time() - start)
pg.exec()