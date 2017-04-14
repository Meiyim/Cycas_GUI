import ctypes as ct
import numpy as np
import vtk


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


def vtk_cell_factory(gmsh_elem):
    ret = None
    npe = 0
    if gmsh_elem.type == 2:
        ret = vtk.vtkTriangle()
        npe = 3
    elif gmsh_elem.type == 3:
        ret = vtk.vtkQuad()
        npe = 4
    elif gmsh_elem.type == 4:
        ret = vtk.vtkTetra()
        npe = 4
    elif gmsh_elem.type == 5:
        ret = vtk.vtkHexahedron()
        npe = 8
    elif gmsh_elem.type == 6: #gmsh-triangle prism
        ret = vtk.vtkWedge()
        npe = 6
    elif gmsh_elem.type == 7:
        ret = vtk.vtkPyramid()
        npe = 5
    else:
        raise CGNSException('unknown gmsh type %d' % gmsh_elem.type)
    ids = ret.GetPointIds()
    for i, index in zip(xrange(0, npe), gmsh_elem.pid[0: npe]):
        ids.SetId(i, index)
    return ret

# type alias
uint_p = ct.POINTER(ct.c_size_t)
int_p = ct.POINTER(ct.c_int)
double_p = ct.POINTER(ct.c_double)

cgns_reader_module = None
nvert = None
nsection = None
nelement = None
part_offset_dict = {}
elements = None
points = None


def init():
    global cgns_reader_module
    cgns_reader_module = np.ctypeslib.load_library('cgns_reader_module.so', '.')
    cgns_reader_module.read_file.argtypes = [ct.c_char_p, uint_p, uint_p, uint_p, int_p]
    cgns_reader_module.read_file.restype = ct.c_int
    cgns_reader_module.read_verts.restype = ct.c_int
    cgns_reader_module.read_element.argtypes = [ct.POINTER(ct.c_char_p), ct.POINTER(uint_p), ct.POINTER(ct.POINTER(Element)) ]
    cgns_reader_module.read_element.restype = ct.c_int
    cgns_reader_module.finalize.argtypes = []
    cgns_reader_module.finalize.restype = ct.c_int


def read_file(filename):
    nv = ct.c_size_t()
    nsec = ct.c_size_t()
    nelem = ct.c_size_t()
    type_flag = ct.c_int()
    check(cgns_reader_module.read_file(filename, ct.byref(nv), ct.byref(nsec), ct.byref(nelem), ct.byref(type_flag)))
    xcord = None
    ycord = None
    zcord = None
    if type_flag.value == 0:
        xcord = double_p()
        ycord = double_p()
        zcord = double_p()
        set_vert_type(ct.POINTER(double_p))
        check(cgns_reader_module.read_verts(ct.byref(xcord), ct.byref(ycord), ct.byref(zcord)))
    else:
        assert False
    part_name_p = ct.c_char_p()
    part_offset_p = uint_p()
    elem_p = ct.POINTER(Element)()
    check( cgns_reader_module.read_element(ct.byref(part_name_p), ct.byref(part_offset_p), ct.byref(elem_p)) )
    global nvert, nsection, nelement, part_offset_dict, elements, points
    nvert = nv.value
    nsection = nsec.value
    nelement = nelem.value
    part_name_list = part_name_p.value.split('@')
    for i in xrange(1, nsection + 1):
        part_offset_dict[part_name_list[i]] = (part_offset_p[i-1], part_offset_p[i])
    print part_offset_dict
    elements = elem_p
    points = vtk.vtkPoints()
    for i in xrange(0, nvert):
        points.InsertNextPoint(xcord[i], ycord[i], zcord[i])

def get_parts():
    return part_offset_dict.keys()

def get_cell_num_at_part(partname):
    return part_offset_dict[partname][1] - part_offset_dict[partname][0]

def get_cell_at_part(partname):
    for i in xrange(part_offset_dict[partname][0], part_offset_dict[partname][1]):
        this_elem = elements[i]
        cell = vtk_cell_factory(this_elem)
        yield  cell

def deinit():
    cgns_reader_module.finalize()

# debug
if __name__ == '__main__':
    init()
    read_file('moxing1.cgns')
    for part_name in get_parts():
        ug = vtk.vtkUnstructuredGrid()
        ug.SetPoints(points)
        nelem = get_cell_num_at_part(part_name)
        for istep, cell in enumerate(get_cell_at_part(part_name)):
            cell_type = cell.GetCellType()
            ug.InsertNextCell(cell_type, cell.GetPointIds())
    deinit()
