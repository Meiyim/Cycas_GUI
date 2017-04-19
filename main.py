import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

import vtk_processor as vtk_proc
import dock_frame
import utility as uti

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(1000, 500)
        self.setWindowTitle('Cycas-GUI')

        # insert properties
        self.dock_left = None
        self.dock_bottom = None
        self.action_dict = {}
        self.left_dock_panels = {}
        self.progress_bar = None
        self.log_widget = None
        self.vtk_processor = None
        # do the real work
        self.setup_ui()
        # lower-left corner
        self.statusBar().showMessage('Ready')
        # place in center of the screen
        self.place_in_center()

    def setup_ui(self):
        # init main window
        # init vtk
        self.vtk_processor = vtk_proc.VtkProcessor(self)

        # init left dock frames
        self.left_dock_panels['PartTree'] = dock_frame.PartsTreeFrame(self.vtk_processor)
        self.left_dock_panels['Solver'] = dock_frame.SolverConfFrame(self.vtk_processor)
        self.left_dock_panels['Output'] = dock_frame.OutputConfFrame(self.vtk_processor)
        self.left_dock_panels['Mesh'] = dock_frame.MeshConfFrame(self.vtk_processor)
        self.left_dock_panels['Material'] = dock_frame.MaterialConfFrame(self.vtk_processor)

        # connect signal in main window
        mesh_dock = self.left_dock_panels['PartTree']
        uti.signal_center.report_part_list_signal.connect(mesh_dock.set_mesh_part_tree_slot)
        uti.signal_center.clear_parts_signal.connect(mesh_dock.clear_parts_slot)
        # init 2 docks
        dock2 = QtGui.QDockWidget(self.tr("Command Line"), self)
        dock2.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        dock2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                              QtCore.Qt.RightDockWidgetArea |
                              QtCore.Qt.BottomDockWidgetArea)
        te1 = dock_frame.CommandlineWidget(self.tr("cycas-GUI start..."))
        dock2.setWidget(te1)
        self.log_widget = te1
        self.dock_bottom = dock2
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock2)

        dock1 = QtGui.QDockWidget(self.tr("Configuration Panel"), self)
        dock1.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        dock1.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        #te1 = QtGui.QTextEdit(self.tr("ting1"))
        te1 = self.left_dock_panels['PartTree']
        dock1.setWidget(te1)
        self.dock_left = dock1
        dock1.setStyleSheet("QLabel{font-size:13px;font-family:Roman times;}")
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock1)

        #load vtk frame
        vtk_frame = self.vtk_processor.load_vtk_frame()
        vtk_frame.setMinimumSize(400, 400)
        self.setCentralWidget(vtk_frame)

        # actions
        exit_action = self.new_action('Exit', 'triggered()', QtCore.SLOT('close()'),
                                      icon='icons/exit', short_cut='Ctrl+Q', tip='Exit app')
        import_mesh_action = self.new_action('Import Mesh', 'triggered()', self.left_dock_panels['Mesh'].import_mesh,
                                             icon='icons/exit.png', short_cut='Ctrl+E', tip='Import CGNS Mesh')
        fit_window_action = self.new_action('Fit Window', 'triggered()', self.vtk_processor.fit_slot,
                                            short_cut = 'Ctrl+F', tip = 'resize the VTK window')

        self.new_action('Mesh', 'triggered()', self.show_panel,
                        tip='mesh configuration')
        self.new_action('PartTree', 'triggered()', self.show_panel,
                        tip='Show mesh panel')
        self.new_action('Output', 'triggered()', self.show_panel,
                         icon='icons/output_config.png', tip = 'configure output directory')
        self.new_action('Solver', 'triggered()', self.show_panel,
                         tip = 'solver configuration')
        self.new_action('Material', 'triggered()', self.show_panel,
                         tip = 'material configuration')

        # status bar and progress bar
        statbar = self.statusBar()
        pbar = QtGui.QProgressBar(statbar)
        pbar.setValue(0)
        pbar.hide()
        statbar.addPermanentWidget(pbar)
        self.progress_bar = pbar

        # add menu bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)
        file_menu.addAction(import_mesh_action)
        view_menu = menubar.addMenu('&View')
        view_menu.addAction(fit_window_action)
        # tool bar
        self.addToolBar('Mesh Config').addAction(self.action_dict['Mesh'])
        self.addToolBar('Parts Config').addAction(self.action_dict['PartTree'])
        self.addToolBar('Solver Config').addAction(self.action_dict['Solver'])
        self.addToolBar('Material Config').addAction(self.action_dict['Material'])
        self.addToolBar('Output Config').addAction(self.action_dict['Output'])

    def new_action(self, title, signal, slot_func, **kwargs):
        if kwargs.get('icon') is None:
            action = QtGui.QAction(title, self)
        else:
            action = QtGui.QAction(QtGui.QIcon(kwargs['icon']), title, self)
        if kwargs.get('short_cut') is not None:
            action.setShortcut(kwargs['short_cut'])
        if kwargs.get('tip') is not None:
            action.setStatusTip(kwargs['tip'])
        self.connect(action, QtCore.SIGNAL(signal), slot_func)
        self.action_dict[title] = action
        return action

    # override
    def show(self):
        super(MainWindow, self).show()
        self.vtk_processor.vtk_iren.Initialize()

    # override
    def closeEvent(self, event):
        reply = QtGui.QMessageBox.question(self, 'Message',
                                           "Are you sure to quit?", QtGui.QMessageBox.Yes, QtGui.QMessageBox.No)
        if reply == QtGui.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()
    #slot func
    @QtCore.pyqtSlot(str)
    def update_status_bar_slot(self, content):
        self.statusBar().showMessage(content, 3000)

    @QtCore.pyqtSlot(str)
    def log_slot(self, content):
        self.log_widget.log(content)

    @QtCore.pyqtSlot(int)
    def udpate_progress_bar_slot(self, istep):
        if istep == 0 or istep == 99:
            self.progress_bar.hide()
        else:
            self.progress_bar.show()
        self.progress_bar.setValue(istep)

    # place self in center
    def place_in_center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)

    @QtCore.pyqtSlot()
    def show_panel(self):
        key = str(self.sender().text())
        self.dock_left.setWindowTitle(key + ' Panel')
        panel = self.left_dock_panels[key]
        if self.dock_left.widget is not panel:
            self.dock_left.setWidget(panel)


app = QtGui.QApplication(sys.argv)
app.setApplicationName('Cycas-GUI')
main = MainWindow()
main.show()
sys.exit(app.exec_())
