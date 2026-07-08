import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from core.exception_handler import AppExceptionHandler
from database.database_manager import DatabaseManager
from database.repositories.user_repository import UserRepository
from dialogs.login_dialog import LoginDialog
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Install global exception hook (must be after QApplication creation)
    AppExceptionHandler.setup_global_handler()

    # --- Application icon ---
    logo_path = os.path.join("resources", "images", "logo.png")
    if os.path.exists(logo_path):
        app.setWindowIcon(QIcon(logo_path))
    else:
        app.setWindowIcon(app.style().standardIcon(app.style().SP_ComputerIcon))

    # --- Database connection ---
    db = DatabaseManager()
    try:
        db.connect()
    except Exception as e:
        AppExceptionHandler.show_error(
            "Database Error",
            f"Could not connect to the local database.\n\n"
            f"Please ensure 'transport_db.sqlite' exists in the application directory.\n\n"
            f"Error: {str(e)}"
        )
        sys.exit(1)

    # --- Login ---
    user_repo = UserRepository(db)
    login = LoginDialog(user_repo)
    if login.exec() != LoginDialog.Accepted:
        sys.exit(0)

    # --- Main Window with user session ---
    try:
        user = login.user_data
        window = MainWindow(db=db, user=user)
        window.show()
    except Exception as e:
        AppExceptionHandler.handle_exception(e, parent=None, title="Startup Error")
        sys.exit(1)

    sys.exit(app.exec())


if __name__ == "__main__":
    main()