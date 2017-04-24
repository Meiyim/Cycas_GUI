import logging
import re
from PyQt4 import QtCore
from PyQt4 import QtGui

class VectorInputor(QtGui.QTextEdit):
    did_set_vec_signal = QtCore.pyqtSignal(tuple)
    def __init__(self, parent = None, **kwargs):
        super(VectorInputor, self).__init__(parent)
        self.textChanged.connect(self.did_change_text_slot)
        self.format_pattern = re.compile(r'^(\d*\.?\d*),(\d*\.?\d*),(\d*\.?\d*)$')
        tup = kwargs.get('init')
        if tup is not None:
            self.setText(str(tup[0])+','+str(tup[1])+','+str(tup[2]))
        else:
            self.setText(',,')
        self.vec = (0, 0, 0)

    @QtCore.pyqtSlot()
    def did_change_text_slot(self):
        text = str(self.toPlainText())
        match = self.format_pattern.match(text)
        cursor = self.textCursor()
        if not match:
            if text.count(',') < 2: # because of delete ','
                cursor.insertText(',')
                cursor.movePosition(QtGui.QTextCursor.Left)
                self.setTextCursor(cursor)
            elif text.count(',') > 2: # because of insert ','
                if text[cursor.position()] == ',':
                    cursor.deleteChar()
                else:
                    cursor.deletePreviousChar()
            else: # illegal char inserted
                cursor.deletePreviousChar()
        elif match.group(1).isdigit() and match.group(2).isdigit() and match.group(3).isdigit():
            self.vec = (float(match.group(1)), float(match.group(2)), float(match.group(3)))
            self.did_set_vec_signal.emit(self.vec)
        else:
            pass

class BCDialog(QtGui.QDialog):
    did_set_signal = QtCore.pyqtSignal(dict)
    def __init__(self, bctype, parent = None, **kwargs):
        super(BCDialog, self).__init__(parent)
        vbox = QtGui.QVBoxLayout()
        self.info = {}
        if kwargs.get('title') is not None:
            self.setWindowTitle(kwargs['title'])
        if bctype == 1: # wall
            hbox = QtGui.QHBoxLayout()
            btm1 = QtGui.QRadioButton('slip wall')
            btm1.toggled.connect(self.did_set_wall_type)
            btm2 = QtGui.QRadioButton('no slip wall')
            init_status = kwargs.get('slipwall')
            if init_status is not None:
                btm1.setChecked(init_status)
                btm2.setChecked(not init_status)
            hbox.addWidget(btm1)
            hbox.addWidget(btm2)
            vbox.addLayout(hbox)
        elif bctype == 2: # inlet
            hbox = QtGui.QHBoxLayout()
            self.vector_input = VectorInputor(self, init=kwargs.get('init'))
            self.vector_input.did_set_vec_signal.connect(self.did_set_vector)
            self.vector_input.setFixedHeight(30)
            hbox.addWidget(self.vector_input)
            vbox.addLayout(hbox)
        elif bctype == 3: # outlet noting to config
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(QtGui.QLabel('Outlet noting to be done'))
            vbox.addLayout(hbox)
        elif bctype == 4: # symmetric
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(QtGui.QLabel('Symmetry noting to be done'))
            vbox.addLayout(hbox)
        elif bctype == 5: # periodic
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(QtGui.QLabel('To be implement?'))
            vbox.addLayout(hbox)
        hbox = QtGui.QHBoxLayout()
        btm = QtGui.QPushButton('OK')
        btm.clicked.connect(self.accept)
        hbox.addWidget(btm)
        btm = QtGui.QPushButton('Cancel')
        btm.clicked.connect(self.reject)
        hbox.addWidget(btm)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    @QtCore.pyqtSlot()
    def accept(self):
        super(BCDialog, self).accept()
        self.did_set_signal.emit(self.info)

    @QtCore.pyqtSlot(bool)
    def did_set_wall_type(self, is_slip_wall):
        self.info['slip wall'] = is_slip_wall
    @QtCore.pyqtSlot(tuple) # vector picked for inlet bc
    def did_set_vector(self, vector):
        self.info['inlet vec'] = vector
