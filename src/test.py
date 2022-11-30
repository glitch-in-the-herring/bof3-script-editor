from parse import parse, process_output

a = """Area Name or Something\\==[COLOR RED]
This is some red text[/COLOR]\\
==[TIME 10]
That just got delayed\\
==[PARTY RYU]

[PARTY RYU] talk??\\
"""
x = parse(a)
x_p = process_output(x)

f = open("test.bin", "wb")
f.write(x_p)
f.close()
