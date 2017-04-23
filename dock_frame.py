import sys
import logging
import subprocess as sp
import os
import shutil

from PyQt4 import QtGui
from PyQt4 import QtCore
import vtk_processor as vtk_proc
import utility as uti
import dialogs as dia

# utility
section_header_font_sytle = "QLabel{font-size:13px;font-weight:bold;font-family:Roman times;}"
def insert_section_header(header, vbox):
    la = QtGui.QLabel(header)
    la.setStyleSheet(section_header_font_sytle)
    la.setFixedHeight(15)
    vbox.addWidget(la)

class ConfFrame(QtGui.QFrame):
    def __init__(self, vtk_processor):
        super(ConfFrame, self).__init__()
        self.vtk_processor = vtk_processor

class MaterialConfFrame(ConfFrame):
    def __init__(self, vtk_processor):
        super(MaterialConfFrame, self).__init__(vtk_processor)
        self.setFixedWidth(300)
        vbox = QtGui.QVBoxLayout()

        self.tree = QtGui.QTreeWidget(self)
        self.tree.setMouseTracking(True)
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabel('Materials')
        vbox.addWidget(self.tree)

        self.root_solid = QtGui.QTreeWidgetItem(self.tree)
        self.root_solid.setText(0, 'Solid Material')
        self.root_liquid = QtGui.QTreeWidgetItem(self.tree)
        self.root_liquid.setText(0, 'Liquid Material')
        self.tree.addTopLevelItem(self.root_solid)
        self.tree.addTopLevelItem(self.root_liquid)

        btm = QtGui.QPushButton('Add')
        btm.clicked.connect(self.add_material_slot)
        vbox.addWidget(btm)
        self.setLayout(vbox)

    @QtCore.pyqtSlot()
    def add_material_slot(self):
        pass

    def generate_input_card(self):
        return ['']

class MeshConfFrame(ConfFrame):
    def __init__(self, vtk_processor):
        super(MeshConfFrame, self).__init__(vtk_processor)
        self.setFixedWidth(300)
        vbox = QtGui.QVBoxLayout()
        self.scale_mod = 0  # 0 -- no scale, 1 -- exact size, 2 -- scale ratio
        # row
        insert_section_header('Input Config', vbox)
        hbox = QtGui.QHBoxLayout()
        btm = QtGui.QPushButton('Import Mesh')
        btm.setFixedSize(100, 30)
        btm.clicked.connect(self.import_mesh)
        hbox.addWidget(btm)
        self.import_dir = QtGui.QTextEdit()
        self.import_dir.setReadOnly(True)
        self.import_dir.setFixedHeight(30)
        hbox.addWidget(self.import_dir)
        vbox.addLayout(hbox)
        # row
        insert_section_header('Mesh Quality', vbox)
        hbox = QtGui.QHBoxLayout()
        btm  = QtGui.QPushButton('Check Quality')
        hbox.addWidget(btm)
        btm  = QtGui.QPushButton('Quality Report')
        hbox.addWidget(btm)
        vbox.addLayout(hbox)
        # row
        insert_section_header('Mesh Unit', vbox)
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
        hbox.addWidget(QtGui.QLabel('Original\nMesh Unit'))
        combo_box = QtGui.QComboBox()
        combo_box.addItem('m')
        combo_box.addItem('mm')
        combo_box.addItem('cm')
        combo_box.addItem('Scale ratio')
        combo_box.currentIndexChanged.connect(self.did_change_scale_mode)
        hbox.addWidget(combo_box)
        self.input_text_edit = QtGui.QTextEdit()
        self.input_text_edit.setFixedHeight(30)
        self.input_text_edit.setEnabled(False)
        hbox.addWidget(self.input_text_edit)
        vbox.addLayout(hbox)

        # row
        vbox.addStretch()
        self.setLayout(vbox)

    def import_mesh(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'import cgns mesh', '/home')
        filename = './moxing1.cgns'
        uti.signal_center.log_signal.emit('loading mesh %s' % filename)
        self.did_set_mesh_input_dir(filename)
        self.vtk_processor.vtk_ren.RemoveAllViewProps()
        task = vtk_proc.LoadCgnsTask(self.vtk_processor, filename)
        QtCore.QThreadPool.globalInstance().start(task)

    @QtCore.pyqtSlot(int)
    def did_change_scale_mode(self, idx):
        self.scale_mod = idx
        if idx != 3:
            self.input_text_edit.setEnabled(False)
            self.input_text_edit.setText('')
        else:
            self.input_text_edit.setEnabled(True)
            self.input_text_edit.setText('ratio')

    def did_set_mesh_input_dir(self, file_dir):
        self.import_dir.setText(file_dir)

    def generate_input_card(self):
        return ['']


