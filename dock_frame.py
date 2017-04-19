import sys
import logging
from PyQt4 import QtGui
from PyQt4 import QtCore

# utility
section_header_font_sytle = "QLabel{font-size:13px;font-weight:bold;font-family:Roman times;}"

def insert_section_header(header, vbox):
    la = QtGui.QLabel(header)
    la.setStyleSheet(section_header_font_sytle)
    la.setFixedHeight(15)
    vbox.addWidget(la)

class MaterialConfFrame(QtGui.QFrame):
    def __init__(self):
        super(MaterialConfFrame, self).__init__()

    def generate_input_card(self):
        return ['']

class MeshConfFrame(QtGui.QFrame):
    def __init__(self):
        super(MeshConfFrame, self).__init__()
        self.setFixedWidth(300)
        vbox = QtGui.QVBoxLayout()
        self.scale_mod = 0  # 0 -- no scale, 1 -- exact size, 2 -- scale ratio
        # row
        insert_section_header('Input Config', vbox)
        hbox = QtGui.QHBoxLayout()
        btm = QtGui.QPushButton('Import Mesh')
        btm.setFixedSize(100, 30)
        hbox.addWidget(btm)
        te = QtGui.QTextEdit()
        te.setReadOnly(True)
        te.setFixedHeight(30)
        hbox.addWidget(te)
        vbox.addLayout(hbox)
        # row
        insert_section_header('Mesh Quality', vbox)
        hbox = QtGui.QHBoxLayout()
        btm = QtGui.QPushButton('Check Quality')
        hbox.addWidget(btm)
        btm = QtGui.QPushButton('Quality Report')
        hbox.addWidget(btm)
        vbox.addLayout(hbox)
        # row
        insert_section_header('Size Scale', vbox)
        hbox = QtGui.QHBoxLayout()
        la = QtGui.QLabel('Mesh Size:')
        la.setFixedSize(100, 50)
        hbox.addWidget(la)
        self.mesh_size_label = QtGui.QLabel('(Xmin, Ymin, Zmin)\n(Xmax, Ymax, Zmax)')
        self.mesh_size_label.setAlignment(QtCore.Qt.AlignCenter)
        self.mesh_size_label.setFrameStyle(QtGui.QFrame.Sunken | QtGui.QFrame.Box)
        hbox.addWidget(self.mesh_size_label)
        vbox.addLayout(hbox)
        hbox = QtGui.QHBoxLayout()
        combo_box = QtGui.QComboBox()
        combo_box.addItem('Not Scale')
        combo_box.addItem('Scale to:')
        combo_box.addItem('Scale by ratio:')
        combo_box.setFixedSize(90, 30)
        combo_box.currentIndexChanged.connect(self.did_change_scale_mode)
        hbox.addWidget(combo_box)
        self.input_text_edit = QtGui.QTextEdit()
        self.input_text_edit.setFixedSize(100, 30)
        self.input_text_edit.setEnabled(False)
        hbox.addWidget(self.input_text_edit)
        self.scale_btm = QtGui.QPushButton('Scale!')
        self.scale_btm.setFixedSize(50, 30)
        self.scale_btm.clicked.connect(self.did_push_scaled_button)
        self.scale_btm.setEnabled(False)
        hbox.addWidget(self.scale_btm)
        vbox.addLayout(hbox)

        # row
        vbox.addStretch()
        self.setLayout(vbox)

    @QtCore.pyqtSlot()
    def did_push_scaled_button(self):
        number = float(self.tr(self.input_text_edit.toPlainText()))
        if self.scale_mod == 1:
            print  'scale to exact size: %f!' % number
        elif self.scale_mod == 2:
            print  'scale to ratio: %f!' % number
        else:
            return

    @QtCore.pyqtSlot(int)
    def did_change_scale_mode(self, idx):
        self.scale_mod = idx
        if idx == 0:
            self.scale_btm.setEnabled(False)
            self.input_text_edit.setEnabled(False)
            self.input_text_edit.setText('')
        elif idx == 1:
            self.scale_btm.setEnabled(True)
            self.input_text_edit.setEnabled(True)
            self.input_text_edit.setText('exact size')
        elif idx == 2:
            self.scale_btm.setEnabled(True)
            self.input_text_edit.setEnabled(True)
            self.input_text_edit.setText('ratio')
        else:
            assert  False

    def generate_input_card(self):
        return ['']


