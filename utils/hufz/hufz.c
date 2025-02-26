#include "hufz.h"

// --- Helper: Write Agon-style header ---
static void write_global_header(uint8_t *header, uint32_t orig_size) {
    header[0] = 'C';
    header[1] = 'm';
    header[2] = 'p';
    header[3] = COMPRESSION_TYPE_HUFZ;

    // Original file size (little-endian)
    header[4] = orig_size & 0xFF;
    header[5] = (orig_size >> 8) & 0xFF;
    header[6] = (orig_size >> 16) & 0xFF;
    header[7] = (orig_size >> 24) & 0xFF;

    // HUFZ magic bytes and version numbers
    header[8] = 'H';
    header[9] = 'U';
    header[10] = 'F';
    header[11] = 'Z';
    header[12] = HUFZ_MAJOR_VERSION;
    header[13] = HUFZ_MINOR_VERSION;
}

// --- Command-line Interface ---
int main(int argc, char *argv[]) {
    if (argc != 4) {
        debug_log("Usage: %s -c|-d input output\n", argv[0]);
        return 1;
    }
    if (strcmp(argv[1], "-c") == 0) {
        compress_file(argv[2], argv[3]);
    } else if (strcmp(argv[1], "-d") == 0) {
        decompress_file(argv[2], argv[3]);
    } else {
        debug_log("Invalid option. Use -c for compression, -d for decompression.\n");
        return 1;
    }
    return 0;
}

// --- Huffman Compression ---
void compress_file(const char *input, const char *output) {
    FILE *in = fopen(input, "rb");
    FILE *out = fopen(output, "wb");
    if (!in || !out) {
        perror("File open error");
        return;
    }

    fseek(in, 0, SEEK_END);
    uint32_t orig_size = ftell(in);
    rewind(in);

    uint32_t freq[MAX_SYMBOLS] = {0};
    uint8_t byte;
    while (fread(&byte, 1, 1, in) == 1) {
        freq[byte]++;
    }
    rewind(in);

    Node *tree = NULL;
    build_huffman_tree(freq, &tree);

    HuffmanTable table = {0};
    uint8_t code[MAX_SYMBOLS] = {0};
    generate_huffman_codes(tree, &table, code, 0);

    uint8_t header[HEADER_SIZE];
    write_global_header(header, orig_size);
    fwrite(header, 1, HEADER_SIZE, out);

    BitStream stream = { out, 0, 0 };

    write_huffman_tree(tree, &stream);

    while (fread(&byte, 1, 1, in) == 1) {
        bitstream_write(&stream, table.code[byte], table.length[byte]);
    }

    bitstream_flush(&stream);
    free_huffman_tree(tree);
    fclose(in);
    fclose(out);
}

void decompress_file(const char *input, const char *output) {
    FILE *in = fopen(input, "rb");
    FILE *out = fopen(output, "wb");
    if (!in || !out) {
        perror("File open error");
        return;
    }

    uint8_t header[HEADER_SIZE];
    if (fread(header, 1, HEADER_SIZE, in) != HEADER_SIZE) {
        debug_log("[ERROR] Failed to read header\n");
        fclose(in);
        fclose(out);
        return;
    }

    // Verify header
    if (memcmp(header, "Cmp", 3) != 0 || header[3] != COMPRESSION_TYPE_HUFZ ||
        memcmp(header + 8, "HUFZ", 4) != 0) {
        debug_log("[ERROR] Invalid file format\n");
        fclose(in);
        fclose(out);
        return;
    }

    uint32_t orig_size = header[4] | (header[5] << 8) | (header[6] << 16) | (header[7] << 24);
    debug_log("[INFO] Decompressing file: expected size = %u bytes\n", orig_size);

    BitStream stream = { in, 0, 0 };

    Node *tree = read_huffman_tree(&stream);
    if (!tree) {
        debug_log("[ERROR] Failed to reconstruct Huffman tree\n");
        fclose(in);
        fclose(out);
        return;
    }

    debug_log("[INFO] Huffman tree reconstructed successfully\n");

    // Decode the bitstream
    Node *current = tree;
    uint32_t bytes_written = 0;

    while (bytes_written < orig_size) {
        int bit = bitstream_read(&stream, 1);
        if (bit == EOF) {
            debug_log("[ERROR] Unexpected end of bitstream at byte %u\n", bytes_written);
            break;
        }

        current = bit ? current->right : current->left;

        // If we reach a leaf node, we have a complete symbol
        if (!current->left && !current->right) {
            uint8_t symbol = current->symbol;
            fwrite(&symbol, 1, 1, out);
            bytes_written++;

            // debug_log("[DEBUG] Byte %u: 0x%02X ('%c')\n", bytes_written, symbol, (symbol >= 32 && symbol < 127) ? symbol : '?');

            current = tree;  // Reset to root for the next symbol
        }
    }

    debug_log("[INFO] Decompression complete: %u bytes written (expected %u)\n", bytes_written, orig_size);

    if (bytes_written != orig_size) {
        debug_log("[WARNING] Decompressed size mismatch! Expected: %u, Got: %u\n", orig_size, bytes_written);
    }

    free_huffman_tree(tree);
    fclose(in);
    fclose(out);
}

