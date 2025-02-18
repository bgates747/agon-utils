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
    float c, m, y, k; // CMYK values
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
int read_png(const char *filename, uint8_t **image_data, int *width, int *height);
int write_png(const char *filename, uint8_t *image_data, int width, int height);
uint8_t* load_png_to_rgba(const char *filename, int *width, int *height);
int save_rgba_to_png(const char *filename, uint8_t *image_data, int width, int height);

// ===========================
// 2. Color Conversion and Quantization
// ---------------------------
int _convert_to_palette_internal(uint8_t *buffer, int width, int height, const char *palette_file, const char *method, PyObject *transparent_color);
uint8_t* _rgba32_to_rgba2_internal(const uint8_t *rgba32, int width, int height);
void rgb_to_hsv_internal(uint8_t r, uint8_t g, uint8_t b, float *h, float *s, float *v);
void rgb_to_cmyk_internal(uint8_t r, uint8_t g, uint8_t b, float *c, float *m, float *y, float *k);
void hsv_to_rgb_internal(float h, float s, float v, uint8_t *r, uint8_t *g, uint8_t *b);
void cmyk_to_rgb_internal(float c, float m, float y, float k, uint8_t *r, uint8_t *g, uint8_t *b);
uint8_t quantize_channel(uint8_t channel);
uint8_t eight_to_two(uint8_t r, uint8_t g, uint8_t b, uint8_t a);
void two_to_eight(uint8_t pixel, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a);
int parse_color(PyObject *args, Color *color);
void quantize_to_rgb565(uint8_t *image_data, int width, int height);

// ===========================
// 3. Color Distance Calculations
// ---------------------------
float get_color_distance_rgb(const Color *color1, const Color *color2);
// float get_color_distance_hsv(const Color *color1, const Color *color2);
float get_color_distance_cmyk(const Color *color1, const Color *color2);

// ===========================
// 4. Palette Color Finding
// ---------------------------
int load_gimp_palette(const char *filename, Palette *palette);
const Color* find_nearest_color_rgb_internal(const Color *target_rgb, const Palette *palette);
const Color* find_nearest_color_hsv_internal(const Color *target_hsv, const Palette *palette);
const Color* find_nearest_color_cmyk_internal(const Color *target_cmyk, const Palette *palette);

// ===========================
// 5. Dithering Functions
// ---------------------------
void dither_atkinson(uint8_t* image_data, int width, int height, Palette *palette);
void dither_bayer(uint8_t* image_data, int width, int height, Palette *palette);
void dither_floyd_steinberg(uint8_t* image_data, int width, int height, Palette *palette);
// ===========================
// 6. Image Conversion Functions
// ---------------------------
void convert_image_rgb(uint8_t *image_data, int width, int height, Palette *palette, bool has_transparent_color, const uint8_t transparent_rgb[3]);
void convert_image_hsv(uint8_t *image_data, int width, int height, Palette *palette, bool has_transparent_color, const uint8_t transparent_rgb[3]);
void convert_image_cmyk(uint8_t *image_data, int width, int height, Palette *palette, bool has_transparent_color, const uint8_t transparent_rgb[3]);

// ===========================
// 8. Utility Functions
// ---------------------------
// Helper function to clamp values between 0 and 255
inline uint8_t clamp(int value) {
    if (value < 0) return 0;
    if (value > 255) return 255;
    return (uint8_t)value;
};

// ===================================================
// Prototypes for the Python C-extension entry points:
// ---------------------------------------------------
PyObject* convert_to_palette(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject* convert_to_palette_bytes(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject* convert_to_rgb565(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject* img_to_rgba2(PyObject *self, PyObject *args);
PyObject* img_to_rgba8(PyObject *self, PyObject *args);
PyObject* rgba32_to_rgba2_bytes(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject* rgba2_to_rgba32_bytes(PyObject *self, PyObject *args, PyObject *kwargs);
PyObject* rgba8_to_img(PyObject *self, PyObject *args);
PyObject* rgba2_to_img(PyObject *self, PyObject *args);
PyObject* rgb_to_hsv(PyObject *self, PyObject *args);
PyObject* rgb_to_cmyk(PyObject *self, PyObject *args);
PyObject* hsv_to_rgb(PyObject *self, PyObject *args);
PyObject* cmyk_to_rgb(PyObject *self, PyObject *args);
PyObject* find_nearest_color_rgb(PyObject *self, PyObject *args);
PyObject* find_nearest_color_hsv(PyObject *self, PyObject *args);
PyObject* find_nearest_color_cmyk(PyObject *self, PyObject *args);
PyObject* csv_to_palette(PyObject *self, PyObject *args);
PyObject* process_image_with_palette(PyObject *self, PyObject *args);

#ifdef __cplusplus
}
#endif

#endif // IMAGES_H
