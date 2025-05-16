import qrcode
import cups


def print_file_with_cups(file_path):

    try:

        conn = cups.Connection()

        printers = conn.getPrinters()

        printer_name = list(printers.keys())[0]  # 使用第一个可用的打印机

        conn.printFile(printer_name, file_path, "Python_Print_Job", {})

        print(f"文件 {file_path} 已发送到打印机 {printer_name}")

    except Exception as e:

        print(f"打印失败: {e}")


print_file_with_cups("example.pdf")