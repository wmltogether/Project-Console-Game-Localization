using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using psp_gxm;
using Core.IO;
using System.IO;
using System.Drawing;

namespace g1ttool
{

    public class G1T
    {
        public TextureInfo textureInfo = new TextureInfo();
        public Bitmap[] texture_bmps;
        public List<byte[]> output_pixeldata;
        public G1T(byte[] Data)
        {
            //GT1G is little endian
            //G1TG is big endian
            EndianBinaryReader br = new EndianBinaryReader(new MemoryStream(Data), Endian.LittleEndian);
            textureInfo.Magic = br.ReadStrings(4);//Get Magic
            textureInfo.Version = br.ReadStrings(4);//Get Version
            textureInfo.Size = br.ReadUInt32();
            textureInfo.HeaderSize = br.ReadUInt32();//Get HeaderSize
            textureInfo.texture_nums = br.ReadUInt32();
            br.BaseStream.Seek(textureInfo.HeaderSize, SeekOrigin.Begin);
            texture_bmps = new Bitmap[textureInfo.texture_nums];
            output_pixeldata = new List<byte[]>();
            textureInfo.p_offsets = Struct.Unpack(string.Format("<{0}I", textureInfo.texture_nums), br.ReadBytes((int)textureInfo.texture_nums * 4));

            br.BaseStream.Seek(textureInfo.HeaderSize + textureInfo.texture_nums * 4, SeekOrigin.Begin);
            for (int i = 0; i < textureInfo.texture_nums; i++)
            {
                br.BaseStream.Seek(textureInfo.p_offsets[i] + textureInfo.HeaderSize, 0);
                g1tTexture texture = new g1tTexture(br);
                textureInfo.p_offsets[i] = texture.position;
                if (texture.textureFormat == PixelDataFormat.FormatDXT5)
                {
                    TextureConv tc = new TextureConv();
                    byte[] output;
                    Bitmap bm = tc.GetDXT5Bitmap(texture.Data, texture.Width, texture.Height ,out output , true);
                    texture_bmps[i] = bm;
                    output_pixeldata.Add(output);
                }
            }




        }

        public class TextureInfo
        {
            /* 0x38 headers*/
            public String Magic;
            public String Version;
            public UInt32 Size;
            public UInt32 HeaderSize;
            public UInt32 texture_nums;
            public UInt32 unk;

            public dynamic[] p_offsets;
            public List<g1tTexture> textures;


        }

        public class g1tTexture
        {
            private byte[] header;
            private int mipmap;
            private int format;
            private int wh;
            private int unk4;
            private int unk5;
            private int unk6;
            private int unk7;

            public int Width;
            public int Height;
            public int MipmapCount;
            public int BitPerPixel = 0;
            public byte[] Data;
            public int position;
            public PixelDataFormat textureFormat;
            public g1tTexture(EndianBinaryReader br)
            {
                header = br.ReadBytes(8);
                mipmap = header[0];
                format = header[1];
                wh = header[2];
                unk4 = header[4];
                unk5 = header[5];
                unk6 = header[6];
                unk7 = header[7];
                if (br.Endianness == Endian.LittleEndian)
                {
                    mipmap = (int)IOMath.Swap4byte((byte)mipmap);
                    format = (int)IOMath.Swap4byte((byte)format);
                    wh = (int)IOMath.Swap4byte((byte)wh);
                    unk4 = (int)IOMath.Swap4byte((byte)unk4);
                    unk5 = (int)IOMath.Swap4byte((byte)unk5);
                    unk6 = (int)IOMath.Swap4byte((byte)unk6);
                    unk7 = (int)IOMath.Swap4byte((byte)unk7);
                }
                MipmapCount = (int)mipmap;
                switch (format)
                {
                    case 0x21:
                        // DXT5 swizzled from PSVITA 影牢(Deception) is 0x21 
                        textureFormat = PixelDataFormat.FormatDXT5;
                        BitPerPixel = 8;
                        break;
                    default:
                        throw new Exception("unknown g1t texture format");
                }
                Width = (1 << (wh >> 4));
                Height = (1 << (wh & 0xf));
                if (unk7 == 1)
                {
                    br.ReadBytes(0xc);
                }
                position = (int)br.BaseStream.Position;
                Data = br.ReadBytes(BitPerPixel / 8 * Width * Height);

            }
        }
    }
}
