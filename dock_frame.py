from PyQt4 import QtGui
from PyQt4 import QtCore

class LeftDockFrame(QtGui.QTreeWidget):
    def __init__(self):
        super(LeftDockFrame, self).__init__()
        self.setColumnCount(1)
        self.setHeaderLabel('Mesh-Tree')
        it1 = QtGui.QTreeWidgetItem(self)
        it1.setText(0, 'Volume Parts')
        #it1.setCheckState(QtGui.QTreeWidgetItem.Checked)
        it2 = QtGui.QTreeWidgetItem(self)
        it2.setText(0, 'Boundary Parts')
        self.addTopLevelItem(it1)
        self.addTopLevelItem(it2)
        self.root_vpart = it1
        self.root_bpart = it2

    @QtCore.pyqtSlot(dict)
    def set_mesh_part_tree_slot(self, dic):
        for root_name, part_names in dic.iteritems():
            rt = self.findItems(root_name, QtCore.Qt.MatchExactly)[0]
            for name in part_names:
                it = QtGui.QTreeWidgetItem(rt)
                it.setText(0, name)
                it.setCheckState(0, QtCore.Qt.Checked)

    @QtCore.pyqtSlot()
    def clear_parts_slot(self):
        self.clear()
        self.addTopLevelItem(self.root_vpart)
        self.addTopLevelItem(self.root_bpart)

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
