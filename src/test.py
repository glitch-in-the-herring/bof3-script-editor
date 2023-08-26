from parse import parse, process_output

with open("../out.txt", "r") as f:
    a = f.read()
    x = parse(a)
    with open("../binout.txt", "wb") as o:
        o.write(x[1])
#x_p = process_output(x)

#f = open("test.bin", "wb")
#f.write(x_p)
#f.close()
