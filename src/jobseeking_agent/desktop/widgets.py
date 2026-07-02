from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QGroupBox,
    QHeaderView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from jobseeking_agent.database.models import Job


def page_container() -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout(widget)
    layout.setContentsMargins(28, 24, 28, 24)
    layout.setSpacing(18)
    return widget


def metric_card(label: str) -> tuple[QGroupBox, QLabel]:
    box = QGroupBox(label)
    box.setObjectName("metricCard")
    layout = QVBoxLayout(box)
    layout.setContentsMargins(18, 18, 18, 16)
    layout.setSpacing(4)
    value = QLabel("0")
    value.setObjectName("metricValue")
    value.setAlignment(Qt.AlignmentFlag.AlignLeft)
    caption = QLabel(label)
    caption.setObjectName("metricLabel")
    layout.addWidget(value)
    layout.addWidget(caption)
    return box, value


def jobs_table() -> QTableWidget:
    table = QTableWidget(0, 7)
    table.setHorizontalHeaderLabels(
        ["ID", "Title", "Company", "Location", "Platform", "Status", "URL"]
    )
    table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
    table.verticalHeader().setVisible(False)
    table.setAlternatingRowColors(True)
    table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
    return table


def fill_jobs_table(table: QTableWidget, jobs: list[Job]) -> None:
    table.setRowCount(len(jobs))
    for row_index, job in enumerate(jobs):
        values = [
            job.id,
            job.title,
            job.company,
            job.location,
            job.platform,
            job.status,
            job.job_url,
        ]
        for column_index, value in enumerate(values):
            item = QTableWidgetItem("" if value is None else str(value))
            item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
            table.setItem(row_index, column_index, item)
