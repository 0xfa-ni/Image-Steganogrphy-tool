"""
SecureSteg — theme.py
Color palette (matches the original CSS custom properties) and global QSS.
"""

BG          = "#08090C"
PANEL       = "#101218"
PANEL_2     = "#161922"
RAISED      = "#1C1F28"
BORDER      = "#262A35"
BORDER_2    = "#353A48"
TEXT        = "#EDEFF4"
TEXT_2      = "#9AA2B1"
TEXT_3      = "#5B6472"
ACCENT      = "#D7DCE5"
ACCENT_DIM  = "rgba(215,220,229,0.10)"
ACCENT_LINE = "rgba(215,220,229,0.35)"
GREEN       = "#6FE3A8"
GREEN_BG    = "rgba(111,227,168,0.08)"
RED         = "#E5484D"
RED_BG      = "rgba(229,72,77,0.08)"
AMBER       = "#E5A93D"
RADIUS      = 8
RADIUS_SM   = 5

MONO = "Consolas, 'Courier New', monospace"
SANS = "'Segoe UI', -apple-system, sans-serif"

GLOBAL_QSS = f"""
QMainWindow {{
    background: {BG};
}}

QWidget {{
    background: transparent;
    color: {TEXT};
    font-family: {SANS};
    font-size: 13px;
}}

QLabel {{
    background: transparent;
}}

#PageRoot {{
    background: {BG};
}}

QScrollArea {{
    border: none;
    background: transparent;
}}

QScrollBar:vertical {{
    background: {PANEL};
    width: 10px;
    border-radius: 5px;
}}
QScrollBar::handle:vertical {{
    background: {BORDER_2};
    border-radius: 5px;
    min-height: 24px;
}}
QScrollBar::handle:vertical:hover {{
    background: {TEXT_3};
}}
QScrollBar::add-line, QScrollBar::sub-line {{
    height: 0px;
}}

/* ---------- Sidebar ---------- */
#Sidebar {{
    background: {PANEL};
    border-right: 1px solid {BORDER};
}}
#BrandName {{
    font-size: 15px;
    font-weight: 700;
    color: {TEXT};
}}
#BrandTag {{
    font-size: 10px;
    color: {TEXT_3};
}}
#BrandMark {{
    font-family: {MONO};
    font-size: 18px;
    color: {ACCENT};
    font-weight: 700;
}}
#NavLabel {{
    font-size: 10px;
    font-weight: 700;
    color: {TEXT_3};
    letter-spacing: 1px;
}}
QPushButton#NavBtn {{
    text-align: left;
    padding: 8px 10px;
    border: none;
    border-radius: {RADIUS_SM}px;
    background: transparent;
    color: {TEXT_2};
    font-size: 12.5px;
}}
QPushButton#NavBtn:hover {{
    background: {RAISED};
    color: {TEXT};
}}
QPushButton#NavBtn[active="true"] {{
    background: rgba(215,220,229,0.10);
    color: {ACCENT};
    font-weight: 600;
}}
#SidebarFoot {{
    font-size: 10.5px;
    color: {TEXT_3};
    border-top: 1px solid {BORDER};
    padding-top: 12px;
}}

/* ---------- Main content ---------- */
#ViewEyebrow {{
    font-family: {MONO};
    font-size: 11px;
    color: {TEXT_3};
    letter-spacing: 1px;
}}
#ViewTitle {{
    font-size: 24px;
    font-weight: 700;
    color: {TEXT};
}}
#ViewSub {{
    font-size: 13px;
    color: {TEXT_2};
}}

/* ---------- Panel ---------- */
#Panel {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: {RADIUS}px;
}}
#PanelHead {{
    font-size: 13px;
    font-weight: 600;
    color: {TEXT};
}}
#PanelStep {{
    background: rgba(215,220,229,0.10);
    border: 1px solid rgba(215,220,229,0.35);
    color: {ACCENT};
    font-family: {MONO};
    font-size: 11px;
    font-weight: 700;
    border-radius: 5px;
}}

/* ---------- Drop zone ---------- */
#DropZone {{
    border: 1px dashed {BORDER_2};
    border-radius: {RADIUS}px;
    background: transparent;
}}
#DropZone:hover {{
    border-color: {ACCENT};
}}
#DropZone[hasimage="true"] {{
    border-style: solid;
}}
#DropIcon {{
    font-size: 22px;
    color: {TEXT_3};
}}
#DropText {{
    font-size: 13px;
    color: {TEXT};
    font-weight: 500;
}}
#DropSub {{
    font-size: 11px;
    color: {TEXT_3};
}}

/* ---------- Stat ---------- */
#StatVal {{
    font-size: 16px;
    font-weight: 700;
    color: {TEXT};
    font-family: {MONO};
}}
#StatLbl {{
    font-size: 10.5px;
    color: {TEXT_3};
}}

/* ---------- Form ---------- */
#FieldLabel {{
    font-size: 10.5px;
    font-weight: 600;
    color: {TEXT_2};
    letter-spacing: 0.5px;
}}
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {RAISED};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    color: {TEXT};
    padding: 8px 10px;
    font-size: 13px;
}}
QLineEdit:focus, QTextEdit:focus {{
    border-color: {ACCENT_LINE.replace('rgba(', 'rgba(') if False else '#8b93a3'};
}}

/* ---------- Technique buttons ---------- */
QPushButton#TechBtn {{
    padding: 6px 14px;
    border-radius: {RADIUS_SM}px;
    border: 1px solid {BORDER};
    background: {RAISED};
    color: {TEXT_2};
    font-size: 12px;
}}
QPushButton#TechBtn:hover {{
    border-color: #8b93a3;
    color: {TEXT};
}}
QPushButton#TechBtn[active="true"] {{
    border-color: #8b93a3;
    background: rgba(215,220,229,0.10);
    color: {ACCENT};
    font-weight: 600;
}}

/* ---------- Key display ---------- */
#KeyDisplay {{
    background: {BG};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    color: {ACCENT};
    font-family: {MONO};
    font-size: 11px;
    padding: 10px 12px;
}}

/* ---------- Buttons ---------- */
QPushButton#PrimaryBtn {{
    background: {ACCENT};
    border: none;
    border-radius: {RADIUS_SM}px;
    color: #0A0B0E;
    font-size: 13px;
    font-weight: 700;
    padding: 11px;
}}
QPushButton#PrimaryBtn:hover {{
    background: #c3c9d4;
}}
QPushButton#PrimaryBtn:disabled {{
    background: #4a4d55;
    color: #888;
}}

QPushButton#GhostBtn {{
    background: transparent;
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    color: {TEXT_2};
    font-size: 12px;
    padding: 7px 14px;
}}
QPushButton#GhostBtn:hover {{
    border-color: #8b93a3;
    color: {ACCENT};
}}

QPushButton#LinkBtn {{
    background: none;
    border: none;
    color: {ACCENT};
    font-size: 12px;
    text-decoration: underline;
}}

/* ---------- Alerts ---------- */
#AlertSuccess {{
    background: {GREEN_BG};
    border: 1px solid rgba(111,227,168,0.25);
    color: {GREEN};
    border-radius: {RADIUS_SM}px;
    padding: 10px 13px;
    font-size: 12.5px;
}}
#AlertError {{
    background: {RED_BG};
    border: 1px solid rgba(229,72,77,0.25);
    color: {RED};
    border-radius: {RADIUS_SM}px;
    padding: 10px 13px;
    font-size: 12.5px;
}}

/* ---------- Decoded result ---------- */
#DecodedBox {{
    background: {RAISED};
    border: 1px solid {BORDER_2};
    border-radius: {RADIUS_SM}px;
}}
#DecodedLabel {{
    font-size: 10px;
    font-weight: 700;
    color: {ACCENT};
    letter-spacing: 0.5px;
}}
#DecodedText {{
    font-size: 14px;
    color: {TEXT};
}}

/* ---------- Info box ---------- */
#InfoBox {{
    background: {RAISED};
    border: 1px solid {BORDER};
    border-left: 3px solid {ACCENT};
    border-radius: {RADIUS_SM}px;
    color: {TEXT_2};
    font-size: 12px;
    padding: 13px 15px;
}}

/* ---------- Table ---------- */
QTableWidget {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
    gridline-color: {BORDER};
    color: {TEXT};
    font-family: {MONO};
    font-size: 12px;
}}
QHeaderView::section {{
    background: {RAISED};
    color: {TEXT_3};
    border: none;
    border-bottom: 1px solid {BORDER};
    padding: 8px 12px;
    font-size: 10px;
    font-weight: 700;
}}
QTableWidget::item {{
    padding: 4px 10px;
    border-bottom: 1px solid {BORDER};
}}

/* ---------- PSNR big number ---------- */
#PsnrNum {{
    font-size: 40px;
    font-weight: 700;
    color: {ACCENT};
}}
#PsnrUnit {{
    font-size: 15px;
    color: {TEXT_3};
}}
#PsnrVerdict {{
    font-size: 13px;
    color: {TEXT_2};
}}

/* ---------- Steganalysis verdict ---------- */
#StegVerdictClean {{
    background: {GREEN_BG};
    border: 1px solid rgba(111,227,168,0.25);
    color: {GREEN};
    font-size: 15px;
    font-weight: 700;
    border-radius: {RADIUS_SM}px;
    padding: 14px 16px;
}}
#StegVerdictSuspect {{
    background: rgba(229,163,61,0.10);
    border: 1px solid rgba(229,163,61,0.30);
    color: {AMBER};
    font-size: 15px;
    font-weight: 700;
    border-radius: {RADIUS_SM}px;
    padding: 14px 16px;
}}
#StegVerdictLikely {{
    background: {RED_BG};
    border: 1px solid rgba(229,72,77,0.25);
    color: {RED};
    font-size: 15px;
    font-weight: 700;
    border-radius: {RADIUS_SM}px;
    padding: 14px 16px;
}}

/* ---------- Bit plane ---------- */
#BitplaneCard {{
    background: {PANEL};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
}}
#BitplaneLabel {{
    font-family: {MONO};
    font-size: 11px;
    color: {TEXT_2};
    border-bottom: 1px solid {BORDER};
    padding: 6px 10px;
}}

/* ---------- History ---------- */
#HistoryItem {{
    background: {RAISED};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
}}
#HistoryMeta {{
    font-size: 10px;
    color: {TEXT_3};
    font-family: {MONO};
}}
#HistoryMsg {{
    font-size: 13px;
    color: {TEXT};
}}
#BadgeEncode {{
    background: rgba(215,220,229,0.10);
    color: {ACCENT};
    border: 1px solid {BORDER_2};
    border-radius: 10px;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
}}
#BadgeDecode {{
    background: {GREEN_BG};
    color: {GREEN};
    border: 1px solid rgba(111,227,168,0.25);
    border-radius: 10px;
    font-size: 10px;
    font-weight: 700;
    padding: 3px 8px;
}}
QPushButton#DeleteBtn {{
    background: none;
    border: none;
    color: {TEXT_3};
    font-size: 13px;
}}
QPushButton#DeleteBtn:hover {{
    color: {RED};
}}

/* ---------- Learn ---------- */
#LearnTitle {{
    font-size: 15px;
    font-weight: 700;
    color: {TEXT};
}}
#LearnBody {{
    font-size: 12.5px;
    color: {TEXT_2};
}}
#LearnCard {{
    background: {RAISED};
    border: 1px solid {BORDER};
    border-radius: {RADIUS_SM}px;
}}
#LearnCardTitle {{
    font-family: {MONO};
    font-size: 12px;
    font-weight: 700;
    color: {ACCENT};
}}
#LearnCardFormula {{
    font-family: {MONO};
    font-size: 11px;
    color: {TEXT};
    background: {BG};
    border-radius: 4px;
    padding: 4px 8px;
}}
#LearnCardBody {{
    font-size: 11px;
    color: {TEXT_3};
}}
"""
