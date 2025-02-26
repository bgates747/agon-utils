#ifndef HUFZ_H
#define HUFZ_H

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>

#define COMPRESSION_TYPE_HUFZ 'h'  // Huffman compression type
#define HUFZ_MAJOR_VERSION 1
#define HUFZ_MINOR_VERSION 0
#define HEADER_SIZE 14
#define MAX_SYMBOLS 256  // Huffman supports up to 256 symbols

#define DEBUG 1  // Set to 1 to enable debug logging

#if DEBUG
    #define debug_log(...) fprintf(stderr, __VA_ARGS__)
#else
    #define debug_log(...) // No-op when DEBUG is 0
#endif

// Huffman tree node structure
typedef struct Node {
    uint8_t symbol;
    uint32_t freq;
    struct Node *left, *right;
} Node;

// Bitstream writer/reader
typedef struct {
    FILE *file;
    uint8_t buffer;
    int bit_count;
} BitStream;

// Huffman code table
typedef struct {
    uint8_t code[MAX_SYMBOLS];
    uint8_t length[MAX_SYMBOLS];
} HuffmanTable;

// Function prototypes
void compress_file(const char *input, const char *output);
void decompress_file(const char *input, const char *output);
void build_huffman_tree(uint32_t *freq, Node **tree);
void free_huffman_tree(Node *node);

void bitstream_write(BitStream *stream, uint32_t data, int bits);
uint32_t bitstream_read(BitStream *stream, int bits);
void bitstream_flush(BitStream *stream);
Node *read_huffman_tree(BitStream *stream);
void write_huffman_tree(Node *node, BitStream *stream);
void generate_huffman_codes(Node *root, HuffmanTable *table, uint8_t *code, int depth);

static void write_global_header(uint8_t *header, uint32_t orig_size);

#endif // HUFZ_H
