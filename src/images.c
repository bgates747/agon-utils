#include "images.h"
#include <math.h>
#include <float.h>  // For FLT_MAX (instead of INFINITY)

// Helper function to read a PNG file into RGBA format
int _read_png(const char *filename, uint8_t **image_data, int *width, int *height) {
    FILE *fp = fopen(filename, "rb");
    if (!fp) {
        fprintf(stderr, "Failed to open file: %s\n", filename);
        return 0;
    }

    png_structp png = png_create_read_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    if (!png) return 0;

    png_infop info = png_create_info_struct(png);
    if (!info) return 0;

    if (setjmp(png_jmpbuf(png))) {
        fclose(fp);
        return 0;
    }

    png_init_io(png, fp);
    png_read_info(png, info);

    *width = png_get_image_width(png, info);
    *height = png_get_image_height(png, info);
    png_byte color_type = png_get_color_type(png, info);
    png_byte bit_depth = png_get_bit_depth(png, info);

    // Ensure the image is in 8-bit per channel RGBA format
    if (bit_depth == 16) png_set_strip_16(png);
    if (color_type == PNG_COLOR_TYPE_PALETTE) png_set_palette_to_rgb(png);
    if (color_type == PNG_COLOR_TYPE_GRAY && bit_depth < 8) png_set_expand_gray_1_2_4_to_8(png);
    if (png_get_valid(png, info, PNG_INFO_tRNS)) png_set_tRNS_to_alpha(png);

    if (color_type == PNG_COLOR_TYPE_RGB || color_type == PNG_COLOR_TYPE_GRAY || color_type == PNG_COLOR_TYPE_PALETTE)
        png_set_filler(png, 0xFF, PNG_FILLER_AFTER);

    if (color_type == PNG_COLOR_TYPE_GRAY || color_type == PNG_COLOR_TYPE_GRAY_ALPHA)
        png_set_gray_to_rgb(png);

    png_read_update_info(png, info);

    // Allocate memory for RGBA data
    *image_data = (uint8_t *)malloc(*width * *height * 4);
    if (!*image_data) {
        fclose(fp);
        png_destroy_read_struct(&png, &info, NULL);
        return 0;
    }

    png_bytep rows[*height];
    for (int y = 0; y < *height; y++) {
        rows[y] = *image_data + y * (*width * 4);
    }

    png_read_image(png, rows);

    fclose(fp);
    png_destroy_read_struct(&png, &info, NULL);
    return 1;
}

// Helper function to write RGBA data to a PNG file
int _write_png(const char *filename, uint8_t *image_data, int width, int height) {
    FILE *fp = fopen(filename, "wb");
    if (!fp) {
        fprintf(stderr, "Failed to open file for writing: %s\n", filename);
        return 0;
    }

    png_structp png = png_create_write_struct(PNG_LIBPNG_VER_STRING, NULL, NULL, NULL);
    if (!png) return 0;

    png_infop info = png_create_info_struct(png);
    if (!info) return 0;

    if (setjmp(png_jmpbuf(png))) {
        fclose(fp);
        return 0;
    }

    png_init_io(png, fp);

    // Set image info (8-bit per channel, RGBA)
    png_set_IHDR(
        png,
        info,
        width, height,
        8,
        PNG_COLOR_TYPE_RGBA,
        PNG_INTERLACE_NONE,
        PNG_COMPRESSION_TYPE_DEFAULT,
        PNG_FILTER_TYPE_DEFAULT
    );

    png_write_info(png, info);

    // Write image data
    png_bytep rows[height];
    for (int y = 0; y < height; y++) {
        rows[y] = image_data + y * width * 4;
    }

    png_write_image(png, rows);
    png_write_end(png, NULL);

    fclose(fp);
    png_destroy_write_struct(&png, &info);
    return 1;
}

// Function to convert RGB to HSV (normalized 0-1)
void _rgb_to_hsv(uint8_t r, uint8_t g, uint8_t b, float *h, float *s, float *v) {
    float r_norm = r / 255.0f;
    float g_norm = g / 255.0f;
    float b_norm = b / 255.0f;

    float max = fmaxf(fmaxf(r_norm, g_norm), b_norm);
    float min = fminf(fminf(r_norm, g_norm), b_norm);
    float delta = max - min;

    // Hue calculation
    if (delta == 0) {
        *h = 0;
    } else if (max == r_norm) {
        *h = fmodf((g_norm - b_norm) / delta, 6.0f) / 6.0f;
    } else if (max == g_norm) {
        *h = ((b_norm - r_norm) / delta + 2.0f) / 6.0f;
    } else {
        *h = ((r_norm - g_norm) / delta + 4.0f) / 6.0f;
    }
    if (*h < 0) *h += 1.0f;

    // Saturation calculation
    *s = (max == 0) ? 0 : delta / max;

    // Value calculation
    *v = max;
}

