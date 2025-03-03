#ifndef IMAGES_H
#define IMAGES_H

#ifdef __cplusplus
extern "C" {
#endif

#include <Python.h>
#include <math.h>
#include <stdint.h>
#include <stdlib.h>
#include <stdio.h>
#include <png.h>
#include <stdbool.h>

typedef struct {
    uint8_t r, g, b;  // RGB values
    float h, s, v;    // HSV values
    char name[64];    // Color name
} Color;

typedef struct {
    Color *colors;  // Array of colors
    size_t size;    // Number of colors in the palette
} Palette;

static const uint8_t bayer_matrix[4][4] = {
    {   0, 136,  34, 170 },
    { 204,  68, 238, 102 },
    {  51, 187,  17, 153 },
    { 255, 119, 221,  85 }
};

// ===========================
// Function prototypes
// ===========================
// 1. Image I/O (Reading and Writing PNG)
// ---------------------------
int _read_png(const char *filename, uint8_t **image_data, int *width, int *height);
int _write_png(const char *filename, uint8_t *image_data, int width, int height);

// ===========================
// 2. Color Conversion and Quantization
// ---------------------------
void _rgb_to_hsv(uint8_t r, uint8_t g, uint8_t b, float *h, float *s, float *v);
void _hsv_to_rgb(float h, float s, float v, uint8_t *r, uint8_t *g, uint8_t *b);
uint8_t _quantize_channel(uint8_t channel);
uint8_t _eight_to_two(uint8_t r, uint8_t g, uint8_t b, uint8_t a);
void _two_to_eight(uint8_t pixel, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a);
void _rgba32_to_rgba2(uint8_t *image_data, size_t num_pixels, uint8_t *output_buffer);
int _parse_color(PyObject *args, Color *color);

// ===========================
// 3. Color Distance Calculations
// ---------------------------
float _distance_rgb(const Color *color1, const Color *color2);

// ===========================
// 4. Palette Color Finding
// ---------------------------
int _load_gimp_palette(const char *filename, Palette *palette);
const Color* _nearest_rgb(const Color *target_rgb, const Palette *palette);
const Color* _nearest_hsv(const Color *target_hsv, const Palette *palette);

// ===========================
// 5. Dithering Functions
// ---------------------------
void _convert_atkinson(uint8_t* image_data, int width, int height, Palette *palette);
void _convert_bayer(uint8_t* image_data, int width, int height, Palette *palette);
void _convert_floyd_steinberg(uint8_t* image_data, int width, int height, Palette *palette);

// ===========================
// 6. Image Conversion Functions
// ---------------------------
void _convert_method_rgb(uint8_t *image_data, int width, int height, Palette *palette, bool has_transparent_color, const uint8_t transparent_rgb[3]);
void _convert_method_hsv(uint8_t *image_data, int width, int height, Palette *palette, bool has_transparent_color, const uint8_t transparent_rgb[3]);
bool _parse_transparent_color(PyObject *transparent_color, uint8_t transparent_rgb[3]);
bool _parse_palette_conversion_args(PyObject *args, PyObject *kwargs, const char **src_file, const char **tgt_file, const char **palette_file, const char **palette_conversion_method, uint8_t **image_data, int *width, int *height, Palette *palette, bool *use_transparent, uint8_t transparent_rgb[3]);
uint8_t* _convert_to_palette(uint8_t *image_data, int width, int height, Palette *palette, const char *palette_conversion_method, bool use_transparent, uint8_t transparent_rgb[3]);

// ===========================
// 8. Utility Functions
// ---------------------------
uint8_t _clamp_256(int value);

// ===================================================
// Prototypes for the Python C-extension entry points:
// ---------------------------------------------------

// convert_to_palette(src_file, tgt_file, palette_file, palette_conversion_method, transparent_color)
PyObject* convert_to_palette(PyObject *self, PyObject *args, PyObject *kwargs);

// img_to_rgba2(src_file, tgt_file, palette_file, palette_conversion_method, transparent_color)
PyObject* img_to_rgba2(PyObject *self, PyObject *args, PyObject *kwargs);

// rgba8_to_img(input_filepath, output_filepath, width, height)
PyObject* rgba8_to_img(PyObject *self, PyObject *args);

// rgba2_to_img(input_filepath, output_filepath, width, height)
PyObject* rgba2_to_img(PyObject *self, PyObject *args);

// csv_to_palette(csv_filepath)
PyObject* csv_to_palette(PyObject *self, PyObject *args);


#ifdef __cplusplus
}
#endif

#endif // IMAGES_H