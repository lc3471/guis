# Laurel Carpenter 
# 07/28/2021

from psu1 import PSU1
from psu2 import PSU2
from pulse import Pulse
from scope import Scope
from motion import Motion

from PyQt5.QtChart import QChartView, QChart, QLineSeries, QSplineSeries, QValueAxis
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)

import sys

class WidgetGallery(QDialog):
    def __init__(self,parent=None):
        super(WidgetGallery,self).__init__(parent)

        mainLayout=QGridLayout()

        self.psu1=PSU1()
        self.psu2=PSU2()
        self.pulse=Pulse()
        self.scope=Scope()
        self.motion=Motion()

        mainLayout.addWidget(self.psu1)
        mainLayout.addWidget(self.psu2)
        mainLayout.addWidget(self.pulse)
        mainLayout.addWidget(self.scope)
        mainLayout.addWidget(self.motion)

        self.setLayout(mainLayout)


if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())

