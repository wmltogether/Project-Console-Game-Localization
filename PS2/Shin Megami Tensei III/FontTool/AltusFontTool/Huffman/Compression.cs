using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.IO;
using AltusFontTool;

namespace Huffman
{
    public class Compression
    {

        public static int[,] ReadDict(byte[] dictData)
        {
            int Dictionary_Size = dictData.Length;
            int[,] Dict = new int[Dictionary_Size / 6, 2];
            using (MemoryStream ms = new MemoryStream(dictData))
            {
                using (BinaryReader br = new BinaryReader(ms))
                {
                    for (int i = 0; i < Dictionary_Size / 6; i++)
                    {
                        ms.Position = ms.Position + 2;
                        Dict[i, 0] = br.ReadInt16();
                        Dict[i, 1] = br.ReadInt16();
                    }
                }
            }
            return Dict;

        }
        public static void Decompress(byte[] input, byte[] dictData, out byte[] output)
        {
            int[,] huffmanDictionary = ReadDict(dictData);
            int CompressedFontBlock_Size = input.Length;
            output = null;
            using (MemoryStream fondec = new MemoryStream())
            {
                using (MemoryStream ms = new MemoryStream(input))
                {
                    using (BinaryReader br = new BinaryReader(ms))
                    {
                        ms.Seek(0, SeekOrigin.Begin);
                        int temp = 0;
                        for (int k = 0; k < CompressedFontBlock_Size; k += 2)
                        {
                            int s4 = br.ReadInt16();
                            for (int i = 0; i < 16; i++)
                            {
                                temp = huffmanDictionary[temp, s4 % 2];
                                s4 = s4 >> 1;

                                if (huffmanDictionary[temp, 0] == 0)
                                {

                                    fondec.WriteByte((byte)(huffmanDictionary[temp, 1]));
                                    temp = 0;
                                }
                            }
                        }
                    }
                }
                output = fondec.ToArray();
            }
            
        }
        public static int WriteGlyphPosition(MemoryStream Font, int[,] Dictionary, PersonaFont.FontInfo fInfo, out byte[] positions)
        {
            List<int> GlyphNewPosition = new List<int>();
            positions = null;
            int size = fInfo.t_length;
            int temp = 0;
            bool boolean = true;
            int a = 0;
            int b = 0;
            int last = 0;
            Font.Seek(0, SeekOrigin.Begin);
            do
            {
                if (Font.Position == Font.Length)
                {
                    boolean = false;
                }

                else
                {
                    int s4 = Font.ReadUshort();
                    a++;
                    for (int i = 0; i < 16; i++)
                    {
                        temp = Dictionary[temp, s4 % 2];
                        s4 = s4 >> 1;

                        if (Dictionary[temp, 0] == 0)
                        {
                            if (b % size == 0)
                            {
                                GlyphNewPosition.Add((((a - 1) * 2) << 3) + i);
                            }
                            b++;
                            temp = 0;
                        }
                    }
                }

            } while (boolean);
            using (MemoryStream ms = new MemoryStream())
            {
                for (int i = 0; i < GlyphNewPosition.Count; i++)
                {
                    last = GlyphNewPosition[i];
                    ms.WriteInt(GlyphNewPosition[i]);
                }

                positions = ms.ToArray();
            }

            return last;

        }

        public static void Compress(byte[] input, byte[] dictData, out byte[] output)
        {
            output = null;
            byte[] cc = null;
            int[,] Dictionary = ReadDict(dictData);
            #region com1
            using (MemoryStream ms = new MemoryStream(input))
            {
                using (BinaryReader br = new BinaryReader(ms))
                {
                    MemoryStream zz = new MemoryStream();
                    bool boolean = true;
                    long position = 0;
                    int DictPart = FindDictPart(Dictionary);
                    while (boolean)
                    {
                        position = ms.Position;
                        if (position == input.Length) boolean = false;
                        else
                        {
                            int s4 = ms.ReadByte();
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
                                v0 = FindDictIndex(v0, Dictionary, DictPart, ref zz);
                            }
                        }
                    }
                    cc = zz.ToArray();
                    zz.Close();
                }


            }
            #endregion
            MemoryStream dst = new MemoryStream();
            MemoryStream FONT_COMPRESS = new MemoryStream(cc);
            FONT_COMPRESS.Seek(0, SeekOrigin.End);
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
                dst.WriteByte(Convert.ToByte(str, 2));
            } while (FONT_COMPRESS.Position != 0);
            if (dst.Position%2 != 0){
                dst.WriteByte((byte)0);
            }
            FONT_COMPRESS.Close();
            output = dst.ToArray();
            dst.Close();

        }

        public static int FindDictPart(int[,] Dict)
        {
            for (int i = 1; i < Dict.Length / 2; i++)
            {
                if (Dict[i, 1] == 0)
                {
                    return i;
                }
            }
            return -1;
        }

        public static int FindDictIndex(int v0 , int[,] Dictionary, int DictPart, ref MemoryStream FONT_COMPRESS)
        {
            if (Dictionary[0, 0] == v0)
            {
                FONT_COMPRESS.WriteByte(0);
                return 0;
            }
            else if (Dictionary[0, 1] == v0)
            {
                FONT_COMPRESS.WriteByte(1);
                return 0;
            }

            for (int i = DictPart + 1; i < Dictionary.Length / 2; i++)
            {
                if (Dictionary[i, 0] == v0)
                {
                    FONT_COMPRESS.WriteByte(0);
                    return i;
                }
                else if (Dictionary[i, 1] == v0)
                {
                    FONT_COMPRESS.WriteByte(1);
                    return i;
                }
            }
            return -1;
        }

    }
}
