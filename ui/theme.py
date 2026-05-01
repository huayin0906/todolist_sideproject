DARK = {
    "bg": "#1e1e2e",
    "bg2": "#181825",
    "bg3": "#252536",
    "border": "#313244",
    "text": "#cdd6f4",
    "text_muted": "#6c7086",
    "accent": "#89b4fa",
    "accent_hover": "#b4d0f7",
    "danger": "#f38ba8",
    "danger_hover": "#f7a8bb",
    "success": "#a6e3a1",
    "success_hover": "#c3edbe",
}

LIGHT = {
    "bg": "#eff1f5",
    "bg2": "#e6e9ef",
    "bg3": "#dce0e8",
    "border": "#ccd0da",
    "text": "#4c4f69",
    "text_muted": "#9ca0b0",
    "accent": "#1e66f5",
    "accent_hover": "#1550cc",
    "danger": "#d20f39",
    "danger_hover": "#a80b2d",
    "success": "#40a02b",
    "success_hover": "#2e7a1f",
}


def get_stylesheet(theme: str) -> str:
    c = DARK if theme == "dark" else LIGHT
    return f"""
/* ── window ───────────────────────────────────────────────────── */
QWidget {{
    background-color: {c['bg']};
    color: {c['text']};
    font-family: "Segoe UI", Arial, sans-serif;
    font-size: 13px;
    border: none;
    outline: none;
}}

#mainFrame {{
    border: 1px solid {c['border']};
    border-radius: 10px;
    background-color: {c['bg']};
}}

/* ── title bar ────────────────────────────────────────────────── */
#titleBar {{
    background-color: {c['bg2']};
    border-top-left-radius: 10px;
    border-top-right-radius: 10px;
}}

#titleLabel {{
    font-size: 14px;
    font-weight: bold;
    color: {c['text']};
    background: transparent;
}}

/* ── icon buttons (theme, settings, close) ────────────────────── */
#iconBtn {{
    background: transparent;
    color: {c['text_muted']};
    border-radius: 5px;
    font-size: 14px;
}}
#iconBtn:hover {{
    background-color: {c['border']};
    color: {c['text']};
}}

#closeBtn {{
    background: transparent;
    color: {c['text_muted']};
    border-radius: 5px;
    font-size: 13px;
}}
#closeBtn:hover {{
    background-color: {c['danger']};
    color: #ffffff;
}}

/* ── task list ────────────────────────────────────────────────── */
QListWidget {{
    background-color: {c['bg']};
    border: none;
    padding: 4px;
}}
QListWidget::item {{
    background-color: {c['bg3']};
    border-radius: 6px;
    margin: 2px 4px;
    padding: 0;
}}
QListWidget::item:selected {{
    background-color: {c['border']};
    outline: none;
}}
QListWidget::item:hover {{
    background-color: {c['border']};
}}

/* ── task item widget ─────────────────────────────────────────── */
#taskItem {{
    background: transparent;
}}

QCheckBox {{
    background: transparent;
    spacing: 6px;
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border: 2px solid {c['border']};
    border-radius: 4px;
    background: {c['bg']};
}}
QCheckBox::indicator:checked {{
    background-color: {c['accent']};
    border-color: {c['accent']};
    image: none;
}}
QCheckBox::indicator:hover {{
    border-color: {c['accent']};
}}

#taskLabel {{
    background: transparent;
    color: {c['text']};
}}
#taskLabelDone {{
    background: transparent;
    color: {c['text_muted']};
    text-decoration: line-through;
}}

#schedBadge {{
    background-color: {c['bg2']};
    color: {c['text_muted']};
    border-radius: 3px;
    font-size: 10px;
    padding: 1px 4px;
}}

#editBtn {{
    background: transparent;
    color: {c['text_muted']};
    border-radius: 4px;
    font-size: 13px;
}}
#editBtn:hover {{
    background-color: {c['accent']};
    color: #ffffff;
}}

#deleteBtn {{
    background: transparent;
    color: {c['text_muted']};
    border-radius: 4px;
    font-size: 12px;
}}
#deleteBtn:hover {{
    background-color: {c['danger']};
    color: #ffffff;
}}

/* ── bottom bar ───────────────────────────────────────────────── */
#bottomBar {{
    background-color: {c['bg2']};
    border-bottom-left-radius: 10px;
    border-bottom-right-radius: 10px;
}}

#addBtn {{
    background-color: {c['success']};
    color: #ffffff;
    border-radius: 6px;
    font-size: 13px;
    font-weight: bold;
    padding: 6px 16px;
}}
#addBtn:hover {{
    background-color: {c['success_hover']};
}}

/* ── dialogs ──────────────────────────────────────────────────── */
QDialog {{
    background-color: {c['bg']};
    color: {c['text']};
}}

QLabel {{
    background: transparent;
    color: {c['text']};
}}

QLineEdit, QTextEdit, QComboBox {{
    background-color: {c['bg3']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 4px 8px;
    selection-background-color: {c['accent']};
}}
QSpinBox, QTimeEdit, QDateTimeEdit {{
    background-color: {c['bg3']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 5px;
    padding: 4px 24px 4px 8px;
    selection-background-color: {c['accent']};
}}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus,
QSpinBox:focus, QDateTimeEdit:focus, QTimeEdit:focus {{
    border-color: {c['accent']};
}}

QComboBox::drop-down {{
    border: none;
    background: transparent;
}}
QComboBox QAbstractItemView {{
    background-color: {c['bg3']};
    color: {c['text']};
    border: 1px solid {c['border']};
    selection-background-color: {c['accent']};
    selection-color: #ffffff;
}}

QSpinBox::up-button, QSpinBox::down-button,
QTimeEdit::up-button, QTimeEdit::down-button,
QDateTimeEdit::up-button, QDateTimeEdit::down-button {{
    background: {c['border']};
    border: none;
    border-radius: 3px;
    width: 18px;
    subcontrol-origin: border;
}}
QSpinBox::up-button {{ subcontrol-position: top right; }}
QSpinBox::down-button {{ subcontrol-position: bottom right; }}
QTimeEdit::up-button {{ subcontrol-position: top right; }}
QTimeEdit::down-button {{ subcontrol-position: bottom right; }}
QDateTimeEdit::up-button {{ subcontrol-position: top right; }}
QDateTimeEdit::down-button {{ subcontrol-position: bottom right; }}

QSpinBox::up-button:hover, QSpinBox::down-button:hover,
QTimeEdit::up-button:hover, QTimeEdit::down-button:hover,
QDateTimeEdit::up-button:hover, QDateTimeEdit::down-button:hover {{
    background: {c['accent']};
}}

QDialogButtonBox QPushButton {{
    background-color: {c['accent']};
    color: #ffffff;
    border-radius: 5px;
    padding: 6px 18px;
    font-weight: bold;
}}
QDialogButtonBox QPushButton:hover {{
    background-color: {c['accent_hover']};
    color: {c['bg']};
}}
QDialogButtonBox QPushButton[text="Cancel"] {{
    background-color: {c['bg3']};
    color: {c['text']};
}}
QDialogButtonBox QPushButton[text="Cancel"]:hover {{
    background-color: {c['border']};
}}

QGroupBox {{
    border: 1px solid {c['border']};
    border-radius: 6px;
    margin-top: 8px;
    padding-top: 8px;
    font-weight: bold;
    color: {c['text_muted']};
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 8px;
}}

QCheckBox#notifCheck {{
    font-weight: bold;
}}

/* ── scroll bar ───────────────────────────────────────────────── */
QScrollBar:vertical {{
    background: {c['bg']};
    width: 6px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {c['border']};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::handle:vertical:hover {{
    background: {c['text_muted']};
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
"""
