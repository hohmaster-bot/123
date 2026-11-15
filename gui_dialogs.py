# gui_dialogs.py
import tkinter as tk
from gui_shared import make_scrollable
from gui_windows import open_window

def ask_int(app, title, prompt, default=1, minvalue=0):
    d = open_window(app, title, 320, 140)
    
    tk.Label(d, text=prompt, anchor="w", justify="left",
             wraplength=300, font=("Segoe UI", 10)
             ).pack(fill="x", padx=10, pady=(10, 4))
    v = tk.IntVar(value=default)
    e = tk.Entry(d, textvariable=v, font=("Segoe UI", 11), width=10)
    e.pack(padx=10, pady=2)
    e.focus_set()
    e.select_range(0, tk.END)
    result = {"val": None}

    def ok(event=None):
        try: result["val"] = max(minvalue, int(v.get()))
        except Exception: result["val"] = None
        d.destroy()

    def cancel(event=None):
        result["val"] = None
        d.destroy()

    bf = tk.Frame(d)
    bf.pack(fill="x", pady=6)
    tk.Button(bf, text="OK", command=ok, bg="#4a7", fg="white", font=("Segoe UI", 10, "bold"), width=8).pack(side="left", padx=8)
    tk.Button(bf, text="Отмена", command=cancel, width=8).pack(side="left")
    
    d.bind("<Return>", ok)
    d.bind("<Escape>", cancel)
    d.wait_window() 
    return result["val"]

def show_text(app, title, text, width=420, height=360):
    d = open_window(app, title, width, height, mode=None)

    outer, canvas, body = make_scrollable(d)
    outer.pack(fill="both", expand=True, padx=6, pady=6)
    for line in str(text).splitlines() or [""]:
        tk.Label(body, text=line, anchor="w", justify="left",
                 font=("Segoe UI", 10), wraplength=width - 40
                 ).pack(fill="x", pady=1)
    tk.Button(d, text="OK", command=d.destroy, bg="#4a7", fg="white",
              font=("Segoe UI", 10, "bold"), width=10
              ).pack(pady=6)
    d.wait_window()
    
def ask_yes_no(app, title, text):
    d = open_window(app, title, 380, 160, mode=None)
    
    tk.Label(d, text=text, anchor="w", justify="left",
             wraplength=340, font=("Segoe UI", 10)
             ).pack(fill="x", padx=12, pady=(12, 6))
    result = {"val": False}
    bf = tk.Frame(d)
    bf.pack(fill="x", pady=8)

    def yes():
        result["val"] = True
        d.destroy()

    def no():
        result["val"] = False
        d.destroy()

    tk.Button(bf, text="Да", command=yes, bg="#4a7", fg="white",
              width=8, font=("Segoe UI", 10, "bold")
              ).pack(side="left", padx=10)
    tk.Button(bf, text="Нет", command=no, width=8
              ).pack(side="left")
    d.bind("<Return>", lambda e: yes())
    d.bind("<Escape>", lambda e: no())
    d.wait_window()
    return result["val"]