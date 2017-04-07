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

        # add to properties
        self.vtk_ren = vtk_ren
        self.vtk_iren = vtk_iren
        self.vtk_widget = vtk_widget

        # delete-able
        self.vtk_frame = vtk_frame
        self.vtk_boxlayout = vtk_boxlayout

        vtk_ren.ResetCamera()
        return vtk_frame

    def load_cgns_file(self, filename):
        import cgns_reader
        cgns_reader.init()
        cgns_reader.read_file('moxing1.cgns')
        self.ug = vtk.vtkUnstructuredGrid()
        self.ug.SetPoints(cgns_reader.points)

        progressDialog = QtGui.QProgressDialog(self.vtk_frame)
        progressDialog.setWindowModality(QtCore.Qt.WindowModal)
        progressDialog.setMinimumDuration(5)
        progressDialog.setWindowTitle(self.vtk_frame.tr("Please wait"))
        progressDialog.setLabelText(self.vtk_frame.tr("loading mesh"))
        progressDialog.setRange(0, cgns_reader.get_cell_num_at_part('BODY') - 1)

        for istep, cell in enumerate(cgns_reader.get_cell_at_part('BODY')):
            progressDialog.setValue(istep)
            self.ug.InsertNextCell(cell.GetCellType(), cell.GetPointIds())
        self.mapper.SetInputData(self.ug)
        self.vtk_ren.ResetCamera()
        cgns_reader.deinit()
