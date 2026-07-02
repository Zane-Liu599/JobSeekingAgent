from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QTextEdit,
    QWidget,
)

from jobseeking_agent.database.db import init_db
from jobseeking_agent.desktop.widgets import page_container
from jobseeking_agent.profile import load_profile


def file_row(line_edit: QLineEdit, button: QPushButton) -> QWidget:
    widget = QWidget()
    layout = QHBoxLayout(widget)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.addWidget(line_edit, 1)
    layout.addWidget(button)
    return widget


def build_settings_page(window: QWidget) -> QWidget:
    widget = page_container()
    layout = widget.layout()
    profile = load_profile()

    profile_group = QGroupBox("Candidate Profile")
    profile_form = QFormLayout(profile_group)
    window.profile_name_input = QLineEdit(profile.name)
    window.profile_email_input = QLineEdit(profile.email)
    window.profile_phone_input = QLineEdit(profile.phone)
    window.profile_location_input = QLineEdit(profile.location)
    window.profile_work_auth_input = QLineEdit(profile.work_authorization)
    window.profile_min_salary_input = QLineEdit(profile.min_salary)
    profile_form.addRow("Name", window.profile_name_input)
    profile_form.addRow("Email", window.profile_email_input)
    profile_form.addRow("Phone", window.profile_phone_input)
    profile_form.addRow("Location", window.profile_location_input)
    profile_form.addRow("Work Authorization", window.profile_work_auth_input)
    profile_form.addRow("Minimum Salary", window.profile_min_salary_input)

    materials_group = QGroupBox("Application Materials")
    materials_form = QFormLayout(materials_group)
    window.profile_resume_input = QLineEdit(profile.resume_path)
    window.profile_cover_template_input = QLineEdit(profile.cover_letter_template_path)
    resume_button = QPushButton("Upload")
    cover_button = QPushButton("Upload")
    resume_button.clicked.connect(window.choose_resume_file)
    cover_button.clicked.connect(window.choose_cover_letter_template)
    materials_form.addRow("Resume", file_row(window.profile_resume_input, resume_button))
    materials_form.addRow(
        "Cover Letter Template",
        file_row(window.profile_cover_template_input, cover_button),
    )

    preferences_group = QGroupBox("Job Preferences")
    preferences_form = QFormLayout(preferences_group)
    window.profile_target_titles_input = QLineEdit(profile.target_titles)
    window.profile_target_locations_input = QLineEdit(profile.target_locations)
    window.profile_notes_input = QTextEdit(profile.notes)
    window.profile_notes_input.setFixedHeight(110)
    preferences_form.addRow("Target Titles", window.profile_target_titles_input)
    preferences_form.addRow("Target Locations", window.profile_target_locations_input)
    preferences_form.addRow("Notes", window.profile_notes_input)

    actions = QHBoxLayout()
    save_button = QPushButton("Save Profile")
    save_button.setObjectName("primaryButton")
    save_button.clicked.connect(window.save_profile_from_form)
    actions.addStretch()
    actions.addWidget(save_button)

    group = QGroupBox("Local Configuration")
    form = QFormLayout(group)
    form.addRow("Database", QLabel(str(init_db())))

    layout.addWidget(profile_group)
    layout.addWidget(materials_group)
    layout.addWidget(preferences_group)
    layout.addLayout(actions)
    layout.addWidget(group)
    return widget
