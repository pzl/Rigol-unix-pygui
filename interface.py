#!/usr/bin/python

import sys
import os
import time
import random
from PySide import QtGui, QtCore

class Rigol:

	def __init__(self, path):
		self.path = path
		self.conn = True
		try:
			self.FILE = os.open(path, os.O_RDWR)
		except OSError as e:
			print >> sys.stderr, "Incorrect path, or device not on: ", e
			self.conn = False

		self.name = self.getName()
		self.gui = Scope(self)

	def write(self, command):
		if self.conn:
			try:
				os.write(self.FILE, command)
			except OSError as e:
				self.conn = False
				print >> sys.stderr, "Write error: ", e


	def read(self, length=300):
		if self.conn:
			try:
				return os.read(self.FILE, length)
			except OSError as e:
				if e.args[0] == 110:
					print >> sys.stderr, "Read Error: Read timeout"
				else:
					print >> sys.stderr, "Read Error: ", e
				return ""

	def getName(self):
		if self.conn:
			self.write("*IDN?")
			return self.read(300)
		else:
			return "Rigol Oscilloscope [Disconnected]"

	def sendReset(self):
		self.write("*RST")

	def close(self):
		if self.conn:
			self.write(":key:lock dis")
			os.close(self.FILE)

	def keypress(self, key):
		self.write(":key:%s" % key)



