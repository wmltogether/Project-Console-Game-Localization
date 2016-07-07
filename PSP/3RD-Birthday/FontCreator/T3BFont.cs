using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Drawing;

namespace FontCreator
{
    public class T3BFont
    {
        public Bitmap bitmap = null;
        public List<int> charvalues = new List<int>();
        public List<string> tbl = new List<string>();
        
        public int texture_width = 512;
        public int max_tiles = 0;
        public int item_width = 0x10;
        public uint unk0 = 0x210095;
        public uint unk1 = 0x4100af;
        public uint unk2 = 0x10008b;
        public int button_tile_id = 0x76d;
        public uint unk3 = 0;

    }
}
