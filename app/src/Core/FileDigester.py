import os
import PySide6.QtCore
from PySide6.QtWidgets import QFileDialog

def file_printer():
    file_selector = QFileDialog()
    print(file_selector)
