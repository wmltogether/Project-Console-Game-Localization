# -*- coding: utf-8 -*-
# nlzss python 2 port 
# use decompress_nlzss() & compress_nlzss() to (de)compress strings
'''
Copyright © magical

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''

import sys
from struct import pack, unpack
from cStringIO import StringIO
from array import array
from collections import defaultdict
from operator import itemgetter

def bits(byte):
    return ((byte >> 7) & 1,
            (byte >> 6) & 1,
            (byte >> 5) & 1,
            (byte >> 4) & 1,
            (byte >> 3) & 1,
            (byte >> 2) & 1,
            (byte >> 1) & 1,
            (byte) & 1)

class SlidingWindow:
    # The size of the sliding window
    size = 4096

    # The minimum displacement.
    disp_min = 2

    # The hard minimum — a disp less than this can't be represented in the
    # compressed stream.
    disp_start = 1

    # The minimum length for a successful match in the window
    match_min = 1

    # The maximum length of a successful match, inclusive.
    match_max = None

    def __init__(self, buf):
        self.data = buf
        self.hash = defaultdict(list)
        self.full = False

        self.start = 0
        self.stop = 0
        #self.index = self.disp_min - 1
        self.index = 0

        assert self.match_max is not None

    def next(self):
        if self.index < self.disp_start - 1:
            self.index += 1
            return

        if self.full:
            olditem = self.data[self.start]
            assert self.hash[olditem][0] == self.start
            self.hash[olditem].pop(0)

        item = self.data[self.stop]
        self.hash[item].append(self.stop)
        self.stop += 1
        self.index += 1

        if self.full:
            self.start += 1
        else:
            if self.size <= self.stop:
                self.full = True

    def advance(self, n=1):
        """Advance the window by n bytes"""
        for _ in range(n):
            self.next()

    def search(self):
        match_max = self.match_max
        match_min = self.match_min

        counts = []
        indices = self.hash[self.data[self.index]]
        for i in indices:
            matchlen = self.match(i, self.index)
            if matchlen >= match_min:
                disp = self.index - i
                #assert self.index - disp >= 0
                #assert self.disp_min <= disp < self.size + self.disp_min
                if self.disp_min <= disp:
                    counts.append((matchlen, -disp))
                    if matchlen >= match_max:
                        #assert matchlen == match_max
                        return counts[-1]

        if counts:
            match = max(counts, key=itemgetter(0))
            return match

        return None

    def match(self, start, bufstart):
        size = self.index - start

        if size == 0:
            return 0

        matchlen = 0
        it = range(min(len(self.data) - bufstart, self.match_max))
        for i in it:
            if self.data[start + (i % size)] == self.data[bufstart + i]:
                matchlen += 1
            else:
                break
        return matchlen

class NLZ10Window(SlidingWindow):
    size = 4096

    match_min = 3
    match_max = 3 + 0xf

class NLZ11Window(SlidingWindow):
    size = 4096
    match_min = 3
    match_max = 0x111 + 0xFFFF

def packflags(flags):
    n = 0
    for i in xrange(8):
        n <<= 1
        try:
            if flags[i]:
                n |= 1
        except IndexError:
            pass
    return n

def _compress(input, windowclass=NLZ11Window):

    window = windowclass(input)

    i = 0
    while True:
        if len(input) <= i:
            break
        match = window.search()
        if match:
            yield match
            #if match[1] == -283:
            #    raise Exception(match, i)
            window.advance(match[0])
            i += match[0]
        else:
            yield input[i]
            window.next()
            i += 1

def chunkit(it, n):
    buf = []
    for x in it:
        buf.append(x)
        if n <= len(buf):
            yield buf
            buf = []
    if buf:
        yield buf

class DecompressionError(ValueError):
    pass

class lz11(object):
    def __init__(self):
        self.lz11_sig = 0x11
        pass

    def decompress_raw_lzss10(self,indata, decompressed_size, _overlay=False):
        """Decompress LZSS-compressed bytes. Returns a bytearray."""
        data = bytearray()

        it = iter(indata)

        if _overlay:
            disp_extra = 3
        else:
            disp_extra = 1

        def writebyte(b):
            data.append(b)

        def readbyte():
            return ord(next(it))

        def readshort():
            # big-endian
            a = ord(next(it))
            b = ord(next(it))
            return (a << 8) | b

        def copybyte():
            data.append(next(it))

        while len(data) < decompressed_size:
            b = readbyte()
            flags = bits(b)
            for flag in flags:
                if flag == 0:
                    copybyte()
                elif flag == 1:
                    sh = readshort()
                    count = (sh >> 0xc) + 3
                    disp = (sh & 0xfff) + disp_extra

                    for _ in range(count):
                        writebyte(data[-disp])
                else:
                    raise ValueError(flag)

                if decompressed_size <= len(data):
                    break

        if len(data) != decompressed_size:
            raise DecompressionError("decompressed size does not match the expected size")

        return data

    def decompress_raw_lzss11(self, indata, decompressed_size):
        """Decompress LZSS-compressed bytes. Returns a bytearray."""
        data = bytearray()

        it = iter(indata)

        def writebyte(b):
            data.append(b)

        def readbyte():
            return ord(next(it))

        def copybyte():
            data.append(next(it))

        while len(data) < decompressed_size:
            b = readbyte()
            flags = bits(b)
            for flag in flags:
                if flag == 0:
                    copybyte()
                elif flag == 1:
                    b = readbyte()
                    indicator = b >> 4

                    if indicator == 0:
                        # 8 bit count, 12 bit disp
                        # indicator is 0, don't need to mask b
                        count = (b << 4)
                        b = readbyte()
                        count += b >> 4
                        count += 0x11
                    elif indicator == 1:
                        # 16 bit count, 12 bit disp
                        count = ((b & 0xf) << 12) + (readbyte() << 4)
                        b = readbyte()
                        count += b >> 4
                        count += 0x111
                    else:
                        # indicator is count (4 bits), 12 bit disp
                        count = indicator
                        count += 1

                    disp = ((b & 0xf) << 8) + readbyte()
                    disp += 1

                    try:
                        for _ in range(count):
                            writebyte(data[-disp])
                    except IndexError:
                        raise Exception(count, disp, len(data), sum(1 for x in it) )
                else:
                    raise ValueError(flag)

                if decompressed_size <= len(data):
                    break

        if len(data) != decompressed_size:
            raise DecompressionError("decompressed size does not match the expected size")

        return data

    def decompress_nlzss(self ,string):
        header = string[:4]
        decompressed_size, = unpack("<L", header[1:4] + '\x00')
        decompress_raw = self.decompress_raw_lzss11
        if header[0] == chr(0x10):
            #lz10
            decompress_raw = self.decompress_raw_lzss10
        elif header[0] == chr(0x11):
            #lz11
            decompress_raw = self.decompress_raw_lzss11
        elif header[0] == chr(0x13):
            #lz13
            header = string[:8]
            decompressed_size, = unpack("<L", header[5:8] + '\x00')
            decompress_raw = self.decompress_raw_lzss11
            return decompress_raw(string[8:], decompressed_size) 
        else:
            pass
            #raise DecompressionError("not as lzss-compressed file")

        return decompress_raw(string[4:], decompressed_size)

    def compress_nlzss(self,string , compress_type):
        out = StringIO()
        input_length = len(string)
        if compress_type == 11:
            self.compress11(string,input_length ,out)
        elif compress_type == 13:
            self.compress11(string,input_length ,out)
            enc_data = out.getvalue()
            enc_data = enc_data[1:4] + enc_data
            enc_data = "\x11" + enc_data
            return enc_data
        elif compress_type == 10:
            self.compress10(string,input_length ,out)
        else:
            pass
            
        return out.getvalue()

    def compress10(self ,input,input_length, out):
        # header
        out.write(pack("<L", (input_length << 8) + 0x10))
        # body
        length = 0
        for tokens in chunkit(_compress(input ,windowclass=NLZ10Window), 8):
            flags = [type(t) == tuple for t in tokens]
            out.write(pack(">B", packflags(flags)))

            for t in tokens:
                if type(t) == tuple:
                    count, disp = t
                    count -= 3
                    disp = (-disp) - 1
                    assert 0 <= disp < 4096
                    sh = (count << 12) | disp
                    out.write(pack(">H", sh))
                else:
                    out.write(pack(">B", ord(t)))

            length += 1
            length += sum(2 if f else 1 for f in flags)
        # padding
        padding = 4 - (length % 4 or 4)
        if padding:
            out.write('\xff' * padding)

    def compress11(self,input , input_length, out):
        # header
        out.write(pack("<L", (input_length << 8) + 0x11))
        # body
        length = 0
        for tokens in chunkit(_compress(input, windowclass=NLZ11Window), 8):
            flags = [type(t) == tuple for t in tokens]
            out.write(pack(">B", packflags(flags)))
            length += 1
            for t in tokens:
                if type(t) == tuple:
                    count, disp = t
                    disp = (-disp) - 1
                    assert 0 <= disp <= 0xFFF
                    if count <= 1 + 0xF:
                        count -= 1
                        assert 2<= count <= 0xf
                        sh = (count << 12) | disp
                        out.write(pack(">H", sh))
                        length += 2
                    elif count <= 0x11 + 0xFF:
                        count -= 0x11
                        assert 0 <= count <= 0xFF
                        b = count >> 4
                        sh = ((count & 0xF) << 12) | disp
                        out.write(pack(">BH", b, sh))
                        length += 3
                    elif count <= 0x111 + 0xFFFF:
                        count -= 0x111
                        assert 0 <= count <= 0xFFFF
                        l = (1 << 28) | (count << 12) | disp
                        out.write(pack(">L", l))
                        length += 4
                    else:
                        raise ValueError(count)

                else:
                    out.write(pack(">B", ord(t)))
                    length += 1

        padding = 4 - (length % 4 or 4)
        if padding:
            out.write(b'\xff' * padding)