void _hsv_to_rgb(float h, float s, float v, uint8_t *r, uint8_t *g, uint8_t *b) {
    float c = v * s;  // Chroma
    float x = c * (1.0f - fabsf(fmodf(h * 6.0f, 2.0f) - 1.0f));
    float m = v - c;

    float r_temp, g_temp, b_temp;

    if (h >= 0.0f && h < 1.0f / 6.0f) {
        r_temp = c;
        g_temp = x;
        b_temp = 0.0f;
    } else if (h >= 1.0f / 6.0f && h < 2.0f / 6.0f) {
        r_temp = x;
        g_temp = c;
        b_temp = 0.0f;
    } else if (h >= 2.0f / 6.0f && h < 3.0f / 6.0f) {
        r_temp = 0.0f;
        g_temp = c;
        b_temp = x;
    } else if (h >= 3.0f / 6.0f && h < 4.0f / 6.0f) {
        r_temp = 0.0f;
        g_temp = x;
        b_temp = c;
    } else if (h >= 4.0f / 6.0f && h < 5.0f / 6.0f) {
        r_temp = x;
        g_temp = 0.0f;
        b_temp = c;
    } else {
        r_temp = c;
        g_temp = 0.0f;
        b_temp = x;
    }

    *r = (uint8_t)((r_temp + m) * 255.0f);
    *g = (uint8_t)((g_temp + m) * 255.0f);
    *b = (uint8_t)((b_temp + m) * 255.0f);
}

// Helper function to quantize an 8-bit channel to 2-bit
uint8_t _quantize_channel(uint8_t channel) {
    if (channel < 64) {
        return 0;
    } else if (channel < 128) {
        return 1;
    } else if (channel < 192) {
        return 2;
    } else {
        return 3;
    }
}

// Helper function to encode 8-bit RGBA into a 2-bit packed pixel
uint8_t _eight_to_two(uint8_t r, uint8_t g, uint8_t b, uint8_t a) {
    // Quantize 8-bit values to 2-bit values
    uint8_t r_q = _quantize_channel(r);
    uint8_t g_q = _quantize_channel(g);
    uint8_t b_q = _quantize_channel(b);
    uint8_t a_q = _quantize_channel(a);

    // Pack the 2-bit channels into a single byte
    return (a_q << 6) | (b_q << 4) | (g_q << 2) | r_q;
}

// Helper function to decode a 2-bit pixel into 8-bit RGBA (used for palette colors)
void _two_to_eight(uint8_t pixel, uint8_t *r, uint8_t *g, uint8_t *b, uint8_t *a) {
    // Extract the individual 2-bit values from the byte
    *a = (pixel >> 6) & 0b11;
    *b = (pixel >> 4) & 0b11;
    *g = (pixel >> 2) & 0b11;
    *r = pixel & 0b11;

    // Map the 2-bit values to 8-bit values (0, 85, 170, 255)
    static const uint8_t mapping[4] = {0, 85, 170, 255};
    *r = mapping[*r];
    *g = mapping[*g];
    *b = mapping[*b];
    *a = mapping[*a];
}

void _rgba32_to_rgba2(uint8_t *image_data, size_t num_pixels, uint8_t *output_buffer) {
    for (size_t i = 0; i < num_pixels; ++i) {
        // Each pixel is 4 bytes (RGBA)
        uint8_t r = image_data[i * 4 + 0];
        uint8_t g = image_data[i * 4 + 1];
        uint8_t b = image_data[i * 4 + 2];
        uint8_t a = image_data[i * 4 + 3];

        // Encode 8-bit RGBA into a 2-bit packed format
        output_buffer[i] = _eight_to_two(r, g, b, a);
    }
}

// Function to calculate Euclidean distance between two RGB colors in the Color struct
float _distance_rgb(const Color *color1, const Color *color2) {
    return sqrtf(powf(color1->r - color2->r, 2) +
                 powf(color1->g - color2->g, 2) +
                 powf(color1->b - color2->b, 2));
}

// Function to find the nearest RGB color in the palette
const Color* _nearest_rgb(const Color *target_rgb, const Palette *palette) {
    const Color *nearest_color = NULL;
    float min_distance = FLT_MAX;  // Set to max float value
    for (size_t i = 0; i < palette->size; ++i) {
        float distance = _distance_rgb(target_rgb, &palette->colors[i]);
        if (distance < min_distance) {
            min_distance = distance;
            nearest_color = &palette->colors[i];
        }
    }
    return nearest_color;
}

