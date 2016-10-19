using System;
using System.Collections.Generic;
using System.Drawing;
using System.Drawing.Imaging;
using System.Linq;
using System.Text;
using System.IO;
using psp_gxm.Compression;
using Core.IO;
using System.Runtime.InteropServices;

namespace psp_gxm
{
    public class TextureConv
    {
        /// <summary>
        /// Decompress DXT5 from bytes
        /// </summary>
        /// <param name="input">input bytes</param>
        /// <param name="Width">texture width</param>
        /// <param name="Height">texture height</param>
        /// <param name="output">output bitmap</param>
        /// <param name="bUseVitaSwizzle">Use psvita swizzle</param>
        /// <returns></returns>
        public Bitmap GetDXT5Bitmap(byte[] input, int Width ,int Height, out byte[] output, bool bUseVitaSwizzle = false)
        {
            Bitmap image = new Bitmap(Width, Height, PixelFormat.Format32bppArgb);
            BitmapData bmpData = image.LockBits(new Rectangle(0, 0, image.Width, image.Height), ImageLockMode.ReadWrite, image.PixelFormat);
            byte[] pixelsForBmp = new byte[bmpData.Height * bmpData.Stride];
            int bitsPerPixel = Bitmap.GetPixelFormatSize(image.PixelFormat);
            byte[] pixelData = DXTC.Decompress(new EndianBinaryReader( new MemoryStream(input) ), Width, Height, PixelDataFormat.SpecialFormatDXT5, input.Length, bUseVitaSwizzle);
            Marshal.Copy(pixelData, 0, bmpData.Scan0, pixelsForBmp.Length);
            image.UnlockBits(bmpData);
            output = pixelData;
            return image.Clone(new Rectangle(0, 0, Width, Height), image.PixelFormat);


        }
    }
}
