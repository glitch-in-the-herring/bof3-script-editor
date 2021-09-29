#include "utils.h"

word convert_little_endian(byte a[], int n, int k)
{
    word result = 0;
    for (int i = n; i >= k; i--)
    {
        result = a[i] << 8 * i | result;
    }
    return result;
}

int is_emi_file(byte toc_header[])
{
    byte magic[8] = {0x4d, 0x41, 0x54, 0x48, 0x5f, 0x54, 0x42, 0x4c};
    for (int i = 8; i < 16; i++)
    {
        if (toc_header[i] != magic[i - 8])
        {
            return 0;
        }
    }
    return 1;
}

int find_text_section(FILE *target_file, word *section_size)
{
    byte toc_entry[16];
    word tmp = 0;
    word address = 0x0800;

    do
    {
        address += tmp;
        if (fread(toc_entry, 1, sizeof(toc_entry), f) != sizeof(toc_entry))
        {
            return -1;
        }

        if (is_dialogue_section(toc_entry))
        {
            *section_size = convert_little_endian(toc_entry, 3, 0);
            return address;
        }

        tmp = convert_little_endian(toc_entry, 3, 0);
        if (tmp % 0x0800 != 0)
        {
            tmp = 0x0800 * ((tmp + 0x0800) / 0x0800);
        }
    } 
    while (count--);
    return 0;
}