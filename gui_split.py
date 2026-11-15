# gui_split.py — 3-панельный режим (v17, независимый)
import tkinter as tk
from gui_buttons import buttons_list, is_visible, CENTER_BUTTONS
from gui_shared import bind_canvas_wheel
import gui_media

class SplitView:
    def __init__(self, app):
        self.app = app
        self.mode = app.c.settings.get("ui_layout_mode", "split") if app.c else "split"
        self.menu_win = None
        self.center_win = None
        self.chips_win = None
        self.current_editor_win = None  # T-SPLIT-4: текущее окно-спутник
        self._drag_x = None
        self._drag_y = None
        self._build()

    def _build(self):
        self._build_menu()
        self._build_center()
        self._build_chips()
        self._apply_pin()
        try:
            self.app.root.withdraw()
            # Принудительно показываем центр, чтобы кнопка «Ч» работала с первого раза
            if self.center_win:
                self.center_win.deiconify()
                self.center_win.lift()
        except Exception:
            pass

    # ---------- МЕНЮ ----------
    def _build_menu(self):
        w = tk.Toplevel(self.app.root)
        w.overrideredirect(False)
        w.attributes("-toolwindow", True)
        w.configure(bg="#1a1a1a")
        w.geometry("280x780+20+60")
        gui_media.force_taskbar_alt_tab(w)
        self.menu_win = w

        import gui_menu
        gui_menu.build_menu(self.app, parent=w)

        self.app._drag_handles = {self.app._menubar}
        # Закрытие меню по Escape
        w.bind("<Escape>", lambda e: self._on_menu_close())
        for ch in self.app._menubar.winfo_children():
            if ch.winfo_class() in ("Frame", "Label"):
                self.app._drag_handles.add(ch)
        for h in self.app._drag_handles:
            h.bind("<ButtonPress-1>", self._menu_start_move)
            h.bind("<B1-Motion>", self._menu_do_move)

        portrait_frame = tk.Frame(w, bg="#1a1a1a")
        portrait_frame.pack(fill="x")
        lbl_portrait = tk.Label(portrait_frame, text="[Портрет]",
                                bg="#1a1a1a", fg="#888", cursor="hand2")
        lbl_portrait.pack(expand=True)
        lbl_portrait.bind("<Button-1>", lambda e: gui_media.expand_portrait(self.app))
        self.app.portrait_frame = portrait_frame
        self.app.lbl_portrait = lbl_portrait

        self._build_side_tabs(w)
        cont = tk.Frame(w, bg="#1a1a1a")
        cont.pack(side="left", fill="both", expand=True)

        canvas = tk.Canvas(cont, bg="#1a1a1a", highlightthickness=0)
        sb = tk.Scrollbar(cont, orient="vertical", command=canvas.yview)
        inner = tk.Frame(canvas, bg="#1a1a1a")
        inner.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=inner, anchor="nw", tags="inner")
        canvas.configure(yscrollcommand=sb.set)
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure("inner", width=e.width))
        canvas.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        bind_canvas_wheel(inner, canvas)
        bind_canvas_wheel(canvas, canvas)

        self.app.buttons_canvas = canvas
        self.app.buttons_inner = inner
        self.app.top = w
        self._rebuild_menu_buttons()
        self._add_resize_grip(w)

    def _build_side_tabs(self, parent):
        side = tk.Frame(parent, bg="#2a2a2a", width=32)
        side.pack(side="right", fill="y")
        side.pack_propagate(False)
        side.bind("<ButtonPress-1>", self._menu_start_move)
        side.bind("<B1-Motion>", self._menu_do_move)
        lbl = tk.Label(side, text="↔", bg="#2a2a2a", fg="#666", font=("Segoe UI", 9), cursor="fleur")
        lbl.pack(side="top", pady=(6, 0))
        lbl.bind("<ButtonPress-1>", self._menu_start_move)
        lbl.bind("<B1-Motion>", self._menu_do_move)
        tk.Button(side, text="Ч", width=2, relief="flat", bg="#3a3a3a", fg="#ccc",
                  font=("Segoe UI", 10, "bold"), activebackground="#555", activeforeground="white",
                  command=self._show_char_sheet).pack(side="top", pady=(4, 2))
        tk.Button(side, text="О", width=2, relief="flat", bg="#3a3a3a", fg="#ccc",
                  font=("Segoe UI", 10, "bold"), activebackground="#555", activeforeground="white",
                  command=self._show_last_editor).pack(side="top", pady=2)
        tk.Button(side, text="Б", width=2, relief="flat", bg="#3a3a3a", fg="#ccc",
                  font=("Segoe UI", 10, "bold"), activebackground="#555", activeforeground="white",
                  command=self._toggle_chips).pack(side="top", pady=2)

    def _rebuild_menu_buttons(self):
        if self.menu_win is None or not self.menu_win.winfo_exists():
            return
        for ch in self.app.buttons_inner.winfo_children():
            ch.destroy()
        for text, cmd, key in buttons_list(self.app):
            if cmd is None:
                tk.Frame(self.app.buttons_inner, height=6, bg="#1a1a1a").pack(fill="x")
                continue
            if self.app.c and not is_visible(self.app, key):
                continue
            tk.Button(self.app.buttons_inner, text=text, anchor="w", font=("Segoe UI", 10),
                      relief="flat", bg="#3a3a3a", fg="white", activebackground="#555",
                      activeforeground="white", command=lambda k=key, c=cmd: self._run_button(k, c)
                      ).pack(fill="x", padx=4, pady=1)

    # ---------- ЦЕНТР ----------
    def _build_center(self):
        w = tk.Toplevel(self.app.root)
        w.overrideredirect(False)
        w.attributes("-toolwindow", True)
        w.configure(bg="#1a1a1a")
        w.geometry("820x780+320+60")
        self.center_win = w

        top = tk.Frame(w, bg="#1a1a1a", pady=6, padx=10)
        top.pack(fill="x")
        # Закрытие чарника по Escape
        w.bind("<Escape>", lambda e: self._on_center_close())
        top.bind("<ButtonPress-1>", self._center_start_move)
        top.bind("<B1-Motion>", self._center_do_move)
        self.app._top = top

        lbl_name = tk.Label(top, text="—", font=("Segoe UI", 14, "bold"), fg="white", bg="#1a1a1a")
        lbl_name.pack(side="left")
        lbl_name.bind("<ButtonPress-1>", self._center_start_move)
        lbl_name.bind("<B1-Motion>", self._center_do_move)
        self.app.lbl_name = lbl_name

        lbl_class = tk.Label(top, text="", font=("Segoe UI", 11), fg="#ccc", bg="#1a1a1a")
        lbl_class.pack(side="left", padx=15)
        lbl_class.bind("<ButtonPress-1>", self._center_start_move)
        lbl_class.bind("<B1-Motion>", self._center_do_move)
        self.app.lbl_class = lbl_class

        btn_levelup = tk.Button(top, text="⬆ Level Up", command=self.app._do_level_up,
                                bg="#3a7a3a", fg="white", relief="flat", font=("Segoe UI", 10, "bold"),
                                activebackground="#5aa05a", activeforeground="white")
        self.app.btn_levelup = btn_levelup

        row1 = tk.Frame(w, bg="#222", pady=4, padx=6)
        row1.pack(fill="x")
        row2 = tk.Frame(w, bg="#222", padx=6, pady=2)
        row2.pack(fill="x")
        import gui_combat
        gui_combat.build_combat_panel(self.app, row1, row2)

        right_container = tk.Frame(w, bg="#1a1a1a")
        right_container.pack(fill="both", expand=True)

        view_main = tk.Frame(right_container, bg="#1a1a1a")
        info_canvas = tk.Canvas(view_main, bg="#1a1a1a", highlightthickness=0)
        scroll = tk.Scrollbar(view_main, orient="vertical", command=info_canvas.yview)
        info_canvas.configure(yscrollcommand=scroll.set)
        info_canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        info_canvas.bind("<Configure>", self.app._on_canvas_resize)
        bind_canvas_wheel(info_canvas, info_canvas)

        view_edit = tk.Frame(right_container, bg="#f4f4f4")
        view_main.pack(fill="both", expand=True)

        self.app.right_container = right_container
        self.app.view_main = view_main
        self.app.view_edit = view_edit
        self.app.info_canvas = info_canvas
        self._add_resize_grip(w)

    # ---------- ЧИПЫ ----------
    def _build_chips(self):
        w = tk.Toplevel(self.app.root)
        w.overrideredirect(False)
        w.attributes("-toolwindow", True)
        w.configure(bg="#2a2a2a")
        w.geometry("820x120+320+850")
        self.chips_win = w

        header = tk.Frame(w, bg="#2b2b2b", pady=4, padx=8)
        header.pack(fill="x")
        header.bind("<ButtonPress-1>", self._chips_start_move)
        header.bind("<B1-Motion>", self._chips_do_move)
        tk.Label(header, text="Быстрый доступ", bg="#2b2b2b", fg="#ccc", font=("Segoe UI", 9, "bold")).pack(side="left")

        resources_frame = tk.Frame(w, bg="#2a2a2a", pady=4, padx=6)
        resources_frame.pack(fill="x")
        self.app.resources_frame = resources_frame
        self.app._flow_frame = None
        self.app._flow_items = []
        self.app._flow_lines = []
        self._add_resize_grip(w)

    # (удалено: T-CHIPS — отдых теперь в chips._rest)

    def _add_resize_grip(self, win):
        grip = tk.Frame(win, bg="#1a1a1a", cursor="bottom_right_corner")
        grip.place(relx=1.0, rely=1.0, anchor="se", width=15, height=15)
        grip.bind("<ButtonPress-1>", lambda e: self._start_resize(e, win))
        grip.bind("<B1-Motion>", self._do_resize)

    def _start_resize(self, event, win):
        self._resize_win = win
        self._resize_x = event.x_root - win.winfo_width()
        self._resize_y = event.y_root - win.winfo_height()

    def _do_resize(self, event):
        if not getattr(self, "_resize_win", None): return
        w = max(200, event.x_root - self._resize_x)
        h = max(100, event.y_root - self._resize_y)
        self._resize_win.geometry(f"{w}x{h}")

    # ---------- ЛОГИКА (СПЛИТ) ----------
    def _run_button(self, key, cmd):
        if key in CENTER_BUTTONS:
            if self.center_win is not None and self.center_win.winfo_exists():
                self.center_win.deiconify()
                self.center_win.lift()
                self._apply_pin()
            else:
                self._build_center()
                self._apply_pin()
            try:
                cmd()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[split] button '{key}' error: {e}")
            self.center_win.lift()
            self.center_win.attributes("-topmost", True)
            self.center_win.after(500, lambda: self.center_win.attributes("-topmost", False) if self.center_win else None)
        else:
            self.app.root.deiconify()
            self.app.root.lift()
            try:
                cmd()
            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"[split] button '{key}' error: {e}")
            finally:
                self.app.root.withdraw()

    # ---------- НОВОЕ: СВОЙ РЕДАКТОР И ГЛАВНЫЙ ВИД ----------
    def show_editor(self, title, build_fn):
        """Рисует редактор в СВОЁМ view_edit. Вызывается из gui.py."""
        if not self.center_win or not self.center_win.winfo_exists():
            self._build_center()
        self.center_win.deiconify()
        self.center_win.lift()
        self._apply_pin()

        self.app.view_main.pack_forget()
        for w in self.app.view_edit.winfo_children():
            w.destroy()
        
        header = tk.Frame(self.app.view_edit, bg="#2b2b2b", pady=8, padx=10)
        header.pack(fill="x")
        tk.Button(header, text="← Назад", command=self.show_main, bg="#555", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#777", activeforeground="white").pack(side="left")
        tk.Label(header, text=title, font=("Segoe UI", 13, "bold"), fg="white", bg="#2b2b2b").pack(side="left", padx=15)
        
        content = tk.Frame(self.app.view_edit, bg="#f4f4f4")
        content.pack(fill="both", expand=True)
        try:
            build_fn(content)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print(f"[split] Ошибка в редакторе '{title}': {e}")
        
        self.app.view_edit.pack(fill="both", expand=True)
        self.app._current_view = "edit"
        self.center_win.update_idletasks()
        self.center_win.update()

    def show_main(self):
        """Возвращает в главный вид."""
        for w in self.app.view_edit.winfo_children():
            w.destroy()
        self.app.view_edit.pack_forget()
        self.app.view_main.pack(fill="both", expand=True)
        self.app._current_view = "main"
        self.app._refresh()

    def _show_win(self, win):
        if win is None or not win.winfo_exists(): return False
        try:
            win.deiconify()
            win.lift()
            win.attributes("-topmost", True)
            def _force_focus():
                try:
                    win.attributes("-topmost", False)
                    win.lift()
                    win.focus_force()
                    win.update_idletasks()
                    win.update()
                except Exception:
                    pass
            win.after(50, _force_focus)
            return True
        except Exception as e:
            print(f"[split] _show_win failed: {e}")
            return False

    def _toggle_center(self):
        if self.center_win is None or not self.center_win.winfo_exists():
            self._build_center()
            self._apply_pin()
            return
        try:
            if self.center_win.state() == "withdrawn" or not self.center_win.winfo_ismapped():
                self._open_center()
            else:
                self._on_center_close()
        except Exception:
            self._open_center()

    def _toggle_chips(self):
        if self.chips_win is None or not self.chips_win.winfo_exists():
            self._build_chips()
            self.chips_win.deiconify()
            self.chips_win.lift()
            self.chips_win.focus_force()
            return
        try:
            if self.chips_win.state() == "withdrawn" or not self.chips_win.winfo_ismapped():
                self._open_chips()
                self.chips_win.deiconify()
                self.chips_win.lift()
                self.chips_win.focus_force()
            else:
                self._on_chips_close()
        except Exception:
            self._open_chips()

    def _show_char_sheet(self):
        """Кнопка Ч: toggle (показать/свернуть). Первый клик — с фокусом."""
        if self.center_win is None or not self.center_win.winfo_exists():
            self._build_center()
            self._apply_pin()
            self.show_main()
            return
        # Уже видимо → свернуть
        try:
            if self.center_win.state() != "withdrawn" and self.center_win.winfo_ismapped():
                self._on_center_close()
                return
        except Exception:
            pass
        # Скрыто → показать с фокусом (фокус-фикс)
        self._show_win(self.center_win)
        self.show_main()
        self._apply_pin()

    def _show_last_editor(self):
        """Кнопка О: toggle (показать/свернуть). Первый клик — с фокусом."""
        if self.center_win is None or not self.center_win.winfo_exists():
            self._build_center()
            self._apply_pin()
            return
        try:
            if self.center_win.state() != "withdrawn" and self.center_win.winfo_ismapped():
                self._on_center_close()
                return
        except Exception:
            pass
        self._show_win(self.center_win)
        self._apply_pin()

    def _open_center(self):
        if self.center_win is None or not self.center_win.winfo_exists():
            self._build_center()
            self._apply_pin()
        else:
            self._show_win(self.center_win)
            self._apply_pin()
        try:
            self.app._refresh()
        except Exception:
            pass

    def _open_chips(self):
        if self.chips_win is None or not self.chips_win.winfo_exists():
            self._build_chips()
        else:
            self._show_win(self.chips_win)

    def _on_center_close(self):
        if self.center_win is not None:
            self.center_win.withdraw()

    def _on_chips_close(self):
        if self.chips_win is not None:
            self.chips_win.withdraw()

    def _on_menu_close(self):
        if self.menu_win is not None:
            self.menu_win.withdraw()

    def set_active_window(self, win):
        if not self._win_ok(win):
            return
        close_prev = True
        if self.app.c:
            close_prev = self.app.c.settings.get("close_prev_window", True)
            
        if close_prev and self.current_editor_win is not None \
                and self.current_editor_win != win \
                and self._win_ok(self.current_editor_win):
            try:
                self.current_editor_win.destroy()
            except Exception:
                pass
                
        self.current_editor_win = win
        # Если магнит включен - двигаем к меню, если нет - оставляем на месте
        if self.app.c and self.app.c.settings.get("pin_editor_to_menu", True):
            self._apply_pin()
            
    def _apply_pin(self):
        if not self._win_ok(self.menu_win): return
        try:
            self.menu_win.update_idletasks()
            gap = 8
            x = self.menu_win.winfo_x() + self.menu_win.winfo_width() + gap
            y = self.menu_win.winfo_y()
            if self._win_ok(self.center_win):
                self.center_win.update_idletasks()
                if self.center_win.winfo_width() > 1:
                    self.center_win.geometry(f"+{x}+{y}")
            # Убрали привязку current_editor_win к меню
        except Exception:
            pass

    @staticmethod
    def _win_ok(w):
        return w is not None and w.winfo_exists()

    def _menu_start_move(self, event):
        if event.widget not in getattr(self.app, "_drag_handles", ()): return
        self._drag_x = event.x_root - self.menu_win.winfo_x()
        self._drag_y = event.y_root - self.menu_win.winfo_y()

    def _menu_do_move(self, event):
        if self._drag_x is None: return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.menu_win.geometry(f"+{x}+{y}")
        self._apply_pin()

    def _center_start_move(self, event):
        if event.widget.winfo_class() not in ("Frame", "Label", "Toplevel"): return
        self._drag_x = event.x_root - self.center_win.winfo_x()
        self._drag_y = event.y_root - self.center_win.winfo_y()

    def _center_do_move(self, event):
        if self._drag_x is None: return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.center_win.geometry(f"+{x}+{y}")
        self._apply_pin()

    def _chips_start_move(self, event):
        if event.widget.winfo_class() not in ("Frame", "Label", "Toplevel"): return
        self._drag_x = event.x_root - self.chips_win.winfo_x()
        self._drag_y = event.y_root - self.chips_win.winfo_y()

    def _chips_do_move(self, event):
        if self._drag_x is None: return
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.chips_win.geometry(f"+{x}+{y}")


def build(app):
    try:
        app._split = SplitView(app)
        return True
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"[split] build failed: {e}")
        try:
            app._split = None
        except Exception:
            pass
        return False