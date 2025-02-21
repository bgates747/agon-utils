#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>

// Define the compression type constant (note: no '=' is used in macro definitions)
#define COMPRESSION_TYPE_MASK 4

typedef struct {
    uint8_t     marker[3];
    uint8_t     type;
    uint32_t    orig_size;
} CompressionFileHeader;

// Compressor: reads the source file in 8‐byte blocks,
// writes a header, then for each block writes one mask byte
// (bit set if the corresponding input byte is nonzero) followed by the nonzero bytes.
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
        uint8_t mask = 0;
        // Compute the mask: each bit set if corresponding byte is nonzero.
        for (size_t i = 0; i < bytesRead; i++) {
            if (block[i] != 0) {
                mask |= (1 << i);
            }
        }
        // Write the mask byte
        if (fwrite(&mask, 1, 1, out) != 1) {
            perror("Error writing mask");
            fclose(in);
            fclose(out);
            return 1;
        }
        // Write nonzero bytes in order
        for (size_t i = 0; i < bytesRead; i++) {
            if (block[i] != 0) {
                if (fwrite(&block[i], 1, 1, out) != 1) {
                    perror("Error writing compressed data");
                    fclose(in);
                    fclose(out);
                    return 1;
                }
            }
        }
    }

    fclose(in);
    fclose(out);
    return 0;
}

// Decompressor: reads the header, then for each 8-byte block
// reads a mask byte and reconstructs the original block by inserting zero bytes where the mask bit is clear.
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
        fprintf(stderr, "Invalid file format\n");
        fclose(in);
        fclose(out);
        return 1;
    }

    uint32_t orig_size = hdr.orig_size;
    uint32_t total_written = 0;

    // Process each block until the original file size is reached.
    while (total_written < orig_size) {
        uint8_t mask;
        if (fread(&mask, 1, 1, in) != 1) {
            perror("Error reading mask");
            fclose(in);
            fclose(out);
            return 1;
        }

        // Determine how many bytes to process in this block (last block may be less than 8 bytes)
        uint32_t block_size = (orig_size - total_written >= 8) ? 8 : (orig_size - total_written);
        for (uint32_t i = 0; i < block_size; i++) {
            uint8_t byte;
            if (mask & (1 << i)) {
                // Byte was nonzero in the original file; read it from the compressed stream.
                if (fread(&byte, 1, 1, in) != 1) {
                    perror("Error reading compressed data");
                    fclose(in);
                    fclose(out);
                    return 1;
                }
            } else {
                byte = 0;
            }
            if (fwrite(&byte, 1, 1, out) != 1) {
                perror("Error writing decompressed data");
                fclose(in);
                fclose(out);
                return 1;
            }
        }
        total_written += block_size;
    }

    fclose(in);
    fclose(out);
    return 0;
}

// Main program: expects command-line arguments:
//   mskz [-c|-d] src_file tgt_file
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
