all: extractor
extractor: src/extractor.c src/utils.c
	gcc -o extractor src/extractor.c src/utils.c -O2