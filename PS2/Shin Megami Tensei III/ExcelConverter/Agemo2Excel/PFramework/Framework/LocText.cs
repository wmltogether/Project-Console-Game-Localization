using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace PFramework
{
    public class LocText
    {
        public string ja_JP;
        public string zh_CN;
        public string zh_TW;
        public LocText(string input)
        {
            ja_JP = input;
            zh_CN = input;
            zh_TW = input;
        }

        public string GetLanguageText(CurrentLanguage curLan)
        {
            switch (curLan)
            {
                case CurrentLanguage.E_CN:
                    return zh_CN;
                case CurrentLanguage.E_TW:
                    return zh_TW;
                case CurrentLanguage.E_JA:
                    return ja_JP;
                default:
                    return zh_CN;
            }
        }
        //public string en_US;
    }

    public enum CurrentLanguage
    {
        E_JA,
        E_CN,
        E_TW
    }
}
