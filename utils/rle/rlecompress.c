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

typedef unsigned int uint4;
typedef unsigned int freq;  /* using uint4 for frequency counts */
#define COMPRESSION_TYPE_RLE2 'r'
#define HEADER_SIZE 14
static char vmayor = 1, vminor = 0;

static void writeglobalheader(uint8_t *header, uint4 orig_size) 
{
    /* Write Agon compression header prefix: "Cmp" and COMPRESSION_TYPE_RLE2 */
    header[0] = 'C';
    header[1] = 'm';
    header[2] = 'p';
    header[3] = COMPRESSION_TYPE_RLE2;
    
    /* Write original file size (4 bytes, little-endian order) */
    header[4] = orig_size & 0xFF;
    header[5] = (orig_size >> 8) & 0xFF;
    header[6] = (orig_size >> 16) & 0xFF;
    header[7] = (orig_size >> 24) & 0xFF;

    /* Write RLE2 magic bytes and version numbers */
    header[8] = 'R';
    header[9] = 'L';
    header[10] = 'E';
    header[11] = '2';
    header[12] = vmayor;  /* Major version */
    header[13] = vminor;  /* Minor version */
}

/* 
 * encodeRLE:
 *   Input:
 *      - input: pointer to an array of 8-bit pixels.
 *      - input_size: number of pixels.
 *   This function first forces each pixel to be fully opaque by ORing with 0xC0,
 *   then encodes the data using our RLE scheme.
 *   Returns a newly allocated buffer with the encoded data and sets *encoded_size.
 */
uint8_t *encodeRLE(const uint8_t *input, size_t input_size, size_t *encoded_size) {
    size_t capacity = HEADER_SIZE + input_size; // Worst case: original size + header
    uint8_t *output = malloc(capacity);
    if (!output) return NULL;
    writeglobalheader(output, (uint4)input_size);

    size_t out_index = HEADER_SIZE;
    size_t i = 0;

    while (i < input_size) {
        uint8_t pixel = input[i]; // Preserve original pixel, including transparency
        size_t count = 1;

        // Count identical pixels (max run length = 130, since 0x7F means 130)
        while (i + count < input_size && input[i + count] == pixel && count < 130) {
            count++;
        }

        if (count == 2) {
            // Two-pixel runs are stored as two singletons
            for (int j = 0; j < 2; j++) {
                uint8_t alpha_bit = ((pixel & 0xC0) == 0xC0) ? 0x40 : 0x00; // Check both bit 6 & 7
                output[out_index++] = 0x80 | alpha_bit | (pixel & 0x3F);
            }
        } else if (count >= 3) {
            // Run encoding: run byte (n-3) + one byte for the pixel
            output[out_index++] = (uint8_t)(count - 3) & 0x7F; // Run marker (bit 7 = 0)
            output[out_index++] = pixel; // Store literal as-is (no modifications to bits 6/7)
        } else {
            // Singleton: Bit 7 is 1, bit 6 is forced based on transparency rule
            uint8_t alpha_bit = ((pixel & 0xC0) == 0xC0) ? 0x40 : 0x00; // Check both bit 6 & 7
            output[out_index++] = 0x80 | alpha_bit | (pixel & 0x3F);
        }

        i += count;
    }

    // Shrink output buffer to actual size
    uint8_t *final_output = realloc(output, out_index);
    if (!final_output)
        final_output = output;
    *encoded_size = out_index;
    return final_output;
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Usage: rlecompress <src file> <tgt file>\n");
        return 1;
    }
    const char *srcFile = argv[1];
    const char *tgtFile = argv[2];

    // Read entire source file into a buffer.
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
    if (fread(input_data, 1, file_size, in) != file_size) {
        fclose(in);
        free(input_data);
        fprintf(stderr, "Error: Failed to read source file %s\n", srcFile);
        return 1;
    }
    fclose(in);

    // Perform RLE encoding.
    size_t encoded_size = 0;
    uint8_t *encoded = encodeRLE(input_data, file_size, &encoded_size);
    free(input_data);
    if (!encoded) {
        fprintf(stderr, "Error: RLE encoding failed\n");
        return 1;
    }

    // Write encoded data to target file.
    FILE *out = fopen(tgtFile, "wb");
    if (!out) {
        fprintf(stderr, "Error: Cannot open target file %s\n", tgtFile);
        free(encoded);
        return 1;
    }
    if (fwrite(encoded, 1, encoded_size, out) != encoded_size) {
        fprintf(stderr, "Error: Failed to write encoded data to %s\n", tgtFile);
        fclose(out);
        free(encoded);
        return 1;
    }
    fclose(out);
    free(encoded);
    return 0;
}
