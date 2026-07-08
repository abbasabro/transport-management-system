from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QHBoxLayout, QLabel, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from database.repositories.user_repository import UserRepository


class LoginDialog(QDialog):
    """
    Login dialog that authenticates against the users table via UserRepository.
    On success, self.user_data contains the user's details.
    """

    def __init__(self, user_repo: UserRepository, parent=None):
        super().__init__(parent)
        self.user_repo = user_repo
        self.user_data = None  # populated on successful login
        self.setWindowTitle("BBSUTSD Transport - Login")
        self.setFixedSize(400, 250)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)

        # Header
        header = QLabel("Welcome to BBSUTSD Transport")
        header.setFont(QFont("Segoe UI", 14, QFont.Bold))
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        # Form
        form = QFormLayout()
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("Enter username")
        form.addRow("Username:", self.username_edit)

        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("Enter password")
        self.password_edit.setEchoMode(QLineEdit.Password)
        form.addRow("Password:", self.password_edit)
        layout.addLayout(form)

        # Buttons
        btn_layout = QHBoxLayout()
        self.login_btn = QPushButton("Login")
        self.login_btn.setIcon(QIcon.fromTheme("dialog-ok"))
        self.login_btn.clicked.connect(self._attempt_login)
        btn_layout.addWidget(self.login_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setIcon(QIcon.fromTheme("dialog-cancel"))
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

    def _attempt_login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            QMessageBox.warning(self, "Input Error", "Please enter both username and password.")
            return

        try:
            user = self.user_repo.authenticate(username, password)
        except Exception as e:
            QMessageBox.critical(self, "Database Error", f"Could not verify credentials:\n{str(e)}")
            return

        if user:
            self.user_data = user
            self.accept()
        else:
            QMessageBox.warning(self, "Login Failed", "Invalid username or password.")
            self.password_edit.clear()
            self.password_edit.setFocus()