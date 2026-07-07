from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
    QGroupBox, QAbstractItemView, QMessageBox, QWidget
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QFont
from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.daily_log_repository import DailyLogRepository


class VehicleLogsDialog(QDialog):
    """
    Dialog that shows daily logs for a selected vehicle with pagination and date filtering.
    """

    PAGE_SIZE = 20

    def __init__(
        self,
        vehicle_id: int,
        vehicle_repo: VehicleRepository,
        log_repo: DailyLogRepository,
        parent=None,
    ):
        super().__init__(parent)
        self.vehicle_id = vehicle_id
        self.vehicle_repo = vehicle_repo
        self.log_repo = log_repo

        # State
        self.current_page = 0          # zero-based
        self.total_records = 0
        self.from_date = None          # strings or None
        self.to_date = None

        self.setWindowTitle("Vehicle Log History")
        self.resize(950, 500)
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # Title with vehicle registration
        vehicle = self.vehicle_repo.get_by_id(self.vehicle_id)
        reg = vehicle["registration_number"] if vehicle else "Unknown"
        title = QLabel(f"Log entries for {reg}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        layout.addWidget(title)

        # Date filter section
        filter_group = QGroupBox("Filter by Date")
        filter_layout = QHBoxLayout(filter_group)

        filter_layout.addWidget(QLabel("From:"))
        self.from_date_edit = QDateEdit()
        self.from_date_edit.setCalendarPopup(True)
        self.from_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.from_date_edit.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.from_date_edit)

        filter_layout.addWidget(QLabel("To:"))
        self.to_date_edit = QDateEdit()
        self.to_date_edit.setCalendarPopup(True)
        self.to_date_edit.setDate(QDate.currentDate())
        self.to_date_edit.setDisplayFormat("yyyy-MM-dd")
        filter_layout.addWidget(self.to_date_edit)

        self.search_btn = QPushButton("Search")
        self.search_btn.clicked.connect(self._apply_filter)
        filter_layout.addWidget(self.search_btn)

        self.clear_btn = QPushButton("Clear Filter")
        self.clear_btn.clicked.connect(self._clear_filter)
        filter_layout.addWidget(self.clear_btn)

        filter_layout.addStretch()
        layout.addWidget(filter_group)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(10)
        self.table.setHorizontalHeaderLabels([
            "Date", "From Time", "To Time", "Purpose / Route",
            "Meter Out", "Meter In", "Mileage", "Fuel",
            "Mobile Oil", "Remarks"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        layout.addWidget(self.table)

        # Pagination controls
        pagination_widget = QWidget()
        pagination_layout = QHBoxLayout(pagination_widget)
        pagination_layout.setContentsMargins(0, 5, 0, 0)

        self.first_btn = QPushButton("<< First")
        self.first_btn.clicked.connect(self._go_to_first_page)
        pagination_layout.addWidget(self.first_btn)

        self.prev_btn = QPushButton("< Previous")
        self.prev_btn.clicked.connect(self._go_to_previous_page)
        pagination_layout.addWidget(self.prev_btn)

        self.page_info_label = QLabel("Page 1 of 1")
        self.page_info_label.setAlignment(Qt.AlignCenter)
        pagination_layout.addWidget(self.page_info_label)

        self.next_btn = QPushButton("Next >")
        self.next_btn.clicked.connect(self._go_to_next_page)
        pagination_layout.addWidget(self.next_btn)

        self.last_btn = QPushButton("Last >>")
        self.last_btn.clicked.connect(self._go_to_last_page)
        pagination_layout.addWidget(self.last_btn)

        self.record_info_label = QLabel("Showing 0-0 of 0 records")
        self.record_info_label.setAlignment(Qt.AlignCenter)
        pagination_layout.addWidget(self.record_info_label)

        layout.addWidget(pagination_widget)

        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.reject)
        layout.addWidget(close_btn)

    def _load_data(self):
        """Fetch current page from repository and update table and pagination controls."""
        try:
            offset = self.current_page * self.PAGE_SIZE
            logs = self.log_repo.get_logs_for_vehicle_filtered(
                self.vehicle_id,
                from_date=self.from_date,
                to_date=self.to_date,
                limit=self.PAGE_SIZE,
                offset=offset,
            )
            self.total_records = self.log_repo.get_logs_count_for_vehicle(
                self.vehicle_id,
                from_date=self.from_date,
                to_date=self.to_date,
            )
            self._populate_table(logs)
            self._update_pagination_controls()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load logs:\n{str(e)}")

    def _populate_table(self, logs):
        """Fill the table with log data."""
        self.table.setRowCount(len(logs))
        for row, log in enumerate(logs):
            self.table.setItem(row, 0, QTableWidgetItem(log.get("log_date", "")))
            self.table.setItem(row, 1, QTableWidgetItem(log.get("from_time", "")))
            self.table.setItem(row, 2, QTableWidgetItem(log.get("to_time", "")))
            self.table.setItem(row, 3, QTableWidgetItem(log.get("purpose_route", "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(log.get("meter_out", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(str(log.get("meter_in", ""))))
            self.table.setItem(row, 6, QTableWidgetItem(str(log.get("mileage", ""))))
            fuel = log.get("fuel")
            self.table.setItem(row, 7, QTableWidgetItem(str(fuel) if fuel is not None else ""))
            oil = log.get("mobile_oil")
            self.table.setItem(row, 8, QTableWidgetItem(str(oil) if oil is not None else ""))
            self.table.setItem(row, 9, QTableWidgetItem(log.get("remarks", "")))

    def _update_pagination_controls(self):
        """Update labels and button states based on current page and total records."""
        total_pages = max(1, (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.page_info_label.setText(f"Page {self.current_page + 1} of {total_pages}")

        # Record range
        start = self.current_page * self.PAGE_SIZE + 1 if self.total_records > 0 else 0
        end = min((self.current_page + 1) * self.PAGE_SIZE, self.total_records)
        self.record_info_label.setText(f"Showing {start}-{end} of {self.total_records} records")

        # Enable/disable navigation buttons
        self.first_btn.setEnabled(self.current_page > 0)
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
        self.last_btn.setEnabled(self.current_page < total_pages - 1)

    def _go_to_first_page(self):
        self.current_page = 0
        self._load_data()

    def _go_to_previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self._load_data()

    def _go_to_next_page(self):
        total_pages = max(1, (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        if self.current_page < total_pages - 1:
            self.current_page += 1
            self._load_data()

    def _go_to_last_page(self):
        total_pages = max(1, (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE)
        self.current_page = total_pages - 1
        self._load_data()

    def _apply_filter(self):
        """Set date filters from the UI and reload page 0."""
        self.from_date = self.from_date_edit.date().toString("yyyy-MM-dd")
        self.to_date = self.to_date_edit.date().toString("yyyy-MM-dd")
        self.current_page = 0
        self._load_data()

    def _clear_filter(self):
        """Reset date filters and reload."""
        self.from_date = None
        self.to_date = None
        self.current_page = 0
        self._load_data()