// --- Huffman Tree Encoding ---
void write_huffman_tree(Node *node, BitStream *stream) {
    if (!node) return;
    
    if (!node->left && !node->right) {  // Leaf node
        bitstream_write(stream, 1, 1);
        bitstream_write(stream, node->symbol, 8);
        debug_log("[DEBUG] Writing leaf: '%c' (0x%02X)\n", 
                  (node->symbol >= 32 && node->symbol < 127) ? node->symbol : '?', node->symbol);
        return;
    }

    bitstream_write(stream, 0, 1);  // Internal node
    debug_log("[DEBUG] Writing internal node\n");

    write_huffman_tree(node->left, stream);
    write_huffman_tree(node->right, stream);
}

Node *read_huffman_tree(BitStream *stream) {
    int flag = bitstream_read(stream, 1);
    if (flag == EOF) {
        debug_log("[ERROR] Unexpected EOF while reading Huffman tree!\n");
        return NULL;
    }

    if (flag == 1) {  // Leaf node
        uint8_t symbol = (uint8_t)bitstream_read(stream, 8);
        debug_log("[DEBUG] Read leaf: '%c' (0x%02X)\n", 
                  (symbol >= 32 && symbol < 127) ? symbol : '?', symbol);

        Node *leaf = (Node *)malloc(sizeof(Node));
        leaf->symbol = symbol;
        leaf->freq = 0;
        leaf->left = NULL;
        leaf->right = NULL;
        return leaf;
    } else {  // Internal node
        debug_log("[DEBUG] Read internal node\n");

        Node *node = (Node *)malloc(sizeof(Node));
        node->freq = 0;
        node->left = read_huffman_tree(stream);
        node->right = read_huffman_tree(stream);
        return node;
    }
}

// --- Huffman Tree Generation ---
void build_huffman_tree(uint32_t *freq, Node **tree) {
    Node *nodes[MAX_SYMBOLS] = {0};
    int count = 0;

    for (int i = 0; i < MAX_SYMBOLS; i++) {
        if (freq[i] > 0) {
            nodes[count] = (Node *)malloc(sizeof(Node));
            nodes[count]->symbol = (uint8_t)i;
            nodes[count]->freq = freq[i];
            nodes[count]->left = nodes[count]->right = NULL;
            count++;
        }
    }

    while (count > 1) {
        int min1 = 0, min2 = 1;
        if (nodes[min1]->freq > nodes[min2]->freq) {
            min1 = 1; min2 = 0;
        }
        for (int i = 2; i < count; i++) {
            if (nodes[i]->freq < nodes[min1]->freq) {
                min2 = min1;
                min1 = i;
            } else if (nodes[i]->freq < nodes[min2]->freq) {
                min2 = i;
            }
        }

        Node *new_node = (Node *)malloc(sizeof(Node));
        new_node->freq = nodes[min1]->freq + nodes[min2]->freq;
        new_node->left = nodes[min1];
        new_node->right = nodes[min2];

        nodes[min1] = new_node;
        nodes[min2] = nodes[count - 1];
        count--;
    }

    *tree = nodes[0];
}

void free_huffman_tree(Node *node) {
    if (!node) return;
    free_huffman_tree(node->left);
    free_huffman_tree(node->right);
    free(node);
}

void generate_huffman_codes(Node *root, HuffmanTable *table, uint8_t *code, int depth) {
    if (!root) return;
    if (!root->left && !root->right) {
        table->code[root->symbol] = *code;
        table->length[root->symbol] = depth;
        return;
    }
    *code <<= 1;
    generate_huffman_codes(root->left, table, code, depth + 1);
    *code |= 1;
    generate_huffman_codes(root->right, table, code, depth + 1);
    *code >>= 1;
}

// --- Bitstream handling ---
void bitstream_write(BitStream *stream, uint32_t data, int bits) {
    while (bits--) {
        stream->buffer <<= 1;
        if (data & (1 << bits)) stream->buffer |= 1;
        stream->bit_count++;
        if (stream->bit_count == 8) {
            fwrite(&stream->buffer, 1, 1, stream->file);
            stream->bit_count = 0;
        }
    }
}

uint32_t bitstream_read(BitStream *stream, int bits) {
    uint32_t result = 0;
    while (bits--) {
        if (stream->bit_count == 0) {
            if (fread(&stream->buffer, 1, 1, stream->file) != 1) return EOF;
            stream->bit_count = 8;
        }
        result <<= 1;
        if (stream->buffer & 0x80) result |= 1;
        stream->buffer <<= 1;
        stream->bit_count--;
    }
    return result;
}

void bitstream_flush(BitStream *stream) {
    if (stream->bit_count > 0) {
        stream->buffer <<= (8 - stream->bit_count);
        fwrite(&stream->buffer, 1, 1, stream->file);
    }
}

