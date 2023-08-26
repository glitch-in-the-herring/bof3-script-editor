import tools

def parse(source_str):
    variables = {
        "PTSIZE" : 512,
        "REGION" : 0
    }

    conv_table = {
        "\n" : b"\x01",
        "(" : b"\x3a",
        ")" : b"\x3b",
        "," : b"\x3c",
        "-" : b"\x3d",
        "." : b"\x3e",
        "/" : b"\x3f",
        "?" : b"\x5c",
        "!" : b"\x5d",
        "+" : b"\x8b",
        "\'" : b"\x8e",
        ":" : b"\x8f",
        "\"" : b"\x90",
        "%" : b"\x93",
        " " : b"\xff"
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
        "PURPLE" : b"\x01",
        "RED" : b"\x02",
        "CYAN" : b"\x03",
        "YELLOW" : b"\x04",
        "PINK" : b"\x05",
        "GREEN" : b"\x06",
        "BLACK" : b"\x07"
    }

    party_tbl = {
        "RYU" : b"\x00",
        "NINA" : b"\x01",
        "GARR" : b"\x02",
        "TEEPO" : b"\x03",
        "REI" : b"\x04",
        "MOMO" : b"\x05",
        "PECO" : b"\x06"
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

    opt_table = {
        "ABOVE" : 0x00,
        "NEW" : 0x10
    }

    close_table = {
        "/COLOR" : b"\x06",
        "/EFFECT" : b"\x0e\x0f"
    }

    state = 0
    offset = 0
    command = ""
    variable = ""
    value = 0
    opt_count = 0
    command_stack = []
    pointer_tbl = []
    text_bytes = b""

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
                text_bytes += b"\x0b"
                state = state & 0xf0 | 3
                offset += 1
            elif i == "|": # continue to next
                text_bytes += b"\x02"
                state = state & 0xf0 | 3
                offset += 1
            elif i == "\\": # end
                text_bytes += b"\x00"
                state = state & 0xf0 | 3
                offset += 1
            else:
                if i in conv_table.keys():
                    text_bytes += conv_table[i]
                else:
                    text_bytes += str.encode(i)
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
                        box_byte_int = 0
                        try:
                            box_byte_int += box_pos_table[command_tokens[1]]
                        except (KeyError, IndexError):
                            state = state & 0xf0 | 3
                            continue
                        try:
                            box_byte_int += box_size_table[command_tokens[2]]
                        except (KeyError, IndexError):
                            state = state & 0xf0 | 3
                            continue
                        box_byte = int.to_bytes(box_byte_int, length=1, byteorder="little")
                        text_bytes += b"\x0c"
                        text_bytes += box_byte
                        state = state & 0xf0 | 3
                        offset += 2
                    elif command_tokens[0] == "COLOR":
                        color_byte = b""
                        try:
                            color_byte += color_table[command_tokens[1]]
                        except (KeyError, IndexError):
                            state = state & 0xf0 | 3
                            continue
                        text_bytes += b"\x05"
                        text_bytes += color_byte
                        command_stack.append("/COLOR")
                        state = 0x13
                        offset += 2
                    elif command_tokens[0] == "/COLOR" and state & 0xf0 == 0x10:
                        if command_tokens[0] == command_stack[-1]:
                            text_bytes += close_table[command_stack[-1]]
                            offset += len(close_table[command_stack.pop()])
                        if len(command_stack) == 0:
                            state = 0x03
                            continue
                        state = state & 0xf0 | 3
                    elif command_tokens[0] == "EFFECT":
                        text_bytes += b"\x0d"
                        command_stack.append("/EFFECT")
                        state = 0x13
                        offset += 1
                    elif command_tokens[0] == "/EFFECT" and state & 0xf0 == 0x10:
                        if command_tokens[0] == command_stack[-1]:
                            try:
                                text_bytes += close_table[command_stack[-1]]
                                text_bytes += int.to_bytes(effects_table.index(command_tokens[1]), length=1, byteorder="little")
                                offset += len(close_table[command_stack.pop()])
                            except IndexError:
                                state = state & 0xf0 | 3
                                continue
                        if len(command_stack) == 0:
                            state = 0x03
                            continue
                        state = state & 0xf0 | 3
                    elif command_tokens[0] == "OPTIONS":
                        layout_byte_int = 0
                        try:
                            layout_byte_int += opt_table[command_tokens[1]]
                        except (KeyError, IndexError):
                            state = state & 0xf0 | 3
                            continue

                        layout_byte = int.to_bytes(layout_byte_int, length=1, byteorder="little")
                        text_bytes += b"\x14"
                        text_bytes += int.to_bytes(opt_count, length=1, byteorder="little")
                        text_bytes += b"\x0c"
                        text_bytes += layout_byte
                        command_stack.append("/OPTIONS")
                        opt_count += 1
                        state = 0x13
                        offset += 4
                    elif command_tokens[0] == "/OPTIONS":
                        if command_tokens == command_stack[-1]:
                            text_bytes += b"\x00"
                            command_stack.pop()
                            offset += 1
                        if len(command_stack) == 0:
                            state = 0x03
                            continue
                        state = state & 0xf0 | 3
                    elif command_tokens[0] == "TIME":
                        time_byte = b""
                        try:
                            time_byte = int.to_bytes(int(command_tokens[1], base=16), length=1, byteorder="little")
                        except (TypeError, IndexError):
                            state = state & 0xf0 | 3
                            continue
                        text_bytes += b"\x16"
                        text_bytes += time_byte
                        state = state & 0xf0 | 3
                        offset += 2
                    elif command_tokens[0] == "PARTY":
                        party_byte = b""
                        try:
                            party_byte += party_tbl[command_tokens[1]]
                        except (KeyError, IndexError):
                            state = state & 0xf0 | 3
                            continue
                        text_bytes += b"\x04"
                        text_bytes += party_byte
                        state = state & 0xf0 | 0
                        offset += 2
                    elif command_tokens[0] == "SYMBOL":
                        symbol_byte = b""
                        try:
                            symbol_byte = int.to_bytes(int(command_tokens[1], base=16), length=1, byteorder="little")
                        except (TypeError, IndexError):
                            state = state & 0xf0 | 3
                            continue
                        text_bytes += symbol_byte
                        state = state & 0xf0 | 3
                        offset += 1
                    elif command_tokens[0] == "PLACEHOLDER":
                        placeholder_byte = b""
                        try:
                            placeholder_byte = int.to_bytes(int(command_tokens[1], base=16), length=1, byteorder="little")
                        except (TypeError, IndexError):
                            state = state & 0xf0 | 3
                            continue
                        text_bytes += b"\x07"
                        text_bytes += placeholder_byte
                        state = state & 0xf0 | 3
                        offset += 2
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
            elif i == "=":
                state = state & 0xf0 | 1
            elif i == "[":
                state = state & 0xf0 | 2
                command = ""
            elif i == "|":
                text_bytes += b"\x02"
                offset += 1
            elif i == "\\":
                text_bytes += b"\x00"
                offset += 1
            else:
                if i in conv_table.keys():
                    text_bytes += conv_table[i]
                else:
                    text_bytes += str.encode(i)
                offset += 1
                state = state & 0xf0 | 0

    variables["OFFSET"] = offset
    return (pointer_tbl, text_bytes, variables)
    
def process_output(tbl):
    ptsize = tbl[2]["PTSIZE"]
    offset = tbl[2]["OFFSET"]
    output = int.to_bytes(ptsize, length=2, byteorder="little")
    for ptr in tbl[0]:
        output += int.to_bytes(ptr + ptsize, length=2, byteorder="little")
    output += int.to_bytes(offset + ptsize, length=2, byteorder="little") * (ptsize // 2 - len(tbl[0]) - 1)
    output += tbl[1]
    output += b"_" * (-(len(output) % -2048))
    return output