# gui_shared.py — общие утилиты (v7)
# v7: + bind_clipboard_all (Ctrl+V/C/X/A при ЛЮБОЙ раскладке —
#     рус/англ, во всех окнах, включая Toplevel-диалоги)

import os
import io
import base64
import tkinter as tk
from PIL import Image, ImageTk


def _resize_image(img, w, h, mode="fill", darken=0):
    img = img.convert("RGBA")
    ratio = (max if mode == "fill" else min)(
        w / img.width, h / img.height)
    nw = max(1, int(img.width * ratio))
    nh = max(1, int(img.height * ratio))
    img = img.resize((nw, nh), Image.LANCZOS)
    if mode == "fill":
        l, t = (nw - w) // 2, (nh - h) // 2
        img = img.crop((l, t, l + w, t + h))
    if darken > 0:
        ov = Image.new("RGBA", img.size, (0, 0, 0, darken))
        img = Image.alpha_composite(img, ov)
    return ImageTk.PhotoImage(img)


def _load_image(path, w, h, mode="fill", darken=0):
    try:
        img = Image.open(path)
        return _resize_image(img, w, h, mode, darken)
    except Exception as e:
        print(f"Картинка (path): {e}")
        return None


def _load_image_from_data(data, w, h, mode="fill", darken=0):
    if not data:
        return None
    try:
        if isinstance(data, str) and len(data) < 260 \
                and os.path.exists(data):
            img = Image.open(data)
        else:
            if "," in data:
                data = data.split(",", 1)[1]
            raw = base64.b64decode(data)
            img = Image.open(io.BytesIO(raw))
        return _resize_image(img, w, h, mode, darken)
    except Exception as e:
        print(f"Картинка (data): {e}")
        return None


def bind_canvas_wheel(widget, canvas):
    def _on_wheel(e):
        delta = e.delta if hasattr(e, "delta") else 0
        if delta == 0:
            return
        steps = int(-delta / 120) if abs(delta) >= 120 else (
            -1 if delta > 0 else 1)
        if steps:
            canvas.yview_scroll(steps, "units")

    def _bind(e=None):
        widget.bind_all("<MouseWheel>", _on_wheel)

    def _unbind(e=None):
        widget.unbind_all("<MouseWheel>")

    widget.bind("<Enter>", _bind)
    widget.bind("<Leave>", _unbind)
    canvas.bind("<Enter>", _bind)
    canvas.bind("<Leave>", _unbind)


def make_scrollable(parent, bg="#f4f4f4"):
    outer = tk.Frame(parent, bg=bg)
    canvas = tk.Canvas(outer, bg=bg, highlightthickness=0, borderwidth=0)
    scrollbar = tk.Scrollbar(outer, orient="vertical",
                              command=canvas.yview)
    inner = tk.Frame(canvas, bg=bg)
    inner.bind("<Configure>",
                lambda e: canvas.configure(
                    scrollregion=canvas.bbox("all")))
    win_id = canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind("<Configure>",
                 lambda e: canvas.itemconfigure(win_id, width=e.width))
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    bind_canvas_wheel(canvas, canvas)
    bind_canvas_wheel(inner, canvas)
    return outer, canvas, inner

def _make_context_menu(widget):
    menu = tk.Menu(widget, tearoff=0)

    def do_copy():
        try:
            if isinstance(widget, tk.Text):
                if widget.tag_ranges(tk.SEL):
                    text = widget.get(tk.SEL.first, tk.SEL.last)
                    widget.clipboard_clear()
                    widget.clipboard_append(text)
            else:
                try:
                    if widget.selection_present():
                        widget.clipboard_clear()
                        widget.clipboard_append(widget.selection_get())
                except Exception:
                    pass
        except Exception as e:
            print(f"[ctx copy] {e}")

    def do_paste():
        try:
            text = widget.clipboard_get()
        except tk.TclError:
            return
        try:
            if isinstance(widget, tk.Text):
                if widget.tag_ranges(tk.SEL):
                    widget.delete(tk.SEL.first, tk.SEL.last)
                widget.insert(tk.INSERT, text)
            else:
                try:
                    if widget.selection_present():
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except Exception:
                    pass
                widget.insert(tk.INSERT, text)
        except Exception as e:
            print(f"[ctx paste] {e}")

    def do_cut():
        do_copy()
        try:
            if isinstance(widget, tk.Text):
                if widget.tag_ranges(tk.SEL):
                    widget.delete(tk.SEL.first, tk.SEL.last)
            else:
                try:
                    if widget.selection_present():
                        widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except Exception:
                    pass
        except Exception as e:
            print(f"[ctx cut] {e}")

    def do_select_all():
        try:
            if isinstance(widget, tk.Text):
                widget.tag_add(tk.SEL, "1.0", "end-1c")
                widget.mark_set(tk.INSERT, "end-1c")
                widget.see(tk.INSERT)
            else:
                try:
                    widget.select_range(0, tk.END)
                    widget.icursor(tk.END)
                except Exception:
                    pass
        except Exception as e:
            print(f"[ctx selall] {e}")

    menu.add_command(label="Копировать", command=do_copy)
    menu.add_command(label="Вставить", command=do_paste)
    menu.add_command(label="Вырезать", command=do_cut)
    menu.add_separator()
    menu.add_command(label="Выделить всё", command=do_select_all)

    def show_menu(event):
        try:
            widget.focus_set()
            menu.tk_popup(event.x_root, event.y_root)
        except Exception as e:
            print(f"[ctx show] {e}")
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    widget.bind("<Button-3>", show_menu, add="+")


