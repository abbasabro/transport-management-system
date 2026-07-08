from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QDialogButtonBox, QMessageBox
)
from database.repositories.user_repository import UserRepository


class ChangePasswordDialog(QDialog):
    """Dialog for a user to change their own password."""

    def __init__(self, user_repo: UserRepository, user_id: int, parent=None):
        super().__init__(parent)
        self.user_repo = user_repo
        self.user_id = user_id
        self.setWindowTitle("Change Password")
        self.setMinimumWidth(350)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.old_pwd_edit = QLineEdit()
        self.old_pwd_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Current Password:", self.old_pwd_edit)

        self.new_pwd_edit = QLineEdit()
        self.new_pwd_edit.setEchoMode(QLineEdit.Password)
        form.addRow("New Password:", self.new_pwd_edit)

        self.confirm_pwd_edit = QLineEdit()
        self.confirm_pwd_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Confirm Password:", self.confirm_pwd_edit)

        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._change_password)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _change_password(self):
        old = self.old_pwd_edit.text()
        new = self.new_pwd_edit.text()
        confirm = self.confirm_pwd_edit.text()

        if not old or not new or not confirm:
            QMessageBox.warning(self, "Validation Error", "All fields are required.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Validation Error", "New passwords do not match.")
            return
        try:
            self.user_repo.change_password(self.user_id, old, new)
            QMessageBox.information(self, "Success", "Password updated successfully.")
            self.accept()
        except ValueError as e:
            QMessageBox.warning(self, "Error", str(e))