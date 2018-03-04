using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using SharpFont;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;


namespace AltusFontTool
{
    public class BMFont
    {

        static Dictionary<string, string> charConstDictionary = new Dictionary<string, string>()
        {
            #region ASCII_CHARS

            {"０","0"},
            {"１", "1"},
            {"２", "2"},
            {"３", "3"},
            {"４", "4"},
            {"５", "5"},
            {"６", "6"},
            {"７", "7"},
            {"８", "8"},
            {"９", "9"},
            {"Ａ", "A"},
            {"Ｂ", "B"},
            {"Ｃ", "C"},
            {"Ｄ", "D"},
            {"Ｅ", "E"},
            {"Ｆ", "F"},
            {"Ｇ", "G"},
            {"Ｈ", "H"},
            {"Ｉ", "I"},
            {"Ｊ", "J"},
            {"Ｋ", "K"},
            {"Ｌ", "L"},
            {"Ｍ", "M"},
            {"Ｎ", "N"},
            {"Ｏ", "O"},
            {"Ｐ", "P"},
            {"Ｑ", "Q"},
            {"Ｒ", "R"},
            {"Ｓ", "S"},
            {"Ｔ", "T"},
            {"Ｕ", "U"},
            {"Ｖ", "V"},
            {"Ｗ", "W"},
            {"Ｘ", "X"},
            {"Ｙ", "Y"},
            {"Ｚ", "Z"},
            {"ａ", "a"},
            {"ｂ", "b"},
            {"ｃ", "c"},
            {"ｄ", "d"},
            {"ｅ", "e"},
            {"ｆ", "f"},
            {"ｇ", "g"},
            {"ｈ", "h"},
            {"ｉ", "i"},
            {"ｊ", "j"},
            {"ｋ", "k"},
            {"ｌ", "l"},
            {"ｍ", "m"},
            {"ｎ", "n"},
            {"ｏ", "o"},
            {"ｐ", "p"},
            {"ｑ", "q"},
            {"ｒ", "r"},
            {"ｓ", "s"},
            {"ｔ", "t"},
            {"ｕ", "u"},
            {"ｖ", "v"},
            {"ｗ", "w"},
            {"ｘ", "x"},
            {"ｙ", "y"},
            {"ｚ", "z"}

            #endregion
            
        };

        static uint uchar2code(string current_char)
        {
            uint ucode = (uint)Char.ConvertToUtf32(current_char, 0);
            return ucode;
        }
        public static List<PFontGlyph> GetGlyphs(string charlist, string ttfName, int width, int height, float scaleRatio)
        {
            StreamWriter sw = new StreamWriter(File.Create("ch.tbl"), System.Text.Encoding.Unicode);
            List<PFontGlyph> glyphs = new List<PFontGlyph>();
            int base_id = 0x8080;
            string currentChar = "";
            Bitmap glyphBitmap;
            PFontGlyph pfontGlyph = null;
            for (int i = 0; i < charlist.Length; i++)
            {
                currentChar = charlist[i].ToString();
                bool hasGlyph = DrawBitmap(currentChar, width, height, ttfName, scaleRatio, out glyphBitmap);
                if (hasGlyph == false)
                {
                    DrawBitmapFallback(currentChar, width, height, scaleRatio, out glyphBitmap);
                }
                int left = 0;
                int right = 0;
                if ((base_id + i)%0x100 == 0)
                {
                    base_id += 0x80;
                }
                int char_id = base_id + i;
                CheckPoints(glyphBitmap, out left, out right);
                //如果是逗号和句号，强制设定字符宽度为18
                if (currentChar.Equals("，") || currentChar.Equals("。"))
                {
                    left = 1;
                    right = (int) ((float)height * 0.75f);
                }
                pfontGlyph = new PFontGlyph(i, base_id , left, right, glyphBitmap);
                glyphs.Add(pfontGlyph);

                sw.Write(string.Format("{0:x4}={1}\r\n", char_id, charlist[i].ToString()));
            }
            sw.Close();
            return glyphs;
        }

