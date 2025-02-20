#define PY_SSIZE_T_CLEAN

#include "images.h"

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

        // Parse the CSV line (expecting "r,g,b,h,s,v,c,m,y,k,hex,name")
        uint8_t r, g, b;
        char name[64];  // For the color name
        char hex[8];    // For the hex code
        float h, s, v, c, m, y, k;

        // Parse the fields correctly, skipping over HSV and CMYK as needed
        if (sscanf(line, "%hhu,%hhu,%hhu,%f,%f,%f,%f,%f,%f,%f,%7[^,],%63[^\n]", 
                &r, &g, &b, &h, &s, &v, &c, &m, &y, &k, hex, name) == 12) {
            // Fill in the RGB values
            palette->colors[color_count].r = r;
            palette->colors[color_count].g = g;
            palette->colors[color_count].b = b;

            // Convert RGB to HSV
            rgb_to_hsv_internal(r, g, b, &palette->colors[color_count].h, &palette->colors[color_count].s, &palette->colors[color_count].v);

            // Convert RGB to CMYK
            rgb_to_cmyk_internal(r, g, b, &palette->colors[color_count].c, &palette->colors[color_count].m, &palette->colors[color_count].y, &palette->colors[color_count].k);

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

PyObject* process_image_with_palette(PyObject* self, PyObject* args) {
    const char* palette_filepath;
    float hue;
    int width, height;

    if (!PyArg_ParseTuple(args, "sfii", &palette_filepath, &hue, &width, &height)) {
        return NULL;
    }

    Palette palette;
    if (load_gimp_palette(palette_filepath, &palette) != 0) {
        return PyErr_Format(PyExc_RuntimeError, "Failed to load palette");
    }

    uint8_t* image_data = malloc(width * height * 4);
    if (!image_data) {
        return PyErr_NoMemory();
    }

    for (int y = 0; y < height; ++y) {
        for (int x = 0; x < width; ++x) {
            // Full saturation and value at top-left, decreasing towards bottom-right
            float saturation = (float)(height - y) / height;
            float value = (float)(width - x) / width;
            Color target_color;
            target_color.h = hue;
            target_color.s = saturation;
            target_color.v = value;

            const Color* nearest_color = find_nearest_color_hsv_internal(&target_color, &palette);

            // Fill the image data with the nearest palette color
            int index = (y * width + x) * 4;
            image_data[index] = nearest_color->r;
            image_data[index + 1] = nearest_color->g;
            image_data[index + 2] = nearest_color->b;
            image_data[index + 3] = 255;  // Alpha (fully opaque)
        }
    }

    PyObject* result = Py_BuildValue("y#", image_data, width * height * 4);
    free(image_data);
    return result;
}

// Function: Simple hello world function
PyObject* hello(PyObject* self, PyObject* args) {
    printf("Hello world from agonutils!\n");
    Py_RETURN_NONE;
}

// Define the methods callable from Python
static PyMethodDef MyMethods[] = {
    // void convert_to_palette(const char *src_file, const char *tgt_file, const char *palette_file, const char *method, uint8_t *transparent_rgb);
    {"convert_to_palette", (PyCFunction)convert_to_palette, METH_VARARGS | METH_KEYWORDS, 
     "Convert image to palette"},

    // void convert_to_rgb565(const char *src_file, const char *tgt_file);
    {"convert_to_rgb565", (PyCFunction)convert_to_rgb565, METH_VARARGS | METH_KEYWORDS, 
     "Convert image to RGB565"},

    // void img_to_rgba2(const char *input_filepath, const char *output_filepath);
    {"img_to_rgba2", img_to_rgba2, METH_VARARGS, 
     "Convert an image to 2-bit RGBA and save to a file"},
    
    // void img_to_rgba8(const char *input_filepath, const char *output_filepath);
    {"img_to_rgba8", img_to_rgba8, METH_VARARGS, 
     "Convert an image to RGBA8 and save to a file"},
    
    // void rgba8_to_img(const char *input_filepath, const char *output_filepath, int width, int height);
    {"rgba8_to_img", rgba8_to_img, METH_VARARGS, 
     "Convert RGBA8 binary file to image"},
    
    // void rgba2_to_img(const char *input_filepath, const char *output_filepath, int width, int height);
    {"rgba2_to_img", rgba2_to_img, METH_VARARGS, 
     "Convert RGBA2 binary file to image"},
     
    // Function: Convert a CSV file to a Palette object
    // Palette* csv_to_palette(const char *csv_filepath);
    {"csv_to_palette", csv_to_palette, METH_VARARGS, "Convert a CSV file to a Palette object"},

    // Function: Process an image with a palette
    // uint8_t* process_image_with_palette(const char* palette_filepath, float hue, int width, int height);
    {"process_image_with_palette", process_image_with_palette, METH_VARARGS, "Process an image with a palette"},
    
    // void hello(void);
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
