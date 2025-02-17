#define PY_SSIZE_T_CLEAN
// Modules
#include "palettes.h"
#include "images.h"

// Python
#include <Python.h>
#include <stdio.h>
#include <time.h>
#include <stdlib.h>
#include <unistd.h>

// Function that prints Hello World and system information
static PyObject* hello(PyObject* self, PyObject* args) {
    time_t now = time(NULL);
    struct tm *t = localtime(&now);
    char hostname[256];
    gethostname(hostname, sizeof(hostname));
    
    printf("Hello, World!\n");
    printf("Package Name: agz\n");
    printf("Build Time: %s", asctime(t));
    printf("Host: %s\n", hostname);
    printf("Running on: %s\n", Py_GetPlatform());
    printf("Python Version: %s\n", Py_GetVersion());
    
    Py_RETURN_NONE;
}

// Function that inverts an rgba2222 data buffer by XORing each byte with 0x3F
static PyObject* invert(PyObject* self, PyObject* args) {
    Py_buffer view;

    // Parse the argument as a bytes-like object
    if (!PyArg_ParseTuple(args, "y*", &view)) {
        return NULL;
    }

    // Create a new bytes object for the result with the same size as the input
    PyObject* result = PyBytes_FromStringAndSize(NULL, view.len);
    if (result == NULL) {
        PyBuffer_Release(&view);
        return NULL;
    }

    char* src = (char*)view.buf;
    char* dest = PyBytes_AsString(result);
    for (Py_ssize_t i = 0; i < view.len; i++) {
        dest[i] = src[i] ^ 0x3F;  // XOR with 0x3F to invert the pixel
    }

    PyBuffer_Release(&view);
    return result;
}

// Method definitions for the module
static PyMethodDef MyMethods[] = {
// Testing Functions
    {"hello", hello, METH_NOARGS, "Print Hello World and system information"},
    {"invert", invert, METH_VARARGS, "Invert the colors of an rgba2222 buffer by XORing with 0x3F"},

// Image Functions

    // void convert_to_palette(const char *src_file, const char *tgt_file, const char *palette_file, const char *method, uint8_t *transparent_rgb);
    {"convert_to_palette", (PyCFunction)convert_to_palette, METH_VARARGS | METH_KEYWORDS, "Convert image to palette"},

    // PyObject* convert_to_palette_bytes(PyObject *self, PyObject *args, PyObject *kwargs);
    {"convert_to_palette_bytes", (PyCFunction)convert_to_palette_bytes, METH_VARARGS | METH_KEYWORDS, 
        "Convert an RGBA image (raw bytes) to a palette and return the processed bytes.\n\n"
        "Arguments:\n"
        "    image_data (bytes)  - Raw 32-bit RGBA image data.\n"
        "    width (int)         - Image width in pixels.\n"
        "    height (int)        - Image height in pixels.\n"
        "    palette_file (str)  - Path to the palette file (GIMP format).\n"
        "    method (str)        - Color conversion method ('RGB', 'HSV', 'CMYK', 'bayer', 'floyd', 'atkinson').\n"
        "    transparent_color (tuple, optional) - RGBA tuple defining a transparent color.\n\n"
        "Returns:\n"
        "    bytes - Processed 32-bit RGBA image data."
    },
    
    // void convert_to_rgb565(const char *src_file, const char *tgt_file);
    {"convert_to_rgb565", (PyCFunction)convert_to_rgb565, METH_VARARGS | METH_KEYWORDS, "Convert image to RGB565"},

    // void img_to_rgba2(const char *input_filepath, const char *output_filepath);
    {"img_to_rgba2", img_to_rgba2, METH_VARARGS, "Convert an image to 2-bit RGBA and save to a file"},

    // void img_to_rgba8(const char *input_filepath, const char *output_filepath);
    {"img_to_rgba8", img_to_rgba8, METH_VARARGS, "Convert an image to RGBA8 and save to a file"},

    // void rgba8_to_img(const char *input_filepath, const char *output_filepath, int width, int height);
    {"rgba8_to_img", rgba8_to_img, METH_VARARGS, "Convert RGBA8 binary file to image"},

    // void rgba2_to_img(const char *input_filepath, const char *output_filepath, int width, int height);
    {"rgba2_to_img", rgba2_to_img, METH_VARARGS, "Convert RGBA2 binary file to image"},

    // Converts RGB to HSV (normalized 0-1)
    // float rgb_to_hsv(uint8_t r, uint8_t g, uint8_t b, float *h, float *s, float *v);
    {"rgb_to_hsv", rgb_to_hsv, METH_VARARGS, "Convert RGB to HSV"},

    // Converts RGB to CMYK (normalized 0-1)
    // float rgb_to_cmyk(uint8_t r, uint8_t g, uint8_t b, float *c, float *m, float *y, float *k);
    {"rgb_to_cmyk", rgb_to_cmyk, METH_VARARGS, "Convert RGB to CMYK"},

    // Converts HSV to RGB
    // void hsv_to_rgb(float h, float s, float v, uint8_t *r, uint8_t *g, uint8_t *b);
    {"hsv_to_rgb", hsv_to_rgb, METH_VARARGS, "Convert HSV to RGB"},

    // Converts CMYK to RGB
    // void cmyk_to_rgb(float c, float m, float y, float k, uint8_t *r, uint8_t *g, uint8_t *b);
    {"cmyk_to_rgb", cmyk_to_rgb, METH_VARARGS, "Convert CMYK to RGB"},

    // Function: Find the nearest RGB color in the palette
    // const Color* find_nearest_color_rgb(const Color *target_rgb, const Palette *palette);
    {"find_nearest_color_rgb", find_nearest_color_rgb, METH_VARARGS, "Find the nearest RGB color in the palette"},

    // Function: Find the nearest HSV color in the palette
    // const Color* find_nearest_color_hsv(const Color *target_hsv, const Palette *palette);
    {"find_nearest_color_hsv", find_nearest_color_hsv, METH_VARARGS, "Find the nearest HSV color in the palette"},

    // Function: Find the nearest CMYK color in the palette
    // const Color* find_nearest_color_cmyk(const Color *target_cmyk, const Palette *palette);
    {"find_nearest_color_cmyk", find_nearest_color_cmyk, METH_VARARGS, "Find the nearest CMYK color in the palette"},

    // Function: Convert a CSV file to a Palette object
    // Palette* csv_to_palette(const char *csv_filepath);
    {"csv_to_palette", csv_to_palette, METH_VARARGS, "Convert a CSV file to a Palette object"},

    // Function: Process an image with a palette
    // uint8_t* process_image_with_palette(const char* palette_filepath, float hue, int width, int height);
    {"process_image_with_palette", process_image_with_palette, METH_VARARGS, "Process an image with a palette"},
   

// Sentinel to end the list
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef agzmodule = {
    PyModuleDef_HEAD_INIT,
    "agz",  // Module name
    NULL,
    -1,
    MyMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_agz(void) {
    return PyModule_Create(&agzmodule);
}
