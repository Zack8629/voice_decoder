import os
import subprocess
from pathlib import Path

import torch
import whisper

from app import FFMPEG_PATH, WHISPER_MODELS_DIR


def convert_to_wav(input_path):
    """Конвертирует аудио- или видеофайл в WAV (PCM 16-bit, 16kHz, mono)"""
    try:
        input_path = Path(input_path)
        output_path = input_path.parent / f'convert_file_{input_path.stem}.wav'

        command = [
            str(FFMPEG_PATH), '-i', str(input_path),
            '-ac', '1', '-ar', '16000', '-acodec', 'pcm_s16le',
            '-threads', '0',
            '-y', str(output_path)
        ]

        print(f'[DEBUG] Запуск FFmpeg: {" ".join(command)}')

        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

        if not os.path.exists(output_path):
            print(f'FFmpeg ошибка: {result.stderr}')
            raise FileNotFoundError(f'FFmpeg не создал файл: {output_path}')

        return str(output_path)

    except subprocess.CalledProcessError as e:
        raise RuntimeError(f'Ошибка при конвертации файла {input_path}: {e}')


def get_best_device():
    """Определяет наиболее эффективное устройство (GPU или CPU)."""
    try:
        if torch.cuda.is_available():
            return 'cuda'
        elif torch.backends.mps.is_available():  # Apple M1/M2
            return 'mps'
        else:
            if torch.cuda.device_count() > 0:
                print('[WARNING] Whisper работает на CPU, хотя GPU доступен! Возможно, не установлены драйверы.')
                return 'cpu (GPU доступен, но не используется!)'
            return 'cpu'

    except Exception as e:
        print(f'[WARNING] Ошибка при определении устройства: {e}')
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
        temp_file = False

        if file_ext in ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']:
            audio_path = file_path
        else:
            audio_path = convert_to_wav(file_path)
            temp_file = True

        if progress_callback:
            progress_callback(25)

        print(f'[DEBUG] Whisper будет работать с файлом: {audio_path}')
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f'[ERROR] Файл {audio_path} не найден перед обработкой в Whisper!')

        if progress_callback:
            progress_callback(50)

        device = get_best_device()
        print(f'Используем устройство: {device}')

        if not WHISPER_MODELS_DIR.exists():
            raise FileNotFoundError(f'Папка whisper_models не найдена: {WHISPER_MODELS_DIR}')

        model = whisper.load_model(model_size, device=device, download_root=str(WHISPER_MODELS_DIR))

        if torch.__version__ >= '2.0':
            try:
                model = torch.compile(model)
                print('[DEBUG] PyTorch model compiled successfully!')
            except Exception as e:
                print(f'[WARNING] Ошибка при компиляции модели: {e}')

        if progress_callback:
            progress_callback(75)

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
            progress_callback(100)

        if temp_file and not save_converted:
            os.remove(audio_path)

        return dialogue_text
    except Exception as e:
        if progress_callback:
            progress_callback(0)
        print(f'Error transcribe => {e}')
        return 'Ошибка при обработке файла'
