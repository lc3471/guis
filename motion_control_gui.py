# author: Laurel Carpenter
# date 07/22/2021

from dcps import ESP301

from PyQt5.QtChart import QChartView, QChart, QLineSeries, QSplineSeries, QValueAxis
from PyQt5.QtCore import Qt, QSize, QTimer
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox, QDateTimeEdit,
        QDial, QDialog, QFrame, QGridLayout, QGroupBox, QHBoxLayout, QLabel, QLCDNumber,
        QLineEdit, QProgressBar, QPushButton, QRadioButton, QScrollBar, QSizePolicy,
        QSlider, QSpinBox, QStyleFactory, QTableWidget, QTabWidget, QTextEdit,
        QVBoxLayout, QFormLayout, QWidget, QMessageBox)

import sys
from time import sleep

wait=100

class WidgetGallery(QDialog):
    def __init__(self,parent=None):
        super(WidgetGallery,self).__init__(parent)

        self.open_newport('ASRL/dev/ttyUSB0::INSTR')
        
        self.qTimer=QTimer()
        self.qTimer.setInterval(1000)
        self.qTimer.start()

        #self.qTimer.timeout.connect(self.check_unit)
        #self.qTimer.timeout.connect(self.check_motor)
        #self.qTimer.timeout.connect(self.check_motion)
        #self.qTimer.timeout.connect(self.check_desired)
        #self.qTimer.timeout.connect(self.check_actual)
        #self.qTimer.timeout.connect(self.check_max)
        #self.qTimer.timeout.connect(self.check_accel)

        mainLayout=QGridLayout()
        self.create_control_box()
        mainLayout.addWidget(self.control_box)
        self.setLayout(mainLayout)


    def open_newport(self,path):
        self.newport=ESP301(path)
        self.newport.open_inst()

    def create_control_box(self):
        self.control_box=QGroupBox()
        self.control_layout=QHBoxLayout()
        self.control_box.setLayout(self.control_layout)

        self.create_display_box()
        self.create_box1()
        #self.create_box2()
        self.create_side_box()

        self.control_layout.addWidget(self.display_box)
        self.control_layout.addWidget(self.box1)
        #self.control_layout.addWidget(self.box2)
        self.control_layout.addWidget(self.side_box)

    def create_display_box(self):
        self.display_box=QGroupBox()

    def create_side_box(self):
        self.side_box=QGroupBox()
        self.side_layout=QVBoxLayout()
        self.side_box.setLayout(self.side_layout)

        self.abort_button=QPushButton("Abort Motion")
        self.abort_button.clicked.connect(self.on_abort_clicked)

        self.abort_prog_button=QPushButton("Abort Program")
        self.abort_prog_button.clicked.connect(self.newport.abort_prog)

        self.quit_prog_button=QPushButton("Quit Programming Mode")
        self.quit_prog_button.clicked.connect(self.newport.quit_prog_mode)

        self.wait_label=QLabel("Set Wait Time [ms]")
        self.wait_edit=QLineEdit()
        self.wait_button=QPushButton("Wait")
        self.wait_button.clicked.connect(self.on_wait_clicked)

        self.side_layout.addWidget(self.abort_button)
        self.side_layout.addWidget(self.abort_prog_button)
        self.side_layout.addWidget(self.quit_prog_button)
        self.side_layout.addWidget(self.wait_label)
        self.side_layout.addWidget(self.wait_edit)
        self.side_layout.addWidget(self.wait_button)

    def create_box1(self):
        self.box1=QGroupBox()
        self.box1layout=QGridLayout()
        self.box1.setLayout(self.box1layout)

        self.newport.set_units(1,'mm')
        #self.create_unit1box()
        self.create_motion1box()
        #self.create_program1box()
        #self.create_wait1box()

        #self.box1layout.addWidget(self.unit1box)
        self.box1layout.addWidget(self.motion1box)

    def create_unit1box(self):
        self.unit1box=QGroupBox()
        self.unit1layout=QVBoxLayout()
        self.unit1box.setLayout(self.unit1layout)

        self.unit1menu=QComboBox()
        self.unit1menu.addItem('encoder count')
        self.unit1menu.addItem('motor step')
        self.unit1menu.addItem('mm')
        self.unit1menu.addItem('\u03BCm')
        self.unit1menu.addItem('in')
        self.unit1menu.addItem('mIn')
        self.unit1menu.addItem('\u03BCIn')
        self.unit1menu.addItem('deg')
        self.unit1menu.addItem('grad')
        self.unit1menu.addItem('rad')
        self.unit1menu.addItem('mRad')
        self.unit1menu.addItem('\u03BCRad')

        self.unit1=self.newport.get_units(1)
        if self.unit1[0]=='u':
            self.unit1text='\u03BC'+self.unit1[1:]
        else:
            self.unit1text=self.unit1

        self.unit1label=QLabel(self.unit1text)

        self.unit1button=QPushButton("Set Unit")
        self.unit1button.clicked.connect(self.on_unit1_clicked)

        # encoder resolution?

        self.unit1layout.addWidget(self.unit1label)
        self.unit1layout.addWidget(self.unit1menu)
        self.unit1layout.addWidget(self.unit1button)


    def create_motion1box(self):
        self.motion1box=QGroupBox()
        self.motion1layout=QGridLayout()
        self.motion1box.setLayout(self.motion1layout)

        self.create_motor1box()
        self.create_stop1box()
        #self.create_indef1box()
        self.create_pos1box()
        #self.create_vel1box()
        #self.create_accel1box()

        self.motion1layout.addWidget(self.motor1box,0,0)
        self.motion1layout.addWidget(self.stop1box,1,0)
        #self.motion1layout.addWidget(self.indef1box,1,0)
        self.motion1layout.addWidget(self.pos1box,0,1,2,1)
        #self.motion1layout.addWidget(self.vel1box,2,0,1,2)
        #self.motion1layout.addWidget(self.accel1box,3,0,1,2)

    def create_motor1box(self):
        self.motor1box=QGroupBox()
        self.motor1layout=QVBoxLayout()
        self.motor1box.setLayout(self.motor1layout)

        self.motor1disp=QLabel()
        self.motor1disp.setAlignment(Qt.AlignCenter)
        self.motor1disp.setFrameShape(QFrame.StyledPanel)

        self.motor1on=self.newport.is_motor_on(1)
        self.newport.wait_time(wait)

        if self.motor1on:
            self.motor1disp.setText("Motor is On")
            self.motor1disp.setStyleSheet('background:limegreen')
        else:
            self.motor1disp.setText("Motor is Off")
            self.motor1disp.setStyleSheet('background:red')

        self.motor1button=QPushButton("Toggle Motor On/Off")
        self.motor1button.clicked.connect(lambda: self.toggle_motor(1))

        self.motor1layout.addWidget(self.motor1disp)
        self.motor1layout.addWidget(self.motor1button)

    def create_stop1box(self):
        self.stop1box=QGroupBox()
        self.stop1layout=QVBoxLayout()
        self.stop1box.setLayout(self.stop1layout)

        self.stop1disp=QLabel()
        self.stop1disp.setAlignment(Qt.AlignCenter)
        self.stop1disp.setFrameShape(QFrame.StyledPanel)
        
        self.motion1done=self.newport.is_motion_done(1)
        self.newport.wait_time(wait)

        if self.motion1done:
            self.stop1disp.setText("Motion Complete")
            self.stop1disp.setStyleSheet("background:limegreen")
        else:
            self.stop1disp.setText("Motion Incomplete")
            self.stop1disp.setStyleSheet("background:red")

        self.stop1button=QPushButton("Stop Motion")
        self.stop1button.clicked.connect(lambda: self.newport.stop_motion(1))

        self.stop1layout.addWidget(self.stop1disp)
        self.stop1layout.addWidget(self.stop1button)

    def create_indef1box(self):
        self.indef1box=QGroupBox()
        self.indef1layout=QGridLayout()

    def create_pos1box(self):
        self.pos1box=QGroupBox()
        self.pos1layout=QGridLayout()
        self.pos1box.setLayout(self.pos1layout)

        self.despos1label=QLabel("Desired Position")
        self.despos1disp=QLCDNumber()
        self.despos1=self.newport.get_des_pos(1)
        self.despos1disp.display(self.despos1)
        self.newport.wait_time(wait)

        self.abs1edit=QLineEdit()
        self.abs1button=QPushButton("Set Absolute Position")
        self.abs1button.clicked.connect(self.on_abs1_clicked)

        self.rel1edit=QLineEdit()
        self.rel1button=QPushButton("Move (Relative)")
        self.rel1button.clicked.connect(self.on_rel1_clicked)

        self.ll1edit=QLineEdit()
        self.ll1button=QPushButton("Set Left Limit")
        self.ll1button.clicked.connect(self.on_ll1_clicked)
        self.rl1edit=QLineEdit()
        self.rl1button=QPushButton("Set Right Limit")
        self.rl1button.clicked.connect(self.on_rl1_clicked)

        self.pos1layout.addWidget(self.despos1label,0,0,1,2)
        self.pos1layout.addWidget(self.despos1disp,1,0,1,2)
        self.pos1layout.addWidget(self.abs1edit,2,0)
        self.pos1layout.addWidget(self.abs1button,3,0)
        self.pos1layout.addWidget(self.rel1edit,2,1)
        self.pos1layout.addWidget(self.rel1button,3,1)
        self.pos1layout.addWidget(self.ll1edit,4,0)
        self.pos1layout.addWidget(self.rl1edit,4,1)
        self.pos1layout.addWidget(self.ll1button,5,0)
        self.pos1layout.addWidget(self.rl1button,5,1)

    def create_vel1box(self):
        self.vel1box=QGroupBox()
        self.vel1layout=QGridLayout()
        self.vel1box.setLayout(self.vel1layout)

        self.desvel1label=QLabel("Desired Velocity")
        self.desvel1disp=QLCDNumber()
        self.desvel1=self.newport.get_des_vel(1)
        self.desvel1disp.display(self.desvel1)
        self.actvel1label=QLabel("Actual Velocity")
        self.actvel1disp=QLCDNumber()
        self.actvel1=self.newport.get_act_vel(1)
        self.actvel1disp.display(self.actvel1)

        self.vel1edit=QLineEdit()
        self.vel1button=QPushButton("Set Velocity")
        self.vel1button.clicked.connect(self.on_vel1_clicked)

        self.maxvel1disp=QLCDNumber()
        self.maxvel1=self.newport.get_max_vel(1)
        self.maxvel1disp.display(self.maxvel1)
        self.maxvel1edit=QLineEdit()
        self.maxvel1button=QPushButton("Set Max Velocity")
        self.maxvel1button.clicked.connect(self.on_maxvel1_clicked)

        self.vel1layout.addWidget(self.desvel1label,0,0)
        self.vel1layout.addWidget(self.desvel1disp,1,0,2,1)
        self.vel1layout.addWidget(self.actvel1label,0,1)
        self.vel1layout.addWidget(self.actvel1disp,1,1,2,1)
        self.vel1layout.addWidget(self.vel1edit,1,2)
        self.vel1layout.addWidget(self.vel1button,2,2)
        self.vel1layout.addWidget(self.maxvel1disp,0,3)
        self.vel1layout.addWidget(self.maxvel1edit,1,3)
        self.vel1layout.addWidget(self.maxvel1button,2,3)

    def create_accel1box(self):
        self.accel1box=QGroupBox()
        self.accel1layout=QGridLayout()
        self.accel1box.setLayout(self.accel1layout)

        self.accel1disp=QLCDNumber()
        self.accel1=self.newport.get_accel(1)
        self.accel1disp.display(self.accel1)
        self.accel1edit=QLineEdit()
        self.accel1button=QPushButton("Set Acceleration")
        self.accel1button.clicked.connect(self.on_accel1_clicked)

        self.decel1disp=QLCDNumber()
        self.decel1=self.newport.get_decel(1)
        self.decel1disp.display(self.decel1)
        self.decel1edit=QLineEdit()
        self.decel1button=QPushButton("Set Deceleration")
        self.decel1button.clicked.connect(self.on_decel1_clicked)

        self.maxaccel1disp=QLCDNumber()
        self.maxaccel1=self.newport.get_max_accel(1)
        self.maxaccel1disp.display(self.maxaccel1)
        self.maxaccel1edit=QLineEdit()
        self.maxaccel1button=QPushButton("Set Max Accel/Decel")
        self.maxaccel1button.clicked.connect(self.on_maxaccel1_clicked)

        self.accel1layout.addWidget(self.accel1disp,0,0)
        self.accel1layout.addWidget(self.accel1edit,1,0)
        self.accel1layout.addWidget(self.accel1button,2,0)
        self.accel1layout.addWidget(self.decel1disp,0,1)
        self.accel1layout.addWidget(self.decel1edit,1,1)
        self.accel1layout.addWidget(self.decel1button,2,1)
        self.accel1layout.addWidget(self.maxaccel1disp,0,2)
        self.accel1layout.addWidget(self.maxaccel1edit,1,2)
        self.accel1layout.addWidget(self.maxaccel1button,2,2)


    def check_unit(self):
        if self.unit1 != self.newport.get_units(1):
            self.unit1=self.newport.get_units(1)
            if self.unit1[0]=='u':
                self.unit1text='\u03BC'+self.unit1[1:]
            else:
                self.unit1text=self.unit1
            self.unit1label.setText(self.unit1text)

    def check_motor(self):
        if self.motor1on != self.newport.is_motor_on(1):
            self.newport.wait_time(wait)
            self.motor1on=self.newport.is_motor_on(1)
            if self.motor1on:
                self.motor1disp.setText("Motor is On")
                self.motor1disp.setStyleSheet('background:limegreen')
            else:
                self.motor1disp.setText("Motor is Off")
                self.motor1disp.setStyleSheet('background:red')
        self.newport.wait_time(wait)

    def check_motion(self):
        if self.motion1done != self.newport.is_motion_done(1):
            self.newport.wait_time(wait)
            self.motion1done=self.newport.is_motion_done(1)
            if self.motion1done:
                self.stop1disp.setText("Motion Complete")
                self.stop1disp.setStyleSheet("background:limegreen")
            else:
                self.stop1disp.setText("Motion Incomplete")
                self.stop1disp.setStyleSheet("background:red")
        self.newport.wait_time(wait)

    def check_desired(self):
        if self.despos1 != self.newport.get_des_pos(1):
            self.newport.wait_time(wait)
            self.despos1=self.newport.get_des_pos(1)
            self.despos1disp.display(self.despos1)
        """if self.desvel1 != self.newport.get_des_vel(1):
            self.desvel1=self.newport.get_des_vel(1)
            self.desvel1disp.display(self.desvel1)"""
        self.newport.wait_time(wait)
    
    def check_actual(self):
        if self.actvel1 !=self.newport.get_act_vel(1):
            self.actvel1=self.newport.get_act_vel(1)
            self.actvel1disp.display(self.actvel1)

    def check_max(self):
        if self.maxvel1 != self.newport.get_max_vel(1):
            self.maxvel1=self.newport.get_max_vel(1)
            self.maxvel1disp.display(self.maxvel1)
        if self.maxaccel1 != self.newport.get_max_accel(1):
            self.maxaccel1=self.newport.get_max_accel(1)
            self.maxaccel1disp.display(self.maxaccel1)

    def check_accel(self):
        if self.accel1 != self.newport.get_accel(1):
            self.accel1=self.newport.get_accel(1)
            self.accel1disp.display(self.accel1)
        if self.decel1 != self.newport.get_decel(1):
            self.decel1=self.newport.get_decel(1)
            self.decel1disp.display(self.decel1)

    def on_abort_clicked(self):
        # some sort of alert/check?
        self.newport.abort_motion()
        self.newport.wait_time(wait)

    def on_wait_clicked(self):
        wait=self.wait_edit.text()
        self.newport.wait_time(wait)
        self.newport.wait_time(wait)

    def toggle_motor(self,axis):
        if self.newport.is_motor_on(axis):
            self.newport.wait_time(wait)
            self.newport.motor_off(axis)
        else: 
            self.newport.wait_time(wait)
            self.newport.motor_on(axis)
        self.newport.wait_time(wait)

    def on_unit1_clicked(self):
        unit=self.unit1menu.currentText()
        if unit[0]=="\u03BC":
            unit=unit.replace("\u03BC","u")
        self.newport.set_units(1,unit)

    def on_abs1_clicked(self):
        pos=self.abs1edit.text()
        self.newport.move_abs_pos(1,pos)
        self.newport.wait_time(wait)

    def on_rel1_clicked(self):
        pos=self.rel1edit.text()
        self.newport.move_rel_pos(1,pos)
        self.newport.wait_time(wait)

    def on_ll1_clicked(self):
        lim=self.ll1edit.text()
        self.newport.set_left_lim(1,lim)
        self.newport.wait_time(wait)

    def on_rl1_clicked(self):
        lim=self.rl1edit.text()
        self.newport.set_right_lim(1,lim)
        self.newport.wait_time(wait)

    def on_vel1_clicked(self):
        vel=self.vel1edit.text()
        self.newport.set_vel(1,vel)

    def on_maxvel1_clicked(self):
        vel=self.maxvel1edit.text()
        self.newport.set_max_vel(1,vel)

    def on_accel1_clicked(self):
        accel=self.accel1edit.text()
        self.newport.set_accel(1,accel)

    def on_decel1_clicked(self):
        decel=self.decel1edit.text()
        self.newport.set_decel(1,decel)

    def on_maxaccel1_clicked(self):
        accel=self.maxaccel1edit.text()
        self.newport.set_max_accel(accel)

if __name__=="__main__":
    app=QApplication(sys.argv)
    app.setStyle('Fusion')
    wg=WidgetGallery()
    wg.show()
    sys.exit(app.exec_())

