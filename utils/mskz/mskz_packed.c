#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// We'll still call it the same compression type for this example.
// In a real system, you might define a new type to avoid confusion
// or ensure older decompressors won't break.
#define COMPRESSION_TYPE_MASK 4

// File header
typedef struct {
    uint8_t     marker[3];
    uint8_t     type;
    uint32_t    orig_size;
} CompressionFileHeader;

/**
 * Write up to 'bitCount' bits from 'bitBuffer' to 'out'.
 * Returns 0 on success, 1 on error.
 */
static int write_bit_buffer(FILE* out, uint64_t bitBuffer, int bitCount) {
    // Number of whole bytes to write from bitBuffer
    int bytesToWrite = (bitCount + 7) / 8; // ceiling division for bits→bytes

    for (int i = 0; i < bytesToWrite; i++) {
        // Extract low 8 bits
        uint8_t b = (uint8_t)(bitBuffer & 0xFF);
        if (fwrite(&b, 1, 1, out) != 1) {
            return 1;
        }
        bitBuffer >>= 8;
    }
    return 0;
}

/**
 * Read 'numBits' from the input stream into a 64-bit buffer (low-order bits first).
 * Returns 0 on success, 1 on error.
 * On success, bitBuffer contains the bits in the lowest 'numBits' bits.
 */
static int read_bit_buffer(FILE* in, uint64_t* bitBuffer, int numBits) {
    *bitBuffer = 0;
    int bytesToRead = (numBits + 7) / 8;
    uint64_t temp = 0;

    uint8_t chunk[6]; // up to 6 bytes needed for 48 bits
    // Initialize to zero for safety
    memset(chunk, 0, sizeof(chunk));

    if (fread(chunk, 1, bytesToRead, in) != (size_t)bytesToRead) {
        return 1;
    }

    // Reassemble into a 64-bit buffer
    for (int i = 0; i < bytesToRead; i++) {
        temp |= ((uint64_t)chunk[i] << (8 * i));
    }
    *bitBuffer = temp;
    return 0;
}

// ---------------------------------------------------------------------------

/**
 * Compress file using mask + 6-bit packing for non-transparent pixels.
 * Non-transparent means top two bits == 11 (values 192..255).
 * We read in 8-byte blocks, build a mask, then bit-pack the lower 6 bits
 * of each non-transparent pixel in the block.
 */
int compress_file(const char* src_path, const char* dst_path) {
    FILE* in = fopen(src_path, "rb");
    if (!in) {
        perror("Error opening source file");
        return 1;
    }
    FILE* out = fopen(dst_path, "wb");
    if (!out) {
        perror("Error opening destination file");
        fclose(in);
        return 1;
    }

    // Determine original file size
    fseek(in, 0, SEEK_END);
    long filesize = ftell(in);
    fseek(in, 0, SEEK_SET);

    // Prepare and write the header
    CompressionFileHeader hdr;
    hdr.marker[0] = 'm';
    hdr.marker[1] = 's';
    hdr.marker[2] = 'k';
    hdr.type      = COMPRESSION_TYPE_MASK;
    hdr.orig_size = (uint32_t)filesize;

    if (fwrite(&hdr, sizeof(hdr), 1, out) != 1) {
        perror("Error writing header");
        fclose(in);
        fclose(out);
        return 1;
    }

    // Process the file in blocks of 8 bytes
    uint8_t block[8];
    size_t bytesRead;
    while ((bytesRead = fread(block, 1, 8, in)) > 0) {
        // Build the mask
        uint8_t mask = 0;
        // We'll store the 6-bit values in a 64-bit buffer with a running bitCount
        uint64_t bitBuffer = 0;
        int bitCount = 0;

        // Identify non-transparent pixels & pack their lower 6 bits
        for (size_t i = 0; i < bytesRead; i++) {
            // If top two bits != 11 (i.e. (val & 0xC0) != 0xC0), treat as transparent
            if ((block[i] & 0xC0) == 0xC0) {
                // Set mask bit
                mask |= (1 << i);
                // Pack the lower 6 bits
                uint8_t val6 = (uint8_t)(block[i] & 0x3F); // bottom 6 bits
                // Put val6 into bitBuffer
                bitBuffer |= ((uint64_t)val6 << bitCount);
                bitCount += 6; // advanced by 6 bits
            }
        }

        // Write the mask
        if (fwrite(&mask, 1, 1, out) != 1) {
            perror("Error writing mask");
            fclose(in);
            fclose(out);
            return 1;
        }

        // Write the packed 6-bit data
        if (bitCount > 0) {
            if (write_bit_buffer(out, bitBuffer, bitCount) != 0) {
                perror("Error writing bit-packed data");
                fclose(in);
                fclose(out);
                return 1;
            }
        }
    }

    fclose(in);
    fclose(out);
    return 0;
}

