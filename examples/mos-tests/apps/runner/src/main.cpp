#include <stdio.h>
#include <string.h>
#include "catalogue_generated.h"
// Same selection code is built natively for the host planner and by AgonDev.
int main(int argc, char** argv) {
    if(argc==2 && strcmp(argv[1],"--list")==0) {
        for(size_t i=0;i<CASE_COUNT;++i) printf("%lu %s %s\n",(unsigned long)CASES[i].key,CASES[i].id,CASES[i].function);
        return 0;
    }
    if(argc<3 || strcmp(argv[1],"--resolve")!=0) {
        printf("Runner foundation: --list or --resolve all|function:NAME|group:NAME|case:ID ...\nExecution/capture is not enabled yet.\n"); return 3;
    }
    bool selected[CASE_COUNT]={};
    for(int a=2;a<argc;++a) {
        bool found=false;
        for(size_t i=0;i<CASE_COUNT;++i) {
            const char* s=argv[a];
            bool match=strcmp(s,"all")==0 ||
                (strncmp(s,"function:",9)==0 && strcmp(s+9,CASES[i].function)==0) ||
                (strncmp(s,"group:",6)==0 && strcmp(s+6,CASES[i].group)==0) ||
                (strncmp(s,"case:",5)==0 && strcmp(s+5,CASES[i].id)==0);
            if(match) { selected[i]=true; found=true; }
        }
        if(!found) { fprintf(stderr,"Unknown selector: %s\n",argv[a]); return 3; }
    }
    for(size_t i=0;i<CASE_COUNT;++i) if(selected[i]) printf("%lu\n",(unsigned long)CASES[i].key);
    return 0;
}