const Color* _nearest_hsv(const Color *target_hsv, const Palette *palette) {
    const Color *nearest_color = NULL;
    float min_distance = FLT_MAX;

    // Iterate through each color in the palette
    for (size_t i = 0; i < palette->size; ++i) {
        const Color *palette_color = &palette->colors[i];

        // Compute the hue distance, accounting for wrap-around
        float hue_distance = fabsf(target_hsv->h - palette_color->h);
        if (hue_distance > 0.5) {
            hue_distance = 1.0 - hue_distance;  // Wrap around the hue circle
        }

        // Compute the Euclidean distance in the HSV space
        float distance = sqrtf(powf(hue_distance, 2) +
                               powf(target_hsv->s - palette_color->s, 2) +
                               powf(target_hsv->v - palette_color->v, 2));

        // If this is the smallest distance so far, store this color as the nearest
        if (distance < min_distance) {
            min_distance = distance;
            nearest_color = palette_color;
        }
    }

    return nearest_color;
}

// Helper function: Parse Python arguments into a Color struct (internal use)
int _parse_color(PyObject *args, Color *color) {
    int r, g, b;

    if (!PyArg_ParseTuple(args, "iii", &r, &g, &b)) {
        PyErr_SetString(PyExc_TypeError, "Expected three integers for RGB values");
        return 0; // Return 0 on failure
    }

    // Ensure the values are in the valid range for RGB (0-255)
    color->r = (uint8_t) (r & 0xFF);
    color->g = (uint8_t) (g & 0xFF);
    color->b = (uint8_t) (b & 0xFF);

    return 1; // Return 1 on success
}

// Function to read a GIMP palette file and load it into the Palette struct
int _load_gimp_palette(const char *filename, Palette *palette) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "Error: Cannot open file %s\n", filename);
        return -1;
    }

    char line[256];
    size_t color_count = 0;
    size_t capacity = 256;  // Initial capacity for 256 colors

    // Allocate memory for the palette
    palette->colors = (Color *)malloc(capacity * sizeof(Color));
    if (!palette->colors) {
        fprintf(stderr, "Error: Memory allocation failed\n");
        fclose(file);
        return -1;
    }

    // Skip header lines (lines starting with '#' or containing "GIMP Palette" or "Columns")
    while (fgets(line, sizeof(line), file)) {
        if (line[0] == '#' || strncmp(line, "GIMP Palette", 12) == 0 || strncmp(line, "Columns", 7) == 0) {
            continue;
        }

        // Parse RGB values from each valid line
        int r, g, b;
        if (sscanf(line, "%d %d %d", &r, &g, &b) == 3) {
            // Check if we need to resize the array
            if (color_count >= capacity) {
                capacity *= 2;
                palette->colors = (Color *)realloc(palette->colors, capacity * sizeof(Color));
                if (!palette->colors) {
                    fprintf(stderr, "Error: Memory reallocation failed\n");
                    fclose(file);
                    return -1;
                }
            }

            // Store the RGB values
            palette->colors[color_count].r = (uint8_t)r;
            palette->colors[color_count].g = (uint8_t)g;
            palette->colors[color_count].b = (uint8_t)b;

            // Convert and store HSV values
            _rgb_to_hsv(r, g, b, 
                        &palette->colors[color_count].h, 
                        &palette->colors[color_count].s, 
                        &palette->colors[color_count].v);

            color_count++;
        }
    }

    // Close the file
    fclose(file);

    // Store the final size
    palette->size = color_count;

    return 0;
}

// Function to free the palette memory
void _free_palette(Palette *palette) {
    if (palette->colors) {
        free(palette->colors);
        palette->colors = NULL;
    }
    palette->size = 0;
}

