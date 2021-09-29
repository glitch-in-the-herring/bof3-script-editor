#include "utils.h"

int main(int argc, char **argv)
{
    if (argc != 3)
    {
        printf("Usage: %s source target\n", argv[0]);
        return 1;
    }

    FILE *source_file = fopen(argv[1], "r");
    FILE *target_file = fopen(argv[2], "r+b");

    if (source_file == NULL)
    {
        printf("Error opening source file!\n");
        return 2;
    }

    if (target_file == NULL)
    {
        printf("Error opening target file!\n");
        return 3;
    }

    byte toc_header[16];
    if (fread(toc_header, 1, sizeof(toc_header), area_file) != sizeof(toc_header))
    {
        printf("Error reading file!\n");
        fclose(area_file);
        return 3;
    }    
}
