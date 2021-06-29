class HuffmanNode:
    def __init__(self, symbol, count, left, right):
        self.symbol = symbol
        self.count = count
        self.left = left
        self.right = right

    def __lt__(self, other):
        # Allows nodes to be sorted by count
        return self.count < other.count

    def MakeEncoding(self):
        return self._MakeEncoding({}, 0, 0)

    def _MakeEncoding(self, encoding, data, nbits):
        # Recursively visit the tree to compute the bit string for each symbol.
        # The result is a dictionary such that encoding[symbol] = (data, nbits),
        # a tuple that represents the variable number of bits in the encoding.
        if self.symbol is not None:
            encoding[self.symbol] = (data, nbits)
        if self.left is not None:
            self.left._MakeEncoding(encoding, data << 1, 1+nbits)
        if self.right is not None:
            self.right._MakeEncoding(encoding, 1 | (data << 1), 1+nbits)
        return encoding

    def TreeTuple(self):
        # Convert the tree into a tuple format.
        # Each internal node becomes a tuple (left, right).
        # Each leaf node is just the symbol by itself.
        if self.symbol is not None:
            return self.symbol
        return (self.left.TreeTuple(), self.right.TreeTuple())

    def SourceCode(self):
        return repr(self.TreeTuple()).replace(' ', '')


class HuffmanEncoder:
    def __init__(self):
        self.table = {}

    def Tally(self, symbol):
        self.table[symbol] = 1 + self.table.get(symbol, 0)

    def Compile(self):
        if len(self.table) == 0:
            raise Exception('Huffman encoder needs to have at least one symbol.')

        # Build a binary tree that allows us to use a variable
        # number of bits to encode each symbol based on its probability.
        # Make a list of HuffmanNodes.
        # Keep it sorted in ascending order of frequency.
        tree = sorted(HuffmanNode(x[0], x[1], None, None) for x in self.table.items())

        # While there is more than one node at the top of the tree,
        # keep removing the least populated pair of items and combine
        # them into a new internal node.
        while len(tree) != 1:
            a, b, *rest = tree
            node = HuffmanNode(None, a.count + b.count, a, b)
            tree = sorted([node] + rest)

        # The single remaining node is the root node of the tree.
        return tree[0]

class BitBuffer:
    def __init__(self):
        self.buf = bytearray()
        self.accum = 0
        self.nbits = 0
        self.column = 0

    def Append(self, pattern):
        data, dbits = pattern
        while self.nbits + dbits >= 6:
            # We can emit a complete base64 character to represent a chunk of 6 bits.
            grab = 6 - self.nbits
            mask = (1 << grab) - 1
            self.accum = (self.accum << grab) | (mask & (data >> (dbits - grab)))
            dbits -= grab
            self.buf.append(b'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'[self.accum])
            self.accum = 0
            self.nbits = 0
            self.column += 1
            if self.column == 80:
                self.buf.append(ord('\n'))
                self.column = 0

        # Transfer any residual data bits into the accumulator.
        if dbits >= 0:
            mask = (1 << dbits) - 1
            self.accum = (self.accum << dbits) | (mask & data)
            self.nbits += dbits

    def Format(self):
        # Flush any remaining bits left in the accumulator.
        if self.nbits > 0:
            self.Append((0, (6 - self.nbits)))

        # Always end on a newline.
        if self.column > 0:
            self.buf.append(ord('\n'))
            self.column = 0

        # Convert the bytes to utf-8 text.
        return self.buf.decode('utf-8')

class CompressorPrefix:
    def Name(self):
        return 'prefix'

    def Compress(self, words):
        repeatRoot, tailRoot, charRoot = self._HuffmanCodes(words)
        repeatCode = repeatRoot.MakeEncoding()
        tailCode = tailRoot.MakeEncoding()
        charCode = charRoot.MakeEncoding()
        buf = self._Encode(words, repeatCode, tailCode, charCode)
        source = "Repeat=" + repeatRoot.SourceCode() + "\n"
        source += "Tail=" + tailRoot.SourceCode() + "\n"
        source += "Char=" + charRoot.SourceCode() + "\n"
        source += "NumWords={:d}\n".format(len(words))
        Bits = buf.Format()
        return source,Bits

    def _Encode(self, words, repeatCode, tailCode, charCode):
        pw = ''
        buf = BitBuffer()
        for w in words:
            prefix = self._LettersInCommon(pw, w)
            buf.Append(repeatCode[prefix])
            tail = w[prefix:]
            buf.Append(tailCode[len(tail)])
            for c in tail:
                buf.Append(charCode[c])
            pw = w
        return buf

    def _HuffmanCodes(self, words):
        repeatHuff = HuffmanEncoder()
        tailHuff = HuffmanEncoder()
        charHuff = HuffmanEncoder()
        pw = ''
        for w in words:
            prefix = self._LettersInCommon(pw, w)
            repeatHuff.Tally(prefix)
            tailHuff.Tally(len(w) - prefix)
            for c in w[prefix:]:
                charHuff.Tally(c)
            pw = w
        return repeatHuff.Compile(), tailHuff.Compile(), charHuff.Compile()

    def _LettersInCommon(self, a, b):
        n = min(len(a), len(b))
        for i in range(n):
            if a[i] != b[i]:
                return i
        return n


class CompressorLetters:
    def Name(self):
        return 'letters'

    def Compress(self, words):
        charRoot = self._HuffmanCode(words)
        charCode = charRoot.MakeEncoding()
        buf = self._Encode(words, charCode)
        source = "Char=" + charRoot.SourceCode() + "\n"
        source += "NumChars={:d}\n".format(sum(1+len(w) for w in words)-1)
        Bits = buf.Format()
        return source,Bits

    def _Encode(self, words, charCode):
        buf = BitBuffer()
        for w in words:
            for c in w:
                buf.Append(charCode[c])
            buf.Append(charCode['\n'])
        return buf

    def _HuffmanCode(self, words):
        charHuff = HuffmanEncoder()
        for w in words:
            for c in w:
                charHuff.Tally(c)
            charHuff.Tally('\n')
        return charHuff.Compile()

class BitReader:
    def __init__(self, encoded):
        self.encoded = encoded.replace('\n', '')
        self.position = 0
        self.accum = 0
        self.nbits = 0

    def GetNextBit(self):
        if self.nbits == 0:
            c = self.encoded[self.position]
            self.position += 1
            self.accum = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'.index(c)
            self.nbits = 6
        bit = 1 & (self.accum >> 5)
        self.accum = 0b111111 & (self.accum << 1)
        self.nbits -= 1
        return bit

