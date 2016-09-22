using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using SharpFont;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;


namespace NISFONTBuilder
{
    public class Table
    {
        public XYWH[] XYWHS;
        public struct XYWH
        {
            public uint charid;
            public uint x_pos;
            public uint y_pos;
            public uint c_width;
            public uint c_height;
            public uint page_num;

        }
    }
    public static class ImageDraw
    {
        public static Bitmap kPasteImage(Bitmap bmp, int newW, int newH, int kx, int ky)
        {
            try
            {
                Bitmap b = new Bitmap(newW, newH);
                Graphics g = Graphics.FromImage(b);

                g.DrawImageUnscaled(bmp, kx, ky);
                g.Dispose();

                return b;
            }
            catch
            {
                return null;
            }
        }
        public static Bitmap kResizeImage(Bitmap bmp, int newW, int newH, System.Drawing.Drawing2D.InterpolationMode currnetMode)
        {
            //插值缩放算法
            try
            {
                Bitmap b = new Bitmap(newW, newH);
                Graphics g = Graphics.FromImage(b);

                // 插值算法的质量
                //g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.Bilinear;
                g.InterpolationMode = currnetMode;

                g.DrawImage(bmp, new Rectangle(0, 0, newW, newH), new Rectangle(0, 0, bmp.Width, bmp.Height), GraphicsUnit.Pixel);
                g.Dispose();

                return b;
            }
            catch
            {
                return null;
            }
        }

    }

    class BMFont : TextureEncoder
    {
        uint uchar2code(string current_char)
        {
            uint ucode = (uint)Char.ConvertToUtf32(current_char, 0);
            return ucode;
        }

        public Bitmap gray2alpha(Bitmap cBmp)
        {
            Bitmap nBmp = new Bitmap((int)cBmp.Width, (int)cBmp.Height);
            Color color;
            Color colorResult;
            for (int i = 0; i < cBmp.Width; i++)
            {
                for (int j = 0; j < cBmp.Height; j++)
                {

                    color = cBmp.GetPixel(i, j);
                    int maxcolor = Math.Max(Math.Max(color.R, color.G), color.B);
                    if (!(color.A == 255))
                    {

                        maxcolor = color.A;
                    }

                    colorResult = Color.FromArgb(maxcolor, maxcolor, maxcolor, maxcolor);
                    nBmp.SetPixel(i, j, colorResult);

                }
            }

            return nBmp;
        }

        public NISFont DrawT3BFontBitmap(char[] strings)
        {
            NISFont fnt_data = new NISFont();
            Bitmap bmp = new Bitmap(Config.texture_width , Config.texture_height);
            Graphics g = Graphics.FromImage(bmp);
            g.Clear(Color.FromArgb(0x00000000));
            int x = 0, y = 0;
            int tile_w = Config.fontWidth;
            int tile_h = Config.fontHeight;
            int relativePositionX = 1;
            int relativePositionY = -2;
            int font_height = Config.fontSize;
            Library library = new Library();
            string facename = Config.ttfName;
            Face face = library.NewFace(facename, 0);
            float left, right, top, bottom, FHT;
            int FHD, kx, ky;
            
            foreach (char currentChar0 in strings)
            {
                uint charid = uchar2code(currentChar0.ToString());
                face.SetCharSize(0, font_height, 0, 72);
                if (charid < 0x7f)
                {
                    font_height = Config.fontSize - 2;
                    face.SetCharSize(0, font_height, 0, 72);
                }
                else
                {
                    font_height = Config.fontSize;
                }
                face.SetPixelSizes((uint)0, (uint)font_height);

                uint glyphIndex = face.GetCharIndex(charid);

                //Console.WriteLine(glyphIndex);
                face.LoadGlyph(glyphIndex, LoadFlags.Default, LoadTarget.Lcd);
                face.Glyph.Outline.Embolden(0.5);
                face.Glyph.RenderGlyph(RenderMode.Normal);

                FTBitmap ftbmp = face.Glyph.Bitmap;
                FTBitmap ftbmp2 = face.Glyph.Bitmap;
                
                left = (float)face.Glyph.Metrics.HorizontalBearingX;
                right = (float)face.Glyph.Metrics.HorizontalBearingX + (float)face.Glyph.Metrics.Width;
                top = (float)face.Glyph.Metrics.HorizontalBearingY;
                bottom = (float)face.Glyph.Metrics.HorizontalBearingY + (float)face.Glyph.Metrics.Height;

                FHT = font_height;
                FHD = (int)Math.Ceiling(FHT);
                kx = x + (int)Math.Round(left);
                ky = (int)Math.Round((float)y + (float)Math.Ceiling(FHT) - (float)top);


                if (ftbmp.Width == 0 || glyphIndex < 0x20)
                {
                    Face face1 = library.NewFace(Config.baseName, 0);
                    face1.SetCharSize(0, font_height, 0, 72);
                    face1.SetPixelSizes((uint)0, (uint)font_height);
                    glyphIndex = face1.GetCharIndex(charid);
                    face1.LoadGlyph(glyphIndex, LoadFlags.Default, LoadTarget.Lcd);
                    face1.Glyph.Outline.Embolden(Fixed26Dot6.FromDouble(0.4));
                    face1.Glyph.RenderGlyph(RenderMode.Normal);

                    left = (float)face1.Glyph.Metrics.HorizontalBearingX;
                    right = (float)face1.Glyph.Metrics.HorizontalBearingX + (float)face1.Glyph.Metrics.Width;
                    top = (float)face1.Glyph.Metrics.HorizontalBearingY;
                    bottom = (float)face1.Glyph.Metrics.HorizontalBearingY + (float)face1.Glyph.Metrics.Height;

                    FHT = font_height;
                    FHD = (int)Math.Ceiling(FHT);
                    kx = x + (int)Math.Round(left);
                    ky = (int)Math.Round((float)y + (float)Math.Ceiling(FHT) - (float)top);
                    ftbmp = face1.Glyph.Bitmap;
                    ftbmp2 = face1.Glyph.Bitmap;


                }

                fnt_data.charvalues.Add(new XYWH((int)uchar2code(currentChar0.ToString()),
                                                   x,
                                                   y,
                                                   tile_w,
                                                   tile_h,
                                                   0));

                if (ftbmp2.Width == 0)
                {
                    x += tile_w;
                    if (x + tile_w > Config.texture_width)
                    {
                        x = 0;
                        y += tile_h;
                    }
                    continue;
                }
                Bitmap cBmp = ftbmp2.ToGdipBitmap(Color.White);
                g.DrawImageUnscaled(cBmp, kx + relativePositionX, ky + relativePositionY);
                g.DrawImageUnscaled(cBmp, kx + relativePositionX, ky + relativePositionY);
                cBmp.Dispose();

                

                x += tile_w;
                if (x + tile_w > Config.texture_width)
                {
                    x = 0;
                    y += tile_h;
                }


            }
            fnt_data.bitmap = bmp;
            return fnt_data;
        }
    }
}