        private static void CheckPoints(Bitmap bmp, out int left, out int right)
        {
            left = 0;
            right = 0;
            int tmpRT = -1;
            int tmpLT = -1;
            int v = 0;
            int[] m = new int[bmp.Width];
            Color col = Color.Black;
            for (int y = 0; y < bmp.Height; y++)
            {
                tmpLT = 0;
                tmpRT = 0;
                m = new int[bmp.Width];
                for (int x = 0; x < bmp.Width; x++)
                {
                    col = bmp.GetPixel(x, y);
                    if (col.A > 0)
                    {
                        m[x] = 1;
                    }
                    else
                    {
                        m[x] = 0;
                    }
                }
                for (int i=0;i< m.Length; i++)
                {
                    v = m[i];
                    if ((v == 1) && (tmpLT == -1))
                    {
                        tmpLT = i;
                    }
                    if ((v == 1) && (tmpLT >= 0))
                    {
                        tmpRT = i;
                    }
                }

                if (left < tmpLT) left = tmpLT;
                if (right < tmpRT) right = tmpRT;
            }

        }

        public static void DrawBitmapFallback(string currentChar0, int width, int height,
            float scaleRatio, out Bitmap bmp)
        {
            string ttfName = PersonaFont.TTF_FALLBACK;
            DrawBitmap(currentChar0, width, height, ttfName, scaleRatio, out bmp);
        }


        public static bool DrawBitmap(string currentChar0, int width, int height, string ttfName, float scaleRatio, out Bitmap bmp)
        {
            if (charConstDictionary.ContainsKey(currentChar0))
            {
                currentChar0 = charConstDictionary[currentChar0];
            }

            bmp = new Bitmap(width, height);
            Graphics g = Graphics.FromImage(bmp);
            g.Clear(Color.Transparent);
            //设定字体信息
            int font_height = (int)Math.Round((float)height * 3f / 4f * scaleRatio);
            int relativePositionX = 0;
            int relativePositionY = 0;
            string fontName = ttfName;

            Library library = new Library();
            Face face = library.NewFace(fontName, 0);
            face.SetCharSize(0, font_height, 0, 96);

            face.SetPixelSizes((uint)0, (uint)font_height);
            uint glyphIndex = face.GetCharIndex(uchar2code(currentChar0));
            face.LoadGlyph(glyphIndex, LoadFlags.Default, LoadTarget.Lcd);
            face.Glyph.RenderGlyph(RenderMode.Normal);
            float left = (float)face.Glyph.Metrics.HorizontalBearingX;
            float right = (float)face.Glyph.Metrics.HorizontalBearingX + (float)face.Glyph.Metrics.Width;
            float top = (float)face.Glyph.Metrics.HorizontalBearingY;
            float bottom = (float)face.Glyph.Metrics.HorizontalBearingY + (float)face.Glyph.Metrics.Height;
            
            int FHD = (int)Math.Ceiling((float)font_height);

            int kx = (int)Math.Round(left);
            int ky = (int)Math.Round((float)0 + (FHD - top));
            Bitmap dBmp;
            FTBitmap ftbmp = face.Glyph.Bitmap;

            bool hasGlyph = false ;
            if (ftbmp.Width == 0)
            {
                dBmp = new Bitmap(width, width);
            }
            else
            {
                dBmp = ftbmp.ToGdipBitmap(Color.FromArgb(255, 0, 0, 255));//描边
                hasGlyph = true;
            }
            g.DrawImageUnscaled(dBmp, kx + relativePositionX - 1, ky + relativePositionY);
            g.DrawImageUnscaled(dBmp, kx + relativePositionX + 1, ky + relativePositionY);
            g.DrawImageUnscaled(dBmp, kx + relativePositionX, ky + relativePositionY - 1);
            g.DrawImageUnscaled(dBmp, kx + relativePositionX, ky + relativePositionY + 1);
            dBmp.Dispose();
            if (hasGlyph)
            {
                FTBitmap ftbmp2 = face.Glyph.Bitmap;
                Bitmap cBmp = ftbmp2.ToGdipBitmap(Color.FromArgb(255, 0xf0, 0xf0, 0xf0));//实色
                g.DrawImageUnscaled(cBmp, kx + relativePositionX, ky + relativePositionY);
                g.DrawImageUnscaled(cBmp, kx + relativePositionX, ky + relativePositionY);
                cBmp.Dispose();
            }

            g.Dispose();
            return hasGlyph;

        }
    }

    public class PFontGlyph
    {
        public int id;
        public int char_id;
        public int left;
        public int right;
        public Bitmap bitmap;

        public PFontGlyph(int _id, int _char_id, int _left, int _right, Bitmap _bitmap)
        {
            id = _id;
            char_id = _char_id;
            left = _left;
            right = _right;
            bitmap = _bitmap;
        }
    }
}