class SolverConfFrame(ConfFrame):
    def __init__(self, vtk_processor):
        super(SolverConfFrame, self).__init__(vtk_processor)
        self.setFixedWidth(300)
        self.models = {'Energy Equation': {'desc': 'off', 'enabled': False},
                       'Viscid Model': {'desc': '','submodel':{
                            'k-epsilon':{'desc': 'off'},
                            'k-omiga':{'desc': 'off'},
                            },
                            'enabled': -1, #enabled idx
                       },
                       'Speciecs': {'desc': 'off', 'enabled': False},
        }
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
        vbox_in.addWidget(QtGui.QLabel('Time'))
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
        #te = QtGui.QTextEdit(self)
        te = dia.VectorInputor()
        te.setFixedSize(200, 30)
        hbox.addWidget(te)
        vbox.addLayout(hbox)
        # row
        insert_section_header('Model Selection',vbox)
        self.tree = QtGui.QTreeWidget(self)
        self.tree.setMouseTracking(True)
        self.tree.setColumnCount(2)
        self.tree.setColumnWidth(0, 150)
        self.tree.setHeaderLabels(['Models', 'Description'])
        vbox.addWidget(self.tree)
        self.update_tree()
        # row
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(QtGui.QPushButton('Edit'))
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def update_tree(self):
        for model, info in self.models.iteritems():
            it = QtGui.QTreeWidgetItem(self.tree)
            it.setText(0, model)
            it.setText(1, info['desc'])
            if info['enabled'] is True:
                it.setCheckState(0, QtCore.Qt.Checked)
            else:
                it.setCheckState(0, QtCore.Qt.Unchecked)
            self.tree.addTopLevelItem(it)
            if info.get('submodel') is not None:
                for idx, (submodel, subinfo) in enumerate(info['submodel'].iteritems()):
                    subit = QtGui.QTreeWidgetItem(it)
                    subit.setText(0, submodel)
                    subit.setText(1, subinfo['desc'])
                    if idx == info['enabled']:
                        subit.setCheckState(0, QtCore.Qt.Checked)
                    else:
                        subit.setCheckState(0, QtCore.Qt.Unchecked)

    def generate_input_card(self):
        return ['']

