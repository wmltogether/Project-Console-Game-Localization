using System.Collections;
using System.Collections.Generic;
using System.IO;
using System;
using System.CodeDom;
using Huffman;
using System.Drawing;

namespace AltusFontTool
{
    public class PersonaFont
    {
        public class FontInfo
        {
            ///
            /// 0000000ch 字模数
            /// 00000010h 字模宽高
            ///
            public uint palette_offset = 0;
            private uint unk0;
            public uint char_nums = 0;
            public UInt16 t_width = 0;
            public UInt16 t_height = 0;
            public UInt16 t_length = 0;
            public UInt16 palette_nums = 0;
            public byte[] palette_data;
            private uint var_98 = 0;
            public uint cfont_offset;
            public uint dbase_offset;

            public FontInfo(BinaryReader br)
            {
                br.BaseStream.Seek(0, SeekOrigin.Begin);
                this.palette_offset = br.ReadUInt32();
                this.unk0 = br.ReadUInt32();
                br.BaseStream.Seek(0xa, SeekOrigin.Begin);
                palette_nums = br.ReadUInt16();
                cfont_offset = (uint)palette_nums * 0x40 + this.palette_offset;
                br.BaseStream.Seek(0x16, SeekOrigin.Begin);
                palette_nums = br.ReadUInt16();
                br.BaseStream.Seek(0xe, SeekOrigin.Begin);
                this.char_nums = br.ReadUInt16();
                this.t_width = br.ReadUInt16();
                this.t_height = br.ReadUInt16();
                this.t_length = br.ReadUInt16();
                br.BaseStream.Seek(this.palette_offset, SeekOrigin.Begin);
                //get palette
                this.palette_data = br.ReadBytes(0x40);
                //get data
                
                
                if (palette_nums != 0)
                {
                    br.BaseStream.Seek(0x4, SeekOrigin.Begin);
                    unk0 = br.ReadUInt32();
                    br.BaseStream.Seek(cfont_offset, SeekOrigin.Begin);
                    uint m_size = br.ReadUInt32(); // 00000060h
                    dbase_offset = cfont_offset + 8 + m_size;
                }

            }
        }
        public byte[] DecompressTexture(BinaryReader br, FontInfo fInfo)
        {
            byte[] dst;
            List<byte> dst_list = new List<byte>();
            uint addr0, addr1, addr2, addr3;
            uint t0, t1, t2;
            int[] tbl;
            br.BaseStream.Seek(fInfo.dbase_offset, SeekOrigin.Begin); //000003f8h
            addr0 = fInfo.dbase_offset + fInfo.char_nums * 4; //00002938h
            br.BaseStream.Seek(addr0, SeekOrigin.Begin);
            t0 = br.ReadUInt32(); // 0x20
            t1 = br.ReadUInt32(); // 0xbd0
            br.BaseStream.Seek(addr0 + 0x18, SeekOrigin.Begin);
            t2 = br.ReadUInt32(); // 0x2540
            addr1 = t0 + addr0; //0x2958 字典地址
            addr2 = t0 + t1 + addr0;//0x3528
            addr3 = t0 + t1 + t2 + addr0; //0x5a68 压缩chunk的起始地址
            int i, j, k;
            k = 1;
            i = 1;
            int c;
            byte b;
            br.BaseStream.Seek(addr1, SeekOrigin.Begin);
            tbl = new int[(int)t1 / 2 - 1];
            for (var v = 0; v < (int)t1 / 2 - 1; v++)
            {
                tbl[v] = br.ReadInt16();
            }
            br.BaseStream.Seek(addr3 - 4, SeekOrigin.Begin);//0x5a64h
            uint n = br.ReadUInt32(); // 0x2c21b7
            
            while (n > 0)
            {
                if (i == 1)
                {
                    c = br.ReadInt16();
                    i = c;
                    if (i < 0) 
                    { 
                        i = i + 0x10000; 
                    } 
                    i = i + 0x10000;
                }
                k = 3 * tbl[k + (i & 1)] + 1;
                i = i / 2;
                n -= 1;
                if (tbl[k] == 0)
                {
                    b = (byte)(tbl[k + 1] & 0xff);
                    dst_list.Add(b);
                    k = 1;
                }

            }
            dst = dst_list.ToArray();
            return dst;

        }

        public void Compress()
        {
            
        }
        public void LoadFont(string fontName)
        {
            byte[] dest;
            FileStream fs = File.Open(fontName, FileMode.Open, FileAccess.Read);
            BinaryReader br = new BinaryReader(fs);
            FontInfo fInfo = new FontInfo(br);
            br.BaseStream.Seek(fInfo.cfont_offset, SeekOrigin.Begin);
            dest = DecompressTexture(br, fInfo);
            File.WriteAllBytes("font.bin", dest);
            TextureEncoder tenc = new TextureEncoder();
            int width = 480;
            int height = width * 6;
            Bitmap bm = tenc.get4Bpp(width,
                            height,
                            (int)fInfo.t_width, 
                            (int)fInfo.t_height, 
                            dest, 
                            fInfo.palette_data, 
                            EndianType.BIG);
            bm.Save("font.png");


        }
        

    }

}