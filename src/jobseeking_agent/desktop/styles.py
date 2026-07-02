APP_STYLES = """
QMainWindow {
    background: #f4f7fa;
    color: #17202a;
}
QMenuBar {
    background: #ffffff;
    border-bottom: 1px solid #dde3ea;
    padding: 4px 8px;
}
QMenuBar::item {
    padding: 6px 10px;
    border-radius: 5px;
}
QMenuBar::item:selected {
    background: #eef6f4;
}
QWidget#leftPanel {
    background: #ffffff;
    border-right: 1px solid #d9e2ec;
}
QLabel#sidebarBrand {
    color: #17202a;
    font-size: 18px;
    font-weight: 800;
}
QLabel#sidebarCaption {
    color: #64748b;
    font-size: 12px;
}
QSplitter#mainSplitter::handle {
    background: #d9e2ec;
    width: 1px;
}
QListWidget#sidebar {
    background: transparent;
    border: 0;
    padding: 0;
    outline: 0;
}
QListWidget#sidebar::item {
    min-height: 40px;
    padding: 9px 12px;
    margin: 4px 0;
    border-radius: 7px;
    color: #334155;
}
QListWidget#sidebar::item:selected {
    background: #e5f3ef;
    color: #0f766e;
    font-weight: 700;
}
QListWidget#sidebar::item:hover {
    background: #f2f7f6;
}
QGroupBox {
    background: #ffffff;
    border: 1px solid #dce5ee;
    border-radius: 8px;
    margin-top: 14px;
    padding: 16px;
    font-weight: 600;
}
QGroupBox#metricCard {
    border: 1px solid #dbe7e3;
    background: #fbfefd;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 5px;
    color: #1f2937;
}
QLineEdit, QTextEdit, QComboBox {
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 9px 10px;
    background: #ffffff;
    selection-background-color: #0f766e;
}
QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
    border: 1px solid #0f766e;
    background: #fcfffe;
}
QPushButton {
    border: 1px solid #0f766e;
    border-radius: 6px;
    padding: 9px 14px;
    color: #0f766e;
    background: #ffffff;
    font-weight: 600;
}
QPushButton:hover {
    background: #ecfdf5;
}
QPushButton:pressed {
    background: #d9f5ec;
}
QPushButton#primaryButton {
    background: #0f766e;
    color: #ffffff;
}
QPushButton#primaryButton:hover {
    background: #0b615a;
}
QTableWidget {
    background: #ffffff;
    alternate-background-color: #f8fafc;
    border: 1px solid #dce5ee;
    border-radius: 8px;
    gridline-color: #e2e8f0;
    selection-background-color: #dff2ec;
    selection-color: #17202a;
}
QHeaderView::section {
    background: #f1f5f9;
    color: #334155;
    border: 0;
    border-bottom: 1px solid #dce5ee;
    padding: 8px;
    font-weight: 700;
}
QLabel#metricValue {
    font-size: 30px;
    font-weight: 700;
    color: #17202a;
}
QLabel#metricLabel {
    color: #64748b;
}
"""
