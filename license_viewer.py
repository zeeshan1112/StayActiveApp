# license_viewer.py
import tkinter as tk
from tkinter import scrolledtext
import os

def show_license_window():
    root = tk.Tk()
    root.title("About StayActiveApp")

    # Optional: Set window icon
    icon_path = os.path.join(os.path.dirname(__file__), "icon.ico")
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except Exception:
            pass  # ICO not supported on macOS, usually ignored

    root.geometry("600x400")
    root.resizable(True, True)

    try:
        with open(os.path.join(os.path.dirname(__file__), "LICENSE.txt"), "r") as f:
            license_text = f.read()
    except Exception:
        license_text = "License file not found."

    text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD)
    text_area.insert(tk.INSERT, license_text)
    text_area.configure(state='disabled')  # Make read-only
    text_area.pack(expand=True, fill='both')

    root.mainloop()
