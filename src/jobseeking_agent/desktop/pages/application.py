from PySide6.QtWidgets import (
    QComboBox,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from jobseeking_agent.desktop.widgets import page_container


def build_application_page(window: QWidget) -> QWidget:
    widget = page_container()
    layout = widget.layout()

    group = QGroupBox("Application Review")
    group_layout = QVBoxLayout(group)
    window.application_job_select = QComboBox()
    window.application_plan = QVBoxLayout()
    mark_reviewing = QPushButton("Mark Reviewing")
    mark_submitted = QPushButton("Mark Submitted")
    mark_submitted.setObjectName("primaryButton")
    mark_reviewing.clicked.connect(lambda: window.update_selected_application_status("reviewing"))
    mark_submitted.clicked.connect(lambda: window.update_selected_application_status("submitted"))

    actions = QHBoxLayout()
    actions.addWidget(mark_reviewing)
    actions.addWidget(mark_submitted)
    group_layout.addWidget(QLabel("Job"))
    group_layout.addWidget(window.application_job_select)
    group_layout.addLayout(window.application_plan)
    group_layout.addLayout(actions)
    window.application_job_select.currentIndexChanged.connect(window.refresh_application_plan)
    layout.addWidget(group)
    return widget
