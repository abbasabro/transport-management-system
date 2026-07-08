import sys
import os
import traceback
import logging
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QMessageBox, QApplication


class AppExceptionHandler:
    """
    Centralized error handler.
    Call `setup()` early in main() to install the global hook.
    Use `show_error()` or `handle_exception()` for controlled catches.
    """

    LOG_DIR = "logs"
    LOG_FILE = os.path.join(LOG_DIR, "application.log")
    MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB per file
    BACKUP_COUNT = 3

    _logger = None

    @classmethod
    def _ensure_log_dir(cls):
        os.makedirs(cls.LOG_DIR, exist_ok=True)

    @classmethod
    def get_logger(cls):
        """Return the configured application logger."""
        if cls._logger is None:
            cls._logger = cls._setup_logger()
        return cls._logger

    @classmethod
    def _setup_logger(cls):
        cls._ensure_log_dir()
        logger = logging.getLogger("BBSUTSD_TMS")
        logger.setLevel(logging.DEBUG)

        # Rotating file handler
        fh = RotatingFileHandler(
            cls.LOG_FILE, maxBytes=cls.MAX_LOG_SIZE, backupCount=cls.BACKUP_COUNT
        )
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(message)s"
        )
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        return logger

    @classmethod
    def setup_global_handler(cls):
        """
        Install the global excepthook. Unhandled exceptions will be logged
        and presented in a message box.
        """
        sys.excepthook = cls._global_exception_hook

    @classmethod
    def _global_exception_hook(cls, exc_type, exc_value, exc_traceback):
        """Global handler for uncaught exceptions."""
        # Log the full traceback
        logger = cls.get_logger()
        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

        # Build a user‑friendly message
        error_msg = f"An unexpected error occurred.\n\nError: {exc_value}"
        cls._show_error_dialog("Application Error", error_msg)

        # Call the original excepthook (so the traceback still appears in the console if needed)
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    @classmethod
    def _show_error_dialog(cls, title, message, parent=None):
        """Show a QMessageBox with the error."""
        app = QApplication.instance()
        if app is None:
            # No Qt application running (early startup)
            print(message, file=sys.stderr)
            return

        # Ensure we create the dialog on the main thread (it's a GUI call)
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    @classmethod
    def show_error(cls, title, message, parent=None):
        """
        Show a user‑friendly error dialog and log the message.
        Use for known/controlled errors that already have a message.
        """
        logger = cls.get_logger()
        logger.error(f"{title}: {message}")
        cls._show_error_dialog(title, message, parent)

    @classmethod
    def handle_exception(cls, exception, parent=None, title="Application Error"):
        """
        Log the exception and show a dialog with its message.
        Use inside try/except blocks when you want to report the exception
        but not let it propagate further.
        """
        logger = cls.get_logger()
        logger.exception(exception)  # logs full traceback
        cls._show_error_dialog(title, str(exception), parent)