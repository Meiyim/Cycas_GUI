import sys
import logging
from PyQt4 import QtGui
from PyQt4 import QtCore

class LeftDockFrame(QtGui.QTreeWidget):

    def __init__(self):
        super(LeftDockFrame, self).__init__()
        self.setColumnCount(1)
        self.setHeaderLabel('Mesh-Tree')
        self.dict_tree = {'Boundary Parts':[], 'Volume Parts':[]}
        it1 = QtGui.QTreeWidgetItem(self)
        it1.setText(0, 'Volume Parts')
        #it1.setCheckState(QtGui.QTreeWidgetItem.Checked)
        it2 = QtGui.QTreeWidgetItem(self)
        it2.setText(0, 'Boundary Parts')
        self.addTopLevelItem(it1)
        self.addTopLevelItem(it2)
        self.root_vpart_item = it1
        self.root_bpart_item = it2

        self.itemChanged.connect(self.item_changed_slot)
        self.vtk_processor = None #set later by processor

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_changed_slot(self, item, column):
        part_name = str(item.text(column))
        if part_name not in self.dict_tree['Boundary Parts'] and \
           part_name not in self.dict_tree['Volume Parts']:
            return

        if item.checkState(column) == QtCore.Qt.Checked:
            self.vtk_processor.activate_parts([part_name])
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            self.vtk_processor.deactivate_parts([part_name])
        else:
            assert False

    @QtCore.pyqtSlot(dict)
    def set_mesh_part_tree_slot(self, dic):
        print 'message received', dic
        for root_name, part_names in dic.iteritems():
            rt = self.findItems(root_name, QtCore.Qt.MatchExactly)[0]
            for name in part_names:
                self.dict_tree[root_name].append(name)
                it = QtGui.QTreeWidgetItem(rt)
                it.setText(0, name)
                if  root_name == 'Volume Parts':
                    it.setCheckState(0, QtCore.Qt.Unchecked)
                else:
                    it.setCheckState(0, QtCore.Qt.Checked)

    @QtCore.pyqtSlot()
    def clear_parts_slot(self):
        self.dict_tree = {'Boundary Parts':[], 'Volume Parts':[]}
        self.root_vpart_item.takeChildren()
        self.root_bpart_item.takeChildren()

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
        print (content)
