import logging
import re
from PyQt4 import QtCore
from PyQt4 import QtGui

class VectorInputor(QtGui.QTextEdit):
    new_text_signal = QtCore.pyqtSignal(tuple)
    def __init__(self, parent = None):
        super(VectorInputor, self).__init__(parent)
        self.textChanged.connect(self.did_change_text_slot)
        self.format_pattern = re.compile(r'^(\d*\.?\d*),(\d*\.?\d*),(\d*\.?\d*)$')
        self.setText(',,')
        self.vec = (0, 0, 0)

    @QtCore.pyqtSlot()
    def did_change_text_slot(self):
        text = str(self.toPlainText())
        print text
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
            self.new_text_signal.emit(self.vec)
        else:
            pass

class BCDialog(QtGui.QDialog):
    def __init__(self, bctype, parent = None, **kwargs):
        super(BCDialog, self).__init__(parent)
        vbox = QtGui.QVBoxLayout()
        self.info = None
        if kwargs.get('title') is not None:
            self.setWindowTitle(kwargs['title'])
        if bctype == 1: # wall
            hbox = QtGui.QHBoxLayout()
            hbox.addWidget(QtGui.QRadioButton('no slip wall'))
            hbox.addWidget(QtGui.QRadioButton('slip wall'))
            vbox.addLayout(hbox)
        elif bctype == 2: # inlet
            hbox = QtGui.QHBoxLayout()
            te = VectorInputor(self)
            te.new_text_signal.connect(self.did_set_vector)
            te.setFixedHeight(30)
            hbox.addWidget(te)
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

    @QtCore.pyqtSlot(tuple)
    def did_set_vector(self, vector):
        self.info = vector
