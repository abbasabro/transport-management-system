import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QIcon
from views.main_window import MainWindow


def main():
    app = QApplication(sys.argv)
    # app.setStyle("Fusion")  # Modern look

    # Set application-wide icon (university logo)
    # logo_path = os.path.join("resources", "images", "university_logo.png")
    # if os.path.exists(logo_path):
    #     app.setWindowIcon(QIcon(logo_path))
    # else:
    #     # Fallback to a built-in icon
    #     app.setWindowIcon(app.style().standardIcon(app.style().SP_ComputerIcon))


    window = MainWindow()
    window.setWindowIcon(QIcon(r"G:\Transport system\Pyside-6 Learning\BBSTUD_logo.jpeg"))
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()