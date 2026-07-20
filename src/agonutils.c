#include "images.h"
#include "simz.h"

// Function: Simple hello world function
PyObject* hello(PyObject* self, PyObject* args) {
    printf("Hello world from agonutils!\n");
    Py_RETURN_NONE;
}

// Define the methods callable from Python
static PyMethodDef MyMethods[] = {
    {"convert_to_palette", (PyCFunction)convert_to_palette, METH_VARARGS | METH_KEYWORDS, 
     "convert_to_palette(src_file: str, tgt_file: str, palette_file: str, palette_conversion_method: str, transparent_color: Optional[tuple[int, int, int]] = None) -> None"},
    
    {"img_to_rgba2", (PyCFunction)img_to_rgba2, METH_VARARGS | METH_KEYWORDS, 
     "img_to_rgba2(src_file: str, tgt_file: str, palette_file: str, palette_conversion_method: str, transparent_color: Optional[tuple[int, int, int]] = None) -> None"},
    
    {"rgba8_to_img", rgba8_to_img, METH_VARARGS, 
     "rgba8_to_img(input_filepath: str, output_filepath: str, width: int, height: int) -> None"},
    
    {"rgba2_to_img", rgba2_to_img, METH_VARARGS, 
     "rgba2_to_img(input_filepath: str, output_filepath: str, width: int, height: int) -> None"},
    
    {"csv_to_palette", csv_to_palette, METH_VARARGS, 
     "csv_to_palette(csv_filepath: str) -> Palette"},

    {"simz_encode", simz_encode, METH_VARARGS,
     "simz_encode(input_file: str, output_file: str) -> None"},

    {"simz_decode", simz_decode, METH_VARARGS,
     "simz_decode(input_file: str, output_file: str) -> None"},

    {"simz_encode_bytes", simz_encode_bytes, METH_VARARGS,
     "simz_encode_bytes(data: bytes) -> bytes"},

    {"simz_decode_bytes", simz_decode_bytes, METH_VARARGS,
     "simz_decode_bytes(data: bytes) -> bytes"},
    
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
