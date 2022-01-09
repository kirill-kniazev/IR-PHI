# import required modules
from PyQt5.QtWidgets import *
import sys
import numpy as np
import pyqtgraph as pg
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from collections import namedtuple


App = QApplication(sys.argv)


# setting title
self.setWindowTitle("PyQtGraph")

# setting geometry
self.setGeometry(100, 100, 600, 500)

# icon
icon = QIcon("skin.png")

# setting icon to the window
self.setWindowIcon(icon)

# calling method
self.UiComponents()

# showing all the widgets
self.show()

# creating a widget object
widget = QWidget()

# creating a label
label = QLabel("Geeksforgeeks Image View")

# setting minimum width
label.setMinimumWidth(130)

# making label do word wrap
label.setWordWrap(True)

# setting configuration options
pg.setConfigOptions(antialias=True)

# creating image view view object
imv = pg.ImageView()

# Displaying the data and assign each frame a time value from 1.0 to 3.0
imv.setImage(data)

self.setCentralWidget(widget)


# start the app
sys.exit(App.exec())
