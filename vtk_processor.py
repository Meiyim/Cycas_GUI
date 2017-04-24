import vtk
from PyQt4 import QtGui
from PyQt4 import QtCore
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

import utility as uti

class VtkProcessor(QtCore.QObject):

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
        uti.signal_center.update_progress_bar_signal.connect(main_window.udpate_progress_bar_slot)
        uti.signal_center.update_status_signal.connect(main_window.update_status_bar_slot)
        uti.signal_center.log_signal.connect(main_window.log_slot)
        self.part_info = {}

        # connect signal
        uti.signal_center.render_signal.connect(self.render_slot)
        uti.signal_center.fit_signal.connect(self.fit_slot)

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
        # Orientation Marker
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
        self.part_info['Sample Sphere'] = {'center': source.GetCenter()}
        self.ug_mapper_actor['Sample Sphere'] = (source, mapper, actor)
        uti.signal_center.report_part_list_signal.emit({'Volume Parts':['Sample Sphere'], 'Boundary Parts':list()})


        # add to properties

        # delete-able

        vtk_ren.ResetCamera()
        return vtk_frame

    def activate_parts(self, part_name_list):
        for name in part_name_list:
            f, m, a = self.ug_mapper_actor[name]
            prop = a.GetProperty()
            prop.SetOpacity(1.0)
        uti.signal_center.render_signal.emit()

    def deactivate_parts(self, part_name_list):
        for name in part_name_list:
            f, m, a = self.ug_mapper_actor[name]
            prop = a.GetProperty()
            prop.SetOpacity(0.0)
        uti.signal_center.render_signal.emit()

    def set_part_color(self, part_name, color):
        u, m, a = self.ug_mapper_actor[part_name]
        a.GetProperty().SetColor(color[0], color[1], color[2])
        uti.signal_center.render_signal.emit()

    def clear(self):
        self.ug_mapper_actor = {}
        self.part_info = {}
        uti.signal_center.clear_parts_signal.emit()

    @QtCore.pyqtSlot()
    def render_slot(self):
        self.vtk_iren.Render()

    @QtCore.pyqtSlot()
    def fit_slot(self):
        self.vtk_ren.ResetCamera()
        uti.signal_center.render_signal.emit()

    @QtCore.pyqtSlot(str)
    def focus_on_part_slot(self, part_name):
        center = self.part_info[part_name]['center']
        camera = self.vtk_ren.GetActiveCamera()
        camera.SetFocalPoint(center)
        camera.ComputeViewPlaneNormal()
        uti.signal_center.render_signal.emit()

# background task
class LoadCgnsTask(QtCore.QRunnable):
    def __init__(self, vtkproc, name):
        super(LoadCgnsTask, self).__init__()
        self.vtk_processor = vtkproc
        self.file_name = name

    def run(self):
        # clear existing part
        self.vtk_processor.clear()
        print 'in thread'
        import cgns_reader
        cgns_reader.init()
        cgns_reader.read_file(self.file_name)
        uti.signal_center.log_signal.emit('number of vertices: %d \n number of parts: %d \n number of elements: %d'
                           % (cgns_reader.nvert, cgns_reader.nsection, cgns_reader.nelement))
        uti.signal_center.log_signal.emit('found parts: %s' % str(cgns_reader.part_offset_dict.keys()))
        v_part = set()
        b_part = set()
        for part_name, cell_array, cell_type_array in cgns_reader.get_parts():
            ug = vtk.vtkUnstructuredGrid()
            ug.SetPoints(cgns_reader.points)
            ug.SetCells(cell_type_array, cell_array)
            self.vtk_processor.part_info[part_name] = {'center' : cgns_reader.center_points[part_name]}
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

        # Create Filter
        uti.signal_center.report_part_list_signal.emit({'Volume Parts':list(v_part), 'Boundary Parts':list(b_part)})
        uti.signal_center.render_signal.emit()
        uti.signal_center.update_status_signal.emit('done')
        self.vtk_processor.vtk_ren.ResetCamera()
        cgns_reader.deinit()

