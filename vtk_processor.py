import vtk
from PyQt4 import QtGui
from PyQt4 import QtCore
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class VtkProcessor(QtCore.QObject):
    report_istep_signal = QtCore.pyqtSignal(int)
    update_status_signal = QtCore.pyqtSignal(str)
    log_signal = QtCore.pyqtSignal(str)
    report_part_list_signal = QtCore.pyqtSignal(dict)
    clear_partlist_signal = QtCore.pyqtSignal()
    def __init__(self, main_window):
        super(VtkProcessor, self).__init__()
        self.vtk_frame = None
        self.vtk_boxlayout = None
        self.vtk_widget = None
        self.vtk_ren = None
        self.vtk_iren = None
        self.mapper = None
        self.ug = None
        #register signal

        self.report_istep_signal.connect(main_window.udpate_progress_bar_slot)
        self.update_status_signal.connect(main_window.update_status_bar_slot)
        self.log_signal.connect(main_window.log_slot)
        self.report_part_list_signal.connect(main_window.left_dock_panels['mesh_conf'].set_mesh_part_tree_slot)
        self.clear_partlist_signal.connect(main_window.left_dock_panels['mesh_conf'].clear_parts_slot)

    def load_vtk_frame(self):
        # vtk
        vtk_frame = QtGui.QFrame()
        vtk_boxlayout = QtGui.QVBoxLayout()
        vtk_widget = QVTKRenderWindowInteractor(vtk_frame)
        vtk_boxlayout.addWidget(vtk_widget)

        vtk_ren = vtk.vtkRenderer()
        vtk_widget.GetRenderWindow().AddRenderer(vtk_ren)
        vtk_iren = vtk_widget.GetRenderWindow().GetInteractor()

        # test work
        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)
        # Create a mapper
        self.mapper = vtk.vtkDataSetMapper()
        self.mapper.SetInputConnection(source.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(self.mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        vtk_ren.AddActor(actor)
        vtk_frame.setLayout(vtk_boxlayout)
        # Create Axes actor
        axesActor = vtk.vtkAxesActor()
        axes_transform = vtk.vtkTransform()
        axes_transform.Translate(-5., -5., -5.)
        axesActor.SetUserTransform(axes_transform)
        vtk_ren.AddActor(axesActor)

        # add to properties
        self.vtk_ren = vtk_ren
        self.vtk_iren = vtk_iren
        self.vtk_widget = vtk_widget

        # delete-able
        self.vtk_frame = vtk_frame
        self.vtk_boxlayout = vtk_boxlayout

        vtk_ren.ResetCamera()
        return vtk_frame

# background task
class LoadCgnsTask(QtCore.QRunnable):
    def __init__(self, vtkproc):
        super(LoadCgnsTask, self).__init__()
        self.vtk_processor = vtkproc

    def run(self):
        import cgns_reader
        cgns_reader.init()
        cgns_reader.read_file('moxing1.cgns')
        self.vtk_processor.log_signal.emit('number of vertices: %d \n number of parts: %d \n number of elements: %d'
                           % (cgns_reader.nvert, cgns_reader.nsection, cgns_reader.nelement))
        part_list = cgns_reader.get_parts()
        self.vtk_processor.log_signal.emit('found parts: %s\n' % str(part_list))
        self.vtk_processor.ug = vtk.vtkUnstructuredGrid()
        self.vtk_processor.ug.SetPoints(cgns_reader.points)

        v_part = set()
        b_part = set()
        for part_name in part_list:
            self.vtk_processor.log_signal.emit('processing part:%s' % part_name)
            self.vtk_processor.update_status_signal.emit('loading mesh part: %s... please wait' % part_name)
            nelem = cgns_reader.get_cell_num_at_part(part_name)
            for istep, cell in enumerate(cgns_reader.get_cell_at_part(part_name)):
                self.vtk_processor.report_istep_signal.emit(int(istep* 100./nelem) )
                cell_type = cell.GetCellType()
                self.vtk_processor.ug.InsertNextCell(cell_type, cell.GetPointIds())
                if cell_type is vtk.VTK_TRIANGLE or cell_type is vtk.VTK_QUAD:
                    b_part.add(part_name)
                else:
                    v_part.add(part_name)
        self.vtk_processor.report_part_list_signal.emit({'Volume Parts':list(v_part), 'Boundary Parts':list(b_part)})
        self.vtk_processor.mapper.SetInputData(self.vtk_processor.ug)
        #self.vtk_processor.vtk_widget.GetRenderWindow().Render()
        self.vtk_processor.vtk_ren.ResetCamera()
        self.vtk_processor.update_status_signal.emit('done')
        cgns_reader.deinit()
