# importing required libaries

from huffman import CompressorLetters, CompressorPrefix
import sys



########################################################################

# Compressing function 
'''
1/ The function read the text file which is going to compress it.
2/ The compress file is based on two techniques of Huffman algorithm which are i) letter and ii) prefix.
3/ If we plan to use the prefix module we have to make the flag of it True otherwise we can use False flag.
4/ The functioin creates a compressed file based on selected methd. 
'''

def doCompressing(path, prefix):
    with open(path, "rt") as file:
        text = file.read()
    words = text.split()
    
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
    
    print('[INFO]...Compressed file has been created and named output.txt')



if __name__ == '__main__':
    doCompressing(sys.argv[1], sys.argv[2])