void _convert_atkinson(uint8_t* image_data, int width, int height, Palette *palette) {
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            uint8_t* pixel = &image_data[(y * width + x) * 4];  // RGBA format

            // Skip dithering for pixels with alpha channel value < 1
            if (pixel[3] < 1) continue;

            // Create a Color struct for the current pixel's RGB values
            Color current_pixel = { .r = pixel[0], .g = pixel[1], .b = pixel[2] };

            // Find the nearest RGB color in the palette
            const Color* nearest_color = _nearest_rgb(&current_pixel, palette);

            // Compute the error (difference between original and nearest color)
            int16_t err_r = pixel[0] - nearest_color->r;
            int16_t err_g = pixel[1] - nearest_color->g;
            int16_t err_b = pixel[2] - nearest_color->b;

            // Update the current pixel with the nearest color
            pixel[0] = nearest_color->r;
            pixel[1] = nearest_color->g;
            pixel[2] = nearest_color->b;

            // Propagate the error to neighboring pixels using Atkinson dithering
            // Divide the error by 8 using bit-shifting (err / 8 = err >> 3)
            int16_t error_r = err_r >> 3;
            int16_t error_g = err_g >> 3;
            int16_t error_b = err_b >> 3;

            // Propagate to right neighbor (x + 1)
            if (x + 1 < width) {
                uint8_t* right_pixel = &image_data[(y * width + (x + 1)) * 4];
                right_pixel[0] = _clamp_256(right_pixel[0] + error_r);
                right_pixel[1] = _clamp_256(right_pixel[1] + error_g);
                right_pixel[2] = _clamp_256(right_pixel[2] + error_b);
            }

            // Propagate to right+2 neighbor (x + 2)
            if (x + 2 < width) {
                uint8_t* right2_pixel = &image_data[(y * width + (x + 2)) * 4];
                right2_pixel[0] = _clamp_256(right2_pixel[0] + error_r);
                right2_pixel[1] = _clamp_256(right2_pixel[1] + error_g);
                right2_pixel[2] = _clamp_256(right2_pixel[2] + error_b);
            }

            // Propagate to bottom neighbor (y + 1)
            if (y + 1 < height) {
                uint8_t* bottom_pixel = &image_data[((y + 1) * width + x) * 4];
                bottom_pixel[0] = _clamp_256(bottom_pixel[0] + error_r);
                bottom_pixel[1] = _clamp_256(bottom_pixel[1] + error_g);
                bottom_pixel[2] = _clamp_256(bottom_pixel[2] + error_b);
            }

            // Propagate to bottom-right neighbor (y + 1, x + 1)
            if (x + 1 < width && y + 1 < height) {
                uint8_t* bottom_right_pixel = &image_data[((y + 1) * width + (x + 1)) * 4];
                bottom_right_pixel[0] = _clamp_256(bottom_right_pixel[0] + error_r);
                bottom_right_pixel[1] = _clamp_256(bottom_right_pixel[1] + error_g);
                bottom_right_pixel[2] = _clamp_256(bottom_right_pixel[2] + error_b);
            }

            // Propagate to bottom-right+2 neighbor (y + 1, x + 2)
            if (x + 2 < width && y + 1 < height) {
                uint8_t* bottom_right2_pixel = &image_data[((y + 1) * width + (x + 2)) * 4];
                bottom_right2_pixel[0] = _clamp_256(bottom_right2_pixel[0] + error_r);
                bottom_right2_pixel[1] = _clamp_256(bottom_right2_pixel[1] + error_g);
                bottom_right2_pixel[2] = _clamp_256(bottom_right2_pixel[2] + error_b);
            }
        }
    }
}

void extrapolate_color(const Color *orig, const Color *matched, Color *extrapolated) {
    extrapolated->r = _clamp_256(orig->r + (orig->r - matched->r));
    extrapolated->g = _clamp_256(orig->g + (orig->g - matched->g));
    extrapolated->b = _clamp_256(orig->b + (orig->b - matched->b));
}

void _convert_bayer(uint8_t* image_data, int width, int height, Palette *palette) {
    for (int x = 0; x < width; x++) {
        for (int y = 0; y < height; y++) {
            uint8_t* pixel = &image_data[(y * width + x) * 4];  // RGBA format

            // Skip dithering for pixels with alpha channel value < 1
            if (pixel[3] < 1) continue;

            // Get the Bayer threshold value for the current pixel position
            uint8_t threshold = bayer_matrix[x % 4][y % 4];

            // Create a Color struct for the current pixel's RGB values
            Color current_pixel = { .r = pixel[0], .g = pixel[1], .b = pixel[2] };

            // Find the nearest RGB color in the palette (initial color1)
            const Color* color1 = _nearest_rgb(&current_pixel, palette);

            // Extrapolate a second color (color2) based on the error from color1
            Color extrapolated_color;
            extrapolate_color(&current_pixel, color1, &extrapolated_color);

            const Color* color2 = _nearest_rgb(&extrapolated_color, palette);

            // Calculate distances
            float err1 = _distance_rgb(&current_pixel, color1);
            float err2 = _distance_rgb(&current_pixel, color2);

            // Determine the relative probability of choosing color1 vs color2
            if (err1 || err2) {
                const int proportion2 = (255 * err2) / (err1 + err2);
                if (threshold > proportion2) {
                    color1 = color2;  // Use the alternative color2
                }
            }

            // Update the pixel with the final color
            pixel[0] = color1->r;
            pixel[1] = color1->g;
            pixel[2] = color1->b;
        }
    }
}

