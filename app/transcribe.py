import os
from pathlib import Path

import torch
import whisper

from app import WHISPER_MODELS_DIR
from app.convert_to_wav import convert_to_wav
from app.format_time import format_time
from app.get_best_device import get_best_device


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
