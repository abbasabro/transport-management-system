from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QComboBox,
    QDialogButtonBox, QMessageBox, QLabel
)
from database.repositories.user_repository import UserRepository


class AddUserDialog(QDialog):
    """Dialog for adding or editing a user. Password is required only for new users."""

    def __init__(self, user_repo: UserRepository, parent=None, user_data: dict = None):
        super().__init__(parent)
        self.user_repo = user_repo
        self.user_data = user_data
        self.edit_mode = user_data is not None
        self.setWindowTitle("Edit User" if self.edit_mode else "Add User")
        self.setMinimumWidth(400)
        self._setup_ui()
        if self.edit_mode:
            self._populate_fields()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        # Username
        self.username_edit = QLineEdit()
        form.addRow("Username:", self.username_edit)

        # Full Name
        self.fullname_edit = QLineEdit()
        form.addRow("Full Name:", self.fullname_edit)

        # Role
        self.role_combo = QComboBox()
        self.role_combo.addItems(["Transport Head", "Transport Clerk"])
        form.addRow("Role:", self.role_combo)

        # Status (only for edit)
        if self.edit_mode:
            self.status_combo = QComboBox()
            self.status_combo.addItems(["Active", "Inactive"])
            form.addRow("Status:", self.status_combo)

        # Password fields
        if self.edit_mode:
            form.addRow(QLabel("Leave blank to keep current password"))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Password:" if not self.edit_mode else "New Password:", self.password_edit)

        self.confirm_password_edit = QLineEdit()
        self.confirm_password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Confirm Password:", self.confirm_password_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _populate_fields(self):
        """Pre‑fill fields when editing."""
        u = self.user_data
        self.username_edit.setText(u.get("username", ""))
        self.fullname_edit.setText(u.get("full_name", ""))
        role = u.get("role", "Transport Clerk")
        idx = self.role_combo.findText(role)
        if idx >= 0:
            self.role_combo.setCurrentIndex(idx)
        status = u.get("status", "Active")
        idx = self.status_combo.findText(status)
        if idx >= 0:
            self.status_combo.setCurrentIndex(idx)

    def _save(self):
        username = self.username_edit.text().strip()
        fullname = self.fullname_edit.text().strip()
        role = self.role_combo.currentText()
        password = self.password_edit.text()
        confirm = self.confirm_password_edit.text()

        if not username:
            QMessageBox.warning(self, "Validation Error", "Username is required.")
            return
        if not fullname:
            QMessageBox.warning(self, "Validation Error", "Full name is required.")
            return

        try:
            if self.edit_mode:
                # Update user details
                status = self.status_combo.currentText()
                self.user_repo.update_user(
                    user_id=self.user_data["id"],
                    username=username,
                    full_name=fullname,
                    role=role,
                    status=status,
                )
                # Change password only if provided
                if password or confirm:
                    if password != confirm:
                        QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
                        return
                    if password:
                        # We need to change password; we can reuse the change_password method
                        # but we don't have old password here, so we can't verify. Instead,
                        # we'll implement a direct update (repo can have a set_password method).
                        # For now, we call a new repository method (to be added) – but to keep
                        # it simple, we'll raise a temporary limitation.
                        # Actually we can add a set_password method in UserRepository that only
                        # requires user_id and new password (no old password). We'll add that now.
                        # We'll include it in the final repo update.
                        self.user_repo.set_password(self.user_data["id"], password)
            else:
                if not password:
                    QMessageBox.warning(self, "Validation Error", "Password is required for new user.")
                    return
                if password != confirm:
                    QMessageBox.warning(self, "Validation Error", "Passwords do not match.")
                    return
                self.user_repo.add_user(
                    username=username,
                    password=password,
                    full_name=fullname,
                    role=role,
                )
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))