// Floyd-Steinberg dithering
void _convert_floyd_steinberg(uint8_t* image_data, int width, int height, Palette *palette) {
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int pixel_index = (y * width + x) * 4;  // RGBA format
            uint8_t *pixel = &image_data[pixel_index];

            // Skip pixels with alpha less than full (i.e., partially transparent)
            if (pixel[3] < 1) {
                continue;
            }

            // Create a temporary Color struct for the current pixel's RGB values
            Color current_pixel = {
                .r = pixel[0],  // Red
                .g = pixel[1],  // Green
                .b = pixel[2],  // Blue
                .h = 0.0f,      // Not used for RGB matching
                .s = 0.0f,      // Not used for RGB matching
                .v = 0.0f,      // Not used for RGB matching
            };

            // Find the nearest RGB color in the palette
            const Color* nearest_color = _nearest_rgb(&current_pixel, palette);

            // Store the original pixel values
            uint8_t old_r = pixel[0];
            uint8_t old_g = pixel[1];
            uint8_t old_b = pixel[2];

            // Set the pixel to the nearest palette color
            pixel[0] = nearest_color->r;  // Red
            pixel[1] = nearest_color->g;  // Green
            pixel[2] = nearest_color->b;  // Blue

            // Calculate the error for each channel (RGB)
            int error_r = old_r - nearest_color->r;
            int error_g = old_g - nearest_color->g;
            int error_b = old_b - nearest_color->b;

            // Distribute the error to neighboring pixels (Floyd-Steinberg dithering)
            if (x + 1 < width) {
                int neighbor_index = (y * width + (x + 1)) * 4;
                image_data[neighbor_index + 0] = _clamp_256(image_data[neighbor_index + 0] + (error_r * 7 / 16));
                image_data[neighbor_index + 1] = _clamp_256(image_data[neighbor_index + 1] + (error_g * 7 / 16));
                image_data[neighbor_index + 2] = _clamp_256(image_data[neighbor_index + 2] + (error_b * 7 / 16));
            }
            if (y + 1 < height) {
                if (x > 0) {
                    int neighbor_index = ((y + 1) * width + (x - 1)) * 4;
                    image_data[neighbor_index + 0] = _clamp_256(image_data[neighbor_index + 0] + (error_r * 3 / 16));
                    image_data[neighbor_index + 1] = _clamp_256(image_data[neighbor_index + 1] + (error_g * 3 / 16));
                    image_data[neighbor_index + 2] = _clamp_256(image_data[neighbor_index + 2] + (error_b * 3 / 16));
                }
                int neighbor_index = ((y + 1) * width + x) * 4;
                image_data[neighbor_index + 0] = _clamp_256(image_data[neighbor_index + 0] + (error_r * 5 / 16));
                image_data[neighbor_index + 1] = _clamp_256(image_data[neighbor_index + 1] + (error_g * 5 / 16));
                image_data[neighbor_index + 2] = _clamp_256(image_data[neighbor_index + 2] + (error_b * 5 / 16));
                if (x + 1 < width) {
                    int neighbor_index = ((y + 1) * width + (x + 1)) * 4;
                    image_data[neighbor_index + 0] = _clamp_256(image_data[neighbor_index + 0] + (error_r * 1 / 16));
                    image_data[neighbor_index + 1] = _clamp_256(image_data[neighbor_index + 1] + (error_g * 1 / 16));
                    image_data[neighbor_index + 2] = _clamp_256(image_data[neighbor_index + 2] + (error_b * 1 / 16));
                }
            }
        }
    }
}

// Convert a PNG image to use a custom palette by matching RGB colors
void _convert_method_rgb(uint8_t *image_data, int width, int height, Palette *palette, bool has_transparent_color, const uint8_t transparent_rgb[3]) {
    // Loop over every pixel in the image
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int pixel_index = (y * width + x) * 4;  // Assuming RGBA format

            uint8_t r = image_data[pixel_index];
            uint8_t g = image_data[pixel_index + 1];
            uint8_t b = image_data[pixel_index + 2];
            uint8_t a = image_data[pixel_index + 3];

            // Handle transparency based on alpha or a specific transparent color
            if (a < 1 || (has_transparent_color && r == transparent_rgb[0] && g == transparent_rgb[1] && b == transparent_rgb[2])) {
                image_data[pixel_index + 3] = 0;  // Fully transparent
                continue;
            }

            // Create a temporary Color struct for the current pixel's RGB values
            Color current_pixel = {r, g, b, 0.0f, 0.0f, 0.0f};
            _rgb_to_hsv(r, g, b, &current_pixel.h, &current_pixel.s, &current_pixel.v);

            // Find the nearest RGB color in the palette
            const Color *nearest_rgb = _nearest_rgb(&current_pixel, palette);

            // Update the image data with the nearest RGB color
            image_data[pixel_index] = nearest_rgb->r;
            image_data[pixel_index + 1] = nearest_rgb->g;
            image_data[pixel_index + 2] = nearest_rgb->b;
        }
    }

    // Free the palette memory
    _free_palette(palette);
}

// Convert a PNG image to use a custom palette by matching HSV colors
void _convert_method_hsv(uint8_t *image_data, int width, int height, Palette *palette, bool has_transparent_color, const uint8_t transparent_rgb[3]) {
    // Loop over every pixel in the image
    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            int pixel_index = (y * width + x) * 4;  // Assuming RGBA format

            uint8_t r = image_data[pixel_index];
            uint8_t g = image_data[pixel_index + 1];
            uint8_t b = image_data[pixel_index + 2];
            uint8_t a = image_data[pixel_index + 3];

            // Handle transparency based on alpha or a specific transparent color
            if (a < 1 || (has_transparent_color && r == transparent_rgb[0] && g == transparent_rgb[1] && b == transparent_rgb[2])) {
                image_data[pixel_index + 3] = 0;  // Fully transparent
                continue;
            }

            // Convert the current pixel's RGB values to HSV
            Color current_pixel;
            _rgb_to_hsv(r, g, b, &current_pixel.h, &current_pixel.s, &current_pixel.v);

            // Find the nearest HSV color in the palette
            const Color *nearest_hsv = _nearest_hsv(&current_pixel, palette);

            // Convert the nearest HSV color back to RGB for output
            uint8_t nearest_r, nearest_g, nearest_b;
            _hsv_to_rgb(nearest_hsv->h, nearest_hsv->s, nearest_hsv->v, &nearest_r, &nearest_g, &nearest_b);

            // Update the image data with the nearest RGB color
            image_data[pixel_index] = nearest_r;
            image_data[pixel_index + 1] = nearest_g;
            image_data[pixel_index + 2] = nearest_b;
        }
    }

    // Free the palette memory
    _free_palette(palette);
}

