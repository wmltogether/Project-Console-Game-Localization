using System.Collections;
using System.Collections.Generic;
using System.IO;
using System;
using System.CodeDom;
using Huffman;
using System.Drawing;
using System.Linq;

namespace AltusFontTool
{
    /// <summary>
    /// 第一区域 
    /// 00000000h~00000020h header 
    ///                     uint32 header_size = 0x20
    ///                     uint32 mem_size = font_size - glyphTable_chunk_size - 7
    ///                     跳过7字节 00 01 01 01 00 00 00
    ///                     uint16 char_nums 
    ///                     uint16 t_width tile宽度
    ///                     uint16 t_height tile高度
    ///                     uint16 t_length tile数据长度
    ///                     byte palette_nums 调色板数量
    ///                     跳过8字节 对齐
    /// 第二区域 
    /// 00000020h~00000060h palette
    /// 
    /// 第三区域
    /// 00000060h~           glyphTable_chunk
    ///                     uint32 glyphTable_chunk_size = chunk.length + 8
    ///                     struct chunk {
    ///                                 byte, (font_left)
    ///                                 byte  (font_right)
    ///                             } * 非汉字部分的字符宽度表
    ///                     跳过8字节 00 00 00 00 00 00 00 00
    ///                     
    ///                     byte[] char_nums * 4 * "00"
    ///                     
    /// 第四区域
    /// 
    /// glyphTable_chunk_offset + glyphTable_chunk_size + 8 ~ +0x20 compress_header
    ///                     uint32 header_size
    ///                     uint32 dictionary_size 字典长度
    ///                     uint32 compressed_size 压缩长度
    ///                     uint32 wnd_length 
    ///                     uint32 tiledata_size 0x120
    ///                     uint32 char_nums + 1
    ///                     uint32 glyphPosList_size 字符指针表长度
    ///                     uint32 decompressed_size解压出的数据长度
    ///                     
    ///                     byte[] 字典
    ///                     byte[] 字符指针表
    ///                     byte[] 压缩数据
    ///                     
    /// </summary>
    public class PersonaFont
    {
        public const string TTF_SANS = "TTF_SANS.otf";
        public const string TTF_SERIF = "TTF_SERIF.otf";
        public const string TTF_FALLBACK = "FALLBACK.otf";
        public class FontInfo
        {
            ///
            /// 0000000ch 字模数
            /// 00000010h 字模宽高
            ///
            public uint palette_offset = 0;
            private uint unk0;
            public uint char_nums = 0;//0xe 字符数
            public UInt16 t_width = 0;// tile宽度
            public UInt16 t_height = 0;// tile高度
            public UInt16 t_length = 0;// tile数据长度 （4bpp t_width * t_height / 2）
            public UInt16 palette_nums = 0;
            public byte[] palette_data;
            public UInt32 glyphTable_chunk_size = 0;
            public byte[] dictData;

            public uint glyphTable_chunk_offset; //value:0x60

            public FontInfo(BinaryReader br)
            {
                br.BaseStream.Seek(0, SeekOrigin.Begin);
                this.palette_offset = br.ReadUInt32();
                this.unk0 = br.ReadUInt32();
                br.BaseStream.Seek(0xa, SeekOrigin.Begin);
                palette_nums = br.ReadUInt16();
                glyphTable_chunk_offset = (uint)palette_nums * 0x40 + this.palette_offset;
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
                    br.BaseStream.Seek(glyphTable_chunk_offset, SeekOrigin.Begin);
                    glyphTable_chunk_size = br.ReadUInt32(); // 00000060h value: 0x349
                }
                uint addr0, addr1, addr2, addr3;
                uint t0, t1, t2;
                uint dbase = glyphTable_chunk_offset + 8 + glyphTable_chunk_size;
                br.BaseStream.Seek(dbase, SeekOrigin.Begin); //000003f8h
                addr0 = dbase + char_nums * 4; //00002938h  压缩块起始地址
                br.BaseStream.Seek(addr0, SeekOrigin.Begin);
                t0 = br.ReadUInt32(); // 0x20  压缩块header 大小
                t1 = br.ReadUInt32(); // 0xbd0  字典长度
                addr1 = t0 + addr0; //0x2958 字典地址
                br.BaseStream.Seek(addr1, SeekOrigin.Begin);
                dictData = br.ReadBytes((int)t1);


            }

