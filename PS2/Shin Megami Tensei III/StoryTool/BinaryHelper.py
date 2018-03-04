# /usr/bin/python2
import struct


class BinaryReader:

    def __init__(self, base_stream):
        self.base_stream = base_stream

    def Seek(self, position, seekorigin=0):
        return self.base_stream.seek(position, seekorigin)

    def Tell(self):
        return self.base_stream.tell()

    def ReadByte(self):
        return self.base_stream.read(1)

    def ReadBytes(self, count):
        return self.base_stream.read(count)

    def ReadChar(self):
        return ord(self.base_stream.read(1))

    def ReadChars(self, count):
        return struct.unpack('%dB', self.base_stream.read(count))

    def ReadInt16(self):
        return struct.unpack('h', self.base_stream.read(2))[0]

    def ReadInt32(self):
        return struct.unpack('i', self.base_stream.read(4))[0]

    def ReadInt64(self):
        return struct.unpack('q', self.base_stream.read(8))[0]

    def ReadUInt16(self):
        return struct.unpack('H', self.base_stream.read(2))[0]

    def ReadUInt32(self):
        return struct.unpack('I', self.base_stream.read(4))[0]

    def ReadUInt64(self):
        return struct.unpack('Q', self.base_stream.read(8))[0]

    def ReadFloat(self):
        return struct.unpack('f', self.base_stream.read(4))[0]

    def ReadBEInt16(self):
        return struct.unpack('>h', self.base_stream.read(2))[0]

    def ReadBEInt32(self):
        return struct.unpack('>i', self.base_stream.read(4))[0]

    def ReadBEInt64(self):
        return struct.unpack('>q', self.base_stream.read(8))[0]

    def ReadBEUInt16(self):
        return struct.unpack('>H', self.base_stream.read(2))[0]

    def ReadBEUInt32(self):
        return struct.unpack('>I', self.base_stream.read(4))[0]

    def ReadBEUInt64(self):
        return struct.unpack('>Q', self.base_stream.read(8))[0]

    def Read7BitEncodedInt(self):
        a, b, c = 0, 0, 0
        mask = 0x7f
        shift = 7
        while c < 5:
            d = ord(self.ReadByte())
            a |= (d & mask) << b
            b += shift
            if ((d & (mask + 1)) == 0):
                break
            c += 1

        if c >= 5:
            raise NameError, ("Too many bytes in 7 bit encoded Int32")
        return a

    def ReadDotNETString(self):
        capacity = self.Read7BitEncodedInt()
        if capacity < 0:
            raise IOError, ("Invalid binary file (string len < 0)")
        if capacity == 0:
            return ""
        string_buffer = self.ReadBytes(capacity)
        return string_buffer

    def ReadCString(self):
        string = ""
        c = True
        while (c):
            var = self.ReadByte()
            if not var:
                break
            if (var != "\x00"):
                string += var
            else:
                self.Seek(-1, 1)
                c = False
                break
        return string


class BinaryWriter:

    def __init__(self, base_stream):
        self.base_stream = base_stream

    def Seek(self, position, seekorigin=0):
        return self.base_stream.seek(position, seekorigin)

    def Tell(self):
        return self.base_stream.tell()

    def WriteByte(self, value):
        self.base_stream.write(value[0])

    def WriteBytes(self, value):
        self.base_stream.write(value)

    def WriteInt16(self, value):
        self.base_stream.write(struct.pack('h', value))

    def WriteInt32(self, value):
        self.base_stream.write(struct.pack('i', value))

    def WriteInt64(self, value):
        self.base_stream.write(struct.pack('q', value))

    def WriteUInt16(self, value):
        self.base_stream.write(struct.pack('H', value))

    def WriteUInt32(self, value):
        self.base_stream.write(struct.pack('I', value))

    def WriteUInt64(self, value):
        self.base_stream.write(struct.pack('Q', value))

    def WriteFloat(self, value):
        self.base_stream.write(struct.pack('f', value))

    def WriteBEInt16(self, value):
        self.base_stream.write(struct.pack('>h', value))

    def WriteBEInt32(self, value):
        self.base_stream.write(struct.pack('>i', value))

    def WriteBEInt64(self, value):
        self.base_stream.write(struct.pack('>q', value))

    def WriteBEUInt16(self, value):
        self.base_stream.write(struct.pack('>H', value))

    def WriteBEUInt32(self, value):
        self.base_stream.write(struct.pack('>I', value))

    def WriteBEUInt64(self, value):
        self.base_stream.write(struct.pack('>Q', value))

    def FillBytes(self, value, count):
        if count <= 0:
            count = 0
        if len(value) <= count:
            value += '\x00' * (count - len(value))
        self.base_stream.write(value[:count])

    def Write7BitEncodedInt(self, value):
        if value == 0:
            self.WriteByte(chr(value))
        while value != 0:
            num = (value >> 7) & 0x1ffffff
            num2 = value & 0x7f
            if num != 0:
                num2 = num2 | 0x80
            self.WriteByte(chr(num2))
            value = num

    def WriteDotNETString(self, value):
        byteCount = len(value)
        self.Write7BitEncodedInt(byteCount)
        self.WriteBytes(value, len(value))

    def Truncate(self):
        self.base_stream.truncate()
