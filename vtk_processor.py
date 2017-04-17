import vtk
import logging
from PyQt4 import QtGui
from PyQt4 import QtCore
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class VtkProcessor(QtCore.QObject):
    update_progress_bar_signal = QtCore.pyqtSignal(int)
    update_status_signal = QtCore.pyqtSignal(str)
    log_signal = QtCore.pyqtSignal(str)
    report_part_list_signal = QtCore.pyqtSignal(dict)
    clear_parts_signal = QtCore.pyqtSignal()
    render_signal = QtCore.pyqtSignal()
    def __init__(self, main_window):
        super(VtkProcessor, self).__init__()
        self.vtk_frame = None
        self.vtk_boxlayout = None
        self.vtk_widget = None
        self.vtk_ren = None
        self.vtk_iren = None
        self.orientation_marker = None
        self.ug_mapper_actor = {}
        #register signal

        self.update_progress_bar_signal.connect(main_window.udpate_progress_bar_slot)
        self.update_status_signal.connect(main_window.update_status_bar_slot)
        self.log_signal.connect(main_window.log_slot)
        self.render_signal.connect(self.render_slot)
        mesh_dock = main_window.left_dock_panels['PartTree']
        self.report_part_list_signal.connect(mesh_dock.set_mesh_part_tree_slot)
        self.clear_parts_signal.connect(mesh_dock.clear_parts_slot)
        mesh_dock.vtk_processor = self
    def load_vtk_frame(self):
        # vtk
        vtk_frame = QtGui.QFrame()
        self.vtk_frame = vtk_frame
        vtk_boxlayout = QtGui.QVBoxLayout()
        self.vtk_boxlayout = vtk_boxlayout
        vtk_widget = QVTKRenderWindowInteractor(vtk_frame)
        self.vtk_widget = vtk_widget
        vtk_boxlayout.addWidget(vtk_widget)

        vtk_ren = vtk.vtkRenderer()
        self.vtk_ren = vtk_ren
        vtk_widget.GetRenderWindow().AddRenderer(vtk_ren)
        vtk_iren = vtk_widget.GetRenderWindow().GetInteractor()
        self.vtk_iren = vtk_iren
        interactor_style = vtk.vtkInteractorStyleTrackballCamera()
        self.vtk_iren.SetInteractorStyle(interactor_style)
        # Create Axes actor
        axesActor = vtk.vtkAxesActor()
        self.orientation_marker = vtk.vtkOrientationMarkerWidget()
        self.orientation_marker.SetOrientationMarker(axesActor)
        self.orientation_marker.SetInteractor(self.vtk_iren)
        self.orientation_marker.EnabledOn()
        self.orientation_marker.InteractiveOn()

        # test work
        # Create source
        source = vtk.vtkSphereSource()
        source.SetCenter(0, 0, 0)
        source.SetRadius(5.0)
        # Create a mapper
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(source.GetOutputPort())
        # Create an actor
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetRepresentationToWireframe()
        vtk_ren.AddActor(actor)
        vtk_frame.setLayout(vtk_boxlayout)
        self.ug_mapper_actor['Sample Sphere'] = (source, mapper, actor)
        self.report_part_list_signal.emit({'Volume Parts':['Sample Sphere'], 'Boundary Parts':list()})


        # add to properties

        # delete-able

        vtk_ren.ResetCamera()
        return vtk_frame

    def activate_parts(self, part_name_list):
        for name in part_name_list:
            f, m, a = self.ug_mapper_actor[name]
            self.vtk_ren.AddActor(a)
        self.render_signal.emit()

    def deactivate_parts(self, part_name_list):
        for name in part_name_list:
            f, m, a = self.ug_mapper_actor[name]
            self.vtk_ren.RemoveActor(a)
        self.render_signal.emit()

    @QtCore.pyqtSlot()
    def render_slot(self):
        self.vtk_iren.Render()
    @QtCore.pyqtSlot()
    def fit_slot(self):
        self.vtk_ren.ResetCamera()
        self.render_signal.emit()


# background task
class LoadCgnsTask(QtCore.QRunnable):
    def __init__(self, vtkproc):
        super(LoadCgnsTask, self).__init__()
        self.vtk_processor = vtkproc

    def run(self):
        # clear existing part
        deletable = set()
        for part_name, (filter, mapper, actor) in self.vtk_processor.ug_mapper_actor.iteritems():
            self.vtk_processor.vtk_ren.RemoveActor(actor)
            deletable.add(part_name)
        for part_name in deletable:
            del self.vtk_processor.ug_mapper_actor[part_name]
        self.vtk_processor.clear_parts_signal.emit()
        import cgns_reader
        cgns_reader.init()
        cgns_reader.progress_signal = self.vtk_processor.update_progress_bar_signal
        cgns_reader.read_file('moxing1.cgns')
        self.vtk_processor.log_signal.emit('number of vertices: %d \n number of parts: %d \n number of elements: %d'
                           % (cgns_reader.nvert, cgns_reader.nsection, cgns_reader.nelement))
        self.vtk_processor.log_signal.emit('found parts: %s' % str(cgns_reader.part_offset_dict.keys()))
        v_part = set()
        b_part = set()
        for part_name, cell_array, cell_type_array in cgns_reader.get_parts():
            ug = vtk.vtkUnstructuredGrid()
            ug.SetPoints(cgns_reader.points)
            self.vtk_processor.log_signal.emit('processing part:%s' % part_name)
            self.vtk_processor.update_status_signal.emit('loading mesh part: %s... please wait' % part_name)
            ug.SetCells(cell_type_array, cell_array)
            if vtk.VTK_TRIANGLE in cell_type_array or vtk.VTK_QUAD in cell_type_array:
                b_part.add(part_name)
            else:
                v_part.add(part_name)
            mapper = vtk.vtkDataSetMapper()
            actor = vtk.vtkActor()
            self.vtk_processor.ug_mapper_actor[part_name] = (ug, mapper, actor)
            self.vtk_processor.vtk_ren.AddActor(actor)
            actor.SetMapper(mapper)
            mapper.SetInputData(ug)
            actor.GetProperty().SetRepresentationToWireframe()

        self.vtk_processor.report_part_list_signal.emit({'Volume Parts':list(v_part), 'Boundary Parts':list(b_part)})
        # Create Filter
        self.vtk_processor.render_signal.emit()
        self.vtk_processor.vtk_ren.ResetCamera()
        self.vtk_processor.update_status_signal.emit('done')
        cgns_reader.deinit()

