from PyQt4 import QtGui
from PyQt4 import QtCore

class LeftDockFrame(QtGui.QTreeWidget):
    def __init__(self):
        super(LeftDockFrame, self).__init__()
        self.setColumnCount(2)
        self.setHeaderLabels(['part', 'nelement / nvertex'])
        it1 = QtGui.QTreeWidgetItem(self)
        it1.setText(0, 'root')
        #it1.setCheckState(QtGui.QTreeWidgetItem.Checked)
        it2 = QtGui.QTreeWidgetItem(self)
        it2.setText(0, 'root2')
        for i in xrange(0, 3):
            child = QtGui.QTreeWidgetItem(it1)
            child.setText(0, 'child%d' % i)
            child.setText(1, 'conf%d' % i)
        self.addTopLevelItem(it1)
        self.addTopLevelItem(it2)


class LeftDockFrame___(QtGui.QFrame):
    def __init__(self):
        super(LeftDockFrame___, self).__init__()
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.line_factory())
        vbox.addLayout(self.line_factory())
        vbox.addLayout(self.line_factory())
        vbox.addStretch(100)
        self.setLayout(vbox)

    def line_factory(self):
        ret = QtGui.QHBoxLayout()
        content = QtGui.QLabel('hello world')
        content.setFixedSize(200, 30)
        ret.addWidget(content)
        return ret


class LeftDockFrame2(QtGui.QFrame):
    def __init__(self):
        super(LeftDockFrame2, self).__init__()
        vbox = QtGui.QVBoxLayout()
        vbox.addLayout(self.line_factory())
        vbox.addLayout(self.line_factory())
        vbox.addLayout(self.line_factory())
        vbox.addStretch(100)
        self.setLayout(vbox)

    def line_factory(self):
        ret = QtGui.QHBoxLayout()
        content = QtGui.QLabel('ouput configure...')
        content.setFixedSize(200, 30)
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
