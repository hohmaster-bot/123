# gui.py — главный файл (v14)
# v14: вынос портрета (gui_media), кнопок (gui_buttons),
#      конфига (gui_app_config) и файловых операций (gui_file_ops)

import pystray
from PIL import Image, ImageDraw
import os
import threading
import json
import webbrowser
import tkinter as tk
from tkinter import messagebox, simpledialog, filedialog
from character import (Character, ensure_dirs, CHARACTERS_DIR,
                       PAIN_MAX, SKILL_TIER_NAMES, WEAPON_LEVELS,
                       ARMOR_DISPLAY, SHIELD_DISPLAY, BASE_DIR,
                       SOURCE_NAMES, DRIVE_KEYS, DRIVE_LEVEL_NAMES,
                       WEAPON_BONUS_CATALOG)
import gui_app_config
from gui_app_config import (load_app_config, save_app_config,
                            get_last_character, set_last_character,
                            CONFIG_FILE)
import gui_buttons
import gui_media
import gui_file_ops
import gui_menu
from gui_buttons import (DEFAULT_VISIBLE_BUTTONS,
                         FORCED_VISIBLE_BUTTONS)
import gui_combat
import gui_editors
import gui_inventory
import gui_rest
import gui_shop
import gui_stub
import gui_skills
import gui_spells
import gui_templates
import gui_training
import gui_wiki
import purchases as P
from gui_shared import (_load_image, _load_image_from_data,
                        bind_canvas_wheel, bind_context_menu,
                        bind_clipboard_all, ToolTip)
from gui_alphabet import TARGET_NAMES as SIT_TARGET_NAMES

# Глобальные опции отображения чарника (меню «Вид»)
DEFAULT_VIEW_OPTIONS = {
    "show_sources": True,
    "show_maneuver": True,
    "show_basics": True,
    "show_mastery": True,
    "show_tier": True,
    "show_saves_breakdown": True,
    "show_buffs_tags": True,
    "show_ignore_marks": True,
}

def _describe_effects(effects):
    parts = []
    for e in effects:
        t = e.get("target", "")
        v = e.get("value", 0)
        v_str = str(v)
        if t == "speed_mult":
            try:
                parts.append(f"×{int(v)/100:.2f}")
            except Exception:
                parts.append(f"×{v_str}")
        elif t == "speed":
            try:
                parts.append(f"{int(v):+d} фт")
            except Exception:
                parts.append(f"{v_str} фт")
        else:
            try:
                parts.append(
                    f"{int(v):+d} {SIT_TARGET_NAMES.get(t, t)}")
            except Exception:
                parts.append(
                    f"{v_str} {SIT_TARGET_NAMES.get(t, t)}")
    return ", ".join(parts)

# ===== Трей (v16) =====
# Иконка создаётся один раз в __init__ и живёт в отдельном daemon-потоке.
# _hide_to_tray только withdraw(); _restore_from_tray только deiconify().
# Остановка — _stop_tray() в _on_close (icon.stop() + Event.wait с таймаутом).

def _tray_mode(app):
    """Текущий режим окна для трея: 'split' / 'classic'."""
    if getattr(app, "_split", None) is not None:
        return "split"
    if app.c is not None and app.c.settings.get("ui_layout_mode") in ("split", "split_pinned"):
        return "split"
    return "classic"


def _make_tray_icon(app):
    """Создаёт pystray.Icon (без run). Меню — динамическое по режиму."""
    # Иконка из WP.png (256x256, лежит в DND/ рядом с кодом).
    # Fallback: старая нарисованная «W», если файла нет/битый.
    image = None
    try:
        _wp_path = os.path.join(BASE_DIR, "WP.png")
        if os.path.exists(_wp_path):
            image = Image.open(_wp_path)
            image.load()  # отвязываем от файла, чтобы не лочить
            image = image.convert("RGBA")
    except Exception as e:
        print(f"[tray] WP.png: {e}")
        image = None
    if image is None:
        image = Image.new('RGB', (64, 64), color=(26, 26, 26))
        d = ImageDraw.Draw(image)
        d.text((20, 20), "W", fill=(255, 255, 255))

    mode = _tray_mode(app)

    def _show(icon, item):
        app.root.after(0, app._restore_from_tray)

    def _quit(icon, item):
        def _do_quit():
            try:
                # Просто вызываем закрытие. Оно само покажет нужное окно.
                app._on_close()
            except RuntimeError:
                # Если mainloop уже мертв, просто выходим
                icon.stop()
                import os
                os._exit(0)
        try:
            app.root.after(0, _do_quit)
        except RuntimeError:
            # mainloop уже не работает (программа закрыта)
            icon.stop()

    def _menu(icon, item):
        app.root.after(0, lambda: app._on_tray_window("menu"))

    def _center(icon, item):
        app.root.after(0, lambda: app._on_tray_window("center"))

    def _chips(icon, item):
        app.root.after(0, lambda: app._on_tray_window("chips"))

    if mode == "split":
        items = (
            pystray.MenuItem("Меню", _menu, default=True),
            pystray.MenuItem("Чарник", _center),
            pystray.MenuItem("Быстрый доступ", _chips),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Завершить работу", _quit),
        )
    else:
        items = (
            pystray.MenuItem("Открыть", _show, default=True),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Завершить работу", _quit),
        )
    return pystray.Icon("WiPeFinder", image, "WiPeFinder",
                        menu=pystray.Menu(*items))

def _start_tray(app):
    """Создаёт иконку и запускает её в daemon-потоке. Идемпотентно."""
    if getattr(app, "_tray_icon", None) is not None:
        return
    app._tray_stop = threading.Event()
    app._tray_icon = _make_tray_icon(app)

    def _loop():
        try:
            app._tray_icon.run()
        finally:
            app._tray_stop.set()

    app._tray_thread = threading.Thread(
        target=_loop, name="pystray", daemon=True)
    app._tray_thread.start()


