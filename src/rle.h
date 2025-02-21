#ifndef RLE_H
#define RLE_H

#ifdef __cplusplus
extern "C" {
#endif

#include <stddef.h>
#include <stdint.h>

/**
 * _rle_encode_internal - Encodes an array of 8-bit rgba2222 pixels using RLE compression.
 *
 * @input:       Pointer to the input array of pixels (each pixel is 8 bits).
 * @input_size:  Number of pixels in the input array.
 * @output_size: Pointer to a size_t variable that will receive the size (in bytes)
 *              of the encoded output.
 *
 * Returns: A pointer to a newly allocated buffer containing the encoded data.
 *          On failure, returns NULL.
 *          The caller is responsible for freeing the returned buffer.
 */
uint8_t *_rle_encode_internal(const uint8_t *input, size_t input_size, size_t *output_size);

/**
 * _rle_decode_internal - Decode an RLE-encoded buffer of rgba2222 pixels.
 *
 * @input: Pointer to the RLE-encoded data.
 * @input_size: Size of the encoded data in bytes.
 * @output_size: Pointer to a size_t variable where the decoded output size will be stored.
 *
 * Returns: A pointer to a newly allocated buffer containing the decoded (raw rgba2222)
 *          data. The caller is responsible for freeing the buffer. On error, returns NULL.
 */
uint8_t *_rle_decode_internal(const uint8_t *input, size_t input_size, size_t *output_size);

#ifdef __cplusplus
}
#endif

#endif /* RLE_H */
