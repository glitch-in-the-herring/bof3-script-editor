from parse import parse

a = "$PTSIZE = 1300;\nThis should appear as bytes"
x = parse(a)
n = 0

for i in x[1]:
    print("{:02x}".format(i), end="")
    if n % 8 == 7:
        print("")
    n += 1
