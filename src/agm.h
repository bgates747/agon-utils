#ifndef AGM_H
#define AGM_H

#ifdef __cplusplus
extern "C" {
#endif

#include <libavcodec/avcodec.h>
#include <libavformat/avformat.h>
#include <libswscale/swscale.h>
#include <libavutil/imgutils.h>
#include <stdio.h>
#include <stdint.h>
#include "images.h"
#include "rle.h"
#include <Python.h>

// ----------------------------------------------------------------
// Internal MP4 Processing Function:
// Processes an MP4 file by extracting frames, applying palette conversion 
// (with both no-dither and dither methods), reusing dithering with lookback, 
// and writing out a single custom movie file (packed RGBA2 frames).
// ----------------------------------------------------------------
int _process_mp4_internal(const char *input_file, const char *output_file,
                          int output_width, int output_height,
                          const char *palette_file,
                          const char *noDither_method, const char *dither_method,
                          int lookback, PyObject *transparent_color);

// ----------------------------------------------------------------
// Internal Helper Functions
// ----------------------------------------------------------------

// Convert raw 32-bit RGBA data to packed RGBA2 data (1 byte per pixel).
// Returns a pointer to a newly allocated buffer of length (width * height)
// or NULL on error.
uint8_t* _rgba32_to_rgba2_internal(const uint8_t *rgba32, int width, int height);

// Apply palette conversion in-place on the RGBA buffer.
// Returns 0 on success, negative on error.
int _convert_to_palette_internal(uint8_t *buffer, int width, int height,
                                 const char *palette_file, const char *method,
                                 PyObject *transparent_color);

// Reuse dithering with lookback.
// For each pixel in arrays of length 'size':
//   - If oldNo[i] == newNo[i], increment unchanged_count[i]; otherwise, reset it to 0.
//   - If unchanged_count[i] < lookback, use oldDither[i] (if unchanged) or newDither[i] (if changed);
//     else, force newDither[i].
// The final result is stored in final_out.
void reuse_dithering_with_lookback_internal(const uint8_t *oldNo, const uint8_t *newNo,
                                              const uint8_t *oldDither, const uint8_t *newDither,
                                              uint16_t *unchanged_count, int size, int lookback,
                                              uint8_t *final_out);

// Compute an 8-bit difference frame between oldFinal and newFinal.
// For each pixel: diff = 0 if unchanged; otherwise diff = newFinal[i].
// The difference is stored in diff_out (length 'size').
void compute_frame_difference_internal(const uint8_t *oldFinal, const uint8_t *newFinal,
                                       int size, uint8_t *diff_out);

#ifdef __cplusplus
}
#endif

#endif // AGM_H
