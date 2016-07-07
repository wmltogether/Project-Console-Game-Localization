using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using SharpFont;
using System.IO;
using System.Drawing;
using System.Drawing.Imaging;

namespace FontCreator
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

                    colorResult = Color.FromArgb(maxcolor, 255, 255, 255);
                    nBmp.SetPixel(i, j, colorResult);

                }
            }

            return nBmp;
        }

        public T3BFont DrawT3BFontBitmap(char[] strings)
        {
            T3BFont t3bFont = new T3BFont();

            #region font texture settings
            int texture_width = 512;
            int texture_height = 512;
            int font_height = 14;
            int tile_w = 17;
            int tile_h = 17;
            int swizzle_w = 32;
            int swizzle_h = 8;
            int a2 = texture_width / tile_w;
            string fontName = "Font/font.ttf";
            int relativePositionX = 1;
            int relativePositionY = -1;

            byte[] o_data = File.ReadAllBytes("Font/base.font");
            Bitmap _bm = new Bitmap("Font/base.png");
            Graphics base_grp = System.Drawing.Graphics.FromImage(_bm);
            #endregion
            Library library = new Library();
            Face face = library.NewFace(fontName, 0);
            int tmp_length = strings.Length;
            if (tmp_length <= 0x76d)
            {
                Console.WriteLine("字太少了，多放点字到charlist.txt");
                throw new Exception("字太少了，多放点字到charlist.txt");
            }
            if (tmp_length >= 2700)
            {
                Console.WriteLine("字太多了，无法装入那么多字，>2700");
                throw new Exception("字太多了，无法装入那么多字");
            }

            if (tmp_length >= 0x76d)
            {
                //当超出0x76D时，加入按钮占用的tile数
                tmp_length += 23;

            }
            //获得texture能达到的最大tile数，00000024h
            int max_tiles = ((int)Math.Ceiling(((double)tmp_length / (double)30)) + 1) * 30;
            t3bFont.max_tiles = max_tiles;

            //获取符合32x8并能容下所有字符的最接近texture_height
            int t1 = tmp_length / 900;
            int t2 = tmp_length % 900;
            int t3 = t1 * 512 + (int)Math.Ceiling(((double)t2 / (double)a2) + 1) * tile_h;
            
            texture_height = (int)Math.Ceiling((double)t3 / (double)swizzle_h) * swizzle_h;


            Bitmap bmp = new Bitmap((int)Math.Ceiling((double)texture_width), (int)Math.Ceiling((double)texture_height));
            Graphics g = Graphics.FromImage(bmp);
            g.Clear(Color.Transparent);
            int x = 0, y = 0;
            bool bGetFromBitmap = false;
            for (int i = 0; i < tmp_length; i++)
            {
                string currentChar0;
                if (i <= 0xc8)
                {
                    //字母数字和标点, 从原始图片中截取（bGetFromBitmap = true）
                    t3bFont.tbl.Add(string.Format("{0:x4}={1}", i, strings[i].ToString()));
                    currentChar0 = " ";
                    bGetFromBitmap = true;

                }
                else if ((0xc9 <= i) && (i <= 0x76c))
                {
                    //在按钮之前的字符， 使用freetype绘制点阵
                    currentChar0 = strings[i].ToString();
                    t3bFont.tbl.Add(string.Format("{0:x4}={1}", i, strings[i].ToString()));
                    bGetFromBitmap = false;
                }
                else if (i >= 0x784)
                {
                    //在按钮之后的字符， 使用freetype绘制点阵
                    currentChar0 = strings[i - 23].ToString();
                    t3bFont.tbl.Add(string.Format("{0:x4}={1}", i, currentChar0.ToString()));
                    bGetFromBitmap = false;
                }
                else
                {
                    //按钮图片, 从原始图片中截取（bGetFromBitmap = true）
                    currentChar0 = " ";
                    bGetFromBitmap = true;
                }

                if (bGetFromBitmap == false)
                {
                    face.SetCharSize(0, font_height, 0, 72);
                    face.SetPixelSizes((uint)0, (uint)font_height);
                    uint glyphIndex = face.GetCharIndex(uchar2code(currentChar0));
                    //face.LoadGlyph(glyphIndex, LoadFlags.Monochrome, LoadTarget.Mono);
                    //face.Glyph.RenderGlyph(RenderMode.Mono);

                    face.LoadGlyph(glyphIndex, LoadFlags.Default, LoadTarget.Lcd);
                    face.Glyph.RenderGlyph(RenderMode.Normal);
                    float left = (float)face.Glyph.Metrics.HorizontalBearingX;
                    float right = (float)face.Glyph.Metrics.HorizontalBearingX + (float)face.Glyph.Metrics.Width;
                    float top = (float)face.Glyph.Metrics.HorizontalBearingY;
                    float bottom = (float)face.Glyph.Metrics.HorizontalBearingY + (float)face.Glyph.Metrics.Height;
                    float FHT = font_height;
                    int FHD = (int)Math.Ceiling(FHT);
                    int kx = x + (int)Math.Round(left);
                    int ky = (int)Math.Round((float)y + (FHD - top));
                    //int ky = (int)Math.Round((float)y + (FHD - face.Glyph.BitmapTop));
                    
                    
                    FTBitmap ftbmp = face.Glyph.Bitmap;
                    if (ftbmp.Width == 0)
                    {
                        x += tile_w;
                        if (x + tile_w > tile_w)
                        {
                            x = 0;
                            y += tile_h;
                        }
                        if (i + 1 == 900 || i + 1 == 1800 || i + 1 == 2700)
                        {
                            y += (2);
                        }
                        continue;
                    }
                    
                    Bitmap dBmp = ftbmp.ToGdipBitmap(Color.FromArgb(255,0x24,0x24,0x24));
                    g.DrawImageUnscaled(dBmp, kx + relativePositionX - 1, ky + relativePositionY);
                    g.DrawImageUnscaled(dBmp, kx + relativePositionX + 1, ky + relativePositionY);
                    g.DrawImageUnscaled(dBmp, kx + relativePositionX, ky + relativePositionY - 1);
                    g.DrawImageUnscaled(dBmp, kx + relativePositionX, ky + relativePositionY + 1);
                    dBmp.Dispose();

                    FTBitmap ftbmp2 = face.Glyph.Bitmap;
                    Bitmap cBmp = ftbmp2.ToGdipBitmap(Color.White);
                    g.DrawImageUnscaled(cBmp, kx + relativePositionX, ky + relativePositionY);
                    g.DrawImageUnscaled(cBmp, kx + relativePositionX, ky + relativePositionY);
                    cBmp.Dispose();


                    x += tile_w;
                    if (x + tile_w > texture_width)
                    {
                        x = 0;
                        y += tile_h;
                    }
                    if (i + 1 == 900 || i + 1 == 1800 || i + 1 == 2700)
                    {
                        y += (2);
                    }
                    t3bFont.charvalues.Add(16);
                }
                else
                {
                    //从原版位图中获取并粘贴位置；
                    //do somethings.

                    int kx = x;
                    int ky = y;
                    int kw = (int)o_data[i + 0x47840];
                    int kh = 17;
                    
                    if (kw > 0)
                    {
                        Bitmap current_bm = new Bitmap(kw, kh);
                        Graphics _tmp_grp = System.Drawing.Graphics.FromImage(current_bm);
                        _tmp_grp.DrawImage(_bm, new Rectangle(0, 0, kw, kh), new Rectangle(kx, ky, kw, kh), GraphicsUnit.Pixel);

                        _tmp_grp.Dispose();
                        g.DrawImageUnscaled(current_bm, kx, ky);

                        //Console.WriteLine(String.Format("x:{0},y:{1},w:{2},h:{3}" , x, y ,kw ,kh));
                    }

                    x += tile_w;

                    if (x + tile_w > texture_width)
                    {
                        x = 0;
                        y += tile_h;
                    }
                    if (i + 1 == 900 || i + 1 == 1800 || i + 1 == 2700)
                    {
                        y += (2);
                    }
                    t3bFont.charvalues.Add(kw);
                }
            }
            g.Dispose();
            base_grp.Dispose();
            _bm.Dispose();
            library.Dispose();
            t3bFont.bitmap = bmp;
            return t3bFont;
        }
    }
}
