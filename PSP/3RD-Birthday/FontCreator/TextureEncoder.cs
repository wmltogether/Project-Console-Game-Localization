using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;
using System.Drawing;

namespace FontCreator
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
        public List<Color> getPaletteData(byte[] paldata, int transparency_index = 0)
        {
            List<Color> RGBlst = new List<Color>();
            for (int i = 0; i < paldata.Length; i+=4 )
            {
                int r = (int)paldata[i];
                int g = (int)paldata[i + 1];
                int b = (int)paldata[i + 2];
                int a = (int)paldata[i + 3];
                RGBlst.Add(Color.FromArgb(a, r, g, b));
            }
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
                int fR; int fG; int fB; int fA;
                
                fR = pixelColor.R;
                fG = pixelColor.G;
                fB = pixelColor.B;
                fA = pixelColor.A;
                foreach (var pColor in RGBlst)
                {
                    int tR; int tG; int tB; int tA;
                    tR = pColor.R;
                    tG = pColor.G;
                    tB = pColor.B;
                    tA = pColor.A;
                    int rMean = (fR * fA + tR * tA) / 510;
                    int rDiff = (fR * fA - tR * tA) / 255;
                    int gDiff = (fG * fA - tG * tA) / 255;
                    int bDiff = (fB * fA - tB * tA) / 255;
                    int aDiff = fA - tA;
                    int dist = (510 + rMean) * (int)Math.Pow(rDiff, 2) +
                                        1020 * (int)Math.Pow(gDiff, 2) +
                                        (765 - rMean) * (int)Math.Pow(bDiff, 2) +
                                        1530 * (int)Math.Pow(aDiff, 2);
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

        public byte[] create4Bpp(Bitmap im, int tile_w , int tile_h ,
                                    List<Color> paletteList, EndianType endianType)
        {
            int width  = im.Width; int height = im.Height;
            List<byte> imByteList = new List<byte>();
            int ntx = width / tile_w;
            int nty = height / tile_h;
            List<Color> nPixel_data = new List<Color>();
            Console.WriteLine("Reading colors xy");
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
            Console.WriteLine("Compressing xy");
            List<int> indexList = new List<int>();
            foreach (Color pixelColor in nPixel_data)
            {
                indexList.Add(findIndexColor(pixelColor, paletteList, 16));
            }
            Console.WriteLine("writing xy");
            for (int i = 0; i < indexList.Count; i+=2)
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
                imByteList.Add((byte)bt);
            }

            return imByteList.ToArray();
        }
    }
}  
