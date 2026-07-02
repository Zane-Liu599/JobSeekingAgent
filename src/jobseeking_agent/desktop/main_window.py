from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from jobseeking_agent.ai.cover_letter_generator import generate_cover_letter
from jobseeking_agent.application.autofill import build_application_plan
from jobseeking_agent.database.db import (
    get_job,
    init_db,
    job_status_counts,
    list_jobs,
    save_job,
    update_job_status,
)
from jobseeking_agent.database.models import Job
from jobseeking_agent.desktop.pages import (
    build_ai_page,
    build_application_page,
    build_dashboard_page,
    build_jobs_page,
    build_settings_page,
    build_tracker_page,
)
from jobseeking_agent.desktop.styles import APP_STYLES
from jobseeking_agent.desktop.widgets import fill_jobs_table
from jobseeking_agent.profile import (
    CandidateProfile,
    copy_cover_letter_template,
    copy_resume,
    load_profile,
    save_profile,
)
from jobseeking_agent.utils.file_manager import ensure_local_directories


class JobSeekingAgentWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        ensure_local_directories()
        init_db()

        self.setWindowTitle("JobSeekingAgent")
        self.setMinimumSize(1080, 680)
        self.resize(1320, 840)
        self.setStyleSheet(APP_STYLES)

        self.sidebar = QListWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar.setMinimumWidth(172)
        self.sidebar.setMaximumWidth(260)
        self.pages = QStackedWidget()

        self.build_pages()
        self.build_menu()
        self.build_shell()
        self.refresh_all()

    def build_shell(self) -> None:
        left_panel = QWidget()
        left_panel.setObjectName("leftPanel")
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(16, 18, 10, 16)
        left_layout.setSpacing(14)

        brand = QLabel("JobSeekingAgent")
        brand.setObjectName("sidebarBrand")
        caption = QLabel("Local automation")
        caption.setObjectName("sidebarCaption")
        left_layout.addWidget(brand)
        left_layout.addWidget(caption)
        left_layout.addWidget(self.sidebar, 1)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setObjectName("mainSplitter")
        splitter.addWidget(left_panel)
        splitter.addWidget(self.pages)
        splitter.setCollapsible(0, False)
        splitter.setCollapsible(1, False)
        splitter.setSizes([220, 1100])

        self.setCentralWidget(splitter)
        self.sidebar.currentRowChanged.connect(self.pages.setCurrentIndex)
        self.sidebar.setCurrentRow(0)

    def build_pages(self) -> None:
        page_builders = [
            ("Dashboard", build_dashboard_page),
            ("Jobs", build_jobs_page),
            ("AI", build_ai_page),
            ("Application", build_application_page),
            ("Tracker", build_tracker_page),
            ("Settings", build_settings_page),
        ]
        for label, builder in page_builders:
            item = QListWidgetItem(label)
            item.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            self.sidebar.addItem(item)
            self.pages.addWidget(builder(self))

    def build_menu(self) -> None:
        view_menu = self.menuBar().addMenu("View")
        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_all)
        default_size_action = QAction("Default Size", self)
        default_size_action.triggered.connect(lambda: self.resize(1320, 840))
        large_size_action = QAction("Large Size", self)
        large_size_action.triggered.connect(lambda: self.resize(1480, 940))
        view_menu.addAction(refresh_action)
        view_menu.addSeparator()
        view_menu.addAction(default_size_action)
        view_menu.addAction(large_size_action)

    def job_select_items(self) -> list[tuple[str, int]]:
        return [
            (f"#{job.id} {job.title} - {job.company}", int(job.id))
            for job in list_jobs(limit=200)
            if job.id is not None
        ]

    def fill_table_with_current_jobs(self, table) -> None:
        fill_jobs_table(table, list_jobs(limit=200))

    def refresh_select(self, combo: QComboBox) -> None:
        current = combo.currentData()
        combo.blockSignals(True)
        combo.clear()
        for label, job_id in self.job_select_items():
            combo.addItem(label, job_id)
        if current is not None:
            index = combo.findData(current)
            if index >= 0:
                combo.setCurrentIndex(index)
        combo.blockSignals(False)

    def refresh_all(self) -> None:
        counts = job_status_counts()
        jobs = list_jobs(limit=200)
        self.jobs_metric.setText(str(len(jobs)))
        self.drafts_metric.setText(str(counts.get("draft", 0) + counts.get("found", 0)))
        self.submitted_metric.setText(str(counts.get("submitted", 0)))
        active = sum(counts.get(status, 0) for status in ("reviewing", "interviewing", "offer"))
        self.active_metric.setText(str(active))

        for table in (self.recent_jobs_table, self.jobs_table_widget, self.tracker_table):
            self.fill_table_with_current_jobs(table)
        for combo in (self.ai_job_select, self.application_job_select, self.tracker_job_select):
            self.refresh_select(combo)
        self.refresh_application_plan()

    def refresh_profile_form(self) -> None:
        profile = load_profile()
        self.profile_name_input.setText(profile.name)
        self.profile_email_input.setText(profile.email)
        self.profile_phone_input.setText(profile.phone)
        self.profile_location_input.setText(profile.location)
        self.profile_work_auth_input.setText(profile.work_authorization)
        self.profile_min_salary_input.setText(profile.min_salary)
        self.profile_resume_input.setText(profile.resume_path)
        self.profile_cover_template_input.setText(profile.cover_letter_template_path)
        self.profile_target_titles_input.setText(profile.target_titles)
        self.profile_target_locations_input.setText(profile.target_locations)
        self.profile_notes_input.setPlainText(profile.notes)

    def profile_from_form(self) -> CandidateProfile:
        return CandidateProfile(
            name=self.profile_name_input.text().strip(),
            email=self.profile_email_input.text().strip(),
            phone=self.profile_phone_input.text().strip(),
            location=self.profile_location_input.text().strip(),
            resume_path=self.profile_resume_input.text().strip(),
            cover_letter_template_path=self.profile_cover_template_input.text().strip(),
            target_titles=self.profile_target_titles_input.text().strip(),
            target_locations=self.profile_target_locations_input.text().strip(),
            min_salary=self.profile_min_salary_input.text().strip(),
            work_authorization=self.profile_work_auth_input.text().strip(),
            notes=self.profile_notes_input.toPlainText().strip(),
        )

    def save_profile_from_form(self) -> None:
        path = save_profile(self.profile_from_form())
        QMessageBox.information(self, "Profile Saved", f"Saved profile to {path}")

    def choose_resume_file(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Resume",
            "",
            "Resume Files (*.pdf *.doc *.docx);;All Files (*)",
        )
        if filename:
            destination = copy_resume(filename)
            self.profile_resume_input.setText(str(destination))
            self.save_profile_from_form()

    def choose_cover_letter_template(self) -> None:
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "Upload Cover Letter Template",
            "",
            "Template Files (*.md *.txt *.doc *.docx);;All Files (*)",
        )
        if filename:
            destination = copy_cover_letter_template(filename)
            self.profile_cover_template_input.setText(str(destination))
            self.save_profile_from_form()

    def save_job_from_form(self) -> None:
        title = self.title_input.text().strip()
        company = self.company_input.text().strip()
        if not title or not company:
            QMessageBox.warning(self, "Missing Fields", "Title and company are required.")
            return

        save_job(
            Job(
                title=title,
                company=company,
                location=self.location_input.text().strip(),
                platform=self.platform_input.currentText(),
                job_url=self.url_input.text().strip(),
                description=self.description_input.toPlainText().strip(),
            )
        )
        self.title_input.clear()
        self.company_input.clear()
        self.location_input.clear()
        self.url_input.clear()
        self.description_input.clear()
        self.refresh_all()

    def selected_job_id(self, combo: QComboBox) -> int | None:
        value = combo.currentData()
        return int(value) if value is not None else None

    def generate_cover_letter_for_selected_job(self) -> None:
        job_id = self.selected_job_id(self.ai_job_select)
        if job_id is None:
            QMessageBox.information(self, "No Job", "Add a job first.")
            return
        job = get_job(job_id)
        if job is None:
            return
        path = generate_cover_letter(job)
        self.cover_letter_output.setPlainText(Path(path).read_text(encoding="utf-8"))

    def clear_layout(self, layout: QVBoxLayout) -> None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def refresh_application_plan(self) -> None:
        self.clear_layout(self.application_plan)
        job_id = self.selected_job_id(self.application_job_select)
        if job_id is None:
            self.application_plan.addWidget(QLabel("Add a job first."))
            return
        job = get_job(job_id)
        if job is None:
            return
        for step in build_application_plan(job):
            checkbox = QCheckBox(step)
            self.application_plan.addWidget(checkbox)
        self.application_plan.addStretch()

    def update_selected_application_status(self, status: str) -> None:
        job_id = self.selected_job_id(self.application_job_select)
        if job_id is not None:
            update_job_status(job_id, status)
            self.refresh_all()

    def update_tracker_status(self) -> None:
        job_id = self.selected_job_id(self.tracker_job_select)
        if job_id is not None:
            update_job_status(job_id, self.status_select.currentText())
            self.refresh_all()


def main() -> None:
    app = QApplication.instance() or QApplication(sys.argv)
    window = JobSeekingAgentWindow()
    window.show()
    sys.exit(app.exec())
