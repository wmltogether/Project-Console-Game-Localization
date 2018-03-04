using System;
using System.Collections;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Drawing;

namespace AltusFontTool
{
    public enum EndianType
    {
        BIG,
        LITTLE,
    }

    public class TextureEncoder
    {
        /*
         *根据python版的脚本直接翻译而来，PIL读入图片更改为GDI 位图读入
         */
        private List<int> tile2linear(List<int> data, int width, int height, int tile_h, int tile_w)
        {
            int ntx = width / tile_w;
            int nty = height / tile_h;
            int tile_len = tile_w * tile_h;
            List<int[]> tilelst = new List<int[]>();
            int[] tile;
            int index, index_tile;
            List<int> nPixel_data = new List<int>();
            for (int k = 0; k < width * height; k+=(tile_w * tile_h))
            {
                tile = data.GetRange(k, tile_len).ToArray();
                tilelst.Add(tile);
            }
            
            for (int a = 0; a < nty; a++)
            {
                for (int b = 0; b < tile_h; b++)
                {
                    for (int c = 0; c < ntx; c++)
                    {
                        for (int d = 0; d < tile_w; d++)
                        {
                            index = a * ntx + c;
                            index_tile = b * tile_w + d;
                            nPixel_data.Add(tilelst[index][index_tile]);
                        }
                    }
                }
            }
            return nPixel_data;
        }
        public List<Color> getPaletteData(byte[] paldata, int transparency_index = 0)
        {
            List<Color> RGBlst = new List<Color>();
            for (int i = 0; i < paldata.Length; i += 4)
            {
                int r = (int) paldata[i];
                int g = (int) paldata[i + 1];
                int b = (int) paldata[i + 2];
                int a = (int) paldata[i + 3];
                RGBlst.Add(Color.FromArgb(a, r, g, b));
            }
            return RGBlst;
        }

        public List<Color> getPS2PaletteData(byte[] paldata, int transparency_index = 0)
        {
            // 调色板0 是描边
            // 调色板1 是透明
            List<Color> RGBlst = new List<Color>();
            for (int i = 0; i < paldata.Length; i += 4)
            {
                int r = (int)paldata[i];
                int g = (int)paldata[i + 1];
                int b = (int)paldata[i + 2];
                int a = (int)((float)255.0 * ((float)paldata[i + 3] / (float)0x80));
                RGBlst.Add(Color.FromArgb(a, r, g, b));
            }
            RGBlst[0] = Color.FromArgb(255, 0, 0, 255);
            RGBlst[1] = Color.FromArgb(0, 0, 0, 0);
            return RGBlst;
        }

