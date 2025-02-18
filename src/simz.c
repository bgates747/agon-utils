/* simz.c - Combined simple zip compressor/decompressor
   (c)1999 Michael Schindler, michael@compressconsult.com

   This version removes I/O macros and replaces them with explicit function calls.
*/

#include "simz.h"
#include "rangecod.h"
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* Version string */
char coderversion[] = "simple zip v1.0 (c)1999 Michael Schindler";

/* Maximum block size */
#define BLOCKSIZE 60000

/***************** Compression Functions *****************/

/* Count occurrences of each byte in the buffer */
static void countblock(const uint8_t *buffer, freq length, freq *counters) {
    for (unsigned int i = 0; i < 257; i++) {
        counters[i] = 0;
    }
    for (unsigned int i = 0; i < length; i++) {
        counters[buffer[i]]++;
    }
}

/* Compress data from input buffer to output buffer */
static uint8_t *compress_data(const uint8_t *input, size_t input_size, size_t *output_size) {
    freq counts[257], blocksize;
    rangecoder rc;
    uint8_t *output = (uint8_t *)malloc(input_size + 1024);  // Allocate enough space
    if (!output) return NULL;

    uint8_t *out_ptr = output;
    start_encoding(&rc, 0, 0);

    size_t processed = 0;
    while (processed < input_size) {
        blocksize = (input_size - processed) > BLOCKSIZE ? BLOCKSIZE : (input_size - processed);

        // Write block flag (one-bit coding)
        encode_freq(&rc, 1, 1, 2);

        // Build statistics
        countblock(input + processed, blocksize, counts);

        // Write statistics for 256 symbols
        for (int i = 0; i < 256; i++) {
            encode_short(&rc, counts[i]);
        }

        // Convert to cumulative counts
        counts[256] = blocksize;
        for (int i = 256; i > 0; i--) {
            counts[i - 1] = counts[i] - counts[i - 1];
        }

        // Encode symbols
        for (int i = 0; i < blocksize; i++) {
            int ch = input[processed + i];
            encode_freq(&rc, counts[ch + 1] - counts[ch], counts[ch], counts[256]);
        }

        processed += blocksize;
    }

    // Flag the end of data
    encode_freq(&rc, 1, 0, 2);

    // Finish encoding
    *output_size = done_encoding(&rc);
    return output;
}

/**************** Decompression Functions ****************/

/* Read frequency counts */
static void readcounts(rangecoder *rc, freq *counters) {
    for (int i = 0; i < 256; i++) {
        counters[i] = decode_short(rc);
    }
}

/* Decompress data from input buffer to output buffer */
static uint8_t *decompress_data(const uint8_t *input, size_t input_size, size_t *output_size) {
    rangecoder rc;
    if (start_decoding(&rc) != 0) {
        return NULL;
    }

    uint8_t *output = (uint8_t *)malloc(input_size * 2);  // Allocate a safe size
    if (!output) return NULL;

    uint8_t *out_ptr = output;
    size_t total_decompressed = 0;

    while (1) {
        // Check if more blocks exist
        freq cf = decode_culfreq(&rc, 2);
        if (cf == 0) break;
        decode_update(&rc, 1, 1, 2);

        freq counts[257], blocksize;

        // Read frequency counts
        readcounts(&rc, counts);

        // Compute block size
        blocksize = 0;
        for (int i = 0; i < 256; i++) {
            freq tmp = counts[i];
            counts[i] = blocksize;
            blocksize += tmp;
        }
        counts[256] = blocksize;

        // Decode symbols
        for (int i = 0; i < blocksize; i++) {
            freq cf_sym = decode_culfreq(&rc, blocksize);
            freq symbol = 0;
            while (counts[symbol + 1] <= cf_sym) {
                symbol++;
            }
            decode_update(&rc, counts[symbol + 1] - counts[symbol], counts[symbol], blocksize);
            *out_ptr++ = (uint8_t)symbol;
            total_decompressed++;
        }
    }

    done_decoding(&rc);
    *output_size = total_decompressed;
    return output;
}