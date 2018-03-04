using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.IO;

namespace AtlusGames.GameFormat
{
    public interface IExtractable
    {
        void GetEntry();
        byte[] Unpack(string itemName);
        byte[] Repack(List<SubItem> subItems);
    }
}