/*
MIT License

Copyright (c) 2024 Curtis Whitley (TurboVega)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
*/

/*
ADDENDUM: February 2025

Lightly modified by Brandon R. Gates (BeeGee747) to compile as a single 
executable with `tvc [-c | -d] <source_file> <target_file>` command line 
arguments. The original source code can be found at: 
https://github.com/TurboVega/agon_compression

All conditions of the original MIT License apply to this modified version, 
including but not limited to the permissions, limitations, and disclaimers 
stated therein. 

All rights, ownership, and claims to the original work remain solely with 
Curtis Whitley (TurboVega). The modifications made herein do not grant any 
additional rights or claims beyond those expressly permitted under the 
original license.

The above notice of modifications and the original license must be included
in all copies or substantial portions of the Software.
*/

#include "tvc.h"

/* --- Compression routines --- */

// This implementation uses a window size of 256 bytes, and a code size of 10 bits.
// The maximum compressed byte string size is 16 bytes.
//
// Code bits:
// 0000000000
// 9876543210
// ----------
// 00xxxxxxxx   New original data byte with value of xxxxxxxx
// 01iiiiiiii   String of 4 bytes starting at window index iiiiiiii
// 10iiiiiiii   String of 8 bytes starting at window index iiiiiiii
// 11iiiiiiii   String of 16 bytes starting at window index iiiiiiii
//
// Note: Worst case, the output can be 25% LARGER than the input!
//
// Usage: tvc [-c | -d] <source_file> <target_file>
//

void my_write_compressed_byte(void* context, uint8_t comp_byte) {
    fwrite(&comp_byte, 1, 1, (FILE*)context);
}

void agon_init_compression(CompressionData* cd, void* context, WriteCompressedByte write_fcn) {
    memset(cd, 0, sizeof(CompressionData));
    cd->context = context;
    cd->write_fcn = write_fcn;
}

void agon_write_compressed_bit(CompressionData* cd, uint8_t comp_bit) {
    cd->out_byte = (cd->out_byte << 1) | comp_bit;
    if (++(cd->out_bits) >= 8) {
        (*cd->write_fcn)(cd->context, cd->out_byte);
        cd->out_byte = 0;
        cd->out_bits = 0;
        cd->output_count++;
    }
}

void agon_write_compressed_byte(CompressionData* cd, uint8_t comp_byte) {
    for (uint8_t bit = 0; bit < 8; bit++) {
        agon_write_compressed_bit(cd, (comp_byte & 0x80) ? 1 : 0);
        comp_byte <<= 1;
    }
}

