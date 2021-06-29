from huffman import BitBuffer,HuffmanEncoder, CompressorLetters, CompressorPrefix
import sys
import os
import subprocess


def doCompressing(path, prefix):
    with open(path, "rt") as file:
        text = file.read()
    words = text.split()
    print('Read {} words, {} bytes.'.format(len(words), len(text)))
    if prefix == "True":
        compressedDataCode, bits = CompressorPrefix().Compress(words)
        with open("./trash.py", "wt") as outfile:
            outfile.write(compressedDataCode)
        with open("output.txt", "wt") as outfile:
            outfile.write(bits)
    else:
        compressedDataCode , bits = CompressorLetters().Compress(words)
        with open("./trash.py", "wt") as outfile:
            outfile.write(compressedDataCode)
        with open("output.txt", "wt") as outfile1:
            outfile1.write(bits)
    size = len(compressedDataCode)
    print('{:9d} ./output.txt'.format(size))



if __name__ == '__main__':
    doCompressing(sys.argv[1], sys.argv[2])
