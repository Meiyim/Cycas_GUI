import logging
from PyQt4 import QtCore
from PyQt4 import QtGui

class VectorInputor(QtGui.QTextEdit):
    new_text_signal = QtCore.pyqtSignal(tuple)
    def __init__(self, parent = None):
        super(VectorInputor, self).__init__(parent)
        self.textChanged.connect(self.did_change_text_slot)
        self.setText(',,')
        self.last_text = ''

    @QtCore.pyqtSlot()
    def did_change_text_slot(self):
        text = self.toPlainText()
        if not text.isdigit():
            self.setText(self.last_text)
            return
        elif text.count(',') > 2:
            print 'wrong vector: %s' % text
            self.undo()
        elif text.count(',') < 2:
            print 'wrong vector: %s' % text
            self.setText(self.last_text)


        self.new_text_signal.emit(text)
        self.last_text = text

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