// Helper function to _clamp_256 values between 0 and 255
inline uint8_t _clamp_256(int value) {
    if (value < 0) return 0;
    if (value > 255) return 255;
    return (uint8_t)value;
};


bool _parse_transparent_color(PyObject *transparent_color, uint8_t transparent_rgb[3]) {
    // Default: No transparency
    bool use_transparent = false;
    transparent_rgb[0] = 0;
    transparent_rgb[1] = 0;
    transparent_rgb[2] = 0;

    // If transparent_color is None, return false (no transparency)
    if (transparent_color == Py_None) {
        return false;
    }

    // Ensure it's a valid 4-tuple
    if (!PyTuple_Check(transparent_color) || PyTuple_Size(transparent_color) != 4) {
        PyErr_SetString(PyExc_TypeError, "transparent_color must be a tuple of 4 integers (R, G, B, A) or None");
        return false;
    }

    // Extract values
    int r = (int)PyLong_AsLong(PyTuple_GetItem(transparent_color, 0));
    int g = (int)PyLong_AsLong(PyTuple_GetItem(transparent_color, 1));
    int b = (int)PyLong_AsLong(PyTuple_GetItem(transparent_color, 2));
    int a = (int)PyLong_AsLong(PyTuple_GetItem(transparent_color, 3));

    // Use transparency only if alpha == 255
    if (a == 255) {
        use_transparent = true;
        transparent_rgb[0] = (uint8_t)r;
        transparent_rgb[1] = (uint8_t)g;
        transparent_rgb[2] = (uint8_t)b;
    }

    return use_transparent;
}

bool _parse_palette_conversion_args(PyObject *args, PyObject *kwargs, const char **src_file, const char **tgt_file, const char **palette_file, const char **method, uint8_t **image_data, int *width, int *height, Palette *palette, bool *use_transparent, uint8_t transparent_rgb[3]) {
    PyObject *transparent_color = Py_None;  // Default to None

    // Define keyword argument names
    static char *kwlist[] = {"src_file", "tgt_file", "palette_file", "method", "transparent_color", NULL};

    // Parse the function arguments
    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ssss|O", kwlist, src_file, tgt_file, palette_file, method, &transparent_color)) {
        return false;
    }

    // Load the palette
    if (_load_gimp_palette(*palette_file, palette) != 0) {
        PyErr_SetString(PyExc_IOError, "Failed to load palette file");
        return false;
    }

    // Load the source image
    if (!_read_png(*src_file, image_data, width, height)) {
        PyErr_SetString(PyExc_IOError, "Failed to load source PNG file");
        _free_palette(palette);
        return false;
    }

    // Determine transparency settings
    *use_transparent = _parse_transparent_color(transparent_color, transparent_rgb);

    return true;
}

uint8_t* _convert_to_palette(uint8_t *image_data, int width, int height, Palette *palette, const char *method, bool use_transparent, uint8_t transparent_rgb[3]) {
    // Dispatch to the appropriate conversion function.
    if (strcasecmp(method, "RGB") == 0) {
        _convert_method_rgb(image_data, width, height, palette, use_transparent, transparent_rgb);
    } else if (strcasecmp(method, "HSV") == 0) {
        _convert_method_hsv(image_data, width, height, palette, use_transparent, transparent_rgb);
    } else if (strcasecmp(method, "atkinson") == 0) {
        _convert_atkinson(image_data, width, height, palette);
    } else if (strcasecmp(method, "bayer") == 0) {
        _convert_bayer(image_data, width, height, palette);
    } else if (strcasecmp(method, "floyd") == 0) {
        _convert_floyd_steinberg(image_data, width, height, palette);
    } else {
        // Invalid conversion method provided.
        return NULL;
    }
    
    return image_data;
}

