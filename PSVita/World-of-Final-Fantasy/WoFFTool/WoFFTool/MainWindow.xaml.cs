using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Controls;
using System.Windows.Data;
using System.Windows.Documents;
using System.Windows.Input;
using System.Windows.Media;
using System.Windows.Media.Imaging;
using System.Windows.Navigation;
using System.Windows.Shapes;
using Microsoft.Win32;
using System.IO;
using WoFFCore;
using System.Diagnostics;

namespace WoFFTool
{
    /// <summary>
    /// MainWindow.xaml 的交互逻辑
    /// </summary>
    public partial class MainWindow : Window
    {
        public MainWindow()
        {
            InitializeComponent();
        }


        private void OpenGxArchive_Click(object sender, RoutedEventArgs e)
        {
            OpenFileDialog openFileDialog = new OpenFileDialog();
            openFileDialog.Filter = "GxArchivedTable (*.csh)|*.csh";
            string table_name, pack_name;
            byte[] magic = new byte[] { 0x00, 0x68, 0x73, 0x63 };
            if (openFileDialog.ShowDialog() == true)
            {
                string name = openFileDialog.FileName;
                table_name = name;
                pack_name = name.Replace("GxArchivedTable", "GxArchivedFile");
                pack_name = pack_name.Replace(".csh", ".dat");
                
                WoFFCore.GxArchive arc = new WoFFCore.GxArchive(pack_name, table_name);
                this.UI_SetTextBlock(pack_name + "Loaded.");
                this.UI_SetTextBlock(string.Format("{0} Files ", arc.gdat_index.Count));
                using (Stream stream = File.Open(pack_name, FileMode.Open))
                {
                    for (int i = 0; i < arc.gdat_index.Count; i++)
                    {
                        Console.WriteLine("Got {0:x8}", (int)arc.gdat_index[i]);
                        string dst = string.Format("{0}_unpacked/{1:d8}.bin", pack_name, i);
                        BILZ item = new BILZ(stream , (int)arc.gdat_index[i] + 0x80);
                        this.UI_SetProgess((float)i / (float)arc.gdat_index.Count * (float)100);
                        this.UI_SetTextBlock(dst);
                        if (item.index_data != null)
                        {
                            if (!Directory.Exists(pack_name + "_unpacked"))
                            {
                                Directory.CreateDirectory(pack_name + "_unpacked");
                            }
                            
                            File.WriteAllBytes(dst, item.index_data);
                        }

                    }

                }
                this.UI_SetProgess(100f);

            }
            MessageBox.Show("Done");

        }
        private delegate void progressbarDelegate(float no);

        private delegate void textblockDelegate(string text);
        private void updateprogressbar(float no)
        {
            progressbar1.Value = no;
        }

        private void updateTextblock(string msg)
        {
            textBox1.Text += (msg + "\n");
        }
        public void UI_SetProgess(float value)
        {
            this.Dispatcher.Invoke(new progressbarDelegate(updateprogressbar), new object[] { (float)value });
        }

        public void UI_SetTextBlock(string msg)
        {
            this.Dispatcher.Invoke(new textblockDelegate(updateTextblock), new object[] { msg });
        }

        private void textBox1_TextChanged(object sender, TextChangedEventArgs e)
        {
            textBox1.SelectionStart = textBox1.Text.Length; 
            textBox1.ScrollToEnd();
        }
    }
}
