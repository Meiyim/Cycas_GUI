import sys
import logging

from PyQt4 import QtGui
from PyQt4 import QtCore

import vtk_processor as vtk_proc
import dock_frame

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='cycas_gui.log',
                filemode='w')

class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(1000, 500)
        self.setWindowTitle('Cycas-GUI')

        # insert properties
        self.dock_left = None
        self.dock_bottom = None
        self.actor_dict = {}
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
        # init left dock frames
        self.left_dock_panels['mesh_conf'] = dock_frame.LeftDockFrame()
        self.left_dock_panels['output_conf'] = dock_frame.LeftDockFrame2()

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
        te1 = self.left_dock_panels['mesh_conf']
        dock1.setWidget(te1)
        self.dock_left = dock1
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock1)

        # add vtk
        self.vtk_processor = vtk_proc.VtkProcessor(self)
        vtk_frame = self.vtk_processor.load_vtk_frame()
        vtk_frame.setMinimumSize(400, 400)
        self.setCentralWidget(vtk_frame)

        # actions
        exit_action = self.new_action('Exit', 'triggered()', QtCore.SLOT('close()'),
                                      short_cut='Ctrl+Q', tip='Exit app')
        show_mesh_panel_action = self.new_action('Mesh', 'triggered()', self.show_mesh_panel,
                                      icon='icons/exit.png', tip='Show mesh panel')
        import_mesh_action = self.new_action('Load Mesh', 'triggered()', self.import_mesh,
                                             icon='icons/exit.png', short_cut='Ctrl+E', tip='Import CGNS Mesh')
        show_output_panel_action = self.new_action('Output', 'triggered()', self.show_output_panel,
                                                   icon='icons/output_config.png', tip = 'configure output directory')
        fit_window_action = self.new_action('Fit Window', 'triggered()', self.vtk_processor.fit_slot,
                                            short_cut = 'Ctrl+F', tip = 'resize the VTK window')
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

        toolbar = self.addToolBar('Mesh')
        toolbar.addAction(show_mesh_panel_action)
        output_panel_tool_bar = self.addToolBar('Output Conf')
        output_panel_tool_bar.addAction(show_output_panel_action)

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
        self.actor_dict[title] = action
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
        self.statusBar().showMessage(content)

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

    # action call backs
    def import_mesh(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'import cgns mesh', '/home')
        self.log_widget.log('loading mesh %s' % filename)
        task = vtk_proc.LoadCgnsTask(self.vtk_processor)
        QtCore.QThreadPool.globalInstance().start(task)

    def show_output_panel(self):
        panel = self.left_dock_panels['output_conf']
        if self.dock_left.widget is not panel:
            self.dock_left.setWidget(panel)

    def show_mesh_panel(self):
        panel = self.left_dock_panels['mesh_conf']
        if self.dock_left.widget is not panel:
            self.dock_left.setWidget(panel)

app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
