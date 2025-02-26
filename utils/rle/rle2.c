#include "rle2.h"
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef unsigned int uint4;  /* For header writing */

static char vmayor = 1, vminor = 0;

/* Write Agon compression header prefix and version info */
static void writeglobalheader(uint8_t *header, uint4 orig_size) 
{
    header[0] = 'C';
    header[1] = 'm';
    header[2] = 'p';
    header[3] = COMPRESSION_TYPE_RLE2;
    
    header[4] = orig_size & 0xFF;
    header[5] = (orig_size >> 8) & 0xFF;
    header[6] = (orig_size >> 16) & 0xFF;
    header[7] = (orig_size >> 24) & 0xFF;

    header[8] = 'R';
    header[9] = 'L';
    header[10] = 'E';
    header[11] = '2';
    header[12] = vmayor;  /* Major version */
    header[13] = vminor;  /* Minor version */
}

/*
 * encodeRLE:
 *   Forces each pixel to be fully opaque by ORing with 0xC0,
 *   then encodes the data using an RLE scheme.
 */
uint8_t *encodeRLE(const uint8_t *input, size_t input_size, size_t *encoded_size) {
    size_t capacity = HEADER_SIZE + input_size; // Worst-case: input plus header.
    uint8_t *output = malloc(capacity);
    if (!output) return NULL;
    writeglobalheader(output, (uint4)input_size);

    size_t out_index = HEADER_SIZE;
    size_t i = 0;
    while (i < input_size) {
        uint8_t pixel = input[i];
        size_t count = 1;
        /* Count identical pixels (max run length = 130) */
        while (i + count < input_size && input[i + count] == pixel && count < 130) {
            count++;
        }

        if (count == 2) {
            /* Two pixels stored as two singletons */
            for (int j = 0; j < 2; j++) {
                uint8_t alpha_bit = ((pixel & 0xC0) == 0xC0) ? 0x40 : 0x00;
                output[out_index++] = 0x80 | alpha_bit | (pixel & 0x3F);
            }
        } else if (count >= 3) {
            /* Run encoding: run byte (n-3) and literal pixel */
            output[out_index++] = (uint8_t)((count - 3) & 0x7F);
            output[out_index++] = pixel;
        } else {
            /* Singleton */
            uint8_t alpha_bit = ((pixel & 0xC0) == 0xC0) ? 0x40 : 0x00;
            output[out_index++] = 0x80 | alpha_bit | (pixel & 0x3F);
        }
        i += count;
    }

    uint8_t *final_output = realloc(output, out_index);
    if (!final_output)
        final_output = output;
    *encoded_size = out_index;
    return final_output;
}

/* Verify header and extract original size */
static int verifyRLEHeader(const uint8_t *input, size_t input_size, uint32_t *orig_size) {
    if (input_size < HEADER_SIZE)
        return 0; /* File too small */

    if (input[0] != 'C' || input[1] != 'm' || input[2] != 'p' || input[3] != COMPRESSION_TYPE_RLE2)
        return 0; /* Invalid header */

    *orig_size = input[4] | (input[5] << 8) | (input[6] << 16) | (input[7] << 24);

    if (input[8] != 'R' || input[9] != 'L' || input[10] != 'E' || input[11] != '2')
        return 0; /* Invalid RLE2 magic */

    return 1;
}

/* 
 * decodeRLE:
 *   Decodes an RLE2-encoded buffer into original pixel data.
 */
