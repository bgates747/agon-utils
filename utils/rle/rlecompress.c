/* rlecompress.c - RLE compressor for 8-bit rgba2222 data (plain C)
   (c)2025 ChatGPT <https://chatgpt.com>

   This version forces all pixels to full opacity (OR with 0xC0) and uses the following scheme:
     - Literal (singleton): encoded as 0x80 | (color & 0x3F)
     - Run (n >= 2): encoded as two bytes:
           first byte: 0x00 to 0x7F, representing (n - 2)
           second byte: literal pixel (already ORed with 0xC0)
   Maximum run length is 129 (since 129-2=127 fits in 7 bits).
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

typedef unsigned int uint4;
typedef unsigned int freq;  /* using uint4 for frequency counts */

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
    // Maximum possible output size: 2 * input_size bytes.
    size_t capacity = input_size * 2;
    uint8_t *output = malloc(capacity);
    if (!output) return NULL;
    size_t out_index = 0;
    size_t i = 0;
    while (i < input_size) {
        // Force the pixel to full opacity.
        uint8_t pixel = input[i] | 0xC0; // Ensure top two bits are 11.
        // Count identical pixels, max run length = 129.
        size_t count = 1;
        while (i + count < input_size && ((input[i + count] | 0xC0) == pixel) && count < 129) {
            count++;
        }
        if (count == 1) {
            // Singleton: output literal with top bit set.
            output[out_index++] = 0x80 | (pixel & 0x3F);
        } else {
            // Run: output run marker byte with top bit 0 and lower 7 bits = (count - 2),
            // then output the literal pixel.
            uint8_t run_marker = (uint8_t)(count - 2) & 0x7F;
            output[out_index++] = run_marker;
            output[out_index++] = pixel;
        }
        i += count;
    }
    // Shrink output buffer to actual size.
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