void agon_compress_byte(CompressionData* cd, uint8_t orig_byte) {
    /* Add the new original byte to the string */
    cd->string_data[cd->string_write_index++] = orig_byte;
    cd->string_write_index &= (COMPRESSION_STRING_SIZE - 1);
    if (cd->string_size < COMPRESSION_STRING_SIZE) {
        (cd->string_size)++;
    } else {
        cd->string_read_index = (cd->string_read_index + 1) & (COMPRESSION_STRING_SIZE - 1);
    }

    if (cd->string_size >= 16) {
        if (cd->window_size >= 16) {
            /* Try to find a full 16-byte match in the window */
            for (uint32_t start = 0; start <= cd->window_size - 16; start++) {
                uint32_t wi = start;
                uint32_t si = cd->string_read_index;
                uint8_t match = 1;
                for (uint8_t i = 0; i < 16; i++) {
                    if (cd->window_data[wi++] != cd->string_data[si++]) {
                        match = 0;
                        break;
                    }
                    wi &= (COMPRESSION_WINDOW_SIZE - 1);
                    si &= (COMPRESSION_STRING_SIZE - 1);
                }
                if (match) {
                    /* Output command: 11 + window index */
                    agon_write_compressed_bit(cd, 1);
                    agon_write_compressed_bit(cd, 1);
                    agon_write_compressed_byte(cd, (uint8_t)(start));
                    cd->string_size = 0;
                    return;
                }
            }
        }

        if (cd->window_size >= 8) {
            /* Try a partial match of 8 bytes */
            for (uint32_t start = 0; start <= cd->window_size - 8; start++) {
                uint32_t wi = start;
                uint32_t si = cd->string_read_index;
                uint8_t match = 1;
                for (uint8_t i = 0; i < 8; i++) {
                    if (cd->window_data[wi++] != cd->string_data[si++]) {
                        match = 0;
                        break;
                    }
                    wi &= (COMPRESSION_WINDOW_SIZE - 1);
                    si &= (COMPRESSION_STRING_SIZE - 1);
                }
                if (match) {
                    /* Output command: 10 + window index */
                    agon_write_compressed_bit(cd, 1);
                    agon_write_compressed_bit(cd, 0);
                    agon_write_compressed_byte(cd, (uint8_t)(start));
                    cd->string_size -= 8;
                    cd->string_read_index = (cd->string_read_index + 8) & (COMPRESSION_STRING_SIZE - 1);
                    return;
                }
            }
        }
            
        if (cd->window_size >= 4) {
            /* Try a partial match of 4 bytes */
            for (uint32_t start = 0; start <= cd->window_size - 4; start++) {
                uint32_t wi = start;
                uint32_t si = cd->string_read_index;
                uint8_t match = 1;
                for (uint8_t i = 0; i < 4; i++) {
                    if (cd->window_data[wi++] != cd->string_data[si++]) {
                        match = 0;
                        break;
                    }
                    wi &= (COMPRESSION_WINDOW_SIZE - 1);
                    si &= (COMPRESSION_STRING_SIZE - 1);
                }
                if (match) {
                    /* Output command: 01 + window index */
                    agon_write_compressed_bit(cd, 0);
                    agon_write_compressed_bit(cd, 1);
                    agon_write_compressed_byte(cd, (uint8_t)(start));
                    cd->string_size -= 4;
                    cd->string_read_index = (cd->string_read_index + 4) & (COMPRESSION_STRING_SIZE - 1);
                    return;
                }
            }
        }

        /* No match found; output the oldest byte in the string */
        uint8_t old_byte = cd->string_data[cd->string_read_index++];
        agon_write_compressed_bit(cd, 0);
        agon_write_compressed_bit(cd, 0);
        agon_write_compressed_byte(cd, old_byte);
        cd->string_size -= 1;
        cd->string_read_index &= (COMPRESSION_STRING_SIZE - 1);

        /* Add the old byte to the window */
        cd->window_data[cd->window_write_index++] = old_byte;
        cd->window_write_index &= (COMPRESSION_WINDOW_SIZE - 1);
        if (cd->window_size < COMPRESSION_WINDOW_SIZE) {
            (cd->window_size)++;
        }
    }
}

void agon_finish_compression(CompressionData* cd) {
    /* Flush any remaining bytes in the string */
    while (cd->string_size) {
        agon_write_compressed_bit(cd, 0);
        agon_write_compressed_bit(cd, 0);
        agon_write_compressed_byte(cd, cd->string_data[cd->string_read_index++]);
        cd->string_size -= 1;
        cd->string_read_index &= (COMPRESSION_STRING_SIZE - 1);
    }
    if (cd->out_bits) {
        (*cd->write_fcn)(cd->context, (cd->out_byte << (8 - cd->out_bits)));
        cd->output_count++;
    }
}

/* --- Decompression routines --- */

void my_write_decompressed_byte(void* context, uint8_t orig_data) {
    fwrite(&orig_data, 1, 1, (FILE*)context);
}

void agon_init_decompression(DecompressionData* dd, void* context, WriteDecompressedByte write_fcn) {
    memset(dd, 0, sizeof(DecompressionData));
    dd->context = context;
    dd->write_fcn = write_fcn;
}

void agon_decompress_byte(DecompressionData* dd, uint8_t comp_byte) {
    for (uint8_t bit = 0; bit < 8; bit++) {
        dd->code = (dd->code << 1) | ((comp_byte & 0x80) ? 1 : 0);
        comp_byte <<= 1;
        if (++(dd->code_bits) >= 10) {
            uint16_t command = (dd->code >> 8);
            uint8_t value = (uint8_t)dd->code;
            dd->code = 0;
            dd->code_bits = 0;
            uint8_t size;

            switch (command) {
                case 0: /* Literal: value is a copy of an original byte */
                    dd->window_data[dd->window_write_index++] = value;
                    dd->window_write_index &= (COMPRESSION_WINDOW_SIZE - 1);
                    if (dd->window_size < COMPRESSION_WINDOW_SIZE)
                        (dd->window_size)++;
                    (*dd->write_fcn)(dd->context, value);
                    dd->output_count++;
                    continue;

                case 1: /* Partial string: 4 bytes */
                    size = 4;
                    break;
                case 2: /* Partial string: 8 bytes */
                    size = 8;
                    break;
                case 3: /* Full string: 16 bytes */
                    size = 16;
                    break;
                default:
                    /* Unknown command; could add error handling here */
                    return;
            }

            /* Output the matched string from the window */
            uint32_t wi = value;
            for (uint8_t si = 0; si < size; si++) {
                uint8_t out_byte = dd->window_data[wi++];
                wi &= (COMPRESSION_WINDOW_SIZE - 1);
                (*dd->write_fcn)(dd->context, out_byte);
                dd->output_count++;
            }            
        }
    }
}

