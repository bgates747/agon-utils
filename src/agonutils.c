#define PY_SSIZE_T_CLEAN
// Modules
#include "palettes.h"
#include "images.h"
#include "agm.h"
#include "rle.h"
#include "simz.h"

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
    printf("Package Name: agonutils\n");
    printf("Build Time: %s", asctime(t));
    printf("Host: %s\n", hostname);
    printf("Running on: %s\n", Py_GetPlatform());
    printf("Python Version: %s\n", Py_GetVersion());
    
    Py_RETURN_NONE;
}

// Python wrapper for process_mp4
// Python-facing function (exported as process_mp4).
// This function expects the following arguments from Python:
//   input_file (str)
//   output_file (str)
//   output_width (int)
//   output_height (int)
//   palette_file (str)
//   noDither_method (str)
//   dither_method (str)
//   lookback (int)
//   transparent_color (tuple, optional)
PyObject* process_mp4(PyObject *self, PyObject *args, PyObject *kwargs) {
    const char *input_file, *output_file, *palette_file, *noDither_method, *dither_method;
    int output_width, output_height, lookback;
    PyObject *transparent_color = Py_None;

    static char *kwlist[] = {"input_file", "output_file", "output_width", "output_height",
                             "palette_file", "noDither_method", "dither_method", "lookback", "transparent_color", NULL};

    // Note: no spaces in the format string
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssiisssi|O", kwlist,
                                     &input_file, &output_file, &output_width, &output_height,
                                     &palette_file, &noDither_method, &dither_method, &lookback, &transparent_color)) {
        return NULL;
    }

    int ret = _process_mp4_internal(input_file, output_file, output_width, output_height,
                                    palette_file, noDither_method, dither_method, lookback, transparent_color);
    return PyLong_FromLong(ret);
}

// Python wrapper for RLE compression
PyObject* rle_encode(PyObject *self, PyObject *args) {
    Py_buffer input_data;
    if (!PyArg_ParseTuple(args, "y*", &input_data)) {
        return NULL;
    }

    size_t output_size;
    uint8_t *compressed = _rle_encode_internal((uint8_t *)input_data.buf, input_data.len, &output_size);
    if (!compressed) {
        PyBuffer_Release(&input_data);
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate RLE output");
        return NULL;
    }

    PyObject *result = PyBytes_FromStringAndSize((char *)compressed, output_size);
    free(compressed);
    PyBuffer_Release(&input_data);
    return result;
}

/**
 * rle_decode - Python wrapper for _rle_decode_internal.
 *
 * Expects a single argument: a bytes object containing RLE-encoded rgba2222 data.
 * Returns a bytes object containing the decoded raw data.
 */
static PyObject* rle_decode(PyObject *self, PyObject *args) {
    Py_buffer input_buf;
    if (!PyArg_ParseTuple(args, "y*", &input_buf)) {
        return NULL;
    }
    
    size_t decoded_size = 0;
    uint8_t *decoded = _rle_decode_internal((const uint8_t *)input_buf.buf, input_buf.len, &decoded_size);
    PyBuffer_Release(&input_buf);
    
    if (!decoded) {
        PyErr_SetString(PyExc_RuntimeError, "RLE decoding failed.");
        return NULL;
    }
    
    PyObject *result = Py_BuildValue("y#", decoded, decoded_size);
    free(decoded);
    return result;
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
    // ============================================================================
    // Testing Functions
    // ----------------------------------------------------------------------------
    {"hello", hello, METH_NOARGS, "Print Hello World and system information"},
    {"invert", invert, METH_VARARGS, "Invert the colors of an rgba2222 buffer by XORing with 0x3F"},

    // ============================================================================
    // Image Functions
    // ----------------------------------------------------------------------------
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

    {"rgba32_to_rgba2_bytes", (PyCFunction)rgba32_to_rgba2_bytes, METH_VARARGS | METH_KEYWORDS,
        "Convert raw 32-bit RGBA bytes to packed 2-bit RGBA (RGBA2) bytes.\n\n"
        "Arguments:\n"
        "  rgba32 (bytes) : Raw image data (width * height * 4 bytes).\n"
        "  width (int)    : Image width in pixels.\n"
        "  height (int)   : Image height in pixels.\n\n"
        "Returns:\n"
        "  bytes : Packed RGBA2 data (1 byte per pixel)."
    },
    {"rgba2_to_rgba32_bytes", (PyCFunction)rgba2_to_rgba32_bytes, METH_VARARGS | METH_KEYWORDS,
        "Convert packed 2-bit RGBA (RGBA2) bytes to raw 32-bit RGBA bytes.\n\n"
        "Arguments:\n"
        "  rgba2 (bytes) : Packed RGBA2 data (width * height bytes).\n"
        "  width (int)   : Image width in pixels.\n"
        "  height (int)  : Image height in pixels.\n\n"
        "Returns:\n"
        "  bytes : Raw 32-bit RGBA image data (width * height * 4 bytes)."
    },

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
  
    // ============================================================================
    // Agon Movie Functions
    // ----------------------------------------------------------------------------
    {"process_mp4", (PyCFunction)process_mp4, METH_VARARGS | METH_KEYWORDS,
        "Process an MP4 file by extracting frames, applying palette conversion with differencing, and producing a custom movie file.\n\n"
        "Arguments:\n"
        "  input_file (str): Path to the input MP4 file.\n"
        "  output_file (str): Path to the output movie file.\n"
        "  output_width (int): Frame width.\n"
        "  output_height (int): Frame height.\n"
        "  palette_file (str): Path to the palette file (GIMP format).\n"
        "  noDither_method (str): Method for base (no-dither) conversion (e.g., \"RGB\").\n"
        "  dither_method (str): Method for dithered conversion (e.g., \"floyd\", \"bayer\").\n"
        "  lookback (int): Threshold for consecutive unchanged frames before forcing new dithering.\n"
        "  transparent_color (tuple, optional): RGBA tuple for transparency.\n\n"
        "Returns:\n"
        "  int: 0 on success, negative on failure."},

    // ============================================================================
    // Compression functions
    // ----------------------------------------------------------------------------
    // RLE encoding
    // ----------------------------------------------------------------------------
    {"rle_encode", rle_encode, METH_VARARGS, "Compress raw RGBA2 data using RLE."},
    {"rle_decode", rle_decode, METH_VARARGS, "Decompress RLE-encoded data."},

    // ----------------------------------------------------------------------------
    // SimZ functions
    /**
     * Compress a file using the simz encoder.
     * Python call signature: `simz_encode(input_file: str, output_file: str) -> None`
     * 
     * Arguments:
     *   - input_file: Path to the input file (string)
     *   - output_file: Path to the output file (string)
     */
    {"simz_encode", simz_encode, METH_VARARGS, "Compress a file using the simz encoder."},
    /**
     * Decompress a file using the simz decoder.
     * Python call signature: `simz_decode(input_file: str, output_file: str) -> None`
     * 
     * Arguments:
     *   - input_file: Path to the input file (string)
     *   - output_file: Path to the output file (string)
     */
    {"simz_decode", simz_decode, METH_VARARGS, "Decompress a file using the simz decoder."},

// ============================================================================
// Sentinel to end the list
// ----------------------------------------------------------------------------
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef agzmodule = {
    PyModuleDef_HEAD_INIT,
    "agonutils",  // Module name
    NULL,
    -1,
    MyMethods
};

// Module initialization function
PyMODINIT_FUNC PyInit_agonutils(void) {
    return PyModule_Create(&agzmodule);
}