class Scope(QtGui.QMainWindow):
	
	def __init__(self, manager):
		super(Scope, self).__init__()

		self.manager = manager

		self.setWindowTitle(manager.name)
		self.setMinimumSize(400,200)
		self.resize(900,450)
		self.center()
		
		self.statusBar().showMessage('Ready')

		exitAction = QtGui.QAction(QtGui.QIcon('exit.png'), '&Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.setStatusTip('Exit Application')
		exitAction.triggered.connect(self.close)

		menubar = self.menuBar()
		fileMenu = menubar.addMenu('&File')
		fileMenu.addAction(exitAction)
		
		
		self.chassis = Chassis(self)
		

		
		self.setCentralWidget(self.chassis)


		"""
		#QtGui.QToolTip.setFont(QtGui.QFont('SansSerif',10))
		#self.setToolTip('This is a <b>QWidget</b> widget')
		#lcd = QtGui.QLCDNumber(self)
		#sld = QtGui.QSlider(QtCore.Qt.Horizontal, self)
		#vbox = QtGui.QVBoxLayout()
		#vbox.addWidget(lcd)
		#vbox.addWidget(sld)
		#self.setLayout(vbox)
		#sld.valueChanged.connect(lcd.display)
		"""
		self.show()
		
	def center(self):
		
		qr = self.frameGeometry()
		cp = QtGui.QDesktopWidget().availableGeometry().center()
		qr.moveCenter(cp)
		self.move(qr.topLeft())

	def closeEvent(self, event):
		self.manager.close()
		event.accept()
		

class Chassis(QtGui.QFrame):
	def __init__(self, parent):
		super(Chassis, self).__init__()
		self.parent = parent

		#POSITION GRID

		self.v_label = QtGui.QLabel('VERTICAL')
		self.h_label = QtGui.QLabel('HORIZONTAL')
		self.trigger_label = QtGui.QLabel('TRIGGER')

		self.v_label.setAlignment(QtCore.Qt.AlignCenter)
		self.v_label.setMaximumHeight(25)
		self.h_label.setAlignment(QtCore.Qt.AlignCenter)
		self.trigger_label.setAlignment(QtCore.Qt.AlignCenter)

		self.v_pos_label = QtGui.QLabel('^ Position')
		self.h_pos_label = QtGui.QLabel('< Position >')
		self.trigger_pos_label = QtGui.QLabel('^ Level')

		self.v_pos_label.setMaximumHeight(25)

		self.v_scale_label = QtGui.QLabel('^ Scale')
		self.h_scale_label = QtGui.QLabel('< Scale >')

		self.trigger_pos = Dial('trig_lvl','small',self)
		self.h_pos = Dial('h_pos','small',self)
		self.v_pos = Dial('v_pos','small',self)
		self.h_scale = Dial('h_scale','big',self)
		self.v_scale = Dial('v_scale','big',self)


		self.chan_off = Btn('OFF','off',self)
		self.h_menu = Btn('MENU','mnutime',self)
		self.trigger_menu = Btn('MENU','mnutrig',self)
		self.trigger_50 = Btn('50%','Trig%50',self)
		self.force = Btn('&FORCE','forc',self)





		self.pos_grid = QtGui.QGridLayout()
		self.pos_grid.setSpacing(2)
		self.pos_grid.addWidget(self.v_label,0,0)
		self.pos_grid.addWidget(self.h_label,0,1)
		self.pos_grid.addWidget(self.trigger_label,0,2)
		self.pos_grid.addWidget(self.v_pos_label,1,0)
		self.pos_grid.addWidget(self.h_pos_label,1,1)
		self.pos_grid.addWidget(self.trigger_pos_label,1,2)
		self.pos_grid.addWidget(self.v_pos,2,0)
		self.pos_grid.addWidget(self.h_pos,2,1)
		self.pos_grid.addWidget(self.trigger_pos,2,2)
		self.pos_grid.addWidget(self.chan_off,3,0)
		self.pos_grid.addWidget(self.h_menu,3,1)
		self.pos_grid.addWidget(self.trigger_menu,3,2)
		self.pos_grid.addWidget(self.v_scale_label,4,0)
		self.pos_grid.addWidget(self.h_scale_label,4,1)
		self.pos_grid.addWidget(self.trigger_50,4,2)
		self.pos_grid.addWidget(self.v_scale,5,0)
		self.pos_grid.addWidget(self.h_scale,5,1)
		self.pos_grid.addWidget(self.force,5,2)

		self.pos_grid.setSpacing(5)
		self.pos_grid.setContentsMargins(0,0,0,0)



		# -----------------------------------------
		# TOP MENUS
		# -----------------------------------------

		self.run_ctrl_label = QtGui.QLabel('RUN CONTROL')
		self.run_ctrl_label.setMaximumHeight(25)
		self.run_ctrl_label.setAlignment(QtCore.Qt.AlignCenter)


		self.auto = Btn('AUTO','auto',self)
		self.run_stop = Btn('RUN/STOP','run',self)

		self.ctrl_btn_layout = QtGui.QHBoxLayout()
		self.ctrl_btn_layout.addWidget(self.auto)
		self.ctrl_btn_layout.addWidget(self.run_stop)
		self.ctrl_btn_layout.setSpacing(2)
		self.ctrl_btn_layout.setContentsMargins(0,0,0,0)

		self.ctrl_layout = QtGui.QVBoxLayout()
		self.ctrl_layout.addWidget(self.run_ctrl_label)
		self.ctrl_layout.addLayout(self.ctrl_btn_layout)

		self.ctrl_layout.setSpacing(2)
		self.ctrl_layout.setContentsMargins(0,0,0,0)


		self.menu_label = QtGui.QLabel('MENU')
		self.measure_menu = Btn('Measure','meas', self)
		self.acquire_menu = Btn('Acquire','acq',self)
		self.storage_menu = Btn('Storage','stor',self)
		self.cursor_menu  = Btn('Cursor','cur',self)
		self.display_menu = Btn('Display','disp',self)
		self.utility_menu = Btn('Utility','util',self)

		#self.menu_label.setStyleSheet("QLabel { }")
		self.menu_label.setMaximumHeight(25)
		self.menu_label.setAlignment(QtCore.Qt.AlignCenter)

		self.menu_layout = QtGui.QGridLayout()
		self.menu_layout.addWidget(self.menu_label,0,0,1,3)
		self.menu_layout.addWidget(self.measure_menu,1,0)
		self.menu_layout.addWidget(self.acquire_menu,1,1)
		self.menu_layout.addWidget(self.storage_menu,1,2)
		self.menu_layout.addWidget(self.cursor_menu, 2,0)
		self.menu_layout.addWidget(self.display_menu,2,1)
		self.menu_layout.addWidget(self.utility_menu,2,2)

		self.menu_layout.setSpacing(2)
		self.menu_layout.setContentsMargins(0,0,0,0)

		self.menu_frame = QtGui.QFrame()
		self.menu_frame.setLayout(self.menu_layout)
		#self.menu_frame.setStyleSheet("QFrame { border: 1px solid blue; border-radius: 8px }")

		self.prog_button_layout = QtGui.QHBoxLayout()
		self.prog_button_layout.addWidget(self.menu_frame)
		self.prog_button_layout.addLayout(self.ctrl_layout)


		self.r_panel = QtGui.QVBoxLayout()
		self.r_panel.addLayout(self.prog_button_layout)
		self.r_panel.addLayout(self.pos_grid)

		# -----------------------------------
		# center buttons
		# -----------------------------------

		self.fn_knob = Dial('func','small',self)
		self.ch1_btn = Btn('CH&1','chan1',self)
		self.ch2_btn = Btn('CH&2','chan2',self)
		self.mth_btn = Btn('MATH','math',self)
		self.ref_btn = Btn('REF','ref',self)


		self.ch1_btn.setMaximumSize(90,30)
		self.ch2_btn.setMaximumSize(90,30)
		self.mth_btn.setMaximumSize(90,30)
		self.ref_btn.setMaximumSize(90,30)

		self.center_btns = QtGui.QVBoxLayout()
		self.center_btns.addWidget(self.fn_knob)
		self.center_btns.addWidget(self.ch1_btn)
		self.center_btns.addWidget(self.ch2_btn)
		self.center_btns.addWidget(self.mth_btn)
		self.center_btns.addWidget(self.ref_btn)

		# -----------------------------------
		# soft buttons
		# -----------------------------------

		self.menu_on_off = Btn("","mnu",self)
		self.menu_on_off.setMaximumSize(20,20)
		self.menu_on_off.setToolTip("Menu On/Off")
		self.menu_on_off.setStyleSheet("QPushButton { border: 1px solid white; background-color: white; border-radius: 10px; }")

		self.f1 = Btn("","F1",self)
		self.f2 = Btn("","F2",self)
		self.f3 = Btn("","F3",self)
		self.f4 = Btn("","F4",self)
		self.f5 = Btn("","F5",self)


		self.f1.setMaximumSize(90,30)
		self.f2.setMaximumSize(90,30)
		self.f3.setMaximumSize(90,30)
		self.f4.setMaximumSize(90,30)
		self.f5.setMaximumSize(90,30)


		self.soft_buttons = QtGui.QVBoxLayout()
		self.soft_buttons.addWidget(self.menu_on_off)
		self.soft_buttons.addWidget(self.f1)
		self.soft_buttons.addWidget(self.f2)
		self.soft_buttons.addWidget(self.f3)
		self.soft_buttons.addWidget(self.f4)
		self.soft_buttons.addWidget(self.f5)




		self.screen = Screen(self)
		self.screen.getData()
		self.buttonPanel = QtGui.QHBoxLayout()
		self.buttonPanel.addLayout(self.soft_buttons)
		self.buttonPanel.addLayout(self.center_btns)
		self.buttonPanel.addLayout(self.r_panel)

		hbox = QtGui.QHBoxLayout()
		hbox.addWidget(self.screen)
		hbox.addLayout(self.buttonPanel)
		self.setLayout(hbox)
		

class Screen(QtGui.QFrame):
	def __init__(self, parent):
		super(Screen,self).__init__()

		self.setGeometry(150,20,100,100)
		self.setStyleSheet("QWidget { background-color: red }")

	def getData(self):
		self.thread = Fetch()
		self.thread.onData.connect(self.recvData, QtCore.Qt.QueuedConnection)
		self.thread.start()

	def recvData(self, data):
		self.setStyleSheet("QWidget { background-color: rgb(%s, 120, 120) }" % data)


class Fetch(QtCore.QThread):
	onData = QtCore.Signal(object)

	def __init__(self):
		super(Fetch, self).__init__()

	def run(self):
		while True:
			self.data = self.get()
			self.onData.emit(self.data)
			time.sleep(0.05)

	def get(self):
		return random.randint(0,255)



class Btn(QtGui.QPushButton):
	def __init__(self, txt, name, parent):
		super(Btn, self).__init__(txt)
		self.parent = parent
		self.clicked.connect(self.clickEvent)
		self.name = name

	def setName(self, name):
		self.name = name

	def getName(self, name):
		return self.name

	def clickEvent(self):
		self.parent.parent.manager.keypress(self.name)


class Dial(QtGui.QDial):
	def __init__(self, name, size, parent):
		super(Dial, self).__init__()
		self.parent = parent
		self.name = name
		self.size = size
		self.val = self.value() % 99
		if size == 'big':
			self.setMaximumSize(80,80)
			self.setMinimumSize(50,50)
		else:
			self.setMaximumSize(50,50)
			self.setMinimumSize(30,30)

		self.setNotchesVisible(1)
		self.setNotchTarget(10)
		self.setWrapping(1)
		self.setSingleStep(1)
		self.valueChanged.connect(self.onChange)


	def setName(self, name):
		self.name = name

	def getName(self, name):
		return self.name

	def onChange(self):
		val = self.value() % 99
		if self.val > val:
			if self.val == 98 and val ==0:
				self.up()
			else:
				self.down()
		elif self.val < 10 and val > 90:
			self.down()
		elif self.val == val:
			"""no change"""
		else:
			self.up()

		self.val = val

	def up(self):
		if self.name.lower() == "func" or self.name.lower() == "function":
			self.parent.parent.manager.keypress("+%s" % self.name)
		else:
			self.parent.parent.manager.keypress("%s_inc" % self.name)

	def down(self):
		if self.name.lower() == "func" or self.name.lower() == "function":
			self.parent.parent.manager.keypress("-%s" % self.name)
		else:
			self.parent.parent.manager.keypress("%s_dec" % self.name)


def main():
	
	app = QtGui.QApplication(sys.argv)
	myScope = Rigol("/dev/usbtmc0")
	sys.exit(app.exec_())


if __name__ == '__main__':
	main()