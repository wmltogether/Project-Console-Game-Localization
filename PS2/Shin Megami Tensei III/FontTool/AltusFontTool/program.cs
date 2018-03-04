using System;
using System.Collections.Generic;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text;
using System.IO;
using System.Drawing.Imaging;
using System.Drawing;
using System.Text.RegularExpressions;

namespace AltusFontTool
{
    class Program
    {
        public static string ReadFromFile(string fName, string baseTblName)
        {
            string str = System.IO.File.ReadAllText(fName,
                Encoding.Unicode);

            string[] lines = File.ReadAllLines(baseTblName, Encoding.Unicode);

            List<string> chars = new List<string>();
            foreach (string line in lines)
            {
                string[] spl = Regex.Split(line, "=");
                if (spl.Length > 1)
                {
                    string chrstr = spl[1].Replace("\r", "");
                    chrstr = chrstr.Replace("\n", "");
                    chrstr = chrstr.Replace("\t", "");
                    chars.Add(chrstr);
                }
            }

            foreach (char chr in str)
            {
                chars.Add(string.Format("{0}", chr));
                /*if (chars.Contains(string.Format("{0}", chr)))
                {
                }
                else
                {
                    chars.Add(string.Format("{0}", chr));
                }*/
            }
            return string.Join("", chars.ToArray());
        }

        [DllImport("kernel32.dll", CharSet = CharSet.Auto, SetLastError = true)]
        private static extern bool SetDllDirectory(string path);
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
                Console.WriteLine("真女神转生3 Font Creator: http://github.com/wmltogether");
                GetFontInfo("font0.fnt");
                MakeFont("charlist.txt", PersonaFont.TTF_SERIF, "font0_ch.fnt", 24, 1f);
                MakeFont("charlist.txt", PersonaFont.TTF_SERIF, "font1_ch.fnt", 24, 0.8f, 2400);
                MakeFont("charlist.txt", PersonaFont.TTF_SERIF, "name_ent_ch.fnt",24, 1f);
            }


        }

        private static void MakeFont(string charlistName, string ttfName, string dstName, int fontSize, float scaleRatio, int maxcharnums = -1)
        {
            
            string charlist =  ReadFromFile(charlistName, "base.TBL");
            if (maxcharnums != -1) {
                if (charlist.Length > maxcharnums) {
                    charlist = charlist.Substring(0, maxcharnums);
                }
            }
            PersonaFont font = new PersonaFont();
            PersonaFont.FontInfo fInfo = font.LoadFont("font0.fnt");

            fInfo.OverrideFontSize(fontSize);

            List<PFontGlyph> pglyphs = BMFont.GetGlyphs(charlist, ttfName, fontSize, fontSize, scaleRatio);
            byte[] dstFont;
            font.MakeFont(fInfo ,pglyphs, out dstFont);

            FileStream fs = File.Create(dstName);
            BinaryWriter bw = new BinaryWriter(fs);
            bw.Write(dstFont);
            bw.Close();
            fs.Close();
            /*TextureEncoder encoder = new TextureEncoder();
            FileStream fs = File.Create("test.bin");
            BinaryWriter bw = new BinaryWriter(fs);
            for (int i = 0; i < pglyphs.Count; i++)
            {
                PFontGlyph glyph = pglyphs[i];
                byte[] data = encoder.create4Bpp(glyph.bitmap, 24, 24, encoder.getPS2PaletteData(fInfo.palette_data), EndianType.BIG);
                bw.Write(data);
            }
            bw.Close();
            fs.Close();
            */

        }

        public static void GetFontInfo(string fname)
        {
            
        }
    }
}