PyObject* convert_to_palette(PyObject *self, PyObject *args, PyObject *kwargs) {
    const char *src_file, *tgt_file, *palette_file, *method; uint8_t *image_data; int width, height; Palette palette; bool use_transparent; uint8_t transparent_rgb[3] = {0, 0, 0};

    // Use helper function to parse arguments and set up data
    if (!_parse_palette_conversion_args(args, kwargs, &src_file, &tgt_file, &palette_file, &method, &image_data, &width, &height, &palette, &use_transparent, transparent_rgb)) {
        return NULL;
    }

    // Perform conversion
    if (_convert_to_palette(image_data, width, height, &palette, method, use_transparent, transparent_rgb) == NULL) {
        free(image_data);
        _free_palette(&palette);
        return NULL;
    }

    // Write output file
    if (!_write_png(tgt_file, image_data, width, height)) {
        PyErr_SetString(PyExc_IOError, "Failed to save target PNG file");
        free(image_data);
        _free_palette(&palette);
        return NULL;
    }

    free(image_data);
    _free_palette(&palette);
    Py_RETURN_NONE;
}

// Python-facing function: Convert a PNG to a palette-based image, then output it as an .rgba2 file
PyObject* img_to_rgba2(PyObject *self, PyObject *args, PyObject *kwargs) {
    const char *src_file, *tgt_file, *palette_file, *method;
    uint8_t *image_data = NULL;
    int width, height;
    Palette palette;
    bool use_transparent;
    uint8_t transparent_rgb[3] = {0, 0, 0};

    // Use helper function to parse arguments and set up data
    if (!_parse_palette_conversion_args(args, kwargs,
            &src_file, &tgt_file, &palette_file, &method,
            &image_data, &width, &height, &palette,
            &use_transparent, transparent_rgb)) {
        return NULL;
    }

    // Perform the palette conversion on the image_data
    if (_convert_to_palette(image_data, width, height, &palette, method, use_transparent, transparent_rgb) == NULL) {
        free(image_data);
        _free_palette(&palette);
        return NULL;
    }

    // Calculate total number of pixels
    size_t num_pixels = (size_t)width * height;
    // Allocate output buffer for RGBA2222 format (1 byte per pixel)
    uint8_t *rgba2_data = (uint8_t *)malloc(num_pixels);
    if (!rgba2_data) {
        PyErr_SetString(PyExc_MemoryError, "Failed to allocate memory for RGBA2222 data.");
        free(image_data);
        _free_palette(&palette);
        return NULL;
    }

    // Convert from 32-bit RGBA (palette converted) to RGBA2222 (8-bit per pixel)
    _rgba32_to_rgba2(image_data, num_pixels, rgba2_data);

    // Open the target file for writing in binary mode
    FILE *outfile = fopen(tgt_file, "wb");
    if (!outfile) {
        PyErr_SetString(PyExc_IOError, "Failed to open output file for writing.");
        free(image_data);
        free(rgba2_data);
        _free_palette(&palette);
        return NULL;
    }

    // Write the RGBA2222 data (one byte per pixel) to the file
    size_t written = fwrite(rgba2_data, 1, num_pixels, outfile);
    if (written != num_pixels) {
        PyErr_SetString(PyExc_IOError, "Failed to write all RGBA2222 data to output file.");
        fclose(outfile);
        free(image_data);
        free(rgba2_data);
        _free_palette(&palette);
        return NULL;
    }
    fclose(outfile);

    // Clean up allocated resources
    free(image_data);
    free(rgba2_data);
    _free_palette(&palette);

    Py_RETURN_NONE;
}


// Function: Convert RGBA2 binary file to PNG
PyObject* rgba2_to_img(PyObject *self, PyObject *args) {
    const char *input_filepath, *output_filepath;
    int int_width, int_height;  // Still use int for parsing arguments
    size_t width, height;       // Use size_t for internal processing

    // Parse arguments: input RGBA2 file, width, height, and output PNG file
    if (!PyArg_ParseTuple(args, "ssii", &input_filepath, &output_filepath, &int_width, &int_height)) {
        return NULL;
    }

    // Convert width and height to size_t
    width = (size_t)int_width;
    height = (size_t)int_height;

    // Open the input RGBA2 file for reading
    FILE *file = fopen(input_filepath, "rb");
    if (!file) {
        PyErr_SetString(PyExc_IOError, "Could not open input RGBA2 file for reading.");
        return NULL;
    }

    // Allocate memory for RGBA8 image data
    size_t image_size = width * height * 4;
    uint8_t *image_data = (uint8_t *)malloc(image_size);
    if (!image_data) {
        fclose(file);
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for image data.");
        return NULL;
    }

    // Read and decode each packed byte
    for (size_t i = 0; i < width * height; ++i) {
        uint8_t packed_pixel;
        if (fread(&packed_pixel, sizeof(uint8_t), 1, file) != 1) {
            free(image_data);
            fclose(file);
            PyErr_SetString(PyExc_IOError, "Error reading RGBA2 file.");
            return NULL;
        }
        
        // Use the helper function to decode the 2-bit packed pixel to 8-bit RGBA
        uint8_t r, g, b, a;
        _two_to_eight(packed_pixel, &r, &g, &b, &a);

        // Store the expanded 8-bit values in the image data
        image_data[i * 4 + 0] = r;
        image_data[i * 4 + 1] = g;
        image_data[i * 4 + 2] = b;
        image_data[i * 4 + 3] = a;
    }

    fclose(file);

    // Write the PNG image using your libpng helper
    if (!_write_png(output_filepath, image_data, width, height)) {
        PyErr_SetString(PyExc_IOError, "Failed to save PNG file.");
        free(image_data);
        return NULL;
    }

    free(image_data);
    Py_RETURN_NONE;
}

