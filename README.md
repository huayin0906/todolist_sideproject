# To-Do List Desktop App

A lightweight, always-visible desktop to-do list built with **Python + PyQt6**.  
Lives on your desktop like a sticky note — other windows can cover it naturally.  
All data is stored **locally only**. Nothing is sent to any server.

---

## Features

- **Sticky-note window** — sits on the desktop, covered by browsers and other apps
- **System tray icon** — minimise to tray, double-click to show/hide
- **Drag & drop** task reordering
- **Click to complete** — click any task to mark it done
- **Smart reset schedules**

  | Type | Behaviour |
  |------|-----------|
  | None | No auto-reset |
  | Daily | Resets every day at a chosen time (default 00:00 UTC+8) |
  | Every N days | Resets every N days at a chosen time |
  | Weekly | Resets on a chosen weekday at a chosen time |
  | Fixed deadline | One-time deadline, task is not reset |

- **Native Windows toast notifications** before reset or deadline (configurable remind time, custom message)
- **Dark / light mode** toggle in the title bar
- **Resizable** — drag any edge or corner
- **Local storage** at `%USERPROFILE%\.todolist\data.json`

---

## Quick Start (from source)

**Requirements:** Windows 10 / 11, Python 3.9+

```bash
# 1. Clone
git clone https://github.com/huayin0906/todolist.git
cd todolist

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python main.py
```

---

## Download (pre-built)

Download the latest `ToDoList.exe` from the [Releases](../../releases) page — no Python needed.

> On first launch, Windows SmartScreen may warn about an unsigned executable.  
> Click **"More info" → "Run anyway"** to proceed.

---

## Build exe yourself

```bash
pip install pyinstaller
pip install -r requirements.txt
pyinstaller ToDoList.spec
# Output → dist/ToDoList.exe
```

---

## Project Structure

```
├── main.py                  # Entry point
├── requirements.txt         # Runtime dependencies
├── ToDoList.spec            # PyInstaller build spec
├── app.ico                  # App icon (used by the build)
├── core/
│   ├── models.py            # Task, Schedule, Notification, AppSettings dataclasses
│   ├── storage.py           # JSON load / save  (~/.todolist/data.json)
│   ├── task_manager.py      # CRUD + reorder operations
│   └── scheduler.py         # QTimer-based reset & notification engine
└── ui/
    ├── theme.py             # Dark / light QSS stylesheets (Catppuccin palette)
    ├── task_item.py         # Draggable task row widget
    ├── task_dialog.py       # Add / edit task dialog
    ├── settings_dialog.py   # Settings dialog (theme, timezone, test notification)
    └── main_window.py       # Frameless sticky-note window + system tray
```

---

## Data & Privacy

All task data is saved to `%USERPROFILE%\.todolist\data.json` on your local machine.  
The app makes **no network requests** of any kind.

---

## CI / CD

| Trigger | Action |
|---------|--------|
| Push or PR → `main` | Lint (`flake8`) + import validation |
| Push a tag `v*` | Build `ToDoList.exe` on Windows and publish a GitHub Release |

See [`.github/workflows/`](.github/workflows/) for details.

---

## Contributing

1. Fork the repo
2. Create a feature branch: `git checkout -b feat/your-feature`
3. Commit your changes
4. Open a pull request against `main`
