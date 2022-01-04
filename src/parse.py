def parse(source_str):
    conv_table = {
        "\n" : 0x01,
        "(" : 0x3a,
        ")" : 0x3b,
        "," : 0x3c,
        "-" : 0x3d,
        "." : 0x3e,
        "/" : 0x3f,
        "?" : 0x5c,
        "!" : 0x5d,
        "\'" : 0x8e,
        ":" : 0x8f,
        "\"" : 0x90,
        " " : 0xff
    }

    box_pos_table = {
        "BM" : 0x00,
        "MM" : 0x01,
        "TM" : 0x02,
        "TL" : 0x03,
        "TR" : 0x04,
        "BL" : 0x05,
        "BR" : 0x06
    }

    box_size_table = {
        "NV" : 0x00,
        "SV" : 0x40,
        "NI" : 0x80
    }

    state = 0
    offset = 0
    length = 0
    command = ""
    pointer_tbl = []
    char_tbl = []

    for i in source_str:
        if state == 0:
            if i == "=":
                state = 1
                continue
            elif i == "[":
                state = 2
                continue
            elif i == "|":
                char_tbl.append(0x02)
                length += 1
                offset += 1
            elif i == "\\":
                char_tbl.append(0x00)
                length += 1
                offset += 1
            else:
                if i in conv_table.keys():
                    char_tbl.append(conv_table[i])
                else:
                    char_tbl.append(ord(i))
                length += 1
                offset += 1
        elif state == 1:
            if i == "=":
                pointer_tbl.append(offset)
            state = 3
        elif state == 2:
            if i == "]":
                if command == "":
                    state = 3
                    continue
                else:
                    command = command.split()
                    if command[0] == "POS":
                        box_byte = 0
                        try:
                            if command[1] in box_pos_table.keys():
                                box_byte += box_pos_table[command[1]]
                        except IndexError:
                            state = 3                            
                            continue
                        try:
                            if command[2] in box_size_table.keys():
                                box_byte += box_size_table[command[2]]
                        except IndexError:
                            pass
                        char_tbl.append(0x0c)
                        char_tbl.append(box_byte)
                        offset += 2
                    command = ""
                state = 3
            else:
                command = "".join([command, i])
        elif state == 3:
            if i == "\n":
                state = 0
                continue
            elif i == "=":
                state = 1
                continue
            elif i == "[":              
                state = 2
                continue
            elif i == "|":
                char_tbl.append(0x02)
                length += 1
                offset += 1
            elif i == "\\":
                char_tbl.append(0x00)
                length += 1
                offset += 1                
            else:
                if i in conv_table.keys():
                    char_tbl.append(conv_table[i])
                else:
                    char_tbl.append(ord(i))
                length += 1
                offset += 1
            state = 0

    return (pointer_tbl, char_tbl)