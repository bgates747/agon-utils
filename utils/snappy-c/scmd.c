/* Simple command line tool for snappy */
#include <fcntl.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>
#include <stdio.h>
#include "snappy.h"
#include "map.h"
#include "util.h"

extern int optind;  /* Explicit declaration for systems that need it */

enum { undef, compress, uncompress } mode = undef;

void usage(void)
{
    fprintf(stderr, 
        "scmd [-c|-d] [-s] file [outfile]\n"
        "-c compress\n"
        "-d uncompress\n"
        "-s print to standard output\n"
        "Compress or uncompress file with snappy.\n"
        "When no output file is specified write to file.snp\n");
    exit(1);
}

int match_suffix(char *p, char *suf)
{
    int suflen = strlen(suf);
    int plen = strlen(p);
    if (plen < suflen)
        return 0;
    char *s = p + plen - suflen;
    return !strcmp(s, suf);
}

/* Updated open_output with extra parameter to indicate if the returned file name
   was dynamically allocated (needs to be freed later) */
int open_output(char *name, char *oname, char **ofn, int *needs_free)
{
    int fd;
    char *file;

    if (oname) {
        file = oname;
        *needs_free = 0;  // Not dynamically allocated
    } else {
        int len = strlen(name);
        file = xmalloc(len + 6);
        *needs_free = 1;  // Dynamically allocated

        if (mode == compress)
            snprintf(file, len + 6, "%s.snp", name);
        else if (match_suffix(name, ".snp")) {
            strcpy(file, name);
            file[len - 4] = 0;            
        } else {
            fprintf(stderr, "Please specify output name\n");
            exit(1);
        }
    }

    *ofn = file;        
    fd = open(file, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (fd < 0) { 
        fprintf(stderr, "Cannot create %s: %s\n", file, strerror(errno));
        exit(1);
    }        
    return fd;
}

int main(int ac, char **av)
{
    int opt;
    int to_stdout = 0;

    while ((opt = getopt(ac, av, "dcs")) != -1) {
        switch (opt) { 
        case 'd':
            mode = uncompress;
            break;
        case 'c':
            mode = compress;
            break;
        case 's':
            to_stdout = 1;
            break;
        default:
            usage();
        }
    }

    char *map;
    size_t size;
    if (!av[optind])
        usage();

    if (mode == undef) {
        if (match_suffix(av[optind], ".snp"))
            mode = uncompress;
        else
            mode = compress;
    }

    map = mapfile(av[optind], O_RDONLY, &size);
    if (!map) { 
        fprintf(stderr, "Cannot open %s: %s\n", av[1], strerror(errno));
        exit(1);
    }
        
    int err;
    char *out;    
    size_t outlen;
    if (mode == uncompress) {
        err = snappy_uncompressed_length(map, size, &outlen);
    } else {    
        outlen = snappy_max_compressed_length(size);
    }
    
    out = xmalloc(outlen);

    struct snappy_env env;
    if (mode == compress) {
        snappy_init_env(&env);
        err = snappy_compress(&env, map, size, out, &outlen);
    } else
        err = snappy_uncompress(map, size, out);

    if (mode == compress) {
        snappy_free_env(&env);
    }
    unmap_file(map, size);

    if (err) {
        fprintf(stderr, "Cannot process %s: %s\n", av[optind], 
            strerror(-err));
        exit(1);
    }

    char *file;
    int fd;
    int needs_free = 0;  // Declare needs_free here so it's visible later
    if (to_stdout) {
        if (av[optind + 1])
            usage();
        fd = 1;
        file = "<stdout>";
    } else {
        if (av[optind + 1] && av[optind + 2])
            usage();
        fd = open_output(av[optind], av[optind + 1], &file, &needs_free);    
    }

    err = 0;
    if (write(fd, out, outlen) != outlen) {
        fprintf(stderr, "Cannot write to %s: %s\n", 
            file,
            strerror(errno));
        err = 1;
    }

    if (!to_stdout && needs_free)
        free(file);

    free(out);
    
    return err;
}
