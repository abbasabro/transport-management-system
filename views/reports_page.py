from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDateEdit,
    QLineEdit, QPushButton, QMessageBox, QGroupBox
)
from PySide6.QtCore import QDate, Signal
from PySide6.QtGui import QFont


class ReportsPage(QWidget):
    """Report generation page with date selectors and placeholder buttons."""

    def __init__(self):
        super().__init__()
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 30, 40, 30)

        heading = QLabel("Download Reports")
        heading.setFont(QFont("Segoe UI", 22, QFont.Bold))
        layout.addWidget(heading)
        layout.addSpacing(20)

        # Date selection
        date_group = QGroupBox("Select Date Range")
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("From:"))
        self.from_date = QDateEdit()
        self.from_date.setCalendarPopup(True)
        self.from_date.setDate(QDate.currentDate().addMonths(-1))
        date_layout.addWidget(self.from_date)

        date_layout.addWidget(QLabel("To:"))
        self.to_date = QDateEdit()
        self.to_date.setCalendarPopup(True)
        self.to_date.setDate(QDate.currentDate())
        date_layout.addWidget(self.to_date)
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)

        # Fuel consumption input
        fuel_layout = QHBoxLayout()
        fuel_layout.addWidget(QLabel("Fuel Consumption (Litre):"))
        self.fuel_input = QLineEdit()
        self.fuel_input.setPlaceholderText("Optional")
        fuel_layout.addWidget(self.fuel_input)
        layout.addLayout(fuel_layout)
        layout.addSpacing(20)

        # Report buttons
        report_group = QGroupBox("Available Reports")
        report_layout = QVBoxLayout()
        buttons = [
            "Download Vehicle Daily Report",
            "Download Vehicle 15 Days Report",
            "Download Vehicle 30 Days Report",
            "Download Vehicle Custom Report",
            "Download Fleet Summary Report",
            "Download Repair Report",
        ]
        for text in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(40)
            btn.setFont(QFont("Segoe UI", 11))
            btn.clicked.connect(self._show_placeholder)
            report_layout.addWidget(btn)
        report_group.setLayout(report_layout)
        layout.addWidget(report_group)
        layout.addStretch()

    def _show_placeholder(self):
        QMessageBox.information(self, "Report", "Report generation is not implemented yet.")