def bind_context_menu(root):
    """Правый клик → меню Копировать/Вставить/Вырезать/Выделить всё
    на всех Text/Entry/Spinbox во всех окнах.
    Работает при любой раскладке."""

    def _attach(event):
        w = event.widget
        # Защита: ttk.Combobox и некоторые popup-элементы
        # присылают event.widget строкой, а не виджетом.
        if w is None or isinstance(w, str):
            return
        if not hasattr(w, "winfo_class"):
            return
        if getattr(w, "_ctx_menu_attached", False):
            return
        try:
            if isinstance(w, (tk.Text, tk.Entry, tk.Spinbox)):
                _make_context_menu(w)
                w._ctx_menu_attached = True
            else:
                cls_name = w.winfo_class()
                if cls_name in ("TEntry", "TSpinbox", "TCombobox"):
                    _make_context_menu(w)
                    w._ctx_menu_attached = True
        except Exception as e:
            try:
                cls_name = w.winfo_class()
            except Exception:
                cls_name = "?"
            print(f"[bind ctx {cls_name}] {e}")

    root.bind_all("<FocusIn>", _attach, add="+")
    root.bind_all("<Enter>", _attach, add="+")

def hint(parent, text, character=None, **kw):
    """Примечание под полем. Скрывается, если settings.hide_hints."""
    if character is not None:
        try:
            if character.settings.get("hide_hints", False):
                return None
        except Exception:
            pass
    kw.setdefault("fg", "#666")
    kw.setdefault("font", ("Segoe UI", 9))
    kw.setdefault("anchor", "w")
    lbl = tk.Label(parent, text=text, **kw)
    lbl.pack(anchor="w", padx=5, pady=(0, 2))
    return lbl

