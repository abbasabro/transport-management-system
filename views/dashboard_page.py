from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFrame, QLabel, QPushButton
)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QFont, QIcon

from database.repositories.vehicle_repository import VehicleRepository
from database.repositories.driver_repository import DriverRepository
from security.permissions import PermissionManager


class DashboardPage(QWidget):
    """Dashboard with live summary cards (active counts) and role‑based action buttons."""

    add_vehicle_clicked = Signal()
    add_driver_clicked = Signal()
    logs_clicked = Signal()
    vehicles_list_clicked = Signal()
    drivers_list_clicked = Signal()
    repairs_clicked = Signal()
    reports_clicked = Signal()
    all_logs_clicked = Signal()
    settings_clicked = Signal()

    PRIMARY_BLUE ="#6a3b21"
    GOLD = "#F2A900"
    def __init__(
        self,
        vehicle_repo: VehicleRepository,
        driver_repo: DriverRepository,
        perm_manager: PermissionManager,
    ):
        super().__init__()
        self.vehicle_repo = vehicle_repo
        self.driver_repo = driver_repo
        self.perm = perm_manager
        self._setup_ui()
        self.refresh()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 30, 40, 30)

        # Title
        title = QLabel("Dashboard")
        title.setFont(QFont("Segoe UI", 22, QFont.Bold))
        title.setStyleSheet(
            f"color: {self.PRIMARY_BLUE}; border-bottom: 3px solid {self.GOLD}; padding-bottom: 5px;"
        )
        main_layout.addWidget(title)

        # Cards row
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        self.vehicle_card, self.vehicle_value_label = self._create_stat_card("Total Vehicles")
        cards_layout.addWidget(self.vehicle_card)

        self.driver_card, self.driver_value_label = self._create_stat_card("Total Drivers")
        cards_layout.addWidget(self.driver_card)

        main_layout.addLayout(cards_layout)
        main_layout.addSpacing(30)

        # Quick Actions
        main_layout.addWidget(QLabel("Quick Actions", font=QFont("Segoe UI", 14, QFont.Bold)))

        # Define all possible buttons with their permission and signal names
        all_buttons = [
            ("Add Vehicle", "list-add", "vehicle.add", "add_vehicle_clicked"),
            ("Add Driver", "list-add", "driver.add", "add_driver_clicked"),
            ("Logs Management", "x-office-spreadsheet", "log.view", "logs_clicked"),
            ("Vehicles List", "view-list-tree", "vehicle.list_view", "vehicles_list_clicked"),
            ("Drivers List", "view-list-details", "driver.list_view", "drivers_list_clicked"),
            ("All Logs", "view-list-tree", "log.view", "all_logs_clicked"),
            ("Repair Management", "applications-engineering", "repair.list_view", "repairs_clicked"),
            ("Report Generation", "document-print-preview", "report.generate", "reports_clicked"),
            ("Settings", "configure", "settings.access", "settings_clicked"),
        ]

        # Filter and create buttons only if permission is granted
        button_widgets = []
        for text, icon_name, perm_key, signal_name in all_buttons:
            if self.perm.has_permission(perm_key):
                btn = self._create_action_button(text, icon_name)
                signal = getattr(self, signal_name, None)
                if signal:
                    btn.clicked.connect(signal.emit)
                button_widgets.append(btn)

        # Arrange buttons in rows of three
        row_layouts = []
        for i in range(0, len(button_widgets), 3):
            row = QHBoxLayout()
            row.setSpacing(20)
            for j in range(3):
                idx = i + j
                if idx < len(button_widgets):
                    row.addWidget(button_widgets[idx])
                else:
                    row.addStretch()
            row_layouts.append(row)

        for row in row_layouts:
            main_layout.addLayout(row)

        main_layout.addStretch()

    def refresh(self):
        """Fetch counts for Active vehicles and drivers only."""
        try:
            active_vehicles = self.vehicle_repo.get_active_vehicles()
            active_drivers = self.driver_repo.get_active_drivers_with_vehicle()
            self.vehicle_value_label.setText(str(len(active_vehicles)))
            self.driver_value_label.setText(str(len(active_drivers)))
        except Exception:
            self.vehicle_value_label.setText("?")
            self.driver_value_label.setText("?")

    def _create_stat_card(self, title: str) -> tuple[QFrame, QLabel]:
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background: white;
                border: 1px solid #d0d7de;
                border-left: 6px solid {self.GOLD};
                border-radius: 10px;
                padding: 20px;
                min-width: 220px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 11))
        title_label.setStyleSheet("color: #555; border: none;")
        value_label = QLabel("0")
        value_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        value_label.setStyleSheet(f"color: {self.PRIMARY_BLUE}; border: none;")
        card_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        card_layout.addWidget(value_label, alignment=Qt.AlignCenter)
        return card, value_label

    def _create_action_button(self, text: str, icon_name: str) -> QPushButton:
        btn = QPushButton(text)
        btn.setIcon(QIcon.fromTheme(icon_name))
        btn.setIconSize(QSize(32, 32))
        btn.setMinimumHeight(60)
        btn.setFont(QFont("Segoe UI", 12))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.PRIMARY_BLUE};
                color: white;
                border: 2px solid transparent;
                border-radius: 10px;
                padding: 10px 20px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #592c1c;
                border-color: {self.GOLD};
            }}
            QPushButton:pressed {{
                background-color: #123a8c;
            }}
        """)
        return btn