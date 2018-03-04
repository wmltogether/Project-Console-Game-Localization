using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;

namespace AtlusGames.Extension
{
    public class BitIO
    {
        public class BitWrite
        {
            private int ac = 0;
            private int bcount = 0;
            private BinaryWriter output;

            public BitWrite(BinaryWriter bw)
            {
                output = bw;
            }

            public void WriteBit(int bit)
            {
                if (this.bcount == 8)
                {
                    this.Flush();
                }

                if (bit > 0)
                {
                    this.ac |= (1 << (7 - this.bcount));
                }

                this.bcount += 1;
            }

            public void writebits(int bits, int value)
            {
                while (value > 0){
                    this.WriteBit(bits & (1 << (value - 1)));
                    value -= 1;
                }
            }
                

            private void Flush()
            {
                this.output.Write((byte)this.ac);
                this.ac = 0;
                this.bcount = 0;
            }

        }

        public class BitReader: IDisposable
        {
            private BinaryReader input;
            private int bcount = 0; 
            private int read = 0;
            private int ac = 0;

            public BitReader(BinaryReader br)
            {
                input = br;
            }

            public void Dispose()
            {
                ((IDisposable)input).Dispose();
            }

            public int ReadBit()
            {
                if (bcount == 0)
                {
                    try
                    {
                        var a = input.ReadByte();
                        ac = (int)a;
                    }
                    catch (Exception e)
                    {
                    }
                    this.bcount = 8;
                    this.read = 1;

                }
                int rv = (this.ac & (1 << (this.bcount - 1))) >> (this.bcount - 1);
                this.bcount -= 1;
                return rv;
            }

            public int ReadBits(int n)
            {
                var v = 0;
                while (n>0)
                {
                    v = (v << 1) | this.ReadBit();
                    n -= 1;
                }

                return v;
            }
        }
    }
}