// ---------------------------------------------------------------------------

/**
 * Decompress file that was compressed by the above function.
 * We read an 8-byte block at a time from the original. For each block:
 *   1) Read the mask (1 byte).
 *   2) Count how many bits are set. Let that be nSetBits.
 *   3) We know we need nSetBits * 6 bits from the compressed stream.
 *   4) Unpack each 6-bit value to reconstruct the original pixel:
 *       pixel = 0xC0 | (val6)
 *   5) If the mask bit was 0, pixel = 0 (transparent).
 */
int decompress_file(const char* src_path, const char* dst_path) {
    FILE* in = fopen(src_path, "rb");
    if (!in) {
        perror("Error opening source file");
        return 1;
    }
    FILE* out = fopen(dst_path, "wb");
    if (!out) {
        perror("Error opening destination file");
        fclose(in);
        return 1;
    }

    // Read and validate header
    CompressionFileHeader hdr;
    if (fread(&hdr, sizeof(hdr), 1, in) != 1) {
        perror("Error reading header");
        fclose(in);
        fclose(out);
        return 1;
    }
    if (hdr.marker[0] != 'm' || hdr.marker[1] != 's' || hdr.marker[2] != 'k' ||
        hdr.type != COMPRESSION_TYPE_MASK) {
        fprintf(stderr, "Invalid file format or compression type\n");
        fclose(in);
        fclose(out);
        return 1;
    }

    uint32_t orig_size = hdr.orig_size;
    uint32_t total_written = 0;

    while (total_written < orig_size) {
        // Each block can be up to 8 bytes, but the last block might be smaller
        uint32_t block_size = (orig_size - total_written >= 8)
                              ? 8
                              : (orig_size - total_written);

        // Read the mask
        uint8_t mask;
        if (fread(&mask, 1, 1, in) != 1) {
            // It's possible we are at EOF exactly, but that would be malformed
            perror("Error reading mask");
            fclose(in);
            fclose(out);
            return 1;
        }

        // Count how many set bits in 'mask' (i.e. how many non-transparent pixels)
        int nSetBits = 0;
        for (int i = 0; i < (int)block_size; i++) {
            if (mask & (1 << i)) {
                nSetBits++;
            }
        }

        // Read bit-packed data (nSetBits * 6 bits)
        if (nSetBits > 0) {
            uint64_t bitBuffer;
            int bitsNeeded = nSetBits * 6;
            if (read_bit_buffer(in, &bitBuffer, bitsNeeded) != 0) {
                perror("Error reading packed bits");
                fclose(in);
                fclose(out);
                return 1;
            }

            // Now decode them in the order of set bits
            int bitOffset = 0;
            for (int i = 0; i < (int)block_size; i++) {
                if (mask & (1 << i)) {
                    // Extract 6 bits from bitBuffer
                    uint8_t val6 = (bitBuffer >> bitOffset) & 0x3F;
                    bitOffset += 6;

                    // Reconstruct original pixel (top bits = 11)
                    uint8_t pixel = 0xC0 | val6;
                    if (fwrite(&pixel, 1, 1, out) != 1) {
                        perror("Error writing pixel");
                        fclose(in);
                        fclose(out);
                        return 1;
                    }
                } else {
                    // Transparent pixel (0)
                    uint8_t zero = 0;
                    if (fwrite(&zero, 1, 1, out) != 1) {
                        perror("Error writing transparent pixel");
                        fclose(in);
                        fclose(out);
                        return 1;
                    }
                }
            }
        } else {
            // No non-transparent pixels => entire block is zeros
            for (uint32_t i = 0; i < block_size; i++) {
                uint8_t zero = 0;
                if (fwrite(&zero, 1, 1, out) != 1) {
                    perror("Error writing zeros");
                    fclose(in);
                    fclose(out);
                    return 1;
                }
            }
        }

        total_written += block_size;
    }

    fclose(in);
    fclose(out);
    return 0;
}

// ---------------------------------------------------------------------------

int main(int argc, char** argv) {
    if (argc != 4) {
        fprintf(stderr, "Usage: %s [-c|-d] src_file tgt_file\n", argv[0]);
        return 1;
    }

    if (strcmp(argv[1], "-c") == 0) {
        return compress_file(argv[2], argv[3]);
    } else if (strcmp(argv[1], "-d") == 0) {
        return decompress_file(argv[2], argv[3]);
    } else {
        fprintf(stderr, "Invalid mode. Use -c for compression and -d for decompression.\n");
        return 1;
    }
}
