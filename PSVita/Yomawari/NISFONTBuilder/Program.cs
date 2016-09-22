using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using SharpFont;
using System.Drawing.Imaging;
using System.Drawing;
using System.Reflection;
using System.Runtime.InteropServices;
using System.IO;
using FreeImageAPI;

namespace NISFONTBuilder
{
    public static class Config
    {
        public static string baseName = Environment.GetFolderPath(Environment.SpecialFolder.Windows) + "\\Fonts\\msgothic.ttc";
        public static int fontWidth = 28;
        public static int fontHeight = 28;
        public static int fontSize = 36;
        public static string ttfName = "font.ttf";
        public static int texture_width = 1024;
        public static int texture_height = 1024;
        public static uint unk0 = 0;
        public static uint unk1 = 0;
        public static uint unk2 = 0;
        public static uint unk3 = 0;


    }
    class Program
    {
        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern bool SetDllDirectory(string path);
        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern long WritePrivateProfileString(string section, string key,
            string val, string filePath);
        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern long GetPrivateProfileString(string section, string key,
            string def, StringBuilder retVal, int size, string filePath);

        public static byte[] MakeFrm(List<XYWH> charvalues)
        {
            byte[] data;
            string magic = "nismultifontfrm\0";
            string end = "nis uti chu eoc ";
            using (MemoryStream ms = new MemoryStream())
            {
                using (BinaryWriter sw = new BinaryWriter(ms))
                {
                    sw.Write(magic.ToCharArray());
                    sw.Write((int)0);
                    sw.Write((int)(charvalues.Count * 8 + 0x8));
                    sw.Write((int)(charvalues.Count * 8 + 0x8));
                    sw.Write((int)0);
                    sw.Write((byte)0);
                    sw.Write((byte)Config.fontWidth);
                    sw.Write((byte)Config.fontHeight);
                    sw.Write((byte)0);
                    sw.Write((Int16)Config.fontHeight);
                    sw.Write((Int16)(charvalues.Count));
                    foreach (XYWH v in charvalues)
                    {
                        sw.Write((Int16)v.x);
                        sw.Write((Int16)v.y);
                        sw.Write((Int16)v.char_id);
                        sw.Write((Int16)0);
                    }
                    sw.Write(end.ToCharArray());
                    sw.Write((Int32)Config.unk0);
                    sw.Write((Int32)Config.unk1);
                    sw.Write((Int32)Config.unk2);
                    sw.Write((Int32)Config.unk3);
                    sw.Close();

                }
                data = ms.ToArray();
            }
            
            return data;
        }

        [System.Security.Permissions.SecurityPermission(
        System.Security.Permissions.SecurityAction.LinkDemand, Flags =
        System.Security.Permissions.SecurityPermissionFlag.UnmanagedCode)]
        public static void MakeFontFromCSV(string fName)
        {

            BMFont bmfont = new BMFont();
            string[] lines = System.IO.File.ReadAllLines(fName,
                EncodingType.GetType(fName));
            foreach (string line in lines)
            {
                if (line.IndexOf("//") == 0) continue;
                if (line.Contains(","))
                {
                    string c_line = line.Replace("\n", "");
                    c_line = c_line.Replace("\r", "");
                    string[] par = c_line.Split(',');
                    string _fontName = par[0];
                    string _ttfName = par[1];
                    string _charmap = par[2];
                    int _fontWidth = Convert.ToInt16(par[3]);
                    int _fontHeight = Convert.ToInt16(par[4]);
                    int _fontSize = Convert.ToInt16(par[5]);
                    
                    string chars = ReadFromFile(_charmap);
                    int _texture_width = 1024;
                    int a2 = _texture_width / _fontWidth;
                    int t1 = chars.Length / a2;
                    int t2 = chars.Length % a2;
                    int _texture_height = t1 * _fontHeight;
                    if (t2  > 0)
                    {
                        _texture_height += _fontHeight;
                    }
                    if (_texture_height%256 != 0)
                    {
                        _texture_height = _texture_height + (256 - _texture_height%256);
                    }
                    Config.fontWidth = _fontWidth;
                    Config.fontHeight = _fontHeight;
                    Config.fontSize = _fontSize;
                    Config.ttfName = _ttfName;
                    Config.texture_width = _texture_width;
                    Config.texture_height = _texture_height;
                    Config.unk0 = Convert.ToUInt32(par[6], 16);
                    Config.unk1 = Convert.ToUInt32(par[7], 16);
                    Config.unk2 = Convert.ToUInt32(par[8], 16);
                    Config.unk3 = Convert.ToUInt32(par[9], 16);
                    if (File.Exists(_ttfName))
                    {
                        Console.WriteLine("Gen NIS font...\n_fontName:{0},{1},{2},{3},{4}:{5}x{6}", 
                                            _fontName,
                                            _ttfName,
                                            _charmap,
                                            _fontHeight,
                                            chars.Length,
                                            _texture_width,
                                            _texture_height);
                        
                        NISFont fnt_data =  bmfont.DrawT3BFontBitmap(chars.ToCharArray());
                        if (!Directory.Exists("import"))
                        {
                            Directory.CreateDirectory("import");
                        }
                        using (Graphics g = Graphics.FromImage(fnt_data.bitmap))
                        {
                            IntPtr hdc = g.GetHdc();
                            string dst_imgname = string.Format("import//{0}.tga", _fontName);
                            string dst_nmfname = string.Format("import//{0}.nmf", _fontName);
                            FIBITMAP fBitmap = FreeImage.CreateFromHbitmap(fnt_data.bitmap.GetHbitmap(),
                                                                           hdc
                                                                           );
                            if (File.Exists(dst_imgname))
                            {
                                File.Delete(dst_imgname);
                            }
                            FreeImage.SaveEx(fBitmap, dst_imgname);

                            byte[] dst_data = MakeFrm(fnt_data.charvalues);
                            File.WriteAllBytes(dst_nmfname, dst_data);
                        }
                    }
                }
            }

        }

