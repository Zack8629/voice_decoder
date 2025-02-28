import os
import subprocess
from pathlib import Path

import torch
import whisper

from app import BASE_DIR, FFMPEG_PATH, WHISPER_MODELS_DIR


def convert_to_wav(video_path):
    """Конвертирует видео в аудиофайл (WAV) и возвращает путь к нему."""
    try:
        video_path = Path(video_path)
        audio_path = video_path.parent / f'convert_file_{video_path.stem}.wav'  # Создание рядом с видео

        ffmpeg_path = FFMPEG_PATH

        command = [
            ffmpeg_path, '-i', video_path, '-ac', '1', '-ar', '16000', '-y', str(audio_path)
        ]

        subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)

        return str(audio_path)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Ошибка при конвертации видео: {e}')

    except Exception as e:
        print(f'Error convert_video_to_audio => {e}')
        return 'convert_video_to_audio'


def get_best_device():
    """Определяет наиболее эффективное устройство (GPU или CPU)."""
    try:
        if torch.cuda.is_available():
            return 'cuda'
        elif torch.backends.mps.is_available():  # Для Apple M1/M2
            return 'mps'
        else:
            return 'cpu'
    except Exception as e:
        print(f'Error get_best_device => {e}')
        return 'cpu'


def format_time(seconds):
    """Форматирует секунды в строку вида 'часы.минуты.секунды'"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f'[{hours}.{minutes:02}.{secs:02}]'
    else:
        return f'[{minutes}.{secs:02}]'


def transcribe(file_path, model_size='small', progress_callback=None, save_converted=True):
    try:
        file_ext = Path(file_path).suffix.lower()
        temp_file = False  # Флаг временного файла

        if file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
            audio_path = file_path
        else:
            audio_path = convert_to_wav(file_path)
            temp_file = True  # Это временный файл

        if progress_callback:
            progress_callback(25)  # Конвертация завершена

        # Добавляем ffmpeg в PATH временно
        ffmpeg_dir = str(BASE_DIR / 'ffmpeg')
        os.environ['PATH'] = f'{ffmpeg_dir};' + os.environ.get('PATH', '')

        if progress_callback:
            progress_callback(50)  # Начало загрузки модели

        device = get_best_device()
        print(f'Используем устройство: {device}')

        if not WHISPER_MODELS_DIR.exists():
            raise FileNotFoundError(f'Папка whisper_models не найдена: {WHISPER_MODELS_DIR}')

        model = whisper.load_model(model_size, device=device, download_root=str(WHISPER_MODELS_DIR))

        if progress_callback:
            progress_callback(75)  # Модель загружена, начало обработки

        result = model.transcribe(audio_path, fp16=(device != 'cpu'))
        segments = result.get('segments', [])

        dialogue_text = ''
        previous_end = 0

        for seg in segments:
            start, end, text = seg['start'], seg['end'], seg['text']
            if start - previous_end > 1.2:
                dialogue_text += '\n'
            dialogue_text += f'{format_time(start)} - {format_time(end)} {text}\n'
            previous_end = end

        if progress_callback:
            progress_callback(100)  # Готово

        # Удаляем временный файл, если галка снята
        if temp_file and not save_converted:
            os.remove(audio_path)

        return dialogue_text
    except Exception as e:
        if progress_callback:
            progress_callback(0)
        print(f'Error transcribe => {e}')
        return 'Ошибка при обработке файла'
