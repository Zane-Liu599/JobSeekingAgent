from PySide6.QtWidgets import QComboBox, QGroupBox, QHBoxLayout, QPushButton, QWidget

from jobseeking_agent.desktop.widgets import jobs_table, page_container
from jobseeking_agent.tracker.status_manager import VALID_STATUSES


def build_tracker_page(window: QWidget) -> QWidget:
    widget = page_container()
    layout = widget.layout()

    status_group = QGroupBox("Status")
    status_layout = QHBoxLayout(status_group)
    window.tracker_job_select = QComboBox()
    window.status_select = QComboBox()
    window.status_select.addItems(sorted(VALID_STATUSES))
    update_button = QPushButton("Update")
    update_button.setObjectName("primaryButton")
    update_button.clicked.connect(window.update_tracker_status)
    status_layout.addWidget(window.tracker_job_select, 3)
    status_layout.addWidget(window.status_select, 1)
    status_layout.addWidget(update_button, 1)

    window.tracker_table = jobs_table()
    layout.addWidget(status_group)
    layout.addWidget(window.tracker_table)
    return widget
