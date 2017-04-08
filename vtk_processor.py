import vtk
from PyQt4 import QtGui
from PyQt4 import QtCore
from vtk.qt4.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class Vtk_processor(object):
    def __init__(self):
        self.vtk_frame = None
        self.vtk_boxlayout = None
        self.vtk_widget = None
        self.vtk_ren = None
        self.vtk_iren = None
        self.mapper = None
        self.ug = None

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

    # consider move this funciton to backgound thread. to optimize the main window performance
    def load_cgns_file(self, filename, main_window):
        log_widget = main_window.log_widet
        log_widget.log('loading mesh %s' % filename)
        import cgns_reader

        cgns_reader.init()
        cgns_reader.read_file('moxing1.cgns')
        log_widget.log('number of vertices: %d \n number of parts: %d \n number of elements: %d'
                       % (cgns_reader.nvert, cgns_reader.nsection, cgns_reader.nelement))
        log_widget.log('found parts: %s\n' % str(cgns_reader.get_parts()))
        self.ug = vtk.vtkUnstructuredGrid()
        self.ug.SetPoints(cgns_reader.points)

        pbar = main_window.progress_bar
        sbar = main_window.statusBar()

        sbar.showMessage('loading mesh... please wait')
        pbar.setRange(0, cgns_reader.get_cell_num_at_part('BODY') - 1)
        pbar.show()
        for istep, cell in enumerate(cgns_reader.get_cell_at_part('BODY')):
            pbar.setValue(istep)
            self.ug.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
        self.mapper.SetInputData(self.ug)
        self.vtk_ren.ResetCamera()
        pbar.hide()
        sbar.clearMessage()
        cgns_reader.deinit()

        log_widget.log('done reading mesh')