def _stop_tray(app):
    """Останавливает иконку и ждёт завершения потока (до 2 с)."""
    icon = getattr(app, "_tray_icon", None)
    if icon is None:
        return
    try:
        icon.stop()
    except Exception:
        pass
    ev = getattr(app, "_tray_stop", None)
    if ev is not None:
        ev.wait(timeout=2)
    app._tray_icon = None

class App:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WiPeFinder — D&D Чарник")
        self.root.geometry("1200x820")
        
        # Убираем системную рамку Windows
        self.root.overrideredirect(True)
        # Возвращаем окно в Alt-Tab / панель задач (иначе overrideredirect его прячет)
        gui_media.force_taskbar_alt_tab(self.root)
        self.c = None
        self._lines = []
        self._feat_line_map = {}
        self._bg_photo = None
        self._portrait_photo = None
        self._bg_timer = None
        self._portrait_timer = None
        self._canvas_tip = None
        self.force_free = False
        self._current_view = "main"
        self._desktop = None  # v1.1: desktop overlay (если режим "desktop")
        self.btn_ot = None
        self.btn_pain = None
        self.btn_morale = None
        self.btn_levelup = None
        cfg = load_app_config()
        self._view_options = dict(DEFAULT_VIEW_OPTIONS)
        self._view_options.update(cfg.get("view_options", {}))
        bind_clipboard_all(self.root)
        bind_context_menu(self.root)
        gui_menu.build_menu(self)
        self._build_layout()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
        self._load_or_new()
        # Трей всегда виден, пока программа работает (v16).
        self._tray_icon = None
        self._tray_thread = None
        self._tray_stop = None
        _start_tray(self)

    # ===== ОБЕРТКИ ФАЙЛОВЫХ ОПЕРАЦИЙ (gui_file_ops) =====
    def _load_or_new(self): gui_file_ops.load_or_new(self)
    def _new_character(self): gui_file_ops.new_character(self)
    def _rename_character(self): gui_file_ops.rename_character(self)
    def _open_characters_folder(self): gui_file_ops.open_characters_folder(self)
    def _open_character(self): gui_file_ops.open_character(self)
    def _save(self, silent=False): gui_file_ops.save(self, silent)
    def _import_character(self): gui_file_ops.import_character(self)
    def _import_character_url(self): gui_file_ops.import_character_url(self)
    def _export_character(self): gui_file_ops.export_character(self)
    def _export_pdf(self): gui_file_ops.export_pdf(self)
    def _on_close(self): gui_file_ops.on_close(self)
    def _copy_sheet(self): gui_file_ops.copy_sheet(self)

    def _rebuild_menu(self):
        """Перестроить меню-бар (для будущего UI-редактора меню)."""
        gui_menu.build_menu(self)

    def _stop_tray(self):
        """Остановить трей (вызывается из gui_file_ops.on_close)."""
        _stop_tray(self)

    def _on_tray_window(self, which):
        """Показать окно сплита из меню трея (всегда наверх)."""
        split = getattr(self, "_split", None)
        if split is None:
            return
        win = {"menu": split.menu_win,
               "center": split.center_win,
               "chips": split.chips_win}.get(which)

        # Если окно уничтожено — пересоздаём
        if win is None or not win.winfo_exists():
            if which == "center":
                split._build_center()
                split._apply_pin()
                win = split.center_win
            elif which == "chips":
                split._build_chips()
                win = split.chips_win
            elif which == "menu":
                split._build_menu()
                win = split.menu_win
            else:
                return

        # Всегда показываем (без проверки is_visible, как в кнопках Ч/О/Б)
        split._show_win(win)
        if which == "center":
            split._apply_pin()
            
        try:
            win.deiconify()
            win.lift()
            win.focus_force()
            win.update_idletasks()
            win.update()
        except Exception:
            pass
                    
    def get_dialog_parent(self):
        """Возвращает гарантированно видимое окно для Toplevel/диалогов."""
        split = getattr(self, "_split", None)
        if split is None:
            return self.root
            
        for attr in ("menu_win", "center_win", "chips_win"):
            w = getattr(split, attr, None)
            if w is not None and w.winfo_exists():
                try:
                    if w.winfo_viewable() and w.state() != "withdrawn":
                        return w
                except Exception:
                    pass
        # Если все скрыты — возвращаем menu_win (пусть диалог сам его поднимет)
        if split.menu_win is not None and split.menu_win.winfo_exists():
            return split.menu_win
        return self.root
    
    def _build_layout(self):
        mode = "split"
        if self.c:
            mode = self.c.settings.get("ui_layout_mode", "split")
        if mode == "desktop":
            import gui_desktop
            try:
                self._desktop = gui_desktop.DesktopView(self)
                return
            except Exception as e:
                print(f"[layout] desktop failed: {e}")
                # fallback: split
                mode = "split"
        if mode in ("split", "split_pinned"):
            import gui_split
            if gui_split.build(self):
                return
            # fallback: если split упал — рисуем classic
            print("[layout] split failed, falling back to classic")
        self._build_layout_classic()

    def _build_layout_classic(self):
        self.top = self.root  # Для внешних окон (Toplevel)
        top = tk.Frame(self.root, bg="#1a1a1a", pady=6, padx=10)
        top.pack(fill="x")
        self._top = top

        self.lbl_name = tk.Label(top, text="—", font=("Segoe UI", 14, "bold"), fg="white", bg="#1a1a1a")
        self.lbl_name.pack(side="left")
        
        self.lbl_class = tk.Label(top, text="", font=("Segoe UI", 11), fg="#ccc", bg="#1a1a1a")
        self.lbl_class.pack(side="left", padx=15)

        self.btn_levelup = tk.Button(top, text="⬆ Level Up", command=self._do_level_up,
                                     bg="#3a7a3a", fg="white", relief="flat",
                                     font=("Segoe UI", 10, "bold"),
                                     activebackground="#5aa05a", activeforeground="white")
        
        # --- Дальше идет остальной интерфейс ---
        row1 = tk.Frame(self.root, bg="#222", pady=4, padx=6)
        row1.pack(fill="x")
        row2 = tk.Frame(self.root, bg="#222", padx=6, pady=2)
        row2.pack(fill="x")
        gui_combat.build_combat_panel(self, row1, row2)

        self.resources_frame = tk.Frame(self.root, bg="#2a2a2a", pady=4, padx=6)
        self.resources_frame.pack(fill="x")

        self.paned = tk.PanedWindow(self.root, orient="horizontal", sashwidth=6, sashrelief="raised", bg="#444", bd=0)
        self.paned.pack(fill="both", expand=True, padx=5, pady=5)

        self.left = tk.Frame(self.paned, bg="#1a1a1a")
        self.paned.add(self.left, minsize=160, width=280)
        self.portrait_frame = tk.Frame(self.left, bg="#1a1a1a")
        self.portrait_frame.pack(fill="x")
        self.lbl_portrait = tk.Label(self.portrait_frame, text="[Портрет]", bg="#1a1a1a", fg="#888", cursor="hand2")
        self.lbl_portrait.pack(expand=True)
        self.lbl_portrait.bind("<Button-1>", lambda e: gui_media.expand_portrait(self))

        self.btn_container = tk.Frame(self.left, bg="#1a1a1a")
        self.btn_container.pack(fill="both", expand=True)
        self.buttons_canvas = tk.Canvas(self.btn_container, bg="#1a1a1a", highlightthickness=0)
        btn_scroll = tk.Scrollbar(self.btn_container, orient="vertical", command=self.buttons_canvas.yview)
        self.buttons_inner = tk.Frame(self.buttons_canvas, bg="#1a1a1a")
        self.buttons_inner.bind("<Configure>", lambda e: self.buttons_canvas.configure(scrollregion=self.buttons_canvas.bbox("all")))
        self.buttons_canvas.create_window((0, 0), window=self.buttons_inner, anchor="nw", tags="inner")
        self.buttons_canvas.configure(yscrollcommand=btn_scroll.set)
        self.buttons_canvas.bind("<Configure>", lambda e: self.buttons_canvas.itemconfigure("inner", width=e.width))
        self.buttons_canvas.pack(side="left", fill="both", expand=True)
        btn_scroll.pack(side="right", fill="y")
        bind_canvas_wheel(self.buttons_inner, self.buttons_canvas)
        bind_canvas_wheel(self.buttons_canvas, self.buttons_canvas)

        gui_buttons.rebuild_side_buttons(self)
        split = getattr(self, "_split", None)
        if split is not None and getattr(split, "menu_win", None) is not None:
            try:
                split._rebuild_menu_buttons()
            except Exception:
                pass

        self.right_container = tk.Frame(self.paned, bg="#1a1a1a")
        self.paned.add(self.right_container, minsize=400)
        self.view_main = tk.Frame(self.right_container, bg="#1a1a1a")
        self.info_canvas = tk.Canvas(self.view_main, bg="#1a1a1a", highlightthickness=0)
        scroll = tk.Scrollbar(self.view_main, orient="vertical", command=self.info_canvas.yview)
        self.info_canvas.configure(yscrollcommand=scroll.set)
        self.info_canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.info_canvas.bind("<Configure>", self._on_canvas_resize)
        bind_canvas_wheel(self.info_canvas, self.info_canvas)
        self.view_edit = tk.Frame(self.right_container, bg="#f4f4f4")
        self.view_main.pack(fill="both", expand=True)
        self.left.bind("<Configure>", self._on_left_resize)

        # --- Перетаскивание окна: ТОЛЬКО за шапки (menubar, top).
        #     Чипы, кнопки меню, саш PanedWindow — НЕ тащат окно.
        self._drag_handles = {self._menubar, self._top, self.lbl_name, self.lbl_class}
        for w in self._drag_handles:
            w.bind("<ButtonPress-1>", self._start_move)
            w.bind("<B1-Motion>", self._do_move)

    def _hide_to_tray(self):
        # Иконка уже создана в __init__ (_start_tray).
        split = getattr(self, "_split", None)
        if split is not None and getattr(split, "menu_win", None) is not None:
            # В сплите скрываем окна сплита, root и так скрыт
            for win in (split.menu_win, split.center_win, split.chips_win):
                if win and win.winfo_exists():
                    win.withdraw()
            return
        # В classic скрываем само окно
        self.root.overrideredirect(False)
        self.root.withdraw()

    def _restore_from_tray(self):
        split = getattr(self, "_split", None)
        if split is not None and getattr(split, "menu_win", None) is not None:
            # сплит: восстанавливаем окна сплита, self.root не трогаем
            try:
                split.menu_win.deiconify()
                split.menu_win.lift()
                gui_media.force_taskbar_alt_tab(split.menu_win)
                split.menu_win.focus_force()
            except Exception:
                pass
            return
        # classic
        self.root.deiconify()
        self.root.overrideredirect(True)
        gui_media.force_taskbar_alt_tab(self.root)
        self.root.lift()
        self.root.focus_force()

    def _start_move(self, event):
        # Клик должен прийти РОВНО в одну из «ручек»-шапок,
        # а не всплыть из дочерней кнопки (Файл/✖/—/Level Up).
        if event.widget not in getattr(self, "_drag_handles", ()):
            return
        self._drag_x = event.x_root - self.root.winfo_x()
        self._drag_y = event.y_root - self.root.winfo_y()

    def _do_move(self, event):
        x = event.x_root - self._drag_x
        y = event.y_root - self._drag_y
        self.root.geometry(f"+{x}+{y}")

    def _restore_window(self, event=None):
        self.root.deiconify()

    def _toggle_view_opt(self, key, var):
        self._view_options[key] = var.get()
        cfg = load_app_config()
        cfg["view_options"] = dict(self._view_options)
        save_app_config(cfg)
        self._refresh()

    def _open_editors_window(self, paid=None):
        import gui_editors_window
        gui_editors_window.open_editors_window(self, paid=paid)

    def _open_inventory(self):
        if not self.c: return
        gui_inventory.open_inventory(self)

    def _open_catalogs(self):
        if not self.c: return
        gui_shop.open_shop(self)

    def _edit_templates(self):
        gui_templates.edit_templates(self)

    def _edit_wiki(self):
        gui_wiki.edit_wiki(self)

    def _rest_dialog(self):
        gui_rest.rest_dialog(self)

    # (удалено: T-CHIPS — отдых теперь в chips._rest)

    def _do_short_rest(self):
        import gui_chips
        gui_chips.do_short_rest(self)

    def _do_long_rest(self):
        import gui_chips
        gui_chips.do_long_rest(self)

    def _show_main(self):
        if hasattr(self, "_split") and self._split:
            self._split.show_main()
            return
        for w in self.view_edit.winfo_children(): w.destroy()
        self.view_edit.pack_forget()
        self.view_main.pack(fill="both", expand=True)
        self._current_view = "main"
        self._refresh()

    def _show_editor(self, title, build_fn):
        if hasattr(self, "_split") and self._split:
            self._split.show_editor(title, build_fn)
            return
        self.view_main.pack_forget()
        for w in self.view_edit.winfo_children(): w.destroy()
        header = tk.Frame(self.view_edit, bg="#2b2b2b", pady=8, padx=10)
        header.pack(fill="x")
        tk.Button(header, text="← Назад", command=self._show_main, bg="#555", fg="white", relief="flat",
                  font=("Segoe UI", 10, "bold"), activebackground="#777", activeforeground="white").pack(side="left")
        tk.Label(header, text=title, font=("Segoe UI", 13, "bold"), fg="white", bg="#2b2b2b").pack(side="left", padx=15)
        content = tk.Frame(self.view_edit, bg="#f4f4f4")
        content.pack(fill="both", expand=True)
        build_fn(content)
        self.view_edit.pack(fill="both", expand=True)
        self._current_view = "edit"
        
        # ЖЕСТКИЙ ФИКС: Принудительно заставляем Tkinter перерисовать всё
        # (это сработает, даже если окно только что вышло из withdraw)
        try:
            parent = self.view_edit.winfo_toplevel()
            if parent and parent.winfo_exists():
                parent.update_idletasks()
                parent.update()
        except Exception:
            pass

    def _on_canvas_resize(self, event):
        if self._bg_timer:
            self.root.after_cancel(self._bg_timer)
        self._bg_timer = self.root.after(200, self._draw_canvas)

    def _on_left_resize(self, event=None):
        if self._portrait_timer:
            self.root.after_cancel(self._portrait_timer)
        self._portrait_timer = self.root.after(100, lambda: gui_media.update_portrait_size(self))

    def _set_music(self):
        if not self.c: return
        url = simpledialog.askstring("Музыка", "Ссылка:", initialvalue=self.c.music_url, parent=self.get_dialog_parent())
        if url is not None: self.c.music_url = url

    def _play_music(self):
        if not self.c or not self.c.music_url:
            messagebox.showinfo("Музыка", "Ссылка не задана", parent=self.get_dialog_parent())
            return
        webbrowser.open(self.c.music_url)

    def _maybe_remove_buff(self, idx, act=False, bid=None):
        import gui_chips
        gui_chips.maybe_remove_buff(self, idx, act=act, bid=bid)

    def _init_flow_container(self):
        import gui_chips
        gui_chips.init_flow_container(self)

    def _add_chip(self, widget):
        import gui_chips
        gui_chips.add_chip(self, widget)

    def _reflow_chips(self, event=None):
        import gui_chips
        gui_chips.reflow_chips(self, event)

    def _rebuild_resources_panel(self):
        import gui_chips
        gui_chips.rebuild_resources_panel(self)

    def _hard_refresh(self):
        if self.c: self.c.recompute_skills_invested()
        self._refresh()

    def _do_level_up(self):
        if not self.c: return
        c = self.c
        if c.xp < c.xp_threshold: return
        hp_die = int(c.char_class.get("hp_die", 8) or 8)
        roll = simpledialog.askinteger("Level Up", f"Уровень {c.level} → {c.level + 1}.\nСколько HP выпало на d{hp_die}?", initialvalue=hp_die // 2 + 1, minvalue=1, maxvalue=hp_die, parent=self.get_dialog_parent())
        if roll is None: return
        c.char_class["level"] = int(c.char_class.get("level", 1)) + 1
        c.char_class.setdefault("hp_rolls", []).append(int(roll))
        c.xp = max(0, c.xp - c.xp_threshold)
        gained_training = int(c.level) * 100
        c.training["available"] = int(c.training.get("available", 0)) + gained_training
        c.recompute_derived()
        self._refresh()
        messagebox.showinfo("Level Up", f"Новый уровень: {c.level}.\nHP-бросок: +{roll}.\nТренировки: +{gained_training}.\nОстаток XP: {c.xp}/{c.xp_threshold}", parent=self.get_dialog_parent())

    def _refresh(self):
        if not self.c: return
        if not (getattr(self, "root", None) and self.root.winfo_exists()):
            return
        c = self.c
        self._feat_line_map = {}
        self.lbl_name.config(text=c.name)
        self.lbl_class.config(text=f"{c.char_class['name']} {c.level}")
        closed = [ln for ln in c.lenses if c.lens_status(ln) == "closed"]
        failed = [ln for ln in c.lenses if c.lens_status(ln) == "failed"]
        if closed:
            self.lbl_name.config(text=f"{c.name}  🏁 ВЫ ЗАКРЫЛИ ЛИНЗУ: {closed[0].get('name','?')}", fg="#7fff7f")
        elif failed:
            self.lbl_name.config(text=f"{c.name}  💀 ВЫ ПРОВАЛИЛИ ЛИНЗУ: {failed[0].get('name','?')}", fg="#ff7f7f")
        else:
            self.lbl_name.config(text=c.name, fg="white")
        self.root.title(f"WiPeFinder — {c.name}")

        if self.btn_levelup is not None:
            if c.xp >= c.xp_threshold:
                if not self.btn_levelup.winfo_ismapped(): self.btn_levelup.pack(side="left", padx=10)
            else:
                if self.btn_levelup.winfo_ismapped(): self.btn_levelup.pack_forget()
                
        self._rebuild_resources_panel()
        gui_buttons.rebuild_side_buttons(self)

        bab = c.bab_base()
        temp = c.combat.get("hp_temp", 0)
        hp_line = f"HP:          {c.combat['hp_current']}/{c.hp_max_actual()}"
        if temp > 0: hp_line += f"  + 🛡 {temp}"
        
        ac_full, ac_touch, ac_flat, ac_parry = c.ac_full(), c.ac_touch(), c.ac_flat(), c.ac_parry()
        ac_sit = c.situational_bonus("ac")
        ac_tail = f"  ({ac_sit:+d} ситуативн.)" if ac_sit else ""
        
        base_spd = c.race.get("speed", 30)
        spd_flat = c.situational_bonus("speed")
        spd_mult = c.speed_multiplier()
        eq_spd = c.equipped_speed_penalty()
        ws = c.weight_status()
        spd_parts = []
        if spd_flat: spd_parts.append(f"{spd_flat:+d} фт")
        if eq_spd: spd_parts.append(f"броня −{eq_spd}")
        if ws in ("loaded", "over"): spd_parts.append("вес −10")
        if spd_mult != 1.0: spd_parts.append(f"×{spd_mult:.2f}")
        spd_line = f"Скорость:    {c.speed_total()} фт  ({', '.join(spd_parts)})" if spd_parts else f"Скорость:    {base_spd} фт"
        
        wt_lbl = {"light": "легко", "loaded": "нагружен", "over": "ПЕРЕГРУЗ"}[ws]
        wt_marker = "  ⚠ ВЫ НЕ МОЖЕТЕ УЙТИ" if ws == "over" else ("  ⚠ DEX→AC макс 2, штраф навыков −2" if ws == "loaded" else "")
        wt_line = f"Вес:         {c.total_weight_display()}  [{wt_lbl}]{wt_marker}"
        size = c.combat.get("size", "Medium")

        L = [f"Класс: {c.char_class['name']} {c.level}", f"XP: {c.xp}/{c.xp_threshold}", "", "═══ Боевые ═══", hp_line, wt_line,
             f"AC:          {ac_full}  (touch {ac_touch} / flat {ac_flat} / parry {ac_parry}){ac_tail}",
             f"Парирование: {c.total_parrying()}", f"ББА:         {bab:+d}", f"CMB:         {c.cmb_total():+d}   CMD: {c.cmd_total()}",
             f"Размер:      {size}", f"БП:          {c.pain_threshold['current']}/{c.pain_threshold['max']}",
             f"Баланс:      {c.balance['current']}/{c.balance['max']}", f"Дух:         {c.spirit['current']}/{c.spirit['max']}",
             spd_line, f"Инициатива:  {c.initiative_total():+d}  ({', '.join(c.initiative_breakdown()['parts'])})", f"Реакции:     {c.reactions}"]
        
        mb = c.morale_bonus()
        pm = c.pain_max
        pain_parts = []
        if c.pain_from_hp(): pain_parts.append(f"HP {c.pain_from_hp()}")
        if c.pain_extra: pain_parts.append(f"несним {c.pain_extra}")
        if c.pain_extra_temp: pain_parts.append(f"боль {c.pain_extra_temp}")
        pain_extra_txt = f"  ({', '.join(pain_parts)})" if pain_parts else ""
        pain_note = "  🚫 игнор" if (self._view_options.get("show_ignore_marks", True) and c.ignore_pain) else ""
        L.append(f"Боль:        {c.pain_level()}/{pm}{pain_extra_txt}" + pain_note + ("  💀 СМЕРТЬ" if c.pain_level() >= pm else ""))
        
        morale_note = "  🚫 игнор" if (self._view_options.get("show_ignore_marks", True) and c.ignore_negative_morale and c.morale < 0) else ""
        L.append(f"Мораль:      {c.morale}" + (f"  (бонус {mb:+d})" if mb else "") + morale_note)
        
        sit_d20 = c.situational_bonus("attack")
        dmg_mod = c.damage_modifier()
        pen_total = c.pain_penalty() + mb + sit_d20
        penalty_parts = []
        if c.pain_penalty(): penalty_parts.append(f"боль {c.pain_penalty():+d}")
        if mb: penalty_parts.append(f"мораль {mb:+d}")
        if sit_d20: penalty_parts.append(f"сит {sit_d20:+d}")
        pen_detail = f"  ({', '.join(penalty_parts)})" if penalty_parts else ""
        L.append(f"Штраф d20:   {pen_total:+d}{pen_detail}")
        L.append(f"Мод. урона:  {dmg_mod:+d}")

        if c.mana.get("enabled"):
            parts = [f"{nm} {val}" for nm, val in c.mana_detail()]
            detail = f"  ({', '.join(parts)})" if parts else ""
            L.append(f"Мана:        {c.mana['current']}/{c.mana['max']}{detail}")
            
        L.append("")
        L.append("Спасброски:")
        for key, name in [("fort", "Fort"), ("ref", "Ref"), ("will", "Will")]:
            b = c.save_breakdown(key)
            good = "хор." if key in c.char_class.get("good_saves", []) else "плох."
            if self._view_options.get("show_saves_breakdown", True):
                parts = [f"класс {b['auto']:+d}", f"{b['ability_stat']} {b['ability']:+d}"]
                for m in b["mods"]: parts.append(f"{m.get('source','?')} {m['value']:+d}")
                if b.get("penalty"): parts.append(f"боль/мор {b['penalty']:+d}")
                L.append(f"  {name}: {b['total']:+d}  [{good}, {', '.join(parts)}]")
            else:
                L.append(f"  {name}: {b['total']:+d}  [{good}]")

        if c.situational_bonuses:
            L.extend(["", "═══ 🎲 Бафы ═══"])
            show_bt = self._view_options.get("show_buffs_tags", True)
            for b in c.situational_bonuses:
                eff_txt = _describe_effects(b.get("effects", []))
                tags = []
                if show_bt:
                    if b.get("duration_rounds", 0) > 0: tags.append(f"⏱{b.get('duration_current', 0)}/{b['duration_rounds']}")
                    if b.get("charges_max", 0) > 0: tags.append(f"⚡{b.get('charges_current', 0)}/{b['charges_max']}")
                tag_str = f" [{' '.join(tags)}]" if tags else ""
                L.append(f"  • {b.get('name','?')}: {eff_txt}{tag_str}")

        L.extend(["", "═══ Характеристики ═══"])
        for ab, full in [("str","Сила"),("dex","Ловкость"),("con","Телосложение"),("int","Интеллект"),("wis","Мудрость"),("cha","Харизма")]:
            base_ab = c.abilities[ab]; dmg = c.ability_damage.get(ab, 0); eff = c.effective_ability(ab); sit_ab = c.situational_bonus(ab); mod = c.ability_modifier(ab)
            parts = []
            if dmg > 0: parts.extend([f"{eff}/{base_ab}", f"урон {dmg}"])
            else: parts.append(f"{base_ab}")
            if sit_ab: parts.append(f"баф {sit_ab:+d}")
            parts.append(f"мод {mod:+d}")
            L.append(f"  {full:14} " + "  ".join(parts))
            
        L.extend(["", f"Тренировки: {c.training['available']} (потрачено {c.training['spent']})"])
        if c.race.get("name"):
            L.extend(["", f"═══ Раса: {c.race['name']} ({c.race.get('type','')}) ═══"])
            for a in c.race.get("abilities", []):
                idx = len(L); uses = f" [{a.get('uses_current', 0)}/{a.get('uses_max', 0)}]" if a.get("uses") else ""
                L.append(f"  • {a['name']}{uses}"); self._feat_line_map[idx] = a
                
        if c.char_class.get("name"):
            L.extend(["", f"═══ Класс: {c.char_class['name']} ═══"])
            for a in c.char_class.get("abilities", []):
                idx = len(L); uses = f" [{a.get('uses_current', 0)}/{a.get('uses_max', 0)}]" if a.get("uses") else ""
                L.append(f"  • {a['name']}{uses}"); self._feat_line_map[idx] = a
                
        if c.feats:
            L.extend(["", "═══ Черты ═══"]); show_src = self._view_options.get("show_sources", True)
            for f in c.feats:
                idx = len(L)
                if show_src: L.append(f"  [{SOURCE_NAMES.get(f.get('source', ''), '?')}] {f['name']}")
                else: L.append(f"  {f['name']}")
                self._feat_line_map[idx] = f
                
        if isinstance(c.drives, dict) and any(c.drives.values()):
            L.extend(["", "═══ 🌀 Драйвы ═══"])
            for k, ru in list(DRIVE_KEYS):
                v = c.drives.get(k, 0)
                if v == 0: continue
                mark = " ⚠ мания" if v >= 5 else (" ★" if v >= 4 else "")
                idx = len(L); lvl_name = DRIVE_LEVEL_NAMES.get(v, "")
                L.append(f"  • {ru} [{v}] {lvl_name}{mark}"); self._feat_line_map[idx] = {"desc": f"Драйв: {ru}, уровень {v} ({lvl_name})", "link": ""}
            if c.drive_principles:
                L.append("  Принципы:")
                for p in c.drive_principles:
                    idx = len(L); dk = p.get("drive_key", ""); dr = dict(DRIVE_KEYS).get(dk, "?")
                    L.append(f"    • [{dr}] {p.get('name','?')}"); self._feat_line_map[idx] = {"desc": p.get("desc", ""), "link": ""}
                    
        if c.courts:
            L.extend(["", "═══ 🏛 Дворы ═══"])
            for ct in c.courts:
                idx = len(L); L.append(f"  • {ct.get('name','?')}: реп {ct.get('reputation', 0)}, Тир {ct.get('tier', 'I')}"); self._feat_line_map[idx] = {"desc": "", "link": ""}
                
        if c.court_quests:
            L.extend(["", "═══ 📜 Задания ═══"])
            for q in c.court_quests:
                idx = len(L); panel = " 📌" if q.get("show_on_panel") else ""
                L.append(f"  • {q.get('name','?')}{panel} [{q.get('court','?')}]"); self._feat_line_map[idx] = {"desc": q.get("desc", ""), "link": ""}
                
        if c.lenses:
            L.extend(["", "═══ 🔍 Линзы ═══"])
            for ln in c.lenses:
                idx = len(L); mark = "✓" if ln.get("done") else "○"
                L.append(f"  {mark} {ln.get('name','?')}"); self._feat_line_map[idx] = {"desc": ln.get("desc", ""), "link": ""}
                
        if c.quirks:
            L.extend(["", "═══ Квирки ═══"])
            for q in c.quirks:
                idx = len(L); parts = [q.get("seed",""), q.get("court",""), q.get("focus","")]; parts = [p for p in parts if p]
                prefix = f"[{'/'.join(parts)}] " if parts else ""
                L.append(f"  • {prefix}{q.get('name','?')}"); self._feat_line_map[idx] = {"desc": q.get("desc",""), "link": ""}
                
        if c.templates:
            L.extend(["", "═══ Шаблоны ═══"])
            for t in c.templates:
                idx = len(L); type_tag = f"[{t.get('type','')}] " if t.get("type") else ""
                L.append(f"  • {type_tag}{t.get('name','?')}"); self._feat_line_map[idx] = {"desc": t.get("desc",""), "link": ""}
                
        if c.attacks:
            L.extend(["", "═══ Атаки ═══"])
            show_src = self._view_options.get("show_sources", True); show_man = self._view_options.get("show_maneuver", True)
            for a in c.attacks:
                bonus = c.attack_bonus(a); ct, cm = c.attack_crit(a); crit = f"{ct}+ x{cm}"; dmg = a.get("damage_dice", "") or "—"; dmg_bonus = c.attack_damage_bonus(a)
                dmg_disp = f"{dmg} ({dmg_bonus:+d})" if dmg_bonus else dmg
                idx = len(L); maneuver_tag = " [прием]" if (show_man and a.get("is_maneuver")) else ""
                src_tag = f"[{SOURCE_NAMES.get(a.get('source', ''), '?')}] " if show_src else ""
                item_tag = ""
                iid = a.get("from_item")
                if iid:
                    it = c.items.get(iid)
                    if it:
                        short = it.get("name", "?")[:14]; item_tag = f" ⚔{short}" if a.get('name', '') != short else " ⚔"
                prof_tag = f" ✦{a['proficiency']}" if a.get("proficiency") and c.weapon_by_name(a["proficiency"]) else ""
                panel_tag = " 📌" if a.get("show_on_panel") else ""
                lucky_thr, _ = c.attack_lucky(a)
                L.append(f"  • {src_tag}{a['name']}{maneuver_tag}{item_tag}{prof_tag}{panel_tag}: {bonus:+d} / {dmg_disp} / крит {crit} / лаки {lucky_thr}+")
                self._feat_line_map[idx] = {"desc": a.get("desc", ""), "link": ""}
                w_obj = c.weapon_by_name(a.get("proficiency"))
                if w_obj and w_obj.get("bonuses"):
                    bon_names = [WEAPON_BONUS_CATALOG[entry.get("id")]["name"] for entry in w_obj.get("bonuses", []) if entry.get("id") in WEAPON_BONUS_CATALOG]
                    if bon_names: L.append("      ✦ Бонусы: " + ", ".join(bon_names))
                if a.get("master_ability"):
                    bdef = WEAPON_BONUS_CATALOG.get(a.get("master_ability_id", ""))
                    if bdef: L.append(f"      🗡 Мастерство: {bdef['name']} [{a.get('uses_current', 0)}/{a.get('uses_max', 0)}]")
                    
        if c.skills:
            L.extend(["", "═══ Навыки ═══"]); show_src = self._view_options.get("show_sources", True); show_tier = self._view_options.get("show_tier", True)
            for s in c.skills:
                tier_ru = SKILL_TIER_NAMES.get(s.get("tier", "normal"), "?"); bonus = c.skill_bonus(s); src_tag = f"[{SOURCE_NAMES.get(s.get('source', ''), '?')}] " if show_src else ""
                tier_tag = f"[{tier_ru}, ранг {s.get('rank', 0)}]" if show_tier else f"[ранг {s.get('rank', 0)}]"
                L.append(f"  {src_tag}{s['name']} {bonus:+d}  {tier_tag}")
                
        if c.proficiencies.get("weapons"):
            L.extend(["", "═══ Оружие ═══"]); show_src = self._view_options.get("show_sources", True); show_bas = self._view_options.get("show_basics", True)
            for w in c.proficiencies["weapons"]:
                lvl = WEAPON_LEVELS[w["level"]]; desc = w.get("desc", ""); basics_tag = " [основы]" if (show_bas and w.get("basics")) else ""
                src_tag = f"[{SOURCE_NAMES.get(w.get('source', ''), '?')}] " if show_src else ""
                L.append(f"  • {src_tag}{w['name']}: {lvl}{basics_tag} (сложн. {w['difficulty']}, масштаб {w['scale']})" + (f" — {desc}" if desc else ""))
                
        armor_ru = ARMOR_DISPLAY.get(c.proficiencies.get("armor"), "?"); shield_ru = SHIELD_DISPLAY.get(c.proficiencies.get("shields"), "?")
        L.extend(["", "═══ Владения ═══", f"  Броня: {armor_ru}", f"  Щит:   {shield_ru}"])
        if c.equipment.get("add_shield_ac_to_balance", False): L.append("  ✓ АЦ щита идёт в Баланс")
        
        if c.spells:
            from character import spell_display_name
            L.extend(["", "═══ Заклинания ═══"]); show_src = self._view_options.get("show_sources", True); show_mas = self._view_options.get("show_mastery", True)
            by_circle = {}
            for s in c.spells: by_circle.setdefault(s["circle"], []).append(s)
            for circle in sorted(by_circle.keys()):
                for s in by_circle[circle]:
                    idx = len(L); masteries = s.get("masteries", []); stars = sum(m.get("stars", 1) for m in masteries); mast = f" [маст. {stars}/3]" if (show_mas and stars) else ""
                    src_tag = f"[{SOURCE_NAMES.get(s.get('source', ''), '?')}] " if show_src else ""
                    extra = []
                    rng = c.spell_range_text(s)
                    if rng and rng != "—": extra.append(rng)
                    if s.get("is_aoe"):
                        shape = s.get("aoe_shape", ""); size = s.get("aoe_size", ""); aoe_txt = "АоЕ"
                        if shape: aoe_txt += f" {shape}"
                        if size: aoe_txt += f" {size}"
                        extra.append(aoe_txt)
                    extra_txt = f"  [{', '.join(extra)}]" if extra else ""
                    L.append(f"  Круг {circle}: {src_tag}{spell_display_name(s)}{mast}{extra_txt}"); self._feat_line_map[idx] = s
                    for m in masteries:
                        m_src = f"[{SOURCE_NAMES.get(m.get('source', ''), '?')}] " if show_src else ""
                        L.append(f"      ⭐ {m_src}{m.get('name','?')} ({'★' * m.get('stars',1)})")
                        
        if c.languages:
            show_src = self._view_options.get("show_sources", True)
            def _lang_str(l):
                src = f"[{SOURCE_NAMES.get(l.get('source', ''), '?')}] " if show_src else ""
                return src + l['name'] + ('(р)' if l['native'] else '')
            L.extend(["", "Языки: " + ", ".join(_lang_str(l) for l in c.languages)])
            
        if c.base["contents"]:
            L.extend(["", f"═══ База ({c.base['slots_max']} слотов) ═══"])
            for it in c.base["contents"]: L.append(f"  • {it['name']}")
            
        if c.notes: L.extend(["", "═══ Заметки ═══", c.notes])
        
        self._lines = L
        self._draw_canvas()
        gui_media.update_portrait_size(self)
        # T-CHIPS-BUTTONS: кнопки в чипах, update_combat_status больше не нужен.        # gui_combat.update_combat_status(self) — T-CHIPS-BUTTONS: кнопки в чипах

    def _draw_canvas(self):
        if not self.c: return
        canvas = self.info_canvas; canvas.delete("all")
        w, h = max(canvas.winfo_width(), 600), max(canvas.winfo_height(), 600)
        bg_data = self.c.background_b64 or self.c.background_image or self.c.portrait_b64 or self.c.portrait
        if bg_data:
            photo = _load_image_from_data(bg_data, w, h, mode="fill", darken=130)
            if photo:
                self._bg_photo = photo; canvas.create_image(0, 0, image=photo, anchor="nw")
        y = 10
        for i, line in enumerate(self._lines):
            tag = f"line_{i}"; color = "#aaddff" if i in self._feat_line_map else "white"
            if "💀" in line: color = "#ff4444"
            elif "⚠ ВЫ НЕ МОЖЕТЕ УЙТИ" in line: color = "#ff6666"
            elif "[нагружен]" in line: color = "#ffcc00"
            canvas.create_text(10, y, text=line, anchor="nw", fill=color, font=("Consolas", 11), tags=(tag,))
            feat = self._feat_line_map.get(i)
            if feat:
                tip_parts = []
                desc = feat.get("desc", "") or ""
                if desc:
                    tip_parts.append(desc)
                
                # Добавляем эффекты
                _effects = feat.get("effects", []) if not feat.get("is_stance") else feat.get("stance_effects", [])
                if _effects:
                    from gui_alphabet import TARGET_NAMES as _TN
                    eff_lines = []
                    for e in _effects:
                        tgt = _TN.get(e.get("target"), e.get("target"))
                        val = e.get("value", 0)
                        btype = e.get("bonus_type", "flat")
                        eff_lines.append(f"{val:+d} {tgt} ({btype})")
                    tip_parts.append("Эффекты: " + ", ".join(eff_lines))
                    
                if feat.get("link"):
                    tip_parts.append(f"🔗 {feat['link']}")
                    
                if tip_parts:
                    tip_text = "\n\n".join(tip_parts)
                    canvas.tag_bind(tag, "<Enter>", lambda e, t=tip_text: self._show_canvas_tip(t, e))
                    canvas.tag_bind(tag, "<Leave>", lambda e: self._hide_canvas_tip())
                    if feat.get("link"): 
                        canvas.tag_bind(tag, "<Button-1>", lambda e, u=feat["link"]: webbrowser.open(u))
                    canvas.tag_bind(tag, "<Leave>", lambda e: self._hide_canvas_tip())
                if feat.get("link"): canvas.tag_bind(tag, "<Button-1>", lambda e, u=feat["link"]: webbrowser.open(u))
            y += 18
        canvas.configure(scrollregion=(0, 0, w, max(y + 20, h)))

    def _show_canvas_tip(self, text, event):
        self._hide_canvas_tip()
        x, y = event.x_root + 15, event.y_root + 25
        self._canvas_tip = tk.Toplevel(self.root)
        self._canvas_tip.wm_overrideredirect(True); self._canvas_tip.wm_geometry(f"+{x}+{y}")
        tk.Label(self._canvas_tip, text=text, background="#ffffe0", relief="solid", borderwidth=1, wraplength=380, font=("Segoe UI", 10), justify="left", padx=8, pady=6).pack()

    def _hide_canvas_tip(self):
        if self._canvas_tip: self._canvas_tip.destroy(); self._canvas_tip = None

    def run(self):
        self.root.mainloop()

# (удалено: дубль _hide_to_tray — используется только метод App._hide_to_tray)
# (_lens_step вынесен в gui_chips.py, T-SPLIT-3.2)

if __name__ == "__main__":
    ensure_dirs()
    App().run()