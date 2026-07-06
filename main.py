import sys
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtGui import QIcon
from database.database_manager import DatabaseManager
from database.repositories.user_repository import UserRepository
from dialogs.login_dialog import LoginDialog
from views.main_window import MainWindow



def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    #db connection
    db = DatabaseManager()
    try:
        db.connect()
    except Exception as e:
        QMessageBox.critical(None, "Database Error",f"Could not connect to database:\n{str(e)}","Please ensure 'transport_db.db' exists in the application directory.",)
        sys.exit(1)
    except Exception as e:
        QMessageBox.critical(
            None,
            "Database Error",
            f"Failed to connect to the database:\n{str(e)}",
        )
        sys.exit(1)
    

    # Show login dialog
    login = LoginDialog(UserRepository(db))
    if login.exec() != LoginDialog.Accepted:
        sys.exit(0)

    # Pass user info to main window
    window = MainWindow(user=login.user_data,db=db)
    window.setWindowIcon(QIcon(r"G:\Transport system\Pyside-6 Learning\BBSTUD_logo.jpeg"))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()