// Function: Convert an RGBA8 binary file to PNG
PyObject* rgba8_to_img(PyObject *self, PyObject *args) {
    const char *input_filepath, *output_filepath;
    int width, height;

    // Parse arguments: input RGBA8 file, width, height, and output PNG file
    if (!PyArg_ParseTuple(args, "ssii", &input_filepath, &output_filepath, &width, &height)) {
        return NULL;
    }

    // Open the input RGBA8 file for reading
    FILE *file = fopen(input_filepath, "rb");
    if (!file) {
        PyErr_SetString(PyExc_IOError, "Could not open input RGBA8 file for reading.");
        return NULL;
    }

    // Allocate memory for RGBA8 image data
    size_t image_size = width * height * 4;
    uint8_t *image_data = (uint8_t *)malloc(image_size);
    if (!image_data) {
        fclose(file);
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for image data.");
        return NULL;
    }

    // Read RGBA8 data from file
    if (fread(image_data, sizeof(uint8_t), image_size, file) != image_size) {
        free(image_data);
        fclose(file);
        PyErr_SetString(PyExc_IOError, "Error reading RGBA8 file.");
        return NULL;
    }

    fclose(file);

    // Write the PNG image using your libpng helper
    if (!_write_png(output_filepath, image_data, width, height)) {
        PyErr_SetString(PyExc_IOError, "Failed to save PNG file.");
        free(image_data);
        return NULL;
    }

    free(image_data);
    Py_RETURN_NONE;
}

// API Function: Converts a CSV file to a Palette object with color names
PyObject* csv_to_palette(PyObject *self, PyObject *args) {
    const char *csv_filepath;

    // Parse the Python argument (CSV file path)
    if (!PyArg_ParseTuple(args, "s", &csv_filepath)) {
        PyErr_SetString(PyExc_TypeError, "Expected a CSV file path string");
        return NULL;
    }

    // Open the CSV file
    FILE *file = fopen(csv_filepath, "r");
    if (!file) {
        PyErr_SetString(PyExc_IOError, "Could not open the CSV file");
        return NULL;
    }

    // Allocate memory for the Palette
    Palette *palette = (Palette *)malloc(sizeof(Palette));
    if (!palette) {
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for the Palette");
        fclose(file);
        return NULL;
    }

    // Temporary storage for reading each line in the CSV
    char line[256];
    size_t capacity = 256;  // Initial capacity for the palette colors
    size_t color_count = 0;

    // Allocate memory for the colors array
    palette->colors = (Color *)malloc(capacity * sizeof(Color));
    if (!palette->colors) {
        PyErr_SetString(PyExc_MemoryError, "Unable to allocate memory for colors");
        free(palette);
        fclose(file);
        return NULL;
    }

    // Read the CSV file line by line
    while (fgets(line, sizeof(line), file)) {
        if (color_count >= capacity) {
            capacity *= 2;  // Double the capacity if needed
            palette->colors = (Color *)realloc(palette->colors, capacity * sizeof(Color));
            if (!palette->colors) {
                PyErr_SetString(PyExc_MemoryError, "Memory reallocation failed");
                fclose(file);
                return NULL;
            }
        }

        // Parse the CSV line (expecting "r,g,b,h,s,v,hex,name")
        uint8_t r, g, b;
        char name[64];  // For the color name
        char hex[8];    // For the hex code (if needed)
        float h, s, v;

        if (sscanf(line, "%hhu,%hhu,%hhu,%f,%f,%f,%7[^,],%63[^\n]",
                &r, &g, &b, &h, &s, &v, hex, name) == 8) {
            // Fill in the RGB values
            palette->colors[color_count].r = r;
            palette->colors[color_count].g = g;
            palette->colors[color_count].b = b;

            // Convert RGB to HSV
            _rgb_to_hsv(r, g, b, &palette->colors[color_count].h, &palette->colors[color_count].s, &palette->colors[color_count].v);

            // Store the color name
            snprintf(palette->colors[color_count].name, sizeof(palette->colors[color_count].name), "%s", name);
            palette->colors[color_count].name[sizeof(palette->colors[color_count].name) - 1] = '\0';  // Ensure null-termination

            // Increment the color count
            color_count++;
        }
    }

    // Close the file
    fclose(file);

    // Set the palette size
    palette->size = color_count;

    // Return the Palette object to Python
    PyObject *palette_py = PyCapsule_New((void *)palette, "Palette", NULL);
    return palette_py;
}