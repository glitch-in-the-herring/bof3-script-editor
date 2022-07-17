def to_little(n, b):
    output = []
    for i in range(b):
        output.append((n & (0xff <<i * 8)) >> i * 8);
    return output