uint8_t *decodeRLE(const uint8_t *input, size_t input_size, size_t *output_size) {
    if (!input || input_size < HEADER_SIZE) {
        if (output_size) *output_size = 0;
        return NULL;
    }

    uint32_t orig_size;
    if (!verifyRLEHeader(input, input_size, &orig_size)) {
        fprintf(stderr, "Error: Invalid RLE2 header\n");
        return NULL;
    }

    uint8_t *output = malloc(orig_size);
    if (!output) {
        if (output_size) *output_size = 0;
        return NULL;
    }

    size_t i = HEADER_SIZE, out_index = 0;
    while (i < input_size) {
        uint8_t cmd = input[i++];
        if (cmd & 0x80) {
            /* Singleton: restore full opacity if needed */
            uint8_t color = cmd & 0x3F;
            uint8_t alpha = (cmd & 0x40) ? 0xC0 : 0x00;
            output[out_index++] = alpha | color;
        } else {
            /* Run: length is (cmd + 3) */
            size_t run = (cmd & 0x7F) + 3;
            if (i >= input_size) {
                free(output);
                if (output_size) *output_size = 0;
                return NULL;
            }
            uint8_t literal = input[i++];
            for (size_t j = 0; j < run; j++) {
                output[out_index++] = literal;
            }
        }
    }

    if (output_size)
        *output_size = out_index;
    return output;
}

/* Utility: Read entire file into a memory buffer */
static uint8_t *readFile(const char *filename, size_t *file_size) {
    FILE *in = fopen(filename, "rb");
    if (!in) return NULL;
    fseek(in, 0, SEEK_END);
    long size = ftell(in);
    rewind(in);
    uint8_t *data = malloc(size);
    if (!data) {
        fclose(in);
        return NULL;
    }
    if (fread(data, 1, size, in) != (size_t)size) {
        fclose(in);
        free(data);
        return NULL;
    }
    fclose(in);
    if (file_size)
        *file_size = size;
    return data;
}

/* Utility: Write a memory buffer to a file */
static int writeFile(const char *filename, const uint8_t *data, size_t data_size) {
    FILE *out = fopen(filename, "wb");
    if (!out) return 0;
    if (fwrite(data, 1, data_size, out) != data_size) {
        fclose(out);
        return 0;
    }
    fclose(out);
    return 1;
}

/* Compress source file to target file using RLE2 encoding */
static int compressFile(const char *srcFile, const char *tgtFile) {
    size_t file_size = 0;
    uint8_t *input_data = readFile(srcFile, &file_size);
    if (!input_data) {
        fprintf(stderr, "Error: Cannot open source file %s\n", srcFile);
        return 0;
    }
    size_t encoded_size = 0;
    uint8_t *encoded = encodeRLE(input_data, file_size, &encoded_size);
    free(input_data);
    if (!encoded) {
        fprintf(stderr, "Error: RLE encoding failed\n");
        return 0;
    }
    if (!writeFile(tgtFile, encoded, encoded_size)) {
        fprintf(stderr, "Error: Failed to write encoded data to %s\n", tgtFile);
        free(encoded);
        return 0;
    }
    free(encoded);
    return 1;
}

/* Decompress source file to target file using RLE2 decoding */
static int decompressFile(const char *srcFile, const char *tgtFile) {
    size_t file_size = 0;
    uint8_t *input_data = readFile(srcFile, &file_size);
    if (!input_data) {
        fprintf(stderr, "Error: Cannot open source file %s\n", srcFile);
        return 0;
    }
    size_t decoded_size = 0;
    uint8_t *decoded = decodeRLE(input_data, file_size, &decoded_size);
    free(input_data);
    if (!decoded) {
        fprintf(stderr, "Error: RLE decoding failed\n");
        return 0;
    }
    if (!writeFile(tgtFile, decoded, decoded_size)) {
        fprintf(stderr, "Error: Failed to write decoded data to %s\n", tgtFile);
        free(decoded);
        return 0;
    }
    free(decoded);
    return 1;
}

/* Main:
 *   Usage: rle2 [-c | -d] <source_file> <target_file>
 *     -c: compress
 *     -d: decompress
 */
int main(int argc, char *argv[]) {
    if (argc != 4) {
        fprintf(stderr, "Usage: rle2 [-c | -d] <source_file> <target_file>\n");
        return 1;
    }
    if (strcmp(argv[1], "-c") == 0) {
        if (!compressFile(argv[2], argv[3]))
            return 1;
    } else if (strcmp(argv[1], "-d") == 0) {
        if (!decompressFile(argv[2], argv[3]))
            return 1;
    } else {
        fprintf(stderr, "Usage: rle2 [-c | -d] <source_file> <target_file>\n");
        return 1;
    }
    return 0;
}
