import argparse

argparser = argparse.ArgumentParser(
    description="Extracts BoFIII text sections into .bf3 files"
)
argparser.add_argument(
    "source", metavar="SOURCE", type=str, help="Source file for the extractor"
)
argparser.add_argument(
    "output", metavar="OUTPUT", type=str, help="File to write"
)

def main():

if __name__ == "__main__":
    main()