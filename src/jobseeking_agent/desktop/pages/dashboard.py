from PySide6.QtWidgets import QGroupBox, QHBoxLayout, QLabel, QVBoxLayout, QWidget

from jobseeking_agent import __version__
from jobseeking_agent.desktop.widgets import jobs_table, metric_card, page_container


def build_dashboard_page(window: QWidget) -> QWidget:
    widget = page_container()
    layout = widget.layout()

    title = QLabel("JobSeekingAgent")
    title.setStyleSheet("font-size: 30px; font-weight: 700; color: #17202a;")
    subtitle = QLabel(f"Local desktop agent · v{__version__}")
    subtitle.setStyleSheet("color: #64748b;")
    layout.addWidget(title)
    layout.addWidget(subtitle)

    metrics = QHBoxLayout()
    window.jobs_metric_box, window.jobs_metric = metric_card("Jobs")
    window.drafts_metric_box, window.drafts_metric = metric_card("Drafts")
    window.submitted_metric_box, window.submitted_metric = metric_card("Submitted")
    window.active_metric_box, window.active_metric = metric_card("Active")
    for box in (
        window.jobs_metric_box,
        window.drafts_metric_box,
        window.submitted_metric_box,
        window.active_metric_box,
    ):
        metrics.addWidget(box)
    layout.addLayout(metrics)

    window.recent_jobs_table = jobs_table()
    recent_group = QGroupBox("Recent Jobs")
    recent_layout = QVBoxLayout(recent_group)
    recent_layout.addWidget(window.recent_jobs_table)
    layout.addWidget(recent_group)
    return widget
