using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace NISFONTBuilder
{
    public struct XYWH
    {
        public int char_id;
        public int x;
        public int y;
        public int tile_w;
        public int tile_h;
        public int v2;

        public XYWH(int char_id, int x, int y, int tile_w, int tile_h, int v2) : this()
        {
            this.char_id = char_id;
            this.x = x;
            this.y = y;
            this.tile_w = tile_w;
            this.tile_h = tile_h;
            this.v2 = v2;
        }
    }

    public class NISFont
    {
        public System.Drawing.Bitmap bitmap = null;
        public List<XYWH> charvalues = new List<XYWH>();
        

    }
    public class NISFont0
    {
        /*
         * 00000000h nismultifontfrm\0
         * 00000010h 4 bytes{
         *             null,
         *             size,
         *             size,
         *             null
         *             }
         * 00000020h 1 byte{
         *             0,
         *             font width,
         *             font_height,
         *             0
         *             }
         * 00000024h 2 bytes{
         *             font_size,
         *             char_nums,
         *             }
         * 00000028h 2 bytes  {
         *             x,
         *             y,
         *             char_id,
         *             0,
         *             }
         *
         * size + 0x20h "nis uti chu eoc "         
         */

        public string magic = "nismultifontfrm\0";

        public int size;
        public int fontWidth;
        public int fontHeight;

        public NISFont0()
        {

        }
    }
}