        public static RGBQUAD[] GetL8Palette()
        {
            RGBQUAD[] quad = new RGBQUAD[256];
            for (int i = 0; i < 256; i++)
            {
                quad[i] = Color.FromArgb(i , 255,255,255);
            }
            return quad;
        }

        public static byte[] GetL8Transparency()
        {
            byte[] transparency = new byte[256];
            for (int i = 0; i < 256; i++)
            {
                transparency[i] = (byte)i;
            }
            return transparency;
        }

        private static uint uchar2code(string current_char)
        {
            uint ucode = (uint)Char.ConvertToUtf32(current_char, 0);
            return ucode;
        }

        private static string code2uchar(uint code)
        {
            string chr = "";
            chr = Char.ConvertFromUtf32((int)code);
            return chr;
        }
        public static string ReadFromFile(string fName)
        {
            if (!File.Exists(fName))
            {
                return "";
            }
            string str = System.IO.File.ReadAllText(fName,
                EncodingType.GetType(fName));
            string base_str = " !\"#$%　'()*+,-./0123456789:;<=>?@ABCDEFGHIJKLMNOPQRSTUVWXYZ[＼]^_`abcdefghijklmnopqrstuvwxyz{|}~、。，．·：？！々ーー－／～…‘’“”（）［］「」『』【】＋－×＜＞％＆○□△※→←↑↓０１２３４５６７８９ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺａｂｃｄｅｆｇｈｉｊｋｌｍｎｏｐｑｒｓｔｕｖｗｘｙｚ";
            str = str.Replace("\r", "");
            str = str.Replace("\n", "");
            str = str.Replace("\t", "");
            char[] m_strs = (base_str + str).ToCharArray();
            List<uint> slist = new List<uint>();
            foreach (var chr in m_strs)
            {
                uint charid = uchar2code(chr.ToString());
                if (!slist.Contains(charid))
                {
                    slist.Add(charid);
                }
            }
            slist.Sort();
            string dst = "";
            foreach (var code in slist )
            {
                dst += code2uchar(code);
            }
            return dst;
        }



        static void Main(string[] args)
        {
            int p = (int)Environment.OSVersion.Platform;
            if (p != 4 && p != 6 && p != 128)
            {
                //Thanks StackOverflow! http://stackoverflow.com/a/2594135/1122135
                string path = System.IO.Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
                path = System.IO.Path.Combine(path, IntPtr.Size == 8 ? "x64" : "x86");
                if (!SetDllDirectory(path))
                    throw new System.ComponentModel.Win32Exception();
                Console.WriteLine(path);
                Console.WriteLine("Nippon ichi multi Font Creator: http://github.com/wmltogether");
                MakeFontFromCSV("font.csv");
                Console.WriteLine("Press Any Key to exit");
                Console.ReadKey();

            }
        }
    }
}
