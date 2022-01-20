#include "extractor.h"

word convert_little_endian(byte a[], int n, int bytes)
{
    word result = 0;
    for (int i = bytes - 1; i >= 0; i--)
    {
        result = a[n + i] << 8 * i | result;
    }
    return result;
}

word find_dialogue_section(FILE *f, word count, word *section_size)
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
            *section_size = convert_little_endian(toc_entry, 0, 4);
            return address;
        }

        tmp = convert_little_endian(toc_entry, 0, 4);
        if (tmp % 0x0800 != 0)
        {
            tmp = 0x0800 * ((tmp + 0x0800) / 0x0800);
        }
    } 
    while (count--);
    return 0;
}

bool is_math_tbl(byte toc_header[])
{
    byte magic[8] = {0x4d, 0x41, 0x54, 0x48, 0x5f, 0x54, 0x42, 0x4c};
    for (int i = 8; i < 16; i++)
    {
        if (toc_header[i] != magic[i - 8])
        {
            return false;
        }
    }
    return true;
}

bool is_dialogue_section(byte toc_entry[])
{
    return toc_entry[6] == 0x01 && toc_entry[7] == 0x80;
}

bool is_alphanum(byte a)
{
    return (a >= 65 && a <= 90) || (a >= 97 && a <= 122) || (a >= 48 && a <= 57);
}

char is_punct(byte a)
{
    switch (a)
    {
        case 0x5d:
            return '!';
            break;
        case 0x90:
            return '"';
            break;
        case 0x8e:
            return '\'';
            break;
        case 0x3c:
            return ',';
            break;
        case 0x3d:
            return '-';
            break;
        case 0x3e:
            return '.';
            break;
        case 0x5c:
            return '?';
            break;
        case 0x8f:
            return ':';
            break;
        case 0x91:
            return ';';
            break;
        default:
            return 0x00;
            break;
    }
}

char *is_position(byte a)
{
    static char buffer[20];
    byte position = a & 0x0f;
    byte style = (a & 0xf0) >> 4;

    switch (position)
    {
        case 0x00:
            strcpy(buffer, "[POS BM");
            break;
        case 0x01:
            strcpy(buffer, "[POS MM");
            break;
        case 0x02:
            strcpy(buffer, "[POS TM");
            break;
        case 0x03:
            strcpy(buffer, "[POS TL");
            break;
        case 0x04:
            strcpy(buffer, "[POS TR");
            break;
        case 0x05:
            strcpy(buffer, "[POS BL");
            break;
        case 0x06:
            strcpy(buffer, "[POS BR");
            break;
    }

    switch (style)
    {
        case 0x00:
            strcat(buffer, " NV] ");
            break;
        case 0x04:
            strcat(buffer, " SV] ");
            break;
        case 0x08:
            strcat(buffer, " NI] ");
            break;
    }

    return buffer;
}

char *is_symbol(byte a)
{
    switch (a)
    {
        case 0x7b:
            return "↑";
            break;
        case 0x7c:
            return "↓";
            break; 
        case 0x7d:
            return "←";
            break;
        case 0x7e:
            return "→";
            break;
        case 0x7f:
            return "〜";
            break;
        case 0x80:
            return "◯";
            break;
        case 0x81:
            return "△";
            break;
        case 0x82:
            return "×";
            break;
        case 0x83:
            return "□";
            break;
        case 0x86:
            return "↖";
            break;
        case 0x87:
            return "↘";
            break; 
        case 0x88:
            return "↗";
            break;
        case 0x89:
            return "↙";
            break;
        case 0x93:
            return "%";
            break;
        case 0x8a:
            return "©";
            break;
        case 0x8d:
            return "&";
            break;
        default:
            return "";
            break;
    }
}

char *is_color(byte a)
{
    switch (a)
    {
        case 0x01:
            return "PURPLE";
            break;
        case 0x02:
            return "RED";
            break;
        case 0x03:
            return "CYAN";
            break;
        case 0x04:
            return "YELLOW";
            break;
        case 0x05:
            return "PINK";
            break;
        case 0x06:
            return "GREEN";
            break;
        case 0x07:
            return "BLACK";
            break;
        default:
            return "";
            break;
    }    
}

char *is_effect(byte a)
{
    switch (a)
    {
        case 0x00:
            return "SHK_S";
            break;
        case 0x01:
            return "SHK_L";
            break;
        case 0x02:
            return "SHK_P";
            break;
        case 0x03:
            return "BIG0_S";
            break;
        case 0x04:
            return "BIG1_S";
            break;
        case 0x05:
            return "BIG2_S";
            break;
        case 0x06:
            return "BIG0_L";
            break;
        case 0x07:
            return "BIG1_L";
            break;
        case 0x08:
            return "BIG2_L";
            break;
        case 0x09:
            return "BIG0_P";
            break;
        case 0x0a:
            return "BIG1_P";
            break;
        case 0x0b:
            return "BIG2_P";
            break;
        case 0x0c:
            return "SML0_S";
            break;
        case 0x0d:
            return "SML1_S";
            break;
        case 0x0e:
            return "SML2_S";
            break;
        case 0x0f:
            return "SML0_L";
            break;
        case 0x10:
            return "SML1_L";
            break;
        case 0x11:
            return "SML2_L";
            break;
        case 0x12:
            return "SML0_P";
            break;
        case 0x13:
            return "SML1_P";
            break;
        case 0x14:
            return "SML2_P";
            break;
        case 0x15:
            return "WAV_L";
            break;
        case 0x16:
            return "WAV_H";
            break;
        case 0x17:
            return "JMP0";
            break;
        case 0x18:
            return "JMP1";
            break;
        case 0x19:
            return "JMP2";
            break;
        default:
            return "";
            break;
    }    
}
