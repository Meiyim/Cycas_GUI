#include<stdio.h>
#include<stdlib.h>
#include<stddef.h>
#include<string.h>
#include<assert.h>

#include<cgnslib.h>
#define ERROR_CHECK(command) do{if(command) {fprintf(stderr, "CGNS error at line %d:%s\n", __LINE__,cg_get_error()); return 1;}} while(0)
#define CGNS_VERBOSE

#ifdef _MSC_VER
#pragma comment(lib, "cgns.lib")
#define DLL_EXPORT __declspec( dllexport )
#else
#define DLL_EXPORT
#endif

typedef struct Element{
    int type;
    size_t pid[8];
} Element;

static int cgns_file = 0;
static int ibase = 1; //always == 1
static int izone = 1; //always == 1
static cgsize_t nvert = 0;
static int nsection = 0;
static int ncords = 0;
static cgsize_t nelem = 0;
static void* global_xcord = NULL;
static void* global_ycord = NULL;
static void* global_zcord = NULL;
static Element* global_elem_list = NULL;
static char* global_part_name = NULL;
static size_t* global_part_offset = NULL;
static DataType_t cord_datatype;

DLL_EXPORT int read_file(const char*, size_t*, size_t*, size_t*, int*);
DLL_EXPORT int read_verts(void**, void**, void**);
DLL_EXPORT int read_element(char**, size_t**, Element**);
DLL_EXPORT int finalize();

int vtk_type(ElementType_t cgns_type, int* gmsh_type){
    switch(cgns_type){
    case TRI_3:
        *gmsh_type = 5; break;
    case QUAD_4:
        *gmsh_type = 9; break;
    case TETRA_4:
        *gmsh_type = 10; break;
    case PYRA_5:
        *gmsh_type = 14; break;
    case PENTA_6:
        *gmsh_type = 13; break;
    case HEXA_8:
        *gmsh_type = 12; break;
    default:
        fprintf(stderr, "unknown element type %s\n", cg_ElementTypeName(cgns_type)); 
        return -1;
    }
    return 0;
}

int read_file(const char* title, size_t* arg_nv, size_t* arg_nsec, size_t* arg_nelem, int* type_flag){
    float version;
    ERROR_CHECK(cg_open(title, CG_MODE_READ, &cgns_file));
    ERROR_CHECK(cg_version(cgns_file, &version));
#ifdef CGNS_VERBOSE
    printf("CGNS file version %f\n", version);
#endif 
    //read points
    ZoneType_t zonetype;
    char charbuffer[512];
    cgsize_t size;   //size == node size
    ERROR_CHECK(cg_zone_read(cgns_file, ibase, izone, charbuffer, &size)); 
    nvert = size;
    ERROR_CHECK(cg_zone_type(cgns_file, ibase, izone, &zonetype));
#ifdef CGNS_VERBOSE
    printf("Zone %d:\"%s\"size: %ld type: %s\n", izone, charbuffer, size, cg_ZoneTypeName(zonetype));
#endif
    if (zonetype != Unstructured) {
        printf("unsupported zone type %s\n", cg_ZoneTypeName(zonetype));
    }
    ERROR_CHECK(cg_coord_info(cgns_file, ibase, izone, 1, &cord_datatype, charbuffer)); //assuming all cord has the same data type
    ERROR_CHECK(cg_ncoords(cgns_file, ibase, izone, &ncords));
    ERROR_CHECK(cg_nsections(cgns_file, ibase, izone, &nsection));
#ifdef CGNS_VERBOSE
    printf("ncoords %u npart %u\n", ncords, nsection);
#endif
    if (!strcmp(cg_DataTypeName(cord_datatype), "RealDouble")) {
        *type_flag = 0; 
    } else if (!strcmp(cg_DataTypeName(cord_datatype), "RealSingle")) {
        *type_flag = 1;
    } else {
		*type_flag = -1;
	}
    cgsize_t istart = 0, iend = 0;
    int nbnd = 0, parent_flag = 0;
    ElementType_t type;
    for (int isec = 1; isec <= nsection; ++isec) {
        //ERROR_CHECK(cg_ElementDataSize(cgns_file, ibase, izone, isec, &sec_data_size));
        ERROR_CHECK(cg_section_read(cgns_file, ibase, izone, isec, charbuffer, &type,
                                    &istart, &iend, &nbnd, &parent_flag));
        nelem += (iend - istart) + 1; //add type info for not mixed cell
    }
    *arg_nv = nvert;
    *arg_nsec = nsection;
    *arg_nelem = nelem;
    return 0;
}