            public void OverrideFontSize(int size)
            {
                this.t_width = (UInt16)size;
                this.t_height = (UInt16)size;
                this.t_length = (UInt16)(this.t_width * this.t_height / 2);

            }
        }
        public byte[] DecompressTexture(BinaryReader br, FontInfo fInfo)
        {
            byte[] dst;
            List<byte> dst_list = new List<byte>();
            uint addr0, addr1, addr2, addr3;
            uint t0, t1, t2;
            int[] tbl;
            List<int> glyphPosList = new List<int>();//字符压缩的指针表，记录每个字符压缩位置的指针
            uint dbase = fInfo.glyphTable_chunk_offset + 8 + fInfo.glyphTable_chunk_size;
            br.BaseStream.Seek(dbase, SeekOrigin.Begin); //000003f8h
            addr0 = dbase + fInfo.char_nums * 4; //00002938h  压缩块起始地址
            br.BaseStream.Seek(addr0, SeekOrigin.Begin);
            t0 = br.ReadUInt32(); // 0x20  压缩块header 大小
            t1 = br.ReadUInt32(); // 0xbd0  字典长度
            uint zlength = br.ReadUInt32();//压缩数据长度

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
            uint n = br.ReadUInt32(); // 0x2c21b7 解压长度
            uint glyph_pos = 0;
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
                    if (dst_list.Count % (0x18 * 0x18/2) == 0)
                    {
                        glyphPosList.Add((int)glyph_pos);
                    }
                    dst_list.Add(b);
                    k = 1;
                }
                glyph_pos += 1;

            }
            long pos = br.BaseStream.Position;
            dst = dst_list.ToArray();
            return dst;

        }

        public FontInfo LoadFont(string fontName)
        {
            
            FileStream fs = File.Open(fontName, FileMode.Open, FileAccess.Read);
            BinaryReader br = new BinaryReader(fs);
            FontInfo fInfo = new FontInfo(br);
            br.Close();
            fs.Close();
            return fInfo;
            /*byte[] dest;
            dest = DecompressTexture(br, fInfo);
            File.WriteAllBytes("font.bin", dest);
            TextureEncoder tenc = new TextureEncoder();
            int width = 24*16;
            int height = (int)fInfo.char_nums / 16 * 24 + 24;
            Bitmap bm = tenc.get4Bpp(width,
                            height,
                            (int)fInfo.t_width, 
                            (int)fInfo.t_height, 
                            dest, 
                            fInfo.palette_data, 
                            EndianType.BIG);
            bm.Save("font.png");*/


        }

        public void MakeFont(FontInfo fInfo, List<PFontGlyph> pglyphs, out byte[] dstFont)
        {
            int nonCHGlyphs = 0x1c6;
            Console.WriteLine(string.Format("构建位图字体\n\t-字模宽度{0}\n\t-字模高度{1}\n\t-字模数量{2}\n", fInfo.t_width, fInfo.t_height, pglyphs.Count));
            dstFont = null;
            using (MemoryStream ms = new MemoryStream())
            {
                using (BinaryWriter bw = new BinaryWriter(ms))
                {
                    //header
                    bw.Write(new byte[0x20]);
                    //palette
                    bw.Write(fInfo.palette_data);
                    //glyphtable
                    byte[] glyphTable = BuildGlyphTable(pglyphs, nonCHGlyphs);
                    bw.Write((int)(glyphTable.Length + 8));
                    bw.Write(glyphTable);
                    bw.Write(new byte[4]);
                    bw.Write(new byte[8]);
                    bw.Write(new byte[pglyphs.Count * 4]);

                    //compress
                    byte[] comp;
                    buildCompress(pglyphs, fInfo, out comp);
                    bw.Write(comp);
                    int font_sz = (int)bw.BaseStream.Position;
                    //rewrite header info
                    bw.Seek(0, SeekOrigin.Begin);
                    bw.Write((Int32)0x20);
                    bw.Write((Int32)(font_sz - 7 - (glyphTable.Length + 8)));
                    bw.Write((byte)1);
                    bw.Write((byte)1);
                    bw.Write((Int32)1);
                    bw.Write((Int16)pglyphs.Count);
                    bw.Write((Int16)fInfo.t_width);
                    bw.Write((Int16)fInfo.t_height);
                    bw.Write((Int16)fInfo.t_length);
                    bw.Write((Int16)1);
                    bw.Write(new byte[8]);

                }
                dstFont = ms.ToArray();
            }
        }

        private byte[] BuildGlyphTable(List<PFontGlyph> pglyphs, int nonCHGlyphs)
        {
            byte[] dst = null;
            using (MemoryStream ms = new MemoryStream())
            {
                using (BinaryWriter bw = new BinaryWriter(ms))
                {
                    for (int i=0;i< nonCHGlyphs; i++)
                    {
                        bw.Write((byte)pglyphs[i].left);
                        bw.Write((byte)pglyphs[i].right);
                    }
                }
                dst = ms.ToArray();
            }
            return dst;
        }

        public void buildCompress(List<PFontGlyph> pglyphs, FontInfo fInfo, out byte[] dst)
        {
            dst = null;
            int wndLen = 0;
            int decLen = 0;
            int compressedsize = 0;
            TextureEncoder encoder = new TextureEncoder();
            using (MemoryStream ms = new MemoryStream())
            {
                using (BinaryWriter bw = new BinaryWriter(ms))
                {
                    bw.Write(new byte[0x20]);
                    bw.Write(fInfo.dictData);
                    int seek_ori = (int)bw.BaseStream.Position;
                    List<int> ptr = new List<int>();

                    //bw.Write(new byte[(pglyphs.Count + 1) * 4]);
                    MemoryStream mem = new MemoryStream();
                    for (int i = pglyphs.Count-1; i >= 0 ; i--)
                    {
                        PFontGlyph glyph = pglyphs[i];
                        byte[] input = encoder.create4Bpp(glyph.bitmap, fInfo.t_width, fInfo.t_height, encoder.getPS2PaletteData(fInfo.palette_data), EndianType.LITTLE);
                        mem.Write(input, 0, input.Length);
                        decLen = (int)mem.Position;
                    }
                    mem.Position = 0;
                    int[,] Dictionary = Compression.ReadDict(fInfo.dictData);
                    int DictPart = Compression.FindDictPart(Dictionary);
                    MemoryStream FONT_COMPRESS = new MemoryStream();

                    bool boolean = true;
                    while (boolean)
                    {
                        if (mem.Position == mem.Length) { boolean = false; }
                        else
                        {
                            int s4 = mem.ReadByte();
                            int i = 1;

                            while (Dictionary[i, 1] != s4)
                            {
                                i++;
                                if (Dictionary[i - 1, 1] == 0)
                                {
                                    if ((s4 >> 4) > ((s4 << 4) >> 4))
                                    {
                                        s4 = s4 - (1 << 4);
                                    }
                                    else
                                    {
                                        s4 = s4 - 1;
                                    }
                                    i = 1;
                                }
                            }
                            int v0 = i;
                            while (v0 != 0)
                            {
                                v0 = Compression.FindDictIndex(v0, Dictionary, DictPart, ref FONT_COMPRESS);
                            }
                        }
                    }

                    int GlyphSize = 0;
                    MemoryStream FONT_COMPRESS_BUFFER = new MemoryStream();
                    do
                    {
                        int i = 0;
                        string str = "";
                        while ((i < 8) & (FONT_COMPRESS.Position != 0))
                        {
                            FONT_COMPRESS.Position--;
                            str = Convert.ToString(FONT_COMPRESS.ReadByte()) + str;
                            FONT_COMPRESS.Position--;
                            i++;
                        }
                        str = str.PadLeft(8, '0');
                        FONT_COMPRESS_BUFFER.WriteByte(Convert.ToByte(str, 2));
                        GlyphSize++; 
                    } while (FONT_COMPRESS.Position != 0);

                    FONT_COMPRESS_BUFFER.WriteByte(0);
                    GlyphSize++;
                    byte[] positions;
                    wndLen = Compression.WriteGlyphPosition(FONT_COMPRESS_BUFFER, Dictionary, fInfo, out positions);

                    byte[] comp = FONT_COMPRESS_BUFFER.ToArray();
                    compressedsize = comp.Length;

                    bw.Write(positions);
                    bw.Write(comp);

                    bw.Seek(0, SeekOrigin.Begin);
                    bw.Write((Int32)0x20);
                    bw.Write((Int32)fInfo.dictData.Length);
                    bw.Write((Int32)compressedsize);
                    bw.Write((Int32)wndLen);
                    bw.Write((Int32)fInfo.t_length);
                    bw.Write((Int32)positions.Length / 4);
                    bw.Write((Int32)positions.Length);
                    bw.Write((Int32)decLen);
                }
                dst = ms.ToArray();
            }
        }
    }

}