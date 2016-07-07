using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Drawing.Imaging;
using System.Drawing;
using System.Reflection;
using System.Runtime.InteropServices;
using System.IO;

namespace FontCreator
{
    /* seg000:08B36150                 lhu     $s0, 0($a2)      # 句子地址，读编码  这里可以断点，修改句子
     * seg000:08B365C8                 lhu     $a2, 0($s5)      # 字符在字库表中索引
     * seg000:08B365CC                 divu    $a2, $a1         # a2/900, 每个字库图是30*30个字符
     * 编码从0000开始，每17x17 后 编码+1，076c=雹 是原版最后一个汉字，0x76d开始为按钮图标，需要保留位置，字库纹理是个512 * 1144的swizzled texture，32x8 4bpp
     * 每个字符宽度是17像素，每页512x512（30x30字），达到512后，y值对齐到512重新结算（就是+=2）
     * CLUT调色板在GE调试器中可以STEP到CLUT: 0x08c3a4a0 (3)
     * 为了接近原始的字库内存排列，texture不要超过3张512x512
     * 
     * usage:
     * charlist.txt中只需要放入汉字，生成的00000016.font在Import目录中
     */

    class Program
    {
        public static string ReadFromFile(string fName)
        {
            string str = System.IO.File.ReadAllText(fName,
                EncodingType.GetType(fName));
            string base_str = " !\"#$%　'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[＼]^_`abcdefghijklmnopqrstuvwxyz{|}~、。，．·：？！々ーー－／～…‘’“”（）［］「」『』【】＋－×＜＞％＆○□△※→←↑↓０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ";
            str = str.Replace("\r", "");
            str = str.Replace("\n", "");
            str = str.Replace("\t", "");
            return base_str + str;
        }
        /// <summary>
        /// 根据中文的t3bfont class 创建0000016.font
        /// </summary>
        /// <param name="t3bFont">T3BFont Class</param>
        /// <param name="dstName">output name</param>
        public static void MakeFontBinary(T3BFont t3bFont, string dstName){
            using (FileStream fs = File.Create(dstName))
            {
                using (BinaryWriter sw = new BinaryWriter(fs))
                {
                    sw.Write((uint)0x6b636170);//add header "pack"
                    sw.Write((uint)0x2);
                    sw.Write((uint)0x0);
                    sw.Write((uint)0x0);
                    sw.Write((uint)0x0);
                    sw.Write((uint)0x0);
                    sw.Write((uint)0x0);
                    sw.Write((uint)0x0);
                    long tmp_pos0 = sw.BaseStream.Position;

                    sw.Write((uint)t3bFont.texture_width);
                    sw.Write((uint)t3bFont.max_tiles);
                    sw.Write((uint)t3bFont.item_width);
                    sw.Write((uint)t3bFont.unk0);
                    sw.Write((uint)t3bFont.unk1);
                    sw.Write((uint)t3bFont.unk2);
                    sw.Write((uint)t3bFont.button_tile_id);
                    sw.Write((uint)t3bFont.unk3);
                    TextureEncoder texEncoder = new TextureEncoder();
                    Console.WriteLine("Creating Palette");
                    List<Color> paletteList = texEncoder.getPaletteData(File.ReadAllBytes("Font/font_pal.bin"));
                    Console.WriteLine("Creating 4BPP BMDATA");
                    byte[] bmdata = texEncoder.create4Bpp(t3bFont.bitmap , 32,8,paletteList ,EndianType.BIG);
                    Console.WriteLine("Writing BMDATA");
                    sw.Write(bmdata);
                    long tmp_pos1 = sw.BaseStream.Position;
                    Console.WriteLine("Writing CHAR INFO");
                    foreach (var value in t3bFont.charvalues)
                    {
                        sw.Write((byte)value);
                    }
                    long tmp_pos2 = sw.BaseStream.Position;

                    sw.BaseStream.Seek(0x8, SeekOrigin.Begin);
                    sw.Write((uint)(tmp_pos1 - tmp_pos0));
                    sw.Write((uint)tmp_pos0);
                    sw.Write((uint)(tmp_pos2 - tmp_pos1));
                    sw.Write((uint)tmp_pos1);

                }
            }
        }
        public static void MakeTbl(List<string> tbl ,string dstName)
        {
            using (FileStream fs = File.Create(dstName))
            {
                using (StreamWriter sw = new StreamWriter(fs , Encoding.Unicode))
                {
                    foreach (string var in tbl){
                        sw.WriteLine(var);
                    }
                }
            }
        }
        public static void MakeFontBitmap(string fName, string dstName)
        {
            BMFont bmfont = new BMFont();
            char[] strings = ReadFromFile(fName).ToCharArray();
            T3BFont t3bFont = bmfont.DrawT3BFontBitmap(strings);
            t3bFont.bitmap.Save(dstName);
            MakeTbl(t3bFont.tbl, "dst.tbl");
            MakeFontBinary(t3bFont, "import/00000016.font");
            Console.WriteLine("Compress Done.");
            
        }

        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern bool SetDllDirectory(string path);

        static void Main(string[] args)
        {
            //根据系统环境选择合适的freetype6.dll
            //这个程序无法使用.net 4.5编译，否则会无法正常找到freetype6.dll
            int p = (int)Environment.OSVersion.Platform;
            if (p != 4 && p != 6 && p != 128)
            {
                //Thanks StackOverflow! http://stackoverflow.com/a/2594135/1122135
                string path = System.IO.Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
                path = System.IO.Path.Combine(path, IntPtr.Size == 8 ? "x64" : "x86");
                if (!SetDllDirectory(path))
                    throw new System.ComponentModel.Win32Exception();
                Console.WriteLine(path);
            }
            Console.WriteLine("T3B Font Creator: http://github.com/wmltogether");
            MakeFontBitmap("charlist.txt", "dst.png");
            Console.WriteLine("按任意键继续");
            Console.ReadKey();

        }
    }
}
