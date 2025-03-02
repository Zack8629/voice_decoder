import os
import subprocess

from app import FFMPEG_PATH
from app.processor import get_best_device

# Параметры моделей: коэффициент скорости + фиксированное время загрузки
MODEL_PARAMS = {
    'small': {'coefficient': 0.5, 'load_time': 5},
    'medium': {'coefficient': 1.0, 'load_time': 10},
    'large': {'coefficient': 2.0, 'load_time': 20}
}


def get_audio_duration(file_path):
    """Возвращает длительность аудио/видео файла в секундах."""
    try:
        if not os.path.exists(file_path):
            return None

        command = [FFMPEG_PATH, '-i', file_path, '-hide_banner']
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, errors='ignore')

        duration_line = [line for line in result.stderr.split("\n") if "Duration" in line]
        if not duration_line:
            return None

        duration_str = duration_line[0].split("Duration: ")[1].split(",")[0]
        h, m, s = map(float, duration_str.replace(":", " ").split())
        return h * 3600 + m * 60 + s

    except Exception as e:
        print(f'Error get_audio_duration => {e}')
        return None


def format_time(seconds):
    """Форматирует секунды в строку вида 'чч:мм:сс'."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    return f'{h:02}:{m:02}:{s:02}'


def estimate_transcription_time(file_path, model_size='small'):
    """Оценивает примерное время расшифровки, включая загрузку модели."""
    try:
        duration = get_audio_duration(file_path)
        if duration is None:
            return 'Не удалось определить длительность файла'

        device = get_best_device()
        gpu_boost = 0.5 if device in ('cuda', 'mps') else 1.0

        model_params = MODEL_PARAMS.get(model_size, {'coefficient': 2.0, 'load_time': 10})  # Значения по умолчанию
        speed_factor = model_params['coefficient'] * gpu_boost
        estimated_time = duration * speed_factor

        # Учитываем время загрузки модели
        total_time = estimated_time + model_params['load_time']

        msg = (f'Будем использовать: {device}\n'
               f'Примерное время расшифровки: {format_time(total_time)}')
        return msg

    except Exception as e:
        print(f'Error estimate_transcription_time => {e}')


if __name__ == '__main__':
    file_path = os.path.normpath('../test_materials/test_video_4.mp4')
    print(estimate_transcription_time(file_path, 'small'))
