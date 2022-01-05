from parse import parse

a = "==[COLOR PURPLE][COLOR RED]test[/COLOR][/COLOR]\\==test"
x = parse(a)
n = 0

for i in x[1]:
    print("{:02x}".format(i), end="")
    if n % 8 == 7:
        print("")
    n += 1
