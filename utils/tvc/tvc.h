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

#ifndef TVC_H
#define TVC_H

#include <stdint.h>
#include <stdio.h>
#include <string.h>

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

#define COMPRESSION_WINDOW_SIZE 256     // Must be a power of 2
#define COMPRESSION_STRING_SIZE 16      // Must be a power of 2
#define COMPRESSION_TYPE_TURBO  'T'      // TurboVega-style compression

#pragma pack(push, 1)
typedef struct {
    uint8_t marker[3];
    uint8_t type;
    uint32_t orig_size;
} CompressionFileHeader;
#pragma pack(pop)

typedef void (*WriteCompressedByte)(void* context, uint8_t);
typedef void (*WriteDecompressedByte)(void* context, uint8_t);

typedef struct {
    void*               context;
    WriteCompressedByte write_fcn;
    uint32_t            window_size;
    uint32_t            window_write_index;
    uint32_t            string_size;
    uint32_t            string_read_index;
    uint32_t            string_write_index;
    uint32_t            input_count;
    uint32_t            output_count;
    uint8_t             window_data[COMPRESSION_WINDOW_SIZE];
    uint8_t             string_data[COMPRESSION_STRING_SIZE];
    uint8_t             out_byte;
    uint8_t             out_bits;
} CompressionData;

typedef struct {
    void*               context;
    WriteDecompressedByte write_fcn;
    uint32_t            window_size;
    uint32_t            window_write_index;
    uint32_t            input_count;
    uint32_t            output_count;
    uint8_t             window_data[COMPRESSION_WINDOW_SIZE];
    uint16_t            code;
    uint8_t             code_bits;
} DecompressionData;

#ifdef __cplusplus
extern "C" {
#endif

/* Compression routines */
void my_write_compressed_byte(void* context, uint8_t comp_byte);
void agon_init_compression(CompressionData* cd, void* context, WriteCompressedByte write_fcn);
void agon_write_compressed_bit(CompressionData* cd, uint8_t comp_bit);
void agon_write_compressed_byte(CompressionData* cd, uint8_t comp_byte);
void agon_compress_byte(CompressionData* cd, uint8_t orig_byte);
void agon_finish_compression(CompressionData* cd);

/* Decompression routines */
void my_write_decompressed_byte(void* context, uint8_t orig_data);
void agon_init_decompression(DecompressionData* dd, void* context, WriteDecompressedByte write_fcn);
void agon_decompress_byte(DecompressionData* dd, uint8_t comp_byte);

/* High-level file operations */
int tvc_compressFile(const char* srcFile, const char* tgtFile);
int tvc_decompressFile(const char* srcFile, const char* tgtFile);

/* Main */
void usage();
int main(int argc, char *argv[]);

#ifdef __cplusplus
}
#endif

#endif /* TVC_H */
