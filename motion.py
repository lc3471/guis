# Laurel Carpenter
# 07/28/2021
# adapted from motion_control_gui.py

from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QComboBox, QDialog, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber, QLineEdit,
    QPushButton, QVBoxLayout, QWidget, QMessageBox)

from dcps import NewportESP301
from pyvisa.errors import VisaIOError
from serial.serialutil import SerialException

wait=100

class Motion(QDialog):
    def __init__(self,parent=None):
        super(Motion,self).__init__(parent)

        mainLayout=QGridLayout()
        try:
            self.create_control_box()
            self.isConnected=True
        except VisaIOError as err:
            self.control_box=QLabel("Motion Controller Not Connected:",str(err))
            self.isConnected=False
        except SerialException as err:
            self.control_box=QLabel("Motion Controller Not Connected:",str(err))
            self.isConnected=False

        mainLayout.addWidget(self.control_box)
        self.setLayout(mainLayout)


    def open_newport(self,path):
        self.newport=NewportESP301(path)
        self.newport.open_inst()


    def create_control_box(self):

        self.open_newport('ASRL/dev/ttyUSB0::INSTR')

        self.qTimer=QTimer()
        self.qTimer.setInterval(1000)
        self.qTimer.start()

        self.qTimer.timeout.connect(self.check_motor1)
        self.qTimer.timeout.connect(self.check_motor2)
        self.qTimer.timeout.connect(self.check_pos1)
        self.qTimer.timeout.connect(self.check_pos2)

        self.control_box=QGroupBox("Newport Motion Controller")
        self.control_layout=QGridLayout()
        self.control_box.setLayout(self.control_layout)

        self.create_indef_box()
        self.create_motion1box()
        self.create_motion2box()
        self.create_side_box()

        self.control_layout.addWidget(self.indef_box,0,0)
        self.control_layout.addWidget(self.side_box,1,0)
        self.control_layout.addWidget(self.motion1box,0,1,2,1)
        self.control_layout.addWidget(self.motion2box,0,3,2,1)

        self.indef_box.setMaximumSize(150,1000)
        self.side_box.setMaximumSize(150,1000)

    def create_indef_box(self):
        self.indef_box=QGroupBox("Move by 1 unit")
        self.indef_layout=QGridLayout()
        self.indef_box.setLayout(self.indef_layout)

        self.upbutton=QPushButton('\u039B')
        self.downbutton=QPushButton('V')
        self.leftbutton=QPushButton('<')
        self.rightbutton=QPushButton('>')

        self.upbutton.clicked.connect(self.on_up_clicked)
        self.downbutton.clicked.connect(self.on_down_clicked)
        self.leftbutton.clicked.connect(self.on_left_clicked)
        self.rightbutton.clicked.connect(self.on_right_clicked)

        self.indef_layout.addWidget(self.upbutton,0,1)
        self.indef_layout.addWidget(self.downbutton,2,1)
        self.indef_layout.addWidget(self.leftbutton,1,0)
        self.indef_layout.addWidget(self.rightbutton,1,2)

    def create_side_box(self):
        self.side_box=QGroupBox()
        self.side_layout=QVBoxLayout()
        self.side_box.setLayout(self.side_layout)

        self.abort_button=QPushButton("Abort Motion")
        self.abort_button.clicked.connect(self.on_abort_clicked)

        self.wait_label=QLabel("Set Wait Time [ms]")
        self.wait_edit=QLineEdit()
        self.wait_button=QPushButton("Wait")
        self.wait_button.clicked.connect(self.on_wait_clicked)

        self.unitmenu=QComboBox()
        self.unitmenu.addItem('mm')
        self.unitmenu.addItem('\u03BCm')
        self.unitmenu.addItem('in')
        self.unitmenu.addItem('mIn')
        self.unitmenu.addItem('\u03BCIn')
        self.unitmenu.addItem('deg')
        self.unitmenu.addItem('grad')
        self.unitmenu.addItem('rad')
        self.unitmenu.addItem('mRad')
        self.unitmenu.addItem('\u03BCRad')

        self.newport.set_units(1,'mm')
        self.newport.set_units(2,'mm')

        self.unitbutton=QPushButton("Set Unit")
        self.unitbutton.clicked.connect(self.on_unit_clicked)

        self.side_layout.addWidget(self.abort_button)
        self.side_layout.addWidget(self.wait_label)
        self.side_layout.addWidget(self.wait_edit)
        self.side_layout.addWidget(self.wait_button)
        self.side_layout.addWidget(self.unitmenu)
        self.side_layout.addWidget(self.unitbutton)

    def create_motion1box(self):
        self.motion1box=QGroupBox("Control Axis 1 (Left/Right)")
        self.motion1layout=QVBoxLayout()
        self.motion1box.setLayout(self.motion1layout)

        self.create_motor1box()
        self.create_pos1box()

        self.motion1layout.addWidget(self.motor1box)
        self.motion1layout.addWidget(self.pos1box)

    def create_motor1box(self):
        self.motor1box=QGroupBox()
        self.motor1layout=QVBoxLayout()
        self.motor1box.setLayout(self.motor1layout)

        self.motor1disp=QLabel()
        self.motor1disp.setAlignment(Qt.AlignCenter)
        self.motor1disp.setFrameShape(QFrame.StyledPanel)

        try:
            self.motor1on=self.newport.is_motor_on(1)
            self.newport.wait_time(wait)
        except:
            self.motor1on=False

        if self.motor1on:
            self.motor1disp.setText("Motor is On")
            self.motor1disp.setStyleSheet('background:limegreen')
        else:
            self.motor1disp.setText("Motor is Off")
            self.motor1disp.setStyleSheet('background:red')

        self.motor1button=QPushButton("Toggle Motor On/Off")
        self.motor1button.clicked.connect(self.toggle_motor1)

        self.motor1layout.addWidget(self.motor1disp)
        self.motor1layout.addWidget(self.motor1button)

    def create_pos1box(self):
        self.pos1box=QGroupBox("Position (Horizontal)")
        self.pos1layout=QGridLayout()
        self.pos1box.setLayout(self.pos1layout)

        self.despos1label=QLabel("Desired")
        self.despos1disp=QLCDNumber()
        self.despos1=0
        self.despos1disp.display(self.despos1)

        self.actpos1label=QLabel("Actual")
        self.actpos1disp=QLCDNumber()
        try:
            self.actpos1=self.newport.get_act_pos(1)
            self.newport.wait_time(wait)
        except:
            self.actpos1=0
        self.actpos1disp.display(self.actpos1)

        self.abs1edit=QLineEdit()
        self.abs1button=QPushButton("Set Absolute")
        self.abs1button.clicked.connect(self.on_abs1_clicked)

        self.rel1edit=QLineEdit()
        self.rel1button=QPushButton("Move Relative")
        self.rel1button.clicked.connect(self.on_rel1_clicked)

        self.ll1disp=QLCDNumber()
        self.ll1edit=QLineEdit()
        self.ll1button=QPushButton("Set Left Limit")
        self.ll1button.clicked.connect(self.on_ll1_clicked)
        self.rl1disp=QLCDNumber()
        self.rl1edit=QLineEdit()
        self.rl1button=QPushButton("Set Right Limit")
        self.rl1button.clicked.connect(self.on_rl1_clicked)

        self.pos1layout.addWidget(self.despos1label,0,0)
        self.pos1layout.addWidget(self.despos1disp,1,0)
        self.pos1layout.addWidget(self.actpos1label,0,1)
        self.pos1layout.addWidget(self.actpos1disp,1,1)
        self.pos1layout.addWidget(self.abs1edit,2,0)
        self.pos1layout.addWidget(self.abs1button,3,0)
        self.pos1layout.addWidget(self.rel1edit,2,1)
        self.pos1layout.addWidget(self.rel1button,3,1)
        #self.pos1layout.addWidget(self.ll1disp,4,0)
        #self.pos1layout.addWidget(self.rl1disp,4,1)
        #self.pos1layout.addWidget(self.ll1edit,5,0)
        #self.pos1layout.addWidget(self.rl1edit,5,1)
        #self.pos1layout.addWidget(self.ll1button,6,0)
        #self.pos1layout.addWidget(self.rl1button,6,1)

    def create_motion2box(self):
        self.motion2box=QGroupBox("Control Axis 2 (Up/Down)")
        self.motion2layout=QVBoxLayout()
        self.motion2box.setLayout(self.motion2layout)

        self.create_motor2box()
        self.create_pos2box()

        self.motion2layout.addWidget(self.motor2box)
        self.motion2layout.addWidget(self.pos2box)

    def create_motor2box(self):
        self.motor2box=QGroupBox()
        self.motor2layout=QVBoxLayout()
        self.motor2box.setLayout(self.motor2layout)

        self.motor2disp=QLabel()
        self.motor2disp.setAlignment(Qt.AlignCenter)
        self.motor2disp.setFrameShape(QFrame.StyledPanel)

        try:
            self.motor2on=self.newport.is_motor_on(2)
            self.newport.wait_time(wait)
        except:
            self.motor2on=False

        if self.motor2on:
            self.motor2disp.setText("Motor is On")
            self.motor2disp.setStyleSheet('background:limegreen')
        else:
            self.motor2disp.setText("Motor is Off")
            self.motor2disp.setStyleSheet('background:red')

        self.motor2button=QPushButton("Toggle Motor On/Off")
        self.motor2button.clicked.connect(self.toggle_motor2)

        self.motor2layout.addWidget(self.motor2disp)
        self.motor2layout.addWidget(self.motor2button)

    def create_pos2box(self):
        self.pos2box=QGroupBox("Position (Vertical)")
        self.pos2layout=QGridLayout()
        self.pos2box.setLayout(self.pos2layout)

        self.despos2label=QLabel("Desired")
        self.despos2disp=QLCDNumber()
        self.despos2=0
        self.despos2disp.display(self.despos2)

        self.actpos2label=QLabel("Actual")
        self.actpos2disp=QLCDNumber()
        try:
            self.actpos2=self.newport.get_act_pos(2)
            self.newport.wait_time(wait)
        except:
            self.actpos2=0
        self.actpos2disp.display(self.actpos2)

        self.abs2edit=QLineEdit()
        self.abs2button=QPushButton("Set Absolute")
        self.abs2button.clicked.connect(self.on_abs2_clicked)

        self.rel2edit=QLineEdit()
        self.rel2button=QPushButton("Move Relative")
        self.rel2button.clicked.connect(self.on_rel2_clicked)

        self.ll2disp=QLCDNumber()
        self.ll2edit=QLineEdit()
        self.ll2button=QPushButton("Set Lower Limit")
        self.ll2button.clicked.connect(self.on_ll2_clicked)
        self.rl2disp=QLCDNumber()
        self.rl2edit=QLineEdit()
        self.rl2button=QPushButton("Set Upper Limit")
        self.rl2button.clicked.connect(self.on_rl2_clicked)

        self.pos2layout.addWidget(self.despos2label,0,0)
        self.pos2layout.addWidget(self.despos2disp,1,0)
        self.pos2layout.addWidget(self.actpos2label,0,1)
        self.pos2layout.addWidget(self.actpos2disp,1,1)
        self.pos2layout.addWidget(self.abs2edit,2,0)
        self.pos2layout.addWidget(self.abs2button,3,0)
        self.pos2layout.addWidget(self.rel2edit,2,1)
        self.pos2layout.addWidget(self.rel2button,3,1)
        #self.pos2layout.addWidget(self.ll2disp,4,0)
        #self.pos2layout.addWidget(self.rl2disp,4,1)
        #self.pos2layout.addWidget(self.ll2edit,5,0)
        #self.pos2layout.addWidget(self.rl2edit,5,1)
        #self.pos2layout.addWidget(self.ll2button,6,0)
        #self.pos2layout.addWidget(self.rl2button,6,1)


    def check_motor1(self):
        try:
            self.motor1on=self.newport.is_motor_on(1)
            self.newport.wait_time(wait)
            if self.motor1on:
                self.motor1disp.setText("Motor is On")
                self.motor1disp.setStyleSheet('background:limegreen')
            else:
                self.motor1disp.setText("Motor is Off")
                self.motor1disp.setStyleSheet('background:red')
        except:
            pass

    def check_pos1(self):
        self.actpos1=self.newport.get_act_pos(1)
        self.actpos1disp.display(self.actpos1)
        self.newport.wait_time(wait)

    def check_motor2(self):
        try:
            self.motor2on=self.newport.is_motor_on(2)
            self.newport.wait_time(wait)
            if self.motor2on:
                self.motor2disp.setText("Motor is On")
                self.motor2disp.setStyleSheet('background:limegreen')
            else:
                self.motor2disp.setText("Motor is Off")
                self.motor2disp.setStyleSheet('background:red')
        except:
            pass

    def check_pos2(self):
        try:
            self.actpos2=self.newport.get_act_pos(2)
            self.actpos2disp.display(self.actpos2)
            self.newport.wait_time(wait)
        except:
            pass

    def on_abort_clicked(self):
        # some sort of alert/check?
        self.newport.abort_motion()
        self.newport.wait_time(wait)

    def on_wait_clicked(self):
        try:
            w=self.wait_edit.text()
            self.newport.wait_time(w)
        except:
            pass

    def toggle_motor1(self):
        try:
            if self.newport.is_motor_on(1):
                self.newport.wait_time(wait)
                self.newport.motor_off(1)
                self.motor1disp.setText("Motor is Off")
                self.motor1disp.setStyleSheet('background:red')
            else:
                self.newport.wait_time(wait)
                self.newport.motor_on(1)
                self.motor1disp.setText("Motor is On")
                self.motor1disp.setStyleSheet('background:limegreen')
            self.newport.wait_time(wait)
        except:
            pass

    def on_unit_clicked(self):
        try:
            unit=self.unitmenu.currentText()
            if unit[0]=="\u03BC":
                unit=unit.replace("\u03BC","u")
            self.newport.set_units(1,unit)
            self.newport.set_units(2,unit)
        except:
            pass

    def toggle_motor2(self):
        try:
            if self.newport.is_motor_on(2):
                self.newport.wait_time(wait)
                self.newport.motor_off(2)
                self.motor2disp.setText("Motor is Off")
                self.motor2disp.setStyleSheet('background:red')
            else:
                self.newport.wait_time(wait)
                self.newport.motor_on(2)
                self.motor2disp.setText("Motor is On")
                self.motor2disp.setStyleSheet('background:limegreen')
            self.newport.wait_time(wait)
        except:
            pass

    def on_left_clicked(self):
        try:
            self.newport.move_rel_pos(1,-1)
            self.newport.wait_motion_stop(1)
        except:
            pass

    def on_right_clicked(self):
        try:
            self.newport.move_rel_pos(1,1)
            self.newport.wait_motion_stop(1)
        except:
            pass

    def on_down_clicked(self):
        try:
            self.newport.move_rel_pos(2,-1)
            self.newport.wait_motion_stop(2)
        except:
            pass

    def on_up_clicked(self):
        try:
            self.newport.move_rel_pos(2,1)
            self.newport.wait_motion_stop(2)
        except:
            pass

    def on_abs1_clicked(self):
        pos=float(self.abs1edit.text())
        #if pos>self.llim1 and pos<self.rlim1:
        try:
            self.newport.move_abs_pos(1,pos)
            self.newport.wait_motion_stop(1)
            self.despos1=pos
            self.despos1disp.display(self.despos1)
        except:
            pass

    def on_rel1_clicked(self):
        try:
            disp=float(self.rel1edit.text())
            pos=self.newport.get_abs_pos(1)
            self.newport.wait_time(wait)
            #if pos+disp>self.llim1 and pos+disp<self.rlim1:
            self.newport.move_rel_pos(1,disp)
            self.newport.wait_motion_stop(1)
            self.despos1=pos+disp
            self.despos1disp.display(self.despos1)
        except:
            pass

    def on_ll1_clicked(self):
        self.llim1=float(self.ll1edit.text())
        self.ll1disp.display(self.llim1)

    def on_rl1_clicked(self):
        self.rlim1=float(self.rl1edit.text())
        self.rl1disp.display(self.rlim1)

    def on_abs2_clicked(self):
        pos=float(self.abs2edit.text())
        #if pos>self.llim2 and pos<self.rlim2:
        try:
            self.newport.move_abs_pos(2,pos)
            self.newport.wait_motion_stop(2)
            self.despos2=pos
            self.despos2disp.display(self.despos2)
        except:
            pass

    def on_rel2_clicked(self):
        try:
            disp=float(self.rel2edit.text())
            pos=self.newport.get_abs_pos(2)
            self.newport.wait_time(wait)
            #if pos+disp>self.llim2 and pos+disp<self.rlim2:
            self.newport.move_rel_pos(2,disp)
            self.newport.wait_motion_stop(2)
            self.despos2=pos+disp
            self.despos2disp.display(self.despos2)
        except:
            pass

    def on_ll2_clicked(self):
        self.llim2=float(self.ll2edit.text())
        self.ll2disp.display(self.llim2)

    def on_rl2_clicked(self):
        self.rlim2=float(self.rl2edit.text())
        self.rl2disp.display(self.rlim2)