class SolverConfFrame(QtGui.QFrame):
    def __init__(self):
        super(SolverConfFrame, self).__init__()
        self.setFixedWidth(300)
        self.models = {'Energy Equation':None,
                       'Viscid Model':None,
                       'Speciecs':None}
        vbox = QtGui.QVBoxLayout()
        #row
        insert_section_header('Solver Config', vbox)
        hbox = QtGui.QHBoxLayout()
        frame_in = QtGui.QFrame()
        frame_in.setFrameStyle(QtGui.QFrame.Sunken | QtGui.QFrame.Box)
        vbox_in = QtGui.QVBoxLayout()
        vbox_in.addWidget(QtGui.QLabel('Solver Type:'))
        self.pressure_based_button = QtGui.QRadioButton('Pressure Based')
        vbox_in.addWidget(self.pressure_based_button)
        self.density_based_button = QtGui.QRadioButton('Density Based')
        vbox_in.addWidget(self.density_based_button)
        frame_in.setLayout(vbox_in)
        hbox.addWidget(frame_in)
        frame_in = QtGui.QFrame()
        frame_in.setFrameStyle(QtGui.QFrame.Sunken | QtGui.QFrame.Box)
        vbox_in = QtGui.QVBoxLayout()
        vbox_in.addWidget(QtGui.QLabel('Time Step:'))
        self.transient_based_button = QtGui.QRadioButton('Transient')
        vbox_in.addWidget(self.transient_based_button)
        self.steaady_based_button = QtGui.QRadioButton('Steady')
        vbox_in.addWidget(self.steaady_based_button)
        frame_in.setLayout(vbox_in)
        hbox.addWidget(frame_in)
        vbox.addLayout(hbox)
        #row
        insert_section_header('Gravity Vector', vbox)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QLabel('Gx, Gy, Gz ='))
        te = QtGui.QTextEdit('0., 0., 0.')
        te.setFixedSize(200, 30)
        hbox.addWidget(te)
        vbox.addLayout(hbox)
        # row
        insert_section_header('Model Selection',vbox)
        self.table = QtGui.QTableWidget(len(self.models), 2)
        self.table.setHorizontalHeaderLabels(['Model', 'Description'])
        self.table.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.table.setColumnWidth(0, 120)
        self.table.setColumnWidth(1, 140)
        for idx, model in enumerate(self.models.keys()):
            it = QtGui.QTableWidgetItem(model, 0) # table-type 0
            self.table.setItem(idx, 0, it)
        vbox.addWidget(self.table)
        # row
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QPushButton('Edit'))
        hbox.addWidget(QtGui.QPushButton('Add'))
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def generate_input_card(self):
        return ['']

class PartsTreeFrame(QtGui.QFrame):
    def __init__(self):
        super(PartsTreeFrame, self).__init__()
        self.setFixedWidth(300)
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
        hbox.addWidget(combo_box)
        edit_button = QtGui.QPushButton("Edit")
        combo_box.addItem('Boundary Type')
        combo_box.addItem('Inlet')
        combo_box.addItem('Outlet')
        combo_box.addItem('Wall')
        combo_box.addItem('Symmetric')
        combo_box.addItem('Periodic')
        hbox.addWidget(edit_button)

        tree_widget.itemChanged.connect(self.item_changed_slot)
        tree_widget.itemDoubleClicked.connect(self.item_double_clicked_slot)

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_changed_slot(self, item, column):
        part_name = str(item.text(column))
        if part_name not in self.dict_tree['Boundary Parts'].keys() and \
           part_name not in self.dict_tree['Volume Parts'].keys():
            return

        if item.checkState(column) == QtCore.Qt.Checked:
            self.vtk_processor.activate_parts([part_name])
            #self.vtk_processor.center_on_part_slot(part_name)
        elif item.checkState(column) == QtCore.Qt.Unchecked:
            self.vtk_processor.deactivate_parts([part_name])
            #self.vtk_processor.fit_signal.emit()
        else:
            assert False

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_double_clicked_slot(self, item, column):
        if column != 0: return
        part_name = str(item.text(column))
        if part_name not in self.dict_tree['Boundary Parts'].keys() and \
                        part_name not in self.dict_tree['Volume Parts'].keys():
            return
        if part_name in self.dict_tree['Volume Parts']:
            self.vtk_processor.fit_slot()
        else:
            self.vtk_processor.focus_on_part_slot(part_name)

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

    def generate_input_card(self):
        return ['']


class OutputCOnfFrame(QtGui.QFrame):
    def __init__(self):
        super(OutputCOnfFrame, self).__init__()
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

    def log(self, content):
        self.append(content)