/* --- High-level file operations --- */

int tvc_compressFile(const char* srcFile, const char* tgtFile) {
    FILE* fin = fopen(srcFile, "rb");
    if (!fin) {
        fprintf(stderr, "Cannot open input file %s\n", srcFile);
        return -1;
    }
    fseek(fin, 0, SEEK_END);
    long orig_size = ftell(fin);
    fseek(fin, 0, SEEK_SET);

    FILE* fout = fopen(tgtFile, "wb");
    if (!fout) {
        fclose(fin);
        fprintf(stderr, "Cannot open output file %s\n", tgtFile);
        return -2;
    }

    CompressionData cd;
    agon_init_compression(&cd, fout, &my_write_compressed_byte);

    CompressionFileHeader hdr;
    hdr.marker[0] = 'C';
    hdr.marker[1] = 'm';
    hdr.marker[2] = 'p';
    hdr.type = COMPRESSION_TYPE_TURBO;
    hdr.orig_size = (uint32_t) orig_size;
    fwrite(&hdr, sizeof(hdr), 1, fout);
    cd.output_count = sizeof(hdr);

    uint8_t input;
    while (fread(&input, 1, 1, fin) == 1) {
        cd.input_count++;
        agon_compress_byte(&cd, input);
    }
    agon_finish_compression(&cd);
    fclose(fout);
    fclose(fin);

    uint32_t pct = (cd.output_count * 100) / (cd.input_count ? cd.input_count : 1);
    printf("Compressed %u input bytes to %u output bytes (%u%%)\n",
           cd.input_count, cd.output_count, pct);
    return 0;
}

int tvc_decompressFile(const char* srcFile, const char* tgtFile) {
    FILE* fin = fopen(srcFile, "rb");
    if (!fin) {
        fprintf(stderr, "Cannot open input file %s\n", srcFile);
        return -1;
    }
    CompressionFileHeader hdr;
    if (fread(&hdr, sizeof(hdr), 1, fin) != 1 ||
        hdr.marker[0] != 'C' ||
        hdr.marker[1] != 'm' ||
        hdr.marker[2] != 'p' ||
        hdr.type != COMPRESSION_TYPE_TURBO) {
        fclose(fin);
        fprintf(stderr, "Not a Turbo-compressed file: %s\n", srcFile);
        return -4;
    }
    FILE* fout = fopen(tgtFile, "wb");
    if (!fout) {
        fclose(fin);
        fprintf(stderr, "Cannot open output file %s\n", tgtFile);
        return -2;
    }
    DecompressionData dd;
    agon_init_decompression(&dd, fout, &my_write_decompressed_byte);
    dd.input_count = sizeof(hdr);
    uint8_t input;
    while (fread(&input, 1, 1, fin) == 1) {
        dd.input_count++;
        agon_decompress_byte(&dd, input);
    }
    fclose(fout);
    fclose(fin);
    uint32_t pct = (dd.output_count * 100) / (dd.input_count ? dd.input_count : 1);
    printf("Decompressed %u input bytes to %u output bytes (%u%%)\n",
           dd.input_count, dd.output_count, pct);
    if (dd.output_count != hdr.orig_size) {
        printf("Decompressed file size %u does not equal original size %u\n",
               dd.output_count, hdr.orig_size);
        return -5;
    }
    return 0;
}

void usage() {
    fprintf(stderr, "Usage: tvc [-c | -d] <source_file> <target_file>\n");
}

/* --- Main --- */
int main(int argc, char *argv[]) {
    if (argc != 4) {
        usage();
        return 1;
    }
    if (strcmp(argv[1], "-c") == 0) {
        return tvc_compressFile(argv[2], argv[3]);
    } else if (strcmp(argv[1], "-d") == 0) {
        return tvc_decompressFile(argv[2], argv[3]);
    } else {
        usage();
        return 1;
    }
}