class PartsTreeFrame(ConfFrame):
    class BoundaryType(object):
        UNDEFINED=-1
        WALL  = 0
        INLET = 1
        OUTLET= 2
        SYMMETRY=3
        PERIODIC=5
    def __init__(self, vtk_processor):
        super(PartsTreeFrame, self).__init__(vtk_processor)
        self.setFixedWidth(300)
        vbox = QtGui.QVBoxLayout()
        self.setLayout(vbox)
        self.dict_tree = {'Boundary Parts':{}, 'Volume Parts':{}}
        tree_widget = QtGui.QTreeWidget()
        tree_widget.setMouseTracking(True)
        vbox.addWidget(tree_widget)
        tree_widget.setColumnCount(2)
        tree_widget.setHeaderLabels(['Parts', 'Type'])
        tree_widget.setColumnWidth(0, 150)
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
        self.combo_box = combo_box
        combo_box.setFixedSize(180, 28)
        combo_box.setEnabled(False)
        hbox.addWidget(combo_box)
        edit_button = QtGui.QPushButton("Edit")
        self.edit_btm = edit_button
        combo_box.addItem('Boundary Type')
        combo_box.addItem('Wall') # --0
        combo_box.addItem('Inlet')# --1
        combo_box.addItem('Outlet')# --2
        combo_box.addItem('Symmetric') # --3
        combo_box.addItem('Periodic') # --4
        hbox.addWidget(edit_button)

        tree_widget.itemChanged.connect(self.item_changed_slot)
        tree_widget.itemDoubleClicked.connect(self.item_double_clicked_slot)
        tree_widget.itemEntered.connect(self.item_entered_slot)
        tree_widget.itemClicked.connect(self.item_clicked_slot)

        combo_box.currentIndexChanged.connect(self.did_set_bc_type)

        edit_button.clicked.connect(self.did_push_edit_btm)

    def switch_to_part(self, part_name):
        info = self.dict_tree['Boundary Parts'][part_name]
        if info.get('type') is None:
            self.combo_box.setCurrentIndex(0)
            self.edit_btm.setEnabled(False)
        else:
            self.combo_box.setCurrentIndex(info['type'])
            self.edit_btm.setEnabled(True)

    # tree widget
    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_changed_slot(self, item, column):
        if column != 0: return
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

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_double_clicked_slot(self, item, column):
        if column != 0: return
        part_name = str(item.text(column))
        if part_name not in self.dict_tree['Boundary Parts'].keys() and \
                        part_name not in self.dict_tree['Volume Parts'].keys():
            return
        if part_name in self.dict_tree['Volume Parts'].keys():
            self.vtk_processor.fit_slot()
        else:
            self.vtk_processor.focus_on_part_slot(part_name)

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_clicked_slot(self, item, column):
        part_name = str(item.text(0))
        if part_name in self.dict_tree['Boundary Parts']:
            self.combo_box.setEnabled(True)
            self.switch_to_part(part_name)
        else:
            self.combo_box.setEnabled(False)

    @QtCore.pyqtSlot(QtGui.QTreeWidgetItem, int)
    def item_entered_slot(self, item, column):
        if column != 0: return
        part_name = str(item.text(column))
        if part_name in self.dict_tree['Boundary Parts'].keys():
            uti.signal_center.update_status_signal.emit('double click to focus on part: %s' %  part_name)

    # combo box
    @QtCore.pyqtSlot(int)
    def did_set_bc_type(self, idx):
        item = self.tree_widget.currentItem()
        part_name = str(item.text(0))
        if idx == 0:
            self.dict_tree['Boundary Parts'][part_name]['type'] = None
        else:
            self.dict_tree['Boundary Parts'][part_name]['type'] = idx
        if idx == 0 :
            self.edit_btm.setEnabled(False)
            self.vtk_processor.set_part_color(part_name, (1., 1., 1.))
            item.setText(1, '')
        else:
            self.edit_btm.setEnabled(True)
            if idx == 1:
                self.vtk_processor.set_part_color(part_name, (0.0, 0.0, 1.0))
                item.setText(1, 'WALL')
            elif idx == 2:
                self.vtk_processor.set_part_color(part_name, (0.0, 1.1, 0.0))
                item.setText(1, 'INLET')
            elif idx == 3:
                self.vtk_processor.set_part_color(part_name, (1., 0., 0.))
                item.setText(1, 'OUTLET')
            elif idx == 4:
                self.vtk_processor.set_part_color(part_name, (1., 1., 0.))
                item.setText(1, 'SYMMETRY')
            elif idx == 5:
                self.vtk_processor.set_part_color(part_name, (0., 1., 1.))
                item.setText(1, 'PERIODIC')

    # push bottom
    @QtCore.pyqtSlot()
    def did_push_edit_btm(self):
        bc_type = self.combo_box.currentIndex()
        bc_dialog = dia.BCDialog(bc_type, self, title='Set Inlet Boundary')
        bc_dialog.accepted.connect(self.did_finish_dialog)
        bc_dialog.exec_() # blocking call

    # dialog
    def did_finish_dialog(self):
        dialog = self.sender()
        item = self.tree_widget.currentItem()
        part_name = str(item.text())
        if dialog.info is not None:
            self.dict_tree['Boundary Parts'][part_name]['vec'] = dialog.info
            print 'getting info from dialog'

    # self define
    @QtCore.pyqtSlot(dict)
    def set_mesh_part_tree_slot(self, dic):
        for root_name, part_names in dic.iteritems():
            rt = self.tree_widget.findItems(root_name, QtCore.Qt.MatchExactly)[0]
            for name in part_names:
                assert name not in self.dict_tree[root_name].keys() # fail when boundary part has the same name
                self.dict_tree[root_name][name] = {}
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


class OutputConfFrame(ConfFrame):
    def __init__(self, vtk_processor):
        super(OutputConfFrame, self).__init__(vtk_processor)
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


class CycasTracker(QtCore.QObject):
    def __init__(self):
        super(CycasTracker, self).__init__()
        self.notifier = None
        self.cycas_dir = None
        self.task = None
        self.logfile = None
        self.task_dir = None

    def start_solver(self, task_name, param, mesh_dir, **kwargs):
        cwd = os.getcwd()
        self.task_dir = os.makedirs(os.path.join(cwd, 'cycas_' + task_name))
        if kwargs.get('not_copy_mesh') is None:
            shutil.move(mesh_dir, self.task_dir)
        shutil.copy(self.cycas_dir, self.task_dir)

        input_pard = open(os.path.join(self.task_dir, 'inp.inp'), 'w')
        input_pard.write(param)

        self.logfile = open(os.path.join(self.task_dir, 'out'), 'w')
        self.task = sp.Popen(['./cycas'], stdout=self.logfile)

        fd = os.open(self.logfile.name, os.O_RDONLY)
        self.notifier = QtCore.QSocketNotifier(fd, QtCore.QSocketNotifier.Read)
        self.notifier.activated.connect(self.log_update_slot)
        self.notifier.setEnabled(True)

    @QtCore.pyqtSlot(int)
    def log_update_slot(self, fd):
        while True:
            data = os.read(fd, 1024)
            if not data:
                break
            print 'data read %s' % repr(data)

class CommandlineWidget(QtGui.QTextEdit):
    def __init__(self, content):
        super(CommandlineWidget, self).__init__(content)
        self.setReadOnly(True)

    def log(self, content):
        self.append(content)