int read_verts(void** xcord, void** ycord, void** zcord){
    assert(ncords == 3);
    void* buffer = NULL;
    char charbuffer[512];
    cgsize_t range_min = 1, range_max = nvert;

    for (int idim = 1; idim <= ncords; ++idim) {
        if (!strcmp(cg_DataTypeName(cord_datatype), "RealDouble")) {
            buffer = malloc(nvert * sizeof(double));
        } else if (!strcmp(cg_DataTypeName(cord_datatype), "RealSingle")) {
            buffer = malloc(nvert * sizeof(float));
        } else {
			assert(0);
		}
		ERROR_CHECK(cg_coord_info(cgns_file, ibase, izone, idim, &cord_datatype, charbuffer));
        printf("base%d zone%d cord_type%d range_min%d range_max%d \n name:%s\n",
                ibase, izone, cord_datatype, range_min, range_max, charbuffer);
        ERROR_CHECK(cg_coord_read(cgns_file, ibase, izone, charbuffer, cord_datatype, &range_min, &range_max, buffer));
        switch(idim){
            case 1: *xcord = buffer; global_xcord = buffer; break; 
            case 2: *ycord = buffer; global_ycord = buffer; break;
            case 3: *zcord = buffer; global_zcord = buffer; break;
            default: printf("unknown coordinate %d\n", idim); return 1;
        }
#ifdef CGNS_VERBOSE
        printf("%s: type: %s %ld --> %ld \n", charbuffer, cg_DataTypeName(cord_datatype), range_min, range_max);
#endif
    }
    return 0;
}

int read_element(char** part_name, size_t** part_offset, Element** elem_list){
    char charbuffer[512];
    ElementType_t type;
    cgsize_t istart, iend, sec_data_size; 
    int parent_flag = 0, nbnd = 0;

    cgsize_t* pid = NULL;
    *elem_list = (Element*) malloc(nelem * sizeof(Element));
    *part_offset = (size_t*) malloc((nsection + 1) * sizeof(size_t));
    *part_name = (char*) malloc(nsection * 512 * sizeof(char));
    Element* elem_list_iter = *elem_list;
    size_t* part_offset_iter = *part_offset;
    char* part_name_iter = *part_name;
    part_offset_iter[0] = 0;
    for (int isec = 1; isec <= nsection; ++isec) {
        *(part_name_iter++) = '@';
        ERROR_CHECK(cg_section_read(cgns_file, ibase, izone, isec, charbuffer, &type,
                                    &istart, &iend, &nbnd, &parent_flag));
#ifdef _MSC_VER
        strcpy_s(part_name_iter, 1024, charbuffer);
#else
        strcpy(part_name_iter, charbuffer);
#endif
        part_name_iter += strlen(charbuffer);
        ERROR_CHECK(cg_ElementDataSize(cgns_file, ibase, izone, isec, &sec_data_size));
        pid = (cgsize_t*)malloc(sec_data_size * sizeof(cgsize_t));
        ERROR_CHECK(cg_elements_read(cgns_file, ibase, izone, isec, pid, NULL));
        cgsize_t nelem_sec = iend - istart + 1;

		printf("section: %s type: %s size: %u\n", charbuffer, cg_ElementTypeName(type), nelem_sec);
        int npe = 0;
        size_t counter = 0;
        if (type != MIXED) {
            ERROR_CHECK(cg_npe(type, &npe));
            for (int iele = 0; iele != nelem_sec; ++iele) {
                Element* this_element = elem_list_iter++;
                if(vtk_type(type, &this_element->type)) return -1;
                for (int j = 0; j != npe; ++j) {
                    this_element->pid[j] = pid[iele * npe + j] - 1; //why -1???
                }
				for (int j = npe; j != 8; ++j) {
                    this_element->pid[j] = - 1;
				}
            }
        } else {
            for (int iele = 0; iele != nelem_sec; ++iele) {
				ElementType_t cell_type = (ElementType_t) pid[counter++];
				ERROR_CHECK(cg_npe(cell_type, &npe));
				Element* this_element = elem_list_iter++;
				if(vtk_type(cell_type, &this_element->type)) return -1;
				for (int j = 0; j != npe; ++j) {
					this_element->pid[j] = pid[counter++] - 1; //why -1???
				}
				for (int j = npe; j != 8; ++j) {
                    this_element->pid[j] = - 1;
				}
			}
        }
        part_offset_iter[isec] = part_offset_iter[isec - 1] + nelem_sec;
        free(pid);
    }
	for (int i = 0; i != nsection + 1; ++i) {
		printf("offset in c %u\n", part_offset_iter[i]);
	}
    global_elem_list = *elem_list;
    global_part_offset = *part_offset;
    global_part_name = *part_name;
    return 0;
}

int finalize(){
    free(global_xcord);
    free(global_ycord);
    free(global_zcord);
    free(global_elem_list);
    free(global_part_offset);
    free(global_part_name);
    ERROR_CHECK(cg_close(cgns_file));
    return 0;
}

