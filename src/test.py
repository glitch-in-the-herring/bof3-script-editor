from parse import parse, process_tbl

a = """==This should appear as bytes
this too...\\
==what about this one?\\
"""
x = parse(a)
n = 0

print("\nPointer tbl")
a = process_tbl(x)
n = 0
for i in a:
    print("{:02x}".format(i), end="")
    if n % 8 == 7:
        print("")
    n += 1