def bind_clipboard_all(root):
    """Ctrl+V/C/X/A — работает при ЛЮБОЙ раскладке (рус/англ)
    на Windows. Использует event.keycode (физическая клавиша),
    а не keysym (зависит от раскладки)."""

    def _paste(event=None):
        w = event.widget if event else None
        if w is None:
            return
        try:
            text = root.clipboard_get()
        except tk.TclError:
            return "break"
        try:
            cls = w.winfo_class()
            if cls == "Text":
                if w.tag_ranges(tk.SEL):
                    w.delete(tk.SEL.first, tk.SEL.last)
                w.insert(tk.INSERT, text)
            elif cls in ("Entry", "Spinbox", "TEntry",
                          "TSpinbox", "TCombobox"):
                try:
                    if w.selection_present():
                        w.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except Exception:
                    pass
                w.insert(tk.INSERT, text)
        except Exception as e:
            print(f"[paste] {e}")
        return "break"

    def _copy(event=None):
        w = event.widget if event else None
        if w is None:
            return
        try:
            cls = w.winfo_class()
            if cls == "Text":
                if w.tag_ranges(tk.SEL):
                    text = w.get(tk.SEL.first, tk.SEL.last)
                    root.clipboard_clear()
                    root.clipboard_append(text)
            elif cls in ("Entry", "Spinbox", "TEntry",
                          "TSpinbox", "TCombobox"):
                try:
                    if w.selection_present():
                        root.clipboard_clear()
                        root.clipboard_append(w.selection_get())
                except Exception:
                    pass
        except Exception as e:
            print(f"[copy] {e}")
        return "break"

    def _cut(event=None):
        w = event.widget if event else None
        if w is None:
            return
        try:
            cls = w.winfo_class()
            if cls == "Text":
                if w.tag_ranges(tk.SEL):
                    text = w.get(tk.SEL.first, tk.SEL.last)
                    root.clipboard_clear()
                    root.clipboard_append(text)
                    w.delete(tk.SEL.first, tk.SEL.last)
            elif cls in ("Entry", "Spinbox", "TEntry",
                          "TSpinbox", "TCombobox"):
                try:
                    if w.selection_present():
                        root.clipboard_clear()
                        root.clipboard_append(w.selection_get())
                        w.delete(tk.SEL_FIRST, tk.SEL_LAST)
                except Exception:
                    pass
        except Exception as e:
            print(f"[cut] {e}")
        return "break"

    def _select_all(event=None):
        w = event.widget if event else None
        if w is None:
            return
        try:
            cls = w.winfo_class()
            if cls == "Text":
                w.tag_add(tk.SEL, "1.0", "end-1c")
                w.mark_set(tk.INSERT, "end-1c")
                w.see(tk.INSERT)
            elif cls in ("Entry", "Spinbox", "TEntry",
                          "TSpinbox", "TCombobox"):
                w.select_range(0, tk.END)
                w.icursor(tk.END)
        except Exception as e:
            print(f"[select_all] {e}")
        return "break"

    def _matches(event, vk, keysyms):
        """Проверяет, соответствует ли событие клавише.
        vk — VK-код Windows (не зависит от раскладки).
        keysyms — fallback для других ОС."""
        try:
            if getattr(event, "keycode", None) == vk:
                return True
        except Exception:
            pass
        try:
            ks = getattr(event, "keysym", "").lower()
            if ks and ks in keysyms:
                return True
        except Exception:
            pass
        return False

    def _on_ctrl_key(event):
        # VK-коды Windows: V=86, C=67, X=88, A=65
        if _matches(event, 86, ("v", "м", "cyrillic_em")):
            return _paste(event)
        if _matches(event, 67, ("c", "с", "cyrillic_es")):
            return _copy(event)
        if _matches(event, 88, ("x", "ч", "cyrillic_che")):
            return _cut(event)
        if _matches(event, 65, ("a", "ф", "cyrillic_ef")):
            return _select_all(event)
        return None

    # Ловим ВСЕ Ctrl+KeyPress — внутри разбираем по keycode
    for seq in ("<Control-KeyPress>", "<Control-Key>"):
        try:
            root.bind_all(seq, _on_ctrl_key)
        except tk.TclError:
            pass

    # Дополнительно — приоритетный бинд на классы полей
    # (иначе стандартные Text/Entry перехватывают Ctrl+V раньше)
    for cls in ("Text", "Entry", "Spinbox",
                "TEntry", "TSpinbox", "TCombobox"):
        try:
            root.bind_class(cls, "<Control-KeyPress>",
                             _on_ctrl_key, add="+")
        except tk.TclError:
            pass

    # Классические Ctrl+Insert / Shift+Insert / Shift+Delete
    try:
        root.bind_all("<Control-Insert>", _copy)
        root.bind_all("<Shift-Insert>", _paste)
        root.bind_all("<Shift-Delete>", _cut)
    except tk.TclError:
        pass


class ToolTip:
    """T39: единый тултип с задержкой, автообновлением и позицией.

    text может быть str или callable → str (для динамических подсказок).
    Задержка — 400 мс (не мелькает). При уходе — отмена таймера.
    """
    _delay_ms = 400
    _wraplength = 380
    _padx = 8
    _pady = 6
    _bg = "#ffffe0"
    _font = ("Segoe UI", 10)

    def __init__(self, widget, text):
        self.widget = widget
        self._text = text
        self.tip = None
        self._after_id = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def set_text(self, text):
        """Обновить текст тултипа (callable или str)."""
        self._text = text
        if self.tip:
            self._render()

    def _resolve(self):
        t = self._text
        if callable(t):
            try:
                return str(t())
            except Exception:
                return ""
        return str(t or "")

    def _show(self, event=None):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = self.widget.after(self._delay_ms,
                                            self._really_show)

    def _really_show(self):
        self._after_id = None
        text = self._resolve()
        if not text:
            return
        if self.tip:
            self._render()
            return
        x = self.widget.winfo_rootx() + 15
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 6
        self.tip = tk.Toplevel(self.widget)
        self.tip.wm_overrideredirect(True)
        # Позиция: если за экраном — прижать
        self.tip.update_idletasks()
        sw = self.widget.winfo_screenwidth()
        sh = self.widget.winfo_screenheight()
        if x + self._wraplength + 20 > sw:
            x = sw - self._wraplength - 20
        self.tip.wm_geometry(f"+{max(0, x)}+{max(0, y)}")
        self._lbl = tk.Label(
            self.tip, text=text, background=self._bg,
            relief="solid", borderwidth=1,
            wraplength=self._wraplength,
            font=self._font, justify="left",
            padx=self._padx, pady=self._pady)
        self._lbl.pack()

    def _render(self):
        text = self._resolve()
        if not text:
            self._hide()
            return
        try:
            self._lbl.config(text=text)
        except Exception:
            pass

    def _hide(self, event=None):
        if self._after_id is not None:
            try:
                self.widget.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None
        if self.tip:
            try:
                self.tip.destroy()
            except Exception:
                pass
            self.tip = None
            self._lbl = None