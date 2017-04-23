import ctypes as ct
import vtk
import platform

import  utility as uti


class CGNSException(Exception):
    def __init__(self, err = 'cgns_error'):
        super(CGNSException, self).__init__(self, err)


class Element(ct.Structure):
    _fields_ = [('type', ct.c_int), ('pid', 8 * ct.c_size_t)]


# utility
def check(ret):
    if ret != 0: raise CGNSException

def set_vert_type(vtype):
    cgns_reader_module.read_verts.argtypes = [vtype, vtype, vtype]
<<<<<<< HEAD
    cgns_reader_module.get_part_center.argtypes = [vtype, vtype, vtype, ct.c_int]
=======
    cgns_reader_module.get_part_center.argtypes = [vtype, vtype, vtype]
>>>>>>> e00191bdcbf36aa98c443d57bf9bb0d9759393e8

vtk_npe = {vtk.VTK_TETRA:4,
       vtk.VTK_QUAD:4,
       vtk.VTK_TRIANGLE:3,
       vtk.VTK_HEXAHEDRON:8,
       vtk.VTK_WEDGE:6,
       vtk.VTK_PYRAMID:5}

# type alias
uint_p = ct.POINTER(ct.c_size_t)
int_p = ct.POINTER(ct.c_int)
double_p = ct.POINTER(ct.c_double)

# global
cgns_reader_module = None
nvert = None
nsection = None
nelement = None
part_offset_dict = {} #partname: (ielementstart, ielementend, buffer_length)
elements = None # self defined data type Element
points = None #vtk point set
center_points = {}

# delegate
progress_signal = uti.signal_center.update_progress_bar_signal
log_signal = uti.signal_center.log_signal
status_signal = uti.signal_center.update_status_signal

def init():
    global cgns_reader_module
    cgns_reader_module = None
    if platform.system() == 'Windows':
        cgns_reader_module = ct.windll.LoadLibrary('cgns_reader.dll')
    else:
        cgns_reader_module = ct.cdll.LoadLibrary('cgns_reader_dll.so')

    cgns_reader_module.read_file.argtypes = [ct.c_char_p, uint_p, uint_p, uint_p, int_p]
    cgns_reader_module.read_file.restype = ct.c_int
    cgns_reader_module.read_verts.restype = ct.c_int
    cgns_reader_module.read_element.argtypes = [ct.POINTER(ct.c_char_p), ct.POINTER(uint_p), ct.POINTER(ct.POINTER(Element)) ]
    cgns_reader_module.read_element.restype = ct.c_int
    cgns_reader_module.get_part_center.restype = ct.c_int
    cgns_reader_module.finalize.argtypes = []
    cgns_reader_module.finalize.restype = ct.c_int


def read_file(filename):
    nv = ct.c_size_t()
    nsec = ct.c_size_t()
    nelem = ct.c_size_t()
    type_flag = ct.c_int()

    # call c function
    check(cgns_reader_module.read_file(filename, ct.byref(nv), ct.byref(nsec), ct.byref(nelem), ct.byref(type_flag)))
    xcord = None
    ycord = None
    zcord = None
    xcenter = None
    ycenter = None
    zcenter = None
    if type_flag.value == 0:
        xcord = double_p()
        ycord = double_p()
        zcord = double_p()
        xcenter = double_p()
        ycenter = double_p()
        zcenter = double_p()
        set_vert_type(ct.POINTER(double_p))
    else:
        assert False
    # call c function
    check(cgns_reader_module.read_verts(ct.byref(xcord), ct.byref(ycord), ct.byref(zcord)))

    # call c function
    part_name_p = ct.c_char_p()
    part_offset_p = uint_p()
    elem_p = ct.POINTER(Element)()
    check(cgns_reader_module.read_element(ct.byref(part_name_p), ct.byref(part_offset_p), ct.byref(elem_p)) )

    # call c function
    check(cgns_reader_module.get_part_center(ct.byref(xcenter), ct.byref(ycenter), ct.byref(zcenter), type_flag))

    global nvert, nsection, nelement, part_offset_dict, elements, points, center_points
    nvert = nv.value
    nsection = nsec.value
    nelement = nelem.value
    part_name_list = part_name_p.value.split('@')
    for i in xrange(1, nsection + 1):
        part_offset_dict[part_name_list[i]] = (part_offset_p[i-1], part_offset_p[i])
    print part_offset_dict
    for i in xrange(1, nsection + 1):
        center_points[part_name_list[i]] = (xcenter[i-1], ycenter[i-1], zcenter[i-1])
    elements = elem_p
    points = vtk.vtkPoints()
    for i in xrange(0, nvert):
        points.InsertNextPoint(xcord[i], ycord[i], zcord[i])

def get_parts():
    for part_name, (istart, iend) in part_offset_dict.iteritems():
        cell_type_array = []
        cell_array = vtk.vtkCellArray()
        cell_array.SetNumberOfCells(iend - istart)
        # log
        if log_signal is not None: log_signal.emit('processing part:%s' % part_name)
        if status_signal is not None: status_signal.emit('loading mesh part: %s... please wait' % part_name)

        for idx in xrange(istart, iend):
            if (idx % ((iend - istart) / 100)) == 0 and progress_signal is not None:
                progress_signal.emit(int(idx / ((iend - istart) / 100)))
            this_elem = elements[idx]
            elem_type = this_elem.type
            cell_type_array.append(elem_type)
            npe = vtk_npe[elem_type]
            cell_array.InsertNextCell(npe, this_elem.pid[0: npe])
        if progress_signal is not None:
            progress_signal.emit(99)
        yield part_name, cell_array, cell_type_array

def get_cell_num_at_part(partname):
    return part_offset_dict[partname][1] - part_offset_dict[partname][0]

def deinit():
    cgns_reader_module.finalize()

# debug
if __name__ == '__main__':
    init()
    read_file('moxing1.cgns')
    for part_name, cell_array, cell_type_array in get_parts():
        ug = vtk.vtkUnstructuredGrid()
        ug.SetPoints(points)
        ug.SetCells(cell_type_array, cell_array)
        mapper =  vtk.vtkDataSetMapper()
        actor = vtk.vtkActor()
        mapper.SetInputData(ug)
        actor.SetMapper(mapper)
        ren = vtk.vtkRenderer()
        ren.AddActor(actor)
        iren = vtk.vtkRenderWindowInteractor()
        renwin = vtk.vtkRenderWindow()
        renwin.SetSize(400, 400)
        iren.SetRenderWindow(renwin)
        renwin.AddRenderer(ren)
        iren.Initialize()
        renwin.Render()
        iren.Start()

    deinit()
