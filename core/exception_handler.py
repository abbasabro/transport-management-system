import sys
import os
import traceback
import logging
from logging.handlers import RotatingFileHandler
from PySide6.QtWidgets import QMessageBox, QApplication
from utils.resource_path import resource_path  # not used directly but kept for consistency


class AppExceptionHandler:
    """
    Centralized error handler.
    Call `setup_global_handler()` early in main() to install the global hook.
    """

    MAX_LOG_SIZE = 5 * 1024 * 1024  # 5 MB
    BACKUP_COUNT = 3

    _logger = None

    @staticmethod
    def _get_log_dir() -> str:
        """Return the writable directory for log files."""
        if getattr(sys, 'frozen', False):
            # Running as a PyInstaller bundle – use AppData
            base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "BBSUTSD-TMS")
        else:
            # Development mode – use the project root
            base = os.path.abspath(".")
        log_dir = os.path.join(base, "logs")
        os.makedirs(log_dir, exist_ok=True)
        return log_dir

    @classmethod
    def get_logger(cls):
        """Return the configured application logger."""
        if cls._logger is None:
            cls._logger = cls._setup_logger()
        return cls._logger

    @classmethod
    def _setup_logger(cls):
        log_dir = cls._get_log_dir()  # now works, static method
        log_path = os.path.join(log_dir, "application.log")
        logger = logging.getLogger("BBSUTSD_TMS")
        logger.setLevel(logging.DEBUG)

        # Remove any existing handlers (to avoid duplicates)
        if logger.hasHandlers():
            logger.handlers.clear()

        fh = RotatingFileHandler(
            log_path, maxBytes=cls.MAX_LOG_SIZE, backupCount=cls.BACKUP_COUNT
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
        """Install the global excepthook."""
        sys.excepthook = cls._global_exception_hook

    @classmethod
    def _global_exception_hook(cls, exc_type, exc_value, exc_traceback):
        """Global handler for uncaught exceptions."""
        logger = cls.get_logger()
        logger.critical(
            "Unhandled exception",
            exc_info=(exc_type, exc_value, exc_traceback),
        )

        error_msg = f"An unexpected error occurred.\n\nError: {exc_value}"
        cls._show_error_dialog("Application Error", error_msg)

        # Optionally call the original excepthook
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    @classmethod
    def _show_error_dialog(cls, title, message, parent=None):
        """Show a QMessageBox with the error."""
        app = QApplication.instance()
        if app is None:
            print(message, file=sys.stderr)
            return

        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()

    @classmethod
    def show_error(cls, title, message, parent=None):
        """Show a user‑friendly error dialog and log the message."""
        logger = cls.get_logger()
        logger.error(f"{title}: {message}")
        cls._show_error_dialog(title, message, parent)

    @classmethod
    def handle_exception(cls, exception, parent=None, title="Application Error"):
        """Log the exception and show a dialog with its message."""
        logger = cls.get_logger()
        logger.exception(exception)
        cls._show_error_dialog(title, str(exception), parent)