/* rledecompress.c - RLE decompressor for 8-bit rgba2222 pixels
   (c)2025 ChatGPT <https://chatgpt.com>

   This program reads an RLE-compressed file produced by our RLE compressor,
   decodes it to raw rgba2222 data (with full alpha, i.e. 11cccccc), and writes
   the output to a target file.

   Compression scheme:
     - Singleton (literal): If the command byte has its top bit set (1xxx xxxx),
       then the lower 6 bits represent the color.
       Decompressed pixel = 0xC0 | (cmd & 0x3F)
     - Run: If the command byte’s top bit is 0 (0xxx xxxx),
       then the lower 7 bits represent (n - 2), where n is the number of pixels.
       The next byte is a literal pixel (already in 11cccccc form).
       The run length n = (cmd & 0x7F) + 2.
*/

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

/* Compute the decoded size by scanning through the input buffer.
   Each command is either a singleton (1 byte) or a run (2 bytes).
*/
static size_t _rle_decoded_size(const uint8_t *input, size_t input_size) {
    size_t decoded_size = 0;
    size_t i = 0;
    while (i < input_size) {
        uint8_t cmd = input[i++];
        if (cmd & 0x80) {
            // Singleton command.
            decoded_size += 1;
        } else {
            // Run command: next byte holds the literal.
            decoded_size += ((cmd & 0x7F) + 2);
            i++; // Skip the literal byte.
        }
    }
    return decoded_size;
}

/* Decode an RLE-encoded buffer.
   Parameters:
      input: pointer to the encoded data.
      input_size: size in bytes of the encoded data.
      output_size: pointer to a size_t to receive the decoded size.
   Returns:
      A newly allocated buffer with the decoded data, or NULL on error.
      The caller is responsible for freeing the buffer.
*/
uint8_t *decodeRLE(const uint8_t *input, size_t input_size, size_t *output_size) {
    if (!input || input_size == 0) {
        if (output_size) *output_size = 0;
        return NULL;
    }

    size_t dec_size = _rle_decoded_size(input, input_size);
    uint8_t *output = (uint8_t *)malloc(dec_size);
    if (!output) {
        if (output_size) *output_size = 0;
        return NULL;
    }

    size_t i = 0, out_index = 0;
    while (i < input_size) {
        uint8_t cmd = input[i++];
        if (cmd & 0x80) {
            // Singleton command: lower 6 bits encode the color.
            uint8_t color = cmd & 0x3F;
            // Decompressed pixel: force full alpha (11xxxxxx).
            output[out_index++] = 0xC0 | color;
        } else {
            // Run command: lower 7 bits indicate (n - 2)
            size_t run = (cmd & 0x7F) + 2;
            if (i >= input_size) { // Ensure there is a literal byte.
                free(output);
                if (output_size) *output_size = 0;
                return NULL;
            }
            uint8_t literal = input[i++];
            // Output the literal 'run' times.
            for (size_t j = 0; j < run; j++) {
                output[out_index++] = literal;
            }
        }
    }
    if (output_size)
        *output_size = out_index;
    return output;
}

/* Main function: command-line interface for decompression.
   Usage: rledecompress <src file> <tgt file>
*/
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
