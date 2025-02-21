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
    "Convert a PNG image to use a custom palette."},
       
    {"img_to_rgba2", (PyCFunction)img_to_rgba2, METH_VARARGS | METH_KEYWORDS, 
    "Convert a PNG image to a custom palette and save as an RGBA2 binary file."},

    {"rgba8_to_img", rgba8_to_img, METH_VARARGS, 
     "Convert RGBA8 binary file to image"},
    
    {"rgba2_to_img", rgba2_to_img, METH_VARARGS, 
     "Convert RGBA2 binary file to image"},

    {"csv_to_palette", csv_to_palette, METH_VARARGS, "Convert a CSV file to a Palette object"},
    
    {"hello", hello, METH_NOARGS, 
     "Print Hello World"},
    
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
