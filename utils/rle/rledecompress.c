/*
 * RLE compressor/decompressor for 8-bit RGBA2222 data
 *
 * Encoding rules:
 *   - Single pixel (n=1): 
 *       top bit = 1 (0x80)
 *       bit 6 encodes alpha (1 => fully opaque [bits 7,6=11], 0 => fully transparent [bits 7,6=00])
 *       bits 5..0 = color
 *
 *   - Two pixels (n=2): stored as two singletons (no run used).
 *
 *   - Run of 3..130 (n >=3): 
 *       the run byte is (n - 3) with top bit 0 (so 0 => 3 pixels, 127 => 130 pixels),
 *       then one more byte containing the pixel in RGBA2222 format, 
 *         but only bits 7,6 are actually used for alpha (1 => 11, 0 => 00).
 *
 * Example:
 *   If count=3, run byte=0, second byte=<pixel>
 *   If count=130, run byte=127, second byte=<pixel>
 *
 * The system displays only fully transparent or fully opaque, so if either bit 7 or bit 6 
 * in the original pixel is clear, we treat alpha as 0 => bits 7,6=00, else bits 7,6=11.
 *
 * Worst-case compressed size is (original file size + 14-byte header).
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define HEADER_SIZE 14
#define COMPRESSION_TYPE_RLE2 'r'

/* Verify header and extract original size */
static int verifyRLEHeader(const uint8_t *input, size_t input_size, uint32_t *orig_size) {
    if (input_size < HEADER_SIZE) {
        return 0; // Invalid file, too small for a valid header.
    }

    // Check magic bytes
    if (input[0] != 'C' || input[1] != 'm' || input[2] != 'p' || input[3] != COMPRESSION_TYPE_RLE2) {
        return 0; // Invalid header
    }

    // Extract original file size (little-endian)
    *orig_size = input[4] | (input[5] << 8) | (input[6] << 16) | (input[7] << 24);

    // Verify RLE2 magic
    if (input[8] != 'R' || input[9] != 'L' || input[10] != 'E' || input[11] != '2') {
        return 0; // Invalid header
    }

    return 1; // Header is valid
}

/* Decode an RLE-encoded buffer. */
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

    uint8_t *output = (uint8_t *)malloc(orig_size);
    if (!output) {
        if (output_size) *output_size = 0;
        return NULL;
    }

    size_t i = HEADER_SIZE, out_index = 0;

    while (i < input_size) {
        uint8_t cmd = input[i++];

        if (cmd & 0x80) {
            // Singleton: Restore transparency by copying bit 6 into bit 7
            uint8_t color = cmd & 0x3F;
            uint8_t alpha = (cmd & 0x40) ? 0xC0 : 0x00; // If bit 6 is 1, set 7+6 to 11; else 00
            output[out_index++] = alpha | color;
        } else {
            // Run: Read length and literal
            size_t run = (cmd & 0x7F) + 3; // Minimum run length is 3
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

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: rledecompress <src file> <tgt file>\n");
        return 1;
    }
    const char *srcFile = argv[1];
    const char *tgtFile = argv[2];

    /* Read the entire source file into memory */
    FILE *in = fopen(srcFile, "rb");
    if (!in) {
        fprintf(stderr, "Error: Cannot open source file %s\n", srcFile);
        return 1;
    }
    fseek(in, 0, SEEK_END);
    long file_size = ftell(in);
    rewind(in);
    uint8_t *input_data = malloc(file_size);
    if (!input_data) {
        fclose(in);
        fprintf(stderr, "Error: Memory allocation failed for input data\n");
        return 1;
    }
    if (fread(input_data, 1, file_size, in) != (size_t)file_size) {
        fclose(in);
        free(input_data);
        fprintf(stderr, "Error: Failed to read source file %s\n", srcFile);
        return 1;
    }
    fclose(in);

    size_t decoded_size = 0;
    uint8_t *decoded = decodeRLE(input_data, file_size, &decoded_size);
    free(input_data);
    if (!decoded) {
        fprintf(stderr, "Error: RLE decoding failed\n");
        return 1;
    }

    /* Write decoded data to target file */
    FILE *out = fopen(tgtFile, "wb");
    if (!out) {
        fprintf(stderr, "Error: Cannot open target file %s\n", tgtFile);
        free(decoded);
        return 1;
    }
    if (fwrite(decoded, 1, decoded_size, out) != decoded_size) {
        fprintf(stderr, "Error: Failed to write decoded data to %s\n", tgtFile);
        fclose(out);
        free(decoded);
        return 1;
    }
    fclose(out);
    free(decoded);
    return 0;
}
