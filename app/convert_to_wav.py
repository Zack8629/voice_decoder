import os
import subprocess
from pathlib import Path

from app import FFMPEG_PATH


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
