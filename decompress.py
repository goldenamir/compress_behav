from huffman import BitReader
import sys
import trash


def Huffman(reader, node):
    while isinstance(node, tuple):
        node = node[reader.GetNextBit()]
    return node


def ExpandLetters(Bits, Char, NumChars):
    reader = BitReader(Bits)
    return ''.join(Huffman(reader, Char) for _ in range(NumChars))


def ExpandPrefix(Bits, NumWords, Repeat, Tail, Char):
    reader = BitReader(Bits)
    pw = ''
    wlist = []
    for w in range(NumWords):
        repeatLen = Huffman(reader, Repeat)
        tailLen = Huffman(reader, Tail)
        w = pw[:repeatLen] + ''.join(Huffman(reader, Char) for _ in range(tailLen))
        wlist.append(w)
        pw = w
    return '\n'.join(wlist)


def doDecompressing(path, prefix):
    file = open(path, "r")
    file1 = file.readlines()
    content=[x for x in file1]
    str1 = ''.join(str(e) for e in content)
    if prefix =="True":
        Repeat = trash.Repeat
        Tail = trash.Tail
        Char = trash.Char
        Numwords = trash.NumWords
        Bits = str1
        data = ExpandPrefix(Bits, Numwords, Repeat, Tail, Char)
        with open("decompressFile.txt", "wt") as outfile:
            outfile.write(data)
    else:
        Char = trash.Char
        Numwords = trash.NumChars
        Bits = str1
        data = ExpandLetters(Bits, Char, Numwords)
        with open("decompressFile.txt", "wt") as outfile:
            outfile.write(data)


if __name__ == '__main__':
    doDecompressing(sys.argv[1], sys.argv[2])
