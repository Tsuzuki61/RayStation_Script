import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
dir = r"DirectoryPath"
fld = filedialog.askdirectory(initialdir=dir)
print(fld)
