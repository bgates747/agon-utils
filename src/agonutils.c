#define PY_SSIZE_T_CLEAN

#include "images.h"

// Function: Simple hello world function
PyObject* hello(PyObject* self, PyObject* args) {
    printf("Hello world from agonutils!\n");
    Py_RETURN_NONE;
}

// Define the methods callable from Python
static PyMethodDef MyMethods[] = {
    {"convert_to_palette", (PyCFunction)convert_to_palette, METH_VARARGS | METH_KEYWORDS, 
     "convert_to_palette(src_file: str, tgt_file: str, palette_file: str, method: str, use_transparent: bool = False, transparent_rgb: tuple[int, int, int] = (0, 0, 0)) -> None"},
    
    {"img_to_rgba2", (PyCFunction)img_to_rgba2, METH_VARARGS | METH_KEYWORDS, 
     "img_to_rgba2(src_file: str, tgt_file: str, palette_file: str, method: str, use_transparent: bool = False, transparent_rgb: tuple[int, int, int] = (0, 0, 0)) -> None"},
    
    {"rgba8_to_img", rgba8_to_img, METH_VARARGS, 
     "rgba8_to_img(input_filepath: str, output_filepath: str, width: int, height: int) -> None"},
    
    {"rgba2_to_img", rgba2_to_img, METH_VARARGS, 
     "rgba2_to_img(input_filepath: str, output_filepath: str, width: int, height: int) -> None"},
    
    {"csv_to_palette", csv_to_palette, METH_VARARGS, 
     "csv_to_palette(csv_filepath: str) -> Palette"},
    
    {"hello", hello, METH_NOARGS, 
     "hello() -> None"},
    
    {NULL, NULL, 0, NULL}  // Sentinel value to indicate end of methods array
};


// Module definition
static struct PyModuleDef agonutilsmodule = {
    PyModuleDef_HEAD_INIT,
    "agonutils",  // Module name
    NULL,
    -1,
    MyMethods  // Method table
};

// Module initialization function
PyMODINIT_FUNC PyInit_agonutils(void) {
    return PyModule_Create(&agonutilsmodule);
}
