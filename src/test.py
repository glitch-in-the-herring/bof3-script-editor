from parse import parse, process_output

a = """[POS BL NV]
[PARTY TEEPO] talk??\\
"""
x = parse(a)
#x_p = process_output(x)

print(x)

#f = open("test.bin", "wb")
#f.write(x_p)
#f.close()
