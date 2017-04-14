import sys
import logging
from PyQt4 import QtGui
from PyQt4 import QtCore

class LeftDockFrame(QtGui.QFrame):
    def __init__(self):
        super(LeftDockFrame, self).__init__()
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        self.dict_tree = {'Boundary Parts':{}, 'Volume Parts':{}}
        self.vtk_processor = None #set later by processor
        tree_widget = QtGui.QTreeWidget()
        vbox.addWidget(tree_widget)
        tree_widget.setColumnCount(1)
        tree_widget.setHeaderLabel('Mesh-Tree')
        it1 = QtGui.QTreeWidgetItem(tree_widget)
        it1.setText(0, 'Volume Parts')
        #it1.setCheckState(QtGui.QTreeWidgetItem.Checked)
        it2 = QtGui.QTreeWidgetItem(tree_widget)
        it2.setText(0, 'Boundary Parts')
        tree_widget.addTopLevelItem(it1)
        tree_widget.addTopLevelItem(it2)
        self.tree_widget = tree_widget
        self.root_vpart_item = it1
        self.root_bpart_item = it2

        # Lower Switch box
        label = QtGui.QLabel("Set Boundary Type")
        label.setFixedSize(200, 20)
        vbox.addWidget(label)

        hbox = QtGui.QHBoxLayout()
        vbox.addLayout(hbox)
        combo_box = QtGui.QComboBox()
        combo_box.setFixedSize(180, 28)
        combo_box.setEnabled(False)
        edit_button = QtGui.QPushButton("Edit")
        combo_box.addItem('Boundary Type')
        combo_box.addItem('Inlet')
        combo_box.addItem('Outlet')
        combo_box.addItem('Wall')
        combo_box.addItem('Symmetric')
        combo_box.addItem('Periodic')

        hbox.addWidget(combo_box)
        hbox.addWidget(edit_button)

        tree_widget.itemChanged.connect(self.item_changed_slot)

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_changed_slot(self, item, column):
        part_name = str(item.text(column))
        if part_name not in self.dict_tree['Boundary Parts'].keys() and \
           part_name not in self.dict_tree['Volume Parts'].keys():
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
            rt = self.tree_widget.findItems(root_name, QtCore.Qt.MatchExactly)[0]
            for name in part_names:
                assert name not in self.dict_tree[root_name] # fail when boundary part has the same name
                self.dict_tree[root_name][name] = None
                it = QtGui.QTreeWidgetItem(rt)
                it.setText(0, name)
                if  root_name == 'Volume Parts':
                    it.setCheckState(0, QtCore.Qt.Unchecked)
                else:
                    it.setCheckState(0, QtCore.Qt.Checked)

    @QtCore.pyqtSlot()
    def clear_parts_slot(self):
        self.dict_tree = {'Boundary Parts':{}, 'Volume Parts':{}}
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
        logging.log(content)
