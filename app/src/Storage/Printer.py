
import cups
import os
import webbrowser

def print_file_with_cups(file_path):

    try:
        conn = cups.Connection()
        print("Connected to cups")
        printers = conn.getPrinters()
        printer_name = list(printers.keys())[0]  # 使用第一个可用的打印机
        conn.printFile(printer_name, file_path, "Python_Print_Job", {})

        print(f"文件 {file_path} 已发送到打印机 {printer_name}")

        open_cups_webui()
        open_dolphin()

    except Exception as e:

        print(f"打印失败: {e}")

def open_cups_webui():
    webbrowser.open("localhost:631/printers/vPrinter?which_jobs=completed")

def open_dolphin():
    os.system("dolphin /var/spool/cups-pdf/shoreninth")

print_file_with_cups("test.txt")
