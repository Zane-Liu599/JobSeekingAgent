from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QGroupBox,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)

from jobseeking_agent.desktop.widgets import jobs_table, page_container


def build_jobs_page(window: QWidget) -> QWidget:
    widget = page_container()
    layout = widget.layout()

    form_group = QGroupBox("Add Job Lead")
    form = QFormLayout(form_group)
    window.title_input = QLineEdit()
    window.company_input = QLineEdit()
    window.location_input = QLineEdit()
    window.platform_input = QComboBox()
    window.platform_input.addItems(["manual", "seek", "linkedin", "indeed", "company"])
    window.url_input = QLineEdit()
    window.description_input = QTextEdit()
    window.description_input.setFixedHeight(120)
    form.addRow("Title", window.title_input)
    form.addRow("Company", window.company_input)
    form.addRow("Location", window.location_input)
    form.addRow("Platform", window.platform_input)
    form.addRow("URL", window.url_input)
    form.addRow("Description", window.description_input)

    save_button = QPushButton("Save Job")
    save_button.setObjectName("primaryButton")
    save_button.clicked.connect(window.save_job_from_form)
    form.addRow("", save_button)

    window.jobs_table_widget = jobs_table()
    layout.addWidget(form_group)
    layout.addWidget(window.jobs_table_widget)
    return widget
