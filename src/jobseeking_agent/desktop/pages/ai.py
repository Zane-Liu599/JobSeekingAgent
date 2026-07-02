from PySide6.QtWidgets import (
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QProgressBar,
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
    window.ai_status_label = QLabel(
        "Gemini uses your saved profile, resume, template, and selected job."
    )
    window.ai_status_label.setObjectName("helperText")
    window.cover_letter_output = QTextEdit()
    window.cover_letter_output.setMinimumHeight(360)
    window.ai_progress = QProgressBar()
    window.ai_progress.setRange(0, 0)
    window.ai_progress.hide()
    window.generate_cover_button = QPushButton("Generate with Gemini")
    window.generate_cover_button.setObjectName("primaryButton")
    window.generate_cover_button.clicked.connect(window.generate_cover_letter_for_selected_job)
    controls_layout.addWidget(QLabel("Job"), 0, 0)
    controls_layout.addWidget(window.ai_job_select, 0, 1)
    controls_layout.addWidget(window.generate_cover_button, 0, 2)
    controls_layout.addWidget(window.ai_status_label, 1, 0, 1, 3)
    controls_layout.addWidget(window.ai_progress, 2, 0, 1, 3)
    controls_layout.addWidget(window.cover_letter_output, 3, 0, 1, 3)
    layout.addWidget(controls)
    return widget
