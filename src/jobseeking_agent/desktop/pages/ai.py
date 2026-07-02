from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QPushButton,
    QTextEdit,
    QWidget,
)

from jobseeking_agent.desktop.widgets import page_container


def build_ai_page(window: QWidget) -> QWidget:
    widget = page_container()
    layout = widget.layout()

    controls = QGroupBox("Application Materials")
    controls_layout = QGridLayout(controls)
    window.ai_job_select = QComboBox()
    window.cover_letter_output = QTextEdit()
    window.cover_letter_output.setMinimumHeight(360)
    generate_button = QPushButton("Generate Cover Letter")
    generate_button.setObjectName("primaryButton")
    generate_button.clicked.connect(window.generate_cover_letter_for_selected_job)
    controls_layout.addWidget(QLabel("Job"), 0, 0)
    controls_layout.addWidget(window.ai_job_select, 0, 1)
    controls_layout.addWidget(generate_button, 0, 2)
    controls_layout.addWidget(window.cover_letter_output, 1, 0, 1, 3)
    layout.addWidget(controls)
    return widget
