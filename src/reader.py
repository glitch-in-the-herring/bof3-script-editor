import argparse

argparser = argparse.ArgumentParser(
    description="A tool for writing Breath of Fire III text sections"
)
argparser.add_argument(
    "source", metavar="SOURCE", type=str, help="Source file for the converter"
)
argparser.add_argument(
    "-o", "--output", metavar="OUTPUT", type=str, help="File to write" # no EMI
)
argparser.add_argument(
    "-p", "--patch", metavar="PATCH", type=str, help="File to write" # with EMI
)
argparser.add_argument(
    "-v", "--verbose", action="store_true", default=False
)
args = argparser.parse_args()
curr_offset = 0
offsets = []

if args.output is None:
    args.output = "".join((args.source, ".out"))


def main():
    source = open(args.source, "r")
    output = open(args.output, "wb")

    source_str = source.read()

    source.close()
    output.close()


if __name__ == "__main__":
    main()
