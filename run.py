from PyQt6.QtWidgets import QApplication

from app.ui import WhisperApp


def main():
    try:
        app = QApplication([])
        window = WhisperApp()
        window.show()
        app.exec()
    except Exception as e:
        print(f'main error -> {e}')


if __name__ == '__main__':
    main()
