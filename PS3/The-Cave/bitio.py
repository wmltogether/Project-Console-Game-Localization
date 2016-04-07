# -*- coding: cp936 -*-
#based on M.Hiroi(bitio.py),change open() to cStringIO() for file input & output
from cStringIO import StringIO
# 定数の定義
WOPEN = "wb"
ROPEN = "rb"

# バイト単位の入出力
def getc(f):
    c = f.read(1)
    if c == '': return None
    return ord(c)

def putc(f, x):
    f.write(chr(x & 0xff))


# クラス定義
class BitIO:
    def __init__(self, file_buff, mode):
        if mode == ROPEN:
            self.cnt = 0
        elif mode == WOPEN:
            self.cnt = 8
        else:
            raise 'BitIO: file mode error'
        self.mode = mode
        #self.file = open(name, mode)
        self.file = file_buff
        self.buff = 0

    # 1 bit input
    def getbit(self):
        self.cnt -= 1
        if self.cnt < 0:
            self.buff = getc(self.file)
            if self.buff is None: return None
            self.cnt = 7
        return (self.buff >> self.cnt) & 1

    # 1 bit output
    def putbit(self, bit):
        self.cnt -= 1
        if bit > 0: self.buff |= (1 << self.cnt)
        if self.cnt == 0:
            putc(self.file, self.buff)
            self.buff = 0
            self.cnt = 8

    # n bits input
    def getbits(self, n):
        v = 0
        p = 1 << (n - 1)
        while p > 0:
            if self.getbit() == 1: v |= p
            p >>= 1
        return v

    # n bits output
    def putbits(self, n, x):
        p = 1 << (n - 1)
        while p > 0:
            self.putbit(p & x)
            p >>= 1



