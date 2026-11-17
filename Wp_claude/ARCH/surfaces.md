# Modes (D3)

Two exclusive modes over the same core state. Exactly one is active. Enabling one disables the other.
Each mode has its own settings (separate profiles, nothing shared except language/theme if the owner wants).
Both modes have an edit mode; it works differently in each.

## Classic
- Normal window, in taskbar, reachable by Alt-Tab, full screen. Whole character sheet, easy to read.
- Editors open inside the window (pages/tabs), not as floating windows.
- Global hotkey shows/hides it: Ctrl+Shift+W.
- Edit mode: forms and lists inside the sheet.

## Overlay (light)
- Frameless always-on-top panels on the desktop. Empty space is click-through.
- Panels are user-chosen: chip groups, action buttons, log, mini-stats. Each has position, size, opacity.
- Lock mode (clicks only) vs edit mode (drag/resize/choose panels).
- Classic and Overlay (light) have different interfaces and different editors; no shared editor window.

## Tray
Switch mode (Classic <-> Overlay), toggle overlay edit mode, quit.

## Panel contract
- A panel type = id + factory + config schema, registered in a panel registry.
- Reads state from core, emits commands only (D5). Re-renders on the core `changed` signal.
- Panel types may be reused by both modes; placement and config are per mode.

## UI profile (per user, not per character)
Two independent blocks: `classic` and `overlay` (panels, positions per monitor, opacity, hotkeys), plus language and theme.

## Risks for the spike
- Exclusive-fullscreen games draw above any overlay; borderless/windowed are fine.
- Multi-monitor and DPI scaling; positions must survive monitor changes.
- Global hotkey needs Win32 `RegisterHotKey` (Qt has no built-in global hotkey).