        public int findIndexColor(Color pixelColor, List<Color> RGBlst, int color_num)
        {
            if (RGBlst.Contains(pixelColor))
            {
                return RGBlst.IndexOf(pixelColor);
            }
            else
            {
                List<int> dlist = new List<int>();
                int fR;
                int fG;
                int fB;
                int fA;

                fR = pixelColor.R;
                fG = pixelColor.G;
                fB = pixelColor.B;
                fA = pixelColor.A;
                foreach (var pColor in RGBlst)
                {
                    int tR;
                    int tG;
                    int tB;
                    int tA;
                    tR = pColor.R;
                    tG = pColor.G;
                    tB = pColor.B;
                    tA = pColor.A;
                    int rMean = (fR * fA + tR * tA) / 510;
                    int rDiff = (fR * fA - tR * tA) / 255;
                    int gDiff = (fG * fA - tG * tA) / 255;
                    int bDiff = (fB * fA - tB * tA) / 255;
                    int aDiff = fA - tA;
                    int dist = (510 + rMean) * (int) Math.Pow(rDiff, 2) +
                               1020 * (int) Math.Pow(gDiff, 2) +
                               (765 - rMean) * (int) Math.Pow(bDiff, 2) +
                               1530 * (int) Math.Pow(aDiff, 2);
                    dlist.Add(dist);
                    if (dist == 0)
                    {
                        break;
                    }
                }
                int minDist = dlist.Min();
                return dlist.IndexOf(minDist);
            }
        }
        public Bitmap get4Bpp(int width, int height , int tile_w, int tile_h,
                                byte[] data, byte[] palette, EndianType endianType)
        {
            List<Color> paletteData = getPS2PaletteData(palette);
            int nNecessBytes = width * height / 2;
            byte[] data_buff = new byte[nNecessBytes];
            if (nNecessBytes > data.Length)
            {
                for (int n = 0; n < nNecessBytes; n++)
                {
                    if (n < data.Length)
                    {
                        data_buff[n] = data[n];
                    }
                    else
                    {
                        data_buff[n] = (byte)0;
                    }
                }
            }
            else
            {
                Array.Copy(data, data_buff, nNecessBytes);
            }
            
            
            int ntx = width / tile_w;
            int nty = height / tile_h;
            int pixNum = 0;
            int j;
            List<int> newdata = new List<int>();
            int nPixels = width * height;
            List<int> nPixel_data;
            for (int i = 0; i < nNecessBytes; i++)
            {
                int bt = (int)data_buff[i];
                for (int b = 0; b < 2; b++)
                {
                    if (pixNum > nPixels)
                    {
                        break;
                    }
                    if (endianType == EndianType.BIG)
                    {
                        j = ((bt & (0x0f << (b * 4))) >> (b * 4));
                        newdata.Add(j);
                    }
                    else
                    {
                        j = ((bt & (0xf0 >> (b * 4))) >> ((1 - b) * 4));
                        newdata.Add(j);
                    }
                    pixNum += 1;
                
                }
            }
            nPixel_data = tile2linear(newdata, width, height, tile_h, tile_w);
            Bitmap bmp = new Bitmap(width, height);
            for (int y = 0; y < bmp.Height; y++)
            {
                for (int x = 0; x < bmp.Width; x++)
                {
                    bmp.SetPixel(x, y, paletteData[nPixel_data[x + bmp.Width * y]]);
                }
            }

            return bmp;

        }

        public byte[] create4Bpp(Bitmap im, int tile_w, int tile_h,
            List<Color> paletteList, EndianType endianType)
        {
            im.RotateFlip(RotateFlipType.Rotate180FlipNone);
            int width = im.Width;
            int height = im.Height;
            List<byte> imByteList = new List<byte>();
            int ntx = width / tile_w;
            int nty = height / tile_h;
            List<Color> nPixel_data = new List<Color>();
            //Console.WriteLine("Reading colors xy");
            for (int a = 0; a < nty; a++)
            {
                for (int b = 0; b < ntx; b++)
                {
                    for (int c = 0; c < tile_h; c++)
                    {
                        for (int d = 0; d < tile_w; d++)
                        {
                            int tx = d + tile_w * b;
                            int ty = c + tile_h * a;
                            nPixel_data.Add(im.GetPixel(tx, ty));
                        }
                    }
                }
            }
            im.Dispose();
            //Console.WriteLine("Compressing xy");
            List<int> indexList = new List<int>();
            foreach (Color pixelColor in nPixel_data)
            {
                indexList.Add(findIndexColor(pixelColor, paletteList, 16));
            }
            //Console.WriteLine("writing xy");
            for (int i = 0; i < indexList.Count; i += 2)
            {
                int[] n = new int[2];
                if (endianType == EndianType.BIG)
                {
                    n[0] = indexList[i];
                    n[1] = indexList[i + 1];
                }
                else
                {
                    n[1] = indexList[i];
                    n[0] = indexList[i + 1];
                }

                int bt = 0;
                bt += (n[0] << (0 * 4));
                bt += (n[1] << (1 * 4));
                imByteList.Add((byte) bt);
            }

            return imByteList.ToArray();
        }
    }
}
