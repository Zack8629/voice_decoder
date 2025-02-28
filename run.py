import ctypes
import sys

from PyQt6.QtWidgets import QApplication

from app.ui import WhisperApp


def enable_console():
    """Создаёт консоль, если запущено с -D."""
    kernel32 = ctypes.windll.kernel32
    kernel32.AllocConsole()
    sys.stdout = open('CONOUT$', 'w')
    sys.stderr = open('CONOUT$', 'w')
    print('Debug mode enabled (-D)')


def main():
    try:
        app = QApplication([])
        window = WhisperApp()
        window.show()
        app.exec()
    except Exception as e:
        print(f'main error -> {e}')


if __name__ == '__main__':
    if '-D' in sys.argv:
        enable_console()

    main()
