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
#include <Python.h>

// Function: Process an MP4 file, extract frames, apply palette conversion, and save as custom format
int _process_mp4_internal(const char *input_file, const char *output_file, int output_width, int output_height, const char *palette_file, const char *method, PyObject *transparent_color);

#ifdef __cplusplus
}
#endif

#endif // AGM_H
