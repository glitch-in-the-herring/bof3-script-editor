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

    color_table = {
        "PURPLE" : 0x01,
        "RED" : 0x02,
        "CYAN" : 0x03,
        "YELLOW" : 0x04,
        "PINK" : 0x05,
        "GREEN" : 0x06,
        "BLACK" : 0x07
    }

    close_table = {
        "/COLOR" : (0x06,),
        "/EFFECT" : (0x0e, 0x0f)
    }

    state = 0
    offset = 0
    command = ""
    command_stack = []
    pointer_tbl = []
    char_tbl = []

    # States
    #
    # lower nibble:
    # 0x00 = not seeking anything actively
    # 0x01 = looking for second "=" in "=="
    # 0x02 = looking for "..]" in "[..]"
    # 0x04 = newline leniency
    #
    # upper nibble:
    # 0x00 = not looking for end tag
    # 0x01 = looking for end tag

    for i in source_str:
        if state & 0x0f == 0:
            if i == "=":
                state = state & 0xf0 | 1
                continue
            elif i == "[":
                state = state & 0xf0 | 2
                command = ""
                continue
            elif i == "|":
                char_tbl.append(0x02)
                state = state & 0xf0 | 4
                offset += 1
            elif i == "\\":
                char_tbl.append(0x00)
                state = state & 0xf0 | 4
                offset += 1
            else:
                if i in conv_table.keys():
                    char_tbl.append(conv_table[i])
                else:
                    char_tbl.append(ord(i))
                offset += 1
        elif state & 0x0f == 1:
            if i == "=":
                pointer_tbl.append(offset)
            state = state & 0xf0 | 4
        elif state & 0x0f == 2:
            if i == "]":
                if command == "":
                    state = state & 0xf0 | 4
                    continue
                else:
                    command_tokens = command.split()
                    if command_tokens[0] == "POS":
                        box_byte = 0
                        try:
                            if command_tokens[1] in box_pos_table.keys():
                                box_byte += box_pos_table[command_tokens[1]]
                        except IndexError:
                            state = state & 0xf0 | 4
                            continue
                        try:
                            if command_tokens[2] in box_size_table.keys():
                                box_byte += box_size_table[command_tokens[2]]
                        except IndexError:
                            pass
                        char_tbl.append(0x0c)
                        char_tbl.append(box_byte)
                        offset += 2
                        state = state & 0xf0 | 4
                    elif command_tokens[0] == "COLOR":
                        color_byte = 0
                        try:
                            if command_tokens[1] in color_table.keys():
                                color_byte += color_table[command_tokens[1]]
                        except IndexError:
                            state = state & 0xf0 | 4
                            continue
                        char_tbl.append(0x05)
                        char_tbl.append(color_byte)
                        offset += 2
                        state = 0x14
                        command_stack.append("/COLOR")
                    elif command_tokens[0] == "/COLOR" and state & 0xf0 == 0x10:
                        if command_tokens[0] == command_stack[-1]:
                            char_tbl.extend(close_table[command_stack[-1]])
                            offset += len(close_table[command_stack.pop()])
                        if len(command_stack) == 0:
                            state = 0x04
                            continue
                        state = state & 0xf0 | 4
            else:
                command = "".join([command, i])
        elif state & 0x0f == 4:
            if i == "\n":
                state = state & 0xf0 | 0
                continue
            elif i == " ":
                continue
            elif i == "=":
                state = state & 0xf0 | 1
                continue
            elif i == "[":
                state = state & 0xf0 | 2
                command = ""
                continue
            elif i == "|":
                char_tbl.append(0x02)
                offset += 1
                continue
            elif i == "\\":
                char_tbl.append(0x00)
                offset += 1
                continue
            else:
                if i in conv_table.keys():
                    char_tbl.append(conv_table[i])
                else:
                    char_tbl.append(ord(i))
                offset += 1
            state = state & 0xf0 | 0

    return (pointer_tbl, char_tbl)
