import os
import sys
from pathlib import Path

APP_VERSION = 'v0.9.0'

try:
    if getattr(sys, 'frozen', False):  # Запуск из .exe
        # Папка, куда распакован .exe (содержимое архива PyInstaller)
        BASE_DIR = Path(sys._MEIPASS)
        # ffmpeg и иконка должны находиться в папке, куда распакован .exe
        FFMPEG_PATH = BASE_DIR / 'ffmpeg' / 'ffmpeg.exe'
        ICON_PATH = BASE_DIR / 'app' / 'main.ico'

        # Модели Whisper должны лежать в папке "whisper_models", которая находится рядом с .exe
        # WHISPER_MODELS_DIR = Path(sys.executable).parent / 'whisper_models'
        WHISPER_MODELS_DIR = BASE_DIR / 'whisper_models'
    else:  # Запуск из .py файла
        BASE_DIR = Path(__file__).resolve().parent.parent
        FFMPEG_PATH = BASE_DIR / 'ffmpeg' / 'ffmpeg.exe'
        ICON_PATH = BASE_DIR / 'app' / 'main.ico'
        WHISPER_MODELS_DIR = BASE_DIR / 'whisper_models'
except Exception as e:
    print(f'Error __init__ => {e}')

# Проверка существования ffmpeg.exe
if not FFMPEG_PATH.is_file():
    raise FileNotFoundError(f'Не найден ffmpeg: {FFMPEG_PATH}')

ffmpeg_dir = str(Path(FFMPEG_PATH).parent)
os.environ['PATH'] = f'{ffmpeg_dir};' + os.environ.get('PATH', '')
