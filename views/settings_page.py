from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QFormLayout, QLineEdit, QAbstractItemView, QMessageBox
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QIcon
from database.repositories.user_repository import UserRepository
# The AddUserDialog will be created later; import will be fixed after its creation.
# For now, we assume it exists.
from dialogs.add_user_dialog import AddUserDialog


class SettingsPage(QWidget):
    """Settings page with user management and change password."""

    back_requested = Signal()

    def __init__(self, user_repo: UserRepository, current_user: dict):
        super().__init__()
        self.user_repo = user_repo
        self.current_user = current_user  # currently logged in user

        self._setup_ui()
        self._load_users()

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 20, 30, 20)
        main_layout.setSpacing(20)

        # Top: back button + title
        top_layout = QHBoxLayout()
        self.back_btn = QPushButton()
        self.back_btn.setIcon(QIcon.fromTheme("go-previous"))
        self.back_btn.setToolTip("Back to Dashboard")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.clicked.connect(self.back_requested.emit)
        top_layout.addWidget(self.back_btn)

        title = QLabel("Settings")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        top_layout.addWidget(title)
        top_layout.addStretch()
        main_layout.addLayout(top_layout)

        # ------------------- User Management Section -------------------
        user_group = QGroupBox("User Management")
        user_layout = QVBoxLayout(user_group)

        # Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(4)
        self.user_table.setHorizontalHeaderLabels([
            "Username", "Full Name", "Role", "Status"
        ])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.user_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.user_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.user_table.setSelectionMode(QAbstractItemView.SingleSelection)
        user_layout.addWidget(self.user_table)

        # Buttons row
        btn_layout = QHBoxLayout()
        self.add_user_btn = QPushButton("Add User")
        self.add_user_btn.setIcon(QIcon.fromTheme("list-add"))
        self.add_user_btn.clicked.connect(self._add_user)
        btn_layout.addWidget(self.add_user_btn)

        self.edit_user_btn = QPushButton("Edit User")
        self.edit_user_btn.setIcon(QIcon.fromTheme("document-edit"))
        self.edit_user_btn.clicked.connect(self._edit_user)
        btn_layout.addWidget(self.edit_user_btn)

        self.activate_btn = QPushButton("Activate")
        self.activate_btn.setIcon(QIcon.fromTheme("task-complete"))
        self.activate_btn.clicked.connect(lambda: self._set_status("Active"))
        btn_layout.addWidget(self.activate_btn)

        self.deactivate_btn = QPushButton("Deactivate")
        self.deactivate_btn.setIcon(QIcon.fromTheme("task-reject"))
        self.deactivate_btn.clicked.connect(lambda: self._set_status("Inactive"))
        btn_layout.addWidget(self.deactivate_btn)

        btn_layout.addStretch()
        user_layout.addLayout(btn_layout)

        main_layout.addWidget(user_group)

        # ------------------- Change Password Section -------------------
        pwd_group = QGroupBox("Change Password")
        pwd_layout = QFormLayout(pwd_group)

        self.current_pwd_edit = QLineEdit()
        self.current_pwd_edit.setEchoMode(QLineEdit.Password)
        pwd_layout.addRow("Current Password:", self.current_pwd_edit)

        self.new_pwd_edit = QLineEdit()
        self.new_pwd_edit.setEchoMode(QLineEdit.Password)
        pwd_layout.addRow("New Password:", self.new_pwd_edit)

        self.confirm_pwd_edit = QLineEdit()
        self.confirm_pwd_edit.setEchoMode(QLineEdit.Password)
        pwd_layout.addRow("Confirm Password:", self.confirm_pwd_edit)

        self.update_pwd_btn = QPushButton("Update Password")
        self.update_pwd_btn.setIcon(QIcon.fromTheme("dialog-password"))
        self.update_pwd_btn.clicked.connect(self._change_password)
        pwd_layout.addWidget(self.update_pwd_btn)

        main_layout.addWidget(pwd_group)
        main_layout.addStretch()

    def _load_users(self):
        """Fetch and display all users."""
        try:
            users = self.user_repo.get_all_users()
            self._populate_user_table(users)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to load users:\n{str(e)}")

    def _populate_user_table(self, users):
        self.user_table.setRowCount(len(users))
        for row, u in enumerate(users):
            # Store user id in UserRole of first column
            username_item = QTableWidgetItem(u["username"])
            username_item.setData(Qt.UserRole, u["id"])
            self.user_table.setItem(row, 0, username_item)

            self.user_table.setItem(row, 1, QTableWidgetItem(u.get("full_name", "")))
            self.user_table.setItem(row, 2, QTableWidgetItem(u.get("role", "")))
            self.user_table.setItem(row, 3, QTableWidgetItem(u.get("status", "Active")))

    def _get_selected_user_id(self):
        """Return the user id of the selected row, or None."""
        selected = self.user_table.selectedItems()
        if not selected:
            QMessageBox.information(self, "No Selection", "Please select a user.")
            return None
        row = selected[0].row()
        return self.user_table.item(row, 0).data(Qt.UserRole)

    def _add_user(self):
        dialog = AddUserDialog(self.user_repo, self, user_data=None)
        if dialog.exec():
            self._load_users()

    def _edit_user(self):
        uid = self._get_selected_user_id()
        if uid is None:
            return
        user = self.user_repo.get_by_id(uid)
        if not user:
            QMessageBox.warning(self, "Error", "User not found.")
            return
        dialog = AddUserDialog(self.user_repo, self, user_data=user)
        if dialog.exec():
            self._load_users()

    def _set_status(self, status):
        uid = self._get_selected_user_id()
        if uid is None:
            return
        try:
            self.user_repo.set_user_status(uid, status)
            self._load_users()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))

    def _change_password(self):
        current = self.current_pwd_edit.text()
        new = self.new_pwd_edit.text()
        confirm = self.confirm_pwd_edit.text()

        if not current or not new or not confirm:
            QMessageBox.warning(self, "Validation Error", "All password fields are required.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Validation Error", "New passwords do not match.")
            return
        try:
            self.user_repo.change_password(self.current_user["id"], current, new)
            QMessageBox.information(self, "Success", "Password updated successfully.")
            self.current_pwd_edit.clear()
            self.new_pwd_edit.clear()
            self.confirm_pwd_edit.clear()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))