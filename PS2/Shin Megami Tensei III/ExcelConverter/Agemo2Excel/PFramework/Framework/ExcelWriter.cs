using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using NPOI.SS.UserModel;
using NPOI.XSSF.UserModel;

namespace PFramework
{
    public class DataMgr : Singleton<DataMgr>
    {
        private DataMgr()
        {

        }

        public Dictionary<string,LocText> GameTextDictionary = new Dictionary<string, LocText>();
    }
    public class ExcelLoader
    {
        private string mFilePath;
        public ExcelLoader(string path)
        {
            mFilePath = path;
        }

        public const int CELL_KEY = 0;
        public const int CELL_JP = 1;
        public const int CELL_CN = 2;
        public const int CELL_TW = 3;

        public void WriteExcel(Dictionary<string, LocText> arg)
        {
            arg = arg.OrderBy(o => o.Key).ToDictionary(o => o.Key, p => p.Value);
            XSSFWorkbook workbook = new XSSFWorkbook();  //新建xlsx工作簿  
            workbook.CreateSheet("Sheet1");
            XSSFSheet sheet = workbook.GetSheet("Sheet1") as XSSFSheet;
            string[] keys = arg.Keys.ToArray();
            int header_length = 1;
            IRow field = sheet.CreateRow(0);
            ICellStyle wrapCellStyle = workbook.CreateCellStyle();
            wrapCellStyle.WrapText = true;
            wrapCellStyle.Alignment = HorizontalAlignment.Left;
            wrapCellStyle.VerticalAlignment = VerticalAlignment.Top;
            ICellStyle jpCellStyle = workbook.CreateCellStyle();
            jpCellStyle.Alignment = HorizontalAlignment.Left;
            jpCellStyle.VerticalAlignment = VerticalAlignment.Top;
            jpCellStyle.WrapText = true;
            field.CreateCell(0).SetCellValue("Key");
            field.CreateCell(1).SetCellValue("日本語");
            field.CreateCell(2).SetCellValue("简体中文");
            field.CreateCell(3).SetCellValue("繁體中文");
            for (int i = 0; i < keys.Length; i++)
            {
                IRow row = sheet.CreateRow(header_length + i);

                ICell cellKey = row.CreateCell(0);
                cellKey.SetCellType(CellType.String);
                cellKey.SetCellValue(keys[i]);

                ICell celljp = row.CreateCell(1);
                celljp.SetCellType(CellType.String);
                celljp.SetCellValue(arg[keys[i]].ja_JP);
                celljp.CellStyle = wrapCellStyle;

                ICell cellcn = row.CreateCell(2);
                cellcn.SetCellType(CellType.String);
                cellcn.SetCellValue(arg[keys[i]].zh_CN);
                cellcn.CellStyle = wrapCellStyle;
            }

            //列宽自适应
            for (int i = 0; i <= keys.Length%1000; i++)
            {
                sheet.AutoSizeColumn(i);
            }

            using (FileStream fs = File.Create(mFilePath))
            {
                workbook.Write(fs);
                workbook.Close();
            }
        }

        public void ReadExcel()
        {
            XSSFWorkbook workbook;
            using (FileStream fs = new FileStream(mFilePath, FileMode.Open, FileAccess.Read))
            {
                workbook = new XSSFWorkbook(fs);
                XSSFSheet sheet = workbook.GetSheetAt(0) as XSSFSheet;
                if (sheet != null)
                {
                    System.Collections.IEnumerator rows = sheet.GetRowEnumerator();
                    int t = 0;
                    while (rows.MoveNext())
                    {
                        if (t == 0)
                        {
                            t += 1;
                            continue;
                        }
                        IRow row = (XSSFRow)rows.Current;
                        int cellCount = row.LastCellNum;
                        if (cellCount < 2)
                        {
                            continue;
                        }
                        List<ICell> cells = new List<ICell>();
                        for (int i = 0; i < row.LastCellNum; i++)
                        {
                            ICell cell = row.GetCell(i);
                            cells.Add(cell);

                        }
                        string strkey = String.Empty;
                        string jpText = String.Empty;
                        string cnText = String.Empty;
                        string twText = String.Empty;
                        ColUtil.GetStringValue(cells[CELL_KEY], out strkey);
                        ColUtil.GetStringValue(cells[CELL_JP], out jpText);
                        ColUtil.GetStringValue(cells[CELL_CN], out cnText);
                        //ColUtil.GetStringValue(cells[CELL_TW], out twText);
                        LocText locText = new LocText(jpText);
                        locText.zh_CN = cnText;
                        locText.zh_TW = twText;

                        DataMgr.Instance.GameTextDictionary.Add(strkey, locText);
                        t += 1;

                    }
                }

            }

        }

        private static ICellStyle SetCellStyle(NPOI.XSSF.UserModel.XSSFWorkbook workbook, string color)
        {
            ICellStyle cellStyle = workbook.CreateCellStyle();
            cellStyle.WrapText = true;
            cellStyle.Alignment = NPOI.SS.UserModel.HorizontalAlignment.Left;
            //边框
            cellStyle.BorderBottom = NPOI.SS.UserModel.BorderStyle.Thin;
            cellStyle.BorderLeft = NPOI.SS.UserModel.BorderStyle.Thin;
            cellStyle.BorderRight = NPOI.SS.UserModel.BorderStyle.Thin;
            cellStyle.BorderTop = NPOI.SS.UserModel.BorderStyle.Thin;
            cellStyle.FillPattern = FillPattern.SolidForeground;
            switch (color)
            {
                case "rose":
                    cellStyle.FillForegroundColor = IndexedColors.Violet.Index;
                    break;
                case "white":
                    cellStyle.FillForegroundColor = IndexedColors.White.Index;
                    break;
                case "red":
                    cellStyle.FillForegroundColor = IndexedColors.Red.Index;
                    break;
                case "yellow":
                    cellStyle.FillForegroundColor = IndexedColors.Yellow.Index;
                    break;
                case "lime":
                    cellStyle.FillForegroundColor = IndexedColors.BrightGreen.Index;
                    break;
                case "gray":
                    cellStyle.FillForegroundColor = IndexedColors.Grey40Percent.Index;
                    break;
                default:
                    cellStyle.FillForegroundColor = IndexedColors.Grey40Percent.Index;
                    break;
            }
            //CellsStyle.FillBackgroundColor = IndexedColors.BrightGreen.Index;
            return cellStyle;
        }
    }

    public class ColUtil
    {
        public static string ConvStrN20A(string str)
        {
            str = str.Replace("\\r", "\r");
            str = str.Replace("\\n", "\n");
            return str;
        }

        public static string ConvStr0A2N(string str)
        {
            str = str.Replace("\r", @"");
            str = str.Replace("\n", "\\n");
            return str;
        }
        public static void GetStringValue(ICell cell, out string result)
        {
            result = null;
            if (cell == null)
            {
                return;
            }

            switch (cell.CellType)
            {
                case CellType.Error:
                case CellType.Unknown:
                    result = null;
                    break;
                case CellType.String:
                    result = cell.StringCellValue;
                    break;
                case CellType.Numeric:
                    result = cell.NumericCellValue.ToString();
                    break;
                case CellType.Formula:
                    result = cell.NumericCellValue.ToString();
                    break;
                default:
                    break;
            }
        }
    }
}
