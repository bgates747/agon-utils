#ifndef RLE2_H
#define RLE2_H

#include <stddef.h>
#include <stdint.h>

/* Compression constants */
#define COMPRESSION_TYPE_RLE2 'r'
#define HEADER_SIZE 14

#ifdef __cplusplus
extern "C" {
#endif

/**
 * encodeRLE:
 *   Encodes an 8-bit RGBA2222 input buffer into RLE2 format.
 *
 * @param input         Pointer to the input pixel data.
 * @param input_size    Number of pixels in the input.
 * @param encoded_size  Pointer to size_t to receive the size of the encoded data.
 *
 * @return A newly allocated buffer containing the RLE2-encoded data,
 *         or NULL if encoding fails.
 */
uint8_t *encodeRLE(const uint8_t *input, size_t input_size, size_t *encoded_size);

/**
 * decodeRLE:
 *   Decodes an RLE2-encoded buffer back into 8-bit RGBA2222 pixel data.
 *
 * @param input         Pointer to the encoded data.
 * @param input_size    Size of the encoded data.
 * @param output_size   Pointer to size_t to receive the size of the decoded data.
 *
 * @return A newly allocated buffer containing the decoded pixel data,
 *         or NULL if decoding fails.
 */
uint8_t *decodeRLE(const uint8_t *input, size_t input_size, size_t *output_size);

#ifdef __cplusplus
}
#endif

#endif /* RLE2_H */
