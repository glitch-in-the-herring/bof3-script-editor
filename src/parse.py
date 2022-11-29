import collections
import tools

def parse(source_str):
    variables = {
        "PTSIZE" : 512
    }

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
        "+" : 0x8b,
        "\'" : 0x8e,
        ":" : 0x8f,
        "\"" : 0x90,
        "%" : 0x93,
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

    party_tbl = {
        "RYU" : 0x00,
        "NINA" : 0x01,
        "GARR" : 0x02,
        "TEEPO" : 0x03,
        "REI" : 0x04,
        "MOMO" : 0x05,
        "PECO" : 0x06
    }

    effects_table = [
        "SHK_S", "SHK_L", "SHK_P",
        "BIG0_S", "BIG1_S", "BIG2_S",
        "BIG0_L", "BIG1_L", "BIG2_L",
        "BIG0_P", "BIG1_P", "BIG2_P",
        "SML0_S", "SML1_S", "SML2_S",
        "SML0_L", "SML1_L", "SML2_L",
        "SML0_P", "SML1_P", "SML2_P",
        "WAV_L", "WAV_H",
        "JMP0", "JMP1", "JMP2" 
    ]

    close_table = {
        "/COLOR" : (0x06,),
        "/EFFECT" : (0x0e, 0x0f)
    }

    state = 0
    offset = 0
    command = ""
    variable = ""
    value = 0
    command_stack = []
    pointer_tbl = []
    char_tbl = []

    # States
    #
    # lower nibble:
    # 0x00 = not seeking anything actively
    # 0x01 = looking for second "=" in "=="
    # 0x02 = looking for "..]" in "[..]"
    # 0x03 = newline leniency
    # 0x04 = looking for ".." in "$..=...;"
    # 0x08 = looking for "..." in "$..=...;"
    #
    # upper nibble:
    # 0x00 = not looking for end tag
    # 0x01 = looking for end tag

    for i in source_str:
        if state & 0x0f == 0:
            if i == "=":
                state = state & 0xf0 | 1
            elif i == "[":
                state = state & 0xf0 | 2
                command = ""
            elif i == "$":
                state = state & 0xf0 | 4
                variable = ""
                value = ""
            elif i == "#": # pause
                char_tbl.append(0x0b)
                state = state & 0xf0 | 3
                offset += 1
            elif i == "|": # continue to next
                char_tbl.append(0x02)
                state = state & 0xf0 | 3
                offset += 1
            elif i == "\\": # end
                char_tbl.append(0x00)
                state = state & 0xf0 | 3
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
            state = state & 0xf0 | 3
        elif state & 0x0f == 2:
            if i == "]":
                if command == "":
                    state = state & 0xf0 | 3
                    continue
                else:
                    command_tokens = command.split()
                    if command_tokens[0] == "POS":
                        box_byte = 0
                        try:
                            if command_tokens[1] in box_pos_table.keys():
                                box_byte += box_pos_table[command_tokens[1]]
                        except IndexError:
                            state = state & 0xf0 | 3
                            continue
                        try:
                            if command_tokens[2] in box_size_table.keys():
                                box_byte += box_size_table[command_tokens[2]]
                        except IndexError:
                            pass
                        char_tbl.append(0x0c)
                        char_tbl.append(box_byte)
                        offset += 2
                        state = state & 0xf0 | 3
                    elif command_tokens[0] == "TIME":
                        time_byte = 0
                        try:
                            time_byte = int(command_tokens[1], base=16)
                        except ValueError:
                            pass
                        char_tbl.append(0x16)
                        char_tbl.append(time_byte)
                    elif command_tokens[0] == "COLOR":
                        color_byte = 0
                        try:
                            color_byte += color_table[command_tokens[1]]
                        except IndexError:
                            state = state & 0xf0 | 3
                            continue
                        char_tbl.append(0x05)
                        char_tbl.append(color_byte)
                        offset += 2
                        state = 0x13
                        command_stack.append("/COLOR")
                    elif command_tokens[0] == "/COLOR" and state & 0xf0 == 0x10:
                        if command_tokens[0] == command_stack[-1]:
                            char_tbl.extend(close_table[command_stack[-1]])
                            offset += len(close_table[command_stack.pop()])
                        if len(command_stack) == 0:
                            state = 0x03
                            continue
                        state = state & 0xf0 | 3
                    elif command_tokens[0] == "EFFECT":
                        char_tbl.append(0x0d)
                        offset += 1
                        state = 0x13
                        command_stack.append("/EFFECT")
                    elif command_tokens[0] == "/EFFECT" and state & 0xf0 == 0x10:
                        if command_tokens[0] == command_stack[-1]:
                            try:
                                char_tbl.extend((0x0e, 0x0f))
                                char_tbl.append(effects_table.index(command_tokens[1]))
                                offset += 3
                                command_stack.pop()
                            except IndexError:
                                state = state & 0xf0 | 3
                                continue
                        if len(command_stack) == 0:
                            state = 0x03
                            continue
                    elif command_tokens[0] == "PARTY":
                        party_byte = 0
                        char_tbl.append(0x04)
                        try:
                            if command_tokens[1] in party_tbl.keys():
                                party_byte += box_pos_table[command_tokens[1]]
                        except IndexError:
                            state = state & 0xf0 | 3
                            continue
                        char_tbl.append(0x04)
                        char.tbl.append(party_byte)
                        offset += 2
                        state = state & 0xf0 | 3
            else:
                command = "".join((command, i))
        elif state & 0x0f == 4:
            if i == "=":
                state = state & 0xf0 | 8
            else:
                if i == "\n":
                    state = state & 0xf0 | 3
                    continue
                elif i == " ":
                    continue
                variable = "".join((variable, i))
        elif state & 0x0f == 8:
            if i == ";":
                try:
                    value = int(value)
                except ValueError:
                    pass
                variables[variable] = value
                state = state & 0xf0 | 3
            else:
                if i == "\n" or i == " ":
                    continue
                value = "".join((value, i))
        elif state & 0x0f == 3:
            if i == "\n":
                state = state & 0xf0 | 0
            elif i == " ":
                continue
            elif i == "=":
                state = state & 0xf0 | 1
            elif i == "[":
                state = state & 0xf0 | 2
                command = ""
            elif i == "|":
                char_tbl.append(0x02)
                offset += 1
            elif i == "\\":
                char_tbl.append(0x00)
                offset += 1
            else:
                if i in conv_table.keys():
                    char_tbl.append(conv_table[i])
                else:
                    char_tbl.append(ord(i))
                offset += 1
            state = state & 0xf0 | 0

    variables["OFFSET"] = offset
    return (pointer_tbl, char_tbl, variables)
    
def process_tbl(parsed):
    ptsize = parsed[2]["PTSIZE"]
    offset = parsed[2]["OFFSET"]
    offset_little = tools.to_little(offset + ptsize, 2)
    tbl = []
    if ptsize & 1 != 0:
        raise ValueError
    tbl.extend(tools.to_little(ptsize, 2))
    j = 0
    for i in parsed[0]:
        j += 1
        tbl.extend(tools.to_little(i + ptsize, 2))

    for i in range((ptsize - j*2 - 2)//2):
        tbl.append(offset_little)

    tbl.extend(parsed[1])
    padding = offset // 2048
    return tbl