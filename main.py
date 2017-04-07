import sys
from PyQt4 import QtGui
from PyQt4 import QtCore

import vtk_processor as vtk_proc


class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        self.resize(1000, 500)
        self.setWindowTitle('main window')

        # insert properties
        self.dock_left = None
        self.dock_bottom = None
        self.vtk_processor = vtk_proc.Vtk_processor()
        self.actor_dict = {}
        # do the real work
        self.setup_ui()
        # lower-left corner
        self.statusBar().showMessage('Ready')
        # place in center of the screen
        self.place_in_center()

    def setup_ui(self):
        # init main window
        # init 2 docks
        dock2 = QtGui.QDockWidget(self.tr("ting1"), self)
        dock2.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        dock2.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea |
                              QtCore.Qt.RightDockWidgetArea |
                              QtCore.Qt.BottomDockWidgetArea)
        te1 = QtGui.QTextEdit(self.tr("ting1"))
        dock2.setWidget(te1)
        self.dock_bottom = dock2
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, dock2)

        dock1 = QtGui.QDockWidget(self.tr("ting1"), self)
        dock1.setFeatures(QtGui.QDockWidget.DockWidgetMovable)
        dock1.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea | QtCore.Qt.RightDockWidgetArea)
        te1 = QtGui.QTextEdit(self.tr("ting1"))
        dock1.setWidget(te1)
        self.dock_left = dock1
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, dock1)

        # add vtk
        vtk_frame = self.vtk_processor.load_vtk_frame()
        self.setCentralWidget(vtk_frame)

        # actions
        exit_action = self.new_action('Exit', 'triggered()', QtCore.SLOT('close()'),
                                      icon='icons/exit.png', short_cut='Ctrl+Q', tip='Exit app')
        import_mesh_action = self.new_action('Load Mesh', 'triggered()', self.import_mesh,
                                      icon='icons/exit.png', short_cut='Ctrl+E', tip='Import CGNS Mesh')
        # add menu bar
        self.statusBar()
        menubar = self.menuBar()
        file_menu = menubar.addMenu('&File')
        file_menu.addAction(exit_action)
        file_menu.addAction(import_mesh_action)
        toolbar = self.addToolBar('Exit')
        toolbar.addAction(exit_action)

    def new_action(self, title, signal, slot_func, **kwargs):
        if kwargs.get('icon') is None:
            action = QtGui.QAction(title, self)
        else:
            action = QtGui.QAction(QtGui.QIcon(kwargs['icon']), title, self)
        if kwargs.get('short_cut') is not None:
            action.setShortcut(kwargs['short_cut'])
        if kwargs.get('tip') is not None:
            action.setShortcut(kwargs['tip'])
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
    # place self in center
    def place_in_center(self):
        screen = QtGui.QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) / 2, (screen.height() - size.height()) / 2)
    # action call backs
    def import_mesh(self):
        filename = QtGui.QFileDialog.getOpenFileName(self, 'import cgns mesh',
                    '/home')
        self.vtk_processor.load_cgns_file(filename)

app = QtGui.QApplication(sys.argv)
main = MainWindow()
main.show()
sys.exit(app.exec_())
