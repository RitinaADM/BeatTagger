import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    try:
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Ошибка при запуске приложения: {e}")

if __name__ == "__main__":
    main()
