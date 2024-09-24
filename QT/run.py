import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from piezo import MainWindow

    
app = QtWidgets.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())