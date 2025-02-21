#include "rle.h"
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdio.h>

// _rle_encode_internal:
// Encode an array of 8-bit rgba2222 pixels using our RLE scheme.
// Each pixel is encoded as follows:
//
//  - For a transparent pixel (i.e. if (pixel & 0xC0) == 0x00):
//       * If a single pixel, output: 0x40.
//       * If a run of n (2<=n<=64) identical transparent pixels, output one byte:
//            0x40 OR (n-1)
//  - For an opaque pixel (i.e. if (pixel & 0xC0) != 0x00):
//       * If a single pixel, output: 0x80 OR (color)  [color = pixel & 0x3F]
//       * If a run of n (2<=n<=64) identical opaque pixels, output two bytes:
//            first byte: 0x80 OR (n-1)
//            second byte: 0xC0 OR (color)
//
// This function allocates an output buffer with an upper-bound capacity of input_size * 2,
// then returns a buffer reallocated to the exact used size.
uint8_t *_rle_encode_internal(const uint8_t *input, size_t input_size, size_t *output_size) {
    if (!input || input_size == 0) {
        if (output_size) *output_size = 0;
        return NULL;
    }
    // Allocate worst-case buffer (each pixel might expand to 2 bytes).
    size_t capacity = input_size * 2;
    uint8_t *output = malloc(capacity);
    if (!output) {
        return NULL;
    }
    size_t out_index = 0;
    size_t i = 0;
    while (i < input_size) {
        uint8_t pixel = input[i];
        // Transparent if top two bits are 00.
        int transparent = ((pixel & 0xC0) == 0x00);
        uint8_t color = pixel & 0x3F;  // 6-bit color.
        // Count run length, cap at 64.
        size_t count = 1;
        while (i + count < input_size && input[i + count] == pixel && count < 64) {
            count++;
        }
        
        if (transparent) {
            if (count == 1) {
                // Single transparent pixel always encodes as 0x40.
                output[out_index++] = 0x40;
            } else {
                // Run: encode one byte: 0x40 | (count-1)
                output[out_index++] = 0x40 | (uint8_t)(count - 1);
            }
        } else {
            if (count == 1) {
                // Single opaque pixel: encode as 0x80 OR the color.
                output[out_index++] = 0x80 | color;
            } else {
                // Run: first byte is 0x80 | (count-1), second byte is 0xC0 OR the color.
                output[out_index++] = 0x80 | (uint8_t)(count - 1);
                output[out_index++] = 0xC0 | color;
            }
        }
        i += count;
    }
    
    // Optionally reallocate to shrink the output buffer to the actual size.
    uint8_t *final_output = realloc(output, out_index);
    if (final_output == NULL) {
        final_output = output;
    }
    if (output_size) {
        *output_size = out_index;
    }
    return final_output;
}


// First, a helper to compute the decoded size.
static size_t _rle_decoded_size(const uint8_t *input, size_t input_size) {
    size_t decoded_size = 0;
    size_t i = 0;
    while (i < input_size) {
        uint8_t cmd = input[i++];
        uint8_t type = cmd & 0xC0;  // Top two bits indicate command type.
        if (type == 0x40) {
            // Transparent pixel command.
            uint8_t run = cmd & 0x3F;
            size_t count = (run == 0) ? 1 : (run + 1);
            decoded_size += count;
        } else if (type == 0x80) {
            // Opaque pixel command.
            // Look ahead: if next byte exists and its top two bits are 0xC0, it's a run.
            if (i < input_size && ((input[i] & 0xC0) == 0xC0)) {
                size_t count = (cmd & 0x3F) + 1;
                decoded_size += count;
                i++; // consume the literal byte.
            } else {
                // Otherwise, it's a literal.
                decoded_size += 1;
            }
        } else {
            fprintf(stderr, "Invalid command type: 0x%X\n", type);
            return 0;
        }
    }
    return decoded_size;
}

uint8_t *_rle_decode_internal(const uint8_t *input, size_t input_size, size_t *output_size) {
    if (!input || input_size == 0) {
        if (output_size) *output_size = 0;
        return NULL;
    }
    
    size_t dec_size = _rle_decoded_size(input, input_size);
    if (dec_size == 0) {
        if (output_size) *output_size = 0;
        return NULL;
    }
    
    uint8_t *output = (uint8_t *)malloc(dec_size);
    if (!output)
        return NULL;
    
    size_t out_index = 0;
    size_t i = 0;
    while (i < input_size) {
        uint8_t cmd = input[i++];
        uint8_t type = cmd & 0xC0;
        if (type == 0x40) {
            uint8_t run = cmd & 0x3F;
            size_t count = (run == 0) ? 1 : (run + 1);
            for (size_t j = 0; j < count; j++) {
                // Transparent pixel in our native representation is 0x00.
                output[out_index++] = 0x00;
            }
        } else if (type == 0x80) {
            if (i < input_size && ((input[i] & 0xC0) == 0xC0)) {
                size_t count = (cmd & 0x3F) + 1;
                uint8_t literal = input[i++];
                for (size_t j = 0; j < count; j++) {
                    output[out_index++] = literal;
                }
            } else {
                uint8_t pixel = 0xC0 | (cmd & 0x3F);
                output[out_index++] = pixel;
            }
        } else {
            free(output);
            if (output_size) *output_size = 0;
            return NULL;
        }
    }
    if (output_size)
        *output_size = out_index;
    return output;
}