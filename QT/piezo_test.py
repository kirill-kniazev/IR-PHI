import os,sys,inspect
from PyQt5 import *
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QFileDialog
from PyQt5.QtCore import QTimer, QEventLoop
from PyQt5 import uic

# to add parent dir to path
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from datetime import datetime
import random

from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg

from madpiezo import Madpiezo
import numpy as np
from time import sleep, time
import re
# import Firefly_SW #192.168.1.229, separate py file
# import Firefly_LW #192.168.1.231, , separate py file
# import zhinst.ziPython, zhinst.utils
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("piezo.ui", self)
        
        
        
        #============================== SLOTS =================================
        self.BUT_initialize.clicked.connect(self.on_initialize)
        self.action_save_r.triggered.connect(self.on_save_r)
        
        #============================== /SLOTS ================================
    def on_initialize(self):
        for i in range(101):
            self.PROGBAR_pb1_IMAGING.setValue(i)
            QtCore.QCoreApplication.processEvents()
            sleep(0.5)
    def on_save_r(self):
        print("Some text")
        


# app = QtWidgets.QApplication(sys.argv)
# window = MainWindow()
# window.show()
# app.exec_()