from PyQt4 import QtGui
from PyQt4 import QtCore

class LeftDockFrame(QtGui.QFrame):
    def __init__(self):
        super(LeftDockFrame, self).__init__()
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.line_factory())
        vbox.addLayout(self.line_factory())
        vbox.addLayout(self.line_factory())
        vbox.addStretch(100)
        self.setLayout(vbox)

    def line_factory(self):
        ret = QtGui.QHBoxLayout()
        content = QtGui.QLabel('hello world')
        content.setFixedSize(100, 30)
        ret.addWidget(content)
        return ret

class CommandlineWidget(QtGui.QTextEdit):
    def __init__(self, content):
        super(CommandlineWidget, self).__init__(content)
        self.setReadOnly(True)
        self.history_log = []
    def log(self, content):
        self.history_log.append(content)
        self.append(content)
